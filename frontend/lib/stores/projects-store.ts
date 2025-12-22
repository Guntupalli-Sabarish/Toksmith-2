import { create } from "zustand";
import { Project, ProjectCreate, ProjectUpdate, ProjectStatus } from "@/lib/api/types";
import { projectsApi, getErrorMessage } from "@/lib/api";

interface ProjectsState {
  projects: Project[];
  currentProject: Project | null;
  total: number;
  page: number;
  perPage: number;
  isLoading: boolean;
  isCreating: boolean;
  isGenerating: boolean;
  error: string | null;

  // Actions
  fetchProjects: (params?: {
    status?: ProjectStatus;
    page?: number;
    per_page?: number;
  }) => Promise<void>;
  fetchProject: (id: string) => Promise<void>;
  createProject: (data: ProjectCreate) => Promise<Project>;
  updateProject: (id: string, data: ProjectUpdate) => Promise<void>;
  deleteProject: (id: string) => Promise<void>;
  scrapeContent: (id: string) => Promise<void>;
  generateScript: (id: string) => Promise<void>;
  generateAudio: (id: string) => Promise<void>;
  generateVideo: (id: string) => Promise<void>;
  generateFull: (id: string) => Promise<void>;
  setCurrentProject: (project: Project | null) => void;
  clearError: () => void;
}

export const useProjectsStore = create<ProjectsState>()((set, get) => ({
  projects: [],
  currentProject: null,
  total: 0,
  page: 1,
  perPage: 20,
  isLoading: false,
  isCreating: false,
  isGenerating: false,
  error: null,

  fetchProjects: async (params) => {
    set({ isLoading: true, error: null });
    try {
      const response = await projectsApi.list(params);
      set({
        projects: response.projects,
        total: response.total,
        page: response.page,
        perPage: response.per_page,
        isLoading: false,
      });
    } catch (error) {
      set({ error: getErrorMessage(error), isLoading: false });
    }
  },

  fetchProject: async (id: string) => {
    set({ isLoading: true, error: null });
    try {
      const project = await projectsApi.get(id);
      set({ currentProject: project, isLoading: false });
    } catch (error) {
      set({ error: getErrorMessage(error), isLoading: false });
    }
  },

  createProject: async (data: ProjectCreate) => {
    set({ isCreating: true, error: null });
    try {
      const project = await projectsApi.create(data);
      set((state) => ({
        projects: [project, ...state.projects],
        isCreating: false,
      }));
      return project;
    } catch (error) {
      set({ error: getErrorMessage(error), isCreating: false });
      throw error;
    }
  },

  updateProject: async (id: string, data: ProjectUpdate) => {
    set({ isLoading: true, error: null });
    try {
      const updatedProject = await projectsApi.update(id, data);
      set((state) => ({
        projects: state.projects.map((p) =>
          p.id === id ? updatedProject : p
        ),
        currentProject:
          state.currentProject?.id === id
            ? updatedProject
            : state.currentProject,
        isLoading: false,
      }));
    } catch (error) {
      set({ error: getErrorMessage(error), isLoading: false });
      throw error;
    }
  },

  deleteProject: async (id: string) => {
    set({ isLoading: true, error: null });
    try {
      await projectsApi.delete(id);
      set((state) => ({
        projects: state.projects.filter((p) => p.id !== id),
        currentProject:
          state.currentProject?.id === id ? null : state.currentProject,
        total: state.total - 1,
        isLoading: false,
      }));
    } catch (error) {
      set({ error: getErrorMessage(error), isLoading: false });
      throw error;
    }
  },

  scrapeContent: async (id: string) => {
    set({ isGenerating: true, error: null });
    try {
      const project = await projectsApi.scrapeContent(id);
      set((state) => ({
        projects: state.projects.map((p) => (p.id === id ? project : p)),
        currentProject:
          state.currentProject?.id === id ? project : state.currentProject,
        isGenerating: false,
      }));
    } catch (error) {
      set({ error: getErrorMessage(error), isGenerating: false });
      throw error;
    }
  },

  generateScript: async (id: string) => {
    set({ isGenerating: true, error: null });
    try {
      const project = await projectsApi.generateScript(id);
      set((state) => ({
        projects: state.projects.map((p) => (p.id === id ? project : p)),
        currentProject:
          state.currentProject?.id === id ? project : state.currentProject,
        isGenerating: false,
      }));
    } catch (error) {
      set({ error: getErrorMessage(error), isGenerating: false });
      throw error;
    }
  },

  generateAudio: async (id: string) => {
    set({ isGenerating: true, error: null });
    try {
      const project = await projectsApi.generateAudio(id);
      set((state) => ({
        projects: state.projects.map((p) => (p.id === id ? project : p)),
        currentProject:
          state.currentProject?.id === id ? project : state.currentProject,
        isGenerating: false,
      }));
    } catch (error) {
      set({ error: getErrorMessage(error), isGenerating: false });
      throw error;
    }
  },

  generateVideo: async (id: string) => {
    set({ isGenerating: true, error: null });
    try {
      const project = await projectsApi.generateVideo(id);
      set((state) => ({
        projects: state.projects.map((p) => (p.id === id ? project : p)),
        currentProject:
          state.currentProject?.id === id ? project : state.currentProject,
        isGenerating: false,
      }));
    } catch (error) {
      set({ error: getErrorMessage(error), isGenerating: false });
      throw error;
    }
  },

  generateFull: async (id: string) => {
    set({ isGenerating: true, error: null });
    try {
      const project = await projectsApi.generateFull(id);
      set((state) => ({
        projects: state.projects.map((p) => (p.id === id ? project : p)),
        currentProject:
          state.currentProject?.id === id ? project : state.currentProject,
        isGenerating: false,
      }));
    } catch (error) {
      set({ error: getErrorMessage(error), isGenerating: false });
      throw error;
    }
  },

  setCurrentProject: (project) => set({ currentProject: project }),
  clearError: () => set({ error: null }),
}));
