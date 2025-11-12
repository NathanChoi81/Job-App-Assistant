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
  const fullUrl = `${API_URL}${endpoint}`;
  console.log(`[API] Making request to: ${fullUrl}`);
  console.log(`[API] API_URL from env: ${process.env.NEXT_PUBLIC_API_URL || 'NOT SET'}`);
  
  try {
    const headers = await getAuthHeaders();
    console.log(`[API] Headers obtained, making fetch request`);
    console.log(`[API] Authorization header present: ${!!headers.Authorization}`);
    
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
    } catch (error: unknown) {
      clearTimeout(timeoutId);
      if (error instanceof Error && error.name === 'AbortError') {
        console.error(`[API] Request aborted (timeout): ${endpoint}`);
        throw new Error('Request timed out. The API might be sleeping or unavailable.');
      }
      console.error(`[API] Fetch error:`, error);
      throw error;
    }
  } catch (error: unknown) {
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
  
  updateVariant: (jobId: string, skills: Array<{ name: string; source: string; locked: boolean; score?: number }>, coursework: Array<{ name: string; score?: number }>) =>
    apiRequest("/api/resume/variant", {
      method: "POST",
      body: JSON.stringify({ job_id: jobId, skills, coursework }),
    }),
  
  getVariant: (jobId: string) =>
    apiRequest(`/api/resume/variant/${jobId}`),
};

type JobCreate = {
  title: string;
  company: string;
  location?: string | null;
  jd_raw?: string;
  source_url?: string | null;
  deadline_at?: string | null;
  notes?: string | null;
};

type JobUpdate = Partial<JobCreate & {
  status?: string;
  application_status?: string;
  connection_status?: string;
}>;

type JDSpans = Record<string, unknown>;

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

type JobDetail = Job & {
  jd_raw: string;
  jd_spans_json: JDSpans;
  source_url: string | null;
  notes: string | null;
  updated_at: string;
};

// Jobs API
export const jobsApi = {
  create: (job: JobCreate) =>
    apiRequest("/api/jobs", {
      method: "POST",
      body: JSON.stringify(job),
    }),
  
  list: (status?: string) =>
    apiRequest<Job[]>(`/api/jobs${status ? `?status=${status}` : ""}`),
  
  get: (jobId: string) => apiRequest<JobDetail>(`/api/jobs/${jobId}`),
  
  update: (jobId: string, updates: JobUpdate) =>
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

type CoverLetter = {
  id: string;
  job_id: string;
  text: string;
  pdf_path: string | null;
  created_at: string;
  updated_at: string;
};

// Cover Letter API
export const coverLetterApi = {
  generate: (jobId: string) =>
    apiRequest<CoverLetter>("/api/cover-letter/generate", {
      method: "POST",
      body: JSON.stringify({ job_id: jobId }),
    }),
  
  get: (jobId: string) => apiRequest<CoverLetter>(`/api/cover-letter/${jobId}`),
  
  update: (jobId: string, text: string) =>
    apiRequest<CoverLetter>(`/api/cover-letter/${jobId}`, {
      method: "PATCH",
      body: JSON.stringify({ text }),
    }),
};

type ContactCreate = {
  job_id?: string;
  name: string;
  email?: string | null;
  linkedin_url?: string | null;
  title?: string | null;
  company?: string | null;
  notes?: string | null;
};

type ContactUpdate = Partial<ContactCreate>;

type Contact = {
  id: string;
  job_id: string | null;
  name: string;
  email: string | null;
  linkedin_url: string | null;
  title: string | null;
  company: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
};

type DMGenerateParams = {
  contact_id: string;
  job_id?: string;
  message_type?: string;
};

// Outreach API
export const outreachApi = {
  createContact: (contact: ContactCreate) =>
    apiRequest<Contact>("/api/outreach/contacts", {
      method: "POST",
      body: JSON.stringify(contact),
    }),
  
  listContacts: (jobId?: string) =>
    apiRequest<Contact[]>(`/api/outreach/contacts${jobId ? `?job_id=${jobId}` : ""}`),
  
  getContact: (contactId: string) =>
    apiRequest<Contact>(`/api/outreach/contacts/${contactId}`),
  
  updateContact: (contactId: string, updates: ContactUpdate) =>
    apiRequest<Contact>(`/api/outreach/contacts/${contactId}`, {
      method: "PATCH",
      body: JSON.stringify(updates),
    }),
  
  generateDM: (params: DMGenerateParams) =>
    apiRequest("/api/outreach/generate-dm", {
      method: "POST",
      body: JSON.stringify(params),
    }),
};

