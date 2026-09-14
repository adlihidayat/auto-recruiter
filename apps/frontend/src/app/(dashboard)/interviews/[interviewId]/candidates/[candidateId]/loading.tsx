import { CandidateReportSkeleton } from "@auto-recruiter/shared-ui";

/**
 * What: Next.js native loading boundary for Candidate Report route.
 * Why: Renders CandidateReportSkeleton during actual candidate report loading without mock timers.
 * Boundaries: Next.js App Router route loading boundary.
 */
export default function CandidateReportLoading() {
  return <CandidateReportSkeleton />;
}
