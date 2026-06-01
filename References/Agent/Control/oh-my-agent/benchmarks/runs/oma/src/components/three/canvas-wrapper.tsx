"use client";

import { Canvas } from "@react-three/fiber";
import { type ReactNode } from "react";

interface CanvasWrapperProps {
  children: ReactNode;
  className?: string;
}

export function CanvasWrapper({ children, className }: CanvasWrapperProps) {
  return (
    <Canvas
      className={className}
      shadows
      camera={{ position: [8, 6, 8], fov: 50 }}
      gl={{ antialias: true }}
    >
      {children}
    </Canvas>
  );
}
