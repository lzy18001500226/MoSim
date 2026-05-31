package usercredentialconnect

import (
	"context"
	"errors"

	"connectrpc.com/connect"

	"github.com/anthropics/agentsmesh/backend/internal/infra/git"
	"github.com/anthropics/agentsmesh/backend/internal/service/user"
	ucv1 "github.com/anthropics/agentsmesh/proto/gen/go/user_credential/v1"
)

func (s *Server) ListRepositoryProviders(
	ctx context.Context, _ *connect.Request[ucv1.ListRepositoryProvidersRequest],
) (*connect.Response[ucv1.ListRepositoryProvidersResponse], error) {
	userID, err := requireUserID(ctx)
	if err != nil {
		return nil, err
	}
	providers, err := s.userSvc.ListRepositoryProviders(ctx, userID)
	if err != nil {
		return nil, connect.NewError(connect.CodeInternal, err)
	}
	items := make([]*ucv1.RepositoryProvider, 0, len(providers))
	for _, p := range providers {
		items = append(items, toProtoRepositoryProvider(p))
	}
	total := int64(len(items))
	return connect.NewResponse(&ucv1.ListRepositoryProvidersResponse{
		Items:  items,
		Total:  total,
		Limit:  int32(total),
		Offset: 0,
	}), nil
}

func (s *Server) GetRepositoryProvider(
	ctx context.Context, req *connect.Request[ucv1.GetRepositoryProviderRequest],
) (*connect.Response[ucv1.RepositoryProvider], error) {
	userID, err := requireUserID(ctx)
	if err != nil {
		return nil, err
	}
	p, err := s.userSvc.GetRepositoryProvider(ctx, userID, req.Msg.GetId())
	if err != nil {
		return nil, mapRepositoryProviderError(err)
	}
	return connect.NewResponse(toProtoRepositoryProvider(p)), nil
}

func (s *Server) CreateRepositoryProvider(
	ctx context.Context, req *connect.Request[ucv1.CreateRepositoryProviderRequest],
) (*connect.Response[ucv1.RepositoryProvider], error) {
	userID, err := requireUserID(ctx)
	if err != nil {
		return nil, err
	}
	in := &user.CreateRepositoryProviderRequest{
		ProviderType: req.Msg.GetProviderType(),
		Name:         req.Msg.GetName(),
		BaseURL:      req.Msg.GetBaseUrl(),
	}
	if req.Msg.ClientId != nil {
		in.ClientID = *req.Msg.ClientId
	}
	if req.Msg.ClientSecret != nil {
		in.ClientSecret = *req.Msg.ClientSecret
	}
	if req.Msg.BotToken != nil {
		in.BotToken = *req.Msg.BotToken
	}
	p, err := s.userSvc.CreateRepositoryProvider(ctx, userID, in)
	if err != nil {
		return nil, mapRepositoryProviderError(err)
	}
	return connect.NewResponse(toProtoRepositoryProvider(p)), nil
}

func (s *Server) UpdateRepositoryProvider(
	ctx context.Context, req *connect.Request[ucv1.UpdateRepositoryProviderRequest],
) (*connect.Response[ucv1.RepositoryProvider], error) {
	userID, err := requireUserID(ctx)
	if err != nil {
		return nil, err
	}
	in := &user.UpdateRepositoryProviderRequest{
		Name:         req.Msg.Name,
		BaseURL:      req.Msg.BaseUrl,
		ClientID:     req.Msg.ClientId,
		ClientSecret: req.Msg.ClientSecret,
		BotToken:     req.Msg.BotToken,
		IsActive:     req.Msg.IsActive,
	}
	p, err := s.userSvc.UpdateRepositoryProvider(ctx, userID, req.Msg.GetId(), in)
	if err != nil {
		return nil, mapRepositoryProviderError(err)
	}
	return connect.NewResponse(toProtoRepositoryProvider(p)), nil
}

func (s *Server) DeleteRepositoryProvider(
	ctx context.Context, req *connect.Request[ucv1.DeleteRepositoryProviderRequest],
) (*connect.Response[ucv1.DeleteRepositoryProviderResponse], error) {
	userID, err := requireUserID(ctx)
	if err != nil {
		return nil, err
	}
	if err := s.userSvc.DeleteRepositoryProvider(ctx, userID, req.Msg.GetId()); err != nil {
		return nil, mapRepositoryProviderError(err)
	}
	return connect.NewResponse(&ucv1.DeleteRepositoryProviderResponse{}), nil
}

func (s *Server) SetDefaultRepositoryProvider(
	ctx context.Context, req *connect.Request[ucv1.SetDefaultRepositoryProviderRequest],
) (*connect.Response[ucv1.SetDefaultRepositoryProviderResponse], error) {
	userID, err := requireUserID(ctx)
	if err != nil {
		return nil, err
	}
	if err := s.userSvc.SetDefaultRepositoryProvider(ctx, userID, req.Msg.GetId()); err != nil {
		return nil, mapRepositoryProviderError(err)
	}
	return connect.NewResponse(&ucv1.SetDefaultRepositoryProviderResponse{}), nil
}

func (s *Server) TestRepositoryProviderConnection(
	ctx context.Context, req *connect.Request[ucv1.TestRepositoryProviderConnectionRequest],
) (*connect.Response[ucv1.TestRepositoryProviderConnectionResponse], error) {
	userID, err := requireUserID(ctx)
	if err != nil {
		return nil, err
	}
	provider, err := s.userSvc.GetRepositoryProvider(ctx, userID, req.Msg.GetId())
	if err != nil {
		return nil, mapRepositoryProviderError(err)
	}
	token, err := s.userSvc.GetDecryptedProviderToken(ctx, userID, req.Msg.GetId())
	if err != nil {
		return nil, connect.NewError(connect.CodeInternal, err)
	}
	if token == "" {
		return nil, connect.NewError(connect.CodeFailedPrecondition,
			errors.New("no token configured for this provider"))
	}
	gp, err := git.NewProvider(provider.ProviderType, provider.BaseURL, token)
	if err != nil {
		return nil, connect.NewError(connect.CodeInvalidArgument, err)
	}
	if _, err := gp.ListProjects(ctx, 1, 1); err != nil {
		if errors.Is(err, git.ErrUnauthorized) {
			return nil, connect.NewError(connect.CodeUnauthenticated, err)
		}
		return nil, connect.NewError(connect.CodeUnavailable, err)
	}
	return connect.NewResponse(&ucv1.TestRepositoryProviderConnectionResponse{
		Success: true,
		Message: "Connection successful",
	}), nil
}

func (s *Server) ListProviderRepositories(
	ctx context.Context, req *connect.Request[ucv1.ListProviderRepositoriesRequest],
) (*connect.Response[ucv1.ListProviderRepositoriesResponse], error) {
	userID, err := requireUserID(ctx)
	if err != nil {
		return nil, err
	}
	page := int(1)
	perPage := int(20)
	if req.Msg.Page != nil && *req.Msg.Page > 0 {
		page = int(*req.Msg.Page)
	}
	if req.Msg.PerPage != nil && *req.Msg.PerPage > 0 && *req.Msg.PerPage <= 100 {
		perPage = int(*req.Msg.PerPage)
	}
	provider, err := s.userSvc.GetRepositoryProvider(ctx, userID, req.Msg.GetId())
	if err != nil {
		return nil, mapRepositoryProviderError(err)
	}
	token, err := s.userSvc.GetDecryptedProviderToken(ctx, userID, req.Msg.GetId())
	if err != nil {
		return nil, connect.NewError(connect.CodeInternal, err)
	}
	if token == "" {
		return nil, connect.NewError(connect.CodeFailedPrecondition,
			errors.New("no token configured for this provider"))
	}
	gp, err := git.NewProvider(provider.ProviderType, provider.BaseURL, token)
	if err != nil {
		return nil, connect.NewError(connect.CodeInvalidArgument, err)
	}
	var projects []*git.Project
	if req.Msg.Search != nil && *req.Msg.Search != "" {
		projects, err = gp.SearchProjects(ctx, *req.Msg.Search, page, perPage)
	} else {
		projects, err = gp.ListProjects(ctx, page, perPage)
	}
	if err != nil {
		if errors.Is(err, git.ErrUnauthorized) {
			return nil, connect.NewError(connect.CodeUnauthenticated, err)
		}
		if errors.Is(err, git.ErrRateLimited) {
			return nil, connect.NewError(connect.CodeResourceExhausted, err)
		}
		return nil, connect.NewError(connect.CodeInternal, err)
	}
	items := make([]*ucv1.ProviderRepository, 0, len(projects))
	for _, p := range projects {
		items = append(items, &ucv1.ProviderRepository{
			Id:            p.ID,
			Name:          p.Name,
			Slug:          p.Slug,
			Description:   p.Description,
			DefaultBranch: p.DefaultBranch,
			Visibility:    p.Visibility,
			HttpCloneUrl:  p.HttpCloneURL,
			SshCloneUrl:   p.SSHCloneURL,
			WebUrl:        p.WebURL,
		})
	}
	total := int64(len(items))
	return connect.NewResponse(&ucv1.ListProviderRepositoriesResponse{
		Items:  items,
		Total:  total,
		Limit:  int32(perPage),
		Offset: int32((page - 1) * perPage),
	}), nil
}

func mapRepositoryProviderError(err error) error {
	switch {
	case errors.Is(err, user.ErrProviderNotFound):
		return connect.NewError(connect.CodeNotFound, err)
	case errors.Is(err, user.ErrProviderAlreadyExists):
		return connect.NewError(connect.CodeAlreadyExists, err)
	case errors.Is(err, user.ErrInvalidProviderType):
		return connect.NewError(connect.CodeInvalidArgument, err)
	default:
		return connect.NewError(connect.CodeInternal, err)
	}
}
