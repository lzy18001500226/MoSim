// Package extensionconnect hosts Connect-RPC handlers for the extension
// domain. Mirrors backend/internal/api/rest/v1/extension.go but exposes
// the data plane via Connect (binary protobuf wire, see conventions.md
// §2.5). REST stays mounted in parallel; the migration runs dual-track
// until all 26 services have flipped.
//
// Handler shape follows runbook §3:
//   * ResolveOrgScope reads org_slug + injects TenantContext.
//   * Single-entity create/sync/toggle return the entity directly.
//   * List responses follow {items, total, limit, offset}.
//   * Errors map to Connect codes (conventions §10).
package extensionconnect

import (
	"context"
	"errors"
	"net/http"

	"connectrpc.com/connect"

	"github.com/anthropics/agentsmesh/backend/internal/api/connect/interceptors"
	"github.com/anthropics/agentsmesh/backend/internal/middleware"
	extensionservice "github.com/anthropics/agentsmesh/backend/internal/service/extension"
	extensionv1 "github.com/anthropics/agentsmesh/proto/gen/go/extension/v1"
)

// ServiceName mirrors proto.extension.v1.SkillRegistryService exactly —
// Connect derives the URL from `<package>.<Service>` (conventions §1, §12).
const ServiceName = "proto.extension.v1.SkillRegistryService"

const (
	ListSkillRegistriesProcedure         = "/" + ServiceName + "/ListSkillRegistries"
	CreateSkillRegistryProcedure         = "/" + ServiceName + "/CreateSkillRegistry"
	SyncSkillRegistryProcedure           = "/" + ServiceName + "/SyncSkillRegistry"
	DeleteSkillRegistryProcedure         = "/" + ServiceName + "/DeleteSkillRegistry"
	TogglePlatformRegistryProcedure      = "/" + ServiceName + "/TogglePlatformRegistry"
	ListSkillRegistryOverridesProcedure  = "/" + ServiceName + "/ListSkillRegistryOverrides"
)

// Server implements the SkillRegistryService contract. The fields mirror the
// dependencies the REST handler in extension.go pulls in, threaded through
// the cmd/server wiring at mount time.
type Server struct {
	extensionSvc *extensionservice.Service
	orgSvc       middleware.OrganizationService
}

func NewServer(extSvc *extensionservice.Service, orgSvc middleware.OrganizationService) *Server {
	return &Server{extensionSvc: extSvc, orgSvc: orgSvc}
}

func (s *Server) ListSkillRegistries(
	ctx context.Context, req *connect.Request[extensionv1.ListSkillRegistriesRequest],
) (*connect.Response[extensionv1.ListSkillRegistriesResponse], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	if err := requireOrgAdmin(ctx); err != nil {
		return nil, err
	}

	tenant := middleware.GetTenant(ctx)
	registries, err := s.extensionSvc.ListSkillRegistries(ctx, tenant.OrganizationID)
	if err != nil {
		return nil, mapServiceError(err)
	}

	items := make([]*extensionv1.SkillRegistry, 0, len(registries))
	for _, r := range registries {
		items = append(items, toProtoSkillRegistry(r))
	}
	return connect.NewResponse(&extensionv1.ListSkillRegistriesResponse{
		Items:  items,
		Total:  int64(len(items)),
		Limit:  req.Msg.GetLimit(),
		Offset: req.Msg.GetOffset(),
	}), nil
}

func (s *Server) CreateSkillRegistry(
	ctx context.Context, req *connect.Request[extensionv1.CreateSkillRegistryRequest],
) (*connect.Response[extensionv1.SkillRegistry], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	if err := requireOrgAdmin(ctx); err != nil {
		return nil, err
	}

	tenant := middleware.GetTenant(ctx)
	input := extensionservice.CreateSkillRegistryInput{
		RepositoryURL:    req.Msg.GetRepositoryUrl(),
		Branch:           req.Msg.GetBranch(),
		SourceType:       req.Msg.GetSourceType(),
		CompatibleAgents: req.Msg.GetCompatibleAgents(),
		AuthType:         req.Msg.GetAuthType(),
		AuthCredential:   req.Msg.GetAuthCredential(),
	}
	reg, err := s.extensionSvc.CreateSkillRegistry(ctx, tenant.OrganizationID, input)
	if err != nil {
		return nil, mapServiceError(err)
	}
	return connect.NewResponse(toProtoSkillRegistry(reg)), nil
}

func (s *Server) SyncSkillRegistry(
	ctx context.Context, req *connect.Request[extensionv1.SyncSkillRegistryRequest],
) (*connect.Response[extensionv1.SkillRegistry], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	if err := requireOrgAdmin(ctx); err != nil {
		return nil, err
	}

	tenant := middleware.GetTenant(ctx)
	reg, err := s.extensionSvc.SyncSkillRegistry(ctx, tenant.OrganizationID, req.Msg.GetId())
	if err != nil {
		return nil, mapServiceError(err)
	}
	return connect.NewResponse(toProtoSkillRegistry(reg)), nil
}

func (s *Server) DeleteSkillRegistry(
	ctx context.Context, req *connect.Request[extensionv1.DeleteSkillRegistryRequest],
) (*connect.Response[extensionv1.DeleteSkillRegistryResponse], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	if err := requireOrgAdmin(ctx); err != nil {
		return nil, err
	}

	tenant := middleware.GetTenant(ctx)
	if err := s.extensionSvc.DeleteSkillRegistry(ctx, tenant.OrganizationID, req.Msg.GetId()); err != nil {
		return nil, mapServiceError(err)
	}
	return connect.NewResponse(&extensionv1.DeleteSkillRegistryResponse{}), nil
}

func (s *Server) TogglePlatformRegistry(
	ctx context.Context, req *connect.Request[extensionv1.TogglePlatformRegistryRequest],
) (*connect.Response[extensionv1.TogglePlatformRegistryResponse], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	if err := requireOrgAdmin(ctx); err != nil {
		return nil, err
	}

	tenant := middleware.GetTenant(ctx)
	if err := s.extensionSvc.TogglePlatformRegistry(
		ctx, tenant.OrganizationID, req.Msg.GetId(), req.Msg.GetDisabled(),
	); err != nil {
		return nil, mapServiceError(err)
	}

	// Re-list overrides to match REST handler (extension.go:206).
	overrides, err := s.extensionSvc.ListSkillRegistryOverrides(ctx, tenant.OrganizationID)
	if err != nil {
		return nil, mapServiceError(err)
	}
	out := make([]*extensionv1.SkillRegistryOverride, 0, len(overrides))
	for _, o := range overrides {
		out = append(out, toProtoSkillRegistryOverride(o))
	}
	return connect.NewResponse(&extensionv1.TogglePlatformRegistryResponse{Overrides: out}), nil
}

func (s *Server) ListSkillRegistryOverrides(
	ctx context.Context, req *connect.Request[extensionv1.ListSkillRegistryOverridesRequest],
) (*connect.Response[extensionv1.ListSkillRegistryOverridesResponse], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	if err := requireOrgAdmin(ctx); err != nil {
		return nil, err
	}

	tenant := middleware.GetTenant(ctx)
	overrides, err := s.extensionSvc.ListSkillRegistryOverrides(ctx, tenant.OrganizationID)
	if err != nil {
		return nil, mapServiceError(err)
	}
	items := make([]*extensionv1.SkillRegistryOverride, 0, len(overrides))
	for _, o := range overrides {
		items = append(items, toProtoSkillRegistryOverride(o))
	}
	return connect.NewResponse(&extensionv1.ListSkillRegistryOverridesResponse{
		Items: items,
		Total: int64(len(items)),
	}), nil
}

// requireOrgAdmin mirrors REST's requireOrgAdmin (extension.go:35).
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

// mapServiceError mirrors handleServiceError (extension.go:18). Translates
// extension-domain sentinels to Connect codes per conventions §10.
func mapServiceError(err error) error {
	switch {
	case errors.Is(err, extensionservice.ErrNotFound):
		return connect.NewError(connect.CodeNotFound, err)
	case errors.Is(err, extensionservice.ErrForbidden):
		return connect.NewError(connect.CodePermissionDenied, err)
	case errors.Is(err, extensionservice.ErrInvalidScope),
		errors.Is(err, extensionservice.ErrInvalidInput):
		return connect.NewError(connect.CodeInvalidArgument, err)
	case errors.Is(err, extensionservice.ErrAlreadyInstalled):
		return connect.NewError(connect.CodeAlreadyExists, err)
	default:
		return connect.NewError(connect.CodeInternal, err)
	}
}

// Mount registers all SkillRegistryService procedures on mux behind the
// auth interceptor supplied via opts (see cmd/server/connect_init.go).
func Mount(mux *http.ServeMux, srv *Server, opts ...connect.HandlerOption) {
	mux.Handle(ListSkillRegistriesProcedure, connect.NewUnaryHandler(
		ListSkillRegistriesProcedure, srv.ListSkillRegistries, opts...,
	))
	mux.Handle(CreateSkillRegistryProcedure, connect.NewUnaryHandler(
		CreateSkillRegistryProcedure, srv.CreateSkillRegistry, opts...,
	))
	mux.Handle(SyncSkillRegistryProcedure, connect.NewUnaryHandler(
		SyncSkillRegistryProcedure, srv.SyncSkillRegistry, opts...,
	))
	mux.Handle(DeleteSkillRegistryProcedure, connect.NewUnaryHandler(
		DeleteSkillRegistryProcedure, srv.DeleteSkillRegistry, opts...,
	))
	mux.Handle(TogglePlatformRegistryProcedure, connect.NewUnaryHandler(
		TogglePlatformRegistryProcedure, srv.TogglePlatformRegistry, opts...,
	))
	mux.Handle(ListSkillRegistryOverridesProcedure, connect.NewUnaryHandler(
		ListSkillRegistryOverridesProcedure, srv.ListSkillRegistryOverrides, opts...,
	))
}
