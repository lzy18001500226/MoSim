import { useMemo } from "react";
import type { AutopilotControllerData, AutopilotIterationData } from "@/lib/viewModels/autopilot";
import type { AutopilotThinkingData } from "@/lib/realtime/types";
import { getAutopilotService, parseWasmAny } from "@/lib/wasm-core";
import { useAutopilotStore } from "./autopilot";

type Ctrl = AutopilotControllerData;
const svc = () => getAutopilotService();

export function useAutopilotControllers(): Ctrl[] {
  const tick = useAutopilotStore((s) => s._tick);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  return useMemo(() => JSON.parse(svc().controllers_json()), [tick]);
}

export function useCurrentAutopilotController(): Ctrl | null {
  const tick = useAutopilotStore((s) => s._tick);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  return useMemo(() => parseWasmAny<Ctrl>(svc().current_controller_json()), [tick]);
}

export function useAutopilotIterations(key: string | null | undefined): AutopilotIterationData[] {
  const tick = useAutopilotStore((s) => s._tick);
  return useMemo(() => {
    if (!key) return [];
    return parseWasmAny<AutopilotIterationData[]>(svc().get_iterations_json(key)) ?? [];
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tick, key]);
}

export function useAutopilotThinking(key: string | null | undefined): AutopilotThinkingData | null {
  const tick = useAutopilotStore((s) => s._tick);
  return useMemo(() => {
    if (!key) return null;
    return parseWasmAny<AutopilotThinkingData>(svc().get_thinking_json(key)) ?? null;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tick, key]);
}

export function useAutopilotThinkingHistory(key: string | null | undefined): AutopilotThinkingData[] {
  const tick = useAutopilotStore((s) => s._tick);
  return useMemo(() => {
    if (!key) return [];
    return parseWasmAny<AutopilotThinkingData[]>(svc().get_thinking_history_json(key)) ?? [];
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tick, key]);
}
