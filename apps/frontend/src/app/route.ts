import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

// Handle Supabase email confirmation redirects that land on root
// This catches cases where Supabase redirects to the domain root instead of /auth/callback
export async function GET(request: NextRequest) {
  const requestUrl = new URL(request.url);
  const code = requestUrl.searchParams.get("code");
  const token = requestUrl.searchParams.get("token");
  const type = requestUrl.searchParams.get("type");
  const access_token = requestUrl.searchParams.get("access_token");
  const refresh_token = requestUrl.searchParams.get("refresh_token");

  // If this looks like a Supabase auth redirect (has code, token, or access_token), forward to callback
  if (code || token || access_token) {
    console.log("[Root Route] Detected Supabase auth redirect", { 
      hasCode: !!code, 
      hasToken: !!token, 
      hasAccessToken: !!access_token,
      type 
    });
    
    const callbackUrl = new URL("/auth/callback", requestUrl.origin);
    
    // Copy all query parameters to the callback URL
    requestUrl.searchParams.forEach((value, key) => {
      callbackUrl.searchParams.set(key, value);
    });
    
    console.log("[Root Route] Redirecting to:", callbackUrl.toString());
    return NextResponse.redirect(callbackUrl);
  }

  // No auth params, continue to normal page rendering
  return NextResponse.next();
}

