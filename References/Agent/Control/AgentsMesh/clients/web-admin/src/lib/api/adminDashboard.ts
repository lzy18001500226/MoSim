// Connect-RPC adapter for GetDashboardStats on proto.admin.v1.AdminService.
// Migrated from REST `/api/v1/admin/dashboard/stats`. Proto carries the
// stat counters as bigint; this module flattens them to number to keep the
// existing DashboardStats TS shape (snake_case + number) stable for the
// dashboard page.
import {
  DashboardStatsSchema,
  GetDashboardStatsRequestSchema,
  type DashboardStats as ProtoDashboardStats,
} from "@proto/admin/v1/admin_pb";

import { callConnect } from "@/lib/connect/transport";
import type { DashboardStats } from "./adminTypes";

const SERVICE = "proto.admin.v1.AdminService";

function fromProto(s: ProtoDashboardStats): DashboardStats {
  return {
    total_users: Number(s.totalUsers),
    active_users: Number(s.activeUsers),
    total_organizations: Number(s.totalOrganizations),
    total_runners: Number(s.totalRunners),
    online_runners: Number(s.onlineRunners),
    total_pods: Number(s.totalPods),
    active_pods: Number(s.activePods),
    total_subscriptions: Number(s.totalSubscriptions),
    active_subscriptions: Number(s.activeSubscriptions),
    new_users_today: Number(s.newUsersToday),
    new_users_this_week: Number(s.newUsersThisWeek),
    new_users_this_month: Number(s.newUsersThisMonth),
  };
}

export async function getDashboardStats(): Promise<DashboardStats> {
  const resp = await callConnect(
    SERVICE,
    "GetDashboardStats",
    GetDashboardStatsRequestSchema,
    DashboardStatsSchema,
    {},
  );
  return fromProto(resp);
}
