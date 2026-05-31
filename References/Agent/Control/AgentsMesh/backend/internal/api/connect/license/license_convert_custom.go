package licenseconnect

import (
	"github.com/anthropics/agentsmesh/backend/internal/domain/billing"
	licenseservice "github.com/anthropics/agentsmesh/backend/internal/service/license"
	licensev1 "github.com/anthropics/agentsmesh/proto/gen/go/license/v1"
)

// toProtoStatus — codegen-backed thin alias. Phase 12 M7.
// Preserves original empty-shape behaviour: nil input returns a default
// LicenseStatus instead of nil, so REST callers receive a shaped JSON object.
func toProtoStatus(s *billing.LicenseStatus) *licensev1.LicenseStatus {
	if s == nil {
		return &licensev1.LicenseStatus{}
	}
	return ToProtoLicenseStatus(s)
}

// toProtoLimits — codegen-backed alias. LicenseLimits travels by value in the
// service layer; the codegen takes a pointer, so we box for the call.
func toProtoLimits(l licenseservice.LicenseLimits) *licensev1.LicenseLimits {
	return ToProtoLicenseLimits(&l)
}

// toProtoValidated — codegen-backed thin alias with derived `valid` flag.
// `valid` is not a field of LicenseData (it's "this preview parsed and
// verified") so the wrapper sets it; everything else routes through codegen.
func toProtoValidated(l *licenseservice.LicenseData) *licensev1.ValidatedLicense {
	if l == nil {
		return &licensev1.ValidatedLicense{Valid: false}
	}
	out := ToProtoValidatedLicense(l)
	out.Valid = true
	return out
}

// limitsValueToProto is the field_custom helper for ValidatedLicense.limits —
// the domain `Limits` is a value-type LicenseLimits but the proto wire shape
// is a pointer. Boxing once here keeps the codegen template simple.
func limitsValueToProto(l licenseservice.LicenseLimits) *licensev1.LicenseLimits {
	return ToProtoLicenseLimits(&l)
}

// limitsValueFromProto is the inverse — proto pointer → domain value.
func limitsValueFromProto(p *licensev1.LicenseLimits) licenseservice.LicenseLimits {
	d := FromProtoLicenseLimits(p)
	if d == nil {
		return licenseservice.LicenseLimits{}
	}
	return *d
}
