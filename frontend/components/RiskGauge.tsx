import React from "react";

interface Props {
  score: number; // 0 - 100
  level: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL" | string;
}

export const RiskGauge: React.FC<Props> = ({ score, level }) => {
  let color = "#10b981"; // Emerald
  if (score > 20) color = "#f59e0b"; // Amber
  if (score > 50) color = "#f97316"; // Orange
  if (score > 75) color = "#ef4444"; // Red

  const radius = 42;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  return (
    <div className="flex flex-col items-center justify-center p-4">
      <div className="relative w-28 h-28 flex items-center justify-center">
        <svg className="w-full h-full transform -rotate-90">
          <circle
            cx="56"
            cy="56"
            r={radius}
            stroke="#1f2937"
            strokeWidth="8"
            fill="transparent"
          />
          <circle
            cx="56"
            cy="56"
            r={radius}
            stroke={color}
            strokeWidth="8"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            fill="transparent"
            className="transition-all duration-700 ease-out"
          />
        </svg>
        <div className="absolute flex flex-col items-center justify-center">
          <span className="text-2xl font-bold text-white tracking-tight">{score}</span>
          <span className="text-[10px] text-slate-400 font-medium uppercase tracking-wider">/ 100</span>
        </div>
      </div>
      <span
        className="mt-2 text-xs font-semibold px-2.5 py-0.5 rounded uppercase tracking-wider"
        style={{ color: color, backgroundColor: `${color}15`, border: `1px solid ${color}30` }}
      >
        {level} RISK
      </span>
    </div>
  );
};
