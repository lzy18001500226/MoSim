import { create } from "zustand";
import { v4 as uuid } from "uuid";
import type { AiMessage } from "@/types/world";

interface AiState {
  messages: AiMessage[];
  isLoading: boolean;
  isOpen: boolean;

  addMessage: (role: "assistant" | "user", content: string) => void;
  setLoading: (loading: boolean) => void;
  toggleOpen: () => void;
  setOpen: (open: boolean) => void;
  clearMessages: () => void;
}

export const useAiStore = create<AiState>((set) => ({
  messages: [],
  isLoading: false,
  isOpen: false,

  addMessage: (role, content) =>
    set((state) => ({
      messages: [
        ...state.messages,
        { id: uuid(), role, content, timestamp: new Date().toISOString() },
      ],
    })),

  setLoading: (isLoading) => set({ isLoading }),
  toggleOpen: () => set((state) => ({ isOpen: !state.isOpen })),
  setOpen: (isOpen) => set({ isOpen }),
  clearMessages: () => set({ messages: [] }),
}));
