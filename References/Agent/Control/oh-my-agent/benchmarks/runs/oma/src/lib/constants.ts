export const SITE_NAME = "Imagine Worlds";

export const AVATAR_OPTIONS = [
  { id: "star", label: "Star", emoji: "⭐" },
  { id: "rocket", label: "Rocket", emoji: "🚀" },
  { id: "flower", label: "Flower", emoji: "🌸" },
  { id: "fish", label: "Fish", emoji: "🐟" },
  { id: "bird", label: "Bird", emoji: "🐦" },
  { id: "cat", label: "Cat", emoji: "🐱" },
] as const;

export const ENVIRONMENT_THEMES = [
  { id: "meadow", label: "Sunny Meadow", skyColor: "#87CEEB", groundColor: "#7CCD7C" },
  { id: "desert", label: "Sandy Desert", skyColor: "#F4A460", groundColor: "#DEB887" },
  { id: "ocean", label: "Deep Ocean", skyColor: "#1a5276", groundColor: "#2E86C1" },
  { id: "space", label: "Outer Space", skyColor: "#0a0a2a", groundColor: "#2d2d5e" },
  { id: "forest", label: "Magic Forest", skyColor: "#355E3B", groundColor: "#228B22" },
  { id: "snow", label: "Snowy Land", skyColor: "#B0C4DE", groundColor: "#FFFAFA" },
] as const;

export const OBJECT_CATALOG = [
  { id: "cube", label: "Box", shape: "box", defaultColor: "#FF6B6B" },
  { id: "sphere", label: "Ball", shape: "sphere", defaultColor: "#4ECDC4" },
  { id: "cylinder", label: "Tube", shape: "cylinder", defaultColor: "#45B7D1" },
  { id: "cone", label: "Cone", shape: "cone", defaultColor: "#96CEB4" },
  { id: "torus", label: "Ring", shape: "torus", defaultColor: "#FFEAA7" },
  { id: "tree", label: "Tree", shape: "tree", defaultColor: "#27AE60" },
  { id: "house", label: "House", shape: "house", defaultColor: "#E74C3C" },
  { id: "star", label: "Star", shape: "star", defaultColor: "#F39C12" },
] as const;

export const COLOR_PALETTE = [
  "#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7",
  "#DDA0DD", "#FF8C69", "#98D8C8", "#F7DC6F", "#BB8FCE",
  "#85C1E9", "#82E0AA", "#F1948A", "#AED6F1", "#FAD7A0",
  "#FFFFFF", "#2C3E50", "#E74C3C", "#3498DB", "#27AE60",
];
