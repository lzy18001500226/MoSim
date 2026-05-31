import { invoke } from "./invoke";
import type { IInvitationConnectService } from "@agentsmesh/service-interface";

export class ElectronInvitationConnectService implements IInvitationConnectService {
  async listInvitationsConnect(request: Uint8Array): Promise<Uint8Array> {
    const bytes = await invoke<number[] | Uint8Array>(
      "invitationListInvitationsConnect", Array.from(request),
    );
    return bytes instanceof Uint8Array ? bytes : new Uint8Array(bytes);
  }

  async createInvitationConnect(request: Uint8Array): Promise<Uint8Array> {
    const bytes = await invoke<number[] | Uint8Array>(
      "invitationCreateInvitationConnect", Array.from(request),
    );
    return bytes instanceof Uint8Array ? bytes : new Uint8Array(bytes);
  }

  async revokeInvitationConnect(request: Uint8Array): Promise<Uint8Array> {
    const bytes = await invoke<number[] | Uint8Array>(
      "invitationRevokeInvitationConnect", Array.from(request),
    );
    return bytes instanceof Uint8Array ? bytes : new Uint8Array(bytes);
  }

  async resendInvitationConnect(request: Uint8Array): Promise<Uint8Array> {
    const bytes = await invoke<number[] | Uint8Array>(
      "invitationResendInvitationConnect", Array.from(request),
    );
    return bytes instanceof Uint8Array ? bytes : new Uint8Array(bytes);
  }

  async acceptInvitationConnect(request: Uint8Array): Promise<Uint8Array> {
    const bytes = await invoke<number[] | Uint8Array>(
      "invitationAcceptInvitationConnect", Array.from(request),
    );
    return bytes instanceof Uint8Array ? bytes : new Uint8Array(bytes);
  }

  async listPendingInvitationsConnect(request: Uint8Array): Promise<Uint8Array> {
    const bytes = await invoke<number[] | Uint8Array>(
      "invitationListPendingInvitationsConnect", Array.from(request),
    );
    return bytes instanceof Uint8Array ? bytes : new Uint8Array(bytes);
  }

  async getInvitationByTokenConnect(request: Uint8Array): Promise<Uint8Array> {
    const bytes = await invoke<number[] | Uint8Array>(
      "invitationGetInvitationByTokenConnect", Array.from(request),
    );
    return bytes instanceof Uint8Array ? bytes : new Uint8Array(bytes);
  }
}
