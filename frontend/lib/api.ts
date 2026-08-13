const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export interface TransactionScoreRequest {
  amount: number;
  time: number;
  pca_features?: Record<string, number>;
  is_synthetic?: boolean;
  ground_truth_label?: number | null;
}

export interface FeatureSignal {
  feature_name: string;
  contribution: number;
  direction: "POS_RISK" | "NEG_RISK";
  description: string;
}

export interface TriggeredRule {
  rule_id: string;
  rule_name: string;
  severity: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  evidence: Record<string, any>;
  explanation: string;
}

export interface TransactionScoreResponse {
  transaction_id: string;
  external_tx_id: string;
  amount: number;
  timestamp: string;
  risk_score: number;
  risk_level: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  calibrated_probability: number;
  model_version: string;
  decision: "ALLOW" | "CHALLENGE" | "REVIEW" | "BLOCK";
  confidence: number;
  triggered_rules: TriggeredRule[];
  top_signals: FeatureSignal[];
  reasons: string[];
  case_created: boolean;
  case_id?: string | null;
}

export interface ThresholdSimulationRequest {
  threshold_allow: number;
  threshold_review: number;
  cost_false_positive: number;
  cost_missed_fraud: number;
  cost_manual_review: number;
}

export interface ThresholdSimulationResponse {
  threshold_allow: number;
  threshold_review: number;
  total_transactions: number;
  total_fraud_count: number;
  fraud_captured_count: number;
  fraud_capture_rate: number;
  false_positive_count: number;
  false_positive_rate: number;
  approval_rate: number;
  review_rate: number;
  block_rate: number;
  estimated_fraud_loss: number;
  estimated_false_positive_cost: number;
  estimated_review_cost: number;
  total_financial_impact: number;
  recommendation: string;
}

export interface MonitoringMetrics {
  total_scored_transactions: number;
  fraud_rate_estimate: number;
  avg_risk_score: number;
  risk_distribution: Record<string, number>;
  decision_breakdown: Record<string, number>;
  active_model_version: string;
  model_pr_auc: number;
  model_brier_score: number;
  system_latency_ms: number;
}

export async function scoreTransaction(data: TransactionScoreRequest): Promise<TransactionScoreResponse> {
  const res = await fetch(`${API_BASE_URL}/transactions/score`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to score transaction");
  return res.json();
}

export async function runSimulation(data: ThresholdSimulationRequest): Promise<ThresholdSimulationResponse> {
  const res = await fetch(`${API_BASE_URL}/simulate/threshold`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to run threshold simulation");
  return res.json();
}

export async function fetchMonitoringMetrics(): Promise<MonitoringMetrics> {
  const res = await fetch(`${API_BASE_URL}/monitoring`);
  if (!res.ok) throw new Error("Failed to fetch monitoring metrics");
  return res.json();
}

export async function fetchCases(status?: string): Promise<any[]> {
  const url = status ? `${API_BASE_URL}/cases?status=${status}` : `${API_BASE_URL}/cases`;
  const res = await fetch(url);
  if (!res.ok) throw new Error("Failed to fetch investigation queue");
  return res.json();
}

export async function overrideCaseDecision(caseId: string, newDecision: string, reason: string): Promise<any> {
  const res = await fetch(`${API_BASE_URL}/cases/${caseId}/override`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ new_decision: newDecision, reason }),
  });
  if (!res.ok) throw new Error("Failed to override decision");
  return res.json();
}
