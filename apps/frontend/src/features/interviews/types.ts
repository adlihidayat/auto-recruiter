/**
 * What: Domain TypeScript interfaces and types for interview campaigns, candidate evaluation, and agent pipeline stages.
 * Why: Defines strict frontend schemas matching backend entities without relying on unsafe 'any' types.
 * Boundaries: Does not handle runtime API queries or state mutations.
 */

export type PipelineStage =
  | "QUESTION_MAKER"
  | "INTERVIEWER_LIVE"
  | "GRADER_EVALUATING"
  | "COMPLETED"
  | "FAILED";

export interface QuestionItem {
  id: string;
  category: string;
  questionText: string;
  difficultyLevel: "Easy" | "Medium" | "Hard" | "Staff";
  targetSkill: string;
}

export interface CandidateRecord {
  id: string;
  fullName: string;
  emailAddress: string;
  status: "Invited" | "In_Progress" | "Evaluated" | "Passed" | "Rejected";
  overallScore?: number;
  technicalDepthScore?: number;
  communicationScore?: number;
  interviewCompletedAt?: string;
}

export interface InterviewCampaign {
  id: string;
  jobTitle: string;
  departmentName: string;
  targetSeniority: "Junior" | "Mid-Level" | "Senior" | "Lead" | "Principal";
  currentPipelineStage: PipelineStage;
  activeCandidateCount: number;
  evaluatedCandidateCount: number;
  createdAtTimestamp: string;
  questionSuite: QuestionItem[];
  candidatesList: CandidateRecord[];
  agentSummary?: string;
}
