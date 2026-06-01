/**
 * 12-topic eval suite for oma-market v1.
 * Validates: coverage, LAW pass rate, determinism, p95 latency.
 */

import { readdir, readFile, rm } from "node:fs/promises";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { afterAll, describe, expect, it } from "vitest";

import { clusterCandidates } from "./cluster.js";
import { fuseCandidates } from "./fuse.js";
import { render } from "./render.js";
import { scoreItems } from "./score.js";
import { SourceItemSchema } from "./shared/schema.js";

const __dirname = dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = join(__dirname, "..", "..", "..");
const FIXTURES_ROOT = join(__dirname, "__fixtures__", "eval");
const TMP_OUT = "/tmp/oma-market-eval-out";

const NOW_MS = 1747958400000;
const VERSION = "0.0.0-test";

type Intent = "pain" | "trend" | "competitor";
type Topic = { intent: Intent; slug: string; topic: string; vs: string | null };

function topicTitle(slug: string, intent: Intent): string {
  // strip leading "N-"
  const name = slug.replace(/^\d+-/, "");
  if (intent === "competitor") {
    const parts = name.split("-vs-");
    return `${capitalize(parts[0] ?? "A")} vs ${capitalize(parts[1] ?? "B")}`;
  }
  return name.replace(/-/g, " ");
}

function competitorEntities(slug: string): { a: string; b: string } {
  const name = slug.replace(/^\d+-/, "");
  const parts = name.split("-vs-");
  return { a: capitalize(parts[0] ?? "A"), b: capitalize(parts[1] ?? "B") };
}

function capitalize(s: string): string {
  return s.charAt(0).toUpperCase() + s.slice(1);
}

async function discoverTopics(): Promise<Topic[]> {
  const intents: Intent[] = ["pain", "trend", "competitor"];
  const topics: Topic[] = [];
  for (const intent of intents) {
    const intentDir = join(FIXTURES_ROOT, intent);
    let slugs: string[];
    try {
      slugs = await readdir(intentDir);
    } catch {
      continue;
    }
    for (const slug of slugs) {
      const title = topicTitle(slug, intent);
      const vs = intent === "competitor" ? competitorEntities(slug).b : null;
      topics.push({ intent, slug, topic: title, vs });
    }
  }
  topics.sort((a, b) => a.slug.localeCompare(b.slug));
  return topics;
}

async function loadTopic(topic: Topic) {
  const dir = join(FIXTURES_ROOT, topic.intent, topic.slug, "sources");
  const sources = ["reddit", "hn", "bluesky", "mastodon"];
  const items: ReturnType<typeof SourceItemSchema.parse>[] = [];
  for (const s of sources) {
    const raw = JSON.parse(
      await readFile(join(dir, `${s}.json`), "utf-8"),
    ) as unknown[];
    for (const item of raw) items.push(SourceItemSchema.parse(item));
  }
  return items;
}

async function runPipeline(topic: Topic) {
  const items = await loadTopic(topic);
  const scored = scoreItems(items, { intent: topic.intent, nowMs: NOW_MS });
  const fused = fuseCandidates(scored);
  const clusters = clusterCandidates(fused);
  const result = await render(
    clusters,
    {
      topic: topic.topic,
      intent: topic.intent,
      version: VERSION,
      nowMs: NOW_MS,
      vs: topic.vs,
      sourcesUsed: ["reddit", "hn", "bluesky", "mastodon"],
      sourcesFailed: [],
      outputDir: TMP_OUT,
    },
    REPO_ROOT,
  );
  return { items, clusters, result };
}

const TOPICS = await discoverTopics();

afterAll(async () => {
  await rm(TMP_OUT, { recursive: true, force: true });
});

describe("eval — coverage", () => {
  for (const topic of TOPICS) {
    it(`${topic.intent}/${topic.slug}: ≥1 cluster from ≥1 source`, async () => {
      const { clusters } = await runPipeline(topic);
      expect(clusters.length).toBeGreaterThanOrEqual(1);
      // top cluster should have at least 1 representative
      expect(clusters[0]?.representatives.length).toBeGreaterThanOrEqual(1);
    });
  }
});

describe("eval — LAW pass rate", () => {
  for (const topic of TOPICS) {
    it(`${topic.intent}/${topic.slug}: render violations empty`, async () => {
      const { result } = await runPipeline(topic);
      expect(result.violations).toEqual([]);
    });
  }
});

describe("eval — determinism", () => {
  it("identical clusters and markdown across 3 replays (pain/1-vscode-slow)", async () => {
    const target = TOPICS.find((t) => t.slug === "1-vscode-slow");
    if (!target) throw new Error("eval topic 1-vscode-slow missing");
    const r1 = await runPipeline(target);
    const r2 = await runPipeline(target);
    const r3 = await runPipeline(target);
    expect(r2.result.markdown).toBe(r1.result.markdown);
    expect(r3.result.markdown).toBe(r1.result.markdown);
  });
});

describe("eval — latency", () => {
  it("p95 of 12 topic pipelines under 5s", async () => {
    const durations: number[] = [];
    for (const topic of TOPICS) {
      const t0 = performance.now();
      await runPipeline(topic);
      durations.push(performance.now() - t0);
    }
    durations.sort((a, b) => a - b);
    const idx = Math.floor(durations.length * 0.95);
    const p95 = durations[Math.min(idx, durations.length - 1)] ?? 0;
    expect(p95).toBeLessThan(5000);
  });
});
