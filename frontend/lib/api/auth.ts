import { apiClient } from "./client";
import {
  AuthResponse,
  UserSignUp,
  UserSignIn,
  User,
  MessageResponse,
} from "./types";

export const authApi = {
  signup: async (data: UserSignUp): Promise<AuthResponse> => {
    const response = await apiClient.post<AuthResponse>(
      "/api/v1/auth/signup",
      data
    );
    return response.data;
  },

  login: async (data: UserSignIn): Promise<AuthResponse> => {
    const response = await apiClient.post<AuthResponse>(
      "/api/v1/auth/login",
      data
    );
    return response.data;
  },

  logout: async (): Promise<MessageResponse> => {
    const response = await apiClient.post<MessageResponse>("/api/v1/auth/logout");
    return response.data;
  },

  refreshToken: async (refreshToken: string): Promise<AuthResponse> => {
    const response = await apiClient.post<AuthResponse>("/api/v1/auth/refresh", {
      refresh_token: refreshToken,
    });
    return response.data;
  },

  requestPasswordReset: async (email: string): Promise<MessageResponse> => {
    const response = await apiClient.post<MessageResponse>(
      "/api/v1/auth/password-reset",
      { email }
    );
    return response.data;
  },

  updatePassword: async (newPassword: string): Promise<MessageResponse> => {
    const response = await apiClient.post<MessageResponse>(
      "/api/v1/auth/password-update",
      { new_password: newPassword }
    );
    return response.data;
  },

  getMe: async (): Promise<User> => {
    const response = await apiClient.get<User>("/api/v1/auth/me");
    return response.data;
  },
};
