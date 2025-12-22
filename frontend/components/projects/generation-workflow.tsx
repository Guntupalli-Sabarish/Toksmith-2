"use client";

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import {
  CheckCircle,
  Circle,
  Loader2,
  FileText,
  Mic,
  Video,
  Play,
  RefreshCw,
  ChevronRight,
  AlertCircle,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface WorkflowStep {
  id: string;
  label: string;
  description: string;
  icon: React.ElementType;
  isComplete: boolean;
  isActive: boolean;
  isDisabled: boolean;
  action?: () => void;
}

interface GenerationWorkflowProps {
  status: string;
  hasScrapedData: boolean;
  hasScriptData: boolean;
  hasAudioUrl: boolean;
  hasVideoUrl: boolean;
  isGenerating: boolean;
  onScrape: () => void;
  onGenerateScript: () => void;
  onGenerateAudio?: () => void;
  onGenerateVideo?: () => void;
  onGenerateFull: () => void;
}

export function GenerationWorkflow({
  status,
  hasScrapedData,
  hasScriptData,
  hasAudioUrl,
  hasVideoUrl,
  isGenerating,
  onScrape,
  onGenerateScript,
  onGenerateAudio,
  onGenerateVideo,
  onGenerateFull,
}: GenerationWorkflowProps) {
  const steps: WorkflowStep[] = [
    {
      id: "scrape",
      label: "Scrape Content",
      description: "Extract content from source URL",
      icon: FileText,
      isComplete: hasScrapedData,
      isActive: !hasScrapedData && status !== "failed",
      isDisabled: false,
      action: onScrape,
    },
    {
      id: "script",
      label: "Generate Script",
      description: "AI creates video script",
      icon: FileText,
      isComplete: hasScriptData,
      isActive: hasScrapedData && !hasScriptData && status !== "failed",
      isDisabled: !hasScrapedData,
      action: onGenerateScript,
    },
    {
      id: "audio",
      label: "Generate Audio",
      description: "Convert script to speech",
      icon: Mic,
      isComplete: hasAudioUrl,
      isActive: hasScriptData && !hasAudioUrl && status !== "failed",
      isDisabled: !hasScriptData,
      action: onGenerateAudio,
    },
    {
      id: "video",
      label: "Generate Video",
      description: "Create final video output",
      icon: Video,
      isComplete: hasVideoUrl,
      isActive: hasAudioUrl && !hasVideoUrl && status !== "failed",
      isDisabled: !hasAudioUrl,
      action: onGenerateVideo,
    },
  ];

  // Calculate progress
  const completedSteps = steps.filter((s) => s.isComplete).length;
  const progress = (completedSteps / steps.length) * 100;

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-base">Generation Pipeline</CardTitle>
        <CardDescription>
          {status === "completed"
            ? "Video generation complete!"
            : status === "failed"
            ? "Generation failed. You can retry."
            : `Step ${completedSteps + 1} of ${steps.length}`}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Progress indicator */}
        <div className="relative">
          <div className="h-2 w-full bg-muted rounded-full overflow-hidden">
            <div
              className={cn(
                "h-full transition-all duration-500 ease-out rounded-full",
                status === "failed" ? "bg-red-500" : "bg-primary"
              )}
              style={{ width: `${progress}%` }}
            />
          </div>
          <div className="flex justify-between mt-1">
            <span className="text-xs text-muted-foreground">
              {completedSteps} completed
            </span>
            <span className="text-xs text-muted-foreground">{Math.round(progress)}%</span>
          </div>
        </div>

        {/* Steps */}
        <div className="space-y-2">
          {steps.map((step, index) => {
            const StepIcon = step.icon;
            return (
              <div
                key={step.id}
                className={cn(
                  "flex items-center gap-3 p-3 rounded-lg transition-colors",
                  step.isActive && "bg-primary/5 border border-primary/20",
                  step.isComplete && "bg-green-500/5",
                  step.isDisabled && !step.isComplete && "opacity-50"
                )}
              >
                {/* Status Icon */}
                <div
                  className={cn(
                    "flex-shrink-0 h-8 w-8 rounded-full flex items-center justify-center",
                    step.isComplete && "bg-green-500/10 text-green-600",
                    step.isActive && "bg-primary/10 text-primary",
                    !step.isComplete && !step.isActive && "bg-muted text-muted-foreground"
                  )}
                >
                  {isGenerating && step.isActive ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : step.isComplete ? (
                    <CheckCircle className="h-4 w-4" />
                  ) : (
                    <span className="text-xs font-medium">{index + 1}</span>
                  )}
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  <p
                    className={cn(
                      "text-sm font-medium",
                      step.isComplete && "text-green-600",
                      step.isActive && "text-primary"
                    )}
                  >
                    {step.label}
                  </p>
                  <p className="text-xs text-muted-foreground truncate">
                    {step.description}
                  </p>
                </div>

                {/* Action */}
                {step.action && !step.isComplete && (
                  <Button
                    variant={step.isActive ? "default" : "ghost"}
                    size="sm"
                    disabled={step.isDisabled || isGenerating}
                    onClick={step.action}
                    className="flex-shrink-0"
                  >
                    {isGenerating && step.isActive ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <>
                        Run
                        <ChevronRight className="h-3 w-3 ml-1" />
                      </>
                    )}
                  </Button>
                )}

                {step.isComplete && (
                  <CheckCircle className="h-5 w-5 text-green-500 flex-shrink-0" />
                )}
              </div>
            );
          })}
        </div>

        <Separator />

        {/* Full Pipeline Button */}
        <Button
          className="w-full"
          size="lg"
          disabled={isGenerating || status === "completed"}
          onClick={onGenerateFull}
        >
          {isGenerating ? (
            <>
              <Loader2 className="h-5 w-5 mr-2 animate-spin" />
              Processing...
            </>
          ) : status === "completed" ? (
            <>
              <CheckCircle className="h-5 w-5 mr-2" />
              Generation Complete
            </>
          ) : (
            <>
              <Play className="h-5 w-5 mr-2" />
              Run Full Pipeline
            </>
          )}
        </Button>

        {status === "failed" && (
          <Button
            variant="outline"
            className="w-full"
            onClick={onGenerateFull}
            disabled={isGenerating}
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Retry Generation
          </Button>
        )}

        {status === "failed" && (
          <div className="flex items-center gap-2 text-sm text-red-500 bg-red-500/10 p-3 rounded-lg">
            <AlertCircle className="h-4 w-4 flex-shrink-0" />
            <p>Generation failed. Please try again or contact support.</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
