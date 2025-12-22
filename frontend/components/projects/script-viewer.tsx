"use client";

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Separator } from "@/components/ui/separator";
import {
  FileText,
  Copy,
  Check,
  Clock,
  Sparkles,
  Play,
  Pause,
  Users,
  MessageSquare,
  Music,
  Timer,
  ChevronRight,
  Volume2,
} from "lucide-react";
import { useState, useEffect, useRef } from "react";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

interface DialogueLine {
  text: string;
  speaker: string;
  duration: number;
  start_time: number;
  audio_file_path?: string;
}

interface ScriptDataWithDialogue {
  id?: string;
  background?: string;
  characters?: string[];
  word_count?: number;
  dialogue_lines?: DialogueLine[];
  estimated_duration?: number;
  // Legacy fields
  title?: string;
  hook?: string;
  sections?: Array<{ type: string; content: string; duration?: number }>;
  full_script?: string;
  script?: string;
}

interface ScriptViewerProps {
  data: Record<string, unknown> | null;
}

// Speaker color mapping
const speakerColors: Record<string, { bg: string; text: string; border: string }> = {
  narrator: { bg: "bg-blue-500/10", text: "text-blue-600", border: "border-blue-500/30" },
  op: { bg: "bg-purple-500/10", text: "text-purple-600", border: "border-purple-500/30" },
  commenter1: { bg: "bg-green-500/10", text: "text-green-600", border: "border-green-500/30" },
  commenter2: { bg: "bg-orange-500/10", text: "text-orange-600", border: "border-orange-500/30" },
  commenter3: { bg: "bg-pink-500/10", text: "text-pink-600", border: "border-pink-500/30" },
  default: { bg: "bg-gray-500/10", text: "text-gray-600", border: "border-gray-500/30" },
};

function getSpeakerColor(speaker: string) {
  const key = speaker.toLowerCase();
  return speakerColors[key] || speakerColors.default;
}

function getSpeakerInitials(speaker: string): string {
  if (speaker.toLowerCase() === "narrator") return "N";
  if (speaker.toLowerCase() === "op") return "OP";
  if (speaker.toLowerCase().startsWith("commenter")) {
    return "C" + speaker.replace(/\D/g, "");
  }
  return speaker.charAt(0).toUpperCase();
}

function formatTime(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}:${secs.toString().padStart(2, "0")}`;
}

// Timeline visualization component
function DialogueTimeline({ 
  lines, 
  totalDuration,
  currentTime,
  onSeek 
}: { 
  lines: DialogueLine[];
  totalDuration: number;
  currentTime: number;
  onSeek: (time: number) => void;
}) {
  return (
    <div className="relative h-12 bg-muted rounded-lg overflow-hidden">
      {/* Timeline segments */}
      <div className="absolute inset-0 flex">
        {lines.map((line, index) => {
          const color = getSpeakerColor(line.speaker);
          const widthPercent = (line.duration / totalDuration) * 100;
          const leftPercent = (line.start_time / totalDuration) * 100;
          
          return (
            <div
              key={index}
              className={cn(
                "absolute h-full cursor-pointer transition-opacity hover:opacity-80",
                color.bg,
                "border-r border-background/50"
              )}
              style={{
                left: `${leftPercent}%`,
                width: `${widthPercent}%`,
              }}
              onClick={() => onSeek(line.start_time)}
              title={`${line.speaker}: ${line.text.slice(0, 50)}...`}
            />
          );
        })}
      </div>
      
      {/* Current time indicator */}
      <div 
        className="absolute top-0 bottom-0 w-0.5 bg-primary z-10 transition-all duration-100"
        style={{ left: `${(currentTime / totalDuration) * 100}%` }}
      />
      
      {/* Time markers */}
      <div className="absolute bottom-1 left-2 text-[10px] text-muted-foreground font-mono">
        {formatTime(0)}
      </div>
      <div className="absolute bottom-1 right-2 text-[10px] text-muted-foreground font-mono">
        {formatTime(totalDuration)}
      </div>
    </div>
  );
}

// Dialogue line card component
function DialogueCard({ 
  line, 
  index, 
  isActive,
  onClick 
}: { 
  line: DialogueLine; 
  index: number;
  isActive: boolean;
  onClick: () => void;
}) {
  const color = getSpeakerColor(line.speaker);
  
  return (
    <div
      className={cn(
        "group flex gap-3 p-3 rounded-lg transition-all cursor-pointer",
        isActive 
          ? `${color.bg} border ${color.border} shadow-sm` 
          : "hover:bg-muted/50 border border-transparent"
      )}
      onClick={onClick}
    >
      {/* Timeline indicator */}
      <div className="flex flex-col items-center gap-1 pt-1">
        <span className="text-[10px] font-mono text-muted-foreground w-10 text-center">
          {formatTime(line.start_time)}
        </span>
        <div className={cn(
          "w-0.5 flex-1 rounded-full",
          isActive ? "bg-primary" : "bg-muted"
        )} />
      </div>
      
      {/* Avatar */}
      <Avatar className={cn("h-8 w-8 shrink-0", color.bg)}>
        <AvatarFallback className={cn("text-xs font-semibold", color.text)}>
          {getSpeakerInitials(line.speaker)}
        </AvatarFallback>
      </Avatar>
      
      {/* Content */}
      <div className="flex-1 min-w-0 space-y-1">
        <div className="flex items-center gap-2">
          <span className={cn("text-sm font-medium capitalize", color.text)}>
            {line.speaker}
          </span>
          <Badge variant="outline" className="text-[10px] px-1.5 py-0 h-4">
            {line.duration}s
          </Badge>
        </div>
        <p className={cn(
          "text-sm leading-relaxed",
          isActive ? "text-foreground" : "text-muted-foreground"
        )}>
          {line.text}
        </p>
      </div>
      
      {/* Play indicator */}
      {isActive && (
        <div className="flex items-center">
          <Volume2 className={cn("h-4 w-4 animate-pulse", color.text)} />
        </div>
      )}
    </div>
  );
}

// Main Script Viewer component
export function ScriptViewer({ data }: ScriptViewerProps) {
  const [copied, setCopied] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [activeLineIndex, setActiveLineIndex] = useState(0);
  const playIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  if (!data) {
    return (
      <Card>
        <CardContent className="py-12">
          <div className="text-center text-muted-foreground">
            <FileText className="h-12 w-12 mx-auto mb-3 opacity-50" />
            <p className="font-medium">No script generated yet</p>
            <p className="text-sm mt-1">
              Scrape content first, then generate a script
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  const scriptData = data as ScriptDataWithDialogue;
  const hasDialogueLines = scriptData.dialogue_lines && scriptData.dialogue_lines.length > 0;
  const totalDuration = scriptData.estimated_duration || 0;

  // Update active line based on current time
  useEffect(() => {
    if (hasDialogueLines) {
      const lines = scriptData.dialogue_lines!;
      for (let i = lines.length - 1; i >= 0; i--) {
        if (currentTime >= lines[i].start_time) {
          setActiveLineIndex(i);
          break;
        }
      }
    }
  }, [currentTime, hasDialogueLines, scriptData.dialogue_lines]);

  // Playback simulation
  useEffect(() => {
    if (isPlaying && hasDialogueLines) {
      playIntervalRef.current = setInterval(() => {
        setCurrentTime((prev) => {
          if (prev >= totalDuration) {
            setIsPlaying(false);
            return 0;
          }
          return prev + 0.1;
        });
      }, 100);
    } else {
      if (playIntervalRef.current) {
        clearInterval(playIntervalRef.current);
      }
    }
    return () => {
      if (playIntervalRef.current) {
        clearInterval(playIntervalRef.current);
      }
    };
  }, [isPlaying, hasDialogueLines, totalDuration]);

  const handleCopy = async () => {
    let textToCopy = "";
    if (hasDialogueLines) {
      textToCopy = scriptData.dialogue_lines!
        .map((line) => `[${line.speaker}]: ${line.text}`)
        .join("\n\n");
    } else {
      textToCopy = scriptData.full_script || scriptData.script || JSON.stringify(data, null, 2);
    }
    
    await navigator.clipboard.writeText(textToCopy);
    setCopied(true);
    toast.success("Script copied to clipboard");
    setTimeout(() => setCopied(false), 2000);
  };

  const handleSeek = (time: number) => {
    setCurrentTime(time);
  };

  const handleLineClick = (index: number) => {
    const line = scriptData.dialogue_lines![index];
    setCurrentTime(line.start_time);
    setActiveLineIndex(index);
  };

  const togglePlayback = () => {
    if (currentTime >= totalDuration) {
      setCurrentTime(0);
    }
    setIsPlaying(!isPlaying);
  };

  // Dialogue lines view (new format)
  if (hasDialogueLines) {
    const lines = scriptData.dialogue_lines!;
    const uniqueSpeakers = [...new Set(lines.map((l) => l.speaker.toLowerCase()))];
    
    return (
      <Card className="overflow-hidden">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <CardTitle className="text-base flex items-center gap-2">
                <Sparkles className="h-4 w-4 text-primary" />
                Video Script
              </CardTitle>
              <CardDescription className="flex items-center gap-3">
                <span className="flex items-center gap-1">
                  <MessageSquare className="h-3 w-3" />
                  {lines.length} lines
                </span>
                <span className="flex items-center gap-1">
                  <Timer className="h-3 w-3" />
                  {formatTime(totalDuration)}
                </span>
                <span className="flex items-center gap-1">
                  <Users className="h-3 w-3" />
                  {uniqueSpeakers.length} characters
                </span>
                {scriptData.word_count && (
                  <span className="flex items-center gap-1">
                    <FileText className="h-3 w-3" />
                    {scriptData.word_count} words
                  </span>
                )}
              </CardDescription>
            </div>
            <Button variant="outline" size="sm" onClick={handleCopy}>
              {copied ? (
                <Check className="h-4 w-4 mr-1 text-green-500" />
              ) : (
                <Copy className="h-4 w-4 mr-1" />
              )}
              {copied ? "Copied" : "Copy"}
            </Button>
          </div>
        </CardHeader>

        {/* Character Legend */}
        <div className="px-6 pb-3">
          <div className="flex flex-wrap gap-2">
            {uniqueSpeakers.map((speaker) => {
              const color = getSpeakerColor(speaker);
              return (
                <Badge
                  key={speaker}
                  variant="outline"
                  className={cn("capitalize", color.bg, color.text, color.border)}
                >
                  {speaker}
                </Badge>
              );
            })}
            {scriptData.background && (
              <Badge variant="secondary" className="gap-1">
                <Music className="h-3 w-3" />
                {scriptData.background.replace(/-/g, " ")}
              </Badge>
            )}
          </div>
        </div>

        {/* Timeline & Playback Controls */}
        <div className="px-6 pb-4 space-y-3">
          <DialogueTimeline
            lines={lines}
            totalDuration={totalDuration}
            currentTime={currentTime}
            onSeek={handleSeek}
          />
          
          <div className="flex items-center gap-3">
            <Button
              variant="outline"
              size="sm"
              className="gap-2"
              onClick={togglePlayback}
            >
              {isPlaying ? (
                <>
                  <Pause className="h-4 w-4" />
                  Pause
                </>
              ) : (
                <>
                  <Play className="h-4 w-4" />
                  Preview
                </>
              )}
            </Button>
            <div className="flex-1">
              <Progress value={(currentTime / totalDuration) * 100} className="h-1" />
            </div>
            <span className="text-xs font-mono text-muted-foreground w-20 text-right">
              {formatTime(Math.floor(currentTime))} / {formatTime(totalDuration)}
            </span>
          </div>
        </div>

        <Separator />

        {/* Dialogue Lines */}
        <CardContent className="p-0">
          <ScrollArea className="h-[400px]" ref={scrollRef}>
            <div className="p-4 space-y-1">
              {lines.map((line, index) => (
                <DialogueCard
                  key={index}
                  line={line}
                  index={index}
                  isActive={index === activeLineIndex && isPlaying}
                  onClick={() => handleLineClick(index)}
                />
              ))}
            </div>
          </ScrollArea>
        </CardContent>
      </Card>
    );
  }

  // Legacy sections view
  const hasStructuredSections = scriptData.sections && scriptData.sections.length > 0;
  const fullScript = scriptData.full_script || scriptData.script || "";

  if (!hasStructuredSections && (fullScript || typeof data === "string")) {
    const scriptText = typeof data === "string" ? data : fullScript;
    return (
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-base flex items-center gap-2">
                <Sparkles className="h-4 w-4 text-primary" />
                Generated Script
              </CardTitle>
              {scriptData.word_count && (
                <CardDescription className="mt-1">
                  {scriptData.word_count} words
                  {scriptData.estimated_duration && (
                    <> • ~{Math.round(scriptData.estimated_duration)}s duration</>
                  )}
                </CardDescription>
              )}
            </div>
            <Button variant="outline" size="sm" onClick={handleCopy}>
              {copied ? (
                <Check className="h-4 w-4 mr-1 text-green-500" />
              ) : (
                <Copy className="h-4 w-4 mr-1" />
              )}
              {copied ? "Copied" : "Copy"}
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <ScrollArea className="max-h-[500px]">
            <div className="prose prose-sm dark:prose-invert max-w-none">
              <p className="whitespace-pre-wrap text-sm leading-relaxed">
                {scriptText}
              </p>
            </div>
          </ScrollArea>
        </CardContent>
      </Card>
    );
  }

  // Fallback to raw JSON with better formatting
  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-base">Script Data</CardTitle>
          <Button variant="outline" size="sm" onClick={handleCopy}>
            {copied ? (
              <Check className="h-4 w-4 mr-1 text-green-500" />
            ) : (
              <Copy className="h-4 w-4 mr-1" />
            )}
            {copied ? "Copied" : "Copy"}
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <ScrollArea className="max-h-[500px]">
          <pre className="text-xs bg-muted p-4 rounded-lg overflow-auto whitespace-pre-wrap">
            {JSON.stringify(data, null, 2)}
          </pre>
        </ScrollArea>
      </CardContent>
    </Card>
  );
}
