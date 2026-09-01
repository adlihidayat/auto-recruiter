import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

/**
 * What: Edge proxy gating authenticated routes.
 * Why: Next.js 15.2+ proxy convention replacing deprecated middleware.ts.
 * Boundaries: Inspects session cookies at edge before route rendering.
 */
const ONE_DAY_MS = 24 * 60 * 60 * 1000; // 24 hours in milliseconds

export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const token = request.cookies.get("access_token")?.value;
  const lastActiveStr = request.cookies.get("last_active_at")?.value;

  const isAuthRoute =
    pathname.startsWith("/login") ||
    pathname.startsWith("/sign-in") ||
    pathname.startsWith("/create-account");
  const isDashboardRoute =
    pathname === "/" ||
    pathname.startsWith("/interviews") ||
    pathname.startsWith("/settings");

  // Bypass redirection for Next.js Server Actions
  if (request.headers.has("next-action")) {
    return NextResponse.next();
  }

  const now = Date.now();

  // Inactivity Timeout Check (1 day / 24h of no user interaction)
  if (token && lastActiveStr) {
    const lastActiveTime = parseInt(lastActiveStr, 10);
    if (!isNaN(lastActiveTime) && now - lastActiveTime > ONE_DAY_MS) {
      // Inactive for more than 24 hours -> terminate session
      const loginUrl = new URL("/login", request.url);
      const response = NextResponse.redirect(loginUrl);
      response.cookies.delete("access_token");
      response.cookies.delete("last_active_at");
      return response;
    }
  }

  // Redirect unauthenticated user trying to access dashboard to /login
  if (isDashboardRoute && !token) {
    const loginUrl = new URL("/login", request.url);
    return NextResponse.redirect(loginUrl);
  }

  // Redirect authenticated user trying to access auth pages to dashboard /
  if (isAuthRoute && token) {
    const dashboardUrl = new URL("/", request.url);
    const response = NextResponse.redirect(dashboardUrl);
    response.cookies.set("last_active_at", now.toString(), {
      path: "/",
      sameSite: "lax",
      secure: process.env.NODE_ENV === "production",
    });
    return response;
  }

  // Update last_active_at timestamp for active sessions
  const response = NextResponse.next();
  if (token) {
    response.cookies.set("last_active_at", now.toString(), {
      path: "/",
      sameSite: "lax",
      secure: process.env.NODE_ENV === "production",
    });
  }

  return response;
}

// Export middleware alias for backwards compatibility
export { proxy as middleware };

export const config = {
  matcher: [
    /*
     * Match all request paths except for:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public assets
     */
    "/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)",
  ],
};
