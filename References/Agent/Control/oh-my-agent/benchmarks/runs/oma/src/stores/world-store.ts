import { create } from "zustand";
import type { WorldObject, Environment, WorldState } from "@/types/world";

const DEFAULT_ENVIRONMENT: Environment = {
  theme: "meadow",
  skyColor: "#87CEEB",
  groundColor: "#7CCD7C",
};

interface WorldStore {
  objects: WorldObject[];
  environment: Environment;
  selectedObjectId: string | null;

  addObject: (obj: WorldObject) => void;
  removeObject: (id: string) => void;
  updateObject: (id: string, updates: Partial<WorldObject>) => void;
  selectObject: (id: string | null) => void;
  setEnvironment: (env: Environment) => void;
  resetWorld: () => void;
  loadWorld: (state: WorldState) => void;
  getWorldState: () => WorldState;
}

export const useWorldStore = create<WorldStore>((set, get) => ({
  objects: [],
  environment: DEFAULT_ENVIRONMENT,
  selectedObjectId: null,

  addObject: (obj) =>
    set((state) => ({ objects: [...state.objects, obj] })),

  removeObject: (id) =>
    set((state) => ({
      objects: state.objects.filter((o) => o.id !== id),
      selectedObjectId: state.selectedObjectId === id ? null : state.selectedObjectId,
    })),

  updateObject: (id, updates) =>
    set((state) => ({
      objects: state.objects.map((o) => (o.id === id ? { ...o, ...updates } : o)),
    })),

  selectObject: (id) => set({ selectedObjectId: id }),

  setEnvironment: (env) => set({ environment: env }),

  resetWorld: () =>
    set({
      objects: [],
      environment: DEFAULT_ENVIRONMENT,
      selectedObjectId: null,
    }),

  loadWorld: (state) =>
    set({
      objects: state.objects,
      environment: state.environment,
      selectedObjectId: null,
    }),

  getWorldState: () => ({
    objects: get().objects,
    environment: get().environment,
  }),
}));
