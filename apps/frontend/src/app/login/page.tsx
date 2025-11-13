"use client";

import { useState } from "react";
import { supabase } from "@/lib/supabase";

// Force dynamic rendering (no static generation)
export const dynamic = 'force-dynamic';

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isSignUp, setIsSignUp] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    console.log("[Login] FORM SUBMITTED - Starting login process");
    console.log("[Login] Email:", email);
    console.log("[Login] Is sign up:", isSignUp);
    
    try {
      if (isSignUp) {
        console.log("[Login] === SIGN UP FLOW START ===");
        
        // Add timeout handling for signup
        const signupPromise = supabase.auth.signUp({
          email,
          password,
        });
        
        const timeoutPromise = new Promise((_, reject) => {
          setTimeout(() => reject(new Error("Request timed out. Supabase may be paused or experiencing issues.")), 30000);
        });
        
        let result;
        try {
          result = await Promise.race([signupPromise, timeoutPromise]) as typeof signupPromise extends Promise<infer T> ? T : never;
        } catch (timeoutError) {
          console.error("[Login] SIGN UP TIMEOUT:", timeoutError);
          alert("Sign up request timed out. This usually means:\n\n1. Your Supabase project may be paused (check dashboard)\n2. Email service may be misconfigured\n3. Network connectivity issues\n\nTry again in a moment, or check your Supabase project status.");
          return;
        }
        
        console.log("[Login] === SIGN UP RESPONSE RECEIVED ===");
        console.log("[Login] Full result:", JSON.stringify(result, null, 2));
        console.log("[Login] Error:", result.error);
        console.log("[Login] Data:", result.data);
        console.log("[Login] User:", result.data?.user);
        console.log("[Login] Session:", result.data?.session);
        
        if (result.error) {
          console.error("[Login] SIGN UP ERROR:", result.error);
          
          // Handle specific error types
          const errorMsg = result.error.message.toLowerCase();
          
          if (errorMsg.includes("timeout") || errorMsg.includes("504")) {
            alert("Sign up timed out. Your Supabase project may be paused or the email service may be misconfigured.\n\nCheck:\n1. Supabase Dashboard → Is your project running?\n2. Settings → Email Auth → Is SMTP configured?\n3. Try again in a few moments.");
          } else if (errorMsg.includes("503") || errorMsg.includes("service unavailable")) {
            alert("Service unavailable (503). This usually means:\n\n1. Your Supabase project is PAUSED → Go to dashboard and resume it\n2. SMTP settings are incorrect → Check Settings → Auth → SMTP\n3. SMTP password/credentials are wrong → Verify all SMTP fields\n\nAfter fixing, wait 30 seconds and try again.");
          } else if (errorMsg.includes("already registered") || errorMsg.includes("user already")) {
            alert("This email is already registered. Try signing in instead.");
            setIsSignUp(false);
          } else if (errorMsg.includes("email") && errorMsg.includes("invalid")) {
            alert("Invalid email address. Please check your email format.");
          } else if (errorMsg.includes("password")) {
            alert("Password issue. Make sure your password is at least 6 characters.");
          } else {
            alert(`Sign up failed: ${result.error.message}\n\nIf this persists, check:\n1. Supabase project status\n2. SMTP configuration\n3. Network connectivity`);
          }
          return;
        }
        
        // Check if email confirmation is required
        if (result.data?.user && !result.data?.session) {
          alert("Sign up successful! Please check your email to confirm your account.");
          // Reset form
          setEmail("");
          setPassword("");
          setIsSignUp(false);
          return;
        }
        
        // If session exists (email confirmation disabled), log them in
        if (result.data?.session) {
          console.log("[Login] Session created during signup, redirecting to dashboard");
          window.location.replace("/dashboard");
          return;
        }
        
        alert("Sign up successful! Please check your email to confirm your account.");
        setEmail("");
        setPassword("");
        setIsSignUp(false);
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
        
        // CRITICAL: Wait for cookies to be set and verify
        // Give the browser time to set cookies
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Check if cookies are actually set
        const allCookies = document.cookie;
        console.log("[Login] All cookies after login:", allCookies);
        
        // Verify Supabase session cookie exists
        const hasSupabaseCookie = allCookies.includes('sb-') || allCookies.includes('supabase');
        console.log("[Login] Has Supabase cookie:", hasSupabaseCookie);
        
        if (!hasSupabaseCookie) {
          console.error("[Login] WARNING: No Supabase cookie found! Session might not be persisted.");
          // Try to manually set the session
          // This is a workaround if createBrowserClient isn't setting cookies
        }
        
        console.log("[Login] Reloading page to /dashboard");
        window.location.replace("/dashboard");
      }
    } catch (error) {
      console.error("[Login] === CATCH BLOCK ===");
      console.error("[Login] Error type:", typeof error);
      console.error("[Login] Error:", error);
      console.error("[Login] Error message:", error instanceof Error ? error.message : String(error));
      console.error("[Login] Error stack:", error instanceof Error ? error.stack : "No stack");
      const message = error instanceof Error ? error.message : "An error occurred";
      alert(`Error: ${message}`);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-900">
      <div className="max-w-md w-full bg-gray-800 rounded-lg shadow-xl p-8 border border-gray-700">
        <h1 className="text-3xl font-bold mb-6 text-white">
          {isSignUp ? "Sign Up" : "Sign In"}
        </h1>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2 text-gray-300">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="you@example.com"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2 text-gray-300">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="••••••••"
              required
            />
          </div>
          <button
            type="submit"
            className="w-full bg-blue-600 text-white py-3 rounded-md hover:bg-blue-700 font-semibold transition-colors"
            onClick={() => {
              console.log("[Login] BUTTON CLICKED");
              // Don't prevent default - let form handle it
            }}
          >
            {isSignUp ? "Sign Up" : "Sign In"}
          </button>
        </form>
        <button
          onClick={() => setIsSignUp(!isSignUp)}
          className="mt-4 text-blue-400 text-sm hover:text-blue-300 transition-colors"
        >
          {isSignUp
            ? "Already have an account? Sign in"
            : "Don't have an account? Sign up"}
        </button>
      </div>
    </div>
  );
}

