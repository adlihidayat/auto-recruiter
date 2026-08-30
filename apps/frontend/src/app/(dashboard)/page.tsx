import React, { Suspense } from "react";
import DashboardView from "@/features/interviews/components/DashboardView";

export const metadata = {
  title: "Auto-Recruiter | HR Talent Acquisition Dashboard",
  description:
    "Autonomous AI-powered interview platform orchestrating Question Generation, Real-Time Voice Interviewing, and Evaluation Grading.",
};

export default function DashboardPage() {
  return (
    <Suspense
      fallback={
        <div className="absolute inset-0 flex items-center justify-center text-xs text-gray-500">
          Loading dashboard...
        </div>
      }
    >
      <DashboardView />
    </Suspense>
  );
}
