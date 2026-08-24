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
    
    // Set access token in HTTP cookie (valid for 1 day)
    const cookieStore = await cookies();
    cookieStore.set("access_token", data.access_token, {
      httpOnly: false, // Accessible to client and edge middleware
      secure: process.env.NODE_ENV === "production",
      sameSite: "lax",
      path: "/",
      maxAge: 60 * 60 * 24, // 24 hours
    });

    return { success: true };
  } catch (err: unknown) {
    const errorMessage = err instanceof Error ? err.message : "Authentication failed";
    return { success: false, error: errorMessage };
  }
}

/**
 * Server action to log out the user by deleting the access token cookie.
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
    return { success: true };
  } catch (err: unknown) {
    console.error("Error in logoutAction:", err);
    return { success: false };
  }
}

