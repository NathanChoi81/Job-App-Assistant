import { createServerClient } from "@supabase/ssr";
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export async function middleware(req: NextRequest) {
  const res = NextResponse.next();
  
  // Get environment variables - these MUST be set in Vercel
  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
  
  // If env vars are missing, skip auth check (shouldn't happen in production)
  if (!supabaseUrl || !supabaseAnonKey) {
    console.error("[Middleware] Missing Supabase env vars - skipping auth check");
    return res;
  }
  
  const supabase = createServerClient(
    supabaseUrl,
    supabaseAnonKey,
    {
      cookies: {
        get(name: string) {
          return req.cookies.get(name)?.value;
        },
        set(name: string, value: string, options?: { path?: string; domain?: string; maxAge?: number; httpOnly?: boolean; secure?: boolean; sameSite?: 'strict' | 'lax' | 'none' }) {
          // Set cookies on both request and response
          req.cookies.set({
            name,
            value,
            ...options,
          });
          res.cookies.set({
            name,
            value,
            ...options,
          });
        },
        remove(name: string, options?: { path?: string; domain?: string; maxAge?: number; httpOnly?: boolean; secure?: boolean; sameSite?: 'strict' | 'lax' | 'none' }) {
          req.cookies.set({
            name,
            value: "",
            ...options,
          });
          res.cookies.set({
            name,
            value: "",
            maxAge: 0,
            ...options,
          });
        },
      },
    }
  );

  // Get session - this will read from cookies
  const {
    data: { session },
    error: sessionError,
  } = await supabase.auth.getSession();

  // Log for debugging (only in development)
  if (process.env.NODE_ENV === 'development') {
    console.log("[Middleware] Path:", req.nextUrl.pathname);
    console.log("[Middleware] Has session:", !!session);
    console.log("[Middleware] Session error:", sessionError);
    if (session) {
      console.log("[Middleware] User email:", session.user?.email);
    }
  }

  // Protect dashboard routes
  if (req.nextUrl.pathname.startsWith("/dashboard") && !session) {
    console.log("[Middleware] No session, redirecting to login");
    return NextResponse.redirect(new URL("/login", req.url));
  }

  // Redirect authenticated users away from login
  if (req.nextUrl.pathname === "/login" && session) {
    console.log("[Middleware] Has session, redirecting to dashboard");
    return NextResponse.redirect(new URL("/dashboard", req.url));
  }

  return res;
}

export const config = {
  matcher: ["/dashboard/:path*", "/login"],
};

