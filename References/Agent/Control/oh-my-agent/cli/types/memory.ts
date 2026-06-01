export interface MemoryObservePayload {
  sessionId: string;
  content: string;
  source: string;
}

export interface MemoryProviderStatus {
  provider: "agentmemory" | "none";
  reachable: boolean;
  endpoint?: string;
  version?: string;
  reason?: string;
}

export interface MemoryProvider {
  name: "agentmemory" | "none";
  status(): Promise<MemoryProviderStatus>;
  observe(payload: MemoryObservePayload): Promise<boolean>;
}

export interface AgentMemoryProviderOptions {
  env?: NodeJS.ProcessEnv;
  homeDir?: string;
  healthTimeoutMs?: number;
  observeTimeoutMs?: number;
}
