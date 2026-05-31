/**
 * Platform init shim for iOS embed mode.
 *
 * Web's normal startup runs `setPlatformInit(doWasmInit)` from
 * `wasm-core.ts` which boots WASM + registers all 40+ Rust services.
 * The iOS embed page imports THIS module instead — it registers a
 * platform init that:
 *   1. Replaces only `blockstoreService` with the JSON-RPC shim,
 *   2. Leaves every other service as a NOOP_PROXY (the embed page
 *      only renders blocks; channel/ticket/pod services aren't
 *      exercised),
 *   3. Marks the runtime ready so `getBlockstoreService()` resolves
 *      to the RPC implementation.
 */

import {
  markServiceReady, registerServiceProvider, setPlatformInit,
} from "@agentsmesh/service-runtime";
import { RpcBlockstoreService } from "./RpcBlockstoreService";

async function doIosBridgeInit(): Promise<void> {
  registerServiceProvider({
    blockstoreService: new RpcBlockstoreService(),
  });
  markServiceReady();
  if (typeof console !== "undefined") {
    console.log("[iOS embed] platform init complete (RPC bridge)");
  }
}

export function setupIosBridge() {
  setPlatformInit(doIosBridgeInit);
  (window as unknown as { __amEmbedMode: string }).__amEmbedMode = "ios";
}

export { ensurePlatformReady } from "@agentsmesh/service-runtime";
export { primeSubtreeCache } from "./RpcBlockstoreService";
