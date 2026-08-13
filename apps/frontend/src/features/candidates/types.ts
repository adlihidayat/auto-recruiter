export type ConfidenceLevel = "Low" | "Medium" | "Medium-High" | "High";
export type GapType = "scored low" | "insufficient evidence" | "single data point";
export type SeverityLevel = "low" | "medium" | "high";
export type CriticalityLevel = "must-have" | "nice-to-have" | "cross-goal";
export type PushbackResponseType = 
  | "defended_with_new_info"
  | "conceded_and_corrected"
  | "defensive_no_new_info"
  | "repeated_unchanged"
  | null;

export interface Citation {
  quote: string;
  turnReference: number;
}

export interface CandidateProfile {
  name: string;
  roleApplied: {
    jobTitle: string;
    team: string;
  };
  interviewMetadata: {
    dateInterviewed: string;
    dateReportGenerated: string;
    interviewStage: string;
    interviewers: string[];
  };
  goalsAssessedCount: string;
  overallConfidence: ConfidenceLevel;
}

export interface MustHaveGoal {
  id: string;
  label: string;
  met: boolean;
}

export interface MustHaveGate {
  goals: MustHaveGoal[];
  gateResult: "pass" | "fail";
}

export interface OverallRecommendation {
  label: "Advance" | "Advance with follow-up" | "Hold";
  reasoning: string;
  ruleApplied: string;
}

export interface StrengthItem {
  goalOrSignalLabel: string;
  citedQuote: string;
  turnReference: number;
}

export interface ConcernItem {
  goalOrSignalLabel: string;
  gapTypeTag: GapType;
  citedQuote: string;
  turnReference: number;
}

export interface RedFlag {
  description: string;
  relatedGoalId: string | null;
  severity: SeverityLevel;
}

export interface CommunicationSignal {
  label: "flow_control" | "active_listening" | "structure" | "assertiveness" | "objection_handling";
  sentence: string;
  rationale: string;
  score: number;
}

export interface CommunicationRead {
  overallScore: number;
  overallConfidence: ConfidenceLevel;
  signals: CommunicationSignal[];
}

export interface PerGoalDetail {
  id: string;
  title: string;
  criticality: CriticalityLevel;
  addressed: boolean;
  score: number | null;
  confidence: ConfidenceLevel | null;
  rationale: string;
  criteriaMatch: {
    passingCriteriaMet: boolean;
    wrongAnswerSignalsTriggered: boolean;
  };
  citations: Citation[];
  pushback: {
    triggered: boolean;
    responseType: PushbackResponseType;
  };
}

export interface CandidateReport {
  id: string;
  profile: CandidateProfile;
  mustHaveGate: MustHaveGate;
  recommendation: OverallRecommendation;
  strengths: StrengthItem[];
  concerns: ConcernItem[];
  redFlags: RedFlag[];
  communicationRead: CommunicationRead;
  goalDetails: PerGoalDetail[];
}
