export interface WorldObject {
  id: string;
  type: ObjectType;
  position: [number, number, number];
  rotation: [number, number, number];
  scale: [number, number, number];
  color: string;
  name: string;
}

export type ObjectType =
  | "cube"
  | "sphere"
  | "cylinder"
  | "cone"
  | "tree"
  | "house"
  | "character"
  | "animal"
  | "flower"
  | "rock"
  | "cloud"
  | "star";

export type EnvironmentTheme =
  | "meadow"
  | "ocean"
  | "space"
  | "desert"
  | "forest"
  | "snow"
  | "candy"
  | "underwater";

export interface World {
  id: string;
  name: string;
  description: string;
  objects: WorldObject[];
  environment: EnvironmentTheme;
  createdAt: string;
  updatedAt: string;
  thumbnail?: string;
}

export interface AIMessage {
  id: string;
  role: "ai" | "child";
  content: string;
  timestamp: string;
  suggestions?: string[];
}

export interface CreativeChallenge {
  id: string;
  title: string;
  description: string;
  prompts: string[];
  category: "storytelling" | "habitat" | "dream" | "book" | "emotion";
  icon: string;
}
