"use client";

import Link from "next/link";

// Force dynamic rendering
export const dynamic = 'force-dynamic';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-bold text-gray-900">Job App Assistant</h1>
            <Link
              href="/login"
              className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
            >
              Sign In
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center mb-16">
          <h2 className="text-5xl font-bold text-gray-900 mb-6">
            Land Your Dream Job Faster
          </h2>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            AI-powered resume tailoring and cover letter generation. 
            Match your skills to job descriptions and create personalized applications in minutes.
          </p>
          <Link
            href="/login"
            className="inline-block bg-blue-600 text-white px-8 py-4 rounded-lg text-lg font-semibold hover:bg-blue-700 transition-colors shadow-lg"
          >
            Get Started Free
          </Link>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-3 gap-8 mt-16">
          <div className="bg-white rounded-lg p-8 shadow-md">
            <div className="text-4xl mb-4">📝</div>
            <h3 className="text-xl font-semibold mb-3">Smart Resume Tailoring</h3>
            <p className="text-gray-600">
              Automatically analyze job descriptions and tailor your resume to highlight the most relevant skills and experiences.
            </p>
          </div>

          <div className="bg-white rounded-lg p-8 shadow-md">
            <div className="text-4xl mb-4">✉️</div>
            <h3 className="text-xl font-semibold mb-3">AI Cover Letters</h3>
            <p className="text-gray-600">
              Generate personalized cover letters that match your resume and the job requirements in seconds.
            </p>
          </div>

          <div className="bg-white rounded-lg p-8 shadow-md">
            <div className="text-4xl mb-4">📊</div>
            <h3 className="text-xl font-semibold mb-3">Track Applications</h3>
            <p className="text-gray-600">
              Keep track of all your job applications, deadlines, and status updates in one organized dashboard.
            </p>
          </div>
        </div>

        {/* CTA Section */}
        <div className="mt-16 text-center bg-white rounded-lg p-12 shadow-md">
          <h3 className="text-3xl font-bold text-gray-900 mb-4">
            Ready to streamline your job search?
          </h3>
          <p className="text-gray-600 mb-8">
            Join thousands of job seekers who are landing interviews faster with AI-powered applications.
          </p>
          <Link
            href="/login"
            className="inline-block bg-blue-600 text-white px-8 py-4 rounded-lg text-lg font-semibold hover:bg-blue-700 transition-colors"
          >
            Start Your Free Account
          </Link>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <p className="text-center text-gray-600">
            © 2025 Job App Assistant. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
}
