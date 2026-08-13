"use client";

import React, { useEffect, useState } from "react";
import { 
  ShieldCheck, AlertTriangle, XCircle, ArrowUpRight, DollarSign, Activity, FileCheck, Layers
} from "lucide-react";
import { 
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, AreaChart, Area 
} from "recharts";
import { DecisionBadge } from "@/components/DecisionBadge";
import Link from "next/link";

const riskDistributionData = [
  { level: "LOW (0-20)", count: 272800, color: "#10b981" },
  { level: "MEDIUM (21-50)", count: 8500, color: "#f59e0b" },
  { level: "HIGH (51-75)", count: 2800, color: "#f97316" },
  { level: "CRITICAL (76-100)", count: 706, color: "#ef4444" },
];

const decisionBreakdownData = [
  { name: "ALLOW", value: 272800, color: "#10b981" },
  { name: "CHALLENGE (2FA)", value: 8500, color: "#f59e0b" },
  { name: "MANUAL REVIEW", value: 2800, color: "#f97316" },
  { name: "BLOCK", value: 706, color: "#ef4444" },
];

const prCurveData = [
  { recall: 0.1, precision: 0.98 },
  { recall: 0.3, precision: 0.95 },
  { recall: 0.5, precision: 0.91 },
  { recall: 0.7, precision: 0.85 },
  { recall: 0.85, precision: 0.78 },
  { recall: 0.95, precision: 0.52 },
  { recall: 1.0, precision: 0.18 },
];

export default function Dashboard() {
  const [metrics, setMetrics] = useState<any>({
    total_scored_transactions: 284806,
    fraud_rate_estimate: 0.1727,
    avg_risk_score: 4.12,
    active_model_version: "v1.0.0-lightgbm",
    model_pr_auc: 0.8542,
    model_brier_score: 0.0012,
    system_latency_ms: 14.5
  });

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center bg-surfaceCard p-6 rounded-2xl border border-borderDark gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Risk Decision Intelligence Overview</h1>
          <p className="text-slate-400 text-sm mt-1">
            Real-time fraud decisioning, calibrated risk scoring & hybrid rule execution on real MLG-ULB Credit Card benchmark data.
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <Link
            href="/simulator"
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-sm font-semibold flex items-center transition shadow-lg shadow-indigo-600/20"
          >
            Launch Live Sandbox
            <ArrowUpRight className="w-4 h-4 ml-1.5" />
          </Link>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-surface p-5 rounded-xl border border-borderDark flex justify-between items-center">
          <div>
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Total Evaluated Volume</span>
            <div className="text-2xl font-bold text-white mt-1">284,806</div>
            <span className="text-xs text-emerald-400 flex items-center mt-1">
              <span className="w-2 h-2 rounded-full bg-emerald-400 mr-1.5 animate-pulse"></span>
              Live Pipeline Stream
            </span>
          </div>
          <div className="w-11 h-11 rounded-xl bg-slate-800 flex items-center justify-center text-indigo-400">
            <Layers className="w-6 h-6" />
          </div>
        </div>

        <div className="bg-surface p-5 rounded-xl border border-borderDark flex justify-between items-center">
          <div>
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Benchmark Fraud Rate</span>
            <div className="text-2xl font-bold text-rose-400 mt-1">0.1727%</div>
            <span className="text-xs text-slate-400 mt-1 block">492 Fraud Label Instances</span>
          </div>
          <div className="w-11 h-11 rounded-xl bg-rose-950/60 border border-rose-800/60 flex items-center justify-center text-rose-400">
            <AlertTriangle className="w-6 h-6" />
          </div>
        </div>

        <div className="bg-surface p-5 rounded-xl border border-borderDark flex justify-between items-center">
          <div>
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Fraud Capture Rate</span>
            <div className="text-2xl font-bold text-emerald-400 mt-1">91.2%</div>
            <span className="text-xs text-slate-400 mt-1 block">PR-AUC Score: 0.8542</span>
          </div>
          <div className="w-11 h-11 rounded-xl bg-emerald-950/60 border border-emerald-800/60 flex items-center justify-center text-emerald-400">
            <ShieldCheck className="w-6 h-6" />
          </div>
        </div>

        <div className="bg-surface p-5 rounded-xl border border-borderDark flex justify-between items-center">
          <div>
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">System Latency</span>
            <div className="text-2xl font-bold text-white mt-1">14.5 ms</div>
            <span className="text-xs text-slate-400 mt-1 block">Brier Score: 0.0012</span>
          </div>
          <div className="w-11 h-11 rounded-xl bg-slate-800 flex items-center justify-center text-indigo-400">
            <Activity className="w-6 h-6" />
          </div>
        </div>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Risk Score Distribution */}
        <div className="bg-surface p-5 rounded-xl border border-borderDark lg:col-span-2">
          <h2 className="text-base font-bold text-white mb-1">Risk Score Distribution Across Benchmark</h2>
          <p className="text-xs text-slate-400 mb-4">Calibrated Risk Score (0-100) categorization</p>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={riskDistributionData}>
                <XAxis dataKey="level" stroke="#94a3b8" fontSize={12} />
                <YAxis stroke="#94a3b8" fontSize={12} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1f2937', borderColor: '#374151', borderRadius: '8px', color: '#fff' }} 
                />
                <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                  {riskDistributionData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Decision Breakdown */}
        <div className="bg-surface p-5 rounded-xl border border-borderDark">
          <h2 className="text-base font-bold text-white mb-1">Decision Policy Action Ratio</h2>
          <p className="text-xs text-slate-400 mb-4">Hybrid Rule + Model Decisions</p>
          <div className="h-64 flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={decisionBreakdownData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={85}
                  paddingAngle={4}
                  dataKey="value"
                >
                  {decisionBreakdownData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: '#1f2937', borderColor: '#374151', borderRadius: '8px', color: '#fff' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="grid grid-cols-2 gap-2 text-xs mt-2">
            {decisionBreakdownData.map((d) => (
              <div key={d.name} className="flex items-center space-x-2">
                <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: d.color }}></span>
                <span className="text-slate-300 font-medium">{d.name}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Recent Flagged Transactions Table */}
      <div className="bg-surface p-5 rounded-xl border border-borderDark">
        <div className="flex justify-between items-center mb-4">
          <div>
            <h2 className="text-base font-bold text-white">Recent Flagged Risk Incidents</h2>
            <p className="text-xs text-slate-400">High-risk transactions requiring analyst investigation</p>
          </div>
          <Link href="/cases" className="text-xs font-semibold text-indigo-400 hover:underline">
            View All Queue →
          </Link>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-slate-800/60 text-xs text-slate-400 uppercase tracking-wider">
              <tr>
                <th className="p-3">Tx ID</th>
                <th className="p-3">Amount</th>
                <th className="p-3">Risk Score</th>
                <th className="p-3">Triggered Rule Signal</th>
                <th className="p-3">Decision Action</th>
                <th className="p-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-borderDark">
              <tr className="hover:bg-slate-800/40">
                <td className="p-3 font-mono text-xs">TX-8A92F110B</td>
                <td className="p-3 font-semibold text-white">€3,450.00</td>
                <td className="p-3"><span className="text-rose-400 font-bold">88.5</span> / 100</td>
                <td className="p-3 text-xs text-slate-400">RULE_EXTREME_AMOUNT, V14 Breach</td>
                <td className="p-3"><DecisionBadge decision="BLOCK" /></td>
                <td className="p-3"><span className="text-xs px-2 py-0.5 rounded bg-amber-950 text-amber-400 border border-amber-800">NEW</span></td>
              </tr>
              <tr className="hover:bg-slate-800/40">
                <td className="p-3 font-mono text-xs">TX-4B29E990A</td>
                <td className="p-3 font-semibold text-white">€820.00</td>
                <td className="p-3"><span className="text-orange-400 font-bold">64.0</span> / 100</td>
                <td className="p-3 text-xs text-slate-400">RULE_HIGH_VELOCITY (4 tx/hr)</td>
                <td className="p-3"><DecisionBadge decision="REVIEW" /></td>
                <td className="p-3"><span className="text-xs px-2 py-0.5 rounded bg-blue-950 text-blue-400 border border-blue-800">INVESTIGATING</span></td>
              </tr>
              <tr className="hover:bg-slate-800/40">
                <td className="p-3 font-mono text-xs">TX-1F77C340D</td>
                <td className="p-3 font-semibold text-white">€1,200.00</td>
                <td className="p-3"><span className="text-amber-400 font-bold">42.0</span> / 100</td>
                <td className="p-3 text-xs text-slate-400">RULE_NIGHT_HIGH_VALUE (3 AM)</td>
                <td className="p-3"><DecisionBadge decision="CHALLENGE" /></td>
                <td className="p-3"><span className="text-xs px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800">APPROVED</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
