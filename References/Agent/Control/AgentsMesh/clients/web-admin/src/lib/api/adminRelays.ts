// Connect-RPC adapter for the 4 relay procedures on
// proto.admin.v1.AdminService. Migrated from REST `/api/v1/admin/relays/*`.
//
// The legacy REST handler only ever served ListRelays / GetRelay /
// GetRelayStats / ForceUnregisterRelay — the session-migration paths
// (listSessions / migrateSession / bulkMigrateSessions) were declared
// on the frontend but the REST router never registered them, so every
// call against the old API returned 404. We keep the export surface
// intact with throwing stubs so the relays page still compiles while
// the dead UI gets cleaned up in a follow-up.
import {
  AdminRelay as ProtoAdminRelay,
  AdminRelaySchema,
  ForceUnregisterRelayRequestSchema,
  ForceUnregisterRelayResponseSchema,
  GetRelayRequestSchema,
  GetRelayResponseSchema,
  GetRelayStatsRequestSchema,
  ListRelaysRequestSchema,
  ListRelaysResponseSchema,
  RelayStatsSchema,
} from "@proto/admin/v1/admin_pb";

import { callConnect, ConnectError } from "@/lib/connect/transport";
import type {
  RelayInfo,
  RelayStats,
  RelayListResponse,
  RelayDetailResponse,
  SessionListResponse,
} from "./adminTypesExtended";

const SERVICE = "proto.admin.v1.AdminService";

// AdminRelay proto omits internal_url (never surfaced through REST either)
// and exposes camelCase. Snake_case + optional internal_url keeps the
// existing page + card components untouched.
void AdminRelaySchema;
function fromProtoRelay(r: ProtoAdminRelay): RelayInfo {
  return {
    id: r.id,
    url: r.url,
    region: r.region,
    capacity: r.capacity,
    connections: r.connections,
    cpu_usage: r.cpuUsage,
    memory_usage: r.memoryUsage,
    last_heartbeat: r.lastHeartbeat,
    healthy: r.healthy,
  };
}

export async function listRelays(): Promise<RelayListResponse> {
  const resp = await callConnect(
    SERVICE,
    "ListRelays",
    ListRelaysRequestSchema,
    ListRelaysResponseSchema,
    {},
  );
  return {
    data: resp.items.map(fromProtoRelay),
    total: resp.total,
  };
}

export async function getRelayStats(): Promise<RelayStats> {
  const resp = await callConnect(
    SERVICE,
    "GetRelayStats",
    GetRelayStatsRequestSchema,
    RelayStatsSchema,
    {},
  );
  return {
    total_relays: resp.totalRelays,
    healthy_relays: resp.healthyRelays,
    total_connections: resp.totalConnections,
    // active_sessions never tracked server-side — surface 0 so the
    // stats card renders consistently.
    active_sessions: 0,
  };
}

export async function getRelay(id: string): Promise<RelayDetailResponse> {
  const resp = await callConnect(
    SERVICE,
    "GetRelay",
    GetRelayRequestSchema,
    GetRelayResponseSchema,
    { id },
  );
  if (!resp.relay) {
    throw new ConnectError("Relay not found", "not_found", 404);
  }
  // Backend never tracked per-relay sessions; sessions stay empty.
  return {
    relay: fromProtoRelay(resp.relay),
    session_count: 0,
    sessions: [],
  };
}

export async function forceUnregisterRelay(
  id: string,
  _migrateSessions: boolean = false,
): Promise<{ status: string; relay_id: string; affected_sessions: number }> {
  const resp = await callConnect(
    SERVICE,
    "ForceUnregisterRelay",
    ForceUnregisterRelayRequestSchema,
    ForceUnregisterRelayResponseSchema,
    { id },
  );
  return {
    status: resp.status,
    relay_id: resp.relayId,
    affected_sessions: 0,
  };
}

// Session migration paths: never wired into REST and not modelled on the
// Connect surface either. The page-level UI that calls these is dead and
// will be removed in a follow-up — throwing keeps the surface honest
// instead of silently swallowing the action.
const sessionsNotImplemented = (op: string): never => {
  throw new ConnectError(
    `${op} is not implemented on the relay subsystem`,
    "unimplemented",
    501,
  );
};

export async function listSessions(_relayId?: string): Promise<SessionListResponse> {
  return sessionsNotImplemented("listSessions");
}

export async function migrateSession(
  _podKey: string,
  _targetRelay: string,
): Promise<{ status: string; from_relay: string; to_relay: string }> {
  return sessionsNotImplemented("migrateSession");
}

export async function bulkMigrateSessions(
  _sourceRelay: string,
  _targetRelay: string,
): Promise<{ status: string; total: number; migrated: number; failed: number }> {
  return sessionsNotImplemented("bulkMigrateSessions");
}
