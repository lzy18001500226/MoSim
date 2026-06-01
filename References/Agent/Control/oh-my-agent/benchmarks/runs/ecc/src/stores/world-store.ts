import { create } from "zustand";
import { v4 as uuid } from "uuid";
import type { WorldObject, WorldProject, EnvironmentTheme, Vec3 } from "@/types/world";

interface WorldState {
  project: WorldProject;
  selectedObjectId: string | null;
  mode: "build" | "play";

  setProjectName: (name: string) => void;
  setTheme: (theme: EnvironmentTheme) => void;
  addObject: (obj: Omit<WorldObject, "id">) => void;
  removeObject: (id: string) => void;
  updateObject: (id: string, updates: Partial<WorldObject>) => void;
  selectObject: (id: string | null) => void;
  setMode: (mode: "build" | "play") => void;
  loadProject: (project: WorldProject) => void;
  resetProject: () => void;
}

const createEmptyProject = (): WorldProject => ({
  id: uuid(),
  name: "My World",
  createdAt: new Date().toISOString(),
  updatedAt: new Date().toISOString(),
  theme: "meadow",
  objects: [],
});

export const useWorldStore = create<WorldState>((set) => ({
  project: createEmptyProject(),
  selectedObjectId: null,
  mode: "build",

  setProjectName: (name) =>
    set((state) => ({
      project: { ...state.project, name, updatedAt: new Date().toISOString() },
    })),

  setTheme: (theme) =>
    set((state) => ({
      project: { ...state.project, theme, updatedAt: new Date().toISOString() },
    })),

  addObject: (obj) =>
    set((state) => {
      const newObj: WorldObject = { ...obj, id: uuid() };
      return {
        project: {
          ...state.project,
          objects: [...state.project.objects, newObj],
          updatedAt: new Date().toISOString(),
        },
        selectedObjectId: newObj.id,
      };
    }),

  removeObject: (id) =>
    set((state) => ({
      project: {
        ...state.project,
        objects: state.project.objects.filter((o) => o.id !== id),
        updatedAt: new Date().toISOString(),
      },
      selectedObjectId: state.selectedObjectId === id ? null : state.selectedObjectId,
    })),

  updateObject: (id, updates) =>
    set((state) => ({
      project: {
        ...state.project,
        objects: state.project.objects.map((o) => (o.id === id ? { ...o, ...updates } : o)),
        updatedAt: new Date().toISOString(),
      },
    })),

  selectObject: (id) => set({ selectedObjectId: id }),

  setMode: (mode) => set({ mode }),

  loadProject: (project) => set({ project, selectedObjectId: null, mode: "build" }),

  resetProject: () => set({ project: createEmptyProject(), selectedObjectId: null, mode: "build" }),
}));
