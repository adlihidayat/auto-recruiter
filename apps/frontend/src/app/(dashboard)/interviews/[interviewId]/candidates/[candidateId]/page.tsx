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
  const { interviewId, candidateId } = await params;

  return (
    <CandidateReportView
      interviewId={interviewId}
      candidateId={candidateId}
    />
  );
}
