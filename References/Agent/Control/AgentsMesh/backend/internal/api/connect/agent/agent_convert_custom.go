package agentconnect

import (
	"context"
	"encoding/json"
	"errors"

	"connectrpc.com/connect"

	domainagent "github.com/anthropics/agentsmesh/backend/internal/domain/agent"
	"github.com/anthropics/agentsmesh/backend/internal/middleware"
	agentservice "github.com/anthropics/agentsmesh/backend/internal/service/agent"
	"github.com/anthropics/agentsmesh/backend/pkg/protoconv"
	agentv1 "github.com/anthropics/agentsmesh/proto/gen/go/agent/v1"
)

// requireUserID is the user-scoped equivalent of interceptors.ResolveOrgScope.
// Mirrors what AuthMiddleware does for REST (conventions §3.5).
func requireUserID(ctx context.Context) (int64, error) {
	tenant := middleware.GetTenant(ctx)
	if tenant == nil || tenant.UserID == 0 {
		return 0, connect.NewError(connect.CodeUnauthenticated, errors.New("authentication required"))
	}
	return tenant.UserID, nil
}

// requireOrgAdmin mirrors REST's tenant.UserRole gate (agents_custom.go:24).
// ResolveOrgScope already populated TenantContext with the user role.
func requireOrgAdmin(ctx context.Context) error {
	tenant := middleware.GetTenant(ctx)
	if tenant == nil {
		return connect.NewError(connect.CodeUnauthenticated, errors.New("missing tenant context"))
	}
	if tenant.UserRole != "admin" && tenant.UserRole != "owner" {
		return connect.NewError(
			connect.CodePermissionDenied,
			errors.New("organization admin role required"),
		)
	}
	return nil
}

// executableToProto handles the empty-string → nil pointer flip required
// because domain stores Executable as a plain string (zero value = absent)
// while the proto wire is `optional string`.
func executableToProto(s string) *string {
	if s == "" {
		return nil
	}
	v := s
	return &v
}

// executableFromProto is the inverse — nil pointer or empty string → "".
func executableFromProto(p *string) string {
	if p == nil {
		return ""
	}
	return *p
}

// toProtoCustomAgent maps an org-scoped CustomAgent. is_builtin is always
// false; supported_modes is "pty" — the REST handler today derives this
// implicitly so we mirror that default. organization_id is required.
// Stays hand-written: CustomAgent struct has a different field set
// (no Executable / IsBuiltin / SupportedModes) so codegen cannot mechanically
// fill the proto from it.
func toProtoCustomAgent(c *domainagent.CustomAgent) *agentv1.Agent {
	if c == nil {
		return nil
	}
	orgID := c.OrganizationID
	return &agentv1.Agent{
		Slug:            c.Slug,
		Name:            c.Name,
		LaunchCommand:   c.LaunchCommand,
		IsBuiltin:       false,
		IsActive:        c.IsActive,
		SupportedModes:  "pty",
		CreatedAt:       protoconv.RFC3339(c.CreatedAt),
		UpdatedAt:       protoconv.RFC3339(c.UpdatedAt),
		OrganizationId:  &orgID,
		Description:     protoconv.StringPtr(c.Description),
		DefaultArgs:     protoconv.StringPtr(c.DefaultArgs),
		AgentfileSource: protoconv.StringPtr(c.AgentfileSource),
	}
}

// toProtoConfigSchema maps a service.ConfigSchemaResponse into proto.
// `default` is JSON-encoded so the wire stays typed regardless of field type
// (boolean / string / number / array — see conventions §3 trade-off note).
func toProtoConfigSchema(s *agentservice.ConfigSchemaResponse) *agentv1.ConfigSchema {
	if s == nil {
		return &agentv1.ConfigSchema{}
	}
	out := &agentv1.ConfigSchema{
		Fields: make([]*agentv1.ConfigField, 0, len(s.Fields)),
	}
	for _, f := range s.Fields {
		options := make([]*agentv1.FieldOption, 0, len(f.Options))
		for _, opt := range f.Options {
			options = append(options, &agentv1.FieldOption{Value: opt.Value})
		}
		field := &agentv1.ConfigField{
			Name:    f.Name,
			Type:    f.Type,
			Options: options,
		}
		if f.Default != nil {
			if b, err := json.Marshal(f.Default); err == nil {
				field.DefaultJson = string(b)
			}
		}
		out.Fields = append(out.Fields, field)
	}
	return out
}

// toProtoUserAgentConfig mirrors UserAgentConfig.ToResponse()
// (domain/agent/user_config.go:37). config_values is JSON-encoded — the map
// values are arbitrary (boolean / string / number / nested objects).
func toProtoUserAgentConfig(c *domainagent.UserAgentConfig) *agentv1.UserAgentConfig {
	if c == nil {
		return nil
	}
	resp := c.ToResponse()
	values, _ := json.Marshal(resp.ConfigValues)
	out := &agentv1.UserAgentConfig{
		Id:               resp.ID,
		UserId:           resp.UserID,
		AgentSlug:        resp.AgentSlug,
		ConfigValuesJson: string(values),
		CreatedAt:        resp.CreatedAt,
		UpdatedAt:        resp.UpdatedAt,
	}
	if resp.AgentName != "" {
		v := resp.AgentName
		out.AgentName = &v
	}
	return out
}
