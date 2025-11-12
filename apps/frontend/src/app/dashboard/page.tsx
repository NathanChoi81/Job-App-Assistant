"use client";

import { useQuery } from "@tanstack/react-query";
import { jobsApi } from "@/lib/api";
import Link from "next/link";

// Force dynamic rendering (no static generation)
export const dynamic = 'force-dynamic';

type Job = {
  id: string;
  title: string;
  company: string;
  location: string | null;
  status: string;
  application_status: string;
  connection_status: string;
  deadline_at: string | null;
  created_at: string;
};

export default function DashboardPage() {
  console.log("[Dashboard] Dashboard component rendered");
  
  const { data: jobs, isLoading, error } = useQuery<Job[]>({
    queryKey: ["jobs"],
    queryFn: () => {
      console.log("[Dashboard] Fetching jobs...");
      return jobsApi.list();
    },
    retry: false,
    enabled: true, // Explicitly enable the query
  });

  // Log state changes
  if (jobs) {
    console.log("[Dashboard] Jobs loaded:", jobs);
  }
  if (error) {
    console.error("[Dashboard] Error loading jobs:", error);
  }
  console.log("[Dashboard] State:", { isLoading, hasError: !!error, jobsCount: jobs?.length ?? 0 });

  if (isLoading) {
    console.log("[Dashboard] Showing loading state");
    return <div className="p-8">Loading...</div>;
  }

  if (error) {
    console.error("[Dashboard] Showing error state:", error);
    return (
      <div className="min-h-screen p-8">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-3xl font-bold mb-8">Dashboard</h1>
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            <p className="font-bold">Error loading jobs:</p>
            <p>{error instanceof Error ? error.message : "Unknown error"}</p>
            <p className="text-sm mt-2">Check if the API is running and NEXT_PUBLIC_API_URL is set correctly.</p>
            <p className="text-xs mt-2">Check browser console (F12) for more details.</p>
          </div>
        </div>
      </div>
    );
  }

  // Handle empty jobs array
  const jobsList = jobs || [];
  const hasJobs = jobsList.length > 0;

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Dashboard</h1>
        
        <div className="mb-6">
          <Link
            href="/dashboard/jobs/new"
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
          >
            Add New Job
          </Link>
          <Link
            href="/dashboard/resume"
            className="ml-4 bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
          >
            Manage Resume
          </Link>
        </div>

        {!hasJobs ? (
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-8 text-center">
            <h2 className="text-xl font-semibold mb-2">No jobs yet</h2>
            <p className="text-gray-600 mb-4">Get started by adding your first job application.</p>
            <Link
              href="/dashboard/jobs/new"
              className="inline-block bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700"
            >
              Add Your First Job
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {jobsList.map((job: Job) => (
              <Link
                key={job.id}
                href={`/dashboard/jobs/${job.id}`}
                className="border rounded-lg p-4 hover:shadow-lg transition-shadow"
              >
                <h2 className="text-xl font-semibold">{job.title}</h2>
                <p className="text-gray-600">{job.company}</p>
                <span className={`inline-block mt-2 px-2 py-1 rounded text-sm ${
                  job.status === "Applied" ? "bg-green-100" :
                  job.status === "Interview" ? "bg-blue-100" :
                  job.status === "Rejected" ? "bg-red-100" :
                  "bg-gray-100"
                }`}>
                  {job.status}
                </span>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

