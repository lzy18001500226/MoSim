/**
 * Shared schemas for `oma market <subcmd>` pipeline.
 * Single source of truth. Every stage's stdin/stdout JSON must conform.
 */

import { z } from "zod";

// ---------------------------------------------------------------------------
// Enums
// ---------------------------------------------------------------------------

export const IntentSchema = z.enum([
  "pain",
  "trend",
  "competitor",
  "discovery",
]);
export type Intent = z.infer<typeof IntentSchema>;

export const SourceNameSchema = z.enum([
  "reddit",
  "x",
  "hn",
  "bluesky",
  "mastodon",
  "youtube",
  "tiktok",
  "instagram",
  "github",
  "polymarket",
  "grounding",
  "perplexity",
  "clien",
  "okky",
]);
export type SourceName = z.infer<typeof SourceNameSchema>;

export const TrustLevelSchema = z.enum([
  "verified",
  "community",
  "external",
  "unknown",
]);

// ---------------------------------------------------------------------------
// Core item
// ---------------------------------------------------------------------------

export const SourceItemSchema = z.object({
  item_id: z.string(),
  source: SourceNameSchema,
  title: z.string().nullable().optional(),
  body: z.string().nullable().optional(),
  snippet: z.string().nullable().optional(),
  url: z.string(),
  author: z.string().nullable().optional(),
  published_at: z.string(), // ISO 8601
  engagement: z.record(z.string(), z.number()).default({}),
  metadata: z
    .object({
      hashtags: z.array(z.string()).optional(),
      labels: z.array(z.string()).optional(),
    })
    .catchall(z.unknown())
    .default({}),
  trust: z
    .object({
      level: TrustLevelSchema,
      score: z.number().nullable(),
    })
    .optional(),
});
export type SourceItem = z.infer<typeof SourceItemSchema>;

// ---------------------------------------------------------------------------
// Candidate (item + scores)
// ---------------------------------------------------------------------------

export const ScoresSchema = z.object({
  relevance: z.number(),
  freshness: z.number(),
  engagement: z.number(),
  source_quality: z.number(),
  final: z.number(),
});

export const CandidateSchema = SourceItemSchema.extend({
  scores: ScoresSchema.optional(),
  rrf_score: z.number().optional(),
});
export type Candidate = z.infer<typeof CandidateSchema>;

// ---------------------------------------------------------------------------
// Cluster
// ---------------------------------------------------------------------------

export const ClusterSchema = z.object({
  cluster_id: z.string(),
  entity_signature: z.array(z.string()),
  representatives: z.array(CandidateSchema),
  members: z.array(CandidateSchema),
  cross_source_count: z.number().int().nonnegative(),
});
export type Cluster = z.infer<typeof ClusterSchema>;

// ---------------------------------------------------------------------------
// Stage outputs
// ---------------------------------------------------------------------------

export const HarvestOutputSchema = z.object({
  query: z.string(),
  window: z.string(), // e.g., "30d"
  sources_used: z.array(z.string()),
  sources_failed: z.array(z.string()).default([]),
  items: z.array(SourceItemSchema),
});
export type HarvestOutput = z.infer<typeof HarvestOutputSchema>;

export const ScoreOutputSchema = z.object({
  items: z.array(CandidateSchema),
});
export type ScoreOutput = z.infer<typeof ScoreOutputSchema>;

export const FuseOutputSchema = ScoreOutputSchema;
export type FuseOutput = z.infer<typeof FuseOutputSchema>;

export const ClusterOutputSchema = z.object({
  clusters: z.array(ClusterSchema),
  topic: z.string(),
  intent: IntentSchema,
  sources_used: z.array(z.string()),
  sources_failed: z.array(z.string()).default([]),
});
export type ClusterOutput = z.infer<typeof ClusterOutputSchema>;

// ---------------------------------------------------------------------------
// Helper
// ---------------------------------------------------------------------------

export function parseStageInput<T extends z.ZodTypeAny>(
  schema: T,
  input: string,
): z.infer<T> {
  let json: unknown;
  try {
    json = JSON.parse(input);
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    throw new Error(`Invalid JSON on stdin: ${msg}`);
  }
  const parsed = schema.safeParse(json);
  if (!parsed.success) {
    const first = parsed.error.issues[0];
    const path = first?.path.join(".") || "(root)";
    throw new Error(`Schema mismatch at ${path}: ${first?.message}`);
  }
  return parsed.data;
}
