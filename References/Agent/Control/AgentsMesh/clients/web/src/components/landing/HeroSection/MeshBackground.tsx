"use client";

const HUB_NODES: Array<{ x: number; y: number; delay: number; size: number }> = [
  { x: 8, y: 15, delay: 0, size: 11 },
  { x: 22, y: 55, delay: 0.8, size: 8 },
  { x: 18, y: 82, delay: 2.6, size: 10 },
  { x: 48, y: 12, delay: 1.6, size: 9 },
  { x: 50, y: 88, delay: 0.4, size: 8 },
  { x: 78, y: 18, delay: 2.2, size: 11 },
  { x: 82, y: 52, delay: 1.2, size: 8 },
  { x: 92, y: 85, delay: 1.8, size: 10 },
  { x: 68, y: 75, delay: 0, size: 9 },
];

const EDGES: Array<[number, number, number]> = [
  [0, 1, 0],
  [1, 2, 0.6],
  [0, 3, 1.2],
  [3, 5, 0.4],
  [5, 6, 1.8],
  [6, 7, 1.0],
  [7, 8, 2.2],
  [8, 4, 1.6],
  [4, 2, 2.6],
  [6, 8, 2.4],
  [1, 3, 0.8],
];

const STARS: Array<{ x: number; y: number; size: number; delay: number; opacity: number }> = [
  { x: 3, y: 14, size: 2.5, delay: 0.3, opacity: 0.9 },
  { x: 7, y: 32, size: 3, delay: 1.8, opacity: 1 },
  { x: 9, y: 6, size: 1.5, delay: 2.4, opacity: 0.7 },
  { x: 11, y: 48, size: 2, delay: 0.6, opacity: 0.85 },
  { x: 15, y: 72, size: 3, delay: 2.1, opacity: 1 },
  { x: 17, y: 20, size: 1.5, delay: 1.1, opacity: 0.75 },
  { x: 19, y: 60, size: 2.5, delay: 0.4, opacity: 0.95 },
  { x: 21, y: 4, size: 2, delay: 2.7, opacity: 0.8 },
  { x: 23, y: 88, size: 3, delay: 1.3, opacity: 1 },
  { x: 25, y: 34, size: 1.5, delay: 0.9, opacity: 0.7 },
  { x: 27, y: 16, size: 2, delay: 2.5, opacity: 0.85 },
  { x: 29, y: 78, size: 2.5, delay: 0.1, opacity: 0.95 },
  { x: 31, y: 46, size: 1, delay: 1.6, opacity: 0.55 },
  { x: 33, y: 26, size: 3, delay: 2.3, opacity: 1 },
  { x: 35, y: 94, size: 2, delay: 0.8, opacity: 0.85 },
  { x: 37, y: 10, size: 1.5, delay: 1.9, opacity: 0.7 },
  { x: 39, y: 66, size: 2.5, delay: 2.8, opacity: 0.95 },
  { x: 41, y: 38, size: 1, delay: 0.5, opacity: 0.5 },
  { x: 43, y: 18, size: 2, delay: 1.5, opacity: 0.8 },
  { x: 45, y: 84, size: 3, delay: 2.2, opacity: 1 },
  { x: 47, y: 52, size: 1, delay: 0.7, opacity: 0.5 },
  { x: 49, y: 4, size: 1.5, delay: 2.6, opacity: 0.7 },
  { x: 51, y: 72, size: 2.5, delay: 1.2, opacity: 0.95 },
  { x: 53, y: 26, size: 1.5, delay: 0.3, opacity: 0.75 },
  { x: 55, y: 94, size: 2, delay: 1.7, opacity: 0.85 },
  { x: 57, y: 42, size: 1, delay: 2.4, opacity: 0.5 },
  { x: 59, y: 12, size: 2.5, delay: 0.6, opacity: 0.95 },
  { x: 61, y: 58, size: 1, delay: 1.4, opacity: 0.5 },
  { x: 63, y: 84, size: 2, delay: 2.9, opacity: 0.85 },
  { x: 65, y: 20, size: 3, delay: 0.2, opacity: 1 },
  { x: 67, y: 68, size: 1.5, delay: 1.8, opacity: 0.7 },
  { x: 69, y: 4, size: 2, delay: 2.5, opacity: 0.8 },
  { x: 71, y: 34, size: 2.5, delay: 1.0, opacity: 0.95 },
  { x: 73, y: 82, size: 1.5, delay: 0.4, opacity: 0.7 },
  { x: 75, y: 48, size: 1, delay: 2.0, opacity: 0.5 },
  { x: 77, y: 14, size: 2.5, delay: 1.5, opacity: 0.9 },
  { x: 79, y: 92, size: 2, delay: 2.7, opacity: 0.85 },
  { x: 81, y: 28, size: 1.5, delay: 0.9, opacity: 0.7 },
  { x: 83, y: 62, size: 3, delay: 1.3, opacity: 1 },
  { x: 85, y: 44, size: 1, delay: 2.3, opacity: 0.55 },
  { x: 87, y: 8, size: 2, delay: 0.5, opacity: 0.85 },
  { x: 89, y: 76, size: 2.5, delay: 2.1, opacity: 0.95 },
  { x: 91, y: 22, size: 1.5, delay: 1.6, opacity: 0.7 },
  { x: 93, y: 92, size: 2, delay: 0.8, opacity: 0.85 },
  { x: 95, y: 50, size: 3, delay: 1.9, opacity: 1 },
  { x: 97, y: 16, size: 2, delay: 2.4, opacity: 0.85 },
  { x: 99, y: 78, size: 1.5, delay: 0.2, opacity: 0.75 },
  { x: 5, y: 84, size: 1.5, delay: 1.1, opacity: 0.7 },
  { x: 13, y: 40, size: 2.5, delay: 2.6, opacity: 0.95 },
  { x: 45, y: 58, size: 0.8, delay: 0.4, opacity: 0.4 },
  { x: 50, y: 38, size: 0.8, delay: 2.2, opacity: 0.4 },
  { x: 55, y: 70, size: 0.8, delay: 1.3, opacity: 0.4 },
  { x: 38, y: 78, size: 0.8, delay: 0.9, opacity: 0.4 },
  { x: 60, y: 80, size: 0.8, delay: 2.5, opacity: 0.4 },
];

export function MeshBackground() {
  const hubMask = {
    maskImage:
      "radial-gradient(ellipse 65% 60% at center, transparent 45%, rgba(0,0,0,0.4) 72%, black 100%)",
    WebkitMaskImage:
      "radial-gradient(ellipse 65% 60% at center, transparent 45%, rgba(0,0,0,0.4) 72%, black 100%)",
  };

  return (
    <>
      <div className="absolute inset-0 pointer-events-none">
        {STARS.map((s, i) => (
          <span
            key={i}
            className="mesh-star absolute rounded-full"
            style={{
              left: `${s.x}%`,
              top: `${s.y}%`,
              width: `${s.size}px`,
              height: `${s.size}px`,
              opacity: s.opacity,
              animationDelay: `${s.delay}s`,
              background: "#ffffff",
              boxShadow: `0 0 ${s.size * 4}px rgba(0, 212, 255, 1), 0 0 ${s.size * 8}px rgba(0, 212, 255, 0.6)`,
              transform: "translate(-50%, -50%)",
            }}
          />
        ))}
      </div>

      <svg
        className="absolute inset-0 w-full h-full pointer-events-none"
        viewBox="0 0 100 100"
        preserveAspectRatio="none"
        aria-hidden="true"
        style={hubMask}
      >
        <defs>
          <linearGradient id="mesh-edge" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="var(--azure-cyan)" stopOpacity="0.1" />
            <stop offset="50%" stopColor="var(--azure-cyan)" stopOpacity="0.9" />
            <stop offset="100%" stopColor="var(--azure-mint)" stopOpacity="0.1" />
          </linearGradient>
        </defs>

        {EDGES.map(([a, b, delay], i) => {
          const from = HUB_NODES[a];
          const to = HUB_NODES[b];
          return (
            <line
              key={i}
              x1={from.x}
              y1={from.y}
              x2={to.x}
              y2={to.y}
              stroke="url(#mesh-edge)"
              strokeWidth="1.4"
              vectorEffect="non-scaling-stroke"
              className="mesh-edge"
              style={{ animationDelay: `${delay}s` }}
            />
          );
        })}
      </svg>

      <div className="absolute inset-0 pointer-events-none" style={hubMask}>
        {HUB_NODES.map((n, i) => (
          <span
            key={i}
            className="mesh-node absolute rounded-full"
            style={{
              left: `${n.x}%`,
              top: `${n.y}%`,
              width: `${n.size}px`,
              height: `${n.size}px`,
              transform: "translate(-50%, -50%)",
              animationDelay: `${n.delay}s`,
              background:
                "radial-gradient(circle, #ffffff 0%, var(--azure-cyan) 30%, rgba(0,212,255,0.3) 70%, rgba(0,212,255,0) 100%)",
              boxShadow: "0 0 22px rgba(0, 212, 255, 0.9), 0 0 40px rgba(0, 212, 255, 0.45)",
            }}
          />
        ))}
      </div>
    </>
  );
}

export default MeshBackground;
