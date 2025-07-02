import { create } from "zustand";

interface AppState {
  // System state
  isLoading: boolean;
  error: string | null;
  
  // YouTube integration state
  videos: any[];
  uploadProgress: { [key: string]: number };
  
  // Analytics state
  analytics: {
    views: number;
    subscribers: number;
    revenue: number;
    engagement: number;
  };
  
  // Actions
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setVideos: (videos: any[]) => void;
  updateUploadProgress: (id: string, progress: number) => void;
  setAnalytics: (analytics: any) => void;
}

export const useAppStore = create<AppState>((set) => ({
  // Initial state
  isLoading: false,
  error: null,
  videos: [],
  uploadProgress: {},
  analytics: {
    views: 0,
    subscribers: 0,
    revenue: 0,
    engagement: 0,
  },

  // Actions
  setLoading: (loading) => set({ isLoading: loading }),
  setError: (error) => set({ error }),
  setVideos: (videos) => set({ videos }),
  updateUploadProgress: (id, progress) =>
    set((state) => ({
      uploadProgress: { ...state.uploadProgress, [id]: progress },
    })),
  setAnalytics: (analytics) => set({ analytics }),
}));
