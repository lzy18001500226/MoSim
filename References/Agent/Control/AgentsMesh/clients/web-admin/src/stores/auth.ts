import { create } from "zustand";
import { persist } from "zustand/middleware";

export interface AdminUser {
  id: number;
  email: string;
  username: string;
  name: string | null;
  avatar_url: string | null;
  is_system_admin: boolean;
}

interface AuthState {
  token: string | null;
  refreshToken: string | null;
  user: AdminUser | null;
  isLoading: boolean;
  error: string | null;

  // Actions
  setAuth: (token: string, refreshToken: string, user: AdminUser) => void;
  setUser: (user: AdminUser) => void;
  logout: () => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      refreshToken: null,
      user: null,
      isLoading: false,
      error: null,

      setAuth: (token, refreshToken, user) =>
        set({ token, refreshToken, user, error: null }),

      setUser: (user) => set({ user }),

      logout: () =>
        set({ token: null, refreshToken: null, user: null, error: null }),

      setLoading: (isLoading) => set({ isLoading }),

      setError: (error) => set({ error }),
    }),
    {
      name: "admin-auth-storage",
      partialize: (state) => ({
        token: state.token,
        refreshToken: state.refreshToken,
        user: state.user,
      }),
    }
  )
);

// Helper to get token for API calls
export function getAuthToken(): string | null {
  return useAuthStore.getState().token;
}
