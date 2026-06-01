"use client";

import { Canvas } from "@react-three/fiber";
import { OrbitControls } from "@react-three/drei";
import { useWorldStore } from "@/store/world-store";
import SceneObject from "./scene-object";
import Environment from "./environment";

interface WorldCanvasProps {
  isPlayMode?: boolean;
}

export default function WorldCanvas({ isPlayMode }: WorldCanvasProps) {
  const objects = useWorldStore((s) => s.currentWorld?.objects ?? []);
  const selectedId = useWorldStore((s) => s.selectedObjectId);
  const selectObject = useWorldStore((s) => s.selectObject);

  return (
    <Canvas
      shadows
      camera={{ position: [8, 6, 8], fov: 50 }}
      onPointerMissed={() => {
        if (!isPlayMode) selectObject(null);
      }}
    >
      <Environment />
      <OrbitControls
        makeDefault
        maxPolarAngle={Math.PI / 2.1}
        minDistance={3}
        maxDistance={25}
        enablePan={!isPlayMode}
      />
      {objects.map((obj) => (
        <SceneObject
          key={obj.id}
          object={obj}
          isSelected={obj.id === selectedId}
          isPlayMode={isPlayMode}
        />
      ))}
    </Canvas>
  );
}
