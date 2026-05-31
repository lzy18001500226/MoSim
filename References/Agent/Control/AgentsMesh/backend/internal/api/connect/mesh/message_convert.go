package meshconnect

import (
	"encoding/json"

	"github.com/anthropics/agentsmesh/backend/internal/domain/agent"
	"github.com/anthropics/agentsmesh/backend/pkg/protoconv"
	meshv1 "github.com/anthropics/agentsmesh/proto/gen/go/mesh/v1"
)

// toProtoMeshMessage converts the GORM-backed agent.AgentMessage to its
// MeshMessage proto wire shape. Matches the legacy REST `DirectMessage`
// shape one-to-one — content travels as a JSON-stringified blob (the
// domain stores it as map[string]any), and ParentMessageID is aliased
// to `reply_to_id` to match the legacy serde DTO + the renderer.
func toProtoMeshMessage(m *agent.AgentMessage) *meshv1.MeshMessage {
	if m == nil {
		return nil
	}
	out := &meshv1.MeshMessage{Id: m.ID}
	if m.SenderPod != "" {
		s := m.SenderPod
		out.SenderPod = &s
	}
	if m.ReceiverPod != "" {
		s := m.ReceiverPod
		out.ReceiverPod = &s
	}
	if m.MessageType != "" {
		s := m.MessageType
		out.MessageType = &s
	}
	if len(m.Content) > 0 {
		if data, err := json.Marshal(m.Content); err == nil {
			s := string(data)
			out.Content = &s
		}
	}
	out.CorrelationId = m.CorrelationID
	out.ReplyToId = m.ParentMessageID
	isRead := m.IsRead()
	out.IsRead = &isRead
	createdAt := protoconv.RFC3339(m.CreatedAt)
	out.CreatedAt = &createdAt
	return out
}

func toProtoMeshMessages(messages []*agent.AgentMessage) []*meshv1.MeshMessage {
	out := make([]*meshv1.MeshMessage, 0, len(messages))
	for _, m := range messages {
		out = append(out, toProtoMeshMessage(m))
	}
	return out
}

// toProtoDeadLetter maps the GORM agent.DeadLetterEntry projection to the
// wire shape. The embedded OriginalMessage may be nil when the GORM query
// didn't preload it — surfaces as a nil `message` field on the wire.
func toProtoDeadLetter(e *agent.DeadLetterEntry) *meshv1.MeshDeadLetterEntry {
	if e == nil {
		return nil
	}
	out := &meshv1.MeshDeadLetterEntry{Id: e.ID}
	if e.OriginalMessage != nil {
		out.Message = toProtoMeshMessage(e.OriginalMessage)
	}
	if e.Reason != "" {
		r := e.Reason
		out.Error = &r
	}
	createdAt := protoconv.RFC3339(e.CreatedAt)
	out.CreatedAt = &createdAt
	return out
}

func toProtoDeadLetters(entries []*agent.DeadLetterEntry) []*meshv1.MeshDeadLetterEntry {
	out := make([]*meshv1.MeshDeadLetterEntry, 0, len(entries))
	for _, e := range entries {
		out = append(out, toProtoDeadLetter(e))
	}
	return out
}
