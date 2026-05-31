// Connect-RPC adapter for proto.ticket.v1.TicketService — ticket CRUD +
// board + assignees + shared wire converters.
//
// Label ops live in `ticketLabelConnect.ts`. The wire layer is hidden
// behind `facade/ticketConnect.ts`.
//
// Encodes requests via @bufbuild/protobuf .toBinary(), passes the Uint8Array
// to the wasm bridge (binary in / binary out per conventions §2.5), decodes
// responses via .fromBinary(). No JSON intermediate.

import {
  AddAssigneeRequestSchema,
  BoardSchema,
  CreateTicketRequestSchema,
  DeleteTicketRequestSchema,
  GetActiveTicketsRequestSchema,
  GetBoardRequestSchema,
  GetSubTicketsRequestSchema,
  GetTicketRequestSchema,
  ListTicketsRequestSchema,
  ListTicketsResponseSchema,
  RemoveAssigneeRequestSchema,
  TicketSchema,
  UpdateTicketRequestSchema,
  UpdateTicketStatusRequestSchema,
  type Label as ProtoLabel,
  type Ticket as ProtoTicket,
} from "@proto/ticket/v1/ticket_pb";
import { create, toBinary, fromBinary } from "@bufbuild/protobuf";
import { getTicketService } from "@/lib/wasm-core";
import type {
  BoardColumn,
  TicketData,
  TicketPriority,
  TicketStatus,
} from "@/lib/viewModels/ticket";

// ============== Wire conversion (proto -> snake_case web shape) ==============
// Exported for cross-file use by ticketLabelConnect.

export function fromProtoTicket(t: ProtoTicket): TicketData {
  return {
    id: Number(t.id),
    number: t.number,
    slug: t.slug,
    title: t.title,
    content: t.content,
    status: t.status as TicketStatus,
    priority: t.priority as TicketPriority,
    severity: t.severity,
    estimate: t.estimate,
    due_date: t.dueDate,
    started_at: t.startedAt,
    completed_at: t.completedAt,
    created_at: t.createdAt,
    updated_at: t.updatedAt,
    repository_id: t.repositoryId !== undefined ? Number(t.repositoryId) : undefined,
  };
}

export function fromProtoLabel(l: ProtoLabel): { id: number; name: string; color: string } {
  return { id: Number(l.id), name: l.name, color: l.color };
}

// ============== Ticket CRUD ==============

export async function listTickets(
  orgSlug: string,
  opts: {
    repository_id?: number;
    status?: string;
    priority?: string;
    assignee_id?: number;
    labels?: string[];
    query?: string;
    offset?: number;
    limit?: number;
  } = {},
): Promise<{ items: TicketData[]; total: number; limit: number; offset: number }> {
  const req = create(ListTicketsRequestSchema, {
    orgSlug,
    repositoryId: opts.repository_id !== undefined ? BigInt(opts.repository_id) : undefined,
    status: opts.status,
    priority: opts.priority,
    assigneeId: opts.assignee_id !== undefined ? BigInt(opts.assignee_id) : undefined,
    labels: opts.labels ?? [],
    query: opts.query,
    offset: opts.offset,
    limit: opts.limit,
  });
  const bytes = toBinary(ListTicketsRequestSchema, req);
  const respBytes = await getTicketService().list_tickets_connect(bytes);
  const resp = fromBinary(ListTicketsResponseSchema, new Uint8Array(respBytes));
  return {
    items: resp.items.map(fromProtoTicket),
    total: Number(resp.total),
    limit: resp.limit,
    offset: resp.offset,
  };
}

export async function getTicket(orgSlug: string, ticketSlug: string): Promise<TicketData> {
  const req = create(GetTicketRequestSchema, { orgSlug, ticketSlug });
  const bytes = toBinary(GetTicketRequestSchema, req);
  const respBytes = await getTicketService().get_ticket_connect(bytes);
  return fromProtoTicket(fromBinary(TicketSchema, new Uint8Array(respBytes)));
}

export interface CreateTicketInput {
  title: string;
  content?: string;
  status?: string;
  priority?: string;
  repository_id?: number;
  assignee_ids?: number[];
  labels?: string[];
  parent_ticket_slug?: string;
  due_date?: string;
}

export async function createTicket(
  orgSlug: string,
  input: CreateTicketInput,
): Promise<TicketData> {
  const req = create(CreateTicketRequestSchema, {
    orgSlug,
    title: input.title,
    content: input.content,
    status: input.status,
    priority: input.priority,
    repositoryId: input.repository_id !== undefined ? BigInt(input.repository_id) : undefined,
    assigneeIds: (input.assignee_ids ?? []).map((id) => BigInt(id)),
    labels: input.labels ?? [],
    parentTicketSlug: input.parent_ticket_slug,
    dueDate: input.due_date,
  });
  const bytes = toBinary(CreateTicketRequestSchema, req);
  const respBytes = await getTicketService().create_ticket_connect(bytes);
  return fromProtoTicket(fromBinary(TicketSchema, new Uint8Array(respBytes)));
}

export interface UpdateTicketInput {
  title?: string;
  content?: string;
  status?: string;
  priority?: string;
  // 0 explicitly clears the repository association (matches REST semantic).
  repository_id?: number;
  assignee_ids?: number[];
  labels?: string[];
  // "" explicitly clears the due_date.
  due_date?: string;
}

export async function updateTicket(
  orgSlug: string,
  ticketSlug: string,
  input: UpdateTicketInput,
): Promise<TicketData> {
  const req = create(UpdateTicketRequestSchema, {
    orgSlug,
    ticketSlug,
    title: input.title,
    content: input.content,
    status: input.status,
    priority: input.priority,
    repositoryId: input.repository_id !== undefined ? BigInt(input.repository_id) : undefined,
    assigneeIds: input.assignee_ids !== undefined
      ? input.assignee_ids.map((id) => BigInt(id))
      : [],
    labels: input.labels ?? [],
    dueDate: input.due_date,
  });
  const bytes = toBinary(UpdateTicketRequestSchema, req);
  const respBytes = await getTicketService().update_ticket_connect(bytes);
  return fromProtoTicket(fromBinary(TicketSchema, new Uint8Array(respBytes)));
}

export async function deleteTicket(orgSlug: string, ticketSlug: string): Promise<void> {
  const req = create(DeleteTicketRequestSchema, { orgSlug, ticketSlug });
  await getTicketService().delete_ticket_connect(toBinary(DeleteTicketRequestSchema, req));
}

export async function updateTicketStatus(
  orgSlug: string,
  ticketSlug: string,
  status: string,
): Promise<void> {
  const req = create(UpdateTicketStatusRequestSchema, { orgSlug, ticketSlug, status });
  await getTicketService().update_ticket_status_connect(
    toBinary(UpdateTicketStatusRequestSchema, req),
  );
}

// ============== Board / active / sub-tickets ==============

export async function getActiveTickets(
  orgSlug: string,
  opts: { repository_id?: number; limit?: number } = {},
): Promise<TicketData[]> {
  const req = create(GetActiveTicketsRequestSchema, {
    orgSlug,
    repositoryId: opts.repository_id !== undefined ? BigInt(opts.repository_id) : undefined,
    limit: opts.limit,
  });
  const bytes = toBinary(GetActiveTicketsRequestSchema, req);
  const respBytes = await getTicketService().get_active_tickets_connect(bytes);
  const resp = fromBinary(ListTicketsResponseSchema, new Uint8Array(respBytes));
  return resp.items.map(fromProtoTicket);
}

export async function getBoard(
  orgSlug: string,
  opts: {
    repository_id?: number;
    limit?: number;
    priority?: string;
    assignee_id?: number;
    query?: string;
  } = {},
): Promise<BoardColumn[]> {
  const req = create(GetBoardRequestSchema, {
    orgSlug,
    repositoryId: opts.repository_id !== undefined ? BigInt(opts.repository_id) : undefined,
    limit: opts.limit,
    priority: opts.priority,
    assigneeId: opts.assignee_id !== undefined ? BigInt(opts.assignee_id) : undefined,
    query: opts.query,
  });
  const bytes = toBinary(GetBoardRequestSchema, req);
  const respBytes = await getTicketService().get_board_connect(bytes);
  const resp = fromBinary(BoardSchema, new Uint8Array(respBytes));
  return resp.columns.map((c) => ({
    status: c.status,
    count: Number(c.totalCount),
    tickets: c.tickets.map(fromProtoTicket),
  }));
}

export async function getSubTickets(
  orgSlug: string,
  ticketSlug: string,
): Promise<TicketData[]> {
  const req = create(GetSubTicketsRequestSchema, { orgSlug, ticketSlug });
  const respBytes = await getTicketService().get_sub_tickets_connect(
    toBinary(GetSubTicketsRequestSchema, req),
  );
  const resp = fromBinary(ListTicketsResponseSchema, new Uint8Array(respBytes));
  return resp.items.map(fromProtoTicket);
}

// ============== Assignees ==============

export async function addAssignee(
  orgSlug: string,
  ticketSlug: string,
  userId: number,
): Promise<void> {
  const req = create(AddAssigneeRequestSchema, {
    orgSlug,
    ticketSlug,
    userId: BigInt(userId),
  });
  await getTicketService().add_assignee_connect(toBinary(AddAssigneeRequestSchema, req));
}

export async function removeAssignee(
  orgSlug: string,
  ticketSlug: string,
  userId: number,
): Promise<void> {
  const req = create(RemoveAssigneeRequestSchema, {
    orgSlug,
    ticketSlug,
    userId: BigInt(userId),
  });
  await getTicketService().remove_assignee_connect(
    toBinary(RemoveAssigneeRequestSchema, req),
  );
}
