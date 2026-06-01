import { create } from 'zustand';
import { WorldObject, EnvironmentTheme, AIMessage, World } from '@/types';
import { v4 as uuid } from 'uuid';
import { getGreeting } from '@/lib/ai';

interface WorldState {
  worldId: string;
  worldName: string;
  theme: EnvironmentTheme;
  objects: WorldObject[];
  selectedObjectId: string | null;
  messages: AIMessage[];
  showAI: boolean;
  mode: 'build' | 'explore';
  undoStack: WorldObject[][];
  redoStack: WorldObject[][];

  setWorldId: (id: string) => void;
  setWorldName: (name: string) => void;
  setTheme: (theme: EnvironmentTheme) => void;
  addObject: (obj: Omit<WorldObject, 'id'>) => void;
  removeObject: (id: string) => void;
  updateObject: (id: string, updates: Partial<WorldObject>) => void;
  selectObject: (id: string | null) => void;
  addMessage: (msg: AIMessage) => void;
  toggleAI: () => void;
  setMode: (mode: 'build' | 'explore') => void;
  undo: () => void;
  redo: () => void;
  loadWorld: (world: World) => void;
  resetWorld: () => void;
  getWorld: () => World;
}

export const useWorldStore = create<WorldState>((set, get) => ({
  worldId: uuid(),
  worldName: 'My World',
  theme: 'meadow',
  objects: [],
  selectedObjectId: null,
  messages: [getGreeting()],
  showAI: true,
  mode: 'build',
  undoStack: [],
  redoStack: [],

  setWorldId: (id) => set({ worldId: id }),
  setWorldName: (name) => set({ worldName: name }),

  setTheme: (theme) => set({ theme }),

  addObject: (obj) => {
    const state = get();
    const newObj: WorldObject = { ...obj, id: uuid() };
    set({
      undoStack: [...state.undoStack, state.objects],
      redoStack: [],
      objects: [...state.objects, newObj],
    });
  },

  removeObject: (id) => {
    const state = get();
    set({
      undoStack: [...state.undoStack, state.objects],
      redoStack: [],
      objects: state.objects.filter((o) => o.id !== id),
      selectedObjectId: state.selectedObjectId === id ? null : state.selectedObjectId,
    });
  },

  updateObject: (id, updates) => {
    const state = get();
    set({
      undoStack: [...state.undoStack, state.objects],
      redoStack: [],
      objects: state.objects.map((o) => (o.id === id ? { ...o, ...updates } : o)),
    });
  },

  selectObject: (id) => set({ selectedObjectId: id }),

  addMessage: (msg) => set((s) => ({ messages: [...s.messages, msg] })),

  toggleAI: () => set((s) => ({ showAI: !s.showAI })),

  setMode: (mode) => set({ mode }),

  undo: () => {
    const state = get();
    if (state.undoStack.length === 0) return;
    const prev = state.undoStack[state.undoStack.length - 1];
    set({
      undoStack: state.undoStack.slice(0, -1),
      redoStack: [...state.redoStack, state.objects],
      objects: prev,
    });
  },

  redo: () => {
    const state = get();
    if (state.redoStack.length === 0) return;
    const next = state.redoStack[state.redoStack.length - 1];
    set({
      redoStack: state.redoStack.slice(0, -1),
      undoStack: [...state.undoStack, state.objects],
      objects: next,
    });
  },

  loadWorld: (world) =>
    set({
      worldId: world.id,
      worldName: world.name,
      theme: world.theme,
      objects: world.objects,
      selectedObjectId: null,
      mode: 'build',
    }),

  resetWorld: () =>
    set({
      worldId: uuid(),
      worldName: 'My World',
      theme: 'meadow',
      objects: [],
      selectedObjectId: null,
      messages: [getGreeting()],
      undoStack: [],
      redoStack: [],
      mode: 'build',
    }),

  getWorld: () => {
    const s = get();
    return {
      id: s.worldId,
      name: s.worldName,
      theme: s.theme,
      objects: s.objects,
      createdBy: '',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };
  },
}));
