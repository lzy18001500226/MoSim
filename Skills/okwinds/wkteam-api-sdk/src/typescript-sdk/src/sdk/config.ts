import type { Logger } from "./logger.js";
import type { Transport } from "./transport.js";

/**
 * SDK 初始化配置（必须由使用方提供 baseUrl 与 Authorization）。
 *
 * - `baseUrl`：离线文档使用 `http://域名地址/...` 占位，因此必须配置
 * - `authorization`：鉴权私钥（平台后台在线登录/登录接口返回）
 */
export type WkteamClientConfig = {
  baseUrl: string;
  authorization: string | (() => string | Promise<string>);
  authorizationHeaderName?: string;
  authorizationPrefix?: string | null;
  timeoutMs?: number;
  retry?: {
    enabled?: boolean;
    maxAttempts?: number;
    backoffMs?: number | ((attempt: number) => number);
    retryOn?: Array<"network" | "timeout" | "http5xx" | "http429">;
    allowSideEffect?: boolean;
  };
  concurrency?: number | null;
  logLevel?: "silent" | "error" | "warn" | "info" | "debug";
  logger?: Logger;
  transport?: Transport;
  defaultHeaders?: Record<string, string>;
  userAgent?: string | null;
  hooks?: Partial<{
    onRequest: (e: {
      requestId: string;
      operationId: string;
      method: string;
      path: string;
      attempt: number;
    }) => void;
    onResponse: (e: {
      requestId: string;
      operationId: string;
      httpStatus: number;
      durationMs: number;
      apiCode?: number;
      attempt: number;
    }) => void;
    onRetry: (e: {
      requestId: string;
      operationId: string;
      attempt: number;
      reason: string;
      backoffMs: number;
    }) => void;
    onError: (e: {
      requestId: string;
      operationId: string;
      errorName: string;
      errorKind: string;
      httpStatus?: number;
      apiCode?: number;
    }) => void;
  }>;
};

export type EndpointCallOptions = {
  requestId?: string;
  timeoutMs?: number;
  headers?: Record<string, string>;
};

export type WkteamRequestOptions = {
  operationId: string;
  method: string;
  path: string;
  params: unknown;
  requiresAuth: boolean;
  retryCategory?: "safe" | "side_effect";
  options?: EndpointCallOptions;
};
