import { InterviewDetailSkeleton } from "@auto-recruiter/shared-ui";

/**
 * What: Next.js native loading boundary for Interview Detail route.
 * Why: Renders InterviewDetailSkeleton during actual data loading without mock timers.
 * Boundaries: Next.js App Router route loading boundary.
 */
export default function InterviewDetailLoading() {
  return <InterviewDetailSkeleton />;
}
