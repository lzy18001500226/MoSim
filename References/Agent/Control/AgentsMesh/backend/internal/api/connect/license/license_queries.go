package licenseconnect

import (
	"context"
	"errors"

	"connectrpc.com/connect"

	licensev1 "github.com/anthropics/agentsmesh/proto/gen/go/license/v1"
)

// LicensePublicService — read-only queries. No auth interceptor. Returns
// CodeUnavailable when the OnPremise license subsystem isn't initialized
// (mirrors REST's apierr.ServiceUnavailable from license_status.go).

func (p *PublicServer) GetLicenseStatus(
	_ context.Context, _ *connect.Request[licensev1.GetLicenseStatusRequest],
) (*connect.Response[licensev1.LicenseStatus], error) {
	if err := requireLicenseService(p.licenseSvc); err != nil {
		return nil, err
	}
	return connect.NewResponse(toProtoStatus(p.licenseSvc.GetLicenseStatus())), nil
}

func (p *PublicServer) GetLicenseLimits(
	_ context.Context, _ *connect.Request[licensev1.GetLicenseLimitsRequest],
) (*connect.Response[licensev1.LicenseLimitsResponse], error) {
	if err := requireLicenseService(p.licenseSvc); err != nil {
		return nil, err
	}
	licenseData := p.licenseSvc.GetCurrentLicense()
	if licenseData == nil {
		return nil, connect.NewError(
			connect.CodeNotFound,
			errors.New("no active license"),
		)
	}
	return connect.NewResponse(&licensev1.LicenseLimitsResponse{
		Limits: toProtoLimits(licenseData.Limits),
		Plan:   licenseData.Plan,
	}), nil
}

func (p *PublicServer) CheckFeature(
	_ context.Context, req *connect.Request[licensev1.CheckFeatureRequest],
) (*connect.Response[licensev1.CheckFeatureResponse], error) {
	if err := requireLicenseService(p.licenseSvc); err != nil {
		return nil, err
	}
	feature := req.Msg.GetFeature()
	if feature == "" {
		return nil, connect.NewError(
			connect.CodeInvalidArgument,
			errors.New("feature is required"),
		)
	}
	return connect.NewResponse(&licensev1.CheckFeatureResponse{
		Feature: feature,
		Enabled: p.licenseSvc.HasFeature(feature),
	}), nil
}
