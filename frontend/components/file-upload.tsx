"use client";

import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { toast } from "sonner";
import {
  Upload,
  X,
  FileVideo,
  FileAudio,
  FileImage,
  Loader2,
  Check,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { cn } from "@/lib/utils";
import { storageApi, FileType } from "@/lib/api";

interface FileUploadProps {
  fileType: FileType;
  projectId?: string;
  onUploadComplete?: (file: { file_id: string; public_url: string }) => void;
  accept?: Record<string, string[]>;
  maxSize?: number;
  className?: string;
}

interface UploadingFile {
  file: File;
  progress: number;
  status: "uploading" | "complete" | "error";
}

const fileTypeIcons: Record<FileType, React.ElementType> = {
  video: FileVideo,
  audio: FileAudio,
  image: FileImage,
  avatar: FileImage,
  thumbnail: FileImage,
  asset: FileImage,
};

export function FileUpload({
  fileType,
  projectId,
  onUploadComplete,
  accept,
  maxSize = 100 * 1024 * 1024, // 100MB default
  className,
}: FileUploadProps) {
  const [uploadingFiles, setUploadingFiles] = useState<UploadingFile[]>([]);

  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      for (const file of acceptedFiles) {
        setUploadingFiles((prev) => [
          ...prev,
          { file, progress: 0, status: "uploading" },
        ]);

        try {
          // Simulate progress (actual progress would need axios onUploadProgress)
          const progressInterval = setInterval(() => {
            setUploadingFiles((prev) =>
              prev.map((f) =>
                f.file === file && f.progress < 90
                  ? { ...f, progress: f.progress + 10 }
                  : f
              )
            );
          }, 200);

          const result = await storageApi.uploadFile(file, fileType, {
            projectId,
            makePublic: true,
          });

          clearInterval(progressInterval);

          setUploadingFiles((prev) =>
            prev.map((f) =>
              f.file === file ? { ...f, progress: 100, status: "complete" } : f
            )
          );

          onUploadComplete?.({
            file_id: result.file_id,
            public_url: result.public_url,
          });

          toast.success(`${file.name} uploaded successfully`);

          // Remove completed file after animation
          setTimeout(() => {
            setUploadingFiles((prev) => prev.filter((f) => f.file !== file));
          }, 2000);
        } catch {
          setUploadingFiles((prev) =>
            prev.map((f) =>
              f.file === file ? { ...f, status: "error" } : f
            )
          );
          toast.error(`Failed to upload ${file.name}`);
        }
      }
    },
    [fileType, projectId, onUploadComplete]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept,
    maxSize,
    multiple: true,
  });

  const Icon = fileTypeIcons[fileType];

  return (
    <div className={className}>
      <div
        {...getRootProps()}
        className={cn(
          "relative border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all",
          isDragActive
            ? "border-primary bg-primary/5"
            : "border-muted-foreground/25 hover:border-primary/50 hover:bg-accent/50"
        )}
      >
        <input {...getInputProps()} />
        <div className="flex flex-col items-center gap-3">
          <div
            className={cn(
              "h-14 w-14 rounded-full flex items-center justify-center transition-colors",
              isDragActive ? "bg-primary/10" : "bg-muted"
            )}
          >
            <Upload
              className={cn(
                "h-6 w-6 transition-colors",
                isDragActive ? "text-primary" : "text-muted-foreground"
              )}
            />
          </div>
          <div>
            <p className="font-medium">
              {isDragActive
                ? "Drop files here"
                : "Drag & drop files here, or click to browse"}
            </p>
            <p className="text-sm text-muted-foreground mt-1">
              Max file size: {Math.round(maxSize / 1024 / 1024)}MB
            </p>
          </div>
        </div>
      </div>

      {/* Upload Progress */}
      {uploadingFiles.length > 0 && (
        <div className="mt-4 space-y-2">
          {uploadingFiles.map((item, index) => (
            <div
              key={index}
              className="flex items-center gap-3 p-3 rounded-lg bg-muted/50"
            >
              <Icon className="h-5 w-5 text-muted-foreground shrink-0" />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">{item.file.name}</p>
                <Progress value={item.progress} className="h-1.5 mt-1" />
              </div>
              {item.status === "uploading" && (
                <Loader2 className="h-4 w-4 animate-spin text-primary" />
              )}
              {item.status === "complete" && (
                <Check className="h-4 w-4 text-green-500" />
              )}
              {item.status === "error" && (
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-6 w-6"
                  onClick={() =>
                    setUploadingFiles((prev) =>
                      prev.filter((f) => f.file !== item.file)
                    )
                  }
                >
                  <X className="h-4 w-4 text-destructive" />
                </Button>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
