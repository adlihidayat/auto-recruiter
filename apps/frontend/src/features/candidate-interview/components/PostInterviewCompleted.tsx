/**
 * What: Post-interview Confirmation & Next Steps View (Phase 3).
 * Why: Confirms to the candidate that their voice session has concluded and provides clear expectations.
 * Boundaries: Rendered when session phase is "completed".
 */

import React from "react";
import { CheckCircle2 } from "lucide-react";

export function PostInterviewCompleted() {
  return (
    <div className="w-full max-w-lg bg-white rounded-3xl border border-gray-200/90 shadow-xl p-8 text-center animate-in fade-in zoom-in-95 duration-200">
      <div className="w-20 h-20 rounded-3xl bg-emerald-50 border border-emerald-100 flex items-center justify-center mx-auto mb-6 text-emerald-600 shadow-xs">
        <CheckCircle2 className="w-10 h-10" strokeWidth="1.5" />
      </div>

      <h1 className="text-lg font-semibold text-gray-900 tracking-tight">
        Interview Completed!
      </h1>

      <div className="w-full flex justify-center">
        <p className="text-sm text-gray-600 max-w-100 mt-3 leading-relaxed">
          Thank you for taking the time to complete your interview. Your voice
          responses have been safely saved and sent for evaluation.
        </p>
      </div>

      <div className="mt-8 p-5 bg-gray-50 border border-gray-200 rounded-2xl text-xs text-gray-600 space-y-1.5 text-left">
        <p className="font-semibold text-gray-900">What happens next?</p>
        <p className="leading-relaxed font-medium">
          The hiring team will review your structured evaluation report and reach
          out regarding next steps.
        </p>
      </div>
    </div>
  );
}
