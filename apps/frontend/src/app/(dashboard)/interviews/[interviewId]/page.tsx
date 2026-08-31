import React from "react";
import InterviewDetailView from "@/features/interviews/components/InterviewDetailView";

/**
 * What: Next.js App Router Page for single interview campaign detail.
 * Why: Receives route parameters and renders InterviewDetailView client component.
 * Boundaries: Server Component entrypoint for /interviews/[interviewId].
 */
export default async function InterviewDetailPage({
  params,
}: {
  params: Promise<{ interviewId: string }>;
}) {
  const { interviewId } = await params;
  return <InterviewDetailView interviewId={interviewId} />;
}
