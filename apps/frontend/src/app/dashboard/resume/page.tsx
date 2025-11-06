"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { resumeApi } from "@/lib/api";
import { useState } from "react";

export default function ResumePage() {
  const queryClient = useQueryClient();
  const [latex, setLatex] = useState("");

  const { data: master, isLoading } = useQuery({
    queryKey: ["resume-master"],
    queryFn: () => resumeApi.getMaster(),
  });

  const uploadMutation = useMutation({
    mutationFn: (latex: string) => resumeApi.uploadMaster(latex),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["resume-master"] });
    },
  });

  if (isLoading) {
    return <div className="p-8">Loading...</div>;
  }

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Master Resume</h1>

        {!master ? (
          <div className="space-y-4">
            <h2 className="text-xl font-semibold">Upload Master Resume (LaTeX)</h2>
            <textarea
              value={latex}
              onChange={(e) => setLatex(e.target.value)}
              className="w-full h-96 p-4 border rounded-md font-mono text-sm"
              placeholder="Paste your LaTeX resume here..."
            />
            <button
              onClick={() => uploadMutation.mutate(latex)}
              className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
              disabled={uploadMutation.isPending}
            >
              {uploadMutation.isPending ? "Uploading..." : "Upload Resume"}
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="bg-green-50 border border-green-200 rounded p-4">
              <p className="text-green-800">Master resume uploaded successfully!</p>
              <p className="text-sm text-green-600 mt-2">
                Skills: {master.parsed?.technicalSkills?.length || 0} | 
                Coursework: {master.parsed?.relevantCoursework?.length || 0}
              </p>
            </div>
            <details>
              <summary className="cursor-pointer font-semibold">View Parsed Resume</summary>
              <pre className="mt-4 p-4 bg-gray-100 rounded overflow-auto">
                {JSON.stringify(master.parsed, null, 2)}
              </pre>
            </details>
          </div>
        )}
      </div>
    </div>
  );
}

