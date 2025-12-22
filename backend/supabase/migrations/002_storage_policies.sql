-- Supabase Storage Bucket Policies
-- Run this in Supabase SQL Editor after creating the buckets via Dashboard

-- ============================================
-- VIDEOS BUCKET POLICIES
-- ============================================

-- Allow authenticated users to upload to their own folder
CREATE POLICY "Users can upload videos to own folder"
ON storage.objects FOR INSERT
WITH CHECK (
    bucket_id = 'videos' 
    AND auth.role() = 'authenticated'
    AND (storage.foldername(name))[1] = auth.uid()::text
);

-- Allow users to view their own videos
CREATE POLICY "Users can view own videos"
ON storage.objects FOR SELECT
USING (
    bucket_id = 'videos'
    AND auth.role() = 'authenticated'
    AND (storage.foldername(name))[1] = auth.uid()::text
);

-- Allow users to delete their own videos
CREATE POLICY "Users can delete own videos"
ON storage.objects FOR DELETE
USING (
    bucket_id = 'videos'
    AND auth.role() = 'authenticated'
    AND (storage.foldername(name))[1] = auth.uid()::text
);

-- ============================================
-- AUDIO BUCKET POLICIES
-- ============================================

CREATE POLICY "Users can upload audio to own folder"
ON storage.objects FOR INSERT
WITH CHECK (
    bucket_id = 'audio' 
    AND auth.role() = 'authenticated'
    AND (storage.foldername(name))[1] = auth.uid()::text
);

CREATE POLICY "Users can view own audio"
ON storage.objects FOR SELECT
USING (
    bucket_id = 'audio'
    AND auth.role() = 'authenticated'
    AND (storage.foldername(name))[1] = auth.uid()::text
);

CREATE POLICY "Users can delete own audio"
ON storage.objects FOR DELETE
USING (
    bucket_id = 'audio'
    AND auth.role() = 'authenticated'
    AND (storage.foldername(name))[1] = auth.uid()::text
);

-- ============================================
-- AVATARS BUCKET POLICIES (PUBLIC READ)
-- ============================================

CREATE POLICY "Users can upload avatars to own folder"
ON storage.objects FOR INSERT
WITH CHECK (
    bucket_id = 'avatars' 
    AND auth.role() = 'authenticated'
    AND (storage.foldername(name))[1] = auth.uid()::text
);

-- Avatars are publicly readable
CREATE POLICY "Anyone can view avatars"
ON storage.objects FOR SELECT
USING (bucket_id = 'avatars');

CREATE POLICY "Users can delete own avatars"
ON storage.objects FOR DELETE
USING (
    bucket_id = 'avatars'
    AND auth.role() = 'authenticated'
    AND (storage.foldername(name))[1] = auth.uid()::text
);

CREATE POLICY "Users can update own avatars"
ON storage.objects FOR UPDATE
USING (
    bucket_id = 'avatars'
    AND auth.role() = 'authenticated'
    AND (storage.foldername(name))[1] = auth.uid()::text
);

-- ============================================
-- ASSETS BUCKET POLICIES
-- ============================================

CREATE POLICY "Users can upload assets to own folder"
ON storage.objects FOR INSERT
WITH CHECK (
    bucket_id = 'assets' 
    AND auth.role() = 'authenticated'
    AND (storage.foldername(name))[1] = auth.uid()::text
);

CREATE POLICY "Users can view own assets"
ON storage.objects FOR SELECT
USING (
    bucket_id = 'assets'
    AND auth.role() = 'authenticated'
    AND (storage.foldername(name))[1] = auth.uid()::text
);

CREATE POLICY "Users can delete own assets"
ON storage.objects FOR DELETE
USING (
    bucket_id = 'assets'
    AND auth.role() = 'authenticated'
    AND (storage.foldername(name))[1] = auth.uid()::text
);
