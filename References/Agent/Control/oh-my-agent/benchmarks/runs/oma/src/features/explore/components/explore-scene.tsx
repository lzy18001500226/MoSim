"use client";

import { OrbitControls, Sky, Grid } from "@react-three/drei";
import { CanvasWrapper } from "@/components/three/canvas-wrapper";
import { PlacedObject } from "@/features/builder/components/placed-object";
import type { WorldState } from "@/types/world";

interface ExploreSceneProps {
  worldState: WorldState;
}

function Scene({ worldState }: ExploreSceneProps) {
  return (
    <>
      <ambientLight intensity={0.6} />
      <directionalLight position={[10, 10, 5]} intensity={1} castShadow />
      <Sky sunPosition={[100, 20, 100]} turbidity={8} rayleigh={2} />
      <Grid
        infiniteGrid
        fadeDistance={30}
        fadeStrength={5}
        cellSize={1}
        cellColor="#ddd"
        sectionSize={5}
        sectionColor="#aaa"
      />
      <mesh
        rotation={[-Math.PI / 2, 0, 0]}
        position={[0, -0.01, 0]}
        receiveShadow
      >
        <planeGeometry args={[50, 50]} />
        <meshStandardMaterial
          color={worldState.environment.groundColor}
          transparent
          opacity={0.3}
        />
      </mesh>
      {worldState.objects.map((obj) => (
        <PlacedObject
          key={obj.id}
          object={obj}
          isSelected={false}
          onSelect={() => {}}
        />
      ))}
      <OrbitControls
        makeDefault
        autoRotate
        autoRotateSpeed={0.5}
        maxPolarAngle={Math.PI / 2.1}
        minDistance={3}
        maxDistance={30}
      />
    </>
  );
}

export function ExploreScene({ worldState }: ExploreSceneProps) {
  return (
    <CanvasWrapper className="w-full h-full">
      <Scene worldState={worldState} />
    </CanvasWrapper>
  );
}
