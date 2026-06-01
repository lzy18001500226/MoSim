import type { Size } from "./types.js";

export interface SizeGuardOk {
  ok: true;
  size: Size;
}

export interface SizeGuardErr {
  ok: false;
  reason: string;
}

export type SizeGuardResult = SizeGuardOk | SizeGuardErr;

// gpt-image-2 documented constraints. Other providers (pollinations, antigravity)
// have their own validators; this guard enforces the union expressible to the
// CLI's `--size` flag. Keep it close to gpt-image-2 because that's the most
// permissive vendor wired in: 16-pixel grid, aspect between 1:3 and 3:1,
// per-edge cap at 3840.
const MIN_EDGE = 16;
const MAX_EDGE = 3840;
const ALIGN = 16;
const MIN_RATIO = 1 / 3;
const MAX_RATIO = 3;

export function validateSize(raw: string): SizeGuardResult {
  if (raw === "auto") return { ok: true, size: "auto" };

  const match = /^(\d+)x(\d+)$/.exec(raw);
  if (!match) {
    return {
      ok: false,
      reason: `expected "WxH" or "auto", got "${raw}"`,
    };
  }

  const width = Number.parseInt(match[1] ?? "0", 10);
  const height = Number.parseInt(match[2] ?? "0", 10);

  if (width < MIN_EDGE || height < MIN_EDGE) {
    return {
      ok: false,
      reason: `width and height must each be ≥ ${MIN_EDGE}px (got ${width}x${height})`,
    };
  }
  if (width > MAX_EDGE || height > MAX_EDGE) {
    return {
      ok: false,
      reason: `width and height must each be ≤ ${MAX_EDGE}px (got ${width}x${height})`,
    };
  }
  if (width % ALIGN !== 0 || height % ALIGN !== 0) {
    return {
      ok: false,
      reason: `width and height must be multiples of ${ALIGN} (got ${width}x${height})`,
    };
  }

  const ratio = width / height;
  if (ratio < MIN_RATIO || ratio > MAX_RATIO) {
    return {
      ok: false,
      reason: `aspect ratio must be between 1:3 and 3:1 (got ${width}:${height})`,
    };
  }

  return { ok: true, size: `${width}x${height}` };
}
