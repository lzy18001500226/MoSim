#!/usr/bin/env python3
"""Generate an offline browser replay HTML from replay JSON.

The generated page has no external CDN dependency. It uses Canvas 2D with a
simple 3D projection, which is reliable for contest recording and works by
opening the HTML file directly in a browser.
"""

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
      color: #eef3fb;
      font-family: Arial, "Microsoft YaHei", sans-serif;
    }}
    canvas {{
      display: block;
      width: 100vw;
      height: 100vh;
    }}
    #hud {{
      position: fixed;
      left: 18px;
      top: 16px;
      z-index: 2;
      width: min(420px, calc(100vw - 36px));
      padding: 12px 14px;
      background: rgba(14, 18, 28, 0.84);
      border: 1px solid rgba(255, 255, 255, 0.14);
      border-radius: 8px;
      backdrop-filter: blur(8px);
      box-sizing: border-box;
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
      color: #bbc6db;
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
      background: rgba(14, 18, 28, 0.84);
      border: 1px solid rgba(255, 255, 255, 0.14);
      border-radius: 8px;
      backdrop-filter: blur(8px);
      box-sizing: border-box;
    }}
    button {{
      height: 34px;
      min-width: 64px;
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
      color: #eef3fb;
      text-align: right;
    }}
  </style>
</head>
<body>
  <canvas id="scene"></canvas>
  <div id="hud">
    <div id="title">{title}</div>
    <div id="meta">
      <div>模型：{model_name}</div>
      <div>说明：{description}</div>
      <div>帧数：{frame_count}</div>
      <div>数据：{source}</div>
      <div>渲染：离线 Canvas 3D 投影，无外部依赖</div>
    </div>
  </div>
  <div id="controls">
    <button id="play">暂停</button>
    <input id="scrub" type="range" min="0" max="{max_index}" value="0" step="1">
    <div id="timeLabel">0.00 s</div>
  </div>
  <script>
    const replay = {payload};
    const frames = replay.frames || [];
    const canvas = document.getElementById('scene');
    const ctx = canvas.getContext('2d');
    const scrub = document.getElementById('scrub');
    const playButton = document.getElementById('play');
    const timeLabel = document.getElementById('timeLabel');

    let width = 0;
    let height = 0;
    let scale = 34;
    let frameIndex = 0;
    let playing = true;
    let lastStep = performance.now();

    function resize() {{
      const ratio = Math.min(window.devicePixelRatio || 1, 2);
      width = Math.floor(window.innerWidth * ratio);
      height = Math.floor(window.innerHeight * ratio);
      canvas.width = width;
      canvas.height = height;
      canvas.style.width = window.innerWidth + 'px';
      canvas.style.height = window.innerHeight + 'px';
      ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
      width = window.innerWidth;
      height = window.innerHeight;
      const bounds = computeBounds();
      const span = Math.max(bounds.maxX - bounds.minX, bounds.maxY - bounds.minY, bounds.maxZ - bounds.minZ, 1);
      scale = Math.max(18, Math.min(54, Math.min(width, height) / (span * 2.2)));
    }}

    function getPosition(frame) {{
      const uav = frame && frame.uav && frame.uav[0];
      return uav ? uav.position : [0, 0, 0];
    }}

    function computeBounds() {{
      const values = frames.map(getPosition);
      const xs = values.map(p => p[0]);
      const ys = values.map(p => p[1]);
      const zs = values.map(p => p[2]);
      return {{
        minX: Math.min(...xs, -2), maxX: Math.max(...xs, 2),
        minY: Math.min(...ys, -2), maxY: Math.max(...ys, 2),
        minZ: Math.min(...zs, 0), maxZ: Math.max(...zs, 2)
      }};
    }}

    function project(point) {{
      const [x, y, z] = point;
      const cx = width * 0.52;
      const cy = height * 0.58;
      const px = cx + (x - y) * scale * 0.82;
      const py = cy + (x + y) * scale * 0.36 - z * scale * 0.92;
      return [px, py];
    }}

    function drawLine3(a, b, color, lineWidth = 1) {{
      const pa = project(a);
      const pb = project(b);
      ctx.beginPath();
      ctx.moveTo(pa[0], pa[1]);
      ctx.lineTo(pb[0], pb[1]);
      ctx.strokeStyle = color;
      ctx.lineWidth = lineWidth;
      ctx.stroke();
    }}

    function drawGrid() {{
      const size = 16;
      for (let i = -size; i <= size; i += 1) {{
        const strong = i === 0;
        drawLine3([-size, i, 0], [size, i, 0], strong ? '#58647a' : '#263044', strong ? 1.5 : 0.8);
        drawLine3([i, -size, 0], [i, size, 0], strong ? '#58647a' : '#263044', strong ? 1.5 : 0.8);
      }}
      drawLine3([0, 0, 0], [4, 0, 0], '#ff6b6b', 2);
      drawLine3([0, 0, 0], [0, 4, 0], '#61d394', 2);
      drawLine3([0, 0, 0], [0, 0, 4], '#8fd3ff', 2);
    }}

    function drawPath() {{
      if (frames.length < 2) return;
      ctx.beginPath();
      frames.forEach((frame, index) => {{
        const p = project(getPosition(frame));
        if (index === 0) ctx.moveTo(p[0], p[1]);
        else ctx.lineTo(p[0], p[1]);
      }});
      ctx.strokeStyle = '#8fd3ff';
      ctx.lineWidth = 2.2;
      ctx.stroke();
    }}

    function drawDrone(position, time) {{
      const center = project(position);
      const arm = 26;
      const bob = Math.sin(time * 5) * 2;
      ctx.save();
      ctx.translate(center[0], center[1] + bob);
      ctx.rotate(Math.sin(time * 0.8) * 0.18);

      ctx.strokeStyle = '#dfe9ff';
      ctx.lineWidth = 5;
      ctx.lineCap = 'round';
      ctx.beginPath();
      ctx.moveTo(-arm, 0);
      ctx.lineTo(arm, 0);
      ctx.moveTo(0, -arm);
      ctx.lineTo(0, arm);
      ctx.stroke();

      ctx.fillStyle = '#f5f8ff';
      ctx.strokeStyle = '#1b2433';
      ctx.lineWidth = 2;
      roundRect(-17, -11, 34, 22, 5);
      ctx.fill();
      ctx.stroke();

      const rotors = [[-arm, 0], [arm, 0], [0, -arm], [0, arm]];
      for (const [x, y] of rotors) {{
        ctx.beginPath();
        ctx.ellipse(x, y, 11, 5, time * 7, 0, Math.PI * 2);
        ctx.fillStyle = '#61ffb5';
        ctx.fill();
        ctx.strokeStyle = 'rgba(255,255,255,0.55)';
        ctx.stroke();
      }}
      ctx.restore();

      const ground = project([position[0], position[1], 0]);
      ctx.beginPath();
      ctx.moveTo(center[0], center[1]);
      ctx.lineTo(ground[0], ground[1]);
      ctx.strokeStyle = 'rgba(255, 209, 102, 0.45)';
      ctx.lineWidth = 1;
      ctx.stroke();
      ctx.beginPath();
      ctx.ellipse(ground[0], ground[1], 12, 5, 0, 0, Math.PI * 2);
      ctx.fillStyle = 'rgba(255, 209, 102, 0.35)';
      ctx.fill();
    }}

    function roundRect(x, y, w, h, r) {{
      ctx.beginPath();
      ctx.moveTo(x + r, y);
      ctx.arcTo(x + w, y, x + w, y + h, r);
      ctx.arcTo(x + w, y + h, x, y + h, r);
      ctx.arcTo(x, y + h, x, y, r);
      ctx.arcTo(x, y, x + w, y, r);
      ctx.closePath();
    }}

    function drawLabels() {{
      ctx.fillStyle = '#bbc6db';
      ctx.font = '12px Arial';
      const x = project([4.2, 0, 0]);
      const y = project([0, 4.2, 0]);
      const z = project([0, 0, 4.2]);
      ctx.fillText('X', x[0], x[1]);
      ctx.fillText('Y', y[0], y[1]);
      ctx.fillText('Z', z[0], z[1]);
    }}

    function render(now) {{
      requestAnimationFrame(render);
      if (playing && frames.length > 0 && now - lastStep > 33) {{
        frameIndex = (frameIndex + 1) % frames.length;
        lastStep = now;
      }}
      const frame = frames[frameIndex] || {{ time: 0 }};
      const time = Number(frame.time || 0);
      scrub.value = frameIndex;
      timeLabel.textContent = `${{time.toFixed(2)}} s`;

      const gradient = ctx.createLinearGradient(0, 0, 0, height);
      gradient.addColorStop(0, '#101827');
      gradient.addColorStop(1, '#0f1117');
      ctx.fillStyle = gradient;
      ctx.fillRect(0, 0, width, height);
      drawGrid();
      drawPath();
      drawDrone(getPosition(frame), time);
      drawLabels();
    }}

    playButton.addEventListener('click', () => {{
      playing = !playing;
      playButton.textContent = playing ? '暂停' : '播放';
    }});

    scrub.addEventListener('input', () => {{
      playing = false;
      playButton.textContent = '播放';
      frameIndex = Number(scrub.value);
    }});

    window.addEventListener('resize', resize);
    resize();
    requestAnimationFrame(render);
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
