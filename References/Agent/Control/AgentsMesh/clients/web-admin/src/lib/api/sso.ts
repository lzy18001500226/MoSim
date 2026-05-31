// Connect-RPC adapter for proto.sso.v1.SSOAdminService.
//
// Migrated from REST `/api/v1/admin/sso/configs/*`. Keeps the existing
// snake_case + number TS surface (`SSOConfig`, `CreateSSOConfigRequest`,
// `SSOTestResult`) so the page + table + form don't need to change.
// Proto types are camelCase + bigint; conversion lives in ssoConvert.ts
// to keep this file under the 200-line cap.
//
// Write-only secrets: oidc_client_secret, saml_idp_cert,
// saml_idp_metadata_xml, ldap_bind_password — transit on Create / Update
// but never round-trip on AdminSSOConfig (response shape mirrors REST's
// ToConfigResponse, which strips them server-side).
import {
  AdminSSOConfigSchema,
  CreateSSOConfigRequestSchema,
  DeleteSSOConfigRequestSchema,
  DeleteSSOConfigResponseSchema,
  DisableSSOConfigRequestSchema,
  EnableSSOConfigRequestSchema,
  GetSSOConfigRequestSchema,
  ListSSOConfigsRequestSchema,
  ListSSOConfigsResponseSchema,
  SSOAdminService,
  TestSSOConnectionRequestSchema,
  TestSSOConnectionResponseSchema,
  UpdateSSOConfigRequestSchema,
} from "@proto/sso/v1/sso_admin_pb";

import { callConnect } from "@/lib/connect/transport";
import { buildCreateInit, buildUpdateInit, fromProto } from "./ssoConvert";
import type {
  CreateSSOConfigRequest,
  SSOConfig,
  SSOConfigListParams,
  SSOTestResult,
  UpdateSSOConfigRequest,
} from "./ssoTypes";

export type {
  CreateSSOConfigRequest,
  SSOConfig,
  SSOConfigListParams,
  SSOProtocol,
  SSOTestResult,
  UpdateSSOConfigRequest,
} from "./ssoTypes";

const SERVICE = "proto.sso.v1.SSOAdminService";
void SSOAdminService;

export async function listSSOConfigs(
  params?: SSOConfigListParams,
): Promise<{ data: SSOConfig[]; total: number }> {
  const resp = await callConnect(
    SERVICE,
    "ListSSOConfigs",
    ListSSOConfigsRequestSchema,
    ListSSOConfigsResponseSchema,
    {
      search: params?.search ?? "",
      protocol: params?.protocol ?? "",
      page: params?.page ?? 0,
      pageSize: params?.page_size ?? 0,
    },
  );
  return { data: resp.data.map(fromProto), total: Number(resp.total) };
}

export async function getSSOConfig(id: number): Promise<SSOConfig> {
  const resp = await callConnect(
    SERVICE,
    "GetSSOConfig",
    GetSSOConfigRequestSchema,
    AdminSSOConfigSchema,
    { id: BigInt(id) },
  );
  return fromProto(resp);
}

export async function createSSOConfig(data: CreateSSOConfigRequest): Promise<SSOConfig> {
  const resp = await callConnect(
    SERVICE,
    "CreateSSOConfig",
    CreateSSOConfigRequestSchema,
    AdminSSOConfigSchema,
    buildCreateInit(data),
  );
  return fromProto(resp);
}

export async function updateSSOConfig(
  id: number,
  data: UpdateSSOConfigRequest,
): Promise<SSOConfig> {
  const resp = await callConnect(
    SERVICE,
    "UpdateSSOConfig",
    UpdateSSOConfigRequestSchema,
    AdminSSOConfigSchema,
    buildUpdateInit(id, data),
  );
  return fromProto(resp);
}

export async function deleteSSOConfig(id: number): Promise<{ message: string }> {
  await callConnect(
    SERVICE,
    "DeleteSSOConfig",
    DeleteSSOConfigRequestSchema,
    DeleteSSOConfigResponseSchema,
    { id: BigInt(id) },
  );
  return { message: "SSO config deleted" };
}

export async function enableSSOConfig(id: number): Promise<SSOConfig> {
  const resp = await callConnect(
    SERVICE,
    "EnableSSOConfig",
    EnableSSOConfigRequestSchema,
    AdminSSOConfigSchema,
    { id: BigInt(id) },
  );
  return fromProto(resp);
}

export async function disableSSOConfig(id: number): Promise<SSOConfig> {
  const resp = await callConnect(
    SERVICE,
    "DisableSSOConfig",
    DisableSSOConfigRequestSchema,
    AdminSSOConfigSchema,
    { id: BigInt(id) },
  );
  return fromProto(resp);
}

export async function testSSOConfig(id: number): Promise<SSOTestResult> {
  const resp = await callConnect(
    SERVICE,
    "TestSSOConnection",
    TestSSOConnectionRequestSchema,
    TestSSOConnectionResponseSchema,
    { id: BigInt(id) },
  );
  return { success: resp.success, message: resp.message, error: resp.error };
}
