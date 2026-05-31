import type { EnvBundle as ProtoEnvBundle } from "@proto/env_bundle/v1/env_bundle_pb";

import type { CredentialProfileViewModel } from "../_shared/credentialViewModel";
import type { RuntimeBundleViewModel } from "./types";

// Project a proto EnvBundle into the CredentialProfileViewModel shape that
// `CredentialsSection` consumes. The view model predates the EnvBundle
// refactor; this adapter keeps the legacy component untouched while wire
// shapes migrated under the hood.
//
// Wire side uses proto types directly (camelCase, bigint id). The ViewModel
// stays snake_case + number id because settings components have not been
// migrated to bigint comparisons yet.
export function toCredentialProfile(
  b: ProtoEnvBundle,
  fallbackAgentSlug: string,
): CredentialProfileViewModel {
  return {
    id: Number(b.id),
    agent_slug: b.agentSlug ?? fallbackAgentSlug,
    name: b.name,
    description: b.description ?? undefined,
    is_default: b.kindPrimary,
    is_active: b.isActive,
    configured_fields: b.configuredFields.length > 0 ? b.configuredFields : undefined,
    configured_values:
      Object.keys(b.configuredValues).length > 0 ? b.configuredValues : undefined,
    created_at: b.createdAt,
    updated_at: b.updatedAt,
  };
}

// Project a proto EnvBundle into a RuntimeBundleViewModel. Runtime values
// round-trip in plaintext, so `configured_values` survives the projection
// intact — the section UI shows the raw KV pairs.
export function toRuntimeBundle(
  b: ProtoEnvBundle,
  fallbackAgentSlug: string,
): RuntimeBundleViewModel {
  return {
    id: Number(b.id),
    agent_slug: b.agentSlug ?? fallbackAgentSlug,
    name: b.name,
    description: b.description ?? undefined,
    is_default: b.kindPrimary,
    is_active: b.isActive,
    configured_fields: b.configuredFields.length > 0 ? b.configuredFields : undefined,
    configured_values:
      Object.keys(b.configuredValues).length > 0 ? b.configuredValues : undefined,
    created_at: b.createdAt,
    updated_at: b.updatedAt,
  };
}
