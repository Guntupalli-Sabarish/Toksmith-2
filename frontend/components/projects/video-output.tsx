"use client";

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Video, Download, Share2, Play, Pause, Volume2, VolumeX, Music } from "lucide-react";
import { useState, useRef } from "react";

interface VideoOutputProps {
  videoUrl: string | null;
  audioUrl?: string | null;
  thumbnailUrl?: string | null;
}

export function VideoOutput({ videoUrl, audioUrl, thumbnailUrl }: VideoOutputProps) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);

  const togglePlay = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause();
      } else {
        videoRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const toggleMute = () => {
    if (videoRef.current) {
      videoRef.current.muted = !isMuted;
      setIsMuted(!isMuted);
    }
  };

  const handleDownload = () => {
    if (videoUrl) {
      const link = document.createElement("a");
      link.href = videoUrl;
      link.download = "video.mp4";
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  const handleAudioDownload = () => {
    if (audioUrl) {
      const link = document.createElement("a");
      link.href = audioUrl;
      link.download = "audio.mp3";
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  // Show audio-only view when no video but has audio
  if (!videoUrl && audioUrl) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <Music className="h-4 w-4 text-primary" />
            Audio Generated
          </CardTitle>
          <CardDescription>Your audio is ready. Video generation is next.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Audio Player */}
          <div className="bg-muted/50 rounded-lg p-6">
            <div className="flex items-center justify-center mb-4">
              <div className="h-20 w-20 rounded-full bg-primary/10 flex items-center justify-center">
                <Music className="h-10 w-10 text-primary" />
              </div>
            </div>
            <audio
              src={audioUrl}
              controls
              className="w-full"
            />
          </div>

          {/* Action Buttons */}
          <div className="flex justify-center gap-2">
            <Button size="sm" onClick={handleAudioDownload}>
              <Download className="h-4 w-4 mr-2" />
              Download Audio
            </Button>
          </div>

          <p className="text-xs text-center text-muted-foreground">
            Generate video to combine audio with visuals
          </p>
        </CardContent>
      </Card>
    );
  }

  if (!videoUrl) {
    return (
      <Card>
        <CardContent className="py-12">
          <div className="text-center text-muted-foreground">
            <Video className="h-12 w-12 mx-auto mb-3 opacity-50" />
            <p className="font-medium">No video generated yet</p>
            <p className="text-sm mt-1">
              Complete the generation pipeline to create your video
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base flex items-center gap-2">
          <Video className="h-4 w-4 text-primary" />
          Video Output
        </CardTitle>
        <CardDescription>Your generated video is ready</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Video Player */}
        <div className="relative aspect-[9/16] max-w-sm mx-auto bg-black rounded-lg overflow-hidden group">
          <video
            ref={videoRef}
            src={videoUrl}
            poster={thumbnailUrl || undefined}
            className="w-full h-full object-contain"
            onPlay={() => setIsPlaying(true)}
            onPause={() => setIsPlaying(false)}
            onEnded={() => setIsPlaying(false)}
          />
          
          {/* Play/Pause Overlay */}
          <div 
            className="absolute inset-0 flex items-center justify-center bg-black/30 opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer"
            onClick={togglePlay}
          >
            <Button
              variant="secondary"
              size="icon"
              className="h-14 w-14 rounded-full"
            >
              {isPlaying ? (
                <Pause className="h-6 w-6" />
              ) : (
                <Play className="h-6 w-6 ml-1" />
              )}
            </Button>
          </div>

          {/* Volume Control */}
          <Button
            variant="secondary"
            size="icon"
            className="absolute bottom-3 right-3 h-8 w-8 rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
            onClick={(e) => {
              e.stopPropagation();
              toggleMute();
            }}
          >
            {isMuted ? (
              <VolumeX className="h-4 w-4" />
            ) : (
              <Volume2 className="h-4 w-4" />
            )}
          </Button>
        </div>

        {/* Action Buttons */}
        <div className="flex justify-center gap-2">
          <Button size="sm" onClick={handleDownload}>
            <Download className="h-4 w-4 mr-2" />
            Download
          </Button>
          <Button size="sm" variant="outline">
            <Share2 className="h-4 w-4 mr-2" />
            Share
          </Button>
        </div>

        {/* Audio Track (if separate) */}
        {audioUrl && (
          <div className="pt-4 border-t">
            <p className="text-sm font-medium mb-2">Audio Track</p>
            <audio
              src={audioUrl}
              controls
              className="w-full h-10"
            />
          </div>
        )}
      </CardContent>
    </Card>
  );
}
