import { invoke } from "./invoke";
import type { ISSOService } from "@agentsmesh/service-interface";

export class ElectronSSOService implements ISSOService {
  async discoverConnect(request: Uint8Array): Promise<Uint8Array> {
    const bytes = await invoke<number[] | Uint8Array>(
      "ssoDiscoverConnect", Array.from(request),
    );
    return bytes instanceof Uint8Array ? bytes : new Uint8Array(bytes);
  }

  async ldapAuthConnect(request: Uint8Array): Promise<Uint8Array> {
    const bytes = await invoke<number[] | Uint8Array>(
      "ssoLdapAuthConnect", Array.from(request),
    );
    return bytes instanceof Uint8Array ? bytes : new Uint8Array(bytes);
  }
}
