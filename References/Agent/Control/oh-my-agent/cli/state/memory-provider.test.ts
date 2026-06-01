import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { createServer, type Server } from "node:http";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, describe, expect, it } from "vitest";
import {
  createAgentMemoryProvider,
  resolveAgentMemoryEndpoint,
} from "./memory-provider.js";

async function startServer(args: {
  version?: string;
  healthStatus?: number;
  observeStatus?: number;
  onObserve?: (body: string) => void;
}): Promise<{ server: Server; url: string }> {
  const server = createServer((req, res) => {
    if (req.url === "/agentmemory/health") {
      res.statusCode = args.healthStatus ?? 200;
      if (args.version) res.setHeader("x-agentmemory-version", args.version);
      res.end("ok");
      return;
    }
    if (req.url === "/agentmemory/observe" && req.method === "POST") {
      let body = "";
      req.setEncoding("utf-8");
      req.on("data", (chunk) => {
        body += chunk;
      });
      req.on("end", () => {
        args.onObserve?.(body);
        res.statusCode = args.observeStatus ?? 200;
        res.end("ok");
      });
      return;
    }
    res.statusCode = 404;
    res.end("not found");
  });

  await new Promise<void>((resolve) => {
    server.listen(0, "127.0.0.1", resolve);
  });
  const address = server.address();
  if (!address || typeof address === "string") {
    throw new Error("expected TCP server address");
  }
  return { server, url: `http://127.0.0.1:${address.port}` };
}

describe("AgentMemory provider", () => {
  const cleanup: Array<() => void> = [];

  afterEach(async () => {
    for (const fn of cleanup.splice(0)) fn();
  });

  it("resolves loopback endpoint.json port unless disabled", () => {
    const homeDir = mkdtempSync(join(tmpdir(), "oma-agentmemory-home-"));
    cleanup.push(() => rmSync(homeDir, { recursive: true, force: true }));
    mkdirSync(join(homeDir, ".agentmemory"), { recursive: true });
    writeFileSync(
      join(homeDir, ".agentmemory", "endpoint.json"),
      JSON.stringify({ port: 3111 }),
      "utf-8",
    );

    expect(resolveAgentMemoryEndpoint({ homeDir, env: {} })).toBe(
      "http://127.0.0.1:3111",
    );
    expect(
      resolveAgentMemoryEndpoint({
        homeDir,
        env: { OMA_NO_AGENTMEMORY: "1" },
      }),
    ).toBeNull();
  });

  it("requires a supported health version before observe", async () => {
    const { server, url } = await startServer({ version: "9.0.0" });
    cleanup.push(() => server.close());
    const provider = createAgentMemoryProvider({
      env: { AGENTMEMORY_URL: url },
    });

    await expect(provider.status()).resolves.toMatchObject({
      provider: "agentmemory",
      reachable: false,
      version: "9.0.0",
    });
    await expect(
      provider.observe({
        sessionId: "oma-test",
        content: "{}\n",
        source: "oma-workflow",
      }),
    ).resolves.toBe(false);
  });

  it("posts observe payload when health is reachable", async () => {
    let observed = "";
    const { server, url } = await startServer({
      version: "0.12.0",
      onObserve: (body) => {
        observed = body;
      },
    });
    cleanup.push(() => server.close());
    const provider = createAgentMemoryProvider({
      env: { AGENTMEMORY_URL: url },
    });

    await expect(
      provider.observe({
        sessionId: "oma-test",
        content: '{"kind":"decision.made"}\n',
        source: "oma-workflow",
      }),
    ).resolves.toBe(true);
    expect(JSON.parse(observed)).toEqual({
      session_id: "oma-test",
      content: '{"kind":"decision.made"}\n',
      source: "oma-workflow",
    });
  });
});
