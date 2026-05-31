package usercredentialconnect

import (
	"context"
	"errors"

	"connectrpc.com/connect"

	"github.com/anthropics/agentsmesh/backend/internal/service/user"
	ucv1 "github.com/anthropics/agentsmesh/proto/gen/go/user_credential/v1"
)

// ListGitCredentials — REST analogue: GET /api/v1/users/git-credentials.
// Returns the user's Git credentials plus a virtual runner_local item that
// represents the no-credential default fallback (user_git_credentials.go:51).
func (s *Server) ListGitCredentials(
	ctx context.Context, _ *connect.Request[ucv1.ListGitCredentialsRequest],
) (*connect.Response[ucv1.ListGitCredentialsResponse], error) {
	userID, err := requireUserID(ctx)
	if err != nil {
		return nil, err
	}
	creds, err := s.userSvc.ListGitCredentials(ctx, userID)
	if err != nil {
		return nil, connect.NewError(connect.CodeInternal, err)
	}
	items := make([]*ucv1.GitCredential, 0, len(creds)+1)
	for _, c := range creds {
		items = append(items, toProtoGitCredential(c))
	}
	defaultCred, _ := s.userSvc.GetDefaultGitCredential(ctx, userID)
	runnerLocalDefault := defaultCred == nil
	items = append(items, virtualRunnerLocalCredential(runnerLocalDefault))
	total := int64(len(items))
	return connect.NewResponse(&ucv1.ListGitCredentialsResponse{
		Items:                items,
		Total:                total,
		Limit:                int32(total),
		Offset:               0,
		RunnerLocalIsDefault: runnerLocalDefault,
	}), nil
}

func (s *Server) GetGitCredential(
	ctx context.Context, req *connect.Request[ucv1.GetGitCredentialRequest],
) (*connect.Response[ucv1.GitCredential], error) {
	userID, err := requireUserID(ctx)
	if err != nil {
		return nil, err
	}
	cred, err := s.userSvc.GetGitCredential(ctx, userID, req.Msg.GetId())
	if err != nil {
		return nil, mapGitCredentialError(err)
	}
	return connect.NewResponse(toProtoGitCredential(cred)), nil
}

func (s *Server) CreateGitCredential(
	ctx context.Context, req *connect.Request[ucv1.CreateGitCredentialRequest],
) (*connect.Response[ucv1.GitCredential], error) {
	userID, err := requireUserID(ctx)
	if err != nil {
		return nil, err
	}
	in := &user.CreateGitCredentialRequest{
		Name:                 req.Msg.GetName(),
		CredentialType:       req.Msg.GetCredentialType(),
		RepositoryProviderID: req.Msg.RepositoryProviderId,
	}
	if req.Msg.Pat != nil {
		in.PAT = *req.Msg.Pat
	}
	if req.Msg.PrivateKey != nil {
		in.PrivateKey = *req.Msg.PrivateKey
	}
	if req.Msg.HostPattern != nil {
		in.HostPattern = *req.Msg.HostPattern
	}
	cred, err := s.userSvc.CreateGitCredential(ctx, userID, in)
	if err != nil {
		return nil, mapGitCredentialError(err)
	}
	return connect.NewResponse(toProtoGitCredential(cred)), nil
}

func (s *Server) UpdateGitCredential(
	ctx context.Context, req *connect.Request[ucv1.UpdateGitCredentialRequest],
) (*connect.Response[ucv1.GitCredential], error) {
	userID, err := requireUserID(ctx)
	if err != nil {
		return nil, err
	}
	in := &user.UpdateGitCredentialRequest{
		Name:        req.Msg.Name,
		PAT:         req.Msg.Pat,
		PrivateKey:  req.Msg.PrivateKey,
		HostPattern: req.Msg.HostPattern,
	}
	cred, err := s.userSvc.UpdateGitCredential(ctx, userID, req.Msg.GetId(), in)
	if err != nil {
		return nil, mapGitCredentialError(err)
	}
	return connect.NewResponse(toProtoGitCredential(cred)), nil
}

func (s *Server) DeleteGitCredential(
	ctx context.Context, req *connect.Request[ucv1.DeleteGitCredentialRequest],
) (*connect.Response[ucv1.DeleteGitCredentialResponse], error) {
	userID, err := requireUserID(ctx)
	if err != nil {
		return nil, err
	}
	if err := s.userSvc.DeleteGitCredential(ctx, userID, req.Msg.GetId()); err != nil {
		return nil, mapGitCredentialError(err)
	}
	return connect.NewResponse(&ucv1.DeleteGitCredentialResponse{}), nil
}

func (s *Server) GetDefaultGitCredential(
	ctx context.Context, _ *connect.Request[ucv1.GetDefaultGitCredentialRequest],
) (*connect.Response[ucv1.GetDefaultGitCredentialResponse], error) {
	userID, err := requireUserID(ctx)
	if err != nil {
		return nil, err
	}
	cred, err := s.userSvc.GetDefaultGitCredential(ctx, userID)
	if err != nil {
		return nil, connect.NewError(connect.CodeInternal, err)
	}
	if cred == nil {
		return connect.NewResponse(&ucv1.GetDefaultGitCredentialResponse{
			IsRunnerLocal: true,
		}), nil
	}
	return connect.NewResponse(&ucv1.GetDefaultGitCredentialResponse{
		Credential:    toProtoGitCredential(cred),
		IsRunnerLocal: false,
	}), nil
}

func (s *Server) SetDefaultGitCredential(
	ctx context.Context, req *connect.Request[ucv1.SetDefaultGitCredentialRequest],
) (*connect.Response[ucv1.SetDefaultGitCredentialResponse], error) {
	userID, err := requireUserID(ctx)
	if err != nil {
		return nil, err
	}
	if req.Msg.CredentialId == nil {
		if err := s.userSvc.ClearDefaultGitCredential(ctx, userID); err != nil {
			return nil, connect.NewError(connect.CodeInternal, err)
		}
		return connect.NewResponse(&ucv1.SetDefaultGitCredentialResponse{
			IsRunnerLocal: true,
		}), nil
	}
	if err := s.userSvc.SetDefaultGitCredential(ctx, userID, *req.Msg.CredentialId); err != nil {
		return nil, mapGitCredentialError(err)
	}
	return connect.NewResponse(&ucv1.SetDefaultGitCredentialResponse{
		IsRunnerLocal: false,
	}), nil
}

func (s *Server) ClearDefaultGitCredential(
	ctx context.Context, _ *connect.Request[ucv1.ClearDefaultGitCredentialRequest],
) (*connect.Response[ucv1.ClearDefaultGitCredentialResponse], error) {
	userID, err := requireUserID(ctx)
	if err != nil {
		return nil, err
	}
	if err := s.userSvc.ClearDefaultGitCredential(ctx, userID); err != nil {
		return nil, connect.NewError(connect.CodeInternal, err)
	}
	return connect.NewResponse(&ucv1.ClearDefaultGitCredentialResponse{}), nil
}

func mapGitCredentialError(err error) error {
	switch {
	case errors.Is(err, user.ErrCredentialNotFound):
		return connect.NewError(connect.CodeNotFound, err)
	case errors.Is(err, user.ErrCredentialAlreadyExists):
		return connect.NewError(connect.CodeAlreadyExists, err)
	case errors.Is(err, user.ErrInvalidCredentialType),
		errors.Is(err, user.ErrInvalidSSHKey),
		errors.Is(err, user.ErrProviderIDRequired):
		return connect.NewError(connect.CodeInvalidArgument, err)
	case errors.Is(err, user.ErrProviderNotFound):
		return connect.NewError(connect.CodeNotFound, err)
	default:
		return connect.NewError(connect.CodeInternal, err)
	}
}
