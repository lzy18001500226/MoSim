"use client";

import { Canvas } from "@react-three/fiber";
import { OrbitControls, Grid, Sky } from "@react-three/drei";
import { useWorldStore } from "@/store/worldStore";
import { WorldObject3D } from "./WorldObject3D";
import { ENVIRONMENT_THEMES } from "@/lib/objects";

export function Canvas3D() {
  const currentWorld = useWorldStore((s) => s.currentWorld);
  const selectedObjectId = useWorldStore((s) => s.selectedObjectId);
  const selectObject = useWorldStore((s) => s.selectObject);
  const isPlaying = useWorldStore((s) => s.isPlaying);

  if (!currentWorld) return null;

  const envTheme = ENVIRONMENT_THEMES.find((e) => e.id === currentWorld.environment);
  const groundColor = envTheme?.groundColor || "#90EE90";
  const isSpace = currentWorld.environment === "space";
  const isUnderwater = currentWorld.environment === "underwater";

  return (
    <div className="h-full w-full">
      <Canvas
        camera={{ position: [5, 5, 5], fov: 60 }}
        shadows
        onClick={() => selectObject(null)}
      >
        <ambientLight intensity={0.5} />
        <directionalLight position={[10, 10, 5]} intensity={1} castShadow />
        <pointLight position={[-5, 5, -5]} intensity={0.3} />

        {!isSpace && !isUnderwater && (
          <Sky sunPosition={[100, 20, 100]} />
        )}

        {isUnderwater && (
          <fog attach="fog" args={["#006994", 5, 30]} />
        )}

        {isSpace && (
          <>
            <color attach="background" args={["#0f0f23"]} />
            <ambientLight intensity={0.2} />
          </>
        )}

        <mesh
          rotation={[-Math.PI / 2, 0, 0]}
          position={[0, -0.01, 0]}
          receiveShadow
        >
          <planeGeometry args={[50, 50]} />
          <meshStandardMaterial color={groundColor} />
        </mesh>

        <Grid
          position={[0, 0, 0]}
          args={[20, 20]}
          cellSize={1}
          cellColor="#6366f1"
          sectionSize={5}
          sectionColor="#4f46e5"
          fadeDistance={25}
          infiniteGrid
        />

        {currentWorld.objects.map((obj) => (
          <WorldObject3D
            key={obj.id}
            object={obj}
            isSelected={obj.id === selectedObjectId}
          />
        ))}

        <OrbitControls
          makeDefault
          maxPolarAngle={Math.PI / 2.1}
          minDistance={2}
          maxDistance={20}
          enablePan={!isPlaying}
        />
      </Canvas>
    </div>
  );
}
