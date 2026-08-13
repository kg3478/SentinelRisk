"use client";

import React, { useState, useEffect } from "react";
import { Sliders, DollarSign, ShieldAlert, TrendingDown, CheckCircle2, RefreshCw } from "lucide-react";
import { runSimulation, ThresholdSimulationResponse } from "@/lib/api";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts";

export default function ThresholdsPage() {
  const [allowThreshold, setAllowThreshold] = useState<number>(20);
  const [reviewThreshold, setReviewThreshold] = useState<number>(75);
  const [costFp, setCostFp] = useState<number>(50);
  const [costMissed, setCostMissed] = useState<number>(100);
  const [costReview, setCostReview] = useState<number>(15);

  const [simulation, setSimulation] = useState<ThresholdSimulationResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  const executeSim = async () => {
    setLoading(true);
    try {
      const res = await runSimulation({
        threshold_allow: allowThreshold,
        threshold_review: reviewThreshold,
        cost_false_positive: costFp,
        cost_missed_fraud: costMissed,
        cost_manual_review: costReview
      });
      setSimulation(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    executeSim();
  }, [allowThreshold, reviewThreshold, costFp, costMissed, costReview]);

  const costBreakdownData = simulation ? [
    { name: "Missed Fraud Loss", amount: simulation.estimated_fraud_loss, color: "#ef4444" },
    { name: "False Positive Friction", amount: simulation.estimated_false_positive_cost, color: "#f59e0b" },
    { name: "Review Operational Cost", amount: simulation.estimated_review_cost, color: "#6366f1" },
  ] : [];

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight flex items-center">
          <Sliders className="w-6 h-6 text-indigo-400 mr-2" />
          Cost-Sensitive Decision Threshold Simulator
        </h1>
        <p className="text-slate-400 text-sm mt-1">
          Evaluate business policy thresholds against realistic false-positive friction costs, missed fraud penalties, and analyst operational expenses.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Interactive Sliders */}
        <div className="lg:col-span-4 bg-surface p-6 rounded-2xl border border-borderDark space-y-6">
          <h2 className="text-base font-bold text-white flex items-center">
            <DollarSign className="w-4 h-4 text-emerald-400 mr-1" />
            Business Policy Parameters
          </h2>

          {/* Threshold Sliders */}
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-xs font-semibold text-slate-300 mb-1">
                <span>ALLOW Risk Cutoff</span>
                <span className="text-emerald-400 font-mono font-bold">{allowThreshold} / 100</span>
              </div>
              <input
                type="range"
                min={5}
                max={50}
                value={allowThreshold}
                onChange={(e) => setAllowThreshold(parseInt(e.target.value))}
                className="w-full accent-emerald-500 cursor-pointer"
              />
              <span className="text-[11px] text-slate-400 block mt-0.5">Transactions with score ≤ {allowThreshold} are APPROVED.</span>
            </div>

            <div>
              <div className="flex justify-between text-xs font-semibold text-slate-300 mb-1">
                <span>REVIEW Risk Cutoff</span>
                <span className="text-rose-400 font-mono font-bold">{reviewThreshold} / 100</span>
              </div>
              <input
                type="range"
                min={51}
                max={95}
                value={reviewThreshold}
                onChange={(e) => setReviewThreshold(parseInt(e.target.value))}
                className="w-full accent-rose-500 cursor-pointer"
              />
              <span className="text-[11px] text-slate-400 block mt-0.5">Transactions with score ≥ {reviewThreshold} are BLOCKED.</span>
            </div>
          </div>

          <hr className="border-borderDark" />

          {/* Financial Assumptions Sliders */}
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-xs font-semibold text-slate-300 mb-1">
                <span>False Positive Friction Cost</span>
                <span className="text-amber-400 font-mono font-bold">€{costFp}</span>
              </div>
              <input
                type="range"
                min={10}
                max={200}
                step={5}
                value={costFp}
                onChange={(e) => setCostFp(parseInt(e.target.value))}
                className="w-full accent-amber-500 cursor-pointer"
              />
            </div>

            <div>
              <div className="flex justify-between text-xs font-semibold text-slate-300 mb-1">
                <span>Missed Fraud Penalty Cost</span>
                <span className="text-rose-400 font-mono font-bold">€{costMissed}</span>
              </div>
              <input
                type="range"
                min={20}
                max={500}
                step={10}
                value={costMissed}
                onChange={(e) => setCostMissed(parseInt(e.target.value))}
                className="w-full accent-rose-500 cursor-pointer"
              />
            </div>

            <div>
              <div className="flex justify-between text-xs font-semibold text-slate-300 mb-1">
                <span>Analyst Review Cost / Case</span>
                <span className="text-indigo-400 font-mono font-bold">€{costReview}</span>
              </div>
              <input
                type="range"
                min={5}
                max={50}
                value={costReview}
                onChange={(e) => setCostReview(parseInt(e.target.value))}
                className="w-full accent-indigo-500 cursor-pointer"
              />
            </div>
          </div>
        </div>

        {/* Right Simulation Outputs */}
        <div className="lg:col-span-8 space-y-6">
          {simulation && (
            <>
              {/* Recommendation Banner */}
              <div className="p-4 bg-indigo-950/60 border border-indigo-800 text-indigo-200 rounded-2xl text-xs flex items-start space-x-3">
                <CheckCircle2 className="w-5 h-5 text-indigo-400 shrink-0 mt-0.5" />
                <div>
                  <span className="font-bold text-white block mb-0.5">Operating Point Analysis</span>
                  <p>{simulation.recommendation}</p>
                </div>
              </div>

              {/* KPI Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                <div className="bg-surface p-4 rounded-xl border border-borderDark">
                  <span className="text-xs text-slate-400 font-semibold uppercase">Fraud Captured</span>
                  <div className="text-2xl font-bold text-emerald-400 mt-1">{simulation.fraud_capture_rate}%</div>
                  <span className="text-[11px] text-slate-400">{simulation.fraud_captured_count} / {simulation.total_fraud_count} cases</span>
                </div>

                <div className="bg-surface p-4 rounded-xl border border-borderDark">
                  <span className="text-xs text-slate-400 font-semibold uppercase">False Positive Rate</span>
                  <div className="text-2xl font-bold text-amber-400 mt-1">{simulation.false_positive_rate}%</div>
                  <span className="text-[11px] text-slate-400">{simulation.false_positive_count} false alarms</span>
                </div>

                <div className="bg-surface p-4 rounded-xl border border-borderDark">
                  <span className="text-xs text-slate-400 font-semibold uppercase">Approval Rate</span>
                  <div className="text-2xl font-bold text-white mt-1">{simulation.approval_rate}%</div>
                  <span className="text-[11px] text-slate-400">Review: {simulation.review_rate}%</span>
                </div>

                <div className="bg-surface p-4 rounded-xl border border-borderDark">
                  <span className="text-xs text-slate-400 font-semibold uppercase">Net Business Loss</span>
                  <div className="text-2xl font-bold text-rose-400 mt-1">€{simulation.total_financial_impact.toLocaleString()}</div>
                  <span className="text-[11px] text-slate-400">Combined impact</span>
                </div>
              </div>

              {/* Cost Breakdown Chart */}
              <div className="bg-surface p-5 rounded-2xl border border-borderDark">
                <h3 className="text-sm font-bold text-white mb-1">Financial Impact Breakdown (€)</h3>
                <p className="text-xs text-slate-400 mb-4">Trade-off components under current threshold settings</p>
                <div className="h-60">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={costBreakdownData}>
                      <XAxis dataKey="name" stroke="#94a3b8" fontSize={12} />
                      <YAxis stroke="#94a3b8" fontSize={12} />
                      <Tooltip contentStyle={{ backgroundColor: '#1f2937', borderColor: '#374151', borderRadius: '8px', color: '#fff' }} />
                      <Bar dataKey="amount" radius={[6, 6, 0, 0]}>
                        {costBreakdownData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
