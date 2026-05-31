// Connect-RPC adapter for proto.ticket_relations.v1.TicketRelationsService.
//
// Encodes requests via @bufbuild/protobuf .toBinary(), passes the Uint8Array
// to the wasm bridge (binary in / binary out per conventions §2.5), decodes
// responses via .fromBinary(). No JSON intermediate.
//
// Returns snake_case web shapes (TicketRelation, TicketCommit, TicketComment,
// MergeRequestData) so call sites don't have to switch wire-camelCase off
// the proto generated types — same pattern as podConnect.ts during the
// dual-track migration window.

import {
  type Comment as ProtoComment,
  type Commit as ProtoCommit,
  CreateCommentRequestSchema,
  CreateRelationRequestSchema,
  CommentSchema,
  CommitSchema,
  DeleteCommentRequestSchema,
  DeleteCommentResponseSchema,
  DeleteRelationRequestSchema,
  DeleteRelationResponseSchema,
  LinkCommitRequestSchema,
  ListCommentsRequestSchema,
  ListCommentsResponseSchema,
  ListCommitsRequestSchema,
  ListCommitsResponseSchema,
  ListMergeRequestsRequestSchema,
  ListMergeRequestsResponseSchema,
  ListRelationsRequestSchema,
  ListRelationsResponseSchema,
  type MergeRequest as ProtoMergeRequest,
  type Relation as ProtoRelation,
  RelationSchema,
  UnlinkCommitRequestSchema,
  UnlinkCommitResponseSchema,
  UpdateCommentRequestSchema,
} from "@proto/ticket_relations/v1/ticket_relations_pb";
import { create, toBinary, fromBinary } from "@bufbuild/protobuf";
import { getTicketRelationsService } from "@/lib/wasm-core";
import type {
  TicketRelation,
  TicketCommit,
  TicketComment,
} from "@/lib/viewModels/ticket";
import type { MergeRequestInfo } from "@/components/ide/BottomPanel/MergeRequestCard";

const SERVICE = "@proto/ticket_relations/v1";
// Suppress the import-only marker. The string keeps the dependency graph
// honest in IDE "go to definition" and grep -F searches.
void SERVICE;

// ====== Proto → web shape converters ======

export function fromProtoRelation(r: ProtoRelation): TicketRelation {
  return {
    id: Number(r.id),
    source_ticket_id: Number(r.sourceTicketId),
    target_ticket_id: Number(r.targetTicketId),
    relation_type: r.relationType,
    created_at: r.createdAt || undefined,
    source_ticket: r.sourceTicket
      ? { id: Number(r.sourceTicket.id), slug: r.sourceTicket.slug, title: r.sourceTicket.title }
      : undefined,
    target_ticket: r.targetTicket
      ? { id: Number(r.targetTicket.id), slug: r.targetTicket.slug, title: r.targetTicket.title }
      : undefined,
  };
}

export function fromProtoCommit(c: ProtoCommit): TicketCommit {
  return {
    id: Number(c.id),
    ticket_id: Number(c.ticketId),
    commit_sha: c.commitSha,
    commit_message: c.commitMessage || undefined,
    commit_url: c.commitUrl || undefined,
    author_name: c.authorName || undefined,
    author_email: c.authorEmail || undefined,
    committed_at: c.committedAt || undefined,
    created_at: c.createdAt || undefined,
  };
}

// fromProtoComment recursively maps replies. Backend ListComments preloads
// children with their User association so a depth-2 tree round-trips
// without an extra fetch.
export function fromProtoComment(c: ProtoComment): TicketComment {
  return {
    id: Number(c.id),
    ticket_id: Number(c.ticketId),
    user_id: Number(c.userId),
    content: c.content,
    parent_id: c.parentId === undefined ? undefined : Number(c.parentId),
    mentions: c.mentions.map((m) => ({ user_id: Number(m.userId), username: m.username })),
    created_at: c.createdAt || undefined,
    updated_at: c.updatedAt || undefined,
    user: c.user
      ? {
          id: Number(c.user.id),
          username: c.user.username,
          name: c.user.name || undefined,
          avatar_url: c.user.avatarUrl || undefined,
        }
      : undefined,
    replies: c.replies.length > 0 ? c.replies.map(fromProtoComment) : undefined,
  };
}

export function fromProtoMergeRequest(mr: ProtoMergeRequest): MergeRequestInfo {
  return {
    id: Number(mr.id),
    mr_iid: mr.mrIid,
    title: mr.title,
    state: mr.state,
    mr_url: mr.mrUrl,
    source_branch: mr.sourceBranch,
    target_branch: mr.targetBranch,
    pipeline_status: mr.pipelineStatus || undefined,
    pipeline_url: mr.pipelineUrl || undefined,
  };
}

// ====== Relations ======

export async function listRelations(
  orgSlug: string,
  ticketSlug: string,
): Promise<{ relations: TicketRelation[] }> {
  const req = create(ListRelationsRequestSchema, { orgSlug, ticketSlug });
  const bytes = toBinary(ListRelationsRequestSchema, req);
  const respBytes = await getTicketRelationsService().list_relations_connect(bytes);
  const resp = fromBinary(ListRelationsResponseSchema, new Uint8Array(respBytes));
  return { relations: resp.items.map(fromProtoRelation) };
}

export async function createRelation(
  orgSlug: string,
  ticketSlug: string,
  targetSlug: string,
  relationType: string,
): Promise<TicketRelation> {
  const req = create(CreateRelationRequestSchema, {
    orgSlug,
    ticketSlug,
    targetSlug,
    relationType,
  });
  const bytes = toBinary(CreateRelationRequestSchema, req);
  const respBytes = await getTicketRelationsService().create_relation_connect(bytes);
  return fromProtoRelation(fromBinary(RelationSchema, new Uint8Array(respBytes)));
}

export async function deleteRelation(
  orgSlug: string,
  ticketSlug: string,
  relationId: number,
): Promise<void> {
  const req = create(DeleteRelationRequestSchema, {
    orgSlug,
    ticketSlug,
    relationId: BigInt(relationId),
  });
  const bytes = toBinary(DeleteRelationRequestSchema, req);
  const respBytes = await getTicketRelationsService().delete_relation_connect(bytes);
  fromBinary(DeleteRelationResponseSchema, new Uint8Array(respBytes));
}

// ====== Merge Requests ======

export async function listMergeRequests(
  orgSlug: string,
  ticketSlug: string,
): Promise<{ merge_requests: MergeRequestInfo[] }> {
  const req = create(ListMergeRequestsRequestSchema, { orgSlug, ticketSlug });
  const bytes = toBinary(ListMergeRequestsRequestSchema, req);
  const respBytes = await getTicketRelationsService().list_merge_requests_connect(bytes);
  const resp = fromBinary(ListMergeRequestsResponseSchema, new Uint8Array(respBytes));
  return { merge_requests: resp.items.map(fromProtoMergeRequest) };
}

// ====== Commits ======

export async function listCommits(
  orgSlug: string,
  ticketSlug: string,
): Promise<{ commits: TicketCommit[] }> {
  const req = create(ListCommitsRequestSchema, { orgSlug, ticketSlug });
  const bytes = toBinary(ListCommitsRequestSchema, req);
  const respBytes = await getTicketRelationsService().list_commits_connect(bytes);
  const resp = fromBinary(ListCommitsResponseSchema, new Uint8Array(respBytes));
  return { commits: resp.items.map(fromProtoCommit) };
}

export interface LinkCommitInput {
  commit_sha: string;
  commit_message?: string;
  commit_url?: string;
  author_name?: string;
  author_email?: string;
  committed_at?: string;
}

export async function linkCommit(
  orgSlug: string,
  ticketSlug: string,
  input: LinkCommitInput,
): Promise<TicketCommit> {
  const req = create(LinkCommitRequestSchema, {
    orgSlug,
    ticketSlug,
    commitSha: input.commit_sha,
    commitMessage: input.commit_message,
    commitUrl: input.commit_url,
    authorName: input.author_name,
    authorEmail: input.author_email,
    committedAt: input.committed_at,
  });
  const bytes = toBinary(LinkCommitRequestSchema, req);
  const respBytes = await getTicketRelationsService().link_commit_connect(bytes);
  return fromProtoCommit(fromBinary(CommitSchema, new Uint8Array(respBytes)));
}

export async function unlinkCommit(
  orgSlug: string,
  ticketSlug: string,
  commitId: number,
): Promise<void> {
  const req = create(UnlinkCommitRequestSchema, {
    orgSlug,
    ticketSlug,
    commitId: BigInt(commitId),
  });
  const bytes = toBinary(UnlinkCommitRequestSchema, req);
  const respBytes = await getTicketRelationsService().unlink_commit_connect(bytes);
  fromBinary(UnlinkCommitResponseSchema, new Uint8Array(respBytes));
}

// ====== Comments ======

export async function listComments(
  orgSlug: string,
  ticketSlug: string,
  opts: { limit?: number; offset?: number } = {},
): Promise<{ comments: TicketComment[]; total: number; limit: number; offset: number }> {
  const req = create(ListCommentsRequestSchema, {
    orgSlug,
    ticketSlug,
    limit: opts.limit,
    offset: opts.offset,
  });
  const bytes = toBinary(ListCommentsRequestSchema, req);
  const respBytes = await getTicketRelationsService().list_comments_connect(bytes);
  const resp = fromBinary(ListCommentsResponseSchema, new Uint8Array(respBytes));
  return {
    comments: resp.items.map(fromProtoComment),
    total: Number(resp.total),
    limit: resp.limit,
    offset: resp.offset,
  };
}

export interface CreateCommentInput {
  content: string;
  parent_id?: number;
  mentions?: Array<{ user_id: number; username: string }>;
}

export async function createComment(
  orgSlug: string,
  ticketSlug: string,
  input: CreateCommentInput,
): Promise<TicketComment> {
  const req = create(CreateCommentRequestSchema, {
    orgSlug,
    ticketSlug,
    content: input.content,
    parentId: input.parent_id === undefined ? undefined : BigInt(input.parent_id),
    mentions: (input.mentions ?? []).map((m) => ({
      userId: BigInt(m.user_id),
      username: m.username,
    })),
  });
  const bytes = toBinary(CreateCommentRequestSchema, req);
  const respBytes = await getTicketRelationsService().create_comment_connect(bytes);
  return fromProtoComment(fromBinary(CommentSchema, new Uint8Array(respBytes)));
}

export interface UpdateCommentInput {
  content: string;
  mentions?: Array<{ user_id: number; username: string }>;
}

export async function updateComment(
  orgSlug: string,
  ticketSlug: string,
  commentId: number,
  input: UpdateCommentInput,
): Promise<TicketComment> {
  const req = create(UpdateCommentRequestSchema, {
    orgSlug,
    ticketSlug,
    commentId: BigInt(commentId),
    content: input.content,
    mentions: (input.mentions ?? []).map((m) => ({
      userId: BigInt(m.user_id),
      username: m.username,
    })),
  });
  const bytes = toBinary(UpdateCommentRequestSchema, req);
  const respBytes = await getTicketRelationsService().update_comment_connect(bytes);
  return fromProtoComment(fromBinary(CommentSchema, new Uint8Array(respBytes)));
}

export async function deleteComment(
  orgSlug: string,
  ticketSlug: string,
  commentId: number,
): Promise<void> {
  const req = create(DeleteCommentRequestSchema, {
    orgSlug,
    ticketSlug,
    commentId: BigInt(commentId),
  });
  const bytes = toBinary(DeleteCommentRequestSchema, req);
  const respBytes = await getTicketRelationsService().delete_comment_connect(bytes);
  fromBinary(DeleteCommentResponseSchema, new Uint8Array(respBytes));
}
