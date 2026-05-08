#!/usr/bin/env python3
"""Generate a self-contained Three.js replay HTML from replay JSON."""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path


HTML_TEMPLATE = """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>
    html, body {{
      margin: 0;
      width: 100%;
      height: 100%;
      overflow: hidden;
      background: #0f1117;
      color: #e8edf7;
      font-family: Arial, "Microsoft YaHei", sans-serif;
    }}
    #hud {{
      position: fixed;
      left: 18px;
      top: 16px;
      z-index: 2;
      min-width: 280px;
      padding: 12px 14px;
      background: rgba(16, 19, 28, 0.82);
      border: 1px solid rgba(255, 255, 255, 0.14);
      border-radius: 8px;
      backdrop-filter: blur(8px);
    }}
    #title {{
      font-size: 15px;
      font-weight: 700;
      margin-bottom: 8px;
    }}
    #meta {{
      display: grid;
      gap: 4px;
      font-size: 12px;
      line-height: 1.45;
      color: #b9c3d9;
    }}
    #controls {{
      position: fixed;
      left: 18px;
      right: 18px;
      bottom: 16px;
      z-index: 2;
      display: grid;
      grid-template-columns: auto 1fr auto;
      gap: 12px;
      align-items: center;
      padding: 10px 12px;
      background: rgba(16, 19, 28, 0.82);
      border: 1px solid rgba(255, 255, 255, 0.14);
      border-radius: 8px;
      backdrop-filter: blur(8px);
    }}
    button {{
      height: 34px;
      padding: 0 14px;
      color: #10131c;
      background: #8fd3ff;
      border: 0;
      border-radius: 6px;
      font-weight: 700;
      cursor: pointer;
    }}
    input[type="range"] {{
      width: 100%;
      accent-color: #8fd3ff;
    }}
    #timeLabel {{
      min-width: 92px;
      font-variant-numeric: tabular-nums;
      color: #e8edf7;
      text-align: right;
    }}
  </style>
</head>
<body>
  <div id="hud">
    <div id="title">{title}</div>
    <div id="meta">
      <div>模型：{model_name}</div>
      <div>说明：{description}</div>
      <div>帧数：{frame_count}</div>
      <div>数据：{source}</div>
    </div>
  </div>
  <div id="controls">
    <button id="play">暂停</button>
    <input id="scrub" type="range" min="0" max="{max_index}" value="0" step="1">
    <div id="timeLabel">0.00 s</div>
  </div>
  <script type="importmap">
    {{
      "imports": {{
        "three": "https://unpkg.com/three@0.165.0/build/three.module.js",
        "three/addons/": "https://unpkg.com/three@0.165.0/examples/jsm/"
      }}
    }}
  </script>
  <script type="module">
    import * as THREE from 'three';
    import {{ OrbitControls }} from 'three/addons/controls/OrbitControls.js';

    const replay = {payload};
    const frames = replay.frames || [];

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0f1117);
    scene.fog = new THREE.Fog(0x0f1117, 28, 95);

    const camera = new THREE.PerspectiveCamera(55, window.innerWidth / window.innerHeight, 0.1, 200);
    camera.position.set(18, -24, 16);

    const renderer = new THREE.WebGLRenderer({{ antialias: true }});
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(window.innerWidth, window.innerHeight);
    document.body.appendChild(renderer.domElement);

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.target.set(0, 0, 4);
    controls.enableDamping = true;

    scene.add(new THREE.HemisphereLight(0xaec9ff, 0x1f2430, 1.6));
    const sun = new THREE.DirectionalLight(0xffffff, 2.4);
    sun.position.set(10, -12, 24);
    scene.add(sun);

    const grid = new THREE.GridHelper(32, 32, 0x3f4b61, 0x202632);
    grid.rotation.x = Math.PI / 2;
    scene.add(grid);

    const axes = new THREE.AxesHelper(4);
    scene.add(axes);

    function getPosition(frame) {{
      const uav = frame.uav && frame.uav[0];
      return uav ? uav.position : [0, 0, 0];
    }}

    const pathPoints = frames.map((frame) => {{
      const p = getPosition(frame);
      return new THREE.Vector3(p[0], p[1], p[2]);
    }});
    const pathGeometry = new THREE.BufferGeometry().setFromPoints(pathPoints);
    const pathMaterial = new THREE.LineBasicMaterial({{ color: 0x8fd3ff }});
    scene.add(new THREE.Line(pathGeometry, pathMaterial));

    const drone = new THREE.Group();
    const body = new THREE.Mesh(
      new THREE.BoxGeometry(0.72, 0.42, 0.18),
      new THREE.MeshStandardMaterial({{ color: 0xf2f6ff, roughness: 0.45, metalness: 0.15 }})
    );
    drone.add(body);

    const armMaterial = new THREE.MeshStandardMaterial({{ color: 0x89a6c8, roughness: 0.35 }});
    const arm1 = new THREE.Mesh(new THREE.BoxGeometry(1.35, 0.06, 0.06), armMaterial);
    const arm2 = new THREE.Mesh(new THREE.BoxGeometry(0.06, 1.35, 0.06), armMaterial);
    drone.add(arm1, arm2);

    const rotorMaterial = new THREE.MeshStandardMaterial({{ color: 0x61ffb5, roughness: 0.25 }});
    for (const [x, y] of [[0.68, 0.68], [0.68, -0.68], [-0.68, 0.68], [-0.68, -0.68]]) {{
      const rotor = new THREE.Mesh(new THREE.CylinderGeometry(0.18, 0.18, 0.035, 32), rotorMaterial);
      rotor.rotation.x = Math.PI / 2;
      rotor.position.set(x, y, 0.02);
      drone.add(rotor);
    }}
    scene.add(drone);

    const marker = new THREE.Mesh(
      new THREE.SphereGeometry(0.08, 20, 20),
      new THREE.MeshBasicMaterial({{ color: 0xffd166 }})
    );
    scene.add(marker);

    const scrub = document.getElementById('scrub');
    const playButton = document.getElementById('play');
    const timeLabel = document.getElementById('timeLabel');
    let frameIndex = 0;
    let playing = true;
    let lastTick = performance.now();

    function setFrame(index) {{
      frameIndex = Math.max(0, Math.min(frames.length - 1, index));
      const frame = frames[frameIndex];
      const p = getPosition(frame);
      drone.position.set(p[0], p[1], p[2]);
      marker.position.set(p[0], p[1], p[2]);
      scrub.value = frameIndex;
      timeLabel.textContent = `${{Number(frame.time || 0).toFixed(2)}} s`;
    }}

    playButton.addEventListener('click', () => {{
      playing = !playing;
      playButton.textContent = playing ? '暂停' : '播放';
    }});

    scrub.addEventListener('input', () => {{
      playing = false;
      playButton.textContent = '播放';
      setFrame(Number(scrub.value));
    }});

    window.addEventListener('resize', () => {{
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    }});

    function animate(now) {{
      requestAnimationFrame(animate);
      controls.update();
      if (playing && frames.length > 0 && now - lastTick > 33) {{
        setFrame((frameIndex + 1) % frames.length);
        lastTick = now;
      }}
      drone.rotation.z += 0.012;
      renderer.render(scene, camera);
    }}

    setFrame(0);
    animate(performance.now());
  </script>
</body>
</html>
"""


def build_html(replay_path: Path, output_path: Path) -> None:
    payload = json.loads(replay_path.read_text(encoding="utf-8"))
    title = f"{payload.get('scene_id', replay_path.stem)} 三维回放"
    frame_count = len(payload.get("frames", []))
    html_text = HTML_TEMPLATE.format(
        title=html.escape(title),
        model_name=html.escape(str(payload.get("model_name", ""))),
        description=html.escape(str(payload.get("description", ""))),
        frame_count=frame_count,
        source=html.escape(str(payload.get("source", replay_path.name))),
        max_index=max(0, frame_count - 1),
        payload=json.dumps(payload, ensure_ascii=False),
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html_text, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("replay_json", type=Path, nargs="?", help="Replay JSON file")
    parser.add_argument("output_html", type=Path, nargs="?", help="Output HTML file")
    parser.add_argument("--all", action="store_true", help="Generate HTML for all results/replay/*.json files")
    parser.add_argument("--input-dir", type=Path, default=Path("results/replay"))
    parser.add_argument("--output-dir", type=Path, default=Path("results/replay_html"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.all:
      paths = sorted(args.input_dir.glob("*.json"))
      if not paths:
          raise FileNotFoundError(f"No replay JSON files found in {args.input_dir}")
      for replay_path in paths:
          output_path = args.output_dir / f"{replay_path.stem}.html"
          build_html(replay_path, output_path)
          print(f"Wrote {output_path}")
      return 0

    if not args.replay_json or not args.output_html:
        raise SystemExit("Usage: generate_replay_html.py <replay_json> <output_html> or --all")
    build_html(args.replay_json, args.output_html)
    print(f"Wrote {args.output_html}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
