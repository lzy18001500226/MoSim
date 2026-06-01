"use client";

import { useCallback, useRef } from "react";
import { OrbitControls, Grid, Sky, TransformControls } from "@react-three/drei";
import { useThree } from "@react-three/fiber";
import * as THREE from "three";
import { CanvasWrapper } from "@/components/three/canvas-wrapper";
import { useWorldStore } from "@/stores/world-store";
import { PlacedObject } from "./placed-object";
import type { ObjectShape } from "@/types/world";

function Scene() {
  const objects = useWorldStore((s) => s.objects);
  const selectedObjectId = useWorldStore((s) => s.selectedObjectId);
  const selectObject = useWorldStore((s) => s.selectObject);
  const updateObject = useWorldStore((s) => s.updateObject);
  const environment = useWorldStore((s) => s.environment);

  const selectedObject = objects.find((o) => o.id === selectedObjectId);
  const transformRef = useRef<THREE.Object3D>(null);

  return (
    <>
      <ambientLight intensity={0.5} />
      <directionalLight position={[10, 10, 5]} intensity={1} castShadow />
      <Sky
        sunPosition={[100, 20, 100]}
        turbidity={8}
        rayleigh={2}
      />
      <Grid
        infiniteGrid
        fadeDistance={30}
        fadeStrength={5}
        cellSize={1}
        cellColor="#ddd"
        sectionSize={5}
        sectionColor="#aaa"
      />
      {/* Ground plane for raycasting */}
      <mesh
        rotation={[-Math.PI / 2, 0, 0]}
        position={[0, -0.01, 0]}
        receiveShadow
        onClick={(e) => {
          e.stopPropagation();
          selectObject(null);
        }}
      >
        <planeGeometry args={[50, 50]} />
        <meshStandardMaterial color={environment.groundColor} transparent opacity={0.3} />
      </mesh>

      {objects.map((obj) => (
        <PlacedObject
          key={obj.id}
          object={obj}
          isSelected={obj.id === selectedObjectId}
          onSelect={() => selectObject(obj.id)}
        />
      ))}

      {selectedObject && transformRef.current && (
        <TransformControls
          object={transformRef.current}
          mode="translate"
          onObjectChange={() => {
            if (transformRef.current) {
              const pos = transformRef.current.position;
              updateObject(selectedObject.id, {
                position: { x: pos.x, y: pos.y, z: pos.z },
              });
            }
          }}
        />
      )}

      <OrbitControls
        makeDefault
        maxPolarAngle={Math.PI / 2.1}
        minDistance={3}
        maxDistance={30}
      />
    </>
  );
}

interface SceneCanvasProps {
  onDrop: (shape: ObjectShape, x: number, y: number) => void;
}

export function SceneCanvas({ onDrop }: SceneCanvasProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      const shape = e.dataTransfer.getData("object-shape") as ObjectShape;
      if (!shape) return;

      const rect = containerRef.current?.getBoundingClientRect();
      if (!rect) return;

      const x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      const y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
      onDrop(shape, x, y);
    },
    [onDrop]
  );

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = "copy";
  }, []);

  return (
    <div
      ref={containerRef}
      className="flex-1 relative"
      onDrop={handleDrop}
      onDragOver={handleDragOver}
    >
      <CanvasWrapper className="w-full h-full">
        <Scene />
      </CanvasWrapper>
    </div>
  );
}
