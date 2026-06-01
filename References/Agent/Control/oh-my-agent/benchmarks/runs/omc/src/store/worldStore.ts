import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { World, WorldObject, EnvironmentTheme, AIMessage } from "@/types/world";

interface WorldState {
  currentWorld: World | null;
  savedWorlds: World[];
  selectedObjectId: string | null;
  isPlaying: boolean;
  aiMessages: AIMessage[];
  undoStack: World[];
  redoStack: World[];

  createWorld: (name: string, environment: EnvironmentTheme) => void;
  addObject: (object: WorldObject) => void;
  updateObject: (id: string, updates: Partial<WorldObject>) => void;
  removeObject: (id: string) => void;
  selectObject: (id: string | null) => void;
  setEnvironment: (theme: EnvironmentTheme) => void;
  setPlaying: (playing: boolean) => void;
  saveWorld: () => void;
  loadWorld: (id: string) => void;
  deleteWorld: (id: string) => void;
  addAIMessage: (message: AIMessage) => void;
  undo: () => void;
  redo: () => void;
  pushUndo: () => void;
}

export const useWorldStore = create<WorldState>()(
  persist(
    (set, get) => ({
      currentWorld: null,
      savedWorlds: [],
      selectedObjectId: null,
      isPlaying: false,
      aiMessages: [],
      undoStack: [],
      redoStack: [],

      createWorld: (name, environment) => {
        const world: World = {
          id: crypto.randomUUID(),
          name,
          description: "",
          objects: [],
          environment,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        };
        set({ currentWorld: world, aiMessages: [], undoStack: [], redoStack: [] });
      },

      addObject: (object) => {
        const { currentWorld } = get();
        if (!currentWorld) return;
        get().pushUndo();
        set({
          currentWorld: {
            ...currentWorld,
            objects: [...currentWorld.objects, object],
            updatedAt: new Date().toISOString(),
          },
          redoStack: [],
        });
      },

      updateObject: (id, updates) => {
        const { currentWorld } = get();
        if (!currentWorld) return;
        get().pushUndo();
        set({
          currentWorld: {
            ...currentWorld,
            objects: currentWorld.objects.map((obj) =>
              obj.id === id ? { ...obj, ...updates } : obj
            ),
            updatedAt: new Date().toISOString(),
          },
          redoStack: [],
        });
      },

      removeObject: (id) => {
        const { currentWorld } = get();
        if (!currentWorld) return;
        get().pushUndo();
        set({
          currentWorld: {
            ...currentWorld,
            objects: currentWorld.objects.filter((obj) => obj.id !== id),
            updatedAt: new Date().toISOString(),
          },
          selectedObjectId: null,
          redoStack: [],
        });
      },

      selectObject: (id) => set({ selectedObjectId: id }),

      setEnvironment: (theme) => {
        const { currentWorld } = get();
        if (!currentWorld) return;
        get().pushUndo();
        set({
          currentWorld: { ...currentWorld, environment: theme },
          redoStack: [],
        });
      },

      setPlaying: (playing) => set({ isPlaying: playing }),

      saveWorld: () => {
        const { currentWorld, savedWorlds } = get();
        if (!currentWorld) return;
        const existing = savedWorlds.findIndex((w) => w.id === currentWorld.id);
        const updated = { ...currentWorld, updatedAt: new Date().toISOString() };
        if (existing >= 0) {
          const worlds = [...savedWorlds];
          worlds[existing] = updated;
          set({ savedWorlds: worlds, currentWorld: updated });
        } else {
          set({ savedWorlds: [...savedWorlds, updated], currentWorld: updated });
        }
      },

      loadWorld: (id) => {
        const world = get().savedWorlds.find((w) => w.id === id);
        if (world) set({ currentWorld: { ...world }, aiMessages: [], undoStack: [], redoStack: [] });
      },

      deleteWorld: (id) => {
        set({ savedWorlds: get().savedWorlds.filter((w) => w.id !== id) });
      },

      addAIMessage: (message) => {
        set({ aiMessages: [...get().aiMessages, message] });
      },

      undo: () => {
        const { undoStack, currentWorld } = get();
        if (undoStack.length === 0 || !currentWorld) return;
        const previous = undoStack[undoStack.length - 1];
        set({
          currentWorld: previous,
          undoStack: undoStack.slice(0, -1),
          redoStack: [...get().redoStack, currentWorld],
        });
      },

      redo: () => {
        const { redoStack, currentWorld } = get();
        if (redoStack.length === 0 || !currentWorld) return;
        const next = redoStack[redoStack.length - 1];
        set({
          currentWorld: next,
          redoStack: redoStack.slice(0, -1),
          undoStack: [...get().undoStack, currentWorld],
        });
      },

      pushUndo: () => {
        const { currentWorld, undoStack } = get();
        if (!currentWorld) return;
        const stack = [...undoStack, { ...currentWorld }];
        if (stack.length > 20) stack.shift();
        set({ undoStack: stack });
      },
    }),
    { name: "dreamworld-storage" }
  )
);
