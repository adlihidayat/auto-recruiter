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
