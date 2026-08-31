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
  id: string;
  email: string;
  username?: string | null;
  country?: string | null;
  born_date?: string | null;
  created_at?: string;
}

export async function checkUsernameApi(
  username: string
): Promise<{ username: string; available: boolean }> {
  const response = await fetch(
    `${API_BASE_URL}/api/auth/check-username?username=${encodeURIComponent(username)}`,
  );
  if (!response.ok) {
    throw new Error("Failed to check username availability");
  }
  return response.json();
}

export interface RegisterPayload {
  username: string;
  email: string;
  password: string;
  country?: string;
  born_date?: string;
}

export interface RegisterResponse {
  user: {
    id: string;
    email: string;
    username: string | null;
    country: string | null;
    born_date: string | null;
    created_at: string;
  };
  access_token: string;
  token_type: string;
}

export async function registerApi(
  payload: RegisterPayload
): Promise<RegisterResponse> {
  const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || "Failed to create account");
  }

  return response.json();
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

export interface BackendCreatorResponse {
  id: string;
  username?: string | null;
  email: string;
}

export interface BackendInterviewResponse {
  id: string;
  job_name: string;
  job_description: string;
  icon?: string | null;
  difficulty: string;
  num_goals: number;
  total_duration_minutes: number;
  domain_hint?: string | null;
  communication_weight: number;
  creator_id: string;
  creator?: BackendCreatorResponse | null;
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

/**
 * Fetch a single interview by ID.
 */
export async function getInterviewDetailApi(
  interviewId: string,
  token: string
): Promise<BackendInterviewResponse> {
  const response = await fetch(`${API_BASE_URL}/api/interviews/${interviewId}`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    handleAuthError(response.status);
    const errorData = await response.json().catch(() => ({ detail: "Failed to fetch interview detail" }));
    throw new Error(`Failed to fetch interview (${response.status}): ${errorData.detail || "Not found"}`);
  }

  return response.json();
}

export interface BackendGoalResponse {
  id: string;
  goal_ref: string;
  interview_id: string;
  topic: str;
  goal: str;
  passing_criteria: string[];
  pushback_triggers: Array<Record<string, unknown>>;
  wrong_answer_signals: string[];
  suggested_opening?: string | null;
  weight: number;
}

/**
 * Fetch all goals generated for a specific interview.
 */
export async function getInterviewGoalsApi(
  interviewId: string,
  token: string
): Promise<BackendGoalResponse[]> {
  const response = await fetch(`${API_BASE_URL}/api/interviews/${interviewId}/goals`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    handleAuthError(response.status);
    const errorData = await response.json().catch(() => ({ detail: "Failed to fetch goals" }));
    throw new Error(`Failed to fetch goals (${response.status}): ${errorData.detail || "Not found"}`);
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
  icon?: string;
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

export interface UpdateInterviewPayload {
  job_name?: string;
  job_description?: string;
  difficulty?: string;
  num_goals?: number;
  total_duration_minutes?: number;
  domain_hint?: string;
  communication_weight?: number;
  scheduled_at?: string | null;
}

/**
 * Update an existing interview position.
 */
export async function updateInterviewApi(
  interviewId: string,
  payload: UpdateInterviewPayload,
  token: string
): Promise<BackendInterviewResponse> {
  const response = await fetch(`${API_BASE_URL}/api/interviews/${interviewId}`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    handleAuthError(response.status);
    const errorData = await response.json().catch(() => ({ detail: "Failed to update interview" }));
    throw new Error(`Failed to update interview (${response.status}): ${errorData.detail || "Bad Request"}`);
  }

  return response.json();
}

/**
 * Delete an interview position and all associated records.
 */
export async function deleteInterviewApi(
  interviewId: string,
  token: string
): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/interviews/${interviewId}`, {
    method: "DELETE",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    handleAuthError(response.status);
    const errorData = await response.json().catch(() => ({ detail: "Failed to delete interview" }));
    throw new Error(`Failed to delete interview (${response.status}): ${errorData.detail || "Bad Request"}`);
  }
}

/**
 * Batch delete multiple interviews and all associated data in one atomic query.
 */
export async function batchDeleteInterviewsApi(
  interviewIds: string[],
  token: string
): Promise<{ deleted_count: number; status: string }> {
  const response = await fetch(`${API_BASE_URL}/api/interviews/batch-delete`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ interview_ids: interviewIds }),
  });
  if (!response.ok) {
    handleAuthError(response.status);
    throw new Error("Failed to batch delete interviews");
  }
  return response.json();
}

/**
 * Fetch top 5 recent interviews for current authenticated user.
 */
export async function getRecentInterviewsApi(
  token: string
): Promise<BackendInterviewResponse[]> {
  const response = await fetch(`${API_BASE_URL}/api/interviews/recents`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  if (!response.ok) {
    handleAuthError(response.status);
    throw new Error("Failed to fetch recent interviews");
  }
  return response.json();
}

/**
 * Explicitly record an interview view and return updated recents.
 */
export async function recordInterviewViewApi(
  interviewId: string,
  token: string
): Promise<BackendInterviewResponse[]> {
  const response = await fetch(`${API_BASE_URL}/api/interviews/${interviewId}/view`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  if (!response.ok) {
    handleAuthError(response.status);
    throw new Error("Failed to record interview view");
  }
  return response.json();
}
