package extension

import (
	"context"
	"errors"
	"fmt"
	"io"
	"log/slog"
	"path"
	"time"

	"github.com/anthropics/agentsmesh/backend/internal/domain/extension"
	"github.com/google/uuid"
)

func (s *Service) InstallSkillFromMarket(ctx context.Context, orgID, repoID, userID, marketItemID int64, scope string) (*extension.InstalledSkill, error) {
	if err := validateScope(scope); err != nil {
		return nil, err
	}

	marketItem, err := s.repo.GetSkillMarketItem(ctx, marketItemID)
	if err != nil {
		return nil, fmt.Errorf("%w: market item %d", ErrNotFound, marketItemID)
	}

	if marketItem.Registry != nil && marketItem.Registry.OrganizationID != nil &&
		*marketItem.Registry.OrganizationID != orgID {
		return nil, fmt.Errorf("%w: skill not accessible to this organization", ErrForbidden)
	}

	skill := &extension.InstalledSkill{
		OrganizationID: orgID,
		RepositoryID:   repoID,
		MarketItemID:   &marketItemID,
		Scope:          scope,
		InstalledBy:    &userID,
		Slug:           marketItem.Slug,
		InstallSource:  "market",
		ContentSha:     marketItem.ContentSha,
		StorageKey:     marketItem.StorageKey,
		PackageSize:    marketItem.PackageSize,
		IsEnabled:      true,
	}

	if err := s.repo.CreateInstalledSkill(ctx, skill); err != nil {
		if errors.Is(err, extension.ErrDuplicateInstall) {
			return nil, fmt.Errorf("%w: skill '%s' is already installed in this repository with scope '%s'", ErrAlreadyInstalled, skill.Slug, skill.Scope)
		}
		slog.ErrorContext(ctx, "failed to install skill from market", "slug", skill.Slug, "org_id", orgID, "repo_id", repoID, "error", err)
		return nil, fmt.Errorf("failed to install skill: %w", err)
	}

	slog.InfoContext(ctx, "skill installed from market", "slug", skill.Slug, "org_id", orgID, "repo_id", repoID, "scope", scope)
	return skill, nil
}

func (s *Service) InstallSkillFromGitHub(ctx context.Context, orgID, repoID, userID int64, url, branch, path, scope string) (*extension.InstalledSkill, error) {
	if err := validateScope(scope); err != nil {
		return nil, err
	}

	if s.packager == nil {
		return nil, fmt.Errorf("skill packager not configured")
	}

	return s.packager.CompleteGitHubInstall(ctx, orgID, repoID, userID, url, branch, path, scope)
}

func (s *Service) InstallSkillFromUpload(ctx context.Context, orgID, repoID, userID int64, reader io.Reader, filename, scope string) (*extension.InstalledSkill, error) {
	if err := validateScope(scope); err != nil {
		return nil, err
	}

	if s.packager == nil {
		return nil, fmt.Errorf("skill packager not configured")
	}

	return s.packager.CompleteUploadInstall(ctx, orgID, repoID, userID, reader, filename, scope)
}

// PresignSkillUploadResponse carries the presigned PUT URL + opaque storage_key
// the client needs to upload a skill archive directly to S3.
type PresignSkillUploadResponse struct {
	PutURL     string
	StorageKey string
	Filename   string
}

// presignedSkillUploadExpiry bounds how long the client has to PUT.
const presignedSkillUploadExpiry = 15 * time.Minute

// maxSkillUploadBytes mirrors the legacy multipart REST limit.
const maxSkillUploadBytes = 50 * 1024 * 1024

// PresignSkillUpload mints an opaque storage_key + presigned PUT URL for the
// 2-step Connect upload-install flow. Mirrors support_ticket.PresignAttachment.
func (s *Service) PresignSkillUpload(ctx context.Context, orgID, repoID, userID int64, filename, contentType string, size int64) (*PresignSkillUploadResponse, error) {
	if s.storage == nil {
		return nil, fmt.Errorf("%w: storage not configured", ErrInvalidInput)
	}
	if size <= 0 {
		return nil, fmt.Errorf("%w: size must be > 0", ErrInvalidInput)
	}
	if size > maxSkillUploadBytes {
		return nil, fmt.Errorf("%w: upload exceeds maximum size of %d bytes", ErrInvalidInput, maxSkillUploadBytes)
	}
	if filename == "" {
		return nil, fmt.Errorf("%w: filename required", ErrInvalidInput)
	}

	storageKey := newSkillUploadKey(orgID, userID, filename)
	putURL, err := s.storage.PresignPutURL(ctx, storageKey, contentType, presignedSkillUploadExpiry)
	if err != nil {
		return nil, fmt.Errorf("failed to presign upload: %w", err)
	}

	slog.InfoContext(ctx, "skill upload presigned",
		"org_id", orgID, "repo_id", repoID, "user_id", userID,
		"storage_key", storageKey, "size", size)

	return &PresignSkillUploadResponse{
		PutURL:     putURL,
		StorageKey: storageKey,
		Filename:   filename,
	}, nil
}

// InstallSkillFromUploadedKey downloads the previously-uploaded archive at
// storageKey, then drives the same packaging pipeline the multipart REST
// handler used. The opaque key carries the original upload session — callers
// must not mutate it.
func (s *Service) InstallSkillFromUploadedKey(ctx context.Context, orgID, repoID, userID int64, storageKey, filename, scope string) (*extension.InstalledSkill, error) {
	if err := validateScope(scope); err != nil {
		return nil, err
	}
	if s.storage == nil {
		return nil, fmt.Errorf("%w: storage not configured", ErrInvalidInput)
	}
	if s.packager == nil {
		return nil, fmt.Errorf("skill packager not configured")
	}
	if storageKey == "" {
		return nil, fmt.Errorf("%w: storage_key required", ErrInvalidInput)
	}
	exists, err := s.storage.Exists(ctx, storageKey)
	if err != nil {
		return nil, fmt.Errorf("failed to verify upload: %w", err)
	}
	if !exists {
		return nil, fmt.Errorf("%w: uploaded file at storage_key not found", ErrNotFound)
	}

	body, _, err := s.storage.Download(ctx, storageKey)
	if err != nil {
		return nil, fmt.Errorf("failed to download upload: %w", err)
	}
	defer body.Close()
	// Limit-read defends against runaway downloads even if the client lied
	// about size at presign-time (S3 enforces the body length, but a hostile
	// uploader could PUT a different key entirely).
	reader := io.LimitReader(body, maxSkillUploadBytes+1)

	skill, installErr := s.packager.CompleteUploadInstall(ctx, orgID, repoID, userID, reader, filename, scope)
	// Always cleanup the staging blob — install pipeline copies it into the
	// canonical skills/direct/{slug}/{sha}.tar.gz key.
	if delErr := s.storage.Delete(ctx, storageKey); delErr != nil {
		slog.WarnContext(ctx, "failed to delete skill upload staging blob",
			"storage_key", storageKey, "error", delErr)
	}
	if installErr != nil {
		return nil, installErr
	}
	return skill, nil
}

func newSkillUploadKey(orgID, userID int64, filename string) string {
	ext := path.Ext(filename)
	if ext == "" {
		ext = ".tar.gz"
	}
	return fmt.Sprintf("skill-uploads/%d/%d/%s%s", orgID, userID, uuid.New().String(), ext)
}

func (s *Service) UpdateSkill(ctx context.Context, orgID, repoID, installID, userID int64, userRole string, enabled *bool, pinnedVersion *int) (*extension.InstalledSkill, error) {
	skill, err := s.repo.GetInstalledSkill(ctx, installID)
	if err != nil {
		return nil, fmt.Errorf("%w: skill %d", ErrNotFound, installID)
	}

	if err := validateSkillAccess(skill, orgID, repoID, userID, userRole); err != nil {
		return nil, err
	}

	if enabled != nil {
		skill.IsEnabled = *enabled
	}
	if pinnedVersion != nil {
		skill.PinnedVersion = pinnedVersion
	}

	if err := s.repo.UpdateInstalledSkill(ctx, skill); err != nil {
		slog.ErrorContext(ctx, "failed to update installed skill", "install_id", installID, "org_id", orgID, "error", err)
		return nil, fmt.Errorf("failed to update skill: %w", err)
	}

	slog.InfoContext(ctx, "skill updated", "install_id", installID, "org_id", orgID, "repo_id", repoID, "slug", skill.Slug)
	return skill, nil
}

func (s *Service) UninstallSkill(ctx context.Context, orgID, repoID, installID, userID int64, userRole string) error {
	skill, err := s.repo.GetInstalledSkill(ctx, installID)
	if err != nil {
		return fmt.Errorf("%w: skill %d", ErrNotFound, installID)
	}

	if err := validateSkillAccess(skill, orgID, repoID, userID, userRole); err != nil {
		return err
	}

	if err := s.repo.DeleteInstalledSkill(ctx, installID); err != nil {
		slog.ErrorContext(ctx, "failed to uninstall skill", "install_id", installID, "slug", skill.Slug, "org_id", orgID, "error", err)
		return err
	}

	slog.InfoContext(ctx, "skill uninstalled", "install_id", installID, "slug", skill.Slug, "org_id", orgID, "repo_id", repoID)
	return nil
}

func validateSkillAccess(skill *extension.InstalledSkill, orgID, repoID, userID int64, userRole string) error {
	if skill.OrganizationID != orgID {
		return fmt.Errorf("%w: skill does not belong to this organization", ErrForbidden)
	}
	if skill.RepositoryID != repoID {
		return fmt.Errorf("%w: skill does not belong to this repository", ErrForbidden)
	}
	if skill.Scope == extension.ScopeOrg && userRole != "admin" && userRole != "owner" {
		return fmt.Errorf("%w: admin permission required to modify org-scoped skill", ErrForbidden)
	}
	if skill.Scope == extension.ScopeUser {
		if skill.InstalledBy == nil || *skill.InstalledBy != userID {
			return fmt.Errorf("%w: can only modify your own user-scoped skill", ErrForbidden)
		}
	}
	return nil
}
