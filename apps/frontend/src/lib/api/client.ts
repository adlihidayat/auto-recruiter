/**
 * What: Typed HTTP client for interacting with the backend API.
 * Why: Provides structured request execution for auth, interviews, and candidate queries.
 * Boundaries: Communicates over HTTP with apps/backend only.
 */

const API_BASE_URL =
  process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface UserMeResponse {
  email: string;
}

/**
 * Exchange email and password for a JWT access token via OAuth2 password flow.
 */
export async function loginApi(
  email: string,
  password: string
): Promise<LoginResponse> {
  const formData = new URLSearchParams();
  formData.append("username", email);
  formData.append("password", password);

  const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: formData.toString(),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: "Login failed" }));
    throw new Error(errorData.detail || "Invalid email or password");
  }

  return response.json();
}

function handleAuthError(status: number) {
  if (status === 401 && typeof window !== "undefined") {
    document.cookie = "access_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT;";
    // eslint-disable-next-line @next/next/no-location-assign-relative-destination
    window.location.href = "/login";
  }
}

/**
 * Fetch the logged-in user profile using the JWT bearer token.
 */
export async function getMeApi(token: string): Promise<UserMeResponse> {
  const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    handleAuthError(response.status);
    throw new Error("Failed to fetch user profile");
  }

  return response.json();
}

export interface BackendInterviewResponse {
  id: string;
  job_name: string;
  job_description: string;
  difficulty: string;
  num_goals: number;
  total_duration_minutes: number;
  domain_hint?: string | null;
  communication_weight: number;
  creator_id: string;
  status: string;
  scheduled_at?: string | null;
  created_at: string;
  updated_at: string;
}

/**
 * Fetch all interviews created by the current user.
 */
export async function getInterviewsApi(
  token: string
): Promise<BackendInterviewResponse[]> {
  const response = await fetch(`${API_BASE_URL}/api/interviews`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    handleAuthError(response.status);
    const errorData = await response.json().catch(() => ({ detail: "Failed to fetch interviews" }));
    throw new Error(`Failed to fetch interviews (${response.status}): ${errorData.detail || "Unauthorized"}`);
  }

  return response.json();
}

export interface BackendCandidateResponse {
  id: string;
  interview_id: string;
  email: string;
  first_name?: string | null;
  last_name?: string | null;
  status: string;
  composite_score?: number | null;
  recommendation?: string | null;
  room_token?: string | null;
  created_at: string;
}

/**
 * Fetch all candidates associated with a specific interview.
 */
export async function getCandidatesForInterviewApi(
  interviewId: string,
  token: string
): Promise<BackendCandidateResponse[]> {
  const response = await fetch(`${API_BASE_URL}/api/interviews/${interviewId}/candidates`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    handleAuthError(response.status);
    const errorData = await response.json().catch(() => ({ detail: "Failed to fetch candidates" }));
    throw new Error(`Failed to fetch candidates (${response.status}): ${errorData.detail || "Unauthorized"}`);
  }

  return response.json();
}

export interface BackendCandidateReportResponse {
  id: string;
  candidate_id: string;
  overall_confidence: string;
  reasoning: string;
  raw_report: {
    candidate_name?: string;
    candidate_email?: string;
    overall_score?: number;
    recommendation?: string;
    status_reason?: string;
    short_summary?: string | string[];
    highlight_bars?: Array<{ text: string; type: "pass" | "fail" }>;
    knowledge_score?: {
      score?: string;
      items?: Array<{ label: string; status: string; type: "pass" | "fail" }>;
      note?: string;
    };
    communication_score?: {
      score?: string;
      items?: Array<{ label: string; status: string; type: "pass" | "fail" }>;
      note?: string;
    };
    [key: string]: unknown;
  };
  grader_version: string;
  graded_at: string;
}

export interface BackendTranscriptResponse {
  id: string;
  candidate_id: string;
  goal_id: string;
  role: string;
  content: string;
  action?: string | null;
  reasoning?: string | null;
  trigger_matched?: string | null;
  flag_for_human_review: boolean;
  created_at: string;
}

/**
 * Fetch the detailed grading report for a specific candidate.
 */
export async function getCandidateReportApi(
  candidateId: string,
  token: string
): Promise<BackendCandidateReportResponse> {
  const response = await fetch(`${API_BASE_URL}/api/candidates/${candidateId}/report`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    handleAuthError(response.status);
    const errorData = await response.json().catch(() => ({ detail: "Failed to fetch candidate report" }));
    throw new Error(`Failed to fetch candidate report (${response.status}): ${errorData.detail || "Not found"}`);
  }

  return response.json();
}

/**
 * Fetch turn-by-turn conversation logs for a candidate.
 */
export async function getCandidateTranscriptsApi(
  candidateId: string,
  token: string
): Promise<BackendTranscriptResponse[]> {
  const response = await fetch(`${API_BASE_URL}/api/candidates/${candidateId}/transcripts`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    handleAuthError(response.status);
    const errorData = await response.json().catch(() => ({ detail: "Failed to fetch candidate transcripts" }));
    throw new Error(`Failed to fetch candidate transcripts (${response.status}): ${errorData.detail || "Not found"}`);
  }

  return response.json();
}

export interface CreateCandidatePayload {
  email: string;
  first_name?: string;
  last_name?: string;
}

export interface CreateInterviewPayload {
  job_name: string;
  job_description: string;
  difficulty?: string;
  num_goals?: number;
  total_duration_minutes?: number;
  domain_hint?: string;
  communication_weight?: number;
  scheduled_at?: string;
  candidates?: CreateCandidatePayload[];
}

export interface InterviewCreationResponse {
  interview: BackendInterviewResponse;
  candidates: BackendCandidateResponse[];
}

/**
 * Submit a new interview position and initial candidates to the backend.
 */
export async function createInterviewApi(
  payload: CreateInterviewPayload,
  token: string
): Promise<InterviewCreationResponse> {
  const response = await fetch(`${API_BASE_URL}/api/interviews`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    handleAuthError(response.status);
    const errorData = await response.json().catch(() => ({ detail: "Failed to create interview" }));
    throw new Error(`Failed to create interview (${response.status}): ${errorData.detail || "Bad Request"}`);
  }

  return response.json();
}
