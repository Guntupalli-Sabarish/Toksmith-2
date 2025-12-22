"use client";

import { useEffect, useState } from "react";
import { toast } from "sonner";
import {
  Upload,
  Search,
  Filter,
  Grid3X3,
  List,
  Trash2,
  Download,
  MoreHorizontal,
  FileVideo,
  FileAudio,
  FileImage,
  File,
  ExternalLink,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
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
import { FileUpload } from "@/components/file-upload";
import { storageApi, FileType, FileUpload as FileUploadType } from "@/lib/api";

const fileTypeIcons: Record<FileType, React.ElementType> = {
  video: FileVideo,
  audio: FileAudio,
  image: FileImage,
  avatar: FileImage,
  thumbnail: FileImage,
  asset: File,
};

const fileTypeColors: Record<FileType, string> = {
  video: "bg-purple-500/10 text-purple-600",
  audio: "bg-blue-500/10 text-blue-600",
  image: "bg-green-500/10 text-green-600",
  avatar: "bg-orange-500/10 text-orange-600",
  thumbnail: "bg-teal-500/10 text-teal-600",
  asset: "bg-gray-500/10 text-gray-600",
};

export default function MediaPage() {
  const [files, setFiles] = useState<FileUploadType[]>([]);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [viewMode, setViewMode] = useState<"grid" | "list">("grid");
  const [searchQuery, setSearchQuery] = useState("");
  const [fileTypeFilter, setFileTypeFilter] = useState<FileType | "all">("all");
  const [showUpload, setShowUpload] = useState(false);
  const [deleteId, setDeleteId] = useState<string | null>(null);

  const fetchFiles = async () => {
    setIsLoading(true);
    try {
      const response = await storageApi.listFiles({
        file_type: fileTypeFilter === "all" ? undefined : fileTypeFilter,
        limit: 50,
      });
      setFiles(response.files);
      setTotal(response.total);
    } catch {
      toast.error("Failed to load files");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchFiles();
  }, [fileTypeFilter]);

  const handleDelete = async () => {
    if (!deleteId) return;
    try {
      await storageApi.deleteFile(deleteId);
      setFiles((prev) => prev.filter((f) => f.file_id !== deleteId));
      setTotal((prev) => prev - 1);
      toast.success("File deleted");
      setDeleteId(null);
    } catch {
      toast.error("Failed to delete file");
    }
  };

  const handleDownload = async (file: FileUploadType) => {
    try {
      const { signed_url } = await storageApi.getSignedUrl(file.file_id);
      window.open(signed_url, "_blank");
    } catch {
      toast.error("Failed to get download link");
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  };

  const filteredFiles = files.filter((f) =>
    f.file_name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Media Library</h1>
          <p className="text-muted-foreground">
            Manage your uploaded files and media assets
          </p>
        </div>
        <Dialog open={showUpload} onOpenChange={setShowUpload}>
          <DialogTrigger asChild>
            <Button size="lg" className="gap-2">
              <Upload className="h-5 w-5" />
              Upload Files
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Upload Files</DialogTitle>
              <DialogDescription>
                Upload videos, audio, images, or other assets
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <FileUpload
                fileType="asset"
                onUploadComplete={() => {
                  fetchFiles();
                }}
                accept={{
                  "video/*": [".mp4", ".webm", ".mov"],
                  "audio/*": [".mp3", ".wav", ".m4a"],
                  "image/*": [".jpg", ".jpeg", ".png", ".gif", ".webp"],
                }}
              />
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="py-4">
          <div className="flex flex-col gap-4 md:flex-row md:items-center">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Search files..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 bg-secondary/50 border-0"
              />
            </div>
            <div className="flex items-center gap-2">
              <Filter className="h-4 w-4 text-muted-foreground" />
              <Select
                value={fileTypeFilter}
                onValueChange={(v) => setFileTypeFilter(v as FileType | "all")}
              >
                <SelectTrigger className="w-[150px] bg-secondary/50 border-0">
                  <SelectValue placeholder="File type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Types</SelectItem>
                  <SelectItem value="video">Videos</SelectItem>
                  <SelectItem value="audio">Audio</SelectItem>
                  <SelectItem value="image">Images</SelectItem>
                  <SelectItem value="asset">Assets</SelectItem>
                </SelectContent>
              </Select>
              <div className="flex items-center border rounded-lg overflow-hidden">
                <Button
                  variant={viewMode === "grid" ? "secondary" : "ghost"}
                  size="icon"
                  className="h-9 w-9 rounded-none"
                  onClick={() => setViewMode("grid")}
                >
                  <Grid3X3 className="h-4 w-4" />
                </Button>
                <Button
                  variant={viewMode === "list" ? "secondary" : "ghost"}
                  size="icon"
                  className="h-9 w-9 rounded-none"
                  onClick={() => setViewMode("list")}
                >
                  <List className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Files Display */}
      {isLoading ? (
        <div
          className={
            viewMode === "grid"
              ? "grid gap-4 md:grid-cols-2 lg:grid-cols-4"
              : "space-y-2"
          }
        >
          {[...Array(8)].map((_, i) => (
            <Card key={i}>
              <CardContent className="p-4">
                <Skeleton
                  className={viewMode === "grid" ? "h-32 w-full" : "h-16 w-full"}
                />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : filteredFiles.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-16">
            <div className="rounded-full bg-muted p-4 mb-4">
              <Upload className="h-8 w-8 text-muted-foreground" />
            </div>
            <h3 className="text-lg font-semibold mb-1">No files found</h3>
            <p className="text-muted-foreground mb-4 text-center max-w-sm">
              {searchQuery || fileTypeFilter !== "all"
                ? "Try adjusting your filters"
                : "Upload your first file to get started"}
            </p>
            {!searchQuery && fileTypeFilter === "all" && (
              <Button onClick={() => setShowUpload(true)}>
                <Upload className="h-4 w-4 mr-2" />
                Upload Files
              </Button>
            )}
          </CardContent>
        </Card>
      ) : viewMode === "grid" ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {filteredFiles.map((file) => {
            const Icon = fileTypeIcons[file.file_type];
            return (
              <Card
                key={file.file_id}
                className="group overflow-hidden hover:border-primary/50 transition-colors"
              >
                <div className="aspect-square bg-muted relative flex items-center justify-center">
                  {file.file_type === "image" ? (
                    <img
                      src={file.public_url}
                      alt={file.file_name}
                      className="w-full h-full object-cover"
                    />
                  ) : file.file_type === "video" ? (
                    <video
                      src={file.public_url}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <Icon className="h-16 w-16 text-muted-foreground" />
                  )}
                  <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
                    <Button
                      variant="secondary"
                      size="icon"
                      onClick={() => handleDownload(file)}
                    >
                      <Download className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="secondary"
                      size="icon"
                      onClick={() => window.open(file.public_url, "_blank")}
                    >
                      <ExternalLink className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="secondary"
                      size="icon"
                      onClick={() => setDeleteId(file.file_id)}
                    >
                      <Trash2 className="h-4 w-4 text-destructive" />
                    </Button>
                  </div>
                </div>
                <CardContent className="p-3">
                  <p className="font-medium text-sm truncate">{file.file_name}</p>
                  <div className="flex items-center justify-between mt-1">
                    <Badge
                      variant="secondary"
                      className={`text-xs capitalize ${fileTypeColors[file.file_type]}`}
                    >
                      {file.file_type}
                    </Badge>
                    <span className="text-xs text-muted-foreground">
                      {formatFileSize(file.file_size)}
                    </span>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      ) : (
        <div className="space-y-2">
          {filteredFiles.map((file) => {
            const Icon = fileTypeIcons[file.file_type];
            return (
              <Card key={file.file_id} className="group">
                <CardContent className="p-4">
                  <div className="flex items-center gap-4">
                    <div
                      className={`h-12 w-12 rounded-lg flex items-center justify-center ${fileTypeColors[file.file_type]}`}
                    >
                      <Icon className="h-6 w-6" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="font-medium truncate">{file.file_name}</p>
                      <p className="text-sm text-muted-foreground">
                        {formatFileSize(file.file_size)} • {formatDate(file.created_at)}
                      </p>
                    </div>
                    <Badge
                      variant="secondary"
                      className={`capitalize ${fileTypeColors[file.file_type]}`}
                    >
                      {file.file_type}
                    </Badge>
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="icon">
                          <MoreHorizontal className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem onClick={() => handleDownload(file)}>
                          <Download className="h-4 w-4 mr-2" />
                          Download
                        </DropdownMenuItem>
                        <DropdownMenuItem
                          onClick={() => window.open(file.public_url, "_blank")}
                        >
                          <ExternalLink className="h-4 w-4 mr-2" />
                          Open
                        </DropdownMenuItem>
                        <DropdownMenuItem
                          onClick={() => setDeleteId(file.file_id)}
                          className="text-destructive"
                        >
                          <Trash2 className="h-4 w-4 mr-2" />
                          Delete
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}

      {/* Stats */}
      {!isLoading && files.length > 0 && (
        <p className="text-sm text-muted-foreground text-center">
          Showing {filteredFiles.length} of {total} files
        </p>
      )}

      {/* Delete Confirmation */}
      <AlertDialog open={!!deleteId} onOpenChange={() => setDeleteId(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete File</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete this file? This action cannot be
              undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDelete}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
