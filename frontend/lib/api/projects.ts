import { apiClient } from "./client";
import {
  Project,
  ProjectCreate,
  ProjectUpdate,
  ProjectListResponse,
  ProjectStatus,
} from "./types";

export const projectsApi = {
  create: async (data: ProjectCreate): Promise<Project> => {
    const response = await apiClient.post<Project>("/api/v1/projects", data);
    return response.data;
  },

  list: async (params?: {
    status?: ProjectStatus;
    page?: number;
    per_page?: number;
  }): Promise<ProjectListResponse> => {
    const response = await apiClient.get<ProjectListResponse>(
      "/api/v1/projects",
      { params }
    );
    return response.data;
  },

  get: async (projectId: string): Promise<Project> => {
    const response = await apiClient.get<Project>(
      `/api/v1/projects/${projectId}`
    );
    return response.data;
  },

  update: async (projectId: string, data: ProjectUpdate): Promise<Project> => {
    const response = await apiClient.patch<Project>(
      `/api/v1/projects/${projectId}`,
      data
    );
    return response.data;
  },

  delete: async (projectId: string): Promise<void> => {
    await apiClient.delete(`/api/v1/projects/${projectId}`);
  },

  scrapeContent: async (projectId: string): Promise<Project> => {
    const response = await apiClient.post<Project>(
      `/api/v1/projects/${projectId}/scrape`
    );
    return response.data;
  },

  generateScript: async (projectId: string): Promise<Project> => {
    const response = await apiClient.post<Project>(
      `/api/v1/projects/${projectId}/generate-script`
    );
    return response.data;
  },

  generateAudio: async (projectId: string): Promise<Project> => {
    const response = await apiClient.post<Project>(
      `/api/v1/projects/${projectId}/generate-audio`
    );
    return response.data;
  },

  generateVideo: async (projectId: string): Promise<Project> => {
    const response = await apiClient.post<Project>(
      `/api/v1/projects/${projectId}/generate-video`
    );
    return response.data;
  },

  generateFull: async (projectId: string): Promise<Project> => {
    const response = await apiClient.post<Project>(
      `/api/v1/projects/${projectId}/generate`
    );
    return response.data;
  },
};
