package skillregistryadminconnect

import (
	"encoding/json"

	"github.com/anthropics/agentsmesh/backend/internal/domain/extension"
)

// detectedTypeToProto mirrors REST's `omitempty` JSON tag — domain stores
// empty string for "no value yet" but the proto wire shape uses optional.
func detectedTypeToProto(v string) *string {
	if v == "" {
		return nil
	}
	return &v
}

func detectedTypeFromProto(p *string) string {
	if p == nil {
		return ""
	}
	return *p
}

// lastCommitShaToProto — same omitempty bridge as detectedType.
func lastCommitShaToProto(v string) *string {
	if v == "" {
		return nil
	}
	return &v
}

func lastCommitShaFromProto(p *string) string {
	if p == nil {
		return ""
	}
	return *p
}

// syncErrorToProto — same omitempty bridge as detectedType.
func syncErrorToProto(v string) *string {
	if v == "" {
		return nil
	}
	return &v
}

func syncErrorFromProto(p *string) string {
	if p == nil {
		return ""
	}
	return *p
}

// compatibleAgentsToProto unpacks the GORM JSONB column. Prefers the
// model's GetCompatibleAgents helper, then falls back to a defensive
// json.Unmarshal for the legacy "[]" raw bytes case (matches the
// org-scoped converter in extension/skill_registry_convert.go:62).
func compatibleAgentsToProto(raw json.RawMessage) []string {
	if len(raw) == 0 {
		return nil
	}
	r := &extension.SkillRegistry{CompatibleAgents: raw}
	if agents := r.GetCompatibleAgents(); len(agents) > 0 {
		return agents
	}
	var parsed []string
	if err := json.Unmarshal(raw, &parsed); err == nil {
		return parsed
	}
	return nil
}

func compatibleAgentsFromProto(p []string) json.RawMessage {
	if len(p) == 0 {
		return nil
	}
	b, err := json.Marshal(p)
	if err != nil {
		return nil
	}
	return b
}
