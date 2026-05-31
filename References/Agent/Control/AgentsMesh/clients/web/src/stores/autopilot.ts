import { create } from "zustand";
import type {
  AutopilotControllerData, AutopilotIterationData,
  CreateAutopilotControllerRequest, ApproveRequest,
} from "@/lib/viewModels/autopilot";
import { AutopilotThinkingData } from "@/lib/realtime/types";
import { reconnectRegistry } from "@/lib/realtime";
import { getErrorMessage } from "@/lib/utils";
import { getAutopilotService, parseWasmAny } from "@/lib/wasm-core";
import { readCurrentOrg } from "@/stores/auth";
import {
  listAutopilots as listAutopilotsConnect,
  getAutopilot as getAutopilotConnect,
  createAutopilot as createAutopilotConnect,
  pauseAutopilot as pauseAutopilotConnect,
  resumeAutopilot as resumeAutopilotConnect,
  stopAutopilot as stopAutopilotConnect,
  approveAutopilot as approveAutopilotConnect,
  takeoverAutopilot as takeoverAutopilotConnect,
  handbackAutopilot as handbackAutopilotConnect,
  getAutopilotIterations as getAutopilotIterationsConnect,
  type AutopilotControllerWire,
  type AutopilotIterationWire,
} from "@/lib/api/facade/autopilotConnect";

export type AutopilotController = AutopilotControllerData;
export type AutopilotIteration = AutopilotIterationData;
export type AutopilotThinking = AutopilotThinkingData;
export type { CreateAutopilotControllerRequest, ApproveRequest };
export {
  useAutopilotControllers, useCurrentAutopilotController,
  useAutopilotIterations, useAutopilotThinking, useAutopilotThinkingHistory,
} from "./autopilotSelectors";

type Ctrl = AutopilotController;
const ACTIVE = ["initializing", "running", "paused", "user_takeover", "waiting_approval"];
const svc = () => getAutopilotService();
const bump = () => useAutopilotStore.setState((s) => ({ _tick: s._tick + 1 }));
const slug = () => readCurrentOrg()?.slug ?? "";

// Proto AutopilotIteration drops legacy fields. Map back to the renderer-
// facing shape: iteration_number→iteration, status→phase, result→summary.
function fromWireIteration(w: AutopilotIterationWire): AutopilotIterationData {
  return {
    id: w.id, autopilot_controller_id: 0,
    iteration: w.iteration_number, phase: w.status, summary: w.result,
    created_at: w.started_at ?? "",
  };
}

// AutopilotControllerWire and AutopilotControllerData are JSON-compatible
// (snake_case + number). Union-type strictness needs an unknown bridge.
const fromWireCtrl = (w: AutopilotControllerWire): Ctrl => w as unknown as Ctrl;

function patchCtrl(key: string, patch: Partial<Ctrl> | ((c: Ctrl) => Partial<Ctrl>)) {
  const ctrls: Ctrl[] = JSON.parse(svc().controllers_json());
  const target = ctrls.find((c) => c.autopilot_controller_key === key);
  if (!target) return;
  const next = { ...target, ...(typeof patch === "function" ? patch(target) : patch) };
  svc().update_controller(key, JSON.stringify(next));
}

interface AutopilotState { _tick: number; loading: boolean; error: string | null; }
interface AutopilotActions {
  fetchAutopilotControllers: () => Promise<void>;
  fetchAutopilotController: (key: string) => Promise<void>;
  createAutopilotController: (data: CreateAutopilotControllerRequest) => Promise<Ctrl>;
  pauseAutopilotController: (key: string) => Promise<void>;
  resumeAutopilotController: (key: string) => Promise<void>;
  stopAutopilotController: (key: string) => Promise<void>;
  approveAutopilotController: (key: string, data?: ApproveRequest) => Promise<void>;
  takeoverAutopilotController: (key: string) => Promise<void>;
  handbackAutopilotController: (key: string) => Promise<void>;
  fetchIterations: (key: string) => Promise<void>;
  updateAutopilotControllerStatus: (key: string, phase: string, cur: number, max: number, cbState: string, cbReason?: string) => void;
  addIteration: (key: string, iteration: AutopilotIteration) => void;
  updateThinking: (key: string, thinking: AutopilotThinking) => void;
  setCurrentAutopilotController: (c: Ctrl | null) => void;
  removeAutopilotController: (key: string) => void;
  clearError: () => void;
  getAutopilotControllerByPodKey: (podKey: string) => Ctrl | undefined;
}

export const useAutopilotStore = create<AutopilotState & AutopilotActions>((set, get) => {
  const action = (
    fn: (s: string, k: string) => Promise<unknown>, msg: string,
    patch: Partial<Ctrl> | ((c: Ctrl) => Partial<Ctrl>),
  ) => async (key: string) => {
    try { await fn(slug(), key); patchCtrl(key, patch); bump(); }
    catch (e) { set({ error: getErrorMessage(e, msg) }); }
  };

  return {
  _tick: 0, loading: false, error: null,

  fetchAutopilotControllers: async () => {
    set({ loading: true, error: null });
    try {
      const items = await listAutopilotsConnect(slug());
      svc().set_controllers(JSON.stringify(items.map(fromWireCtrl)));
      set({ loading: false, _tick: get()._tick + 1 });
    } catch (e) { set({ error: getErrorMessage(e, "Failed to fetch controllers"), loading: false }); }
  },

  fetchAutopilotController: async (key) => {
    try {
      const ctrl = fromWireCtrl(await getAutopilotConnect(slug(), key));
      svc().add_controller(JSON.stringify(ctrl));
      svc().set_current_controller(JSON.stringify(ctrl));
      bump();
    } catch (e) { set({ error: getErrorMessage(e, "Failed to fetch controller") }); }
  },

  createAutopilotController: async (data) => {
    try {
      const ctrl = fromWireCtrl(await createAutopilotConnect({
        orgSlug: slug(), podKey: data.pod_key, prompt: data.prompt,
        maxIterations: data.max_iterations, iterationTimeoutSec: data.iteration_timeout_sec,
        noProgressThreshold: data.no_progress_threshold, sameErrorThreshold: data.same_error_threshold,
        approvalTimeoutMin: data.approval_timeout_min, controlAgentSlug: data.control_agent_slug,
        controlPromptTemplate: data.control_prompt_template, mcpConfigJson: data.mcp_config_json,
      }));
      svc().add_controller(JSON.stringify(ctrl));
      svc().set_current_controller(JSON.stringify(ctrl));
      bump();
      return ctrl;
    } catch (e) { set({ error: getErrorMessage(e, "Failed to create") }); throw e; }
  },

  pauseAutopilotController: action(pauseAutopilotConnect, "Failed to pause", { phase: "paused" }),
  resumeAutopilotController: action(resumeAutopilotConnect, "Failed to resume", { phase: "running" }),
  stopAutopilotController: action(stopAutopilotConnect, "Failed to stop", { phase: "stopped" }),
  takeoverAutopilotController: action(takeoverAutopilotConnect, "Failed to takeover", { phase: "user_takeover", user_takeover: true }),
  handbackAutopilotController: action(handbackAutopilotConnect, "Failed to handback", { phase: "running", user_takeover: false }),

  approveAutopilotController: async (key, data) => {
    try {
      await approveAutopilotConnect(slug(), key, data?.continue_execution, data?.additional_iterations);
      patchCtrl(key, (c) => ({
        phase: data?.continue_execution === false ? "stopped" : "running",
        max_iterations: data?.additional_iterations ? c.max_iterations + data.additional_iterations : c.max_iterations,
      }));
      bump();
    } catch (e) { set({ error: getErrorMessage(e, "Failed to approve") }); }
  },

  fetchIterations: async (key) => {
    try {
      const items = await getAutopilotIterationsConnect(slug(), key);
      svc().set_iterations(key, JSON.stringify(items.map(fromWireIteration)));
      bump();
    } catch (e) { set({ error: getErrorMessage(e, "Failed to fetch iterations") }); }
  },

  updateAutopilotControllerStatus: (key, phase, cur, max, cbState, cbReason) => {
    patchCtrl(key, {
      phase: phase as Ctrl["phase"], current_iteration: cur, max_iterations: max,
      circuit_breaker: { state: cbState as Ctrl["circuit_breaker"]["state"], reason: cbReason },
    });
    bump();
  },

  addIteration: (key, iter) => { svc().add_iteration(key, JSON.stringify(iter)); bump(); },
  updateThinking: (key, t) => { svc().update_thinking(key, JSON.stringify(t)); bump(); },
  setCurrentAutopilotController: (c) => { svc().set_current_controller(c ? JSON.stringify(c) : ""); bump(); },
  removeAutopilotController: (key) => { svc().remove_controller(key); bump(); },
  clearError: () => set({ error: null }),

  getAutopilotControllerByPodKey: (podKey) => {
    const val = parseWasmAny<Ctrl>(svc().get_controller_by_pod_key_json(podKey));
    return val && ACTIVE.includes(val.phase) ? val : undefined;
  },
  };
});

reconnectRegistry.register({
  name: "autopilot:controllers",
  fn: () => useAutopilotStore.getState().fetchAutopilotControllers?.(),
  priority: "low",
});
