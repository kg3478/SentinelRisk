import React from "react";
import { CheckCircle, AlertTriangle, HelpCircle, OctagonAlert } from "lucide-react";

interface Props {
  decision: "ALLOW" | "CHALLENGE" | "REVIEW" | "BLOCK" | string;
}

export const DecisionBadge: React.FC<Props> = ({ decision }) => {
  switch (decision) {
    case "ALLOW":
      return (
        <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-950/80 text-emerald-400 border border-emerald-800/80">
          <CheckCircle className="w-3.5 h-3.5 mr-1" />
          ALLOW
        </span>
      );
    case "CHALLENGE":
      return (
        <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-950/80 text-amber-400 border border-amber-800/80">
          <HelpCircle className="w-3.5 h-3.5 mr-1" />
          CHALLENGE (2FA)
        </span>
      );
    case "REVIEW":
      return (
        <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-orange-950/80 text-orange-400 border border-orange-800/80">
          <AlertTriangle className="w-3.5 h-3.5 mr-1" />
          MANUAL REVIEW
        </span>
      );
    case "BLOCK":
    default:
      return (
        <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-950/80 text-rose-400 border border-rose-800/80">
          <OctagonAlert className="w-3.5 h-3.5 mr-1" />
          BLOCK
        </span>
      );
  }
};
