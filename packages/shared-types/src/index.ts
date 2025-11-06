import { z } from "zod";

// Job Status Types
export const JobStatusSchema = z.enum([
  "Not Applied",
  "Applied",
  "Interview",
  "Offer",
  "Rejected",
]);
export type JobStatus = z.infer<typeof JobStatusSchema>;

export const ApplicationStatusSchema = z.enum(["Not Sent", "Sent", "Waiting"]);
export type ApplicationStatus = z.infer<typeof ApplicationStatusSchema>;

export const ConnectionStatusSchema = z.enum([
  "No Connection",
  "Reached Out",
  "Connected",
]);
export type ConnectionStatus = z.infer<typeof ConnectionStatusSchema>;

// Outreach Contact Status
export const ContactStatusSchema = z.enum([
  "Not Contacted",
  "Reached Out",
  "Connected",
  "Not Interested",
]);
export type ContactStatus = z.infer<typeof ContactStatusSchema>;

// Action Types
export const ActionTypeSchema = z.enum([
  "jd_processed",
  "resume_compiled",
  "cover_letter_generated",
  "job_added",
  "outreach_dm_generated",
  "resume_viewed",
  "applied",
  "connected",
  "messaged",
]);
export type ActionType = z.infer<typeof ActionTypeSchema>;

// Skill Source Types
export const SkillSourceSchema = z.enum([
  "requirement",
  "responsibility",
  "nice_to_have",
  "static",
]);
export type SkillSource = z.infer<typeof SkillSourceSchema>;

// Parsed Resume Structure
export const SkillSchema = z.object({
  name: z.string(),
  source: SkillSourceSchema,
  locked: z.boolean(),
  score: z.number().optional(),
});
export type Skill = z.infer<typeof SkillSchema>;

export const CourseworkItemSchema = z.object({
  name: z.string(),
  score: z.number().optional(),
});
export type CourseworkItem = z.infer<typeof CourseworkItemSchema>;

export const ParsedResumeSchema = z.object({
  sections: z.record(z.string(), z.string()),
  technicalSkills: z.array(SkillSchema),
  relevantCoursework: z.array(CourseworkItemSchema),
});
export type ParsedResume = z.infer<typeof ParsedResumeSchema>;

// JD Spans
export const JDSpanSchema = z.object({
  requirements: z.array(z.tuple([z.number(), z.number()])),
  responsibilities: z.array(z.tuple([z.number(), z.number()])),
  nice_to_haves: z.array(z.tuple([z.number(), z.number()])),
});
export type JDSpan = z.infer<typeof JDSpanSchema>;

// Job Schema
export const JobSchema = z.object({
  id: z.string().uuid(),
  user_id: z.string().uuid(),
  title: z.string(),
  company: z.string(),
  location: z.string().nullable(),
  jd_raw: z.string(),
  jd_spans_json: JDSpanSchema.nullable(),
  status: JobStatusSchema,
  application_status: ApplicationStatusSchema,
  connection_status: ConnectionStatusSchema,
  source_url: z.string().nullable(),
  deadline_at: z.string().datetime().nullable(),
  notes: z.string().nullable(),
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
});
export type Job = z.infer<typeof JobSchema>;

// Resume Master Schema
export const ResumeMasterSchema = z.object({
  id: z.string().uuid(),
  user_id: z.string().uuid(),
  latex_blob: z.string(),
  parsed_json: ParsedResumeSchema,
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
});
export type ResumeMaster = z.infer<typeof ResumeMasterSchema>;

// Resume Variant Schema
export const ResumeVariantSchema = z.object({
  id: z.string().uuid(),
  user_id: z.string().uuid(),
  job_id: z.string().uuid(),
  latex_blob: z.string(),
  pdf_path: z.string().nullable(),
  diff_json: z.record(z.unknown()).nullable(),
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
});
export type ResumeVariant = z.infer<typeof ResumeVariantSchema>;

// Cover Letter Schema
export const CoverLetterSchema = z.object({
  id: z.string().uuid(),
  job_id: z.string().uuid(),
  text: z.string(),
  pdf_path: z.string().nullable(),
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
});
export type CoverLetter = z.infer<typeof CoverLetterSchema>;

// Outreach Contact Schema
export const OutreachContactSchema = z.object({
  id: z.string().uuid(),
  job_id: z.string().uuid().nullable(),
  user_id: z.string().uuid(),
  name: z.string(),
  linkedin_url: z.string().nullable(),
  role: z.string().nullable(),
  status: ContactStatusSchema,
  last_contacted_at: z.string().datetime().nullable(),
  notes: z.string().nullable(),
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
});
export type OutreachContact = z.infer<typeof OutreachContactSchema>;

// API Request/Response Types
export const UploadResumeRequestSchema = z.object({
  latex: z.string().min(1),
});
export type UploadResumeRequest = z.infer<typeof UploadResumeRequestSchema>;

export const AnalyzeJDRequestSchema = z.object({
  jd_text: z.string().min(1),
  job_id: z.string().uuid().optional(),
});
export type AnalyzeJDRequest = z.infer<typeof AnalyzeJDRequestSchema>;

export const AnalyzeJDResponseSchema = z.object({
  spans: JDSpanSchema,
  skills: z.array(SkillSchema),
  coursework: z.array(CourseworkItemSchema),
});
export type AnalyzeJDResponse = z.infer<typeof AnalyzeJDResponseSchema>;

export const UpdateResumeVariantRequestSchema = z.object({
  job_id: z.string().uuid(),
  skills: z.array(SkillSchema),
  coursework: z.array(CourseworkItemSchema),
});
export type UpdateResumeVariantRequest = z.infer<
  typeof UpdateResumeVariantRequestSchema
>;

export const GenerateCoverLetterRequestSchema = z.object({
  job_id: z.string().uuid(),
});
export type GenerateCoverLetterRequest = z.infer<
  typeof GenerateCoverLetterRequestSchema
>;

export const GenerateDMRequestSchema = z.object({
  contact_id: z.string().uuid().optional(),
  job_id: z.string().uuid().optional(),
  role: z.string().optional(),
  name: z.string().optional(),
});
export type GenerateDMRequest = z.infer<typeof GenerateDMRequestSchema>;

