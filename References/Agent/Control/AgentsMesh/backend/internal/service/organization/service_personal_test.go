package organization

import (
	"context"
	"errors"
	"testing"

	"github.com/anthropics/agentsmesh/backend/internal/domain/billing"
	orgDomain "github.com/anthropics/agentsmesh/backend/internal/domain/organization"
)

// personalStubRepo is a minimal Repository implementation for CreatePersonal tests.
// SlugExistsFn returns false for an unused slug; CreateWithMemberFn fails when the
// caller wants to simulate a race or DB error.
type personalStubRepo struct {
	slugTaken         map[string]bool
	createCallSlugs   []string
	createOnce        map[string]error // returns the error once for that slug, then succeeds
}

func (r *personalStubRepo) SlugExists(_ context.Context, slug string) (bool, error) {
	return r.slugTaken[slug], nil
}

func (r *personalStubRepo) CreateWithMember(_ context.Context, params *orgDomain.CreateOrgParams) error {
	slug := params.Organization.Slug
	r.createCallSlugs = append(r.createCallSlugs, slug)
	if errs, ok := r.createOnce[slug]; ok && errs != nil {
		delete(r.createOnce, slug)
		r.slugTaken[slug] = true
		return errs
	}
	if r.slugTaken[slug] {
		return errors.New("unique violation idx_organizations_slug")
	}
	r.slugTaken[slug] = true
	params.Organization.ID = int64(len(r.slugTaken))
	return nil
}

func (r *personalStubRepo) GetByID(context.Context, int64) (*orgDomain.Organization, error) {
	panic("not implemented")
}
func (r *personalStubRepo) GetBySlug(context.Context, string) (*orgDomain.Organization, error) {
	panic("not implemented")
}
func (r *personalStubRepo) Update(context.Context, int64, map[string]interface{}) error {
	panic("not implemented")
}
func (r *personalStubRepo) ListByUser(context.Context, int64) ([]*orgDomain.Organization, error) {
	panic("not implemented")
}
func (r *personalStubRepo) DeleteWithCleanup(context.Context, int64) error {
	panic("not implemented")
}
func (r *personalStubRepo) CreateMember(context.Context, *orgDomain.Member) error {
	panic("not implemented")
}
func (r *personalStubRepo) GetMember(context.Context, int64, int64) (*orgDomain.Member, error) {
	panic("not implemented")
}
func (r *personalStubRepo) DeleteMember(context.Context, int64, int64) error {
	panic("not implemented")
}
func (r *personalStubRepo) UpdateMemberRole(context.Context, int64, int64, string) error {
	panic("not implemented")
}
func (r *personalStubRepo) ListMembers(context.Context, int64) ([]*orgDomain.Member, error) {
	panic("not implemented")
}
func (r *personalStubRepo) ListMembersWithUser(context.Context, int64) ([]*orgDomain.Member, error) {
	panic("not implemented")
}
func (r *personalStubRepo) MemberExists(context.Context, int64, int64) (bool, error) {
	panic("not implemented")
}

func newPersonalStub() *personalStubRepo {
	return &personalStubRepo{
		slugTaken:  make(map[string]bool),
		createOnce: make(map[string]error),
	}
}

func TestCreatePersonal_HappyPath(t *testing.T) {
	repo := newPersonalStub()
	svc := NewService(repo)

	org, err := svc.CreatePersonal(context.Background(), 42, "johndoe", "John Doe")
	if err != nil {
		t.Fatalf("CreatePersonal failed: %v", err)
	}
	if org.Slug != "johndoe-workspace" {
		t.Errorf("slug = %q, want johndoe-workspace", org.Slug)
	}
	if org.Name != "John Doe's Workspace" {
		t.Errorf("name = %q, want John Doe's Workspace", org.Name)
	}
	if org.SubscriptionPlan != billing.PlanBased {
		t.Errorf("plan = %q, want %q", org.SubscriptionPlan, billing.PlanBased)
	}
}

func TestCreatePersonal_UsernameWithDots(t *testing.T) {
	repo := newPersonalStub()
	svc := NewService(repo)

	org, err := svc.CreatePersonal(context.Background(), 1, "John.Doe", "")
	if err != nil {
		t.Fatalf("CreatePersonal failed: %v", err)
	}
	if org.Slug != "john-doe-workspace" {
		t.Errorf("slug = %q, want john-doe-workspace", org.Slug)
	}
	if org.Name != "John.Doe's Workspace" {
		t.Errorf("name = %q (display defaults to username when no displayName)", org.Name)
	}
}

func TestCreatePersonal_EmojiUsernameUsesFallback(t *testing.T) {
	repo := newPersonalStub()
	svc := NewService(repo)

	// "🚀" sanitizes to "" — should skip rawSlug seeds entirely and use
	// fallback directly, avoiding every emoji/Unicode user racing for the
	// degenerate "workspace" slug.
	org, err := svc.CreatePersonal(context.Background(), 7, "🚀", "")
	if err != nil {
		t.Fatalf("CreatePersonal failed: %v", err)
	}
	if org.Slug != "user-7-workspace" {
		t.Errorf("slug = %q, want user-7-workspace (Unicode-only username should skip raw seeds)", org.Slug)
	}
}

func TestCreatePersonal_UnicodeUsernameSkipsRawSeed(t *testing.T) {
	repo := newPersonalStub()
	svc := NewService(repo)

	// Chinese-only username sanitizes to "" — must NOT collapse to "workspace".
	org, err := svc.CreatePersonal(context.Background(), 11, "用户名", "张三")
	if err != nil {
		t.Fatalf("CreatePersonal failed: %v", err)
	}
	if org.Slug != "user-11-workspace" {
		t.Errorf("slug = %q, want user-11-workspace (sanitize-empty username must use fallback only)", org.Slug)
	}
	// Two distinct Unicode-only users in sequence must not collide.
	org2, err := svc.CreatePersonal(context.Background(), 22, "用户", "李四")
	if err != nil {
		t.Fatalf("second CreatePersonal failed: %v", err)
	}
	if org2.Slug != "user-22-workspace" {
		t.Errorf("second slug = %q, want user-22-workspace", org2.Slug)
	}
}

func TestCreatePersonal_EmptyUsernameUsesFallback(t *testing.T) {
	repo := newPersonalStub()
	svc := NewService(repo)

	// Sanitize("-workspace") = "workspace" → valid → uses raw path; ownerID 13
	// is reflected only in fallback. Verify it still creates an org.
	org, err := svc.CreatePersonal(context.Background(), 13, "", "")
	if err != nil {
		t.Fatalf("CreatePersonal failed: %v", err)
	}
	if org.Slug == "" {
		t.Error("slug should not be empty")
	}
}

func TestCreatePersonal_RaceRetry(t *testing.T) {
	repo := newPersonalStub()
	repo.createOnce["johndoe-workspace"] = ErrSlugAlreadyExists

	svc := NewService(repo)
	org, err := svc.CreatePersonal(context.Background(), 1, "johndoe", "John")
	if err != nil {
		t.Fatalf("CreatePersonal should retry on race, got: %v", err)
	}
	// After race on "johndoe-workspace", GenerateUnique sees it taken and
	// returns "johndoe-workspace-2".
	if org.Slug != "johndoe-workspace-2" {
		t.Errorf("slug = %q, want johndoe-workspace-2 (after race retry)", org.Slug)
	}
	if len(repo.createCallSlugs) != 2 {
		t.Errorf("create called %d times, want 2 (initial + retry)", len(repo.createCallSlugs))
	}
}

func TestCreatePersonal_PreExistingSlugUsesSuffix(t *testing.T) {
	repo := newPersonalStub()
	repo.slugTaken["johndoe-workspace"] = true

	svc := NewService(repo)
	org, err := svc.CreatePersonal(context.Background(), 1, "johndoe", "")
	if err != nil {
		t.Fatalf("CreatePersonal failed: %v", err)
	}
	if org.Slug != "johndoe-workspace-2" {
		t.Errorf("slug = %q, want johndoe-workspace-2", org.Slug)
	}
}

func TestCreatePersonal_RaceOnRawSeedFallsBackToUserID(t *testing.T) {
	repo := newPersonalStub()
	// Force every raw-derived candidate to lose the race; the third attempt
	// should switch to the userID fallback seed.
	repo.createOnce["johndoe-workspace"] = ErrSlugAlreadyExists
	repo.createOnce["johndoe-workspace-2"] = ErrSlugAlreadyExists

	svc := NewService(repo)
	org, err := svc.CreatePersonal(context.Background(), 7, "johndoe", "")
	if err != nil {
		t.Fatalf("CreatePersonal failed: %v", err)
	}
	if org.Slug != "user-7-workspace" {
		t.Errorf("slug = %q, want user-7-workspace (fallback after raw exhausted)", org.Slug)
	}
	if len(repo.createCallSlugs) != 3 {
		t.Errorf("create called %d times, want 3", len(repo.createCallSlugs))
	}
}

func TestCreatePersonal_AllAttemptsRaceReturnsError(t *testing.T) {
	repo := newPersonalStub()
	repo.createOnce["johndoe-workspace"] = ErrSlugAlreadyExists
	repo.createOnce["johndoe-workspace-2"] = ErrSlugAlreadyExists
	repo.createOnce["user-9-workspace"] = ErrSlugAlreadyExists

	svc := NewService(repo)
	_, err := svc.CreatePersonal(context.Background(), 9, "johndoe", "")
	if !errors.Is(err, ErrSlugAlreadyExists) {
		t.Errorf("err = %v, want ErrSlugAlreadyExists", err)
	}
}
