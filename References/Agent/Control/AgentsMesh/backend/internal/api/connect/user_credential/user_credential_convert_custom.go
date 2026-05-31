package usercredentialconnect

import (
	"context"
	"errors"

	"connectrpc.com/connect"

	domainuser "github.com/anthropics/agentsmesh/backend/internal/domain/user"
	"github.com/anthropics/agentsmesh/backend/internal/middleware"
	ucv1 "github.com/anthropics/agentsmesh/proto/gen/go/user_credential/v1"
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

// toProtoGitCredential — codegen-backed thin alias. Phase 12 M7.
// Routes through ToResponse() so the derived ProviderName + RFC3339 timestamp
// strings come from the canonical helper, then through codegen for the
// wire mapping.
func toProtoGitCredential(c *domainuser.GitCredential) *ucv1.GitCredential {
	if c == nil {
		return nil
	}
	return ToProtoGitCredential(c.ToResponse())
}

// virtualRunnerLocalCredential mirrors REST's RunnerLocalCredentialResponse —
// a zero-id placeholder always returned in lists (user_git_credentials.go:67).
// Used here for list response item composition.
func virtualRunnerLocalCredential(isDefault bool) *ucv1.GitCredential {
	return &ucv1.GitCredential{
		Id:             0,
		Name:           "Runner Local",
		CredentialType: domainuser.CredentialTypeRunnerLocal,
		IsDefault:      isDefault,
		CreatedAt:      "",
		UpdatedAt:      "",
	}
}

// toProtoRepositoryProvider — codegen-backed thin alias. Phase 12 M7.
// Routes through ToResponse() so the has_identity / has_client_id / has_bot_token
// flags come from the canonical helper, then through codegen for the wire
// mapping.
func toProtoRepositoryProvider(p *domainuser.RepositoryProvider) *ucv1.RepositoryProvider {
	if p == nil {
		return nil
	}
	return ToProtoRepositoryProvider(p.ToResponse())
}
