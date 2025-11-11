import { createClient } from "@supabase/supabase-js";

// Get environment variables with fallbacks for build-time
// NEXT_PUBLIC_ vars are embedded at build time, so we need valid values
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || "https://placeholder.supabase.co";
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBsYWNlaG9sZGVyIiwicm9sZSI6ImFub24iLCJpYXQiOjE2NDUxOTIwMDAsImV4cCI6MTk2MDc2ODAwMH0.placeholder";

// Create client - will use real values if env vars are set in Vercel
// Placeholder values allow build to complete without errors
export const supabase = createClient(supabaseUrl, supabaseAnonKey);

