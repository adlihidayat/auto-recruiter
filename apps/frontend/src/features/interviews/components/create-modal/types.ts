/**
 * What: TypeScript interfaces and types for the Create Interview Modal workflow.
 * Why: Centralizes data structures for form inputs, candidate listings, and step navigation.
 * Boundaries: Local to the create interview modal feature package.
 */


export type ModalStep = "form" | "loading" | "success";

export interface CandidateInput {
  email: string;
  first_name: string;
  last_name: string;
}

export interface InterviewFormData {
  icon: string;
  job_name: string;
  job_description: string;
  difficulty: string;
  num_goals: number;
  total_duration_minutes: number;
  domain_hint: string;
  communication_weight: number;
  scheduled_at: string;
}

export interface CreateInterviewModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCampaignCreated: () => void;
}
