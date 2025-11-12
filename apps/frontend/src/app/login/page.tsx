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
    console.log("[Login] FORM SUBMITTED - Starting login process");
    console.log("[Login] Email:", email);
    console.log("[Login] Is sign up:", isSignUp);
    
    try {
      if (isSignUp) {
        console.log("[Login] Sign up flow");
        const { error } = await supabase.auth.signUp({
          email,
          password,
        });
        if (error) throw error;
        alert("Check your email for confirmation link");
      } else {
        console.log("[Login] === SIGN IN FLOW START ===");
        console.log("[Login] Calling signInWithPassword...");
        
        const result = await supabase.auth.signInWithPassword({
          email,
          password,
        });
        
        console.log("[Login] === SIGN IN RESPONSE RECEIVED ===");
        console.log("[Login] Full result:", JSON.stringify(result, null, 2));
        console.log("[Login] Error:", result.error);
        console.log("[Login] Data:", result.data);
        console.log("[Login] Session:", result.data?.session);
        console.log("[Login] User:", result.data?.user);
        
        if (result.error) {
          console.error("[Login] ERROR:", result.error);
          alert(`Login failed: ${result.error.message}`);
          return;
        }
        
        if (!result.data?.session) {
          console.error("[Login] NO SESSION IN RESPONSE!");
          alert("Login failed: No session received");
          return;
        }
        
        console.log("[Login] Session exists! User email:", result.data.session.user?.email);
        console.log("[Login] Access token:", result.data.session.access_token?.substring(0, 20) + "...");
        
        // Wait a bit for session to be persisted
        console.log("[Login] Waiting 500ms for session to be set...");
        await new Promise(resolve => setTimeout(resolve, 500));
        
        // Verify session is actually set
        console.log("[Login] Verifying session...");
        const { data: sessionData, error: sessionError } = await supabase.auth.getSession();
        console.log("[Login] Session verification result:", { sessionData, sessionError });
        
        if (!sessionData?.session) {
          console.error("[Login] SESSION NOT SET IN CLIENT!");
          alert("Login failed: Session not set properly. Check console.");
          return;
        }
        
        console.log("[Login] Session verified! Redirecting to dashboard...");
        
        // Redirect immediately
        console.log("[Login] Setting window.location.href = /dashboard");
        window.location.href = "/dashboard";
        console.log("[Login] Redirect command executed (this might not log if redirect works)");
      }
    } catch (error) {
      console.error("[Login] === CATCH BLOCK ===]);
      console.error("[Login] Error type:", typeof error);
      console.error("[Login] Error:", error);
      console.error("[Login] Error message:", error instanceof Error ? error.message : String(error));
      console.error("[Login] Error stack:", error instanceof Error ? error.stack : "No stack");
      const message = error instanceof Error ? error.message : "An error occurred";
      alert(`Error: ${message}`);
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

