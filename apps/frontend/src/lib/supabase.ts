import { createBrowserClient } from "@supabase/ssr";

// Get environment variables with fallbacks for build-time
// NEXT_PUBLIC_ vars are embedded at build time, so we need valid values
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || "https://placeholder.supabase.co";
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBsYWNlaG9sZGVyIiwicm9sZSI6ImFub24iLCJpYXQiOjE2NDUxOTIwMDAsImV4cCI6MTk2MDc2ODAwMH0.placeholder";

// Log which URL we're using (only in browser, not during build)
if (typeof window !== 'undefined') {
  console.log("[Supabase] Client URL:", supabaseUrl?.substring(0, 30) + "...");
  console.log("[Supabase] Using real Supabase:", !supabaseUrl?.includes("placeholder"));
}

// Create browser client using @supabase/ssr for cookie-based session management
// This ensures sessions are stored in cookies and can be read by middleware
export const supabase = createBrowserClient(supabaseUrl, supabaseAnonKey);

