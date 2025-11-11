import { supabase } from "./supabase";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function getAuthHeaders() {
  const {
    data: { session },
  } = await supabase.auth.getSession();
  
  if (!session?.access_token) {
    throw new Error("Not authenticated");
  }
  
  return {
    Authorization: `Bearer ${session.access_token}`,
    "Content-Type": "application/json",
  };
}

export async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  console.log(`[API] Making request to: ${API_URL}${endpoint}`);
  
  try {
    const headers = await getAuthHeaders();
    console.log(`[API] Headers obtained, making fetch request`);
    
    // Add timeout to prevent hanging
    const controller = new AbortController();
    const timeoutId = setTimeout(() => {
      console.error(`[API] Request timeout after 10s: ${endpoint}`);
      controller.abort();
    }, 10000); // 10 second timeout
    
    try {
      const response = await fetch(`${API_URL}${endpoint}`, {
        ...options,
        signal: controller.signal,
        headers: {
          ...headers,
          ...options.headers,
        },
      });
      
      clearTimeout(timeoutId);
      console.log(`[API] Response received: ${response.status} ${response.statusText}`);
      
      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: "Unknown error" }));
        console.error(`[API] Error response:`, error);
        throw new Error(error.detail || `HTTP ${response.status}`);
      }
      
      const data = await response.json();
      console.log(`[API] Success:`, data);
      return data;
    } catch (error: any) {
      clearTimeout(timeoutId);
      if (error.name === 'AbortError') {
        console.error(`[API] Request aborted (timeout): ${endpoint}`);
        throw new Error('Request timed out. The API might be sleeping or unavailable.');
      }
      console.error(`[API] Fetch error:`, error);
      throw error;
    }
  } catch (error: any) {
    console.error(`[API] Error in apiRequest:`, error);
    throw error;
  }
}

// Resume API
export const resumeApi = {
  uploadMaster: (latex: string) =>
    apiRequest("/api/resume/master", {
      method: "POST",
      body: JSON.stringify({ latex }),
    }),
  
  getMaster: () => apiRequest<{
    id: string;
    latex: string;
    parsed: {
      sections: Record<string, string>;
      technicalSkills: Array<{
        name: string;
        source: string;
        locked: boolean;
        score?: number;
      }>;
      relevantCoursework: Array<{
        name: string;
        score?: number;
      }>;
    };
  }>("/api/resume/master"),
  
  updateVariant: (jobId: string, skills: any[], coursework: any[]) =>
    apiRequest("/api/resume/variant", {
      method: "POST",
      body: JSON.stringify({ job_id: jobId, skills, coursework }),
    }),
  
  getVariant: (jobId: string) =>
    apiRequest(`/api/resume/variant/${jobId}`),
};

// Jobs API
export const jobsApi = {
  create: (job: any) =>
    apiRequest("/api/jobs", {
      method: "POST",
      body: JSON.stringify(job),
    }),
  
  list: (status?: string) =>
    apiRequest<Array<{
      id: string;
      title: string;
      company: string;
      location: string | null;
      status: string;
      application_status: string;
      connection_status: string;
      deadline_at: string | null;
      created_at: string;
    }>>(`/api/jobs${status ? `?status=${status}` : ""}`),
  
  get: (jobId: string) => apiRequest<{
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
  }>(`/api/jobs/${jobId}`),
  
  update: (jobId: string, updates: any) =>
    apiRequest(`/api/jobs/${jobId}`, {
      method: "PATCH",
      body: JSON.stringify(updates),
    }),
  
  delete: (jobId: string) =>
    apiRequest(`/api/jobs/${jobId}`, {
      method: "DELETE",
    }),
  
  analyzeJD: (jdText: string, jobId?: string) =>
    apiRequest("/api/jobs/analyze-jd", {
      method: "POST",
      body: JSON.stringify({ jd_text: jdText, job_id: jobId }),
    }),
};

// Cover Letter API
export const coverLetterApi = {
  generate: (jobId: string) =>
    apiRequest("/api/cover-letter/generate", {
      method: "POST",
      body: JSON.stringify({ job_id: jobId }),
    }),
  
  get: (jobId: string) => apiRequest(`/api/cover-letter/${jobId}`),
  
  update: (jobId: string, text: string) =>
    apiRequest(`/api/cover-letter/${jobId}`, {
      method: "PATCH",
      body: JSON.stringify({ text }),
    }),
};

// Outreach API
export const outreachApi = {
  createContact: (contact: any) =>
    apiRequest("/api/outreach/contacts", {
      method: "POST",
      body: JSON.stringify(contact),
    }),
  
  listContacts: (jobId?: string) =>
    apiRequest(`/api/outreach/contacts${jobId ? `?job_id=${jobId}` : ""}`),
  
  getContact: (contactId: string) =>
    apiRequest(`/api/outreach/contacts/${contactId}`),
  
  updateContact: (contactId: string, updates: any) =>
    apiRequest(`/api/outreach/contacts/${contactId}`, {
      method: "PATCH",
      body: JSON.stringify(updates),
    }),
  
  generateDM: (params: any) =>
    apiRequest("/api/outreach/generate-dm", {
      method: "POST",
      body: JSON.stringify(params),
    }),
};

