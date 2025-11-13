import { createServerClient } from "@supabase/ssr";
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export async function GET(request: NextRequest) {
  const requestUrl = new URL(request.url);
  const code = requestUrl.searchParams.get("code");
  const next = requestUrl.searchParams.get("next") || "/dashboard";
  const debug = requestUrl.searchParams.get("debug") === "true";

  console.log("[Auth Callback] === START ===");
  console.log("[Auth Callback] URL:", requestUrl.toString());
  console.log("[Auth Callback] Has code:", !!code);
  console.log("[Auth Callback] Code length:", code?.length || 0);
  console.log("[Auth Callback] Next:", next);
  console.log("[Auth Callback] All query params:", Object.fromEntries(requestUrl.searchParams.entries()));

  if (code) {
    const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
    const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

    if (!supabaseUrl || !supabaseAnonKey) {
      console.error("[Auth Callback] Missing Supabase env vars");
      console.error("[Auth Callback] supabaseUrl:", !!supabaseUrl);
      console.error("[Auth Callback] supabaseAnonKey:", !!supabaseAnonKey);
      
      if (debug) {
        return new NextResponse(
          `Debug: Missing env vars. URL: ${!!supabaseUrl}, Key: ${!!supabaseAnonKey}`,
          { status: 500 }
        );
      }
      return NextResponse.redirect(new URL("/login?error=config", requestUrl.origin));
    }

    console.log("[Auth Callback] Env vars present, creating Supabase client...");

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

    console.log("[Auth Callback] Exchanging code for session...");
    let data: { session: { user: { id?: string; email?: string } } | null } | null = null;
    let error: { message: string } | null = null;
    
    try {
      const result = await supabase.auth.exchangeCodeForSession(code);
      data = result.data as { session: { user: { id?: string; email?: string } } | null } | null;
      error = result.error;
      console.log("[Auth Callback] Exchange result:", { 
        hasData: !!data, 
        hasError: !!error,
        hasSession: !!data?.session,
        errorMessage: error?.message 
      });
    } catch (err) {
      console.error("[Auth Callback] Exception during exchange:", err);
      error = { message: err instanceof Error ? err.message : String(err) };
      if (debug) {
        return new NextResponse(
          `Debug: Exception during exchange: ${err instanceof Error ? err.message : String(err)}`,
          { status: 500 }
        );
      }
    }

    if (error) {
      console.error("[Auth Callback] Error exchanging code:", error);
      console.error("[Auth Callback] Error details:", JSON.stringify(error, null, 2));
      const errorMsg = error.message.includes("expired") || error.message.includes("invalid")
        ? "Your confirmation link has expired. Please request a new confirmation email."
        : error.message;
      
      if (debug) {
        return new NextResponse(
          `Debug: Exchange error: ${errorMsg}\n\nFull error: ${JSON.stringify(error, null, 2)}`,
          { status: 400 }
        );
      }
      return NextResponse.redirect(new URL(`/login?error=${encodeURIComponent(errorMsg)}`, requestUrl.origin));
    }

    // Success - verify session was created
    if (!data || !data.session) {
      console.error("[Auth Callback] No session after code exchange");
      console.error("[Auth Callback] Data received:", JSON.stringify(data, null, 2));
      
      if (debug) {
        return new NextResponse(
          `Debug: No session created. Data: ${JSON.stringify(data, null, 2)}`,
          { status: 400 }
        );
      }
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
    const cookies = response.cookies.getAll();
    console.log("[Auth Callback] Cookies to copy:", cookies.length);
    cookies.forEach((cookie) => {
      console.log("[Auth Callback] Setting cookie:", cookie.name, "path:", cookie.path);
      redirectResponse.cookies.set(cookie.name, cookie.value, {
        path: cookie.path || '/',
        maxAge: cookie.maxAge,
        httpOnly: cookie.httpOnly,
        secure: cookie.secure ?? true,
        sameSite: cookie.sameSite as 'strict' | 'lax' | 'none' | undefined,
      });
    });
    
    console.log("[Auth Callback] Redirecting to:", next);
    console.log("[Auth Callback] === SUCCESS ===");
    
    if (debug) {
      return new NextResponse(
        `Debug: Success! Session created for ${data.session.user?.email}. Cookies: ${cookies.length}. Would redirect to: ${next}`,
        { status: 200 }
      );
    }
    
    return redirectResponse;
  }

  // No code provided, redirect to login
  console.log("[Auth Callback] No code provided");
  console.log("[Auth Callback] === END (NO CODE) ===");
  
  if (debug) {
    return new NextResponse("Debug: No code parameter in URL", { status: 400 });
  }
  
  return NextResponse.redirect(new URL("/login", requestUrl.origin));
}

