package skillregistryadminconnect

import (
	"context"

	"connectrpc.com/connect"

	"github.com/anthropics/agentsmesh/backend/internal/api/connect/interceptors"
	"github.com/anthropics/agentsmesh/backend/internal/domain/extension"
	extensionv1 "github.com/anthropics/agentsmesh/proto/gen/go/extension/v1"
)

func (s *Server) ListSkillRegistries(
	ctx context.Context, _ *connect.Request[extensionv1.ListAdminSkillRegistriesRequest],
) (*connect.Response[extensionv1.ListAdminSkillRegistriesResponse], error) {
	ctx, _, err := interceptors.ResolveSystemAdmin(ctx, s.db)
	if err != nil {
		return nil, err
	}

	registries, err := s.repo.ListSkillRegistries(ctx, nil)
	if err != nil {
		return nil, connect.NewError(connect.CodeInternal, err)
	}

	items := make([]*extensionv1.AdminSkillRegistry, 0, len(registries))
	for _, r := range registries {
		items = append(items, ToProtoAdminSkillRegistry(r))
	}
	return connect.NewResponse(&extensionv1.ListAdminSkillRegistriesResponse{
		Items: items,
		Total: int64(len(items)),
	}), nil
}

func (s *Server) CreateSkillRegistry(
	ctx context.Context, req *connect.Request[extensionv1.CreateAdminSkillRegistryRequest],
) (*connect.Response[extensionv1.AdminSkillRegistry], error) {
	ctx, _, err := interceptors.ResolveSystemAdmin(ctx, s.db)
	if err != nil {
		return nil, err
	}

	branch := req.Msg.GetBranch()
	if branch == "" {
		branch = "main"
	}

	if existing, _ := s.repo.FindSkillRegistryByURL(ctx, nil, req.Msg.GetRepositoryUrl()); existing != nil {
		return nil, connect.NewError(
			connect.CodeAlreadyExists,
			errPlatformRegistryDuplicate,
		)
	}

	registry := &extension.SkillRegistry{
		OrganizationID: nil,
		RepositoryURL:  req.Msg.GetRepositoryUrl(),
		Branch:         branch,
		SourceType:     extension.SourceTypeAuto,
		SyncStatus:     extension.SyncStatusPending,
		IsActive:       true,
	}
	if err := s.repo.CreateSkillRegistry(ctx, registry); err != nil {
		return nil, connect.NewError(connect.CodeInternal, err)
	}

	// Best-effort async sync — mirrors REST behavior (skill_registries.go:97).
	// Errors here never abort Create; the next manual Sync call surfaces them.
	if s.worker != nil {
		triggerAsyncSync(s.worker, registry.ID)
	}

	return connect.NewResponse(ToProtoAdminSkillRegistry(registry)), nil
}
