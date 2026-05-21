/**
 * SDK 错误基类。
 */
export class WkteamSdkError extends Error {
  public readonly requestId: string;
  public readonly operationId: string;

  constructor(message: string, opts: { requestId: string; operationId: string }) {
    super(message);
    this.name = "WkteamSdkError";
    this.requestId = opts.requestId;
    this.operationId = opts.operationId;
  }
}

/**
 * 参数/配置校验错误（在发起网络请求前失败）。
 */
export class WkteamValidationError extends WkteamSdkError {
  constructor(message: string, opts: { requestId: string; operationId: string }) {
    super(message, opts);
    this.name = "WkteamValidationError";
  }
}

/**
 * 响应解析错误（非 JSON 或结构不符合预期）。
 */
export class WkteamParseError extends WkteamSdkError {
  public readonly bodyTextSnippet?: string;

  constructor(
    message: string,
    opts: { requestId: string; operationId: string; bodyTextSnippet?: string },
  ) {
    super(message, opts);
    this.name = "WkteamParseError";
    this.bodyTextSnippet = opts.bodyTextSnippet;
  }
}

/**
 * 请求超时错误。
 */
export class WkteamTimeoutError extends WkteamSdkError {
  public readonly cause?: unknown;

  constructor(message: string, opts: { requestId: string; operationId: string; cause?: unknown }) {
    super(message, opts);
    this.name = "WkteamTimeoutError";
    this.cause = opts.cause;
  }
}

/**
 * 网络错误（DNS/断连等）。
 */
export class WkteamNetworkError extends WkteamSdkError {
  public readonly cause?: unknown;

  constructor(message: string, opts: { requestId: string; operationId: string; cause?: unknown }) {
    super(message, opts);
    this.name = "WkteamNetworkError";
    this.cause = opts.cause;
  }
}

/**
 * HTTP 非 2xx 错误。
 */
export class WkteamHttpError extends WkteamSdkError {
  public readonly status: number;
  public readonly bodyText?: string;

  constructor(
    message: string,
    opts: { requestId: string; operationId: string; status: number; bodyText?: string },
  ) {
    super(message, opts);
    this.name = "WkteamHttpError";
    this.status = opts.status;
    this.bodyText = opts.bodyText;
  }
}

/**
 * 业务错误（HTTP 成功但 code!=1000）。
 */
export class WkteamApiBusinessError extends WkteamSdkError {
  public readonly apiCode: number;
  public readonly apiMessage?: string;
  public readonly data?: unknown;

  constructor(
    message: string,
    opts: {
      requestId: string;
      operationId: string;
      apiCode: number;
      apiMessage?: string;
      data?: unknown;
    },
  ) {
    super(message, opts);
    this.name = "WkteamApiBusinessError";
    this.apiCode = opts.apiCode;
    this.apiMessage = opts.apiMessage;
    this.data = opts.data;
  }
}
