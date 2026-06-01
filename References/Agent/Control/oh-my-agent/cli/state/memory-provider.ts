import { existsSync, readFileSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";
import { http } from "../io/http.js";
import type {
  AgentMemoryProviderOptions,
  MemoryProvider,
  MemoryProviderStatus,
} from "../types/memory.js";

const SUPPORTED_AGENTMEMORY_VERSION = /^0\.(1[12])\./;

function headerValue(value: string | string[] | undefined): string | undefined {
  if (Array.isArray(value)) return value[0];
  return value;
}

export function resolveAgentMemoryEndpoint(options: {
  env?: NodeJS.ProcessEnv;
  homeDir?: string;
}): string | null {
  const env = options.env ?? process.env;
  if (env.OMA_NO_AGENTMEMORY === "1") return null;
  if (env.AGENTMEMORY_URL) return env.AGENTMEMORY_URL;

  const endpointPath = join(
    options.homeDir ?? homedir(),
    ".agentmemory",
    "endpoint.json",
  );
  if (!existsSync(endpointPath)) return null;

  try {
    const cfg = JSON.parse(readFileSync(endpointPath, "utf-8")) as {
      port?: number;
      url?: string;
      socket?: string;
    };
    if (typeof cfg.port === "number") return `http://127.0.0.1:${cfg.port}`;
    if (typeof cfg.url === "string" && cfg.url.trim()) return cfg.url;
    return null;
  } catch {
    return null;
  }
}

export function createNoneMemoryProvider(): MemoryProvider {
  return {
    name: "none",
    async status() {
      return {
        provider: "none",
        reachable: false,
        reason: "disabled",
      };
    },
    async observe() {
      return false;
    },
  };
}

export function createAgentMemoryProvider(
  options: AgentMemoryProviderOptions = {},
): MemoryProvider {
  const env = options.env ?? process.env;
  let cachedStatus: MemoryProviderStatus | null = null;

  async function status(): Promise<MemoryProviderStatus> {
    if (cachedStatus) return cachedStatus;
    if (env.OMA_NO_AGENTMEMORY === "1") {
      cachedStatus = {
        provider: "agentmemory",
        reachable: false,
        reason: "disabled by OMA_NO_AGENTMEMORY",
      };
      return cachedStatus;
    }

    const endpoint = resolveAgentMemoryEndpoint({
      env,
      homeDir: options.homeDir,
    });
    if (!endpoint) {
      cachedStatus = {
        provider: "agentmemory",
        reachable: false,
        reason: "endpoint not configured",
      };
      return cachedStatus;
    }

    try {
      const response = await http.get(`${endpoint}/agentmemory/health`, {
        timeout: options.healthTimeoutMs ?? 500,
        validateStatus: () => true,
      });
      const version = headerValue(response.headers["x-agentmemory-version"]);
      if (response.status < 200 || response.status >= 300) {
        cachedStatus = {
          provider: "agentmemory",
          endpoint,
          reachable: false,
          version,
          reason: `health returned ${response.status}`,
        };
        return cachedStatus;
      }
      if (!version || !SUPPORTED_AGENTMEMORY_VERSION.test(version)) {
        cachedStatus = {
          provider: "agentmemory",
          endpoint,
          reachable: false,
          version,
          reason: `unsupported version ${version ?? "(missing)"}`,
        };
        return cachedStatus;
      }
      cachedStatus = {
        provider: "agentmemory",
        endpoint,
        reachable: true,
        version,
      };
      return cachedStatus;
    } catch (error) {
      cachedStatus = {
        provider: "agentmemory",
        endpoint,
        reachable: false,
        reason: error instanceof Error ? error.message : String(error),
      };
      return cachedStatus;
    }
  }

  return {
    name: "agentmemory",
    status,
    async observe(payload) {
      const current = await status();
      if (!current.reachable || !current.endpoint) return false;
      try {
        const response = await http.post(
          `${current.endpoint}/agentmemory/observe`,
          {
            session_id: payload.sessionId,
            content: payload.content,
            source: payload.source,
          },
          {
            headers: { "content-type": "application/json" },
            timeout: options.observeTimeoutMs ?? 500,
            validateStatus: () => true,
          },
        );
        return response.status >= 200 && response.status < 300;
      } catch {
        return false;
      }
    },
  };
}
