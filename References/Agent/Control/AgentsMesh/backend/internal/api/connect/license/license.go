// Package licenseconnect hosts Connect-RPC handlers for the OnPremise
// license domain. Mirrors backend/internal/api/rest/v1/license*.go but
// exposes the data plane via Connect (binary protobuf wire, see
// conventions §2.5).
//
// Auth model — TWO services, two surfaces:
//
//   * LicenseService (auth-required): ActivateLicense / RefreshLicense /
//     ValidateLicense. The auth interceptor enforces a valid JWT. REST
//     additionally gated these on `tenant.UserRole == "owner"` when a
//     tenant context was present; the Connect handler re-creates that
//     policy below (requireOwner helper). When no tenant context exists
//     (initial OnPremise activation before any org is created), the
//     valid JWT is the bar — same behavior as REST.
//
//   * LicensePublicService (no auth): GetLicenseStatus /
//     GetLicenseLimits / CheckFeature. The login page hits these
//     before any token exists, so the auth interceptor is bypassed via
//     a separate Mount function (mirrors billing public pricing,
//     conventions §3.5 exception #1).
//
// System-wide, not org-scoped (conventions §3.5 EXCEPTION): one license
// per server, no per-org licenses. No `org_slug` field on any request.
//
// REST handler stays mounted in parallel — dual-track until consumers
// flip lanes.
package licenseconnect

import (
	"context"
	"errors"
	"net/http"

	"connectrpc.com/connect"

	"github.com/anthropics/agentsmesh/backend/internal/middleware"
	licenseservice "github.com/anthropics/agentsmesh/backend/internal/service/license"
)

const (
	ServiceName       = "proto.license.v1.LicenseService"
	PublicServiceName = "proto.license.v1.LicensePublicService"
)

const (
	ActivateLicenseProcedure = "/" + ServiceName + "/ActivateLicense"
	RefreshLicenseProcedure  = "/" + ServiceName + "/RefreshLicense"
	ValidateLicenseProcedure = "/" + ServiceName + "/ValidateLicense"

	GetLicenseStatusProcedure = "/" + PublicServiceName + "/GetLicenseStatus"
	GetLicenseLimitsProcedure = "/" + PublicServiceName + "/GetLicenseLimits"
	CheckFeatureProcedure     = "/" + PublicServiceName + "/CheckFeature"
)

// Server implements the auth-required LicenseService contract.
type Server struct {
	licenseSvc *licenseservice.Service
}

func NewServer(licenseSvc *licenseservice.Service) *Server {
	return &Server{licenseSvc: licenseSvc}
}

// PublicServer implements the unauthenticated LicensePublicService contract.
type PublicServer struct {
	licenseSvc *licenseservice.Service
}

func NewPublicServer(licenseSvc *licenseservice.Service) *PublicServer {
	return &PublicServer{licenseSvc: licenseSvc}
}

// requireLicenseService enforces the "license service not configured" guard
// REST handlers replicated on every entry point. Returns CodeUnavailable
// when the OnPremise license subsystem wasn't initialized (no public key,
// no repo, etc.) — mirrors apierr.ServiceUnavailable from REST.
func requireLicenseService(svc *licenseservice.Service) error {
	if svc == nil {
		return connect.NewError(
			connect.CodeUnavailable,
			errors.New("license service not configured"),
		)
	}
	return nil
}

// requireOwner re-creates the REST owner-role gate from license_activation.go.
// When a tenant context exists (typical: caller flows through the org-scoped
// REST interceptor), the role must be "owner". When no tenant context
// exists (initial activation before any org is created), the valid JWT
// from the auth interceptor is the bar — same fall-through as REST.
func requireOwner(ctx context.Context) error {
	tenant := middleware.GetTenant(ctx)
	if tenant == nil {
		return nil
	}
	if tenant.UserRole != "" && tenant.UserRole != "owner" {
		return connect.NewError(
			connect.CodePermissionDenied,
			errors.New("only organization owner can manage licenses"),
		)
	}
	return nil
}

// Mount registers auth-required LicenseService procedures behind the auth
// interceptor supplied via opts (cmd/server/connect_init.go).
func Mount(mux *http.ServeMux, srv *Server, opts ...connect.HandlerOption) {
	mux.Handle(ActivateLicenseProcedure, connect.NewUnaryHandler(
		ActivateLicenseProcedure, srv.ActivateLicense, opts...,
	))
	mux.Handle(RefreshLicenseProcedure, connect.NewUnaryHandler(
		RefreshLicenseProcedure, srv.RefreshLicense, opts...,
	))
	mux.Handle(ValidateLicenseProcedure, connect.NewUnaryHandler(
		ValidateLicenseProcedure, srv.ValidateLicense, opts...,
	))
}

// MountPublic registers LicensePublicService procedures WITHOUT the auth
// interceptor. Mirrors billing.MountPublic — token IS optional (no JWT
// required for read-only license inspection from the login page).
func MountPublic(mux *http.ServeMux, srv *PublicServer, opts ...connect.HandlerOption) {
	mux.Handle(GetLicenseStatusProcedure, connect.NewUnaryHandler(
		GetLicenseStatusProcedure, srv.GetLicenseStatus, opts...,
	))
	mux.Handle(GetLicenseLimitsProcedure, connect.NewUnaryHandler(
		GetLicenseLimitsProcedure, srv.GetLicenseLimits, opts...,
	))
	mux.Handle(CheckFeatureProcedure, connect.NewUnaryHandler(
		CheckFeatureProcedure, srv.CheckFeature, opts...,
	))
}
