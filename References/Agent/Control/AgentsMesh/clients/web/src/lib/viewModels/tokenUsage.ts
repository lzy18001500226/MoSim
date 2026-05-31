/**
 * Token Usage ViewModels — UI-side projections of `proto.token_usage.v1.*`.
 *
 * The dashboard reads JSON via `getTokenUsageService().get_dashboard()` (not
 * the Connect adapter), so the existing snake_case + `number` shapes stay
 * for the chart / table components. Wire-layer adapters translate to/from
 * the proto types when needed.
 */
export interface TokenUsageSummary {
  input_tokens: number;
  output_tokens: number;
  cache_read_tokens: number;
  cache_creation_tokens: number;
  total_tokens: number;
}

export interface TokenUsageTimeSeriesPoint {
  period: string;
  input_tokens: number;
  output_tokens: number;
  cache_read_tokens: number;
  cache_creation_tokens: number;
}

export interface TokenUsageByAgent {
  agent_slug: string;
  input_tokens: number;
  output_tokens: number;
  cache_read_tokens: number;
  cache_creation_tokens: number;
  total_tokens: number;
}

export interface TokenUsageByUser {
  user_id: number;
  username: string;
  email: string;
  input_tokens: number;
  output_tokens: number;
  cache_read_tokens: number;
  cache_creation_tokens: number;
  total_tokens: number;
}

export interface TokenUsageByModel {
  model: string;
  input_tokens: number;
  output_tokens: number;
  cache_read_tokens: number;
  cache_creation_tokens: number;
  total_tokens: number;
}

export interface TokenUsageQueryParams {
  start_time?: string;
  end_time?: string;
  agent_slug?: string;
  user_id?: number;
  model?: string;
  granularity?: "day" | "week" | "month";
}
