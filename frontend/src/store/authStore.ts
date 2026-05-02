import { create } from "zustand";
import { persist } from "zustand/middleware";

interface AuthState {
  token: string | null;
  userName: string | null;
  login: (token: string, userName: string) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      userName: null,
      login: (token, userName) => set({ token, userName }),
      logout: () => set({ token: null, userName: null }),
    }),
    {
      name: "studypilot-auth", // Guarda la sesión en localStorage
    }
  )
);
