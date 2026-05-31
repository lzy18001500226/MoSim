type RequestMethod = "GET" | "POST" | "PUT" | "DELETE" | "PATCH";

export interface RequestOptions {
  method?: RequestMethod;
  body?: unknown;
  headers?: Record<string, string>;
  skipAuthRefresh?: boolean;
  signal?: AbortSignal;
}

export interface ApiErrorData {
  error?: string;
  code?: string;
  [key: string]: unknown;
}

export class ApiError extends Error {
  constructor(
    public status: number,
    public statusText: string,
    public data?: unknown
  ) {
    super(`API Error: ${status} ${statusText}`);
    this.name = "ApiError";
  }

  get code(): string | undefined {
    const d = this.data as ApiErrorData | null | undefined;
    return d?.code;
  }

  get serverMessage(): string | undefined {
    const d = this.data as ApiErrorData | null | undefined;
    return d?.error;
  }

  hasCode(code: string): boolean {
    return this.code === code;
  }
}
