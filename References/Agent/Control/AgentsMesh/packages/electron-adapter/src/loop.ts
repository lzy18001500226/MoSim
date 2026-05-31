import { invoke } from "./invoke";
import type { ILoopService } from "@agentsmesh/service-interface";

export class ElectronLoopService implements ILoopService {
  private _loopsCache = "[]";
  private _runsCache = "[]";
  private _currentLoopCache: string | null = null;

  loops_json(): string { return this._loopsCache; }
  runs_json(): string { return this._runsCache; }
  current_loop_json(): unknown { return this._currentLoopCache; }

  get_loop_by_slug_json(slug: string): unknown {
    const loops = JSON.parse(this._loopsCache) as { slug: string }[];
    const l = loops.find(x => x.slug === slug);
    return l ? JSON.stringify(l) : null;
  }

  set_loops(json: string): void { this._loopsCache = json; }
  set_runs(json: string): void { this._runsCache = json; }
  set_current_loop(json: string): void { this._currentLoopCache = json || null; }

  add_run(json: string): void {
    const runs = JSON.parse(this._runsCache) as unknown[];
    runs.push(JSON.parse(json));
    this._runsCache = JSON.stringify(runs);
  }

  append_runs(json: string): void {
    const existing = JSON.parse(this._runsCache) as unknown[];
    const newer = JSON.parse(json) as unknown[];
    this._runsCache = JSON.stringify([...existing, ...newer]);
  }

  clear_runs(): void { this._runsCache = "[]"; }

  update_loop_local(slug: string, json: string): void {
    const loops = JSON.parse(this._loopsCache) as { slug: string }[];
    const idx = loops.findIndex(x => x.slug === slug);
    if (idx >= 0) loops[idx] = { ...loops[idx], ...JSON.parse(json) };
    this._loopsCache = JSON.stringify(loops);
  }

  update_run_status(runId: bigint, status: string): void {
    const runs = JSON.parse(this._runsCache) as { id: number; status?: string }[];
    const r = runs.find(x => x.id === Number(runId));
    if (r) r.status = status;
    this._runsCache = JSON.stringify(runs);
  }

  async fetch_loops(status?: string | null, limit?: number | null, offset?: number | null): Promise<string> {
    const result = await invoke<string>("loopSvcFetchLoops", status, limit, offset);
    const parsed = JSON.parse(result);
    this._loopsCache = JSON.stringify(parsed.loops ?? []);
    return result;
  }

  async fetch_loop(slug: string): Promise<string> {
    const result = await invoke<string>("loopSvcFetchLoop", slug);
    this._currentLoopCache = result;
    return result;
  }

  async fetch_runs(slug: string, status?: string | null, limit?: number | null, offset?: number | null): Promise<string> {
    const result = await invoke<string>("loopSvcFetchRuns", slug, status, limit, offset);
    const parsed = JSON.parse(result);
    this._runsCache = JSON.stringify(parsed.runs ?? []);
    return result;
  }

  async create_loop(json: string): Promise<string> {
    const result = await invoke<string>("loopSvcCreateLoop", json);
    const loops = JSON.parse(this._loopsCache) as unknown[];
    loops.push(JSON.parse(result));
    this._loopsCache = JSON.stringify(loops);
    this._currentLoopCache = result;
    return result;
  }

  async update_loop(slug: string, json: string): Promise<string> {
    const result = await invoke<string>("loopSvcUpdateLoop", slug, json);
    this.update_loop_local(slug, result);
    this._currentLoopCache = result;
    return result;
  }

  async delete_loop(slug: string): Promise<void> {
    await invoke<void>("loopSvcDeleteLoop", slug);
    const loops = JSON.parse(this._loopsCache) as { slug: string }[];
    this._loopsCache = JSON.stringify(loops.filter(x => x.slug !== slug));
  }

  async enable_loop(slug: string): Promise<string> {
    const result = await invoke<string>("loopSvcEnableLoop", slug);
    this.update_loop_local(slug, result);
    this._currentLoopCache = result;
    return result;
  }

  async disable_loop(slug: string): Promise<string> {
    const result = await invoke<string>("loopSvcDisableLoop", slug);
    this.update_loop_local(slug, result);
    this._currentLoopCache = result;
    return result;
  }

  async trigger_loop(slug: string): Promise<string> {
    const result = await invoke<string>("loopSvcTriggerLoop", slug);
    this.update_loop_local(slug, result);
    this._currentLoopCache = result;
    return result;
  }

  async cancel_run(slug: string, runId: bigint): Promise<void> {
    await invoke<void>("loopSvcCancelRun", slug, Number(runId));
    this.update_run_status(runId, "cancelled");
  }

  async fetch_iterations(key: string): Promise<string> {
    return invoke<string>("loopSvcFetchIterations", key);
  }
}
