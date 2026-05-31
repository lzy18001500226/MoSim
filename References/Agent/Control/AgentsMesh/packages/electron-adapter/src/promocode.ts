import { invoke } from "./invoke";
import type { IPromoCodeService } from "@agentsmesh/service-interface";

export class ElectronPromoCodeService implements IPromoCodeService {
  async validatePromoCodeConnect(request: Uint8Array): Promise<Uint8Array> {
    const bytes = await invoke<number[] | Uint8Array>(
      "promocodeValidatePromoCodeConnect", Array.from(request),
    );
    return bytes instanceof Uint8Array ? bytes : new Uint8Array(bytes);
  }

  async redeemPromoCodeConnect(request: Uint8Array): Promise<Uint8Array> {
    const bytes = await invoke<number[] | Uint8Array>(
      "promocodeRedeemPromoCodeConnect", Array.from(request),
    );
    return bytes instanceof Uint8Array ? bytes : new Uint8Array(bytes);
  }

  async getRedemptionHistoryConnect(request: Uint8Array): Promise<Uint8Array> {
    const bytes = await invoke<number[] | Uint8Array>(
      "promocodeGetRedemptionHistoryConnect", Array.from(request),
    );
    return bytes instanceof Uint8Array ? bytes : new Uint8Array(bytes);
  }
}
