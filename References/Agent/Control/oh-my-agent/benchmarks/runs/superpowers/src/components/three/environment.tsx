"use client";

import { useWorldStore } from "@/store/world-store";
import type { EnvironmentTheme } from "@/types/world";

const THEME_COLORS: Record<EnvironmentTheme, { ground: string; sky: string; fog: string; ambient: string }> = {
  meadow: { ground: "#7BC67E", sky: "#87CEEB", fog: "#C8E6C9", ambient: "#FFF8E1" },
  desert: { ground: "#F4D03F", sky: "#F5CBA7", fog: "#FAD7A0", ambient: "#FFF3E0" },
  ocean: { ground: "#1565C0", sky: "#4FC3F7", fog: "#B3E5FC", ambient: "#E1F5FE" },
  space: { ground: "#1A1A2E", sky: "#0D0D1A", fog: "#1A1A2E", ambient: "#311B92" },
  forest: { ground: "#2E7D32", sky: "#81C784", fog: "#A5D6A7", ambient: "#E8F5E9" },
  snow: { ground: "#ECEFF1", sky: "#E3F2FD", fog: "#F5F5F5", ambient: "#E8EAF6" },
  candy: { ground: "#F8BBD0", sky: "#FCE4EC", fog: "#F8BBD0", ambient: "#FFF3E0" },
  volcano: { ground: "#5D4037", sky: "#FF8A65", fog: "#BCAAA4", ambient: "#FBE9E7" },
};

export default function Environment() {
  const theme = useWorldStore((s) => s.currentWorld?.theme ?? "meadow");
  const colors = THEME_COLORS[theme];

  return (
    <>
      <color attach="background" args={[colors.sky]} />
      <fog attach="fog" args={[colors.fog, 15, 40]} />
      <ambientLight intensity={0.6} color={colors.ambient} />
      <directionalLight position={[10, 10, 5]} intensity={1} castShadow />
      <directionalLight position={[-5, 5, -5]} intensity={0.3} />

      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0, 0]} receiveShadow>
        <planeGeometry args={[60, 60]} />
        <meshStandardMaterial color={colors.ground} />
      </mesh>

      <gridHelper args={[30, 30, "#ffffff33", "#ffffff22"]} position={[0, 0.01, 0]} />
    </>
  );
}
