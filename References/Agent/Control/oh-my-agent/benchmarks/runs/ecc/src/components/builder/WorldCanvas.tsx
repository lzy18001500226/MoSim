"use client";

import { Canvas } from "@react-three/fiber";
import { OrbitControls, TransformControls } from "@react-three/drei";
import { useWorldStore } from "@/stores/world-store";
import { EnvironmentLayer } from "./EnvironmentLayer";
import { WorldObject3D } from "./WorldObject3D";
import { useRef } from "react";
import type { Mesh } from "three";
import type { WorldObject } from "@/types/world";

export function WorldCanvas() {
  const objects = useWorldStore((s) => s.project.objects);
  const selectedObjectId = useWorldStore((s) => s.selectedObjectId);
  const updateObject = useWorldStore((s) => s.updateObject);
  const selectObject = useWorldStore((s) => s.selectObject);
  const mode = useWorldStore((s) => s.mode);
  const addObject = useWorldStore((s) => s.addObject);

  const selectedObject = objects.find((o) => o.id === selectedObjectId);

  const handleCanvasClick = () => {
    selectObject(null);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const shape = e.dataTransfer.getData("object-shape");
    const color = e.dataTransfer.getData("object-color");
    const name = e.dataTransfer.getData("object-name");
    if (!shape) return;

    const rect = e.currentTarget.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width) * 20 - 10;
    const z = ((e.clientY - rect.top) / rect.height) * 20 - 10;

    addObject({
      name: name || shape,
      category: "nature",
      shape: shape as WorldObject["shape"],
      position: [x, 0.5, z],
      rotation: [0, 0, 0],
      scale: [1, 1, 1],
      color: color || "#f97316",
    });
  };

  return (
    <div
      className="w-full h-full relative rounded-2xl overflow-hidden"
      onDragOver={(e) => e.preventDefault()}
      onDrop={handleDrop}
    >
      <Canvas
        shadows
        camera={{ position: [8, 8, 8], fov: 50 }}
        onClick={handleCanvasClick}
      >
        <EnvironmentLayer />

        {objects.map((obj) => (
          <WorldObject3D key={obj.id} object={obj} />
        ))}

        {selectedObject && mode === "build" && (
          <TransformControlsWrapper
            object={selectedObject}
            onUpdate={updateObject}
          />
        )}

        {mode === "build" && (
          <OrbitControls
            makeDefault
            maxPolarAngle={Math.PI / 2.1}
            minDistance={3}
            maxDistance={30}
          />
        )}
      </Canvas>
    </div>
  );
}

function TransformControlsWrapper({
  object,
  onUpdate,
}: {
  object: { id: string; position: [number, number, number]; rotation: [number, number, number]; scale: [number, number, number] };
  onUpdate: (id: string, updates: Record<string, unknown>) => void;
}) {
  const meshRef = useRef<Mesh>(null);

  return (
    <>
      <mesh ref={meshRef} position={object.position} rotation={object.rotation} scale={object.scale}>
        <boxGeometry args={[0, 0, 0]} />
        <meshBasicMaterial visible={false} />
      </mesh>
      <TransformControls
        object={meshRef.current ?? undefined}
        mode="translate"
        onObjectChange={() => {
          if (meshRef.current) {
            const pos = meshRef.current.position;
            onUpdate(object.id, { position: [pos.x, pos.y, pos.z] });
          }
        }}
      />
    </>
  );
}
