import { mkdtemp, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import {
  parseVtt,
  readInfoJsons,
  readTranscriptFile,
  toSourceItem,
} from "./youtube.js";

describe("parseVtt", () => {
  it("strips header, timestamps, cue numbers, and inline tags", () => {
    const vtt = [
      "WEBVTT",
      "Kind: captions",
      "Language: en",
      "",
      "1",
      "00:00:00.080 --> 00:00:02.470 align:start position:0%",
      "Anthropic<00:00:00.880><c> has</c><00:00:01.120><c> released</c>",
      "",
      "2",
      "00:00:02.470 --> 00:00:04.560",
      "subagents for Claude Code",
      "",
    ].join("\n");
    const out = parseVtt(vtt);
    expect(out).toBe("Anthropic has released subagents for Claude Code");
  });

  it("dedupes consecutive identical lines (auto-sub smooth-scroll repeats)", () => {
    const vtt = [
      "WEBVTT",
      "",
      "00:00:00.000 --> 00:00:02.000",
      "hello world",
      "",
      "00:00:02.000 --> 00:00:04.000",
      "hello world",
      "",
      "00:00:04.000 --> 00:00:06.000",
      "goodbye world",
    ].join("\n");
    expect(parseVtt(vtt)).toBe("hello world goodbye world");
  });

  it("skips NOTE blocks", () => {
    const vtt = [
      "WEBVTT",
      "",
      "NOTE this is metadata",
      "",
      "00:00:00.000 --> 00:00:02.000",
      "actual content",
    ].join("\n");
    expect(parseVtt(vtt)).toBe("actual content");
  });

  it("returns empty string for empty input", () => {
    expect(parseVtt("")).toBe("");
  });

  it("handles CRLF line endings", () => {
    const vtt = "WEBVTT\r\n\r\n00:00:00.000 --> 00:00:02.000\r\ncrlf line\r\n";
    expect(parseVtt(vtt)).toBe("crlf line");
  });

  it("collapses whitespace inside surviving content", () => {
    const vtt = [
      "WEBVTT",
      "",
      "00:00:00.000 --> 00:00:02.000",
      "spaced   out    text",
    ].join("\n");
    expect(parseVtt(vtt)).toBe("spaced out text");
  });
});

// ---------------------------------------------------------------------------
// Integration: simulate yt-dlp temp-dir output (pre-populated fixture files)
// and exercise the deterministic read+normalize pipeline.
// ---------------------------------------------------------------------------

describe("youtube integration (fixture temp dir)", () => {
  let tempDir: string;

  beforeEach(async () => {
    tempDir = await mkdtemp(join(tmpdir(), "oma-yt-test-"));
  });
  afterEach(async () => {
    await rm(tempDir, { recursive: true, force: true }).catch(() => {});
  });

  async function dropInfo(
    id: string,
    overrides: Record<string, unknown> = {},
  ): Promise<void> {
    const base = {
      id,
      title: `Title for ${id}`,
      channel: `Channel for ${id}`,
      view_count: 1000,
      duration: 300,
      webpage_url: `https://www.youtube.com/watch?v=${id}`,
      upload_date: "20260501",
      like_count: 50,
      comment_count: 10,
      description: `Description for ${id}`,
    };
    await writeFile(
      join(tempDir, `${id}.info.json`),
      JSON.stringify({ ...base, ...overrides }),
      "utf-8",
    );
  }

  async function dropVtt(
    id: string,
    lang: string,
    body: string,
  ): Promise<void> {
    const vtt = `WEBVTT\n\n00:00:00.000 --> 00:00:02.000\n${body}\n`;
    await writeFile(join(tempDir, `${id}.${lang}.vtt`), vtt, "utf-8");
  }

  it("readInfoJsons returns one VideoInfo per video info.json, skipping playlist json", async () => {
    await dropInfo("vid001");
    await dropInfo("vid002");
    // Playlist-level info.json (must be skipped)
    await writeFile(
      join(tempDir, "claude code.info.json"),
      JSON.stringify({ _type: "playlist", entries: [] }),
      "utf-8",
    );

    const videos = await readInfoJsons(tempDir);
    expect(videos).toHaveLength(2);
    const ids = videos.map((v) => v.id).sort();
    expect(ids).toEqual(["vid001", "vid002"]);
    expect(videos[0]?.title).toMatch(/^Title for /);
    expect(videos[0]?.view_count).toBe(1000);
    expect(videos[0]?.upload_date).toBe("20260501");
  });

  it("readInfoJsons returns [] for empty dir", async () => {
    expect(await readInfoJsons(tempDir)).toEqual([]);
  });

  it("readInfoJsons skips malformed json without throwing", async () => {
    await dropInfo("good");
    await writeFile(join(tempDir, "bad.info.json"), "{ not json", "utf-8");
    const videos = await readInfoJsons(tempDir);
    expect(videos).toHaveLength(1);
    expect(videos[0]?.id).toBe("good");
  });

  it("readTranscriptFile parses the VTT matching <id>.<lang>.vtt", async () => {
    await dropVtt("vidA", "en", "first line");
    const t = await readTranscriptFile(tempDir, "vidA", "en");
    expect(t).toBe("first line");
  });

  it("readTranscriptFile returns null when VTT for lang is missing", async () => {
    await dropVtt("vidA", "en", "english only");
    expect(await readTranscriptFile(tempDir, "vidA", "ko")).toBeNull();
  });

  it("toSourceItem prefers transcript over description for body", async () => {
    await dropInfo("vidB", { description: "fallback desc" });
    const videos = await readInfoJsons(tempDir);
    const v = videos[0];
    if (!v) throw new Error("expected one VideoInfo");
    const item = toSourceItem(v, "the actual transcript text");
    expect(item.body).toBe("the actual transcript text");
    expect(item.metadata.labels).toContain("has-transcript");
    expect(item.item_id).toBe("youtube:vidB");
    expect(item.source).toBe("youtube");
    expect(item.url).toBe("https://www.youtube.com/watch?v=vidB");
    expect(item.published_at).toBe("2026-05-01T00:00:00Z");
    expect(item.engagement.view_count).toBe(1000);
    expect(item.engagement.like_count).toBe(50);
    expect(item.engagement.num_comments).toBe(10);
  });

  it("toSourceItem falls back to description when transcript missing", async () => {
    await dropInfo("vidC", { description: "desc only" });
    const [v] = await readInfoJsons(tempDir);
    if (!v) throw new Error("expected one VideoInfo");
    const item = toSourceItem(v, null);
    expect(item.body).toBe("desc only");
    expect(item.metadata.labels).toContain("no-transcript");
  });

  it("toSourceItem uses current ISO when upload_date is missing", async () => {
    await dropInfo("vidD", { upload_date: null });
    const [v] = await readInfoJsons(tempDir);
    if (!v) throw new Error("expected one VideoInfo");
    const item = toSourceItem(v, null);
    // ISO 8601, not the 'YYYY-MM-DDT00:00:00Z' yt-dlp-date form
    expect(item.published_at).toMatch(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/);
  });
});
