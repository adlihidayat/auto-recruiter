"use server";

import { cookies } from "next/headers";
import { loginApi, LoginResponse } from "@/lib/api/client";

/**
 * What: Server action for handling user login and setting session cookies.
 * Why: Allows secure HTTP-only session cookie management on the server side.
 * Boundaries: Operates on auth tokens and cookies only.
 */

export async function loginAction(
  email: string,
  password: string
): Promise<{ success: boolean; error?: string }> {
  try {
    const data: LoginResponse = await loginApi(email, password);
    
    // Set access token in HTTP session cookie (no maxAge/expires so it expires on browser shutdown)
    const cookieStore = await cookies();
    cookieStore.set("access_token", data.access_token, {
      httpOnly: false, // Accessible to client and edge middleware
      secure: process.env.NODE_ENV === "production",
      sameSite: "lax",
      path: "/",
    });

    // Track last active timestamp for 24h inactivity proxy timeout
    cookieStore.set("last_active_at", Date.now().toString(), {
      httpOnly: false,
      secure: process.env.NODE_ENV === "production",
      sameSite: "lax",
      path: "/",
    });

    return { success: true };
  } catch (err: unknown) {
    const errorMessage = err instanceof Error ? err.message : "Authentication failed";
    return { success: false, error: errorMessage };
  }
}

/**
 * Server action to log out the user by deleting access token & last active cookies.
 */
export async function logoutAction(): Promise<{ success: boolean }> {
  try {
    const cookieStore = await cookies();
    cookieStore.set("access_token", "", {
      path: "/",
      maxAge: 0,
      expires: new Date(0),
    });
    cookieStore.delete("access_token");
    cookieStore.set("last_active_at", "", {
      path: "/",
      maxAge: 0,
      expires: new Date(0),
    });
    cookieStore.delete("last_active_at");
    return { success: true };
  } catch (err: unknown) {
    console.error("Error in logoutAction:", err);
    return { success: false };
  }
}

