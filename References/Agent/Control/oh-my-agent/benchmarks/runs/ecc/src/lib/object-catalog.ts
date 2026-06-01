import type { ObjectCategory, WorldObject } from "@/types/world";

interface CatalogItem {
  name: string;
  shape: WorldObject["shape"];
  category: ObjectCategory;
  defaultColor: string;
  emoji: string;
}

export const OBJECT_CATALOG: CatalogItem[] = [
  { name: "Box", shape: "box", category: "building", defaultColor: "#f97316", emoji: "📦" },
  { name: "Ball", shape: "sphere", category: "nature", defaultColor: "#3b82f6", emoji: "⚽" },
  { name: "Pillar", shape: "cylinder", category: "building", defaultColor: "#8b5cf6", emoji: "🏛️" },
  { name: "Cone", shape: "cone", category: "nature", defaultColor: "#10b981", emoji: "🔺" },
  { name: "Donut", shape: "torus", category: "fantasy", defaultColor: "#ec4899", emoji: "🍩" },
  { name: "Tree", shape: "tree", category: "nature", defaultColor: "#22c55e", emoji: "🌳" },
  { name: "House", shape: "house", category: "building", defaultColor: "#eab308", emoji: "🏠" },
  { name: "Star", shape: "star", category: "fantasy", defaultColor: "#f59e0b", emoji: "⭐" },
  { name: "Cloud", shape: "cloud", category: "nature", defaultColor: "#e2e8f0", emoji: "☁️" },
  { name: "Rock", shape: "rock", category: "nature", defaultColor: "#6b7280", emoji: "🪨" },
];

export const COLOR_PALETTE = [
  "#ef4444", "#f97316", "#f59e0b", "#eab308",
  "#84cc16", "#22c55e", "#10b981", "#14b8a6",
  "#06b6d4", "#0ea5e9", "#3b82f6", "#6366f1",
  "#8b5cf6", "#a855f7", "#d946ef", "#ec4899",
  "#f43f5e", "#ffffff", "#6b7280", "#1f2937",
];

export const ENVIRONMENT_THEMES = [
  { id: "meadow" as const, name: "Meadow", emoji: "🌿", skyColor: "#87ceeb", groundColor: "#4ade80" },
  { id: "ocean" as const, name: "Ocean", emoji: "🌊", skyColor: "#0ea5e9", groundColor: "#0369a1" },
  { id: "space" as const, name: "Space", emoji: "🚀", skyColor: "#1e1b4b", groundColor: "#312e81" },
  { id: "forest" as const, name: "Forest", emoji: "🌲", skyColor: "#6ee7b7", groundColor: "#065f46" },
  { id: "desert" as const, name: "Desert", emoji: "🏜️", skyColor: "#fde68a", groundColor: "#d97706" },
  { id: "snow" as const, name: "Snow", emoji: "❄️", skyColor: "#dbeafe", groundColor: "#e2e8f0" },
  { id: "night" as const, name: "Night", emoji: "🌙", skyColor: "#1e1b4b", groundColor: "#1e293b" },
  { id: "candy" as const, name: "Candy", emoji: "🍬", skyColor: "#fce7f3", groundColor: "#f9a8d4" },
];
