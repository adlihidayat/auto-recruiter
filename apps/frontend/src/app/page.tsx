import React, { Suspense } from "react";
import Navbar from "@/components/layout/Navbar";
import DashboardView from "@/features/interviews/components/DashboardView";

/**
 * What: Main entry point page for the HR Recruiting Dashboard.
 * Why: Server Component page rendering top navigation shell and dashboard feature view with Suspense boundaries.
 * Boundaries: Thin page layout wrapping dashboard feature components.
 */

export const metadata = {
  title: "Auto-Recruiter | HR Talent Acquisition Dashboard",
  description:
    "Autonomous AI-powered interview platform orchestrating Question Generation, Real-Time Voice Interviewing, and Evaluation Grading.",
};

export default function DashboardPage() {
  return (
    <div className="min-h-screen bg-[#080c14] text-slate-100 flex flex-col selection:bg-indigo-500 selection:text-white">
      <Navbar />
      <div className="flex-1">
        <Suspense
          fallback={
            <div className="max-w-7xl mx-auto px-4 py-12 text-center text-xs text-slate-500">
              Loading dashboard telemetry...
            </div>
          }
        >
          <DashboardView />
        </Suspense>
      </div>
    </div>
  );
}
