// Upload-install flow: two Connect RPCs replace the REST multipart handler.
// Step 1 (PresignSkillUpload) authorizes the caller against the repo and
// mints a presigned S3 PUT URL + opaque storage_key. The browser PUTs the
// archive directly to S3. Step 2 (InstallSkillFromUploadedFile) verifies the
// upload landed, then drives the same packaging pipeline the multipart
// handler used. Same pattern as support_ticket attachments.
package extensionconnect

import (
	"context"
	"errors"

	"connectrpc.com/connect"

	"github.com/anthropics/agentsmesh/backend/internal/api/connect/interceptors"
	"github.com/anthropics/agentsmesh/backend/internal/middleware"
	extensionv1 "github.com/anthropics/agentsmesh/proto/gen/go/extension/v1"
)

func (s *RepoSkillServer) PresignSkillUpload(
	ctx context.Context, req *connect.Request[extensionv1.PresignSkillUploadRequest],
) (*connect.Response[extensionv1.PresignSkillUploadResponse], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	if err := validatePresignSkillUploadReq(req.Msg); err != nil {
		return nil, err
	}
	tenant := middleware.GetTenant(ctx)

	resp, err := s.extensionSvc.PresignSkillUpload(
		ctx, tenant.OrganizationID, req.Msg.GetRepositoryId(), tenant.UserID,
		req.Msg.GetFilename(), req.Msg.GetContentType(), req.Msg.GetSize(),
	)
	if err != nil {
		return nil, mapServiceError(err)
	}
	return connect.NewResponse(&extensionv1.PresignSkillUploadResponse{
		PutUrl:     resp.PutURL,
		StorageKey: resp.StorageKey,
		Filename:   resp.Filename,
	}), nil
}

func (s *RepoSkillServer) InstallSkillFromUploadedFile(
	ctx context.Context, req *connect.Request[extensionv1.InstallSkillFromUploadedFileRequest],
) (*connect.Response[extensionv1.InstalledSkill], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	if req.Msg.GetStorageKey() == "" {
		return nil, connect.NewError(connect.CodeInvalidArgument,
			errors.New("storage_key is required"))
	}
	if req.Msg.GetFilename() == "" {
		return nil, connect.NewError(connect.CodeInvalidArgument,
			errors.New("filename is required"))
	}
	if req.Msg.GetScope() == "org" {
		if err := requireOrgAdmin(ctx); err != nil {
			return nil, err
		}
	}
	tenant := middleware.GetTenant(ctx)

	skill, err := s.extensionSvc.InstallSkillFromUploadedKey(
		ctx, tenant.OrganizationID, req.Msg.GetRepositoryId(), tenant.UserID,
		req.Msg.GetStorageKey(), req.Msg.GetFilename(), req.Msg.GetScope(),
	)
	if err != nil {
		return nil, mapServiceError(err)
	}
	return connect.NewResponse(toProtoInstalledSkill(skill)), nil
}

func validatePresignSkillUploadReq(req *extensionv1.PresignSkillUploadRequest) error {
	if req.GetRepositoryId() == 0 {
		return connect.NewError(connect.CodeInvalidArgument,
			errors.New("repository_id is required"))
	}
	if req.GetFilename() == "" {
		return connect.NewError(connect.CodeInvalidArgument,
			errors.New("filename is required"))
	}
	if req.GetContentType() == "" {
		return connect.NewError(connect.CodeInvalidArgument,
			errors.New("content_type is required"))
	}
	if req.GetSize() <= 0 {
		return connect.NewError(connect.CodeInvalidArgument,
			errors.New("size must be > 0"))
	}
	return nil
}
