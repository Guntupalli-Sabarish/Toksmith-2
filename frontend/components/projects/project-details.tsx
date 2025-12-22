"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";
import { Calendar, Palette, Info } from "lucide-react";

interface ProjectDetailsProps {
  description: string | null;
  videoStyle: string;
  createdAt: string | null;
}

const videoStyleLabels: Record<string, { label: string; description: string }> = {
  tiktok: { label: "TikTok", description: "Vertical 9:16, fast-paced" },
  youtube_short: { label: "YouTube Shorts", description: "Vertical 9:16, engaging" },
  instagram_reel: { label: "Instagram Reel", description: "Vertical 9:16, trendy" },
  youtube: { label: "YouTube", description: "Horizontal 16:9, detailed" },
};

export function ProjectDetails({ description, videoStyle, createdAt }: ProjectDetailsProps) {
  const styleInfo = videoStyleLabels[videoStyle] || { 
    label: videoStyle.replace("_", " "), 
    description: "" 
  };

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-base flex items-center gap-2">
          <Info className="h-4 w-4" />
          Project Details
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {description && (
          <div>
            <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-1.5">
              Description
            </p>
            <p className="text-sm leading-relaxed">{description}</p>
          </div>
        )}

        <Separator />

        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-1.5 flex items-center gap-1">
              <Palette className="h-3 w-3" />
              Video Style
            </p>
            <div>
              <Badge variant="secondary" className="capitalize">
                {styleInfo.label}
              </Badge>
              {styleInfo.description && (
                <p className="text-xs text-muted-foreground mt-1">
                  {styleInfo.description}
                </p>
              )}
            </div>
          </div>
          <div>
            <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-1.5 flex items-center gap-1">
              <Calendar className="h-3 w-3" />
              Created
            </p>
            <p className="text-sm">
              {createdAt
                ? new Date(createdAt).toLocaleDateString("en-US", {
                    year: "numeric",
                    month: "short",
                    day: "numeric",
                  })
                : "—"}
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
