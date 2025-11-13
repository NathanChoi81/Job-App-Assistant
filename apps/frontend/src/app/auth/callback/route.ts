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

    // Create response object first so we can set cookies on it
    const response = NextResponse.next();
    
    const supabase = createServerClient(supabaseUrl, supabaseAnonKey, {
      cookies: {
        get(name: string) {
          return request.cookies.get(name)?.value;
        },
        set(name: string, value: string, options: { path?: string; maxAge?: number; httpOnly?: boolean; secure?: boolean; sameSite?: 'strict' | 'lax' | 'none' }) {
          // Set cookies on the response object
          response.cookies.set({
            name,
            value,
            ...options,
          });
        },
        remove(name: string, options: { path?: string; maxAge?: number; httpOnly?: boolean; secure?: boolean; sameSite?: 'strict' | 'lax' | 'none' }) {
          response.cookies.set({
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

    console.log("[Auth Callback] Session created successfully", { 
      userId: data.session.user?.id,
      email: data.session.user?.email 
    });
    
    // Success - redirect to dashboard
    // Create redirect response and copy all cookies from the session exchange
    const redirectResponse = NextResponse.redirect(new URL(next, requestUrl.origin));
    
    // Copy all cookies from the session exchange to the redirect response
    response.cookies.getAll().forEach((cookie) => {
      redirectResponse.cookies.set(cookie.name, cookie.value, {
        path: cookie.path || '/',
        maxAge: cookie.maxAge,
        httpOnly: cookie.httpOnly,
        secure: cookie.secure ?? true,
        sameSite: cookie.sameSite as 'strict' | 'lax' | 'none' | undefined,
      });
    });
    
    console.log("[Auth Callback] Redirecting to:", next);
    return redirectResponse;
  }

  // No code provided, redirect to login
  return NextResponse.redirect(new URL("/login", requestUrl.origin));
}

