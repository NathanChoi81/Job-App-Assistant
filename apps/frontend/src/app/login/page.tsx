"use client";

import { useState } from "react";
import { supabase } from "@/lib/supabase";
import { useRouter } from "next/navigation";

// Force dynamic rendering (no static generation)
export const dynamic = 'force-dynamic';

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isSignUp, setIsSignUp] = useState(false);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      if (isSignUp) {
        const { error } = await supabase.auth.signUp({
          email,
          password,
        });
        if (error) throw error;
        alert("Check your email for confirmation link");
      } else {
        console.log("[Login] Attempting sign in with email:", email);
        const { data, error } = await supabase.auth.signInWithPassword({
          email,
          password,
        });
        
        console.log("[Login] Auth response received");
        console.log("[Login] Error:", error);
        console.log("[Login] Data:", data);
        
        if (error) {
          console.error("[Login] Sign in error:", error);
          alert(`Login failed: ${error.message}`);
          return;
        }
        
        if (!data.session) {
          console.error("[Login] No session in response!");
          alert("Login failed: No session received");
          return;
        }
        
        console.log("[Login] Session received:", data.session.user?.email);
        console.log("[Login] Access token exists:", !!data.session.access_token);
        
        // Verify session is actually set
        const { data: { session: verifiedSession } } = await supabase.auth.getSession();
        console.log("[Login] Verified session:", verifiedSession ? "YES" : "NO");
        
        if (!verifiedSession) {
          console.error("[Login] Session not set in Supabase client!");
          alert("Login failed: Session not set properly");
          return;
        }
        
        console.log("[Login] Redirecting to dashboard in 1 second...");
        
        // Give time for cookies to be set
        setTimeout(() => {
          console.log("[Login] Executing redirect NOW");
          window.location.href = "/dashboard";
        }, 1000);
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : "An error occurred";
      alert(message);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full bg-white rounded-lg shadow-md p-8">
        <h1 className="text-2xl font-bold mb-6">
          {isSignUp ? "Sign Up" : "Sign In"}
        </h1>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-3 py-2 border rounded-md"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-3 py-2 border rounded-md"
              required
            />
          </div>
          <button
            type="submit"
            className="w-full bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700"
          >
            {isSignUp ? "Sign Up" : "Sign In"}
          </button>
        </form>
        <button
          onClick={() => setIsSignUp(!isSignUp)}
          className="mt-4 text-blue-600 text-sm"
        >
          {isSignUp
            ? "Already have an account? Sign in"
            : "Don't have an account? Sign up"}
        </button>
      </div>
    </div>
  );
}

