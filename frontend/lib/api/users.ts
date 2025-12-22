import { apiClient } from "./client";
import { Profile, ProfileUpdate, ProfileStats } from "./types";

export const usersApi = {
  getProfile: async (): Promise<Profile> => {
    const response = await apiClient.get<Profile>("/api/v1/users/me/profile");
    return response.data;
  },

  updateProfile: async (data: ProfileUpdate): Promise<Profile> => {
    const response = await apiClient.patch<Profile>(
      "/api/v1/users/me/profile",
      data
    );
    return response.data;
  },

  uploadAvatar: async (file: File): Promise<Profile> => {
    const formData = new FormData();
    formData.append("file", file);
    const response = await apiClient.post<Profile>(
      "/api/v1/users/me/avatar",
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      }
    );
    return response.data;
  },

  getStats: async (): Promise<ProfileStats> => {
    const response = await apiClient.get<ProfileStats>("/api/v1/users/me/stats");
    return response.data;
  },

  getCredits: async (): Promise<{ credits_remaining: number }> => {
    const response = await apiClient.get<{ credits_remaining: number }>(
      "/api/v1/users/me/credits"
    );
    return response.data;
  },
};
