// Connect-RPC adapter for proto.token_usage.v1.TokenUsageService.
//
// Encodes requests via @bufbuild/protobuf .toBinary(), passes the Uint8Array
// to the wasm bridge (binary in / binary out — conventions §2.5), decodes
// responses via .fromBinary(). No JSON intermediate.

import {
  GetDashboardRequestSchema,
  GetDashboardResponseSchema,
  type AgentUsage as ProtoAgentUsage,
  type ModelUsage as ProtoModelUsage,
  type TimeSeriesPoint as ProtoTimeSeriesPoint,
  type UsageSummary as ProtoUsageSummary,
  type UserUsage as ProtoUserUsage,
} from "@proto/token_usage/v1/token_usage_pb";
import { create, toBinary, fromBinary } from "@bufbuild/protobuf";
import { getTokenUsageService } from "@/lib/wasm-core";
import type {
  TokenUsageByAgent,
  TokenUsageByModel,
  TokenUsageByUser,
  TokenUsageSummary,
  TokenUsageTimeSeriesPoint,
} from "@/lib/viewModels/tokenUsage";

export type {
  TokenUsageByAgent,
  TokenUsageByModel,
  TokenUsageByUser,
  TokenUsageSummary,
  TokenUsageTimeSeriesPoint,
  TokenUsageQueryParams,
} from "@/lib/viewModels/tokenUsage";

export interface TokenUsageDashboard {
  summary: TokenUsageSummary | null;
  time_series: TokenUsageTimeSeriesPoint[];
  by_agent: TokenUsageByAgent[];
  by_user: TokenUsageByUser[];
  by_model: TokenUsageByModel[];
}

function fromProtoSummary(p: ProtoUsageSummary | undefined): TokenUsageSummary | null {
  if (!p) return null;
  return {
    input_tokens: Number(p.inputTokens),
    output_tokens: Number(p.outputTokens),
    cache_creation_tokens: Number(p.cacheCreationTokens),
    cache_read_tokens: Number(p.cacheReadTokens),
    total_tokens: Number(p.totalTokens),
  };
}

function fromProtoTimeSeries(p: ProtoTimeSeriesPoint): TokenUsageTimeSeriesPoint {
  return {
    period: p.period,
    input_tokens: Number(p.inputTokens),
    output_tokens: Number(p.outputTokens),
    cache_creation_tokens: Number(p.cacheCreationTokens),
    cache_read_tokens: Number(p.cacheReadTokens),
  };
}

function fromProtoByAgent(p: ProtoAgentUsage): TokenUsageByAgent {
  return {
    agent_slug: p.agentSlug,
    input_tokens: Number(p.inputTokens),
    output_tokens: Number(p.outputTokens),
    cache_creation_tokens: Number(p.cacheCreationTokens),
    cache_read_tokens: Number(p.cacheReadTokens),
    total_tokens: Number(p.totalTokens),
  };
}

function fromProtoByUser(p: ProtoUserUsage): TokenUsageByUser {
  return {
    user_id: Number(p.userId),
    username: p.username,
    email: p.email,
    input_tokens: Number(p.inputTokens),
    output_tokens: Number(p.outputTokens),
    cache_creation_tokens: Number(p.cacheCreationTokens),
    cache_read_tokens: Number(p.cacheReadTokens),
    total_tokens: Number(p.totalTokens),
  };
}

function fromProtoByModel(p: ProtoModelUsage): TokenUsageByModel {
  return {
    model: p.model,
    input_tokens: Number(p.inputTokens),
    output_tokens: Number(p.outputTokens),
    cache_creation_tokens: Number(p.cacheCreationTokens),
    cache_read_tokens: Number(p.cacheReadTokens),
    total_tokens: Number(p.totalTokens),
  };
}

export interface DashboardParams {
  orgSlug: string;
  startTime?: string;
  endTime?: string;
  granularity?: "day" | "week" | "month";
  agentSlug?: string;
  userId?: number;
  model?: string;
}

export async function getDashboard(params: DashboardParams): Promise<TokenUsageDashboard> {
  const req = create(GetDashboardRequestSchema, {
    orgSlug: params.orgSlug,
    startTime: params.startTime ?? "",
    endTime: params.endTime ?? "",
    granularity: params.granularity ?? "",
    agentSlug: params.agentSlug ?? "",
    userId: params.userId !== undefined ? BigInt(params.userId) : undefined,
    model: params.model ?? "",
  });
  const bytes = toBinary(GetDashboardRequestSchema, req);
  const respBytes = await getTokenUsageService().getDashboardConnect(bytes);
  const resp = fromBinary(GetDashboardResponseSchema, new Uint8Array(respBytes));

  return {
    summary: fromProtoSummary(resp.summary),
    time_series: resp.timeSeries.map(fromProtoTimeSeries),
    by_agent: resp.byAgent.map(fromProtoByAgent),
    by_user: resp.byUser.map(fromProtoByUser),
    by_model: resp.byModel.map(fromProtoByModel),
  };
}
