"use client";

import { useEffect, useState, use } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";

import {
  ProjectHeader,
  ProjectDetails,
  ScrapedContent,
  ScriptViewer,
  VideoOutput,
  GenerationWorkflow,
  ProjectPageSkeleton,
} from "@/components/projects";

import { useProjectsStore } from "@/lib/stores";

export default function ProjectDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const router = useRouter();
  const {
    currentProject: project,
    isLoading,
    isGenerating,
    fetchProject,
    deleteProject,
    scrapeContent,
    generateScript,
    generateAudio,
    generateVideo,
    generateFull,
  } = useProjectsStore();

  const [showDelete, setShowDelete] = useState(false);
  const [activeTab, setActiveTab] = useState("content");

  useEffect(() => {
    fetchProject(id);
  }, [fetchProject, id]);

  // Auto-switch tabs based on generation progress
  useEffect(() => {
    if (project) {
      if (project.video_url) {
        setActiveTab("output");
      } else if (project.script_data && !project.scraped_data) {
        setActiveTab("script");
      }
    }
  }, [project?.status]);

  const handleDelete = async () => {
    try {
      await deleteProject(id);
      toast.success("Project deleted successfully");
      router.push("/dashboard/projects");
    } catch {
      toast.error("Failed to delete project");
    }
  };

  const handleScrape = async () => {
    try {
      await scrapeContent(id);
      toast.success("Content scraped successfully");
      setActiveTab("content");
    } catch {
      toast.error("Failed to scrape content");
    }
  };

  const handleGenerateScript = async () => {
    try {
      await generateScript(id);
      toast.success("Script generated successfully");
      setActiveTab("script");
    } catch {
      toast.error("Failed to generate script");
    }
  };

  const handleGenerateAudio = async () => {
    try {
      await generateAudio(id);
      toast.success("Audio generated successfully");
      setActiveTab("output");
    } catch {
      toast.error("Failed to generate audio");
    }
  };

  const handleGenerateVideo = async () => {
    try {
      await generateVideo(id);
      toast.success("Video generated successfully");
      setActiveTab("output");
    } catch {
      toast.error("Failed to generate video");
    }
  };

  const handleGenerateFull = async () => {
    try {
      await generateFull(id);
      toast.success("Video generation started");
    } catch {
      toast.error("Failed to start generation");
    }
  };

  // Loading state
  if (isLoading || !project) {
    return <ProjectPageSkeleton />;
  }

  return (
    <div className="max-w-5xl mx-auto space-y-6 pb-8">
      {/* Header */}
      <ProjectHeader
        id={id}
        title={project.title}
        status={project.status}
        sourceType={project.source_type}
        sourceUrl={project.source_url}
        onDelete={() => setShowDelete(true)}
      />

      {/* Main Content */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Left Column - Content Tabs */}
        <div className="lg:col-span-2 space-y-6">
          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="content" className="relative">
                Content
                {project.scraped_data && (
                  <span className="absolute -top-1 -right-1 h-2 w-2 bg-green-500 rounded-full" />
                )}
              </TabsTrigger>
              <TabsTrigger value="script" className="relative">
                Script
                {project.script_data && (
                  <span className="absolute -top-1 -right-1 h-2 w-2 bg-green-500 rounded-full" />
                )}
              </TabsTrigger>
              <TabsTrigger value="output" className="relative">
                Output
                {(project.video_url || project.audio_url) && (
                  <span className="absolute -top-1 -right-1 h-2 w-2 bg-green-500 rounded-full" />
                )}
              </TabsTrigger>
            </TabsList>

            <TabsContent value="content" className="mt-4 space-y-4">
              {/* Project Details */}
              <ProjectDetails
                description={project.description}
                videoStyle={project.video_style}
                createdAt={project.created_at}
              />

              {/* Scraped Content */}
              <ScrapedContent
                data={project.scraped_data}
                sourceType={project.source_type}
              />
            </TabsContent>

            <TabsContent value="script" className="mt-4">
              <ScriptViewer data={project.script_data} />
            </TabsContent>

            <TabsContent value="output" className="mt-4">
              <VideoOutput
                videoUrl={project.video_url}
                audioUrl={project.audio_url}
                thumbnailUrl={project.thumbnail_url}
              />
            </TabsContent>
          </Tabs>
        </div>

        {/* Right Column - Workflow */}
        <div className="space-y-4">
          <GenerationWorkflow
            status={project.status}
            hasScrapedData={!!project.scraped_data}
            hasScriptData={!!project.script_data}
            hasAudioGenerated={
              project.status === "audio_generated" ||
              project.status === "video_generated" ||
              project.status === "completed" ||
              !!project.audio_url
            }
            hasVideoUrl={!!project.video_url}
            isGenerating={isGenerating}
            onScrape={handleScrape}
            onGenerateScript={handleGenerateScript}
            onGenerateAudio={handleGenerateAudio}
            onGenerateVideo={handleGenerateVideo}
            onGenerateFull={handleGenerateFull}
          />
        </div>
      </div>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={showDelete} onOpenChange={setShowDelete}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Project</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete &quot;{project.title || "Untitled Project"}&quot;?
              This action cannot be undone and all generated content will be lost.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDelete}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              Delete Project
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
