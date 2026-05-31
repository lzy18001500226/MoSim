package tokenusageconnect

import (
	"github.com/anthropics/agentsmesh/backend/internal/domain/tokenusage"
	"github.com/anthropics/agentsmesh/backend/pkg/protoconv"
	tuv1 "github.com/anthropics/agentsmesh/proto/gen/go/token_usage/v1"
)

func toProtoSummary(s *tokenusage.UsageSummary) *tuv1.UsageSummary {
	if s == nil {
		return nil
	}
	return &tuv1.UsageSummary{
		InputTokens:         s.InputTokens,
		OutputTokens:        s.OutputTokens,
		CacheCreationTokens: s.CacheCreationTokens,
		CacheReadTokens:     s.CacheReadTokens,
		TotalTokens:         s.TotalTokens,
	}
}

func toProtoTimeSeries(in []tokenusage.TimeSeriesPoint) []*tuv1.TimeSeriesPoint {
	out := make([]*tuv1.TimeSeriesPoint, 0, len(in))
	for _, p := range in {
		out = append(out, &tuv1.TimeSeriesPoint{
			Period:              protoconv.RFC3339(p.Period),
			InputTokens:         p.InputTokens,
			OutputTokens:        p.OutputTokens,
			CacheCreationTokens: p.CacheCreationTokens,
			CacheReadTokens:     p.CacheReadTokens,
		})
	}
	return out
}

func toProtoByAgent(in []tokenusage.AgentUsage) []*tuv1.AgentUsage {
	out := make([]*tuv1.AgentUsage, 0, len(in))
	for _, a := range in {
		out = append(out, &tuv1.AgentUsage{
			AgentSlug:           a.AgentSlug,
			InputTokens:         a.InputTokens,
			OutputTokens:        a.OutputTokens,
			CacheCreationTokens: a.CacheCreationTokens,
			CacheReadTokens:     a.CacheReadTokens,
			TotalTokens:         a.TotalTokens,
		})
	}
	return out
}

func toProtoByUser(in []tokenusage.UserUsage) []*tuv1.UserUsage {
	out := make([]*tuv1.UserUsage, 0, len(in))
	for _, u := range in {
		out = append(out, &tuv1.UserUsage{
			UserId:              u.UserID,
			Username:            u.Username,
			Email:               u.Email,
			InputTokens:         u.InputTokens,
			OutputTokens:        u.OutputTokens,
			CacheCreationTokens: u.CacheCreationTokens,
			CacheReadTokens:     u.CacheReadTokens,
			TotalTokens:         u.TotalTokens,
		})
	}
	return out
}

func toProtoByModel(in []tokenusage.ModelUsage) []*tuv1.ModelUsage {
	out := make([]*tuv1.ModelUsage, 0, len(in))
	for _, m := range in {
		out = append(out, &tuv1.ModelUsage{
			Model:               m.Model,
			InputTokens:         m.InputTokens,
			OutputTokens:        m.OutputTokens,
			CacheCreationTokens: m.CacheCreationTokens,
			CacheReadTokens:     m.CacheReadTokens,
			TotalTokens:         m.TotalTokens,
		})
	}
	return out
}
