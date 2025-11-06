"use client";

import { useParams } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { jobsApi, resumeApi, coverLetterApi } from "@/lib/api";
import { useState } from "react";
import Link from "next/link";

export default function JobDetailPage() {
  const params = useParams();
  const jobId = params.id as string;
  const queryClient = useQueryClient();
  const [jdText, setJdText] = useState("");

  const { data: job, isLoading } = useQuery<{
    id: string;
    title: string;
    company: string;
    location: string | null;
    jd_raw: string;
    jd_spans_json: any;
    status: string;
    application_status: string;
    connection_status: string;
    source_url: string | null;
    deadline_at: string | null;
    notes: string | null;
    created_at: string;
    updated_at: string;
  }>({
    queryKey: ["job", jobId],
    queryFn: () => jobsApi.get(jobId),
  });

  const analyzeMutation = useMutation({
    mutationFn: (text: string) => jobsApi.analyzeJD(text, jobId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["job", jobId] });
    },
  });

  if (isLoading) {
    return <div className="p-8">Loading...</div>;
  }

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-4">{job?.title}</h1>
        <p className="text-xl text-gray-600 mb-8">{job?.company}</p>

        <div className="space-y-6">
          <section>
            <h2 className="text-2xl font-semibold mb-4">Job Description</h2>
            <textarea
              value={jdText || job?.jd_raw || ""}
              onChange={(e) => setJdText(e.target.value)}
              className="w-full h-64 p-4 border rounded-md"
              placeholder="Paste job description here..."
            />
            <button
              onClick={() => analyzeMutation.mutate(jdText || job?.jd_raw)}
              className="mt-4 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
              disabled={analyzeMutation.isPending}
            >
              {analyzeMutation.isPending ? "Analyzing..." : "Analyze JD"}
            </button>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">Resume</h2>
            <Link
              href={`/dashboard/jobs/${jobId}/resume`}
              className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
            >
              Tailor Resume
            </Link>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">Cover Letter</h2>
            <Link
              href={`/dashboard/jobs/${jobId}/cover-letter`}
              className="bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700"
            >
              Generate Cover Letter
            </Link>
          </section>
        </div>
      </div>
    </div>
  );
}

