"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard, Zap, ShieldQuestion, Sliders, Activity } from "lucide-react";

export const Sidebar = () => {
  const pathname = usePathname();

  const navItems = [
    { name: "Risk Overview", href: "/", icon: LayoutDashboard },
    { name: "Live Simulator", href: "/simulator", icon: Zap },
    { name: "Investigation Queue", href: "/cases", icon: ShieldQuestion },
    { name: "Decision Simulator", href: "/thresholds", icon: Sliders },
    { name: "Model Monitoring", href: "/monitoring", icon: Activity },
  ];

  return (
    <aside className="w-64 bg-surface border-r border-borderDark flex flex-col justify-between p-4 hidden md:flex min-h-[calc(100vh-4rem)]">
      <div className="space-y-1">
        <div className="px-3 py-2 text-xs font-semibold text-slate-400 uppercase tracking-wider">
          Decision Platform
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                isActive
                  ? "bg-indigo-600/15 text-indigo-400 border border-indigo-500/30"
                  : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50"
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? "text-indigo-400" : "text-slate-400"}`} />
              <span>{item.name}</span>
            </Link>
          );
        })}
      </div>

      <div className="p-3 bg-surfaceCard rounded-xl border border-borderDark text-xs text-slate-400 space-y-1">
        <div className="font-semibold text-slate-200">SentinelRisk Engine</div>
        <div>Calibrated LightGBM + Rule Hybrid</div>
        <div className="text-slate-500">PR-AUC: 0.8542 | Brier: 0.0012</div>
      </div>
    </aside>
  );
};
