-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table (extends Supabase auth.users)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT UNIQUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Master Resume table
CREATE TABLE IF NOT EXISTS resume_master (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    latex_blob TEXT NOT NULL,
    parsed_json JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id)
);

-- Jobs table
CREATE TABLE IF NOT EXISTS jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    company TEXT NOT NULL,
    location TEXT,
    jd_raw TEXT NOT NULL,
    jd_spans_json JSONB,
    status TEXT NOT NULL DEFAULT 'Not Applied' CHECK (status IN ('Not Applied', 'Applied', 'Interview', 'Offer', 'Rejected')),
    application_status TEXT NOT NULL DEFAULT 'Not Sent' CHECK (application_status IN ('Not Sent', 'Sent', 'Waiting')),
    connection_status TEXT NOT NULL DEFAULT 'No Connection' CHECK (connection_status IN ('No Connection', 'Reached Out', 'Connected')),
    source_url TEXT,
    deadline_at TIMESTAMPTZ,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Resume Variant table (tailored resumes per job)
CREATE TABLE IF NOT EXISTS resume_variant (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    job_id UUID NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    latex_blob TEXT NOT NULL,
    pdf_path TEXT,
    diff_json JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, job_id)
);

-- Cover Letters table
CREATE TABLE IF NOT EXISTS cover_letters (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id UUID NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    text TEXT NOT NULL,
    pdf_path TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(job_id)
);

-- Outreach Contacts table
CREATE TABLE IF NOT EXISTS outreach_contacts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id UUID REFERENCES jobs(id) ON DELETE SET NULL,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    linkedin_url TEXT,
    role TEXT,
    status TEXT NOT NULL DEFAULT 'Not Contacted' CHECK (status IN ('Not Contacted', 'Reached Out', 'Connected', 'Not Interested')),
    last_contacted_at TIMESTAMPTZ,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Actions/Events table (for analytics)
CREATE TABLE IF NOT EXISTS actions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    job_id UUID REFERENCES jobs(id) ON DELETE SET NULL,
    type TEXT NOT NULL CHECK (type IN ('jd_processed', 'resume_compiled', 'cover_letter_generated', 'job_added', 'outreach_dm_generated', 'resume_viewed', 'applied', 'connected', 'messaged')),
    meta JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_resume_master_user_id ON resume_master(user_id);
CREATE INDEX IF NOT EXISTS idx_jobs_user_id ON jobs(user_id);
CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
CREATE INDEX IF NOT EXISTS idx_resume_variant_user_job ON resume_variant(user_id, job_id);
CREATE INDEX IF NOT EXISTS idx_cover_letters_job_id ON cover_letters(job_id);
CREATE INDEX IF NOT EXISTS idx_outreach_contacts_user_id ON outreach_contacts(user_id);
CREATE INDEX IF NOT EXISTS idx_outreach_contacts_job_id ON outreach_contacts(job_id);
CREATE INDEX IF NOT EXISTS idx_actions_user_id ON actions(user_id);
CREATE INDEX IF NOT EXISTS idx_actions_type ON actions(type);
CREATE INDEX IF NOT EXISTS idx_actions_created_at ON actions(created_at);

-- RLS Policies (Row Level Security)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE resume_master ENABLE ROW LEVEL SECURITY;
ALTER TABLE jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE resume_variant ENABLE ROW LEVEL SECURITY;
ALTER TABLE cover_letters ENABLE ROW LEVEL SECURITY;
ALTER TABLE outreach_contacts ENABLE ROW LEVEL SECURITY;
ALTER TABLE actions ENABLE ROW LEVEL SECURITY;

-- Users can only see their own data
CREATE POLICY "Users can view own data" ON users FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can update own data" ON users FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can manage own resume_master" ON resume_master FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Users can manage own jobs" ON jobs FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Users can manage own resume_variant" ON resume_variant FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Users can manage own cover_letters" ON cover_letters FOR ALL USING (
    EXISTS (SELECT 1 FROM jobs WHERE jobs.id = cover_letters.job_id AND jobs.user_id = auth.uid())
);
CREATE POLICY "Users can manage own outreach_contacts" ON outreach_contacts FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Users can manage own actions" ON actions FOR ALL USING (auth.uid() = user_id);

-- Functions for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_resume_master_updated_at BEFORE UPDATE ON resume_master FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_jobs_updated_at BEFORE UPDATE ON jobs FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_resume_variant_updated_at BEFORE UPDATE ON resume_variant FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_cover_letters_updated_at BEFORE UPDATE ON cover_letters FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_outreach_contacts_updated_at BEFORE UPDATE ON outreach_contacts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

