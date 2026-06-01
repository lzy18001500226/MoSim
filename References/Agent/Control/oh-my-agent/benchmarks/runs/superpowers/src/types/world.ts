export type ObjectShape = "box" | "sphere" | "cylinder" | "cone" | "torus" | "tree" | "house" | "character" | "rock" | "flower" | "cloud" | "star";

export type EnvironmentTheme = "meadow" | "desert" | "ocean" | "space" | "forest" | "snow" | "candy" | "volcano";

export interface WorldObject {
  id: string;
  shape: ObjectShape;
  position: [number, number, number];
  rotation: [number, number, number];
  scale: [number, number, number];
  color: string;
  name: string;
  animated?: boolean;
  animationType?: "bounce" | "spin" | "float" | "pulse";
}

export interface World {
  id: string;
  name: string;
  description: string;
  theme: EnvironmentTheme;
  objects: WorldObject[];
  createdAt: string;
  updatedAt: string;
  thumbnail?: string;
  creatorName?: string;
}

export interface CreativeChallenge {
  id: string;
  title: string;
  description: string;
  prompts: string[];
  theme?: EnvironmentTheme;
  category: "storytelling" | "habitat" | "dream" | "book" | "emotion";
}

export interface AIMessage {
  id: string;
  role: "assistant" | "user";
  content: string;
  timestamp: string;
}
