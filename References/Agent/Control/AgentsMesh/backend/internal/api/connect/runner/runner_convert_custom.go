package runnerconnect

import (
	"encoding/json"

	rundom "github.com/anthropics/agentsmesh/backend/internal/domain/runner"
	runner "github.com/anthropics/agentsmesh/backend/internal/service/runner"
	runnerlog "github.com/anthropics/agentsmesh/backend/internal/service/runnerlog"
	"github.com/anthropics/agentsmesh/backend/pkg/protoconv"
	runnerapiv1 "github.com/anthropics/agentsmesh/proto/gen/go/runner_api/v1"
)

func toProtoRunners(runners []*rundom.Runner) []*runnerapiv1.Runner {
	return protoconv.Slice(runners, ToProtoRunner)
}

// agentVersionsToProto bridges the AgentVersionSlice gorm column type to a
// repeated AgentVersion wire slice. Codegen calls this via field_custom.
func agentVersionsToProto(versions rundom.AgentVersionSlice) []*runnerapiv1.AgentVersion {
	if len(versions) == 0 {
		return nil
	}
	return protoconv.Slice([]rundom.AgentVersion(versions), func(v rundom.AgentVersion) *runnerapiv1.AgentVersion {
		return ToProtoAgentVersion(&v)
	})
}

// stringSliceToProto unwraps the domain StringSlice alias into the wire []string.
// Codegen calls this via field_custom (StringSlice is a domain-local alias,
// not pq.StringArray, so the generic protoconv.StringSlice doesn't apply).
func stringSliceToProto(s rundom.StringSlice) []string {
	if s == nil {
		return nil
	}
	return []string(s)
}

// marshalHostInfo encodes the HostInfo gorm column (map[string]interface{})
// as a JSON string — conventions §6 rationale: avoid pulling
// google.protobuf.Struct + prost-types into the wasm graph.
func marshalHostInfo(hi rundom.HostInfo) string {
	if hi == nil {
		return ""
	}
	b, err := json.Marshal(hi)
	if err != nil {
		return ""
	}
	return string(b)
}

func toProtoRelayConnections(connections []runner.RelayConnectionInfo) []*runnerapiv1.RelayConnectionInfo {
	if len(connections) == 0 {
		return nil
	}
	return protoconv.Slice(connections, func(c runner.RelayConnectionInfo) *runnerapiv1.RelayConnectionInfo {
		return &runnerapiv1.RelayConnectionInfo{
			PodKey:      c.PodKey,
			RelayUrl:    c.RelayURL,
			SessionId:   c.SessionID,
			Connected:   c.Connected,
			ConnectedAt: c.ConnectedAt.UnixMilli(),
		}
	})
}

func toProtoSandboxStatuses(in []*runner.SandboxStatus) []*runnerapiv1.SandboxStatus {
	out := make([]*runnerapiv1.SandboxStatus, 0, len(in))
	for _, s := range in {
		if s == nil {
			continue
		}
		ps := &runnerapiv1.SandboxStatus{
			PodKey:    s.PodKey,
			Exists:    s.Exists,
			CanResume: s.CanResume,
		}
		if s.SandboxPath != "" {
			v := s.SandboxPath
			ps.SandboxPath = &v
		}
		if s.RepositoryURL != "" {
			v := s.RepositoryURL
			ps.RepositoryUrl = &v
		}
		if s.BranchName != "" {
			v := s.BranchName
			ps.BranchName = &v
		}
		if s.CurrentCommit != "" {
			v := s.CurrentCommit
			ps.CurrentCommit = &v
		}
		if s.SizeBytes != 0 {
			v := s.SizeBytes
			ps.SizeBytes = &v
		}
		if s.LastModified != 0 {
			v := s.LastModified
			ps.LastModified = &v
		}
		if s.HasUncommittedChanges {
			v := s.HasUncommittedChanges
			ps.HasUncommittedChanges = &v
		}
		if s.Error != "" {
			v := s.Error
			ps.Error = &v
		}
		out = append(out, ps)
	}
	return out
}

// toProtoLogEntry serializes the runnerlog.LogEntry shape (the REST handler's
// JSON shape) into the proto wire shape.
func toProtoLogEntry(e *runnerlog.LogEntry) *runnerapiv1.RunnerLog {
	if e == nil || e.RunnerLog == nil {
		return nil
	}
	out := &runnerapiv1.RunnerLog{
		Id:            e.ID,
		RunnerId:      e.RunnerID,
		RequestId:     e.RequestID,
		Status:        e.Status,
		SizeBytes:     e.SizeBytes,
		RequestedById: e.RequestedByID,
	}
	if e.StorageKey != "" {
		v := e.StorageKey
		out.StorageKey = &v
	}
	if e.ErrorMessage != "" {
		v := e.ErrorMessage
		out.ErrorMessage = &v
	}
	if e.DownloadURL != "" {
		v := e.DownloadURL
		out.DownloadUrl = &v
	}
	if !e.CreatedAt.IsZero() {
		v := protoconv.RFC3339(e.CreatedAt)
		out.CreatedAt = &v
	}
	out.CompletedAt = protoconv.RFC3339Ptr(e.CompletedAt)
	return out
}

func toProtoToken(t rundom.GRPCRegistrationToken) *runnerapiv1.RunnerToken {
	out := &runnerapiv1.RunnerToken{
		Id: t.ID,
	}
	if t.Name != nil {
		out.Name = t.Name
	}
	maxUses := int32(t.MaxUses)
	usedCount := int32(t.UsedCount)
	out.MaxUses = &maxUses
	out.UsedCount = &usedCount
	if !t.ExpiresAt.IsZero() {
		v := protoconv.RFC3339(t.ExpiresAt)
		out.ExpiresAt = &v
	}
	if !t.CreatedAt.IsZero() {
		v := protoconv.RFC3339(t.CreatedAt)
		out.CreatedAt = &v
	}
	return out
}
