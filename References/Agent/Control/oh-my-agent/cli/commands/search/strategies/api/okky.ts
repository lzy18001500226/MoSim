/**
 * OKKY (okky.kr) public search.
 *
 * `https://okky.kr/articles?query={query}&sort=recent`
 *
 * Returns HTML. Same regex strategy as Clien.
 */

import type { FetchResult, PlatformHandler } from "../../types.js";
import { impersonateStrategy } from "../impersonate.js";
import { apiFetch, invalidInputResult } from "./helpers.js";

const OKKY_HOST = new Set(["okky.kr", "www.okky.kr"]);
const SEARCH_URL = "https://okky.kr/articles";

// OKKY uses Next.js / React; cards typically have <article> wrappers or
// <div class="article-list-item">. Use loose patterns to be resilient.
const ROW_RE =
  /<(?:article|div)[^>]*class="[^"]*(?:article-list-item|article-card|post-list-row)[^"]*"[\s\S]*?(?=<(?:article|div)[^>]*class="[^"]*(?:article-list-item|article-card|post-list-row)|$)/g;
const ANCHOR_RE = /<a[^>]+href="(\/articles\/[^"]+)"[^>]*>([\s\S]*?)<\/a>/;
const TITLE_TEXT_RE = /<h[1-4][^>]*>([\s\S]*?)<\/h[1-4]>/;
const AUTHOR_RE =
  /<(?:a|span)[^>]*class="[^"]*(?:user|author|nickname)[^"]*"[^>]*>([^<]+)<\/(?:a|span)>/;
const DATE_RE =
  /<(?:time|span)[^>]*class="[^"]*(?:date|time|created)[^"]*"[^>]*(?:datetime="([^"]+)")?[^>]*>([^<]*)</;
const VIEW_RE = /조회\s*[:：]?\s*([0-9,]+)/;
const COMMENT_RE = /(?:댓글|comments?)\s*[:：]?\s*([0-9,]+)/i;

interface OkkyItem {
  item_id: string;
  url: string;
  title: string;
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

function stripTags(html: string): string {
  return decodeEntities(html.replace(/<[^>]+>/g, "")).trim();
}

function parseCount(raw: string | undefined): number {
  if (!raw) return 0;
  const n = Number.parseInt(raw.replace(/,/g, ""), 10);
  return Number.isFinite(n) ? n : 0;
}

function extractItems(html: string): OkkyItem[] {
  const items: OkkyItem[] = [];
  const seenUrls = new Set<string>();
  const matches = html.match(ROW_RE) ?? [];
  for (const row of matches) {
    const anchor = ANCHOR_RE.exec(row);
    if (anchor == null || anchor[1] == null) continue;
    const path = anchor[1];

    // Title preference: <h*> text, else anchor inner text
    let title = "";
    const h = TITLE_TEXT_RE.exec(row);
    if (h?.[1] != null) {
      title = stripTags(h[1]);
    } else if (anchor[2] != null) {
      title = stripTags(anchor[2]);
    }
    if (!title) continue;

    const url = `https://okky.kr${path.startsWith("/") ? path : `/${path}`}`;
    if (seenUrls.has(url)) continue;
    seenUrls.add(url);

    const idMatch = /\/articles\/(\d+)/.exec(url);
    const itemId = idMatch?.[1] ?? url;

    const author = AUTHOR_RE.exec(row)?.[1]?.trim() ?? null;
    const dateMatch = DATE_RE.exec(row);
    const dateRaw = dateMatch?.[1] ?? dateMatch?.[2];
    let postedAt: string | null = null;
    if (dateRaw) {
      const iso = /(\d{4})-(\d{2})-(\d{2})(?:[T ](\d{2}):(\d{2}))?/.exec(
        dateRaw,
      );
      if (iso) {
        const hh = iso[4] ?? "00";
        const mm = iso[5] ?? "00";
        postedAt = `${iso[1]}-${iso[2]}-${iso[3]}T${hh}:${mm}:00+09:00`;
      }
    }
    const viewCount = parseCount(VIEW_RE.exec(row)?.[1]);
    const commentCount = parseCount(COMMENT_RE.exec(row)?.[1]);

    items.push({
      item_id: `okky:${itemId}`,
      url,
      title,
      author,
      posted_at: postedAt,
      view_count: viewCount,
      comment_count: commentCount,
    });
  }
  return items;
}

export const okky: PlatformHandler = {
  id: "okky",
  match(url) {
    return OKKY_HOST.has(url.hostname);
  },
  async fetch(url, ctx) {
    return apiFetch({
      platform: "okky",
      url,
      fetchUrl: url.toString(),
      ctx,
      mapBody: (raw) => raw,
    });
  },
  async keywordSearch(query, ctx) {
    if (!query.trim()) {
      return invalidInputResult({
        url: SEARCH_URL,
        platform: "okky",
        reason: "empty query",
      });
    }
    const searchUrl = new URL(SEARCH_URL);
    searchUrl.searchParams.set("query", query);
    searchUrl.searchParams.set("sort", "recent");

    // First pass: plain apiFetch with browser-ish headers
    const first = await apiFetch({
      platform: "okky",
      url: searchUrl,
      fetchUrl: searchUrl.toString(),
      ctx,
      headers: {
        "User-Agent":
          "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.8",
        Accept:
          "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
      },
      mapBody: (raw) =>
        JSON.stringify({ source: "okky", items: extractItems(raw) }),
    });

    // If Cloudflare returned 403 / blocked, retry via TLS-impersonate strategy.
    // Requires curl_cffi (pip install curl_cffi) — falls through gracefully.
    if (first.status === "blocked" || first.httpStatus === 403) {
      const impersonated = await impersonateStrategy(searchUrl, ctx);
      if (impersonated.status === "ok" && impersonated.content) {
        const envelope = JSON.stringify({
          source: "okky",
          items: extractItems(impersonated.content),
        });
        const result: FetchResult = {
          ...impersonated,
          strategy: "api",
          platform: "okky",
          content: envelope,
        };
        return result;
      }
      // impersonate also failed: surface the more diagnostic message
      return {
        ...first,
        error:
          first.error ??
          impersonated.error ??
          "Cloudflare blocked OKKY; install curl_cffi (pip install curl_cffi) to enable impersonate fallback",
      };
    }
    return first;
  },
};
