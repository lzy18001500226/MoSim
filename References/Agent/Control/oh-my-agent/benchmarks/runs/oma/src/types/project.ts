import type { WorldState } from "./world";

export interface Project {
  id: string;
  title: string;
  thumbnail: string | null;
  worldData: WorldState;
  childId: string;
  isSample: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface ProjectSummary {
  id: string;
  title: string;
  thumbnail: string | null;
  createdAt: string;
}
