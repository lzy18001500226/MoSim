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
  streamJsonl,
} from "./shared.js";

const QWEN_BASE = join(homedir(), ".qwen", "projects");

function findChatFiles(): string[] {
  if (!existsSync(QWEN_BASE)) return [];

  const files: string[] = [];
  try {
    for (const projectDir of readdirSync(QWEN_BASE)) {
      const chatsDir = join(QWEN_BASE, projectDir, "chats");
      if (!existsSync(chatsDir)) continue;
      for (const file of readdirSync(chatsDir)) {
        if (file.endsWith(".jsonl")) {
          files.push(join(chatsDir, file));
        }
      }
    }
  } catch {
    // ignore permission errors
  }
  return files;
}

interface QwenRow {
  type?: string;
  timestamp?: string;
  message?: { parts?: Array<{ text?: string }> };
  cwd?: string;
  sessionId?: string;
  gitBranch?: string;
}

function rowText(row: QwenRow): string {
  return (row.message?.parts || [])
    .map((p) => p.text || "")
    .filter(Boolean)
    .join(" ");
}

registerParser({
  name: "qwen",

  async detect() {
    return existsSync(QWEN_BASE);
  },

  async parse(start, end) {
    const files = findChatFiles();
    if (files.length === 0) return [];

    const entries: NormalizedEntry[] = [];

    for (const file of files) {
      // Collect user/assistant messages first for user→assistant pairing.
      const msgs: QwenRow[] = [];
      for await (const row of streamJsonl<QwenRow>(file)) {
        if (row.type === "user" || row.type === "assistant") msgs.push(row);
      }

      const pairs: PairMessage[] = msgs.map((row) => ({
        role: row.type === "user" ? "user" : "assistant",
        text: rowText(row),
      }));

      for (let i = 0; i < msgs.length; i++) {
        const row = msgs[i];
        if (!row || row.type !== "user") continue;

        const ts = row.timestamp ? new Date(row.timestamp).getTime() : 0;
        if (!inWindow(ts, start, end)) continue;

        const text = rowText(row);
        if (!text) continue;

        const response = findResponse(pairs, i, "immediate");

        entries.push({
          tool: "qwen",
          timestamp: ts,
          project: pathToProjectName(row.cwd),
          prompt: text,
          response: response ? preview(response) : undefined,
          sessionId: row.sessionId || undefined,
          metadata: {
            gitBranch: row.gitBranch || undefined,
          },
        });
      }
    }

    return entries;
  },
});
