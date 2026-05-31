import { invoke } from "./invoke";
import type { IRepositoryService, IRepoState } from "@agentsmesh/service-interface";

// Web's wasm-side `WasmRepositoryService` exposes `<verb>Connect(bytes)`
// methods. RepositoryService in Rust core is a thin proxy (no cache, no
// business logic — see ADR 2026-05-24-service-binding-matrix.md "Decision
// 1: thin-proxy services don't require binding symmetry"). Desktop renderer
// reaches the backend through `connectCall` generic IPC proxy (main owns
// the auth header injection + URL prefix) — adding a dedicated napi binding
// would be form symmetry without functional gain, so we go directly to the
// backend Connect endpoint through main process.
async function connectCall(method: string, request: Uint8Array): Promise<Uint8Array> {
  const resp = await invoke<number[] | Uint8Array>(
    "connectCall",
    "proto.repository.v1.RepositoryService",
    method,
    Array.from(request),
  );
  return resp instanceof Uint8Array ? resp : new Uint8Array(resp);
}

// Service-is-State-superset 模式（对齐 ElectronPodService）：内部 cache 由 Service 持有，
// provider 让 repoState 别名同一实例，renderer 端 useRepositories() 读到的就是这里的 cache。
export class ElectronRepositoryService implements IRepositoryService, IRepoState {
  private _repositoriesCache = "[]";
  private _currentRepoCache: string | null = null;
  private _branchesCache = "[]";

  // ===== IRepoState =====

  repositories_json(): string { return this._repositoriesCache; }
  current_repo_json(): unknown { return this._currentRepoCache; }
  branches_json(): string { return this._branchesCache; }

  set_repositories(json: string): void { this._repositoriesCache = json || "[]"; }
  set_current_repo(json: string): void { this._currentRepoCache = json || null; }
  set_branches(json: string): void { this._branchesCache = json || "[]"; }

  add_repository(json: string): void {
    const repo = JSON.parse(json) as { id: number };
    const repos = JSON.parse(this._repositoriesCache) as { id: number }[];
    repos.push(repo);
    this._repositoriesCache = JSON.stringify(repos);
  }

  update_repository(id: string, json: string): void {
    const updated = JSON.parse(json) as { id: number };
    const repos = JSON.parse(this._repositoriesCache) as { id: number }[];
    const idx = repos.findIndex(r => String(r.id) === id);
    if (idx >= 0) repos[idx] = updated;
    this._repositoriesCache = JSON.stringify(repos);
  }

  remove_repository(id: string): void {
    const repos = JSON.parse(this._repositoriesCache) as { id: number }[];
    this._repositoriesCache = JSON.stringify(repos.filter(r => String(r.id) !== id));
  }

  // ===== IRepositoryService =====

  async list(): Promise<string> {
    return invoke<string>("repositoryList");
  }

  async get(id: bigint): Promise<string> {
    return invoke<string>("repositoryGet", Number(id));
  }

  async create(json: string): Promise<string> {
    return invoke<string>("repositoryCreate", json);
  }

  async update(id: bigint, json: string): Promise<string> {
    return invoke<string>("repositoryUpdate", Number(id), json);
  }

  async delete(id: bigint): Promise<void> {
    await invoke<void>("repositoryDelete", Number(id));
  }

  async list_branches(id: bigint): Promise<string> {
    return invoke<string>("repositoryListBranches", Number(id));
  }

  async sync_branches(id: bigint, json: string): Promise<string> {
    return invoke<string>("repositorySyncBranches", Number(id), json);
  }

  async list_merge_requests(id: bigint, branch?: string | null, state?: string | null): Promise<string> {
    return invoke<string>("repositoryListMergeRequests", Number(id), branch, state);
  }

  async register_webhook(id: bigint): Promise<void> {
    await invoke<void>("repositoryRegisterWebhook", Number(id));
  }

  async delete_webhook(id: bigint): Promise<void> {
    await invoke<void>("repositoryDeleteWebhook", Number(id));
  }

  async get_webhook_secret(id: bigint): Promise<string> {
    return invoke<string>("repositoryGetWebhookSecret", Number(id));
  }

  async get_webhook_status(id: bigint): Promise<string> {
    return invoke<string>("repositoryGetWebhookStatus", Number(id));
  }

  async mark_webhook_configured(id: bigint): Promise<void> {
    await invoke<void>("repositoryMarkWebhookConfigured", Number(id));
  }

  // ── Connect-RPC binary surface (mirrors WasmRepositoryService) ──

  listRepositoriesConnect(request: Uint8Array): Promise<Uint8Array> {
    return connectCall("ListRepositories", request);
  }
  getRepositoryConnect(request: Uint8Array): Promise<Uint8Array> {
    return connectCall("GetRepository", request);
  }
  createRepositoryConnect(request: Uint8Array): Promise<Uint8Array> {
    return connectCall("CreateRepository", request);
  }
  updateRepositoryConnect(request: Uint8Array): Promise<Uint8Array> {
    return connectCall("UpdateRepository", request);
  }
  deleteRepositoryConnect(request: Uint8Array): Promise<Uint8Array> {
    return connectCall("DeleteRepository", request);
  }
  listRepositoryBranchesConnect(request: Uint8Array): Promise<Uint8Array> {
    return connectCall("ListRepositoryBranches", request);
  }
  syncRepositoryBranchesConnect(request: Uint8Array): Promise<Uint8Array> {
    return connectCall("SyncRepositoryBranches", request);
  }
  listRepositoryMergeRequestsConnect(request: Uint8Array): Promise<Uint8Array> {
    return connectCall("ListRepositoryMergeRequests", request);
  }
  registerRepositoryWebhookConnect(request: Uint8Array): Promise<Uint8Array> {
    return connectCall("RegisterRepositoryWebhook", request);
  }
  deleteRepositoryWebhookConnect(request: Uint8Array): Promise<Uint8Array> {
    return connectCall("DeleteRepositoryWebhook", request);
  }
  getRepositoryWebhookStatusConnect(request: Uint8Array): Promise<Uint8Array> {
    return connectCall("GetRepositoryWebhookStatus", request);
  }
  getRepositoryWebhookSecretConnect(request: Uint8Array): Promise<Uint8Array> {
    return connectCall("GetRepositoryWebhookSecret", request);
  }
  markRepositoryWebhookConfiguredConnect(request: Uint8Array): Promise<Uint8Array> {
    return connectCall("MarkRepositoryWebhookConfigured", request);
  }
}
