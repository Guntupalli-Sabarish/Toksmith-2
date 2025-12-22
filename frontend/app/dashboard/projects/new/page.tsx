"use client";

import { useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { toast } from "sonner";
import {
  ArrowLeft,
  Loader2,
  Link as LinkIcon,
  Sparkles,
  Video,
  Instagram,
  Youtube,
} from "lucide-react";
import Link from "next/link";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useProjectsStore } from "@/lib/stores";
import { SourceType, VideoStyle } from "@/lib/api/types";

const projectSchema = z.object({
  title: z.string().optional(),
  description: z.string().optional(),
  source_url: z.string().url("Please enter a valid URL"),
  source_type: z.enum(["reddit", "twitter", "stackoverflow", "custom"]).optional(),
  video_style: z.enum(["tiktok", "youtube_short", "instagram_reel", "youtube"]),
});

type ProjectFormData = z.infer<typeof projectSchema>;

const sourceTypes = [
  { value: "reddit", label: "Reddit", icon: "🔥", color: "orange" },
  { value: "twitter", label: "Twitter / X", icon: "🐦", color: "blue" },
  { value: "stackoverflow", label: "StackOverflow", icon: "📚", color: "yellow" },
  { value: "custom", label: "Custom URL", icon: "🔗", color: "purple" },
];

const videoStyles = [
  {
    value: "tiktok",
    label: "TikTok",
    icon: Video,
    description: "Vertical 9:16, 60s max",
  },
  {
    value: "youtube_short",
    label: "YouTube Shorts",
    icon: Youtube,
    description: "Vertical 9:16, 60s max",
  },
  {
    value: "instagram_reel",
    label: "Instagram Reel",
    icon: Instagram,
    description: "Vertical 9:16, 90s max",
  },
  {
    value: "youtube",
    label: "YouTube",
    icon: Youtube,
    description: "Horizontal 16:9",
  },
];

export default function NewProjectPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { createProject, isCreating } = useProjectsStore();
  const [selectedSource, setSelectedSource] = useState<SourceType | null>(
    (searchParams.get("source") as SourceType) || null
  );

  const form = useForm<ProjectFormData>({
    resolver: zodResolver(projectSchema),
    defaultValues: {
      title: "",
      description: "",
      source_url: "",
      source_type: (searchParams.get("source") as SourceType) || undefined,
      video_style: "tiktok",
    },
  });

  const onSubmit = async (data: ProjectFormData) => {
    try {
      const project = await createProject({
        ...data,
        source_type: selectedSource || undefined,
      });
      toast.success("Project created successfully!");
      router.push(`/dashboard/projects/${project.id}`);
    } catch {
      toast.error("Failed to create project");
    }
  };

  const detectSourceType = (url: string): SourceType | null => {
    if (url.includes("reddit.com")) return "reddit";
    if (url.includes("twitter.com") || url.includes("x.com")) return "twitter";
    if (url.includes("stackoverflow.com")) return "stackoverflow";
    return "custom";
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link href="/dashboard/projects">
          <Button variant="ghost" size="icon">
            <ArrowLeft className="h-5 w-5" />
          </Button>
        </Link>
        <div>
          <h1 className="text-3xl font-bold tracking-tight">New Project</h1>
          <p className="text-muted-foreground">
            Create a new video generation project
          </p>
        </div>
      </div>

      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
          {/* Source Selection */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <LinkIcon className="h-5 w-5" />
                Content Source
              </CardTitle>
              <CardDescription>
                Choose where to pull your content from
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Source Type Buttons */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {sourceTypes.map((source) => (
                  <button
                    key={source.value}
                    type="button"
                    onClick={() => {
                      setSelectedSource(source.value as SourceType);
                      form.setValue("source_type", source.value as SourceType);
                    }}
                    className={`p-4 rounded-xl border-2 text-center transition-all ${
                      selectedSource === source.value
                        ? "border-primary bg-primary/5"
                        : "border-border hover:border-primary/50"
                    }`}
                  >
                    <span className="text-2xl mb-2 block">{source.icon}</span>
                    <span className="text-sm font-medium">{source.label}</span>
                  </button>
                ))}
              </div>

              {/* Source URL */}
              <FormField
                control={form.control}
                name="source_url"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Source URL</FormLabel>
                    <FormControl>
                      <Input
                        placeholder="https://reddit.com/r/..."
                        className="h-12 bg-secondary/50 border-0"
                        {...field}
                        onChange={(e) => {
                          field.onChange(e);
                          const detected = detectSourceType(e.target.value);
                          if (detected && !selectedSource) {
                            setSelectedSource(detected);
                            form.setValue("source_type", detected);
                          }
                        }}
                      />
                    </FormControl>
                    <FormDescription>
                      Paste the URL of the content you want to transform
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </CardContent>
          </Card>

          {/* Video Style */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Video className="h-5 w-5" />
                Video Style
              </CardTitle>
              <CardDescription>
                Choose the format for your output video
              </CardDescription>
            </CardHeader>
            <CardContent>
              <FormField
                control={form.control}
                name="video_style"
                render={({ field }) => (
                  <FormItem>
                    <FormControl>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                        {videoStyles.map((style) => {
                          const Icon = style.icon;
                          return (
                            <button
                              key={style.value}
                              type="button"
                              onClick={() => field.onChange(style.value)}
                              className={`p-4 rounded-xl border-2 text-left transition-all ${
                                field.value === style.value
                                  ? "border-primary bg-primary/5"
                                  : "border-border hover:border-primary/50"
                              }`}
                            >
                              <Icon className="h-5 w-5 mb-2 text-muted-foreground" />
                              <span className="text-sm font-medium block">
                                {style.label}
                              </span>
                              <span className="text-xs text-muted-foreground">
                                {style.description}
                              </span>
                            </button>
                          );
                        })}
                      </div>
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </CardContent>
          </Card>

          {/* Project Details */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Sparkles className="h-5 w-5" />
                Project Details
              </CardTitle>
              <CardDescription>
                Optional details to help organize your project
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <FormField
                control={form.control}
                name="title"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Title</FormLabel>
                    <FormControl>
                      <Input
                        placeholder="My awesome video project"
                        className="h-12 bg-secondary/50 border-0"
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="description"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Description</FormLabel>
                    <FormControl>
                      <Textarea
                        placeholder="Brief description of what this video is about..."
                        className="min-h-[100px] bg-secondary/50 border-0 resize-none"
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </CardContent>
          </Card>

          {/* Submit */}
          <div className="flex items-center justify-end gap-4">
            <Link href="/dashboard/projects">
              <Button type="button" variant="outline">
                Cancel
              </Button>
            </Link>
            <Button type="submit" size="lg" disabled={isCreating}>
              {isCreating ? (
                <Loader2 className="h-5 w-5 animate-spin" />
              ) : (
                <>
                  <Sparkles className="h-4 w-4 mr-2" />
                  Create Project
                </>
              )}
            </Button>
          </div>
        </form>
      </Form>
    </div>
  );
}
