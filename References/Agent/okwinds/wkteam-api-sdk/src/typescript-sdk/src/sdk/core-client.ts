import { z } from "zod";
import type { WkteamClientConfig, WkteamRequestOptions } from "./config.js";
import {
  WkteamApiBusinessError,
  WkteamHttpError,
  WkteamNetworkError,
  WkteamParseError,
  WkteamTimeoutError,
  WkteamValidationError,
} from "./errors.js";
import { createDefaultLogger } from "./logger.js";
import type { Logger } from "./logger.js";
import { createFetchTransport } from "./transport.js";
import type { Transport } from "./transport.js";

const envelopeSchema = z
  .object({
    code: z.union([z.number(), z.string()]),
    message: z.string().optional(),
    msg: z.string().optional(),
    data: z.unknown().optional(),
  })
  .passthrough();

function normalizeBaseUrl(baseUrl: string): string {
  return baseUrl.endsWith("/") ? baseUrl.slice(0, -1) : baseUrl;
}

function joinUrl(baseUrl: string, path: string): string {
  if (!path.startsWith("/")) return `${baseUrl}/${path}`;
  return `${baseUrl}${path}`;
}

function defaultRequestId(): string {
  return `req_${Math.random().toString(16).slice(2)}_${Date.now()}`;
}

function sleepMs(ms: number): Promise<void> {
  if (ms <= 0) return Promise.resolve();
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function logLevelRank(level: WkteamClientConfig["logLevel"]): number {
  switch (level) {
    case "silent":
      return 0;
    case "error":
      return 1;
    case "warn":
      return 2;
    case "info":
      return 3;
    case "debug":
      return 4;
    default:
      return 3;
  }
}

function shouldLog(
  config: { logLevel: WkteamClientConfig["logLevel"] },
  level: "error" | "warn" | "info" | "debug",
): boolean {
  return logLevelRank(config.logLevel) >= logLevelRank(level);
}

async function resolveAuthorization(config: WkteamClientConfig): Promise<string> {
  const raw =
    typeof config.authorization === "function"
      ? await config.authorization()
      : config.authorization;
  const prefix = config.authorizationPrefix ?? null;
  return prefix ? `${prefix}${raw}` : raw;
}

/**
 * 低层 Core Client：只负责 transport、重试、错误映射、响应解析等通用能力。
 *
 * 由 codegen 生成的 endpoint wrapper（`src/typescript-sdk/src/generated/**`）会依赖本类的 `call()`。
 */
export class WkteamCoreClient {
  protected readonly config: {
    baseUrl: string;
    authorization: WkteamClientConfig["authorization"];
    authorizationHeaderName: string;
    authorizationPrefix: string | null;
    timeoutMs: number;
    retry: {
      enabled: boolean;
      maxAttempts: number;
      backoffMs: number | ((attempt: number) => number);
      retryOn: Array<"network" | "timeout" | "http5xx" | "http429">;
      allowSideEffect: boolean;
    };
    concurrency: number | null;
    logLevel: NonNullable<WkteamClientConfig["logLevel"]>;
    logger: Logger;
    transport: Transport;
    defaultHeaders: Record<string, string>;
    userAgent: string | null;
    hooks: NonNullable<WkteamClientConfig["hooks"]>;
  };
  private readonly semaphore: null | { acquire: () => Promise<() => void> };

  constructor(config: WkteamClientConfig) {
    if (!config.baseUrl) throw new Error("baseUrl 不能为空");
    if (!config.authorization) throw new Error("authorization 不能为空");

    this.config = {
      baseUrl: normalizeBaseUrl(config.baseUrl),
      authorization: config.authorization,
      authorizationHeaderName: config.authorizationHeaderName ?? "Authorization",
      authorizationPrefix: config.authorizationPrefix ?? null,
      timeoutMs: config.timeoutMs ?? 15000,
      retry: {
        enabled: config.retry?.enabled ?? true,
        maxAttempts: config.retry?.maxAttempts ?? 2,
        backoffMs: config.retry?.backoffMs ?? 200,
        retryOn: config.retry?.retryOn ?? ["network", "timeout", "http5xx"],
        allowSideEffect: config.retry?.allowSideEffect ?? false,
      },
      concurrency: config.concurrency ?? null,
      logLevel: config.logLevel ?? "info",
      logger: config.logger ?? createDefaultLogger(),
      transport: config.transport ?? createFetchTransport(),
      defaultHeaders: config.defaultHeaders ?? {},
      userAgent: config.userAgent ?? null,
      hooks: config.hooks ?? {},
    };

    const c = this.config.concurrency;
    this.semaphore =
      typeof c === "number" && Number.isFinite(c) && c > 0 ? createSemaphore(c) : null;
  }

  /**
   * 低层调用入口：按 operationId + method/path 发起请求。
   *
   * @param input - 请求信息（由 codegen wrapper 传入）
   * @returns API envelope 中的 data（成功时）或抛出 SDK 错误
   */
  async call(input: WkteamRequestOptions): Promise<unknown> {
    const requestId = input.options?.requestId ?? defaultRequestId();
    let url = joinUrl(this.config.baseUrl, input.path);

    const headers: Record<string, string> = {
      ...this.config.defaultHeaders,
      ...(input.options?.headers ?? {}),
    };

    if (this.config.userAgent) headers["user-agent"] = this.config.userAgent;
    if (input.requiresAuth) {
      headers[this.config.authorizationHeaderName] = await resolveAuthorization(this.config);
    }

    const isGet = input.method.toUpperCase() === "GET";
    if (isGet && input.params && typeof input.params === "object") {
      const u = new URL(url);
      for (const [key, value] of Object.entries(input.params as Record<string, unknown>)) {
        if (value === undefined || value === null) continue;
        if (Array.isArray(value)) {
          for (const item of value) u.searchParams.append(key, String(item));
        } else if (typeof value === "object") {
          u.searchParams.set(key, JSON.stringify(value));
        } else {
          u.searchParams.set(key, String(value));
        }
      }
      url = u.toString();
    }

    const bodyText = isGet ? undefined : JSON.stringify(input.params ?? {});
    if (bodyText) headers["content-type"] = "application/json";

    const retryCategory =
      input.retryCategory ?? (input.method.toUpperCase() === "GET" ? "safe" : "side_effect");
    const canRetryThisEndpoint = retryCategory === "safe" || this.config.retry.allowSideEffect;
    const maxAttempts = Math.max(1, this.config.retry.maxAttempts);

    for (let attempt = 1; attempt <= maxAttempts; attempt += 1) {
      const startedAt = Date.now();

      this.config.hooks.onRequest?.({
        requestId,
        operationId: input.operationId,
        method: input.method,
        path: input.path,
        attempt,
      });
      if (shouldLog(this.config, "debug")) {
        this.config.logger.debug("wkteam.http.request", {
          requestId,
          operationId: input.operationId,
          method: input.method,
          path: input.path,
          attempt,
        });
      }

      let resp: { status: number; headers: Record<string, string>; bodyText: string };
      let release: null | (() => void) = null;
      try {
        release = this.semaphore ? await this.semaphore.acquire() : null;
        resp = await this.config.transport({
          url,
          method: input.method,
          headers,
          bodyText,
          timeoutMs: input.options?.timeoutMs ?? this.config.timeoutMs,
        });
      } catch (e) {
        const errName =
          typeof e === "object" && e !== null && "name" in e
            ? (e as { name?: unknown }).name
            : undefined;
        const isAbortError = errName === "AbortError";
        const err = isAbortError
          ? new WkteamTimeoutError("请求超时", {
              requestId,
              operationId: input.operationId,
              cause: e,
            })
          : new WkteamNetworkError("网络请求失败", {
              requestId,
              operationId: input.operationId,
              cause: e,
            });

        const reason: "network" | "timeout" = isAbortError ? "timeout" : "network";
        const shouldRetry =
          this.config.retry.enabled &&
          canRetryThisEndpoint &&
          attempt < maxAttempts &&
          this.config.retry.retryOn.includes(reason);

        if (shouldRetry) {
          const backoffMs =
            typeof this.config.retry.backoffMs === "function"
              ? this.config.retry.backoffMs(attempt + 1)
              : this.config.retry.backoffMs;
          this.config.hooks.onRetry?.({
            requestId,
            operationId: input.operationId,
            attempt: attempt + 1,
            reason,
            backoffMs,
          });
          if (shouldLog(this.config, "warn")) {
            this.config.logger.warn("wkteam.http.retry", {
              requestId,
              operationId: input.operationId,
              attempt: attempt + 1,
              reason,
              backoffMs,
            });
          }
          await sleepMs(backoffMs);
          continue;
        }

        this.config.hooks.onError?.({
          requestId,
          operationId: input.operationId,
          errorName: err.name,
          errorKind: isAbortError ? "TimeoutError" : "NetworkError",
        });
        if (shouldLog(this.config, "error")) {
          this.config.logger.error("wkteam.http.error", {
            requestId,
            operationId: input.operationId,
            errorName: err.name,
            errorKind: isAbortError ? "TimeoutError" : "NetworkError",
            attempt,
          });
        }
        throw err;
      } finally {
        release?.();
      }

      if (resp.status < 200 || resp.status >= 300) {
        const err = new WkteamHttpError(`HTTP 请求失败：${resp.status}`, {
          requestId,
          operationId: input.operationId,
          status: resp.status,
          bodyText: resp.bodyText.slice(0, 1024),
        });

        const retryReason: null | "http429" | "http5xx" =
          resp.status === 429 ? "http429" : resp.status >= 500 ? "http5xx" : null;
        const shouldRetry =
          this.config.retry.enabled &&
          canRetryThisEndpoint &&
          attempt < maxAttempts &&
          retryReason !== null &&
          this.config.retry.retryOn.includes(retryReason);

        if (shouldRetry) {
          const reason = retryReason as "http429" | "http5xx";
          const backoffMs =
            typeof this.config.retry.backoffMs === "function"
              ? this.config.retry.backoffMs(attempt + 1)
              : this.config.retry.backoffMs;
          this.config.hooks.onRetry?.({
            requestId,
            operationId: input.operationId,
            attempt: attempt + 1,
            reason,
            backoffMs,
          });
          if (shouldLog(this.config, "warn")) {
            this.config.logger.warn("wkteam.http.retry", {
              requestId,
              operationId: input.operationId,
              attempt: attempt + 1,
              reason,
              backoffMs,
            });
          }
          await sleepMs(backoffMs);
          continue;
        }

        this.config.hooks.onError?.({
          requestId,
          operationId: input.operationId,
          errorName: err.name,
          errorKind: "HttpError",
          httpStatus: resp.status,
        });
        if (shouldLog(this.config, "error")) {
          this.config.logger.error("wkteam.http.error", {
            requestId,
            operationId: input.operationId,
            errorName: err.name,
            errorKind: "HttpError",
            httpStatus: resp.status,
            attempt,
          });
        }
        throw err;
      }

      let json: unknown;
      try {
        json = JSON.parse(resp.bodyText);
      } catch (_e) {
        const err = new WkteamParseError("响应解析失败：非 JSON", {
          requestId,
          operationId: input.operationId,
          bodyTextSnippet: resp.bodyText.slice(0, 256),
        });
        this.config.hooks.onError?.({
          requestId,
          operationId: input.operationId,
          errorName: err.name,
          errorKind: "ParseError",
          httpStatus: resp.status,
        });
        if (shouldLog(this.config, "error")) {
          this.config.logger.error("wkteam.parse.error", {
            requestId,
            operationId: input.operationId,
            errorName: err.name,
            errorKind: "ParseError",
            attempt,
          });
        }
        throw err;
      }

      const parsed = envelopeSchema.safeParse(json);
      if (!parsed.success) {
        const err = new WkteamParseError("响应解析失败：结构不符合预期", {
          requestId,
          operationId: input.operationId,
          bodyTextSnippet: resp.bodyText.slice(0, 256),
        });
        this.config.hooks.onError?.({
          requestId,
          operationId: input.operationId,
          errorName: err.name,
          errorKind: "ParseError",
          httpStatus: resp.status,
        });
        if (shouldLog(this.config, "error")) {
          this.config.logger.error("wkteam.parse.error", {
            requestId,
            operationId: input.operationId,
            errorName: err.name,
            errorKind: "ParseError",
            attempt,
          });
        }
        throw err;
      }

      const envelope = parsed.data;
      const apiCode = typeof envelope.code === "string" ? Number(envelope.code) : envelope.code;
      const apiMessage = envelope.message ?? envelope.msg;

      const durationMs = Date.now() - startedAt;
      this.config.hooks.onResponse?.({
        requestId,
        operationId: input.operationId,
        httpStatus: resp.status,
        durationMs,
        apiCode,
        attempt,
      });
      if (shouldLog(this.config, "debug")) {
        this.config.logger.debug("wkteam.http.response", {
          requestId,
          operationId: input.operationId,
          httpStatus: resp.status,
          durationMs,
          apiCode,
          attempt,
        });
      }

      if (apiCode !== 1000) {
        const err = new WkteamApiBusinessError(`API 业务失败：${apiCode}`, {
          requestId,
          operationId: input.operationId,
          apiCode,
          apiMessage,
          data: envelope.data,
        });
        this.config.hooks.onError?.({
          requestId,
          operationId: input.operationId,
          errorName: err.name,
          errorKind: "ApiBusinessError",
          apiCode,
        });
        if (shouldLog(this.config, "warn")) {
          this.config.logger.warn("wkteam.api.business_error", {
            requestId,
            operationId: input.operationId,
            apiCode,
            attempt,
          });
        }
        throw err;
      }

      return envelope.data;
    }

    throw new WkteamValidationError("重试参数非法：maxAttempts 必须 >= 1", {
      requestId,
      operationId: input.operationId,
    });
  }
}

function createSemaphore(max: number): { acquire: () => Promise<() => void> } {
  let active = 0;
  const queue: Array<() => void> = [];

  const acquire = async () => {
    if (active < max) {
      active += 1;
      return () => {
        active -= 1;
        queue.shift()?.();
      };
    }
    await new Promise<void>((resolve) => queue.push(resolve));
    active += 1;
    return () => {
      active -= 1;
      queue.shift()?.();
    };
  };

  return { acquire };
}
