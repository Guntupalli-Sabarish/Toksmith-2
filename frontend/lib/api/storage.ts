import { apiClient } from "./client";
import { FileUpload, FileListResponse, SignedUrlResponse, FileType } from "./types";

export const storageApi = {
  uploadFile: async (
    file: File,
    fileType: FileType,
    options?: { projectId?: string; makePublic?: boolean }
  ): Promise<FileUpload> => {
    const formData = new FormData();
    formData.append("file", file);

    const params = new URLSearchParams();
    params.append("file_type", fileType);
    if (options?.projectId) {
      params.append("project_id", options.projectId);
    }
    if (options?.makePublic) {
      params.append("make_public", "true");
    }

    const response = await apiClient.post<FileUpload>(
      `/api/v1/storage/upload?${params.toString()}`,
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      }
    );
    return response.data;
  },

  listFiles: async (params?: {
    file_type?: FileType;
    project_id?: string;
    limit?: number;
    offset?: number;
  }): Promise<FileListResponse> => {
    const response = await apiClient.get<FileListResponse>(
      "/api/v1/storage/files",
      { params }
    );
    return response.data;
  },

  downloadFile: async (fileId: string): Promise<Blob> => {
    const response = await apiClient.get(
      `/api/v1/storage/files/${fileId}/download`,
      { responseType: "blob" }
    );
    return response.data;
  },

  getSignedUrl: async (
    fileId: string,
    expiresIn?: number
  ): Promise<SignedUrlResponse> => {
    const response = await apiClient.post<SignedUrlResponse>(
      `/api/v1/storage/files/${fileId}/signed-url`,
      null,
      { params: { expires_in: expiresIn } }
    );
    return response.data;
  },

  deleteFile: async (fileId: string): Promise<void> => {
    await apiClient.delete(`/api/v1/storage/files/${fileId}`);
  },
};
