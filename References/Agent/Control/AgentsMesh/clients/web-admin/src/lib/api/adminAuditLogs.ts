// Connect-RPC adapter for ListAuditLogs on proto.admin.v1.AdminService.
// Migrated from REST `/api/v1/admin/audit-logs`. Proto carries IDs as bigint
// and uses camelCase fields; this module flattens them to keep the existing
// AuditLog TS shape (snake_case + number) stable for the audit-logs page.
import {
  AdminAuditLog as ProtoAdminAuditLog,
  ListAuditLogsRequestSchema,
  ListAuditLogsResponseSchema,
} from "@proto/admin/v1/admin_pb";

import { callConnect } from "@/lib/connect/transport";
import type { PaginatedResponse } from "./base";
import type { AuditLog, AuditLogListParams } from "./adminTypes";

const SERVICE = "proto.admin.v1.AdminService";

function fromProto(l: ProtoAdminAuditLog): AuditLog {
  return {
    id: Number(l.id),
    admin_user_id: Number(l.adminUserId),
    action: l.action,
    target_type: l.targetType,
    target_id: Number(l.targetId),
    old_data: l.oldData ?? null,
    new_data: l.newData ?? null,
    ip_address: l.ipAddress ?? null,
    user_agent: l.userAgent ?? null,
    created_at: l.createdAt,
    admin_user: l.adminUser
      ? {
          id: Number(l.adminUser.id),
          email: l.adminUser.email,
          username: l.adminUser.username,
          name: l.adminUser.name ?? null,
          avatar_url: l.adminUser.avatarUrl ?? null,
        }
      : undefined,
  };
}

export async function listAuditLogs(
  params?: AuditLogListParams,
): Promise<PaginatedResponse<AuditLog>> {
  const resp = await callConnect(
    SERVICE,
    "ListAuditLogs",
    ListAuditLogsRequestSchema,
    ListAuditLogsResponseSchema,
    {
      adminUserId:
        params?.admin_user_id !== undefined ? BigInt(params.admin_user_id) : undefined,
      action: params?.action,
      targetType: params?.target_type,
      targetId:
        params?.target_id !== undefined ? BigInt(params.target_id) : undefined,
      startTime: params?.start_time,
      endTime: params?.end_time,
      page: params?.page,
      pageSize: params?.page_size,
    },
  );
  return {
    data: resp.items.map(fromProto),
    total: Number(resp.total),
    page: resp.page,
    page_size: resp.pageSize,
    total_pages: resp.totalPages,
  };
}
