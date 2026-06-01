/**
 * Clien (clien.net) public search.
 *
 * `https://www.clien.net/service/search?q={query}&sort=recency&boardCd=&isBoard=false`
 *
 * Search returns HTML. We extract listing rows with regex (no DOM dep) and
 * map to a JSON envelope so downstream consumers receive structured data.
 */

import type { PlatformHandler } from "../../types.js";
import { apiFetch, invalidInputResult } from "./helpers.js";

const CLIEN_HOST = new Set(["www.clien.net", "clien.net"]);
const SEARCH_URL = "https://www.clien.net/service/search";

const ROW_RE =
  /<div[^>]*class="[^"]*list_item[^"]*"[\s\S]*?(?=<div[^>]*class="[^"]*list_item|$)/g;
// Clien search row: <a href="..." class="subject_fixed" data-role="..." title="...">텍스트</a>
const TITLE_RE =
  /<a[^>]*href="([^"]+)"[^>]*class="[^"]*subject_fixed[^"]*"[^>]*title="([^"]+)"/;
// Author lives inside the nickname span; inner span may carry title attr too
const AUTHOR_RE =
  /<span[^>]*class="[^"]*nickname[^"]*"[^>]*>\s*(?:<span[^>]*>)?([^<]+)/;
const DATE_RE = /<span[^>]*class="[^"]*timestamp[^"]*"[^>]*>([^<]+)<\/span>/;
const HIT_RE = /<span[^>]*class="[^"]*hit[^"]*"[^>]*>([^<]+)<\/span>/;
const COMMENT_RE = /<span[^>]*class="[^"]*rSymph05[^"]*"[^>]*>([^<]+)<\/span>/;
// Preview snippet under each row (body-match excerpt)
const PREVIEW_RE =
  /<div[^>]*class="[^"]*preview[^"]*"[^>]*>\s*<span[^>]*>([\s\S]*?)<\/span>/;

interface ClienItem {
  item_id: string;
  url: string;
  title: string;
  snippet: string | null;
  author: string | null;
  posted_at: string | null;
  view_count: number;
  comment_count: number;
}

function decodeEntities(text: string): string {
  return text
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&nbsp;/g, " ");
}

function parseCount(raw: string | undefined): number {
  if (!raw) return 0;
  const s = raw.trim().replace(/,/g, "");
  if (s.endsWith("k")) {
    return Math.round(Number.parseFloat(s) * 1000);
  }
  const n = Number.parseInt(s, 10);
  return Number.isFinite(n) ? n : 0;
}

function parseDate(raw: string | undefined): string | null {
  if (!raw) return null;
  const trimmed = raw.trim();
  // Clien uses YYYY-MM-DD HH:mm or relative ("3시간 전")
  const ymd = /(\d{4})-(\d{2})-(\d{2})\s+(\d{2}):(\d{2})/.exec(trimmed);
  if (ymd) {
    // Treat as KST (UTC+9) since Clien serves KR users
    return `${ymd[1]}-${ymd[2]}-${ymd[3]}T${ymd[4]}:${ymd[5]}:00+09:00`;
  }
  const dateOnly = /(\d{4})-(\d{2})-(\d{2})/.exec(trimmed);
  if (dateOnly) {
    return `${dateOnly[1]}-${dateOnly[2]}-${dateOnly[3]}T00:00:00+09:00`;
  }
  return null;
}

function extractItems(html: string): ClienItem[] {
  const items: ClienItem[] = [];
  const matches = html.match(ROW_RE) ?? [];
  for (const row of matches) {
    let title = "";
    let path = "";

    const m1 = TITLE_RE.exec(row);
    if (m1?.[1] != null && m1[2] != null) {
      path = m1[1];
      title = decodeEntities(m1[2].trim());
    }

    if (!path || !title) continue;

    const url = path.startsWith("http")
      ? path
      : `https://www.clien.net${path.startsWith("/") ? path : `/${path}`}`;

    // Stable id from URL path tail
    const idMatch = /\/(\d+)(?:[/?#]|$)/.exec(url);
    const itemId = idMatch?.[1] ?? url;

    const author = AUTHOR_RE.exec(row)?.[1]?.trim() ?? null;
    const postedAt = parseDate(DATE_RE.exec(row)?.[1]);
    const viewCount = parseCount(HIT_RE.exec(row)?.[1]);
    const commentCount = parseCount(COMMENT_RE.exec(row)?.[1]);
    const previewRaw = PREVIEW_RE.exec(row)?.[1] ?? null;
    const snippet = previewRaw
      ? decodeEntities(previewRaw.replace(/<[^>]+>/g, "").trim()).slice(0, 280)
      : null;

    items.push({
      item_id: `clien:${itemId}`,
      url,
      title,
      snippet,
      author: author ? decodeEntities(author) : null,
      posted_at: postedAt,
      view_count: viewCount,
      comment_count: commentCount,
    });
  }
  return items;
}

export const clien: PlatformHandler = {
  id: "clien",
  match(url) {
    return CLIEN_HOST.has(url.hostname);
  },
  async fetch(url, ctx) {
    return apiFetch({
      platform: "clien",
      url,
      fetchUrl: url.toString(),
      ctx,
      // Clien returns text/html; we leave raw HTML for non-search reads.
      mapBody: (raw) => raw,
    });
  },
  async keywordSearch(query, ctx) {
    if (!query.trim()) {
      return invalidInputResult({
        url: SEARCH_URL,
        platform: "clien",
        reason: "empty query",
      });
    }
    const searchUrl = new URL(SEARCH_URL);
    searchUrl.searchParams.set("q", query);
    searchUrl.searchParams.set("sort", "recency");
    searchUrl.searchParams.set("boardCd", "");
    searchUrl.searchParams.set("isBoard", "false");
    return apiFetch({
      platform: "clien",
      url: searchUrl,
      fetchUrl: searchUrl.toString(),
      ctx,
      mapBody: (raw) =>
        JSON.stringify({ source: "clien", items: extractItems(raw) }),
    });
  },
};
