"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  ArrowLeft,
  Edit,
  Trash2,
  ExternalLink,
  CheckCircle,
  Clock,
  AlertCircle,
  FileText,
  Mic,
  Video,
} from "lucide-react";

interface ProjectHeaderProps {
  id: string;
  title: string | null;
  status: string;
  sourceType: string | null;
  sourceUrl: string | null;
  onDelete: () => void;
}

const statusConfig: Record<
  string,
  { label: string; color: string; icon: React.ElementType }
> = {
  draft: {
    label: "Draft",
    color: "bg-muted text-muted-foreground",
    icon: Edit,
  },
  pending: {
    label: "Processing",
    color: "bg-yellow-500/10 text-yellow-600 border-yellow-500/20",
    icon: Clock,
  },
  scraped: {
    label: "Content Scraped",
    color: "bg-blue-500/10 text-blue-600 border-blue-500/20",
    icon: FileText,
  },
  script_generated: {
    label: "Script Generated",
    color: "bg-purple-500/10 text-purple-600 border-purple-500/20",
    icon: FileText,
  },
  audio_generated: {
    label: "Audio Generated",
    color: "bg-indigo-500/10 text-indigo-600 border-indigo-500/20",
    icon: Mic,
  },
  video_generated: {
    label: "Video Generated",
    color: "bg-teal-500/10 text-teal-600 border-teal-500/20",
    icon: Video,
  },
  completed: {
    label: "Completed",
    color: "bg-green-500/10 text-green-600 border-green-500/20",
    icon: CheckCircle,
  },
  failed: {
    label: "Failed",
    color: "bg-red-500/10 text-red-600 border-red-500/20",
    icon: AlertCircle,
  },
};

const sourceTypeLabels: Record<string, { label: string; color: string }> = {
  reddit: { label: "Reddit", color: "bg-orange-500/10 text-orange-600" },
  twitter: { label: "Twitter / X", color: "bg-sky-500/10 text-sky-600" },
  stackoverflow: { label: "StackOverflow", color: "bg-amber-500/10 text-amber-600" },
  custom: { label: "Custom", color: "bg-gray-500/10 text-gray-600" },
};

function truncateUrl(url: string, maxLength: number = 40): string {
  if (url.length <= maxLength) return url;
  
  try {
    const urlObj = new URL(url);
    const path = urlObj.pathname;
    const truncatedPath = path.length > 20 ? path.slice(0, 20) + "..." : path;
    return `${urlObj.hostname}${truncatedPath}`;
  } catch {
    return url.slice(0, maxLength) + "...";
  }
}

export function ProjectHeader({
  id,
  title,
  status,
  sourceType,
  sourceUrl,
  onDelete,
}: ProjectHeaderProps) {
  const router = useRouter();
  const statusInfo = statusConfig[status] || statusConfig.draft;
  const StatusIcon = statusInfo.icon;
  const sourceInfo = sourceType ? sourceTypeLabels[sourceType] : null;

  return (
    <div className="space-y-4">
      {/* Back button and title */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-4">
          <Link href="/dashboard/projects">
            <Button variant="ghost" size="icon" className="h-9 w-9">
              <ArrowLeft className="h-5 w-5" />
            </Button>
          </Link>
          <div className="space-y-1">
            <h1 className="text-xl sm:text-2xl font-bold tracking-tight line-clamp-1">
              {title || "Untitled Project"}
            </h1>
            <div className="flex flex-wrap items-center gap-2">
              <Badge variant="outline" className={statusInfo.color}>
                <StatusIcon className="h-3 w-3 mr-1" />
                {statusInfo.label}
              </Badge>
              {sourceInfo && (
                <Badge variant="secondary" className={sourceInfo.color}>
                  {sourceInfo.label}
                </Badge>
              )}
            </div>
          </div>
        </div>
        
        {/* Actions */}
        <div className="flex items-center gap-2 ml-13 sm:ml-0">
          <Button
            variant="outline"
            size="sm"
            onClick={() => router.push(`/dashboard/projects/${id}/edit`)}
          >
            <Edit className="h-4 w-4 mr-2" />
            Edit
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={onDelete}
            className="text-destructive hover:text-destructive hover:bg-destructive/10"
          >
            <Trash2 className="h-4 w-4 mr-2" />
            Delete
          </Button>
        </div>
      </div>

      {/* Source URL */}
      {sourceUrl && (
        <div className="ml-13 sm:ml-13 pl-13">
          <a
            href={sourceUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 text-sm text-muted-foreground hover:text-primary transition-colors group max-w-full"
          >
            <ExternalLink className="h-3.5 w-3.5 flex-shrink-0 group-hover:text-primary" />
            <span className="truncate">{truncateUrl(sourceUrl, 60)}</span>
          </a>
        </div>
      )}
    </div>
  );
}
