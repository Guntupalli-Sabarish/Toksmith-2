import { create } from "zustand";
import { persist } from "zustand/middleware";
import { User, Profile, ProfileStats } from "@/lib/api/types";
import { authApi, usersApi, getErrorMessage } from "@/lib/api";

interface AuthState {
  user: User | null;
  profile: Profile | null;
  stats: ProfileStats | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  error: string | null;

  // Actions
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string, fullName?: string) => Promise<void>;
  logout: () => Promise<void>;
  fetchUser: () => Promise<void>;
  fetchProfile: () => Promise<void>;
  fetchStats: () => Promise<void>;
  clearError: () => void;
  setUser: (user: User | null) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      profile: null,
      stats: null,
      isLoading: false,
      isAuthenticated: false,
      error: null,

      login: async (email: string, password: string) => {
        set({ isLoading: true, error: null });
        try {
          const response = await authApi.login({ email, password });
          localStorage.setItem("access_token", response.access_token);
          localStorage.setItem("refresh_token", response.refresh_token);
          set({
            user: response.user,
            isAuthenticated: true,
            isLoading: false,
          });
          // Fetch full profile after login
          get().fetchProfile();
          get().fetchStats();
        } catch (error) {
          set({
            error: getErrorMessage(error),
            isLoading: false,
            isAuthenticated: false,
          });
          throw error;
        }
      },

      signup: async (email: string, password: string, fullName?: string) => {
        set({ isLoading: true, error: null });
        try {
          const response = await authApi.signup({
            email,
            password,
            full_name: fullName,
          });
          localStorage.setItem("access_token", response.access_token);
          localStorage.setItem("refresh_token", response.refresh_token);
          set({
            user: response.user,
            isAuthenticated: true,
            isLoading: false,
          });
        } catch (error) {
          set({
            error: getErrorMessage(error),
            isLoading: false,
            isAuthenticated: false,
          });
          throw error;
        }
      },

      logout: async () => {
        try {
          await authApi.logout();
        } catch {
          // Ignore logout errors
        } finally {
          localStorage.removeItem("access_token");
          localStorage.removeItem("refresh_token");
          set({
            user: null,
            profile: null,
            stats: null,
            isAuthenticated: false,
          });
        }
      },

      fetchUser: async () => {
        const token = localStorage.getItem("access_token");
        if (!token) {
          set({ isAuthenticated: false });
          return;
        }

        set({ isLoading: true });
        try {
          const user = await authApi.getMe();
          set({ user, isAuthenticated: true, isLoading: false });
        } catch {
          set({ isAuthenticated: false, isLoading: false });
          localStorage.removeItem("access_token");
          localStorage.removeItem("refresh_token");
        }
      },

      fetchProfile: async () => {
        try {
          const profile = await usersApi.getProfile();
          set({ profile });
        } catch (error) {
          console.error("Failed to fetch profile:", error);
        }
      },

      fetchStats: async () => {
        try {
          const stats = await usersApi.getStats();
          set({ stats });
        } catch (error) {
          console.error("Failed to fetch stats:", error);
        }
      },

      clearError: () => set({ error: null }),
      setUser: (user) => set({ user, isAuthenticated: !!user }),
    }),
    {
      name: "auth-storage",
      partialize: (state) => ({
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);
