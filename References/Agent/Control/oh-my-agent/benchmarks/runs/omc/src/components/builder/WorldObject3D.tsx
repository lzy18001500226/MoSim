"use client";

import { useState } from "react";
import type { WorldObject } from "@/types/world";
import { useWorldStore } from "@/store/worldStore";
import type { ThreeEvent } from "@react-three/fiber";

interface Props {
  object: WorldObject;
  isSelected: boolean;
}

export function WorldObject3D({ object, isSelected }: Props) {
  const [hovered, setHovered] = useState(false);
  const selectObject = useWorldStore((s) => s.selectObject);
  const isPlaying = useWorldStore((s) => s.isPlaying);

  const handleClick = (e: ThreeEvent<MouseEvent>) => {
    e.stopPropagation();
    if (!isPlaying) {
      selectObject(object.id);
    }
  };

  const geometry = getGeometry(object.type);

  return (
    <mesh
      position={object.position}
      rotation={object.rotation}
      scale={object.scale}
      onClick={handleClick}
      onPointerOver={() => setHovered(true)}
      onPointerOut={() => setHovered(false)}
    >
      {geometry}
      <meshStandardMaterial
        color={hovered && !isPlaying ? "#ffffff" : object.color}
        emissive={isSelected ? "#4f46e5" : hovered ? "#6366f1" : "#000000"}
        emissiveIntensity={isSelected ? 0.3 : hovered ? 0.15 : 0}
      />
    </mesh>
  );
}

function getGeometry(type: string) {
  switch (type) {
    case "cube":
      return <boxGeometry args={[1, 1, 1]} />;
    case "sphere":
      return <sphereGeometry args={[0.5, 32, 32]} />;
    case "cylinder":
      return <cylinderGeometry args={[0.4, 0.4, 1.2, 32]} />;
    case "cone":
      return <coneGeometry args={[0.5, 1, 32]} />;
    case "tree":
      return <coneGeometry args={[0.6, 1.5, 8]} />;
    case "house":
      return <boxGeometry args={[1.2, 1, 1]} />;
    case "character":
      return <capsuleGeometry args={[0.3, 0.6, 8, 16]} />;
    case "animal":
      return <sphereGeometry args={[0.5, 16, 16]} />;
    case "flower":
      return <dodecahedronGeometry args={[0.4]} />;
    case "rock":
      return <dodecahedronGeometry args={[0.5, 0]} />;
    case "cloud":
      return <sphereGeometry args={[0.7, 16, 16]} />;
    case "star":
      return <octahedronGeometry args={[0.5]} />;
    default:
      return <boxGeometry args={[1, 1, 1]} />;
  }
}
