"use client";

import { useRef } from "react";
import * as THREE from "three";
import type { WorldObject } from "@/types/world";

interface PlacedObjectProps {
  object: WorldObject;
  isSelected: boolean;
  onSelect: () => void;
}

function ShapeGeometry({ shape }: { shape: string }) {
  switch (shape) {
    case "sphere":
      return <sphereGeometry args={[0.5, 32, 32]} />;
    case "cylinder":
      return <cylinderGeometry args={[0.3, 0.3, 1, 32]} />;
    case "cone":
      return <coneGeometry args={[0.5, 1, 32]} />;
    case "torus":
      return <torusGeometry args={[0.4, 0.15, 16, 32]} />;
    case "tree":
      return <coneGeometry args={[0.5, 1.5, 8]} />;
    case "house":
      return <boxGeometry args={[1, 0.8, 1]} />;
    case "star":
      return <dodecahedronGeometry args={[0.5, 0]} />;
    default:
      return <boxGeometry args={[1, 1, 1]} />;
  }
}

export function PlacedObject({ object, isSelected, onSelect }: PlacedObjectProps) {
  const meshRef = useRef<THREE.Mesh>(null);

  return (
    <mesh
      ref={meshRef}
      position={[object.position.x, object.position.y, object.position.z]}
      rotation={[object.rotation.x, object.rotation.y, object.rotation.z]}
      scale={[object.scale.x, object.scale.y, object.scale.z]}
      onClick={(e) => {
        e.stopPropagation();
        onSelect();
      }}
      castShadow
    >
      <ShapeGeometry shape={object.shape} />
      <meshStandardMaterial
        color={object.color}
        emissive={isSelected ? "#ffffff" : "#000000"}
        emissiveIntensity={isSelected ? 0.1 : 0}
      />
      {isSelected && (
        <lineSegments>
          <edgesGeometry args={[meshRef.current?.geometry]} />
          <lineBasicMaterial color="#6C63FF" linewidth={2} />
        </lineSegments>
      )}
    </mesh>
  );
}
