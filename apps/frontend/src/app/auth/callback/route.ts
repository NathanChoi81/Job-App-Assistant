import { createServerClient } from "@supabase/ssr";
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export async function GET(request: NextRequest) {
  const requestUrl = new URL(request.url);
  const code = requestUrl.searchParams.get("code");
  const next = requestUrl.searchParams.get("next") || "/dashboard";

  if (code) {
    const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
    const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

    if (!supabaseUrl || !supabaseAnonKey) {
      console.error("[Auth Callback] Missing Supabase env vars");
      return NextResponse.redirect(new URL("/login?error=config", requestUrl.origin));
    }

    const supabase = createServerClient(supabaseUrl, supabaseAnonKey, {
      cookies: {
        get(name: string) {
          return request.cookies.get(name)?.value;
        },
        set(name: string, value: string, options: { path?: string; maxAge?: number; httpOnly?: boolean; secure?: boolean; sameSite?: 'strict' | 'lax' | 'none' }) {
          request.cookies.set({
            name,
            value,
            ...options,
          });
        },
        remove(name: string, options: { path?: string; maxAge?: number; httpOnly?: boolean; secure?: boolean; sameSite?: 'strict' | 'lax' | 'none' }) {
          request.cookies.set({
            name,
            value: "",
            maxAge: 0,
            ...options,
          });
        },
      },
    });

    const { data, error } = await supabase.auth.exchangeCodeForSession(code);

    if (error) {
      console.error("[Auth Callback] Error exchanging code:", error);
      const errorMsg = error.message.includes("expired") || error.message.includes("invalid")
        ? "Your confirmation link has expired. Please request a new confirmation email."
        : error.message;
      return NextResponse.redirect(new URL(`/login?error=${encodeURIComponent(errorMsg)}`, requestUrl.origin));
    }

    // Success - verify session was created
    if (!data.session) {
      console.error("[Auth Callback] No session after code exchange");
      return NextResponse.redirect(new URL("/login?error=No session created", requestUrl.origin));
    }

    console.log("[Auth Callback] Session created successfully, redirecting to dashboard");
    
    // Success - redirect to dashboard
    // Use a full page redirect to ensure cookies are set
    const response = NextResponse.redirect(new URL(next, requestUrl.origin));
    
    // Ensure cookies are properly set
    return response;
  }

  // No code provided, redirect to login
  return NextResponse.redirect(new URL("/login", requestUrl.origin));
}

