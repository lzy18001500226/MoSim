'use client';

import { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import { Outlines } from '@react-three/drei';
import * as THREE from 'three';
import { ObjectType, AnimationType } from '@/types';

interface WorldObject3DProps {
  id: string;
  type: ObjectType;
  position: [number, number, number];
  rotation: [number, number, number];
  scale: [number, number, number];
  color: string;
  animation?: AnimationType;
  isSelected: boolean;
  onClick: () => void;
}

function SelectionOutline({ visible }: { visible: boolean }) {
  if (!visible) return null;
  return <Outlines thickness={3} color="#facc15" screenspace />;
}

// ---------------------------------------------------------------------------
// Individual shape components
// ---------------------------------------------------------------------------

function CubeShape({ color, isSelected }: { color: string; isSelected: boolean }) {
  return (
    <mesh>
      <boxGeometry args={[1, 1, 1]} />
      <meshStandardMaterial color={color} />
      <SelectionOutline visible={isSelected} />
    </mesh>
  );
}

function SphereShape({ color, isSelected }: { color: string; isSelected: boolean }) {
  return (
    <mesh>
      <sphereGeometry args={[0.5, 32, 32]} />
      <meshStandardMaterial color={color} />
      <SelectionOutline visible={isSelected} />
    </mesh>
  );
}

function CylinderShape({ color, isSelected }: { color: string; isSelected: boolean }) {
  return (
    <mesh>
      <cylinderGeometry args={[0.5, 0.5, 1, 32]} />
      <meshStandardMaterial color={color} />
      <SelectionOutline visible={isSelected} />
    </mesh>
  );
}

function ConeShape({ color, isSelected }: { color: string; isSelected: boolean }) {
  return (
    <mesh>
      <coneGeometry args={[0.5, 1, 32]} />
      <meshStandardMaterial color={color} />
      <SelectionOutline visible={isSelected} />
    </mesh>
  );
}

function TreeShape({ isSelected }: { isSelected: boolean }) {
  return (
    <group>
      {/* Trunk */}
      <mesh position={[0, 0.3, 0]}>
        <cylinderGeometry args={[0.12, 0.15, 0.6, 12]} />
        <meshStandardMaterial color="#8B4513" />
      </mesh>
      {/* Foliage */}
      <mesh position={[0, 0.9, 0]}>
        <coneGeometry args={[0.5, 0.9, 12]} />
        <meshStandardMaterial color="#228B22" />
        <SelectionOutline visible={isSelected} />
      </mesh>
    </group>
  );
}

function HouseShape({ color, isSelected }: { color: string; isSelected: boolean }) {
  return (
    <group>
      {/* Body */}
      <mesh position={[0, 0.35, 0]}>
        <boxGeometry args={[0.8, 0.7, 0.8]} />
        <meshStandardMaterial color={color} />
      </mesh>
      {/* Roof */}
      <mesh position={[0, 0.9, 0]} rotation={[0, Math.PI / 4, 0]}>
        <coneGeometry args={[0.65, 0.5, 4]} />
        <meshStandardMaterial color="#A0522D" />
        <SelectionOutline visible={isSelected} />
      </mesh>
    </group>
  );
}

function FlowerShape({ color, isSelected }: { color: string; isSelected: boolean }) {
  return (
    <group>
      {/* Stem */}
      <mesh position={[0, 0.2, 0]}>
        <cylinderGeometry args={[0.03, 0.03, 0.4, 8]} />
        <meshStandardMaterial color="#2E8B57" />
      </mesh>
      {/* Blossom */}
      <mesh position={[0, 0.45, 0]}>
        <sphereGeometry args={[0.12, 16, 16]} />
        <meshStandardMaterial color={color} />
        <SelectionOutline visible={isSelected} />
      </mesh>
    </group>
  );
}

function RockShape({ color, isSelected }: { color: string; isSelected: boolean }) {
  return (
    <mesh>
      <icosahedronGeometry args={[0.4, 0]} />
      <meshStandardMaterial color={color} flatShading />
      <SelectionOutline visible={isSelected} />
    </mesh>
  );
}

function MushroomShape({ color, isSelected }: { color: string; isSelected: boolean }) {
  return (
    <group>
      {/* Stem */}
      <mesh position={[0, 0.15, 0]}>
        <cylinderGeometry args={[0.08, 0.1, 0.3, 12]} />
        <meshStandardMaterial color="#F5F5DC" />
      </mesh>
      {/* Cap */}
      <mesh position={[0, 0.35, 0]}>
        <sphereGeometry args={[0.25, 24, 24, 0, Math.PI * 2, 0, Math.PI / 2]} />
        <meshStandardMaterial color={color} />
        <SelectionOutline visible={isSelected} />
      </mesh>
    </group>
  );
}

function StarShape({ isSelected }: { isSelected: boolean }) {
  return (
    <mesh>
      <dodecahedronGeometry args={[0.4, 0]} />
      <meshStandardMaterial color="#FFD700" />
      <SelectionOutline visible={isSelected} />
    </mesh>
  );
}

function CloudShape({ isSelected }: { isSelected: boolean }) {
  return (
    <group>
      <mesh position={[-0.3, 0, 0]}>
        <sphereGeometry args={[0.25, 16, 16]} />
        <meshStandardMaterial color="#f0f0f0" />
      </mesh>
      <mesh position={[0, 0.1, 0]}>
        <sphereGeometry args={[0.35, 16, 16]} />
        <meshStandardMaterial color="#ffffff" />
        <SelectionOutline visible={isSelected} />
      </mesh>
      <mesh position={[0.3, 0, 0]}>
        <sphereGeometry args={[0.25, 16, 16]} />
        <meshStandardMaterial color="#f0f0f0" />
      </mesh>
    </group>
  );
}

function CatShape({ color, isSelected }: { color: string; isSelected: boolean }) {
  return (
    <group>
      {/* Body */}
      <mesh position={[0, 0.2, 0]}>
        <boxGeometry args={[0.5, 0.3, 0.3]} />
        <meshStandardMaterial color={color} />
      </mesh>
      {/* Head */}
      <mesh position={[0.3, 0.4, 0]}>
        <boxGeometry args={[0.25, 0.25, 0.25]} />
        <meshStandardMaterial color={color} />
        <SelectionOutline visible={isSelected} />
      </mesh>
      {/* Tail */}
      <mesh position={[-0.35, 0.3, 0]} rotation={[0, 0, Math.PI / 4]}>
        <cylinderGeometry args={[0.02, 0.02, 0.3, 8]} />
        <meshStandardMaterial color={color} />
      </mesh>
    </group>
  );
}

function DogShape({ color, isSelected }: { color: string; isSelected: boolean }) {
  return (
    <group>
      {/* Body */}
      <mesh position={[0, 0.22, 0]}>
        <boxGeometry args={[0.6, 0.35, 0.35]} />
        <meshStandardMaterial color={color} />
      </mesh>
      {/* Head */}
      <mesh position={[0.35, 0.42, 0]}>
        <boxGeometry args={[0.3, 0.28, 0.28]} />
        <meshStandardMaterial color={color} />
        <SelectionOutline visible={isSelected} />
      </mesh>
      {/* Snout */}
      <mesh position={[0.52, 0.38, 0]}>
        <boxGeometry args={[0.1, 0.1, 0.12]} />
        <meshStandardMaterial color={color} />
      </mesh>
    </group>
  );
}

function BirdShape({ color, isSelected }: { color: string; isSelected: boolean }) {
  return (
    <group>
      {/* Body */}
      <mesh>
        <sphereGeometry args={[0.2, 16, 16]} />
        <meshStandardMaterial color={color} />
        <SelectionOutline visible={isSelected} />
      </mesh>
      {/* Beak */}
      <mesh position={[0.25, 0.02, 0]} rotation={[0, 0, -Math.PI / 2]}>
        <coneGeometry args={[0.05, 0.15, 8]} />
        <meshStandardMaterial color="#FFA500" />
      </mesh>
    </group>
  );
}

function FishShape({ color, isSelected }: { color: string; isSelected: boolean }) {
  return (
    <group>
      {/* Body */}
      <mesh scale={[1.6, 0.8, 0.8]}>
        <sphereGeometry args={[0.2, 16, 16]} />
        <meshStandardMaterial color={color} />
        <SelectionOutline visible={isSelected} />
      </mesh>
      {/* Tail fin */}
      <mesh position={[-0.35, 0, 0]} rotation={[0, 0, Math.PI / 2]}>
        <coneGeometry args={[0.12, 0.15, 4]} />
        <meshStandardMaterial color={color} />
      </mesh>
    </group>
  );
}

function KidShape({ color, isSelected }: { color: string; isSelected: boolean }) {
  return (
    <group>
      {/* Body */}
      <mesh position={[0, 0.3, 0]}>
        <cylinderGeometry args={[0.15, 0.18, 0.5, 12]} />
        <meshStandardMaterial color={color} />
      </mesh>
      {/* Head */}
      <mesh position={[0, 0.7, 0]}>
        <sphereGeometry args={[0.18, 16, 16]} />
        <meshStandardMaterial color="#FFDAB9" />
        <SelectionOutline visible={isSelected} />
      </mesh>
    </group>
  );
}

function RobotShape({ color, isSelected }: { color: string; isSelected: boolean }) {
  return (
    <group>
      {/* Body */}
      <mesh position={[0, 0.3, 0]}>
        <boxGeometry args={[0.4, 0.5, 0.3]} />
        <meshStandardMaterial color={color} metalness={0.7} roughness={0.3} />
      </mesh>
      {/* Head */}
      <mesh position={[0, 0.7, 0]}>
        <boxGeometry args={[0.3, 0.25, 0.25]} />
        <meshStandardMaterial color={color} metalness={0.7} roughness={0.3} />
        <SelectionOutline visible={isSelected} />
      </mesh>
      {/* Antenna */}
      <mesh position={[0, 0.88, 0]}>
        <cylinderGeometry args={[0.02, 0.02, 0.1, 6]} />
        <meshStandardMaterial color="#C0C0C0" metalness={0.9} roughness={0.1} />
      </mesh>
    </group>
  );
}

function FenceShape({ color, isSelected }: { color: string; isSelected: boolean }) {
  return (
    <mesh>
      <boxGeometry args={[2, 0.5, 0.08]} />
      <meshStandardMaterial color={color} />
      <SelectionOutline visible={isSelected} />
    </mesh>
  );
}

function BridgeShape({ color, isSelected }: { color: string; isSelected: boolean }) {
  return (
    <mesh>
      <boxGeometry args={[1.5, 0.1, 0.8]} />
      <meshStandardMaterial color={color} />
      <SelectionOutline visible={isSelected} />
    </mesh>
  );
}

function LampShape({ isSelected }: { isSelected: boolean }) {
  return (
    <group>
      {/* Post */}
      <mesh position={[0, 0.4, 0]}>
        <cylinderGeometry args={[0.04, 0.06, 0.8, 8]} />
        <meshStandardMaterial color="#555555" metalness={0.6} roughness={0.4} />
      </mesh>
      {/* Light bulb */}
      <mesh position={[0, 0.85, 0]}>
        <sphereGeometry args={[0.12, 16, 16]} />
        <meshStandardMaterial
          color="#FFFACD"
          emissive="#FFFACD"
          emissiveIntensity={0.8}
        />
        <SelectionOutline visible={isSelected} />
      </mesh>
    </group>
  );
}

// ---------------------------------------------------------------------------
// Shape renderer lookup
// ---------------------------------------------------------------------------

function ObjectShape({
  type,
  color,
  isSelected,
}: {
  type: ObjectType;
  color: string;
  isSelected: boolean;
}) {
  switch (type) {
    case 'cube':
      return <CubeShape color={color} isSelected={isSelected} />;
    case 'sphere':
      return <SphereShape color={color} isSelected={isSelected} />;
    case 'cylinder':
      return <CylinderShape color={color} isSelected={isSelected} />;
    case 'cone':
      return <ConeShape color={color} isSelected={isSelected} />;
    case 'tree':
      return <TreeShape isSelected={isSelected} />;
    case 'house':
      return <HouseShape color={color} isSelected={isSelected} />;
    case 'flower':
      return <FlowerShape color={color} isSelected={isSelected} />;
    case 'rock':
      return <RockShape color={color} isSelected={isSelected} />;
    case 'mushroom':
      return <MushroomShape color={color} isSelected={isSelected} />;
    case 'star':
      return <StarShape isSelected={isSelected} />;
    case 'cloud':
      return <CloudShape isSelected={isSelected} />;
    case 'animal_cat':
      return <CatShape color={color} isSelected={isSelected} />;
    case 'animal_dog':
      return <DogShape color={color} isSelected={isSelected} />;
    case 'animal_bird':
      return <BirdShape color={color} isSelected={isSelected} />;
    case 'animal_fish':
      return <FishShape color={color} isSelected={isSelected} />;
    case 'character_kid':
      return <KidShape color={color} isSelected={isSelected} />;
    case 'character_robot':
      return <RobotShape color={color} isSelected={isSelected} />;
    case 'fence':
      return <FenceShape color={color} isSelected={isSelected} />;
    case 'bridge':
      return <BridgeShape color={color} isSelected={isSelected} />;
    case 'lamp':
      return <LampShape isSelected={isSelected} />;
    default:
      return <CubeShape color={color} isSelected={isSelected} />;
  }
}

// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------

export default function WorldObject3D({
  id,
  type,
  position,
  rotation,
  scale,
  color,
  animation,
  isSelected,
  onClick,
}: WorldObject3DProps) {
  const groupRef = useRef<THREE.Group>(null);
  const basePosition = useRef(position);
  const baseScale = useRef(scale);

  useFrame((_, delta) => {
    const group = groupRef.current;
    if (!group || !animation || animation === 'none') return;

    const time = performance.now() / 1000;

    switch (animation) {
      case 'bounce':
        group.position.y =
          basePosition.current[1] + Math.sin(time * 4) * 0.15;
        break;

      case 'spin':
        group.rotation.y += delta * 1.5;
        break;

      case 'float':
        group.position.y =
          basePosition.current[1] + Math.sin(time * 1.5) * 0.08;
        break;

      case 'pulse': {
        const s = 1 + Math.sin(time * 3) * 0.1;
        group.scale.set(
          baseScale.current[0] * s,
          baseScale.current[1] * s,
          baseScale.current[2] * s,
        );
        break;
      }
    }
  });

  return (
    <group
      ref={groupRef}
      position={position}
      rotation={rotation}
      scale={scale}
      onClick={(e) => {
        e.stopPropagation();
        onClick();
      }}
      userData={{ id }}
    >
      <ObjectShape type={type} color={color} isSelected={isSelected} />
    </group>
  );
}
