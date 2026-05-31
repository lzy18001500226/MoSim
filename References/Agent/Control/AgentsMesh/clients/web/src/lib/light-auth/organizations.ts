// Org list / create over Connect-RPC JSON. Used by post-login redirect
// resolution and the onboarding flow's "create my first workspace" call.

import { lightConnect } from "./api-fetch";
import { updateLightSessionOrgSlug } from "@/lib/light-session";

export interface LightOrganization {
  id: number;
  name: string;
  slug: string;
  role?: string;
  logo_url?: string;
  subscription_plan?: string;
  subscription_status?: string;
}

interface ConnectOrg {
  id: number | string | bigint;
  name: string;
  slug: string;
  logoUrl?: string;
  subscriptionPlan?: string;
  subscriptionStatus?: string;
  role?: string;
}

interface ListMyOrgsResponse {
  items?: ConnectOrg[];
}

// Per proto/org/v1/org.proto convention: create/get/update return the
// Organization message directly (no envelope wrapper). The Connect JSON
// transport mirrors the proto shape, so the response is the Organization
// itself, not { organization: ... }.

function toLightOrg(o: ConnectOrg): LightOrganization {
  return {
    id: Number(o.id),
    name: o.name,
    slug: o.slug,
    role: o.role,
    logo_url: o.logoUrl,
    subscription_plan: o.subscriptionPlan,
    subscription_status: o.subscriptionStatus,
  };
}

export async function lightListOrganizations(): Promise<LightOrganization[]> {
  const resp = await lightConnect<Record<string, never>, ListMyOrgsResponse>(
    "proto.org.v1.OrgService",
    "ListMyOrgs",
    {},
    { authenticated: true },
  );
  return (resp?.items ?? []).map(toLightOrg);
}

export interface LightCreateOrgInput {
  name: string;
  slug: string;
  logo_url?: string;
}

export async function lightCreateOrganization(
  input: LightCreateOrgInput,
): Promise<LightOrganization> {
  const resp = await lightConnect<{ name: string; slug: string; logoUrl?: string }, ConnectOrg>(
    "proto.org.v1.OrgService",
    "CreateOrg",
    { name: input.name, slug: input.slug, logoUrl: input.logo_url },
    { authenticated: true },
  );
  if (!resp?.slug) throw new Error("OrgService.CreateOrg returned 200 with no organization payload");
  const light = toLightOrg(resp);
  updateLightSessionOrgSlug(light.slug);
  return light;
}

// Server derives slug from users.username via slugkit.Sanitize — caller passes
// no body. Use this for onboarding "Quick Start"; never construct the slug
// client-side.
export async function lightCreatePersonalOrganization(): Promise<LightOrganization> {
  const resp = await lightConnect<Record<string, never>, ConnectOrg>(
    "proto.org.v1.OrgService",
    "CreatePersonalOrg",
    {},
    { authenticated: true },
  );
  if (!resp?.slug) throw new Error("OrgService.CreatePersonalOrg returned 200 with no organization payload");
  const light = toLightOrg(resp);
  updateLightSessionOrgSlug(light.slug);
  return light;
}
