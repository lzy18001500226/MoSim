import type { ObjectType } from "@/types/world";

export interface ObjectDefinition {
  type: ObjectType;
  label: string;
  icon: string;
  defaultColor: string;
  category: "shapes" | "nature" | "buildings" | "characters";
}

export const OBJECT_DEFINITIONS: ObjectDefinition[] = [
  { type: "cube", label: "Box", icon: "📦", defaultColor: "#ff6b6b", category: "shapes" },
  { type: "sphere", label: "Ball", icon: "🔮", defaultColor: "#4ecdc4", category: "shapes" },
  { type: "cylinder", label: "Pillar", icon: "🧱", defaultColor: "#ffe66d", category: "shapes" },
  { type: "cone", label: "Cone", icon: "🔺", defaultColor: "#a8e6cf", category: "shapes" },
  { type: "tree", label: "Tree", icon: "🌳", defaultColor: "#2d6a4f", category: "nature" },
  { type: "flower", label: "Flower", icon: "🌸", defaultColor: "#ff69b4", category: "nature" },
  { type: "rock", label: "Rock", icon: "🪨", defaultColor: "#7f8c8d", category: "nature" },
  { type: "cloud", label: "Cloud", icon: "☁️", defaultColor: "#ffffff", category: "nature" },
  { type: "star", label: "Star", icon: "⭐", defaultColor: "#ffd700", category: "nature" },
  { type: "house", label: "House", icon: "🏠", defaultColor: "#e17055", category: "buildings" },
  { type: "character", label: "Person", icon: "🧑", defaultColor: "#fdcb6e", category: "characters" },
  { type: "animal", label: "Animal", icon: "🐾", defaultColor: "#e8a87c", category: "characters" },
];

export const COLORS = [
  "#ff6b6b", "#ff9ff3", "#feca57", "#ff9f43",
  "#48dbfb", "#0abde3", "#1dd1a1", "#10ac84",
  "#5f27cd", "#341f97", "#54a0ff", "#2e86de",
  "#ee5a24", "#ffffff", "#636e72", "#2d3436",
];

export const ENVIRONMENT_THEMES = [
  { id: "meadow" as const, label: "Sunny Meadow", icon: "🌻", groundColor: "#90EE90", skyColor: "#87CEEB" },
  { id: "ocean" as const, label: "Ocean", icon: "🌊", groundColor: "#1e90ff", skyColor: "#4169e1" },
  { id: "space" as const, label: "Outer Space", icon: "🚀", groundColor: "#1a1a2e", skyColor: "#0f0f23" },
  { id: "desert" as const, label: "Desert", icon: "🏜️", groundColor: "#f4a460", skyColor: "#ffcc80" },
  { id: "forest" as const, label: "Deep Forest", icon: "🌲", groundColor: "#228b22", skyColor: "#556b2f" },
  { id: "snow" as const, label: "Snow World", icon: "❄️", groundColor: "#f0f8ff", skyColor: "#b0c4de" },
  { id: "candy" as const, label: "Candy Land", icon: "🍭", groundColor: "#ffb6c1", skyColor: "#ffd1dc" },
  { id: "underwater" as const, label: "Underwater", icon: "🐠", groundColor: "#006994", skyColor: "#004c6d" },
];
