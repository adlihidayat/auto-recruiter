import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

/**
 * What: Edge proxy gating authenticated routes.
 * Why: Next.js 15.2+ proxy convention replacing deprecated middleware.ts.
 * Boundaries: Inspects session cookies at edge before route rendering.
 */
export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const token = request.cookies.get("access_token")?.value;

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

  // Redirect unauthenticated user trying to access dashboard to /login
  if (isDashboardRoute && !token) {
    const loginUrl = new URL("/login", request.url);
    return NextResponse.redirect(loginUrl);
  }

  // Redirect authenticated user trying to access auth pages to dashboard /
  if (isAuthRoute && token) {
    const dashboardUrl = new URL("/", request.url);
    return NextResponse.redirect(dashboardUrl);
  }

  return NextResponse.next();
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
