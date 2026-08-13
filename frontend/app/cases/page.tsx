"use client";

import React, { useState, useEffect } from "react";
import { ShieldQuestion, CheckCircle, XCircle, Search, Filter, MessageSquare, AlertTriangle } from "lucide-react";
import { fetchCases, overrideCaseDecision } from "../../lib/api";
import { DecisionBadge } from "../../components/DecisionBadge";

export default function CasesPage() {
  const [cases, setCases] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [filterStatus, setFilterStatus] = useState<string>("");
  const [selectedCase, setSelectedCase] = useState<any | null>(null);
  const [overrideDecision, setOverrideDecision] = useState<string>("APPROVED");
  const [overrideReason, setOverrideReason] = useState<string>("");
  const [submitting, setSubmitting] = useState<boolean>(false);

  const loadData = async () => {
    setLoading(true);
    try {
      const data = await fetchCases(filterStatus || undefined);
      setCases(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [filterStatus]);

  const handleOverrideSubmit = async () => {
    if (!selectedCase || !overrideReason.trim()) return;
    setSubmitting(true);
    try {
      await overrideCaseDecision(selectedCase.id, overrideDecision, overrideReason);
      setSelectedCase(null);
      setOverrideReason("");
      loadData();
    } catch (err) {
      alert("Failed to submit decision override");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center">
            <ShieldQuestion className="w-6 h-6 text-indigo-400 mr-2" />
            Fraud Investigation Queue & Case Management
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Review suspicious transactions flagged by the decision engine. Analysts can investigate evidence and override automated decisions.
          </p>
        </div>

        {/* Filter Dropdown */}
        <div className="flex items-center space-x-2 bg-surface p-1.5 rounded-xl border border-borderDark text-xs">
          <Filter className="w-4 h-4 text-slate-400 ml-2" />
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="bg-slate-900 text-white rounded-lg px-3 py-1.5 border border-borderDark focus:outline-none"
          >
            <option value="">All Statuses</option>
            <option value="NEW">New</option>
            <option value="INVESTIGATING">Investigating</option>
            <option value="APPROVED">Approved (Overridden)</option>
            <option value="REJECTED">Rejected (Confirmed Fraud)</option>
          </select>
        </div>
      </div>

      {/* Queue Table */}
      <div className="bg-surface rounded-2xl border border-borderDark overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-slate-800/80 text-xs text-slate-400 uppercase tracking-wider">
              <tr>
                <th className="p-4">Case Number</th>
                <th className="p-4">Amount</th>
                <th className="p-4">Risk Score</th>
                <th className="p-4">System Decision</th>
                <th className="p-4">Priority</th>
                <th className="p-4">Status</th>
                <th className="p-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-borderDark">
              {loading ? (
                <tr>
                  <td colSpan={7} className="p-8 text-center text-slate-500 text-sm">
                    Loading investigation queue...
                  </td>
                </tr>
              ) : cases.length === 0 ? (
                <tr>
                  <td colSpan={7} className="p-8 text-center text-slate-500 text-sm">
                    No cases match the selected filter.
                  </td>
                </tr>
              ) : (
                cases.map((c) => (
                  <tr key={c.id} className="hover:bg-slate-800/40 transition">
                    <td className="p-4 font-mono text-xs font-bold text-white">{c.case_number}</td>
                    <td className="p-4 font-semibold text-white">€{c.amount.toFixed(2)}</td>
                    <td className="p-4">
                      <span className={`font-bold ${c.risk_score >= 75 ? "text-rose-400" : "text-amber-400"}`}>
                        {c.risk_score}
                      </span> / 100
                    </td>
                    <td className="p-4"><DecisionBadge decision={c.original_decision} /></td>
                    <td className="p-4">
                      <span className={`text-xs px-2 py-0.5 rounded font-semibold ${
                        c.priority === "CRITICAL" ? "bg-rose-950 text-rose-400 border border-rose-800" : "bg-amber-950 text-amber-400 border border-amber-800"
                      }`}>
                        {c.priority}
                      </span>
                    </td>
                    <td className="p-4">
                      <span className={`text-xs px-2 py-0.5 rounded font-semibold ${
                        c.status === "APPROVED" ? "bg-emerald-950 text-emerald-400 border border-emerald-800" :
                        c.status === "REJECTED" ? "bg-rose-950 text-rose-400 border border-rose-800" : "bg-blue-950 text-blue-400 border border-blue-800"
                      }`}>
                        {c.status}
                      </span>
                    </td>
                    <td className="p-4 text-right">
                      <button
                        onClick={() => setSelectedCase(c)}
                        className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-lg transition"
                      >
                        Investigate & Override
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Override Modal */}
      {selectedCase && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-surfaceCard border border-borderDark rounded-2xl max-w-lg w-full p-6 space-y-5 shadow-2xl">
            <div className="flex justify-between items-center border-b border-borderDark pb-4">
              <div>
                <h3 className="text-lg font-bold text-white">Investigate Case {selectedCase.case_number}</h3>
                <p className="text-xs text-slate-400 mt-0.5">Amount: €{selectedCase.amount.toFixed(2)} | System Score: {selectedCase.risk_score}/100</p>
              </div>
              <button onClick={() => setSelectedCase(null)} className="text-slate-400 hover:text-white text-sm">✕</button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Analyst Override Decision</label>
                <select
                  value={overrideDecision}
                  onChange={(e) => setOverrideDecision(e.target.value)}
                  className="w-full bg-slate-900 text-white rounded-lg p-2.5 border border-borderDark text-sm focus:outline-none"
                >
                  <option value="APPROVED">APPROVE (Override System to ALLOW)</option>
                  <option value="REJECTED">REJECT (Confirm Fraud to BLOCK)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Audit Log Justification Reason</label>
                <textarea
                  rows={3}
                  value={overrideReason}
                  onChange={(e) => setOverrideReason(e.target.value)}
                  placeholder="Provide explicit business/investigation justification for this decision override..."
                  className="w-full bg-slate-900 text-white rounded-lg p-2.5 border border-borderDark text-sm focus:outline-none"
                />
              </div>
            </div>

            <div className="flex justify-end space-x-3 pt-2">
              <button
                onClick={() => setSelectedCase(null)}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-sm font-semibold"
              >
                Cancel
              </button>
              <button
                onClick={handleOverrideSubmit}
                disabled={submitting || !overrideReason.trim()}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white rounded-lg text-sm font-semibold transition"
              >
                {submitting ? "Submitting Override..." : "Confirm & Log Override"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
