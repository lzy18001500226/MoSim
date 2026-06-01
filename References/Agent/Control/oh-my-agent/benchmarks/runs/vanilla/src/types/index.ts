export interface WorldObject {
  id: string;
  type: ObjectType;
  name: string;
  position: [number, number, number];
  rotation: [number, number, number];
  scale: [number, number, number];
  color: string;
  animation?: AnimationType;
}

export type ObjectType =
  | 'cube'
  | 'sphere'
  | 'cylinder'
  | 'cone'
  | 'tree'
  | 'house'
  | 'flower'
  | 'rock'
  | 'mushroom'
  | 'star'
  | 'cloud'
  | 'animal_cat'
  | 'animal_dog'
  | 'animal_bird'
  | 'animal_fish'
  | 'character_kid'
  | 'character_robot'
  | 'fence'
  | 'bridge'
  | 'lamp';

export type AnimationType = 'none' | 'bounce' | 'spin' | 'float' | 'pulse';

export type EnvironmentTheme =
  | 'meadow'
  | 'night'
  | 'underwater'
  | 'space'
  | 'desert'
  | 'snow'
  | 'sunset'
  | 'candy';

export interface World {
  id: string;
  name: string;
  theme: EnvironmentTheme;
  objects: WorldObject[];
  createdBy: string;
  createdAt: string;
  updatedAt: string;
  thumbnail?: string;
}

export interface UserProfile {
  id: string;
  name: string;
  avatar: string;
  grade: string;
  worlds: string[];
  createdAt: string;
}

export interface Challenge {
  id: string;
  title: string;
  description: string;
  prompts: string[];
  theme?: EnvironmentTheme;
  category: 'storytelling' | 'habitat' | 'dream' | 'book' | 'emotion';
}

export interface AIMessage {
  id: string;
  role: 'ai' | 'child';
  content: string;
  timestamp: string;
  suggestions?: string[];
}

export interface TeacherPrompt {
  id: string;
  title: string;
  description: string;
  assignedTo: string[];
  createdAt: string;
}
