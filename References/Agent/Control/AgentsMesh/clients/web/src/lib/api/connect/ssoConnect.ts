// Connect-RPC adapter for proto.sso.v1.SSOService (public — no auth).
//
// Wire layer is proto-SSOT: returns and consumes `@proto/sso/v1` types
// directly. No adapter DTO layer.

import {
  DiscoverRequestSchema,
  DiscoverResponseSchema,
  LdapAuthRequestSchema,
  LdapAuthResponseSchema,
  type LdapAuthResponse,
  type SSODiscoverConfig,
} from "@proto/sso/v1/sso_pb";
import { create, toBinary, fromBinary } from "@bufbuild/protobuf";
import { getSSOService } from "@/lib/wasm-core";

export type { LdapAuthResponse, SSODiscoverConfig } from "@proto/sso/v1/sso_pb";

export async function discover(email: string): Promise<{ items: SSODiscoverConfig[] }> {
  const req = create(DiscoverRequestSchema, { email });
  const bytes = toBinary(DiscoverRequestSchema, req);
  const respBytes = await getSSOService().discoverConnect(bytes);
  const resp = fromBinary(DiscoverResponseSchema, new Uint8Array(respBytes));
  return { items: resp.items };
}

export async function ldapAuth(
  domain: string,
  username: string,
  password: string,
): Promise<LdapAuthResponse> {
  const req = create(LdapAuthRequestSchema, { domain, username, password });
  const bytes = toBinary(LdapAuthRequestSchema, req);
  const respBytes = await getSSOService().ldapAuthConnect(bytes);
  return fromBinary(LdapAuthResponseSchema, new Uint8Array(respBytes));
}
