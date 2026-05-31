package promocodeconnect

import (
	"context"
	"errors"
	"testing"
	"time"

	"connectrpc.com/connect"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	promocodedomain "github.com/anthropics/agentsmesh/backend/internal/domain/promocode"
	"github.com/anthropics/agentsmesh/backend/internal/middleware"
	promocodesvc "github.com/anthropics/agentsmesh/backend/internal/service/promocode"
	promocodev1 "github.com/anthropics/agentsmesh/proto/gen/go/promocode/v1"
)

// fakeOrg / fakeOrgService satisfy middleware.OrganizationGetter +
// OrganizationService for ResolveOrgScope. Mirrors invitation_test.go.
type fakeOrg struct {
	id   int64
	slug string
}

func (f fakeOrg) GetID() int64    { return f.id }
func (f fakeOrg) GetSlug() string { return f.slug }
func (f fakeOrg) GetName() string { return f.slug }

type fakeOrgService struct {
	role string
}

func (f *fakeOrgService) GetBySlug(_ context.Context, slug string) (middleware.OrganizationGetter, error) {
	if slug == "missing" {
		return nil, errors.New("org not found")
	}
	return fakeOrg{id: 7, slug: slug}, nil
}
func (f *fakeOrgService) IsMember(context.Context, int64, int64) (bool, error) { return true, nil }
func (f *fakeOrgService) GetMemberRole(context.Context, int64, int64) (string, error) {
	return f.role, nil
}

func ctxAsUser(userID int64) context.Context {
	return middleware.SetTenant(context.Background(),
		&middleware.TenantContext{UserID: userID})
}

func connectCodeOf(t *testing.T, err error) connect.Code {
	t.Helper()
	var ce *connect.Error
	require.True(t, errors.As(err, &ce), "expected *connect.Error, got %v", err)
	return ce.Code()
}

// --- Validate ---

func TestValidate_MissingOrgSlug_InvalidArgument(t *testing.T) {
	srv := NewServer(nil, &fakeOrgService{role: "member"})
	_, err := srv.Validate(ctxAsUser(42),
		connect.NewRequest(&promocodev1.ValidatePromoCodeRequest{Code: "X"}))
	require.Error(t, err)
	assert.Equal(t, connect.CodeInvalidArgument, connectCodeOf(t, err))
}

func TestValidate_NoAuth_Unauthenticated(t *testing.T) {
	srv := NewServer(nil, &fakeOrgService{role: "member"})
	_, err := srv.Validate(context.Background(),
		connect.NewRequest(&promocodev1.ValidatePromoCodeRequest{OrgSlug: "acme", Code: "X"}))
	require.Error(t, err)
	assert.Equal(t, connect.CodeUnauthenticated, connectCodeOf(t, err))
}

func TestValidate_EmptyCode_InvalidArgument(t *testing.T) {
	srv := NewServer(nil, &fakeOrgService{role: "member"})
	_, err := srv.Validate(ctxAsUser(42),
		connect.NewRequest(&promocodev1.ValidatePromoCodeRequest{OrgSlug: "acme"}))
	require.Error(t, err)
	assert.Equal(t, connect.CodeInvalidArgument, connectCodeOf(t, err))
}

// --- Redeem ---

func TestRedeem_MissingOrgSlug_InvalidArgument(t *testing.T) {
	srv := NewServer(nil, &fakeOrgService{role: "owner"})
	_, err := srv.Redeem(ctxAsUser(42),
		connect.NewRequest(&promocodev1.RedeemPromoCodeRequest{Code: "X"}))
	require.Error(t, err)
	assert.Equal(t, connect.CodeInvalidArgument, connectCodeOf(t, err))
}

func TestRedeem_NoAuth_Unauthenticated(t *testing.T) {
	srv := NewServer(nil, &fakeOrgService{role: "owner"})
	_, err := srv.Redeem(context.Background(),
		connect.NewRequest(&promocodev1.RedeemPromoCodeRequest{OrgSlug: "acme", Code: "X"}))
	require.Error(t, err)
	assert.Equal(t, connect.CodeUnauthenticated, connectCodeOf(t, err))
}

func TestRedeem_EmptyCode_InvalidArgument(t *testing.T) {
	srv := NewServer(nil, &fakeOrgService{role: "owner"})
	_, err := srv.Redeem(ctxAsUser(42),
		connect.NewRequest(&promocodev1.RedeemPromoCodeRequest{OrgSlug: "acme"}))
	require.Error(t, err)
	assert.Equal(t, connect.CodeInvalidArgument, connectCodeOf(t, err))
}

// --- GetRedemptionHistory ---

func TestGetRedemptionHistory_MissingOrgSlug_InvalidArgument(t *testing.T) {
	srv := NewServer(nil, &fakeOrgService{role: "member"})
	_, err := srv.GetRedemptionHistory(ctxAsUser(42),
		connect.NewRequest(&promocodev1.GetRedemptionHistoryRequest{}))
	require.Error(t, err)
	assert.Equal(t, connect.CodeInvalidArgument, connectCodeOf(t, err))
}

func TestGetRedemptionHistory_NoAuth_Unauthenticated(t *testing.T) {
	srv := NewServer(nil, &fakeOrgService{role: "member"})
	_, err := srv.GetRedemptionHistory(context.Background(),
		connect.NewRequest(&promocodev1.GetRedemptionHistoryRequest{OrgSlug: "acme"}))
	require.Error(t, err)
	assert.Equal(t, connect.CodeUnauthenticated, connectCodeOf(t, err))
}

// --- toProtoValidateResponse table ---

func mustParseTime(t *testing.T, s string) time.Time {
	t.Helper()
	tt, err := time.Parse(time.RFC3339, s)
	require.NoError(t, err)
	return tt
}

func TestToProtoValidateResponse_ValidPath(t *testing.T) {
	expires := mustParseTime(t, "2026-12-31T23:59:59Z")
	out := toProtoValidateResponse(&promocodesvc.ValidateResponse{
		Valid:           true,
		Code:            "WELCOME2026",
		PlanName:        "pro",
		PlanDisplayName: "Pro",
		DurationMonths:  3,
		ExpiresAt:       &expires,
	})
	require.NotNil(t, out)
	assert.True(t, out.GetValid())
	assert.Equal(t, "WELCOME2026", out.GetCode())
	assert.Equal(t, "pro", out.GetPlanName())
	assert.Equal(t, "Pro", out.GetPlanDisplayName())
	assert.Equal(t, int32(3), out.GetDurationMonths())
	assert.Equal(t, "2026-12-31T23:59:59Z", out.GetExpiresAt())
	assert.Empty(t, out.GetMessageCode(),
		"valid path should not carry a message_code")
}

func TestToProtoValidateResponse_InvalidPath(t *testing.T) {
	out := toProtoValidateResponse(&promocodesvc.ValidateResponse{
		Valid:       false,
		Code:        "BOGUS",
		MessageCode: promocodesvc.ErrCodeNotFound,
	})
	require.NotNil(t, out)
	assert.False(t, out.GetValid())
	assert.Equal(t, "promo_code_not_found", out.GetMessageCode())
	assert.Empty(t, out.GetPlanName(),
		"failure path should not set plan_name (optional absent)")
	assert.Nil(t, out.PlanName)
	assert.Nil(t, out.ExpiresAt)
}

func TestToProtoValidateResponse_OmitsZeroDuration(t *testing.T) {
	out := toProtoValidateResponse(&promocodesvc.ValidateResponse{
		Valid: false,
		Code:  "X",
	})
	require.NotNil(t, out)
	assert.Nil(t, out.DurationMonths,
		"zero DurationMonths must collapse to absent on wire")
}

// --- toProtoRedeemResponse table ---

func TestToProtoRedeemResponse_Success(t *testing.T) {
	end := mustParseTime(t, "2026-08-01T00:00:00Z")
	out := toProtoRedeemResponse(&promocodesvc.RedeemResponse{
		Success:        true,
		PlanName:       "pro",
		DurationMonths: 3,
		NewPeriodEnd:   end,
		MessageCode:    promocodesvc.ErrCodeRedeemSuccess,
	})
	require.NotNil(t, out)
	assert.True(t, out.GetSuccess())
	assert.Equal(t, "pro", out.GetPlanName())
	assert.Equal(t, int32(3), out.GetDurationMonths())
	assert.Equal(t, "2026-08-01T00:00:00Z", out.GetNewPeriodEnd())
	assert.Equal(t, "promo_code_redeem_success", out.GetMessageCode())
}

func TestToProtoRedeemResponse_NotOwnerFailure(t *testing.T) {
	out := toProtoRedeemResponse(&promocodesvc.RedeemResponse{
		Success:     false,
		MessageCode: promocodesvc.ErrCodeNotOwner,
	})
	require.NotNil(t, out)
	assert.False(t, out.GetSuccess())
	assert.Equal(t, "promo_code_not_owner", out.GetMessageCode())
	assert.Nil(t, out.PlanName)
	assert.Nil(t, out.NewPeriodEnd,
		"failure must not carry a fake new_period_end")
}

func TestToProtoRedeemResponse_OmitsZeroTime(t *testing.T) {
	out := toProtoRedeemResponse(&promocodesvc.RedeemResponse{
		Success:     false,
		MessageCode: "promo_code_invalid",
	})
	require.NotNil(t, out)
	assert.Nil(t, out.NewPeriodEnd,
		"zero NewPeriodEnd must collapse to absent on wire")
}

// --- toProtoRedemption table ---

func TestToProtoRedemption_Nil(t *testing.T) {
	assert.Nil(t, toProtoRedemption(nil))
}

func TestToProtoRedemption_AllFields(t *testing.T) {
	prevPlan := "free"
	prevEnd := mustParseTime(t, "2026-05-01T00:00:00Z")
	ip := "203.0.113.42"
	ua := "Mozilla/5.0"
	r := &promocodedomain.Redemption{
		ID:                1,
		PromoCodeID:       7,
		OrganizationID:    42,
		UserID:            100,
		PlanName:          "pro",
		DurationMonths:    3,
		PreviousPlanName:  &prevPlan,
		PreviousPeriodEnd: &prevEnd,
		NewPeriodEnd:      mustParseTime(t, "2026-08-01T00:00:00Z"),
		IPAddress:         &ip,
		UserAgent:         &ua,
		CreatedAt:         mustParseTime(t, "2026-05-12T13:16:10Z"),
	}
	out := toProtoRedemption(r)
	require.NotNil(t, out)
	assert.Equal(t, int64(1), out.GetId())
	assert.Equal(t, int64(7), out.GetPromoCodeId())
	assert.Equal(t, int64(42), out.GetOrganizationId())
	assert.Equal(t, int64(100), out.GetUserId())
	assert.Equal(t, "pro", out.GetPlanName())
	assert.Equal(t, int32(3), out.GetDurationMonths())
	assert.Equal(t, "free", out.GetPreviousPlanName())
	assert.Equal(t, "2026-05-01T00:00:00Z", out.GetPreviousPeriodEnd())
	assert.Equal(t, "2026-08-01T00:00:00Z", out.GetNewPeriodEnd())
	assert.Equal(t, "203.0.113.42", out.GetIpAddress())
	assert.Equal(t, "Mozilla/5.0", out.GetUserAgent())
	assert.Equal(t, "2026-05-12T13:16:10Z", out.GetCreatedAt())
}

func TestToProtoRedemption_OptionalsAbsent(t *testing.T) {
	r := &promocodedomain.Redemption{
		ID:             2,
		PromoCodeID:    8,
		OrganizationID: 43,
		UserID:         101,
		PlanName:       "enterprise",
		DurationMonths: 12,
		NewPeriodEnd:   mustParseTime(t, "2027-05-01T00:00:00Z"),
		CreatedAt:      mustParseTime(t, "2026-05-12T13:16:10Z"),
	}
	out := toProtoRedemption(r)
	require.NotNil(t, out)
	assert.Nil(t, out.PreviousPlanName, "absent previous_plan_name round-trips as nil")
	assert.Nil(t, out.PreviousPeriodEnd)
	assert.Nil(t, out.IpAddress)
	assert.Nil(t, out.UserAgent)
}
