import { existsSync, readdirSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";
import { registerParser } from "../registry.js";
import type { NormalizedEntry } from "../schema.js";
import {
  findResponse,
  inWindow,
  type PairMessage,
  pathToProjectName,
  preview,
  readJsonlSync,
  streamJsonl,
} from "./shared.js";

const CODEX_DIR = join(homedir(), ".codex");
const HISTORY_PATH = join(CODEX_DIR, "history.jsonl");

interface SessionData {
  project: string;
  responses: Map<string, string>; // promptText → responseSnippet
}

/**
 * Build session_id → { project, responses } from session files.
 * Reads session_meta for cwd and event_msg/response_item for responses.
 */
function loadSessionData(): Map<string, SessionData> {
  const map = new Map<string, SessionData>();

  for (const dir of ["sessions", "archived_sessions"]) {
    const base = join(CODEX_DIR, dir);
    if (!existsSync(base)) continue;
    try {
      scanDir(base, map);
    } catch {
      // ignore
    }
  }

  return map;
}

interface CodexRow {
  type?: string;
  payload?: {
    id?: string;
    cwd?: string;
    role?: string;
    content?: Array<{ type?: string; text?: string }>;
  };
}

function scanDir(dir: string, map: Map<string, SessionData>): void {
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    const full = join(dir, entry.name);
    if (entry.isDirectory()) {
      scanDir(full, map);
    } else if (entry.name.endsWith(".jsonl")) {
      const rows = readJsonlSync<CodexRow>(full);
      const first = rows[0];
      if (first?.type !== "session_meta") continue;

      const sid = first.payload?.id;
      const cwd = first.payload?.cwd;
      if (!sid || !cwd) continue;

      // Collect response_items with user/assistant roles.
      const items: PairMessage[] = [];
      for (const row of rows) {
        if (row.type !== "response_item") continue;
        const p = row.payload;
        if (!p?.role || !p.content) continue;
        if (p.role === "user") {
          const text = p.content
            .filter((c) => c.type === "input_text")
            .map((c) => c.text || "")
            .join(" ")
            .trim();
          if (text && !text.startsWith("<environment_context>")) {
            items.push({ role: "user", text });
          }
        } else if (p.role === "assistant") {
          const text = p.content
            .filter((c) => c.type === "output_text")
            .map((c) => c.text || "")
            .join(" ")
            .trim();
          if (text) items.push({ role: "assistant", text });
        }
      }

      const responses = new Map<string, string>();
      for (let i = 0; i < items.length; i++) {
        const item = items[i];
        if (item?.role !== "user") continue;
        const resp = findResponse(items, i, "first");
        if (resp) responses.set(item.text.slice(0, 100), preview(resp));
      }

      map.set(sid, {
        project: pathToProjectName(cwd) ?? cwd,
        responses,
      });
    }
  }
}

registerParser({
  name: "codex",

  async detect() {
    return existsSync(HISTORY_PATH);
  },

  async parse(start, end) {
    if (!existsSync(HISTORY_PATH)) return [];

    const sessionData = loadSessionData();
    const entries: NormalizedEntry[] = [];

    for await (const row of streamJsonl<{
      ts?: number;
      text?: string;
      session_id?: string;
    }>(HISTORY_PATH)) {
      // Codex uses Unix seconds — convert to ms.
      const ts = (row.ts ?? 0) * 1000;
      if (!inWindow(ts, start, end)) continue;

      const prompt = row.text;
      if (!prompt) continue;

      const sessionId = row.session_id || undefined;
      const data = sessionId ? sessionData.get(sessionId) : undefined;

      // Match response by prompt text prefix.
      const response = data?.responses.get(prompt.slice(0, 100));

      entries.push({
        tool: "codex",
        timestamp: ts,
        project: data?.project,
        prompt,
        response,
        sessionId,
      });
    }

    return entries;
  },
});
