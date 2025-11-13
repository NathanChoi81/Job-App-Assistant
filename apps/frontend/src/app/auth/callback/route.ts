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

    const { error } = await supabase.auth.exchangeCodeForSession(code);

    if (error) {
      console.error("[Auth Callback] Error exchanging code:", error);
      return NextResponse.redirect(new URL(`/login?error=${encodeURIComponent(error.message)}`, requestUrl.origin));
    }

    // Success - redirect to dashboard
    const response = NextResponse.redirect(new URL(next, requestUrl.origin));
    return response;
  }

  // No code provided, redirect to login
  return NextResponse.redirect(new URL("/login", requestUrl.origin));
}

