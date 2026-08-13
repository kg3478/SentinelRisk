"use client";

import React, { useState } from "react";
import { Zap, Play, AlertCircle, ShieldAlert, CheckCircle2, Sliders, Info } from "lucide-react";
import { RiskGauge } from "@/components/RiskGauge";
import { DecisionBadge } from "@/components/DecisionBadge";
import { scoreTransaction, TransactionScoreResponse } from "@/lib/api";

interface ScenarioPreset {
  name: string;
  amount: number;
  time: number;
  pca?: Record<string, number>;
  desc: string;
}

const PRESETS: ScenarioPreset[] = [
  {
    name: "Normal Everyday Purchase",
    amount: 45.50,
    time: 43200, // 12 PM
    pca: { V1: 0.1, V2: -0.2, V14: 0.5 },
    desc: "Standard retail transaction within normal spending patterns."
  },
  {
    name: "Extreme Value Spike (€3,800)",
    amount: 3800.00,
    time: 54000, // 3 PM
    pca: { V1: -1.2, V2: 2.1, V14: -3.8 },
    desc: "High amount exceeding €2,500 threshold with moderate PCA deviation."
  },
  {
    name: "Off-Hours High Value (3 AM)",
    amount: 1250.00,
    time: 10800, // 3 AM
    pca: { V1: -0.5, V2: 1.1, V14: -2.2 },
    desc: "Large purchase initiated during late night off-hours."
  },
  {
    name: "Severe Anomaly Signal Breach (V14)",
    amount: 890.00,
    time: 68000,
    pca: { V14: -7.2, V12: -5.1, V10: -4.8 },
    desc: "Critical anomaly breach on primary fraud subspace features (V14/V12)."
  }
];

export default function SimulatorPage() {
  const [amount, setAmount] = useState<number>(450.00);
  const [time, setTime] = useState<number>(14400); // 4 AM
  const [selectedPreset, setSelectedPreset] = useState<number | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [result, setResult] = useState<TransactionScoreResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const applyPreset = (idx: number) => {
    const p = PRESETS[idx];
    setSelectedPreset(idx);
    setAmount(p.amount);
    setTime(p.time);
  };

  const handleScore = async () => {
    setLoading(true);
    setError(null);
    try {
      const pca = selectedPreset !== null ? PRESETS[selectedPreset].pca : undefined;
      const res = await scoreTransaction({
        amount,
        time,
        pca_features: pca,
        is_synthetic: true
      });
      setResult(res);
    } catch (err: any) {
      setError(err.message || "Error communicating with backend scoring engine");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight flex items-center">
          <Zap className="w-6 h-6 text-amber-400 mr-2" />
          Real-Time Authorization Sandbox
        </h1>
        <p className="text-slate-400 text-sm mt-1">
          Simulate live payment authorization payloads through the full pipeline: Features → Calibrated ML → Rules → Decision → SHAP Explainability.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Input Form */}
        <div className="lg:col-span-5 bg-surface p-6 rounded-2xl border border-borderDark space-y-5">
          <h2 className="text-base font-bold text-white flex items-center">
            <Sliders className="w-4 h-4 text-indigo-400 mr-2" />
            Transaction Payload Inputs
          </h2>

          {/* Scenario Presets */}
          <div>
            <label className="block text-xs font-semibold text-slate-400 mb-2 uppercase">Scenario Presets</label>
            <div className="grid grid-cols-1 gap-2">
              {PRESETS.map((p, idx) => (
                <button
                  key={p.name}
                  onClick={() => applyPreset(idx)}
                  className={`text-left p-3 rounded-xl border text-xs transition ${
                    selectedPreset === idx
                      ? "bg-indigo-600/20 border-indigo-500 text-white"
                      : "bg-surfaceCard border-borderDark text-slate-300 hover:border-slate-500"
                  }`}
                >
                  <div className="font-semibold text-slate-200">{p.name}</div>
                  <div className="text-slate-400 text-[11px] mt-0.5">{p.desc}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Custom Input Controls */}
          <div className="space-y-4 pt-2">
            <div>
              <label className="block text-xs font-semibold text-slate-400 mb-1">Transaction Amount (€)</label>
              <input
                type="number"
                value={amount}
                onChange={(e) => { setSelectedPreset(null); setAmount(parseFloat(e.target.value) || 0); }}
                className="w-full bg-slate-900 border border-borderDark rounded-lg px-3 py-2 text-white font-mono text-sm focus:outline-none focus:border-indigo-500"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-400 mb-1">Time Elapsed / Timestamp (Seconds)</label>
              <input
                type="number"
                value={time}
                onChange={(e) => { setSelectedPreset(null); setTime(parseFloat(e.target.value) || 0); }}
                className="w-full bg-slate-900 border border-borderDark rounded-lg px-3 py-2 text-white font-mono text-sm focus:outline-none focus:border-indigo-500"
              />
              <span className="text-[11px] text-slate-400 mt-1 block">
                Approx. {Math.round((time % 86400) / 3600)}:00 hrs of the day
              </span>
            </div>

            <button
              onClick={handleScore}
              disabled={loading}
              className="w-full py-3 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-bold rounded-xl text-sm transition flex items-center justify-center shadow-lg shadow-indigo-600/25"
            >
              {loading ? "Calculating Risk Engine..." : "Evaluate Transaction Risk"}
              {!loading && <Play className="w-4 h-4 ml-2 fill-current" />}
            </button>
          </div>
        </div>

        {/* Right Output Results Panel */}
        <div className="lg:col-span-7 bg-surface p-6 rounded-2xl border border-borderDark flex flex-col justify-between">
          {error && (
            <div className="p-4 bg-rose-950/60 border border-rose-800 text-rose-300 rounded-xl text-sm flex items-center mb-4">
              <AlertCircle className="w-5 h-5 mr-2 shrink-0" />
              {error}
            </div>
          )}

          {!result && !error && (
            <div className="h-full flex flex-col items-center justify-center text-center p-8 text-slate-500 space-y-3">
              <ShieldAlert className="w-12 h-12 text-slate-600" />
              <div>
                <p className="font-semibold text-slate-300">No Transaction Evaluated Yet</p>
                <p className="text-xs mt-1 text-slate-500">Select a scenario preset or click 'Evaluate Transaction Risk' to execute the decision pipeline.</p>
              </div>
            </div>
          )}

          {result && (
            <div className="space-y-6">
              {/* Score Header & Decision */}
              <div className="bg-surfaceCard p-4 rounded-xl border border-borderDark flex items-center justify-between">
                <div>
                  <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block">Decision Engine Action</span>
                  <div className="mt-1"><DecisionBadge decision={result.decision} /></div>
                  <span className="text-xs text-slate-400 mt-2 block">
                    Confidence: <span className="text-white font-semibold">{Math.round(result.confidence * 100)}%</span> | Model: <span className="font-mono text-indigo-400">{result.model_version}</span>
                  </span>
                </div>
                <RiskGauge score={result.risk_score} level={result.risk_level} />
              </div>

              {/* Triggered Deterministic Rules */}
              <div>
                <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Triggered Risk Rules</h3>
                {result.triggered_rules.length === 0 ? (
                  <div className="p-3 bg-slate-900/60 rounded-lg text-xs text-emerald-400 border border-emerald-900/50 flex items-center">
                    <CheckCircle2 className="w-4 h-4 mr-2" /> No deterministic risk rules breached.
                  </div>
                ) : (
                  <div className="space-y-2">
                    {result.triggered_rules.map((r) => (
                      <div key={r.rule_id} className="p-3 bg-rose-950/40 border border-rose-900/60 rounded-lg text-xs space-y-1">
                        <div className="flex justify-between font-bold text-rose-300">
                          <span>{r.rule_name}</span>
                          <span className="px-1.5 py-0.5 rounded bg-rose-900 text-rose-200 text-[10px]">{r.severity}</span>
                        </div>
                        <p className="text-slate-300">{r.explanation}</p>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Model Signal Attribution (SHAP Signals) */}
              <div>
                <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Model Signal Attribution (SHAP)</h3>
                <div className="space-y-2">
                  {result.top_signals.map((sig, i) => (
                    <div key={i} className="p-3 bg-slate-900/80 rounded-lg border border-borderDark text-xs flex justify-between items-center">
                      <div>
                        <span className="font-semibold text-white">{sig.feature_name}</span>
                        <p className="text-slate-400 text-[11px] mt-0.5">{sig.description}</p>
                      </div>
                      <span className={`font-mono font-bold ml-3 px-2 py-0.5 rounded ${
                        sig.direction === "POS_RISK" ? "bg-rose-950 text-rose-400" : "bg-emerald-950 text-emerald-400"
                      }`}>
                        {sig.contribution > 0 ? `+${sig.contribution}` : sig.contribution}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Case Created Banner */}
              {result.case_created && (
                <div className="p-3 bg-amber-950/60 border border-amber-800 text-amber-300 rounded-xl text-xs flex justify-between items-center">
                  <span>Flagged for investigation. Investigation case created in analyst queue.</span>
                  <span className="font-mono text-white font-bold">{result.case_id}</span>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
