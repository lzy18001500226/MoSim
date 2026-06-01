import { create } from "zustand";
import type { CompanionMessage } from "@/types/companion";

interface CompanionStore {
  messages: CompanionMessage[];
  suggestions: string[];
  isLoading: boolean;

  addMessage: (message: CompanionMessage) => void;
  setSuggestions: (suggestions: string[]) => void;
  setLoading: (loading: boolean) => void;
  clearConversation: () => void;
}

export const useCompanionStore = create<CompanionStore>((set) => ({
  messages: [],
  suggestions: [
    "What kind of world do you want to build?",
    "Who lives in this place?",
    "What happens here at night?",
  ],
  isLoading: false,

  addMessage: (message) =>
    set((state) => ({ messages: [...state.messages, message] })),

  setSuggestions: (suggestions) => set({ suggestions }),

  setLoading: (loading) => set({ isLoading: loading }),

  clearConversation: () =>
    set({
      messages: [],
      suggestions: [
        "What kind of world do you want to build?",
        "Who lives in this place?",
        "What happens here at night?",
      ],
    }),
}));
