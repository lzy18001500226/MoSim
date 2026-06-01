import { create } from "zustand";
import { persist } from "zustand/middleware";
import { v4 as uuidv4 } from "uuid";
import type { World, WorldObject, EnvironmentTheme, ObjectShape, AIMessage } from "@/types/world";

interface WorldState {
  currentWorld: World | null;
  savedWorlds: World[];
  selectedObjectId: string | null;
  aiMessages: AIMessage[];
  undoStack: World[];
  redoStack: World[];
  isPlaying: boolean;
  userName: string;
  hasOnboarded: boolean;

  setUserName: (name: string) => void;
  setOnboarded: () => void;
  createNewWorld: (name: string, theme: EnvironmentTheme) => void;
  loadWorld: (id: string) => void;
  saveCurrentWorld: () => void;
  deleteWorld: (id: string) => void;

  addObject: (shape: ObjectShape, position?: [number, number, number]) => void;
  removeObject: (id: string) => void;
  updateObject: (id: string, updates: Partial<WorldObject>) => void;
  selectObject: (id: string | null) => void;
  setTheme: (theme: EnvironmentTheme) => void;
  setWorldName: (name: string) => void;

  undo: () => void;
  redo: () => void;
  pushUndo: () => void;

  addAIMessage: (message: Omit<AIMessage, "id" | "timestamp">) => void;
  clearAIMessages: () => void;

  setPlaying: (playing: boolean) => void;
}

const SHAPE_NAMES: Record<ObjectShape, string> = {
  box: "Block",
  sphere: "Ball",
  cylinder: "Pillar",
  cone: "Cone",
  torus: "Ring",
  tree: "Tree",
  house: "House",
  character: "Person",
  rock: "Rock",
  flower: "Flower",
  cloud: "Cloud",
  star: "Star",
};

const DEFAULT_COLORS: Record<ObjectShape, string> = {
  box: "#FF6B6B",
  sphere: "#4ECDC4",
  cylinder: "#FFE66D",
  cone: "#FF8E53",
  torus: "#A78BFA",
  tree: "#4ADE80",
  house: "#F9A8D4",
  character: "#60A5FA",
  rock: "#9CA3AF",
  flower: "#F472B6",
  cloud: "#E0E7FF",
  star: "#FBBF24",
};

export const useWorldStore = create<WorldState>()(
  persist(
    (set, get) => ({
      currentWorld: null,
      savedWorlds: [],
      selectedObjectId: null,
      aiMessages: [],
      undoStack: [],
      redoStack: [],
      isPlaying: false,
      userName: "",
      hasOnboarded: false,

      setUserName: (name) => set({ userName: name }),
      setOnboarded: () => set({ hasOnboarded: true }),

      createNewWorld: (name, theme) => {
        const world: World = {
          id: uuidv4(),
          name,
          description: "",
          theme,
          objects: [],
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          creatorName: get().userName,
        };
        set({
          currentWorld: world,
          selectedObjectId: null,
          aiMessages: [],
          undoStack: [],
          redoStack: [],
        });
      },

      loadWorld: (id) => {
        const world = get().savedWorlds.find((w) => w.id === id);
        if (world) {
          set({
            currentWorld: { ...world },
            selectedObjectId: null,
            aiMessages: [],
            undoStack: [],
            redoStack: [],
          });
        }
      },

      saveCurrentWorld: () => {
        const { currentWorld, savedWorlds } = get();
        if (!currentWorld) return;
        const updated = { ...currentWorld, updatedAt: new Date().toISOString() };
        const existing = savedWorlds.findIndex((w) => w.id === updated.id);
        const newWorlds = [...savedWorlds];
        if (existing >= 0) {
          newWorlds[existing] = updated;
        } else {
          newWorlds.push(updated);
        }
        set({ currentWorld: updated, savedWorlds: newWorlds });
      },

      deleteWorld: (id) => {
        set((s) => ({ savedWorlds: s.savedWorlds.filter((w) => w.id !== id) }));
      },

      addObject: (shape, position) => {
        const { currentWorld } = get();
        if (!currentWorld) return;
        get().pushUndo();
        const obj: WorldObject = {
          id: uuidv4(),
          shape,
          position: position || [
            (Math.random() - 0.5) * 6,
            0.5,
            (Math.random() - 0.5) * 6,
          ],
          rotation: [0, 0, 0],
          scale: [1, 1, 1],
          color: DEFAULT_COLORS[shape],
          name: SHAPE_NAMES[shape],
        };
        set({
          currentWorld: {
            ...currentWorld,
            objects: [...currentWorld.objects, obj],
          },
          selectedObjectId: obj.id,
        });
      },

      removeObject: (id) => {
        const { currentWorld } = get();
        if (!currentWorld) return;
        get().pushUndo();
        set({
          currentWorld: {
            ...currentWorld,
            objects: currentWorld.objects.filter((o) => o.id !== id),
          },
          selectedObjectId: null,
        });
      },

      updateObject: (id, updates) => {
        const { currentWorld } = get();
        if (!currentWorld) return;
        set({
          currentWorld: {
            ...currentWorld,
            objects: currentWorld.objects.map((o) =>
              o.id === id ? { ...o, ...updates } : o
            ),
          },
        });
      },

      selectObject: (id) => set({ selectedObjectId: id }),

      setTheme: (theme) => {
        const { currentWorld } = get();
        if (!currentWorld) return;
        get().pushUndo();
        set({ currentWorld: { ...currentWorld, theme } });
      },

      setWorldName: (name) => {
        const { currentWorld } = get();
        if (!currentWorld) return;
        set({ currentWorld: { ...currentWorld, name } });
      },

      pushUndo: () => {
        const { currentWorld, undoStack } = get();
        if (!currentWorld) return;
        set({
          undoStack: [...undoStack.slice(-19), { ...currentWorld }],
          redoStack: [],
        });
      },

      undo: () => {
        const { undoStack, currentWorld } = get();
        if (undoStack.length === 0 || !currentWorld) return;
        const prev = undoStack[undoStack.length - 1];
        set({
          currentWorld: prev,
          undoStack: undoStack.slice(0, -1),
          redoStack: [...get().redoStack, { ...currentWorld }],
        });
      },

      redo: () => {
        const { redoStack, currentWorld } = get();
        if (redoStack.length === 0 || !currentWorld) return;
        const next = redoStack[redoStack.length - 1];
        set({
          currentWorld: next,
          redoStack: redoStack.slice(0, -1),
          undoStack: [...get().undoStack, { ...currentWorld }],
        });
      },

      addAIMessage: (message) => {
        set((s) => ({
          aiMessages: [
            ...s.aiMessages,
            { ...message, id: uuidv4(), timestamp: new Date().toISOString() },
          ],
        }));
      },

      clearAIMessages: () => set({ aiMessages: [] }),

      setPlaying: (playing) => set({ isPlaying: playing }),
    }),
    {
      name: "wonderworld-storage",
      partialize: (state) => ({
        savedWorlds: state.savedWorlds,
        userName: state.userName,
        hasOnboarded: state.hasOnboarded,
      }),
    }
  )
);
