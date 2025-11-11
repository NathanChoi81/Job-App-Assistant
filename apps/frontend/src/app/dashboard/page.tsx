"use client";

import { useQuery } from "@tanstack/react-query";
import { jobsApi } from "@/lib/api";
import Link from "next/link";

export default function DashboardPage() {
  const { data: jobs, isLoading, error } = useQuery<Array<{
    id: string;
    title: string;
    company: string;
    location: string | null;
    status: string;
    application_status: string;
    connection_status: string;
    deadline_at: string | null;
    created_at: string;
  }>>({
    queryKey: ["jobs"],
    queryFn: () => jobsApi.list(),
    retry: false,
  });

  if (isLoading) {
    return <div className="p-8">Loading...</div>;
  }

  if (error) {
    return (
      <div className="p-8">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          <p className="font-bold">Error loading jobs:</p>
          <p>{error instanceof Error ? error.message : "Unknown error"}</p>
          <p className="text-sm mt-2">Check if the API is running and NEXT_PUBLIC_API_URL is set correctly.</p>
        </div>
      </div>
    );
  }

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

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {jobs?.map((job) => (
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
      </div>
    </div>
  );
}

