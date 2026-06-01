"use client";

import { useRef, useState } from "react";
import { useFrame } from "@react-three/fiber";
import type { Group } from "three";
import type { WorldObject } from "@/types/world";
import { useWorldStore } from "@/store/world-store";

function AnimatedWrapper({
  children,
  animated,
  animationType,
}: {
  children: React.ReactNode;
  animated?: boolean;
  animationType?: string;
}) {
  const ref = useRef<Group>(null);

  useFrame((state) => {
    if (!ref.current || !animated) return;
    const t = state.clock.elapsedTime;
    switch (animationType) {
      case "bounce":
        ref.current.position.y = Math.abs(Math.sin(t * 2)) * 0.5;
        break;
      case "spin":
        ref.current.rotation.y = t;
        break;
      case "float":
        ref.current.position.y = Math.sin(t) * 0.3;
        break;
      case "pulse":
        const s = 1 + Math.sin(t * 3) * 0.1;
        ref.current.scale.set(s, s, s);
        break;
    }
  });

  return <group ref={ref}>{children}</group>;
}

function ShapeGeometry({ shape, color }: { shape: string; color: string }) {
  switch (shape) {
    case "sphere":
      return (
        <mesh>
          <sphereGeometry args={[0.5, 32, 32]} />
          <meshStandardMaterial color={color} />
        </mesh>
      );
    case "cylinder":
      return (
        <mesh>
          <cylinderGeometry args={[0.3, 0.3, 1, 32]} />
          <meshStandardMaterial color={color} />
        </mesh>
      );
    case "cone":
      return (
        <mesh>
          <coneGeometry args={[0.5, 1, 32]} />
          <meshStandardMaterial color={color} />
        </mesh>
      );
    case "torus":
      return (
        <mesh>
          <torusGeometry args={[0.4, 0.15, 16, 32]} />
          <meshStandardMaterial color={color} />
        </mesh>
      );
    case "tree":
      return (
        <group>
          <mesh position={[0, 0.4, 0]}>
            <cylinderGeometry args={[0.1, 0.15, 0.8, 8]} />
            <meshStandardMaterial color="#8B5A2B" />
          </mesh>
          <mesh position={[0, 1.1, 0]}>
            <coneGeometry args={[0.6, 1.2, 8]} />
            <meshStandardMaterial color={color} />
          </mesh>
        </group>
      );
    case "house":
      return (
        <group>
          <mesh position={[0, 0.4, 0]}>
            <boxGeometry args={[1, 0.8, 0.8]} />
            <meshStandardMaterial color={color} />
          </mesh>
          <mesh position={[0, 1, 0]} rotation={[0, Math.PI / 4, 0]}>
            <coneGeometry args={[0.7, 0.5, 4]} />
            <meshStandardMaterial color="#C2410C" />
          </mesh>
        </group>
      );
    case "character":
      return (
        <group>
          <mesh position={[0, 0.4, 0]}>
            <capsuleGeometry args={[0.2, 0.4, 8, 16]} />
            <meshStandardMaterial color={color} />
          </mesh>
          <mesh position={[0, 0.95, 0]}>
            <sphereGeometry args={[0.22, 16, 16]} />
            <meshStandardMaterial color="#FFD4B8" />
          </mesh>
        </group>
      );
    case "rock":
      return (
        <mesh>
          <dodecahedronGeometry args={[0.4, 0]} />
          <meshStandardMaterial color={color} flatShading />
        </mesh>
      );
    case "flower":
      return (
        <group>
          <mesh position={[0, 0.3, 0]}>
            <cylinderGeometry args={[0.03, 0.03, 0.6, 8]} />
            <meshStandardMaterial color="#22C55E" />
          </mesh>
          <mesh position={[0, 0.65, 0]}>
            <sphereGeometry args={[0.2, 8, 8]} />
            <meshStandardMaterial color={color} />
          </mesh>
        </group>
      );
    case "cloud":
      return (
        <group>
          <mesh position={[0, 0, 0]}>
            <sphereGeometry args={[0.4, 16, 16]} />
            <meshStandardMaterial color={color} transparent opacity={0.9} />
          </mesh>
          <mesh position={[0.35, 0.05, 0]}>
            <sphereGeometry args={[0.3, 16, 16]} />
            <meshStandardMaterial color={color} transparent opacity={0.9} />
          </mesh>
          <mesh position={[-0.3, -0.05, 0]}>
            <sphereGeometry args={[0.3, 16, 16]} />
            <meshStandardMaterial color={color} transparent opacity={0.9} />
          </mesh>
        </group>
      );
    case "star":
      return (
        <mesh rotation={[Math.PI / 2, 0, 0]}>
          <torusGeometry args={[0.35, 0.08, 4, 5]} />
          <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.3} />
        </mesh>
      );
    default:
      return (
        <mesh>
          <boxGeometry args={[0.8, 0.8, 0.8]} />
          <meshStandardMaterial color={color} />
        </mesh>
      );
  }
}

interface SceneObjectProps {
  object: WorldObject;
  isSelected: boolean;
  isPlayMode?: boolean;
}

export default function SceneObject({ object, isSelected, isPlayMode }: SceneObjectProps) {
  const meshRef = useRef<Group>(null);
  const [hovered, setHovered] = useState(false);
  const selectObject = useWorldStore((s) => s.selectObject);

  return (
    <group
      position={object.position}
      rotation={object.rotation}
      scale={object.scale}
    >
      <AnimatedWrapper animated={object.animated} animationType={object.animationType}>
        <group
          ref={meshRef}
          onClick={(e) => {
            e.stopPropagation();
            if (!isPlayMode) selectObject(object.id);
          }}
          onPointerOver={(e) => {
            e.stopPropagation();
            setHovered(true);
            document.body.style.cursor = "pointer";
          }}
          onPointerOut={() => {
            setHovered(false);
            document.body.style.cursor = "auto";
          }}
        >
          <ShapeGeometry shape={object.shape} color={object.color} />
          {(isSelected || hovered) && !isPlayMode && (
            <mesh>
              <boxGeometry args={[1.4, 1.4, 1.4]} />
              <meshBasicMaterial
                color={isSelected ? "#3B82F6" : "#93C5FD"}
                wireframe
                transparent
                opacity={0.5}
              />
            </mesh>
          )}
        </group>
      </AnimatedWrapper>
    </group>
  );
}
