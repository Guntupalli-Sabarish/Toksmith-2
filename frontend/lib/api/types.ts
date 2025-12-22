// User types
export interface User {
  id: string;
  email: string;
  full_name: string | null;
  avatar_url: string | null;
  created_at: string | null;
}

export interface AuthResponse {
  user: User;
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface UserSignUp {
  email: string;
  password: string;
  full_name?: string;
}

export interface UserSignIn {
  email: string;
  password: string;
}

// Profile types
export interface Profile {
  id: string;
  email: string;
  full_name: string | null;
  avatar_url: string | null;
  bio: string | null;
  subscription_tier: SubscriptionTier;
  credits_remaining: number;
  created_at: string | null;
  updated_at: string | null;
}

export interface ProfileUpdate {
  full_name?: string;
  avatar_url?: string;
  bio?: string;
}

export interface ProfileStats {
  total_projects: number;
  total_videos_generated: number;
  credits_used: number;
  credits_remaining: number;
  subscription_tier: SubscriptionTier;
}

export type SubscriptionTier = "free" | "pro" | "enterprise";

// Project types
export interface Project {
  id: string;
  user_id: string;
  title: string | null;
  description: string | null;
  source_url: string | null;
  source_type: SourceType | null;
  video_style: VideoStyle;
  status: ProjectStatus;
  scraped_data: Record<string, unknown> | null;
  script_data: Record<string, unknown> | null;
  video_url: string | null;
  audio_url: string | null;
  thumbnail_url: string | null;
  created_at: string | null;
  updated_at: string | null;
}

export interface ProjectCreate {
  title?: string;
  description?: string;
  source_url: string;
  source_type?: SourceType;
  video_style?: VideoStyle;
}

export interface ProjectUpdate {
  title?: string;
  description?: string;
  video_style?: VideoStyle;
}

export interface ProjectListResponse {
  projects: Project[];
  total: number;
  page: number;
  per_page: number;
}

export type SourceType = "reddit" | "twitter" | "stackoverflow" | "custom";
export type VideoStyle = "tiktok" | "youtube_short" | "instagram_reel" | "youtube";
export type ProjectStatus =
  | "draft"
  | "pending"
  | "scraped"
  | "script_generated"
  | "audio_generated"
  | "video_generated"
  | "completed"
  | "failed";

// Storage types
export interface FileUpload {
  file_id: string;
  file_name: string;
  file_path: string;
  public_url: string;
  file_type: FileType;
  file_size: number;
  mime_type: string;
  created_at: string;
}

export interface FileListResponse {
  files: FileUpload[];
  total: number;
}

export interface SignedUrlResponse {
  signed_url: string;
  expires_at: string;
}

export type FileType = "video" | "audio" | "image" | "avatar" | "thumbnail" | "asset";

// Generic responses
export interface MessageResponse {
  message: string;
  success: boolean;
}
