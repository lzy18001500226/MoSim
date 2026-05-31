import { invoke } from "./invoke";
import type { IRunnerService } from "@agentsmesh/service-interface";

export class ElectronRunnerService implements IRunnerService {
  private _runnersCache = "[]";
  private _availableRunnersCache = "[]";
  private _currentRunnerCache: string | null = null;

  runners_json(): string { return this._runnersCache; }
  available_runners_json(): string { return this._availableRunnersCache; }
  current_runner_json(): unknown { return this._currentRunnerCache; }

  get_runner_json(id: bigint): unknown {
    const runners = JSON.parse(this._runnersCache) as { id: number }[];
    const r = runners.find(x => x.id === Number(id));
    return r ? JSON.stringify(r) : null;
  }

  set_runners(json: string): void { this._runnersCache = json; }
  set_available_runners(json: string): void { this._availableRunnersCache = json; }
  set_current_runner(json: string): void { this._currentRunnerCache = json || null; }

  update_runner_local(id: number, json: string): void {
    const runners = JSON.parse(this._runnersCache) as { id: number }[];
    const idx = runners.findIndex(x => x.id === id);
    if (idx >= 0) runners[idx] = { ...runners[idx], ...JSON.parse(json) };
    this._runnersCache = JSON.stringify(runners);
  }

  update_runner_status(id: bigint, status: string): void {
    const runners = JSON.parse(this._runnersCache) as { id: number; status?: string }[];
    const r = runners.find(x => x.id === Number(id));
    if (r) r.status = status;
    this._runnersCache = JSON.stringify(runners);
  }

  remove_runner_local(id: bigint): void {
    const runners = JSON.parse(this._runnersCache) as { id: number }[];
    this._runnersCache = JSON.stringify(runners.filter(x => x.id !== Number(id)));
  }

  async fetch_runners(status?: string | null): Promise<string> {
    const result = await invoke<string>("runnerFetchRunners", status);
    const parsed = JSON.parse(result);
    this._runnersCache = JSON.stringify(parsed.runners ?? []);
    return result;
  }

  async fetch_runner(id: bigint): Promise<string> {
    const result = await invoke<string>("runnerFetchRunner", Number(id));
    this._currentRunnerCache = result;
    return result;
  }

  async fetch_available_runners(): Promise<string> {
    const result = await invoke<string>("runnerFetchAvailableRunners");
    const parsed = JSON.parse(result);
    this._availableRunnersCache = JSON.stringify(parsed.runners ?? []);
    return result;
  }

  async create_token(json: string): Promise<string> {
    return invoke<string>("runnerCreateToken", json);
  }

  async fetch_tokens(): Promise<string> {
    return invoke<string>("runnerFetchTokens");
  }

  async delete_token(id: bigint): Promise<void> {
    await invoke<void>("runnerDeleteToken", Number(id));
  }

  async delete_runner(id: bigint): Promise<void> {
    await invoke<void>("runnerDeleteRunner", Number(id));
    this.remove_runner_local(id);
  }

  async update_runner(id: bigint, json: string): Promise<string> {
    const result = await invoke<string>("runnerUpdateRunner", Number(id), json);
    this.update_runner_local(Number(id), result);
    this._currentRunnerCache = result;
    return result;
  }

  async upgrade_runner(id: bigint, json: string): Promise<string> {
    return invoke<string>("runnerUpgradeRunner", Number(id), json);
  }

  async authorize_runner(json: string): Promise<string> {
    return invoke<string>("runnerAuthorizeRunner", json);
  }

  async get_auth_status(authKey: string): Promise<string> {
    return invoke<string>("runnerGetAuthStatus", authKey);
  }

  async list_runner_logs(id: bigint): Promise<string> {
    return invoke<string>("runnerListRunnerLogs", Number(id));
  }

  async list_runner_pods(id: bigint, status?: string | null, limit?: number | null, offset?: number | null): Promise<string> {
    return invoke<string>("runnerListRunnerPods", Number(id), status, limit, offset);
  }

  async query_runner_sandboxes(id: bigint, json: string): Promise<string> {
    return invoke<string>("runnerQueryRunnerSandboxes", Number(id), json);
  }

  async request_log_upload(id: bigint): Promise<void> {
    await invoke<void>("runnerRequestLogUpload", Number(id));
  }
}
