import { create } from 'zustand';
import { UserProfile } from '@/types';
import { loadUser, saveUser } from '@/lib/storage';
import { v4 as uuid } from 'uuid';

interface UserState {
  user: UserProfile | null;
  isLoaded: boolean;
  loadUserFromStorage: () => void;
  createUser: (name: string, avatar: string, grade: string) => void;
  addWorldToUser: (worldId: string) => void;
}

export const useUserStore = create<UserState>((set, get) => ({
  user: null,
  isLoaded: false,

  loadUserFromStorage: () => {
    const user = loadUser();
    set({ user, isLoaded: true });
  },

  createUser: (name, avatar, grade) => {
    const user: UserProfile = {
      id: uuid(),
      name,
      avatar,
      grade,
      worlds: [],
      createdAt: new Date().toISOString(),
    };
    saveUser(user);
    set({ user, isLoaded: true });
  },

  addWorldToUser: (worldId) => {
    const { user } = get();
    if (!user) return;
    if (user.worlds.includes(worldId)) return;
    const updated = { ...user, worlds: [...user.worlds, worldId] };
    saveUser(updated);
    set({ user: updated });
  },
}));
