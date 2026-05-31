import { createElectronServiceProvider } from "@agentsmesh/electron-adapter";
import {
  registerServiceProvider, markServiceReady, setPlatformInit,
} from "@agentsmesh/service-runtime";

setPlatformInit(async () => {
  const provider = createElectronServiceProvider();
  registerServiceProvider(provider);
  markServiceReady();
});

export function isElectron(): boolean {
  return typeof window !== "undefined" && !!(window as any).electronAPI;
}
