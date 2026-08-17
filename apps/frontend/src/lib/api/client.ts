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
    throw new Error("Failed to fetch user profile");
  }

  return response.json();
}
