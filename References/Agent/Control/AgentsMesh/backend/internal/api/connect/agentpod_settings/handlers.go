package agentpodsettingsconnect

import (
	"context"
	"errors"

	"connectrpc.com/connect"

	"github.com/anthropics/agentsmesh/backend/internal/middleware"
	"github.com/anthropics/agentsmesh/backend/internal/service/agentpod"
	podv1 "github.com/anthropics/agentsmesh/proto/gen/go/pod/v1"
)

// requireUserID is the user-scoped equivalent of interceptors.ResolveOrgScope.
// Returns CodeUnauthenticated if the auth interceptor didn't populate UserID
// — mirrors what AuthMiddleware does for REST and matches conventions §3.5.
func requireUserID(ctx context.Context) (int64, error) {
	tenant := middleware.GetTenant(ctx)
	if tenant == nil || tenant.UserID == 0 {
		return 0, connect.NewError(connect.CodeUnauthenticated, errors.New("authentication required"))
	}
	return tenant.UserID, nil
}

// GetSettings — REST analogue: GET /api/v1/users/me/agentpod/settings.
// Auto-creates default settings on first read (mirrors SettingsService.GetUserSettings).
func (s *Server) GetSettings(
	ctx context.Context, _ *connect.Request[podv1.GetSettingsRequest],
) (*connect.Response[podv1.AgentPodSettings], error) {
	userID, err := requireUserID(ctx)
	if err != nil {
		return nil, err
	}
	settings, err := s.settings.GetUserSettings(ctx, userID)
	if err != nil {
		return nil, connect.NewError(connect.CodeInternal, err)
	}
	return connect.NewResponse(toProtoSettings(settings)), nil
}

// UpdateSettings — REST analogue: PUT /api/v1/users/me/agentpod/settings.
// Field-level partial update; absent fields are not touched.
func (s *Server) UpdateSettings(
	ctx context.Context, req *connect.Request[podv1.UpdateSettingsRequest],
) (*connect.Response[podv1.AgentPodSettings], error) {
	userID, err := requireUserID(ctx)
	if err != nil {
		return nil, err
	}
	updates := &agentpod.UserSettingsUpdate{
		DefaultAgentSlug: req.Msg.DefaultAgentSlug,
		DefaultModel:     req.Msg.DefaultModel,
		DefaultPermMode:  req.Msg.DefaultPermMode,
		TerminalTheme:    req.Msg.TerminalTheme,
	}
	if req.Msg.TerminalFontSize != nil {
		v := int(*req.Msg.TerminalFontSize)
		updates.TerminalFontSize = &v
	}
	settings, err := s.settings.UpdateUserSettings(ctx, userID, updates)
	if err != nil {
		return nil, connect.NewError(connect.CodeInternal, err)
	}
	return connect.NewResponse(toProtoSettings(settings)), nil
}

// ListProviders — REST analogue: GET /api/v1/users/me/agentpod/providers.
// Encrypted credentials never leave the server — the domain field has no
// proto counterpart, so codegen omits it automatically.
func (s *Server) ListProviders(
	ctx context.Context, _ *connect.Request[podv1.ListProvidersRequest],
) (*connect.Response[podv1.ListProvidersResponse], error) {
	userID, err := requireUserID(ctx)
	if err != nil {
		return nil, err
	}
	providers, err := s.aiProvider.GetUserProviders(ctx, userID)
	if err != nil {
		return nil, connect.NewError(connect.CodeInternal, err)
	}
	items := make([]*podv1.AIProvider, 0, len(providers))
	for _, p := range providers {
		items = append(items, ToProtoAIProvider(p))
	}
	return connect.NewResponse(&podv1.ListProvidersResponse{
		Items: items,
		Total: int64(len(items)),
	}), nil
}

// CreateProvider — REST analogue: POST /api/v1/users/me/agentpod/providers.
func (s *Server) CreateProvider(
	ctx context.Context, req *connect.Request[podv1.CreateProviderRequest],
) (*connect.Response[podv1.AIProvider], error) {
	userID, err := requireUserID(ctx)
	if err != nil {
		return nil, err
	}
	if err := s.aiProvider.ValidateCredentials(req.Msg.GetProviderType(), req.Msg.GetCredentials()); err != nil {
		return nil, connect.NewError(connect.CodeInvalidArgument, err)
	}
	provider, err := s.aiProvider.CreateUserProvider(
		ctx, userID,
		req.Msg.GetProviderType(),
		req.Msg.GetName(),
		req.Msg.GetCredentials(),
		req.Msg.GetIsDefault(),
	)
	if err != nil {
		return nil, connect.NewError(connect.CodeInternal, err)
	}
	return connect.NewResponse(ToProtoAIProvider(provider)), nil
}

// UpdateProvider — REST analogue: PUT /api/v1/users/me/agentpod/providers/:id.
func (s *Server) UpdateProvider(
	ctx context.Context, req *connect.Request[podv1.UpdateProviderRequest],
) (*connect.Response[podv1.AIProvider], error) {
	if _, err := requireUserID(ctx); err != nil {
		return nil, err
	}
	isDefault := false
	if req.Msg.IsDefault != nil {
		isDefault = *req.Msg.IsDefault
	}
	isEnabled := true
	if req.Msg.IsEnabled != nil {
		isEnabled = *req.Msg.IsEnabled
	}
	name := ""
	if req.Msg.Name != nil {
		name = *req.Msg.Name
	}
	provider, err := s.aiProvider.UpdateUserProvider(
		ctx, req.Msg.GetId(),
		name, req.Msg.GetCredentials(), isDefault, isEnabled,
	)
	if err != nil {
		if errors.Is(err, agentpod.ErrProviderNotFound) {
			return nil, connect.NewError(connect.CodeNotFound, err)
		}
		return nil, connect.NewError(connect.CodeInternal, err)
	}
	return connect.NewResponse(ToProtoAIProvider(provider)), nil
}

// DeleteProvider — REST analogue: DELETE /api/v1/users/me/agentpod/providers/:id.
func (s *Server) DeleteProvider(
	ctx context.Context, req *connect.Request[podv1.DeleteProviderRequest],
) (*connect.Response[podv1.DeleteProviderResponse], error) {
	if _, err := requireUserID(ctx); err != nil {
		return nil, err
	}
	if err := s.aiProvider.DeleteUserProvider(ctx, req.Msg.GetId()); err != nil {
		return nil, connect.NewError(connect.CodeInternal, err)
	}
	return connect.NewResponse(&podv1.DeleteProviderResponse{Message: "Provider deleted"}), nil
}

// SetDefaultProvider — REST analogue: POST /api/v1/users/me/agentpod/providers/:id/default.
func (s *Server) SetDefaultProvider(
	ctx context.Context, req *connect.Request[podv1.SetDefaultProviderRequest],
) (*connect.Response[podv1.SetDefaultProviderResponse], error) {
	if _, err := requireUserID(ctx); err != nil {
		return nil, err
	}
	if err := s.aiProvider.SetDefaultProvider(ctx, req.Msg.GetId()); err != nil {
		if errors.Is(err, agentpod.ErrProviderNotFound) {
			return nil, connect.NewError(connect.CodeNotFound, err)
		}
		return nil, connect.NewError(connect.CodeInternal, err)
	}
	return connect.NewResponse(&podv1.SetDefaultProviderResponse{Message: "Default provider set"}), nil
}
