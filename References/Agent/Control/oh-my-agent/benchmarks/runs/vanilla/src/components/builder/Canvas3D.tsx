'use client';

import { Canvas } from '@react-three/fiber';
import { OrbitControls, Grid, Sky, Stars, Environment, ContactShadows } from '@react-three/drei';
import { useWorldStore } from '@/store/useWorldStore';
import { ENVIRONMENT_THEMES } from '@/lib/objects';
import WorldObject3D from './WorldObject3D';
import { Suspense } from 'react';
import * as THREE from 'three';

function SceneEnvironment() {
  const theme = useWorldStore((s) => s.theme);
  const themeData = ENVIRONMENT_THEMES.find((t) => t.id === theme)!;

  return (
    <>
      {theme === 'night' || theme === 'space' ? (
        <Stars radius={100} depth={50} count={3000} factor={4} saturation={0} fade speed={1} />
      ) : (
        <Sky
          sunPosition={
            theme === 'sunset'
              ? [100, 10, 100]
              : [100, 100, 100]
          }
          turbidity={theme === 'desert' ? 15 : 8}
          rayleigh={theme === 'sunset' ? 4 : 2}
        />
      )}

      <fog attach="fog" args={[themeData.fogColor, 20, 60]} />

      <ambientLight intensity={theme === 'night' || theme === 'space' ? 0.3 : 0.6} />
      <directionalLight
        position={[10, 15, 10]}
        intensity={theme === 'night' ? 0.2 : 1}
        castShadow
        shadow-mapSize={[1024, 1024]}
      />
      {(theme === 'night' || theme === 'underwater') && (
        <pointLight position={[0, 5, 0]} intensity={0.5} color="#4FC3F7" />
      )}

      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.01, 0]} receiveShadow>
        <planeGeometry args={[100, 100]} />
        <meshStandardMaterial color={themeData.groundColor} />
      </mesh>

      <Grid
        position={[0, 0.01, 0]}
        args={[50, 50]}
        cellSize={1}
        cellThickness={0.5}
        cellColor="#00000015"
        sectionSize={5}
        sectionThickness={1}
        sectionColor="#00000020"
        fadeDistance={30}
        infiniteGrid
      />

      <ContactShadows
        position={[0, 0, 0]}
        opacity={0.4}
        scale={20}
        blur={2}
        far={4}
      />
    </>
  );
}

function WorldObjects() {
  const objects = useWorldStore((s) => s.objects);
  const selectedObjectId = useWorldStore((s) => s.selectedObjectId);
  const selectObject = useWorldStore((s) => s.selectObject);
  const updateObject = useWorldStore((s) => s.updateObject);
  const mode = useWorldStore((s) => s.mode);

  return (
    <>
      {objects.map((obj) => (
        <WorldObject3D
          key={obj.id}
          id={obj.id}
          type={obj.type}
          position={obj.position}
          rotation={obj.rotation}
          scale={obj.scale}
          color={obj.color}
          animation={obj.animation}
          isSelected={selectedObjectId === obj.id}
          onClick={() => {
            if (mode === 'build') {
              selectObject(selectedObjectId === obj.id ? null : obj.id);
            }
          }}
        />
      ))}
    </>
  );
}

function ClickPlane() {
  const selectObject = useWorldStore((s) => s.selectObject);
  const mode = useWorldStore((s) => s.mode);

  return (
    <mesh
      rotation={[-Math.PI / 2, 0, 0]}
      position={[0, 0, 0]}
      onClick={(e) => {
        if (mode === 'build') {
          e.stopPropagation();
          selectObject(null);
        }
      }}
      visible={false}
    >
      <planeGeometry args={[100, 100]} />
      <meshBasicMaterial transparent opacity={0} />
    </mesh>
  );
}

export default function Canvas3D() {
  const mode = useWorldStore((s) => s.mode);
  const theme = useWorldStore((s) => s.theme);
  const themeData = ENVIRONMENT_THEMES.find((t) => t.id === theme)!;

  return (
    <Canvas
      shadows
      camera={{ position: [8, 8, 8], fov: 50 }}
      style={{ background: themeData.skyColor }}
      onPointerMissed={() => {
        if (mode === 'build') {
          useWorldStore.getState().selectObject(null);
        }
      }}
    >
      <Suspense fallback={null}>
        <SceneEnvironment />
        <WorldObjects />
        <ClickPlane />
        <OrbitControls
          makeDefault
          maxPolarAngle={Math.PI / 2.1}
          minDistance={3}
          maxDistance={30}
          enablePan={mode === 'explore'}
        />
      </Suspense>
    </Canvas>
  );
}
