package agentconnect

import (
	"context"
	"encoding/json"

	"connectrpc.com/connect"

	domainagent "github.com/anthropics/agentsmesh/backend/internal/domain/agent"
	agentv1 "github.com/anthropics/agentsmesh/proto/gen/go/agent/v1"
)

// ListUserAgentConfigs mirrors REST `ListUserAgentConfigs`
// (agents_user_config.go:13). User-scoped — no org_slug field per
// conventions §3.5 exception #1.
func (s *Server) ListUserAgentConfigs(
	ctx context.Context, _ *connect.Request[agentv1.ListUserAgentConfigsRequest],
) (*connect.Response[agentv1.UserAgentConfigListResponse], error) {
	userID, err := requireUserID(ctx)
	if err != nil {
		return nil, err
	}

	configs, err := s.userConfigSvc.ListUserAgentConfigs(ctx, userID)
	if err != nil {
		return nil, connect.NewError(connect.CodeInternal, err)
	}

	items := make([]*agentv1.UserAgentConfig, 0, len(configs))
	for _, c := range configs {
		items = append(items, toProtoUserAgentConfig(c))
	}
	return connect.NewResponse(&agentv1.UserAgentConfigListResponse{Configs: items}), nil
}

// GetUserAgentConfig mirrors REST `GetUserAgentConfig`
// (agents_user_config.go:31).
func (s *Server) GetUserAgentConfig(
	ctx context.Context, req *connect.Request[agentv1.GetUserAgentConfigRequest],
) (*connect.Response[agentv1.UserAgentConfig], error) {
	userID, err := requireUserID(ctx)
	if err != nil {
		return nil, err
	}

	config, err := s.userConfigSvc.GetUserAgentConfig(ctx, userID, req.Msg.GetAgentSlug())
	if err != nil {
		return nil, connect.NewError(connect.CodeInternal, err)
	}
	return connect.NewResponse(toProtoUserAgentConfig(config)), nil
}

// SetUserAgentConfig mirrors REST `SetUserAgentConfig`
// (agents_user_config.go:45). Decodes the JSON-encoded config_values bag
// before forwarding to the service.
func (s *Server) SetUserAgentConfig(
	ctx context.Context, req *connect.Request[agentv1.SetUserAgentConfigRequest],
) (*connect.Response[agentv1.UserAgentConfig], error) {
	userID, err := requireUserID(ctx)
	if err != nil {
		return nil, err
	}

	var rawValues map[string]interface{}
	if v := req.Msg.GetConfigValuesJson(); v != "" {
		if err := json.Unmarshal([]byte(v), &rawValues); err != nil {
			return nil, connect.NewError(connect.CodeInvalidArgument, err)
		}
	} else {
		rawValues = map[string]interface{}{}
	}
	configValues := make(domainagent.ConfigValues, len(rawValues))
	for k, val := range rawValues {
		configValues[k] = val
	}

	config, err := s.userConfigSvc.SetUserAgentConfig(
		ctx, userID, req.Msg.GetAgentSlug(), configValues,
	)
	if err != nil {
		return nil, connect.NewError(connect.CodeInternal, err)
	}
	return connect.NewResponse(toProtoUserAgentConfig(config)), nil
}

// DeleteUserAgentConfig mirrors REST `DeleteUserAgentConfig`
// (agents_user_config.go:69).
func (s *Server) DeleteUserAgentConfig(
	ctx context.Context, req *connect.Request[agentv1.DeleteUserAgentConfigRequest],
) (*connect.Response[agentv1.DeleteUserAgentConfigResponse], error) {
	userID, err := requireUserID(ctx)
	if err != nil {
		return nil, err
	}

	if err := s.userConfigSvc.DeleteUserAgentConfig(ctx, userID, req.Msg.GetAgentSlug()); err != nil {
		return nil, connect.NewError(connect.CodeInternal, err)
	}
	return connect.NewResponse(&agentv1.DeleteUserAgentConfigResponse{
		Message: "User config deleted",
	}), nil
}
