/**
 * YouTube harvest via yt-dlp subprocess.
 *
 * Two-pass strategy:
 *   1. **Metadata pass.** Single `yt-dlp ytsearch{limit}:query --dateafter
 *      <cutoff> --write-info-json --skip-download` call. Fast (~10s for 8
 *      hits) and produces `<id>.info.json` per accepted video. Metadata
 *      always lands even if later subtitle fetches fail.
 *   2. **Subtitle pass.** For each video id, parallel
 *      `yt-dlp <url> --write-auto-sub --sub-lang <lang> --skip-download`.
 *      Bounded concurrency = 4. Sub failure (429 / unavailable) is OK —
 *      the item still ships using `description` as body fallback.
 *
 * Why two passes: a one-shot run with both `--write-info-json` and
 * `--write-auto-sub` aborts on the first 429 and never writes info.json,
 * which loses every hit. Splitting them isolates failure domains.
 *
 * Why subs: title + description alone are weak signal for SWOT / pain
 * extraction. Auto-subtitles give the actual spoken transcript — same role
 * as Reddit body text or HN comment_text in other sources.
 */

import { execFile } from "node:child_process";
import { mkdtemp, readdir, readFile, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { promisify } from "node:util";
import type { SourceItem } from "./schema.js";

const execFileAsync = promisify(execFile);

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface VideoInfo {
  id: string;
  title: string;
  channel: string | null;
  view_count: number;
  duration: number | null;
  webpage_url: string;
  upload_date: string | null; // YYYYMMDD
  like_count: number | null;
  comment_count: number | null;
  description: string | null;
}

export interface YoutubeHarvestOpts {
  query: string;
  window: string; // "7d" | "30d" | "90d" | "180d" | "all"
  limit: number;
  locale: "en" | "ko";
  timeoutMs: number; // overall budget for the harvest
}

const SUB_CONCURRENCY = 4;

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

export async function youtubeHarvest(
  opts: YoutubeHarvestOpts,
): Promise<{ items: SourceItem[]; reason?: string }> {
  const tempDir = await mkdtemp(join(tmpdir(), "oma-yt-"));
  // Half the budget for metadata, the rest for subs.
  const metaBudget = Math.max(15_000, Math.floor(opts.timeoutMs / 2));
  const subBudget = Math.max(15_000, opts.timeoutMs - metaBudget);
  try {
    let videos: VideoInfo[];
    try {
      videos = await ytSearchMeta(opts, tempDir, metaBudget);
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      return { items: [], reason: `yt-dlp search: ${msg.slice(0, 200)}` };
    }
    if (videos.length === 0) return { items: [], reason: "no results" };

    // Bounded-parallel subtitle fetch.
    const subLang = opts.locale === "ko" ? "ko" : "en";
    const perVideoTimeout = Math.max(
      8_000,
      Math.floor(subBudget / videos.length),
    );
    const transcripts = await mapBoundedParallel(videos, SUB_CONCURRENCY, (v) =>
      ytFetchSub(v.id, v.webpage_url, subLang, tempDir, perVideoTimeout).catch(
        () => null,
      ),
    );

    const items: SourceItem[] = videos.map((v, i) =>
      toSourceItem(v, transcripts[i] ?? null),
    );
    return { items };
  } finally {
    await rm(tempDir, { recursive: true, force: true }).catch(() => {});
  }
}

// ---------------------------------------------------------------------------
// Pass 1: metadata only
// ---------------------------------------------------------------------------

async function ytSearchMeta(
  opts: YoutubeHarvestOpts,
  tempDir: string,
  timeoutMs: number,
): Promise<VideoInfo[]> {
  const args = [
    `ytsearch${Math.max(1, Math.min(50, opts.limit))}:${opts.query}`,
    "--write-info-json",
    "--skip-download",
    "--no-warnings",
    "--quiet",
    "-o",
    join(tempDir, "%(id)s"),
  ];
  const cutoff = windowToDateAfter(opts.window);
  if (cutoff) args.push("--dateafter", cutoff);

  try {
    await execFileAsync("yt-dlp", args, {
      timeout: timeoutMs,
      maxBuffer: 8 * 1024 * 1024,
    });
  } catch {
    // yt-dlp exits non-zero when all hits get filtered. Continue and read
    // whatever info.json files did land.
  }

  return readInfoJsons(tempDir);
}

export async function readInfoJsons(tempDir: string): Promise<VideoInfo[]> {
  let files: string[];
  try {
    files = await readdir(tempDir);
  } catch {
    return [];
  }
  const videos: VideoInfo[] = [];
  for (const f of files) {
    if (!f.endsWith(".info.json")) continue;
    let info: Record<string, unknown>;
    try {
      const raw = await readFile(join(tempDir, f), "utf-8");
      info = JSON.parse(raw) as Record<string, unknown>;
    } catch {
      continue;
    }
    // Skip the playlist-level info.json (no real video id).
    if (info._type === "playlist") continue;
    if (typeof info.id !== "string" || info.id.length === 0) continue;
    videos.push(toVideoInfo(info));
  }
  return videos;
}

// ---------------------------------------------------------------------------
// Pass 2: per-video subtitle fetch
// ---------------------------------------------------------------------------

async function ytFetchSub(
  id: string,
  webpageUrl: string,
  lang: "en" | "ko",
  tempDir: string,
  timeoutMs: number,
): Promise<string | null> {
  try {
    await execFileAsync(
      "yt-dlp",
      [
        webpageUrl,
        "--write-auto-sub",
        "--sub-lang",
        lang,
        "--sub-format",
        "vtt",
        "--skip-download",
        "--no-warnings",
        "--quiet",
        "-o",
        join(tempDir, "%(id)s"),
      ],
      { timeout: timeoutMs, maxBuffer: 8 * 1024 * 1024 },
    );
  } catch {
    return null;
  }
  return readTranscriptFile(tempDir, id, lang);
}

/**
 * Read + parse the VTT file yt-dlp wrote for a single video.
 * Returns null when the file doesn't exist (sub fetch failed / unavailable).
 * Exposed for tests that pre-populate the temp dir without invoking yt-dlp.
 */
export async function readTranscriptFile(
  tempDir: string,
  id: string,
  lang: "en" | "ko",
): Promise<string | null> {
  const want = `${id}.${lang}.vtt`;
  try {
    const raw = await readFile(join(tempDir, want), "utf-8");
    return parseVtt(raw);
  } catch {
    return null;
  }
}

// ---------------------------------------------------------------------------
// VTT parser
// ---------------------------------------------------------------------------

/**
 * Convert WEBVTT auto-caption text to a plain transcript.
 *   - drops WEBVTT header / NOTE blocks / cue numbers / timestamp lines
 *   - strips inline tags like `<00:00:00.880><c> word</c>`
 *   - dedupes consecutive identical lines (yt-dlp auto-sub repeats lines
 *     for the smooth-scroll effect — keeping them would 3x the text)
 */
export function parseVtt(raw: string): string {
  if (!raw) return "";
  const out: string[] = [];
  let last = "";
  for (const rawLine of raw.split(/\r?\n/)) {
    const line = rawLine.trim();
    if (!line) continue;
    if (line === "WEBVTT") continue;
    if (line.startsWith("Kind:") || line.startsWith("Language:")) continue;
    if (line.startsWith("NOTE")) continue;
    if (/^\d+$/.test(line)) continue; // cue number
    if (/^\d{2}:\d{2}:\d{2}/.test(line)) continue; // timestamp
    if (line.includes("-->")) continue;
    const clean = line.replace(/<[^>]+>/g, "").trim();
    if (!clean) continue;
    if (clean === last) continue;
    out.push(clean);
    last = clean;
  }
  return out.join(" ").replace(/\s+/g, " ").trim();
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function toVideoInfo(info: Record<string, unknown>): VideoInfo {
  const id = String(info.id);
  return {
    id,
    title: String(info.title ?? "").trim(),
    channel:
      info.channel != null
        ? String(info.channel)
        : info.uploader != null
          ? String(info.uploader)
          : null,
    view_count: Number(info.view_count ?? 0),
    duration: info.duration != null ? Number(info.duration) : null,
    webpage_url:
      (info.webpage_url as string | undefined) ??
      `https://www.youtube.com/watch?v=${id}`,
    upload_date: info.upload_date != null ? String(info.upload_date) : null,
    like_count: info.like_count != null ? Number(info.like_count) : null,
    comment_count:
      info.comment_count != null ? Number(info.comment_count) : null,
    description:
      info.description != null ? String(info.description).slice(0, 2000) : null,
  };
}

function windowToDateAfter(window: string): string | null {
  const match = /^(\d+)d$/.exec(window);
  if (!match) return null;
  const days = Number(match[1]);
  const ms = days * 24 * 60 * 60 * 1000;
  const cutoff = new Date(Date.now() - ms);
  const y = cutoff.getUTCFullYear();
  const m = String(cutoff.getUTCMonth() + 1).padStart(2, "0");
  const d = String(cutoff.getUTCDate()).padStart(2, "0");
  return `${y}${m}${d}`;
}

export function toSourceItem(
  v: VideoInfo,
  transcript: string | null,
): SourceItem {
  // Prefer transcript for body, fall back to description
  const body = transcript ?? v.description ?? null;
  const snippet = body ? body.slice(0, 280) : v.title.slice(0, 280);
  const publishedIso = v.upload_date
    ? `${v.upload_date.slice(0, 4)}-${v.upload_date.slice(4, 6)}-${v.upload_date.slice(6, 8)}T00:00:00Z`
    : new Date().toISOString();
  const engagement: Record<string, number> = {
    view_count: v.view_count,
  };
  if (v.like_count != null) engagement.like_count = v.like_count;
  if (v.comment_count != null) engagement.num_comments = v.comment_count;
  return {
    item_id: `youtube:${v.id}`,
    source: "youtube",
    title: v.title || null,
    body,
    snippet,
    url: v.webpage_url,
    author: v.channel,
    published_at: publishedIso,
    engagement,
    metadata: {
      labels: transcript ? ["has-transcript"] : ["no-transcript"],
    },
  };
}

async function mapBoundedParallel<I, O>(
  inputs: I[],
  limit: number,
  fn: (input: I) => Promise<O>,
): Promise<O[]> {
  const results: O[] = new Array(inputs.length);
  let cursor = 0;
  const workers = Array.from(
    { length: Math.min(limit, inputs.length) },
    async () => {
      while (true) {
        const i = cursor++;
        if (i >= inputs.length) return;
        const input = inputs[i] as I;
        results[i] = await fn(input);
      }
    },
  );
  await Promise.all(workers);
  return results;
}
