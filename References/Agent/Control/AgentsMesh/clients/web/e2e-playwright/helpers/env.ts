import { readFileSync, existsSync } from "node:fs";
import { resolve } from "node:path";

/**
 * Resolves environment variables for E2E tests.
 *
 * Priority:
 * 1. process.env (CI or explicit overrides)
 * 2. deploy/dev/.env (local dev via dev.sh)
 * 3. Defaults (WEB_PORT=3000, HTTP_PORT=10000)
 */

interface EnvConfig {
  webPort: string;
  httpPort: string;
  postgresPort: string;
  composeProject: string;
}

function findProjectRoot(): string {
  // Walk up from cwd to find the repo root (has deploy/ dir)
  let dir = process.cwd();
  for (let i = 0; i < 5; i++) {
    if (existsSync(resolve(dir, "deploy/dev/.env"))) return dir;
    dir = resolve(dir, "..");
  }
  return process.cwd();
}

function parseEnvFile(): Record<string, string> {
  const envPath = resolve(findProjectRoot(), "deploy/dev/.env");
  if (!existsSync(envPath)) return {};

  const content = readFileSync(envPath, "utf-8");
  const vars: Record<string, string> = {};
  for (const line of content.split("\n")) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) continue;
    const eqIndex = trimmed.indexOf("=");
    if (eqIndex === -1) continue;
    const key = trimmed.slice(0, eqIndex).trim();
    const value = trimmed.slice(eqIndex + 1).trim().replace(/^["']|["']$/g, "");
    vars[key] = value;
  }
  return vars;
}

function getEnvVar(key: string, fallback: string): string {
  if (process.env[key]) return process.env[key]!;
  const fileVars = parseEnvFile();
  return fileVars[key] ?? fallback;
}

function resolveConfig(): EnvConfig {
  return {
    webPort: getEnvVar("WEB_PORT", "3000"),
    httpPort: getEnvVar("HTTP_PORT", "10000"),
    postgresPort: getEnvVar("POSTGRES_PORT", "5432"),
    composeProject: getEnvVar("COMPOSE_PROJECT_NAME", "agentsmesh-dev"),
  };
}

const config = resolveConfig();

export function getWebBaseUrl(): string {
  return `http://localhost:${config.webPort}`;
}

export function getApiBaseUrl(): string {
  return `http://localhost:${config.httpPort}`;
}

export function getPostgresContainer(): string {
  return `${config.composeProject}-postgres-1`;
}

export function getPostgresPort(): number {
  return parseInt(config.postgresPort, 10);
}

export function getComposeProject(): string {
  return config.composeProject;
}

/** Test account credentials (from deploy/dev/seed/seed.sql) */
export const TEST_USER = {
  email: "dev@agentsmesh.local",
  password: "devpass123",
} as const;

export const ADMIN_USER = {
  email: "admin@agentsmesh.local",
  password: "adminpass123",
} as const;

export const TEST_ORG_SLUG = "dev-org";
