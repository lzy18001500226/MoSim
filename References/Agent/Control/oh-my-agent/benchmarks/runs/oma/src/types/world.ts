export interface Position {
  x: number;
  y: number;
  z: number;
}

export interface Rotation {
  x: number;
  y: number;
  z: number;
}

export interface Scale {
  x: number;
  y: number;
  z: number;
}

export type ObjectShape =
  | "box"
  | "sphere"
  | "cylinder"
  | "cone"
  | "torus"
  | "tree"
  | "house"
  | "star";

export interface WorldObject {
  id: string;
  shape: ObjectShape;
  label: string;
  position: Position;
  rotation: Rotation;
  scale: Scale;
  color: string;
}

export interface Environment {
  theme: string;
  skyColor: string;
  groundColor: string;
}

export interface WorldState {
  objects: WorldObject[];
  environment: Environment;
}
