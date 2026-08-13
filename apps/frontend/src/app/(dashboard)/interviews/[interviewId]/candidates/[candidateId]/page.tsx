import React from "react";
import CandidateReportView from "@/features/candidates/components/CandidateReportView";
import { Metadata } from "next";

export const metadata: Metadata = {
  title: "Candidate Report | Auto-Recruiter",
  description: "Detailed AI candidate prescreen evaluation report",
};

export default async function CandidateReportPage({
  params,
}: {
  params: Promise<{ interviewId: string; candidateId: string }>;
}) {
  await params; // Await params per Next.js 15 convention

  return (
    <main className="w-full min-h-screen bg-[#F4F4F5]">
      <CandidateReportView />
    </main>
  );
}
