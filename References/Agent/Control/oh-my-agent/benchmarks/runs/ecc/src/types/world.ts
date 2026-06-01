export type Vec3 = [number, number, number];

export type ObjectCategory = "nature" | "building" | "character" | "vehicle" | "furniture" | "fantasy";

export type EnvironmentTheme = "meadow" | "ocean" | "space" | "forest" | "desert" | "snow" | "night" | "candy";

export interface WorldObject {
  id: string;
  name: string;
  category: ObjectCategory;
  shape: "box" | "sphere" | "cylinder" | "cone" | "torus" | "tree" | "house" | "star" | "cloud" | "rock";
  position: Vec3;
  rotation: Vec3;
  scale: Vec3;
  color: string;
}

export interface WorldProject {
  id: string;
  name: string;
  createdAt: string;
  updatedAt: string;
  theme: EnvironmentTheme;
  objects: WorldObject[];
  thumbnail?: string;
  creatorName?: string;
}

export interface AiMessage {
  id: string;
  role: "assistant" | "user";
  content: string;
  timestamp: string;
}
