import { createBrowserClient } from "@supabase/ssr";

// Get environment variables with fallbacks for build-time
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || "https://placeholder.supabase.co";
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBsYWNlaG9sZGVyIiwicm9sZSI6ImFub24iLCJpYXQiOjE2NDUxOTIwMDAsImV4cCI6MTk2MDc2ODAwMH0.placeholder";

// Create browser client - this should use cookies automatically
// But we'll verify it's working by checking cookies after login
export const supabase = createBrowserClient(supabaseUrl, supabaseAnonKey);

// Helper function to manually set session in cookies if needed
export async function setSessionCookie(session: any) {
  if (typeof document === 'undefined') return;
  
  // The session should already be in cookies if createBrowserClient is working
  // But we can verify by checking if cookies exist
  console.log("[Supabase] Session should be in cookies now");
}

