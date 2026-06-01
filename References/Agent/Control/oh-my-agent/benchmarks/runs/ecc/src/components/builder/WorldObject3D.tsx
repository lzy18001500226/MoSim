"use client";

import { useRef } from "react";
import { useWorldStore } from "@/stores/world-store";
import type { WorldObject } from "@/types/world";
import { BoxGeometry, type Mesh } from "three";

interface WorldObject3DProps {
  object: WorldObject;
}

export function WorldObject3D({ object }: WorldObject3DProps) {
  const meshRef = useRef<Mesh>(null);
  const selectObject = useWorldStore((s) => s.selectObject);
  const selectedObjectId = useWorldStore((s) => s.selectedObjectId);
  const isSelected = selectedObjectId === object.id;

  const handleClick = (e: { stopPropagation: () => void }) => {
    e.stopPropagation();
    selectObject(object.id);
  };

  return (
    <mesh
      ref={meshRef}
      position={object.position}
      rotation={object.rotation}
      scale={object.scale}
      onClick={handleClick}
    >
      <ObjectGeometry shape={object.shape} />
      <meshStandardMaterial
        color={object.color}
        emissive={isSelected ? object.color : "#000000"}
        emissiveIntensity={isSelected ? 0.15 : 0}
      />
      {isSelected && (
        <lineSegments>
          <edgesGeometry args={[getGeometryForShape(object.shape)]} />
          <lineBasicMaterial color="#ffffff" linewidth={2} />
        </lineSegments>
      )}
    </mesh>
  );
}

function ObjectGeometry({ shape }: { shape: WorldObject["shape"] }) {
  switch (shape) {
    case "box":
      return <boxGeometry args={[1, 1, 1]} />;
    case "sphere":
      return <sphereGeometry args={[0.5, 32, 32]} />;
    case "cylinder":
      return <cylinderGeometry args={[0.3, 0.3, 1.5, 32]} />;
    case "cone":
      return <coneGeometry args={[0.5, 1, 32]} />;
    case "torus":
      return <torusGeometry args={[0.4, 0.15, 16, 32]} />;
    case "tree":
      return <coneGeometry args={[0.6, 1.5, 8]} />;
    case "house":
      return <boxGeometry args={[1.2, 1, 1]} />;
    case "star":
      return <octahedronGeometry args={[0.5]} />;
    case "cloud":
      return <sphereGeometry args={[0.6, 16, 16]} />;
    case "rock":
      return <dodecahedronGeometry args={[0.4]} />;
    default:
      return <boxGeometry args={[1, 1, 1]} />;
  }
}

function getGeometryForShape(_shape: string) {
  return new BoxGeometry(1.02, 1.02, 1.02);
}
