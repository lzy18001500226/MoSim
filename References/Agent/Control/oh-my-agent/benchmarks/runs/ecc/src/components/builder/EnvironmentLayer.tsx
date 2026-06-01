"use client";

import { useWorldStore } from "@/stores/world-store";
import { ENVIRONMENT_THEMES } from "@/lib/object-catalog";
import { Sky, Stars, Grid } from "@react-three/drei";

export function EnvironmentLayer() {
  const theme = useWorldStore((s) => s.project.theme);
  const envConfig = ENVIRONMENT_THEMES.find((t) => t.id === theme) ?? ENVIRONMENT_THEMES[0];

  const isNight = theme === "night" || theme === "space";
  const isSpace = theme === "space";

  return (
    <>
      <ambientLight intensity={isNight ? 0.3 : 0.6} />
      <directionalLight
        position={[10, 15, 10]}
        intensity={isNight ? 0.4 : 1.2}
        castShadow
        shadow-mapSize={[1024, 1024]}
      />

      {!isSpace && (
        <Sky
          sunPosition={isNight ? [0, -1, 0] : [100, 20, 100]}
          turbidity={isNight ? 20 : 8}
          rayleigh={isNight ? 0 : 2}
        />
      )}

      {(isNight || isSpace) && <Stars radius={100} depth={50} count={2000} fade speed={1} />}

      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.01, 0]} receiveShadow>
        <planeGeometry args={[100, 100]} />
        <meshStandardMaterial color={envConfig.groundColor} />
      </mesh>

      <Grid
        position={[0, 0, 0]}
        args={[50, 50]}
        cellSize={1}
        cellThickness={0.5}
        cellColor="#a0aec0"
        sectionSize={5}
        sectionThickness={1}
        sectionColor="#718096"
        fadeDistance={30}
        fadeStrength={1}
        infiniteGrid
      />

      <fog attach="fog" args={[envConfig.skyColor, 20, 60]} />
    </>
  );
}
