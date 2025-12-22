-- Supabase Database Schema for TokSmith
-- Run this in Supabase SQL Editor to set up the database

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- PROFILES TABLE (extends Supabase Auth users)
-- ============================================
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    full_name TEXT,
    avatar_url TEXT,
    bio TEXT,
    subscription_tier TEXT DEFAULT 'free' CHECK (subscription_tier IN ('free', 'pro', 'enterprise')),
    credits_remaining INTEGER DEFAULT 10,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

-- Profile policies
CREATE POLICY "Users can view own profile" ON public.profiles
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON public.profiles
    FOR UPDATE USING (auth.uid() = id);

-- Service role can do everything
CREATE POLICY "Service role has full access to profiles" ON public.profiles
    FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

-- ============================================
-- PROJECTS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS public.projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    title TEXT,
    description TEXT,
    source_url TEXT,
    source_type TEXT CHECK (source_type IN ('reddit', 'twitter', 'stackoverflow', 'custom')),
    video_style TEXT DEFAULT 'tiktok' CHECK (video_style IN ('tiktok', 'youtube_short', 'instagram_reel', 'youtube')),
    status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'pending', 'scraped', 'script_generated', 'audio_generated', 'video_generated', 'completed', 'failed')),
    scraped_data JSONB,
    script_data JSONB,
    video_url TEXT,
    audio_url TEXT,
    thumbnail_url TEXT,
    error_message TEXT,
    credits_used INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for faster user queries
CREATE INDEX IF NOT EXISTS idx_projects_user_id ON public.projects(user_id);
CREATE INDEX IF NOT EXISTS idx_projects_status ON public.projects(status);
CREATE INDEX IF NOT EXISTS idx_projects_created_at ON public.projects(created_at DESC);

-- Enable RLS
ALTER TABLE public.projects ENABLE ROW LEVEL SECURITY;

-- Project policies
CREATE POLICY "Users can view own projects" ON public.projects
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can create own projects" ON public.projects
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own projects" ON public.projects
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own projects" ON public.projects
    FOR DELETE USING (auth.uid() = user_id);

-- Service role can do everything
CREATE POLICY "Service role has full access to projects" ON public.projects
    FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

-- ============================================
-- VIDEO JOBS TABLE (for async processing)
-- ============================================
CREATE TABLE IF NOT EXISTS public.video_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    job_type TEXT NOT NULL CHECK (job_type IN ('scrape', 'generate_script', 'generate_audio', 'generate_video', 'full_pipeline')),
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'cancelled')),
    progress INTEGER DEFAULT 0 CHECK (progress >= 0 AND progress <= 100),
    result_data JSONB,
    error_message TEXT,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_video_jobs_project_id ON public.video_jobs(project_id);
CREATE INDEX IF NOT EXISTS idx_video_jobs_user_id ON public.video_jobs(user_id);
CREATE INDEX IF NOT EXISTS idx_video_jobs_status ON public.video_jobs(status);

-- Enable RLS
ALTER TABLE public.video_jobs ENABLE ROW LEVEL SECURITY;

-- Video jobs policies
CREATE POLICY "Users can view own jobs" ON public.video_jobs
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can create own jobs" ON public.video_jobs
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can cancel own jobs" ON public.video_jobs
    FOR UPDATE USING (auth.uid() = user_id);

-- Service role can do everything
CREATE POLICY "Service role has full access to video_jobs" ON public.video_jobs
    FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

-- ============================================
-- GENERATED FILES TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS public.generated_files (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    project_id UUID REFERENCES public.projects(id) ON DELETE SET NULL,
    file_name TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_type TEXT NOT NULL CHECK (file_type IN ('video', 'audio', 'image', 'avatar', 'thumbnail', 'asset')),
    file_size BIGINT,
    mime_type TEXT,
    bucket_name TEXT NOT NULL,
    public_url TEXT,
    is_public BOOLEAN DEFAULT FALSE,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_generated_files_user_id ON public.generated_files(user_id);
CREATE INDEX IF NOT EXISTS idx_generated_files_project_id ON public.generated_files(project_id);
CREATE INDEX IF NOT EXISTS idx_generated_files_type ON public.generated_files(file_type);

-- Enable RLS
ALTER TABLE public.generated_files ENABLE ROW LEVEL SECURITY;

-- Generated files policies
CREATE POLICY "Users can view own files" ON public.generated_files
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can create own files" ON public.generated_files
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own files" ON public.generated_files
    FOR DELETE USING (auth.uid() = user_id);

-- Service role can do everything
CREATE POLICY "Service role has full access to generated_files" ON public.generated_files
    FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

-- ============================================
-- CREDIT TRANSACTIONS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS public.credit_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    project_id UUID REFERENCES public.projects(id) ON DELETE SET NULL,
    amount INTEGER NOT NULL,
    transaction_type TEXT NOT NULL CHECK (transaction_type IN ('purchase', 'usage', 'refund', 'bonus')),
    description TEXT,
    balance_after INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_credit_transactions_user_id ON public.credit_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_credit_transactions_created_at ON public.credit_transactions(created_at DESC);

-- Enable RLS
ALTER TABLE public.credit_transactions ENABLE ROW LEVEL SECURITY;

-- Credit transaction policies
CREATE POLICY "Users can view own transactions" ON public.credit_transactions
    FOR SELECT USING (auth.uid() = user_id);

-- Service role can do everything
CREATE POLICY "Service role has full access to credit_transactions" ON public.credit_transactions
    FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

-- ============================================
-- TRIGGERS FOR UPDATED_AT
-- ============================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_profiles_updated_at
    BEFORE UPDATE ON public.profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_projects_updated_at
    BEFORE UPDATE ON public.projects
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- FUNCTION: Auto-create profile on user signup
-- ============================================
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, email, full_name, avatar_url)
    VALUES (
        NEW.id,
        NEW.email,
        NEW.raw_user_meta_data ->> 'full_name',
        NEW.raw_user_meta_data ->> 'avatar_url'
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to auto-create profile
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_new_user();

-- ============================================
-- STORAGE BUCKETS SETUP
-- Run these in the Supabase dashboard or via API
-- ============================================
-- Note: Storage buckets should be created via Supabase Dashboard:
-- 1. videos - for generated videos
-- 2. audio - for generated audio files
-- 3. avatars - for user profile pictures
-- 4. assets - for misc assets

-- Storage policies need to be set in Supabase Dashboard:
-- Videos bucket:
--   - SELECT: Authenticated users can view their own files (bucket_id = 'videos' AND auth.uid()::text = (storage.foldername(name))[1])
--   - INSERT: Authenticated users can upload to their own folder
--   - DELETE: Authenticated users can delete their own files

COMMENT ON TABLE public.profiles IS 'User profiles extending Supabase Auth';
COMMENT ON TABLE public.projects IS 'Video generation projects';
COMMENT ON TABLE public.video_jobs IS 'Async video processing jobs';
COMMENT ON TABLE public.generated_files IS 'Record of all generated files';
COMMENT ON TABLE public.credit_transactions IS 'Credit usage and purchase history';
