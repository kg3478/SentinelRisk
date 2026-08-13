import React from "react";
import { ShieldAlert, Activity, CheckCircle2, Database } from "lucide-react";

export const Navbar = () => {
  return (
    <header className="h-16 bg-surface border-b border-borderDark flex items-center justify-between px-6 sticky top-0 z-40">
      <div className="flex items-center space-x-3">
        <div className="w-9 h-9 rounded-lg bg-indigo-600 flex items-center justify-center shadow-lg shadow-indigo-500/20">
          <ShieldAlert className="w-5 h-5 text-white" />
        </div>
        <div>
          <span className="font-bold text-lg text-white tracking-wide">Sentinel<span className="text-indigo-400">Risk</span></span>
          <span className="ml-2 text-xs px-2 py-0.5 rounded bg-indigo-950 text-indigo-300 border border-indigo-800 font-mono">v1.0.0</span>
        </div>
      </div>

      <div className="flex items-center space-x-4">
        {/* Real Data Provenance Badge */}
        <div className="hidden md:flex items-center space-x-2 px-3 py-1 rounded-full bg-slate-800/80 border border-slate-700 text-xs text-slate-300">
          <Database className="w-3.5 h-3.5 text-blue-400" />
          <span>ULB Credit Card Benchmark (284,807 tx)</span>
        </div>

        {/* Live System Health Badge */}
        <div className="flex items-center space-x-2 px-3 py-1 rounded-full bg-emerald-950/60 border border-emerald-800/60 text-xs text-emerald-400">
          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
          <span className="font-medium">Model Engine Active</span>
        </div>
      </div>
    </header>
  );
};
