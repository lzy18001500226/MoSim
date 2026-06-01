import { World, UserProfile } from '@/types';

const WORLDS_KEY = 'dreamworld_worlds';
const USER_KEY = 'dreamworld_user';
const TEACHER_KEY = 'dreamworld_teacher_prompts';

export function saveWorld(world: World): void {
  const worlds = loadAllWorlds();
  const idx = worlds.findIndex((w) => w.id === world.id);
  if (idx >= 0) {
    worlds[idx] = world;
  } else {
    worlds.push(world);
  }
  if (typeof window !== 'undefined') {
    localStorage.setItem(WORLDS_KEY, JSON.stringify(worlds));
  }
}

export function loadWorld(id: string): World | null {
  const worlds = loadAllWorlds();
  return worlds.find((w) => w.id === id) ?? null;
}

export function loadAllWorlds(): World[] {
  if (typeof window === 'undefined') return [];
  const data = localStorage.getItem(WORLDS_KEY);
  if (!data) return [];
  try {
    return JSON.parse(data) as World[];
  } catch {
    return [];
  }
}

export function deleteWorld(id: string): void {
  const worlds = loadAllWorlds().filter((w) => w.id !== id);
  if (typeof window !== 'undefined') {
    localStorage.setItem(WORLDS_KEY, JSON.stringify(worlds));
  }
}

export function saveUser(user: UserProfile): void {
  if (typeof window !== 'undefined') {
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  }
}

export function loadUser(): UserProfile | null {
  if (typeof window === 'undefined') return null;
  const data = localStorage.getItem(USER_KEY);
  if (!data) return null;
  try {
    return JSON.parse(data) as UserProfile;
  } catch {
    return null;
  }
}

export function saveTeacherPrompts(prompts: { id: string; title: string; description: string }[]): void {
  if (typeof window !== 'undefined') {
    localStorage.setItem(TEACHER_KEY, JSON.stringify(prompts));
  }
}

export function loadTeacherPrompts(): { id: string; title: string; description: string }[] {
  if (typeof window === 'undefined') return [];
  const data = localStorage.getItem(TEACHER_KEY);
  if (!data) return [];
  try {
    return JSON.parse(data);
  } catch {
    return [];
  }
}
