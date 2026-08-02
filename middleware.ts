import { NextResponse, type NextRequest } from "next/server";

const PUBLIC_PATHS = ["/login", "/callback"];
const REFRESH_COOKIE = "cch_refresh";

function isPublicPath(pathname: string): boolean {
  return PUBLIC_PATHS.some((path) => pathname === path || pathname.startsWith(`${path}/`));
}

export function middleware(request: NextRequest): NextResponse {
  const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL;

  // Mock-only mode: no route protection when backend is not configured.
  if (!apiBaseUrl) {
    return NextResponse.next();
  }

  const { pathname } = request.nextUrl;
  const hasRefreshCookie = Boolean(request.cookies.get(REFRESH_COOKIE));

  if (isPublicPath(pathname)) {
    if (hasRefreshCookie && pathname === "/login") {
      return NextResponse.redirect(new URL("/dashboard", request.url));
    }
    return NextResponse.next();
  }

  if (!hasRefreshCookie && pathname !== "/") {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("returnTo", pathname);
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)"],
};
