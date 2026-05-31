package ssoadminconnect

import (
	"context"
	"log/slog"

	"connectrpc.com/connect"

	"github.com/anthropics/agentsmesh/backend/internal/api/connect/interceptors"
	"github.com/anthropics/agentsmesh/backend/internal/domain/admin"
	ssoservice "github.com/anthropics/agentsmesh/backend/internal/service/sso"
	ssov1 "github.com/anthropics/agentsmesh/proto/gen/go/sso/v1"
)

// CreateSSOConfig mirrors REST's CreateConfig (sso.go:99).
func (s *Server) CreateSSOConfig(
	ctx context.Context, req *connect.Request[ssov1.CreateSSOConfigRequest],
) (*connect.Response[ssov1.AdminSSOConfig], error) {
	ctx, adminUser, err := interceptors.ResolveSystemAdmin(ctx, s.db)
	if err != nil {
		return nil, err
	}

	cfg, err := s.ssoSvc.CreateConfig(ctx, fromCreateRequest(req.Msg), adminUser.ID)
	if err != nil {
		return nil, mapServiceError(err)
	}

	resp := s.ssoSvc.ToConfigResponse(cfg)
	logAdminAction(ctx, s.adminSvc, adminUser.ID,
		admin.AuditActionCreate, admin.TargetTypeSSOConfig, cfg.ID,
		nil, resp, req.Peer().Addr, req.Header().Get("User-Agent"))

	return connect.NewResponse(toProtoAdminSSOConfig(resp)), nil
}

// UpdateSSOConfig mirrors REST's UpdateConfig (sso.go:149).
func (s *Server) UpdateSSOConfig(
	ctx context.Context, req *connect.Request[ssov1.UpdateSSOConfigRequest],
) (*connect.Response[ssov1.AdminSSOConfig], error) {
	ctx, adminUser, err := interceptors.ResolveSystemAdmin(ctx, s.db)
	if err != nil {
		return nil, err
	}

	id := req.Msg.GetId()
	oldCfg, auditErr := s.ssoSvc.GetConfig(ctx, id)
	if auditErr != nil {
		slog.WarnContext(ctx, "failed to retrieve old SSO config for audit",
			"id", id, "error", auditErr)
	}

	cfg, err := s.ssoSvc.UpdateConfig(ctx, id, fromUpdateRequest(req.Msg))
	if err != nil {
		return nil, mapServiceError(err)
	}

	var oldResp *ssoservice.ConfigResponse
	if oldCfg != nil {
		oldResp = s.ssoSvc.ToConfigResponse(oldCfg)
	}
	newResp := s.ssoSvc.ToConfigResponse(cfg)
	logAdminAction(ctx, s.adminSvc, adminUser.ID,
		admin.AuditActionUpdate, admin.TargetTypeSSOConfig, id,
		oldResp, newResp, req.Peer().Addr, req.Header().Get("User-Agent"))

	return connect.NewResponse(toProtoAdminSSOConfig(newResp)), nil
}

// DeleteSSOConfig mirrors REST's DeleteConfig (sso.go:189).
func (s *Server) DeleteSSOConfig(
	ctx context.Context, req *connect.Request[ssov1.DeleteSSOConfigRequest],
) (*connect.Response[ssov1.DeleteSSOConfigResponse], error) {
	ctx, adminUser, err := interceptors.ResolveSystemAdmin(ctx, s.db)
	if err != nil {
		return nil, err
	}

	id := req.Msg.GetId()
	oldCfg, auditErr := s.ssoSvc.GetConfig(ctx, id)
	if auditErr != nil {
		slog.WarnContext(ctx, "failed to retrieve old SSO config for audit",
			"id", id, "error", auditErr)
	}

	if err := s.ssoSvc.DeleteConfig(ctx, id); err != nil {
		return nil, mapServiceError(err)
	}

	var oldResp *ssoservice.ConfigResponse
	if oldCfg != nil {
		oldResp = s.ssoSvc.ToConfigResponse(oldCfg)
	}
	logAdminAction(ctx, s.adminSvc, adminUser.ID,
		admin.AuditActionDelete, admin.TargetTypeSSOConfig, id,
		oldResp, nil, req.Peer().Addr, req.Header().Get("User-Agent"))

	return connect.NewResponse(&ssov1.DeleteSSOConfigResponse{}), nil
}

// EnableSSOConfig mirrors REST's EnableConfig (sso_actions.go:40).
func (s *Server) EnableSSOConfig(
	ctx context.Context, req *connect.Request[ssov1.EnableSSOConfigRequest],
) (*connect.Response[ssov1.AdminSSOConfig], error) {
	return s.toggleEnabled(ctx, req.Msg.GetId(), true,
		admin.AuditActionActivate,
		req.Peer().Addr, req.Header().Get("User-Agent"))
}

// DisableSSOConfig mirrors REST's DisableConfig (sso_actions.go:69).
func (s *Server) DisableSSOConfig(
	ctx context.Context, req *connect.Request[ssov1.DisableSSOConfigRequest],
) (*connect.Response[ssov1.AdminSSOConfig], error) {
	return s.toggleEnabled(ctx, req.Msg.GetId(), false,
		admin.AuditActionDeactivate,
		req.Peer().Addr, req.Header().Get("User-Agent"))
}

// toggleEnabled centralizes the enable/disable pair — they only differ on
// the bool flag + audit action. Mirrors sso_actions.go's pattern of
// rewriting the request into an UpdateConfig call with a single IsEnabled
// pointer set.
func (s *Server) toggleEnabled(
	ctx context.Context, id int64, enable bool,
	action admin.AuditAction, ip, userAgent string,
) (*connect.Response[ssov1.AdminSSOConfig], error) {
	ctx, adminUser, err := interceptors.ResolveSystemAdmin(ctx, s.db)
	if err != nil {
		return nil, err
	}

	oldCfg, auditErr := s.ssoSvc.GetConfig(ctx, id)
	if auditErr != nil {
		slog.WarnContext(ctx, "failed to retrieve old SSO config for audit",
			"id", id, "error", auditErr)
	}

	cfg, err := s.ssoSvc.UpdateConfig(ctx, id, &ssoservice.UpdateConfigRequest{
		IsEnabled: boolPtr(enable),
	})
	if err != nil {
		return nil, mapServiceError(err)
	}

	var oldResp *ssoservice.ConfigResponse
	if oldCfg != nil {
		oldResp = s.ssoSvc.ToConfigResponse(oldCfg)
	}
	newResp := s.ssoSvc.ToConfigResponse(cfg)
	logAdminAction(ctx, s.adminSvc, adminUser.ID,
		action, admin.TargetTypeSSOConfig, id,
		oldResp, newResp, ip, userAgent)

	return connect.NewResponse(toProtoAdminSSOConfig(newResp)), nil
}
