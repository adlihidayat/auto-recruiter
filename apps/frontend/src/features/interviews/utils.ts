import { BackendInterviewResponse } from "@/lib/api/client";
import { InterviewCampaign, PipelineStage } from "./types";

/**
 * Maps a backend Interview model to the frontend InterviewCampaign interface.
 */
export function mapBackendInterviewToCampaign(
  backendInterview: BackendInterviewResponse
): InterviewCampaign {
  const dateToFormat = backendInterview.scheduled_at ? backendInterview.scheduled_at : backendInterview.created_at;
  const formattedDate = new Date(dateToFormat).toLocaleDateString("en-GB", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  });

  // Normalize status string to PipelineStage
  let pipelineStage: PipelineStage = "QUESTION_MAKER";
  const upperStatus = backendInterview.status?.toUpperCase() || "";
  if (upperStatus.includes("COMPLET") || upperStatus.includes("FINISH")) {
    pipelineStage = "COMPLETED";
  } else if (upperStatus.includes("LIVE") || upperStatus.includes("SCHEDULED")) {
    pipelineStage = "INTERVIEWER_LIVE";
  } else if (upperStatus.includes("EVALUAT") || upperStatus.includes("GRADE")) {
    pipelineStage = "GRADER_EVALUATING";
  } else if (upperStatus.includes("FAIL")) {
    pipelineStage = "FAILED";
  } else {
    pipelineStage = "QUESTION_MAKER";
  }

  // Map difficulty string to target seniority
  let targetSeniority: "Junior" | "Mid-Level" | "Senior" | "Lead" | "Principal" = "Senior";
  const diffLower = backendInterview.difficulty.toLowerCase();
  if (diffLower.includes("junior")) targetSeniority = "Junior";
  else if (diffLower.includes("mid")) targetSeniority = "Mid-Level";
  else if (diffLower.includes("lead")) targetSeniority = "Lead";
  else if (diffLower.includes("principal")) targetSeniority = "Principal";

  const creatorName =
    backendInterview.creator?.username ||
    backendInterview.creator?.email?.split("@")[0] ||
    "HR Manager";

  return {
    id: backendInterview.id,
    jobTitle: backendInterview.job_name,
    departmentName: backendInterview.domain_hint || "Core",
    targetSeniority,
    currentPipelineStage: pipelineStage,
    activeCandidateCount: 0,
    evaluatedCandidateCount: 0,
    createdAtTimestamp: formattedDate,
    agentSummary: backendInterview.job_description,
    questionSuite: [],
    candidatesList: [],
    creatorName,
    icon: backendInterview.icon || "💼",
  };
}
