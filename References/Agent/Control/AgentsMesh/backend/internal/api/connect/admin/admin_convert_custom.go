package adminconnect

import (
	"encoding/json"

	"github.com/anthropics/agentsmesh/backend/internal/domain/admin"
	"github.com/anthropics/agentsmesh/backend/internal/domain/organization"
	domainrunner "github.com/anthropics/agentsmesh/backend/internal/domain/runner"
	"github.com/anthropics/agentsmesh/backend/internal/domain/user"
	adminv1 "github.com/anthropics/agentsmesh/proto/gen/go/admin/v1"
)

// userSummaryToProto is field_custom helper for the embedded user pointer in
// AdminOrganizationMember and AdminAuditLog. Codegen passes the preloaded
// *user.User association directly.
func userSummaryToProto(u *user.User) *adminv1.AdminUserSummary {
	return ToProtoAdminUserSummary(u)
}

// auditActionToProto casts the typed AuditAction (string alias) to wire string.
func auditActionToProto(a admin.AuditAction) string {
	return string(a)
}

// targetTypeToProto casts the typed TargetType (string alias) to wire string.
func targetTypeToProto(t admin.TargetType) string {
	return string(t)
}

// toProtoAdminRunner attaches the optional organization summary onto the
// codegen-generated AdminRunner. The Runner table doesn't preload its
// Organization so it's passed as a second arg by the handler.
func toProtoAdminRunner(r *domainrunner.Runner, org *organization.Organization) *adminv1.AdminRunner {
	out := ToProtoAdminRunner(r)
	if out == nil {
		return nil
	}
	if org != nil {
		out.Organization = ToProtoAdminOrganizationSummary(org)
	}
	return out
}

// adminDescriptionToProto flips empty string → nil pointer (REST omits
// `description` when empty; proto field is optional).
func adminDescriptionToProto(s string) *string {
	if s == "" {
		return nil
	}
	v := s
	return &v
}

// adminStringSliceToProto unwraps the domain StringSlice alias into wire []string.
func adminStringSliceToProto(s domainrunner.StringSlice) []string {
	if s == nil {
		return nil
	}
	return []string(s)
}

// adminHostInfoToProto returns nil pointer when the host map is empty so the
// wire field is absent (parity with the REST omitempty behavior).
func adminHostInfoToProto(hi domainrunner.HostInfo) *string {
	if len(hi) == 0 {
		return nil
	}
	b, err := json.Marshal(hi)
	if err != nil {
		return nil
	}
	v := string(b)
	return &v
}
