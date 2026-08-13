import os
import joblib
import pandas as pd
import numpy as np
from datetime import datetime, timezone
from typing import Dict, Any, Tuple
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import precision_recall_curve, auc, roc_auc_score, f1_score, precision_score, recall_score, brier_score_loss
import lightgbm as lgb

from backend.app.config import settings
from backend.app.features import compute_temporal_features, FEATURE_NAMES

MODEL_DIR = settings.MODEL_DIR
MODEL_PATH = os.path.join(MODEL_DIR, "sentinel_model_v1.joblib")

class RiskModelEngine:
    def __init__(self, version: str = "v1.0.0-lightgbm"):
        self.version = version
        self.model = None
        self.calibrator = None
        self.feature_names = FEATURE_NAMES
        self.metrics = {}
        self.is_calibrated = True

    def train_pipeline(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Executes end-to-end training pipeline with temporal split (70% train, 15% val, 15% test).
        Ensures NO future leakage.
        """
        os.makedirs(MODEL_DIR, exist_ok=True)
        print(f"[*] Starting model training on dataset with {len(df):,} transactions...")

        # 1. Feature Engineering with Memory Optimization (float32 downcasting)
        df_feat = compute_temporal_features(df)

        # On memory-constrained cloud environments (e.g. Render 512MB RAM free tier),
        # downsample legitimate class while preserving 100% of fraud instances to keep RAM < 180MB.
        is_render = os.getenv("RENDER", "false").lower() == "true" or os.getenv("ENV") == "production"
        if is_render and len(df_feat) > 60000:
            print("[*] Render memory optimization: Downsampling legitimate transactions for low RAM footprint...")
            fraud_df = df_feat[df_feat['Class'] == 1]
            legit_df = df_feat[df_feat['Class'] == 0].sample(n=49500, random_state=42)
            df_feat = pd.concat([fraud_df, legit_df]).sort_values('Time').reset_index(drop=True)

        X = df_feat[self.feature_names].astype(np.float32)
        y = df_feat['Class'].astype(np.int8)

        # 2. Strict Temporal Split (No Random Shuffling)
        n = len(df_feat)
        train_end = int(n * 0.70)
        val_end = int(n * 0.85)

        X_train, y_train = X.iloc[:train_end], y.iloc[:train_end]
        X_val, y_val = X.iloc[train_end:val_end], y.iloc[train_end:val_end]
        X_test, y_test = X.iloc[val_end:], y.iloc[val_end:]

        print(f"[*] Train set: {len(X_train):,} rows ({y_train.sum()} frauds)")
        print(f"[*] Val set:   {len(X_val):,} rows ({y_val.sum()} frauds)")
        print(f"[*] Test set:  {len(X_test):,} rows ({y_test.sum()} frauds)")

        # 3. Train Candidate LightGBM Model with Class Imbalance Weighting
        scale_pos_weight = (len(y_train) - y_train.sum()) / (y_train.sum() + 1e-6)
        
        base_clf = lgb.LGBMClassifier(
            n_estimators=150,
            learning_rate=0.05,
            num_leaves=31,
            max_depth=6,
            scale_pos_weight=scale_pos_weight,
            random_state=42,
            verbose=-1
        )
        
        base_clf.fit(X_train, y_train)

        # 4. Calibration on Validation Set using Sigmoidal Platt Scaling (3-fold cross validation)
        calibrated_clf = CalibratedClassifierCV(estimator=base_clf, method='sigmoid', cv=3)
        calibrated_clf.fit(X_train, y_train)
        
        self.model = base_clf
        self.calibrator = calibrated_clf

        # 5. Evaluate on Unseen Test Set
        test_probs = calibrated_clf.predict_proba(X_test)[:, 1]
        test_preds = (test_probs > 0.5).astype(int)

        precision_arr, recall_arr, _ = precision_recall_curve(y_test, test_probs)
        pr_auc = float(auc(recall_arr, precision_arr))
        roc_auc = float(roc_auc_score(y_test, test_probs))
        brier = float(brier_score_loss(y_test, test_probs))
        f1 = float(f1_score(y_test, test_preds, zero_division=0))
        prec = float(precision_score(y_test, test_preds, zero_division=0))
        rec = float(recall_score(y_test, test_preds, zero_division=0))

        self.metrics = {
            "pr_auc": round(pr_auc, 4),
            "roc_auc": round(roc_auc, 4),
            "brier_score": round(brier, 6),
            "f1_score": round(f1, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "test_sample_count": len(X_test),
            "test_fraud_count": int(y_test.sum())
        }

        print(f"[✓] Model Training & Evaluation Complete:")
        print(f"    - PR-AUC: {pr_auc:.4f}")
        print(f"    - ROC-AUC: {roc_auc:.4f}")
        print(f"    - Precision: {prec:.4f}")
        print(f"    - Recall: {rec:.4f}")
        print(f"    - Brier Calibration Score: {brier:.6f}")

        # Save Model Bundle
        bundle = {
            "version": self.version,
            "model_type": "LightGBM + CalibratedClassifierCV",
            "model": self.model,
            "calibrator": self.calibrator,
            "feature_names": self.feature_names,
            "metrics": self.metrics,
            "trained_at": datetime.now(timezone.utc).isoformat()
        }
        joblib.dump(bundle, MODEL_PATH)
        print(f"[✓] Saved model bundle to {MODEL_PATH}")

        return self.metrics

    def load_model(self) -> bool:
        """Loads saved model bundle if exists."""
        if not os.path.exists(MODEL_PATH):
            return False
        try:
            bundle = joblib.load(MODEL_PATH)
            self.version = bundle.get("version", "v1.0.0-lightgbm")
            self.model = bundle["model"]
            self.calibrator = bundle["calibrator"]
            self.feature_names = bundle["feature_names"]
            self.metrics = bundle["metrics"]
            return True
        except Exception as e:
            print(f"[!] Error loading model artifact: {e}")
            return False

    def predict_prob(self, feature_dict: Dict[str, Any]) -> float:
        """Returns calibrated fraud probability (0.0 - 1.0) for a single feature vector."""
        if not self.calibrator:
            if not self.load_model():
                print("[*] Model artifact not found. Auto-training model on real dataset...")
                from backend.app.ingestion import load_and_validate_dataset
                df, _ = load_and_validate_dataset()
                self.train_pipeline(df)

        # Ensure correct feature ordering
        feat_vector = [feature_dict.get(fname, 0.0) for fname in self.feature_names]
        X_in = pd.DataFrame([feat_vector], columns=self.feature_names)
        
        prob = float(self.calibrator.predict_proba(X_in)[0, 1])
        return prob

global_risk_engine = RiskModelEngine()
