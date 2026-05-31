package ssoadminconnect

import (
	ssoservice "github.com/anthropics/agentsmesh/backend/internal/service/sso"
	ssov1 "github.com/anthropics/agentsmesh/proto/gen/go/sso/v1"
)

// toProtoAdminSSOConfig mirrors REST's `ToConfigResponse` output (the
// secret-stripped admin GET payload). The service has already filtered
// cross-protocol fields — we just transcribe non-empty/non-nil values
// onto the proto optional fields, matching REST's `omitempty` semantics.
//
// Empty strings on the input ConfigResponse are dropped because REST's
// `omitempty` JSON tag does the same — keeps the wire shape identical
// between the two transports.
func toProtoAdminSSOConfig(r *ssoservice.ConfigResponse) *ssov1.AdminSSOConfig {
	if r == nil {
		return nil
	}
	out := &ssov1.AdminSSOConfig{
		Id:         r.ID,
		Domain:     r.Domain,
		Name:       r.Name,
		Protocol:   r.Protocol,
		IsEnabled:  r.IsEnabled,
		EnforceSso: r.EnforceSSO,
		CreatedAt:  r.CreatedAt,
		UpdatedAt:  r.UpdatedAt,
	}
	setStringPtr(&out.OidcIssuerUrl, r.OIDCIssuerURL)
	setStringPtr(&out.OidcClientId, r.OIDCClientID)
	setStringPtr(&out.OidcScopes, r.OIDCScopes)

	setStringPtr(&out.SamlIdpMetadataUrl, r.SAMLIDPMetadataURL)
	setStringPtr(&out.SamlIdpSsoUrl, r.SAMLIDPSSOURL)
	setStringPtr(&out.SamlSpEntityId, r.SAMLSPEntityID)
	setStringPtr(&out.SamlNameIdFormat, r.SAMLNameIDFormat)

	setStringPtr(&out.LdapHost, r.LDAPHost)
	if r.LDAPPort != nil {
		v := int32(*r.LDAPPort)
		out.LdapPort = &v
	}
	if r.LDAPUseTLS != nil {
		v := *r.LDAPUseTLS
		out.LdapUseTls = &v
	}
	setStringPtr(&out.LdapBindDn, r.LDAPBindDN)
	setStringPtr(&out.LdapBaseDn, r.LDAPBaseDN)
	setStringPtr(&out.LdapUserFilter, r.LDAPUserFilter)
	setStringPtr(&out.LdapEmailAttr, r.LDAPEmailAttr)
	setStringPtr(&out.LdapNameAttr, r.LDAPNameAttr)
	setStringPtr(&out.LdapUsernameAttr, r.LDAPUsernameAttr)

	if r.CreatedBy != nil {
		v := *r.CreatedBy
		out.CreatedBy = &v
	}
	return out
}

// setStringPtr copies a non-empty value into a *string field, leaving it
// nil for empty strings to mirror REST's `omitempty` JSON semantics.
func setStringPtr(dst **string, v string) {
	if v == "" {
		return
	}
	dst2 := v
	*dst = &dst2
}

// fromCreateRequest transcribes the proto CreateSSOConfigRequest onto the
// service's CreateConfigRequest. Proto `optional` fields → service
// pointer-or-empty-string mapping: the service struct uses zero-value
// strings (not pointers), so we dereference when set and leave empty
// otherwise. The service validates required fields per protocol.
func fromCreateRequest(req *ssov1.CreateSSOConfigRequest) *ssoservice.CreateConfigRequest {
	return &ssoservice.CreateConfigRequest{
		Domain:             req.GetDomain(),
		Name:               req.GetName(),
		Protocol:           req.GetProtocol(),
		IsEnabled:          req.GetIsEnabled(),
		EnforceSSO:         req.GetEnforceSso(),
		OIDCIssuerURL:      req.GetOidcIssuerUrl(),
		OIDCClientID:       req.GetOidcClientId(),
		OIDCClientSecret:   req.GetOidcClientSecret(),
		OIDCScopes:         req.GetOidcScopes(),
		SAMLIDPMetadataURL: req.GetSamlIdpMetadataUrl(),
		SAMLIDPMetadataXML: req.GetSamlIdpMetadataXml(),
		SAMLIDPSSOURL:      req.GetSamlIdpSsoUrl(),
		SAMLIDPCert:        req.GetSamlIdpCert(),
		SAMLSPEntityID:     req.GetSamlSpEntityId(),
		SAMLNameIDFormat:   req.GetSamlNameIdFormat(),
		LDAPHost:           req.GetLdapHost(),
		LDAPPort:           int(req.GetLdapPort()),
		LDAPUseTLS:         req.GetLdapUseTls(),
		LDAPBindDN:         req.GetLdapBindDn(),
		LDAPBindPassword:   req.GetLdapBindPassword(),
		LDAPBaseDN:         req.GetLdapBaseDn(),
		LDAPUserFilter:     req.GetLdapUserFilter(),
		LDAPEmailAttr:      req.GetLdapEmailAttr(),
		LDAPNameAttr:       req.GetLdapNameAttr(),
		LDAPUsernameAttr:   req.GetLdapUsernameAttr(),
	}
}

// fromUpdateRequest maps every proto-optional field onto a *T on the
// service struct. nil-on-proto → nil-on-service (leave alone). Pointer
// presence on the service struct drives buildUpdateMap's
// "only-set-fields-update" semantics; we preserve that.
func fromUpdateRequest(req *ssov1.UpdateSSOConfigRequest) *ssoservice.UpdateConfigRequest {
	out := &ssoservice.UpdateConfigRequest{
		Name:               req.Name,
		IsEnabled:          req.IsEnabled,
		EnforceSSO:         req.EnforceSso,
		OIDCIssuerURL:      req.OidcIssuerUrl,
		OIDCClientID:       req.OidcClientId,
		OIDCClientSecret:   req.OidcClientSecret,
		OIDCScopes:         req.OidcScopes,
		SAMLIDPMetadataURL: req.SamlIdpMetadataUrl,
		SAMLIDPMetadataXML: req.SamlIdpMetadataXml,
		SAMLIDPSSOURL:      req.SamlIdpSsoUrl,
		SAMLIDPCert:        req.SamlIdpCert,
		SAMLSPEntityID:     req.SamlSpEntityId,
		SAMLNameIDFormat:   req.SamlNameIdFormat,
		LDAPHost:           req.LdapHost,
		LDAPUseTLS:         req.LdapUseTls,
		LDAPBindDN:         req.LdapBindDn,
		LDAPBindPassword:   req.LdapBindPassword,
		LDAPBaseDN:         req.LdapBaseDn,
		LDAPUserFilter:     req.LdapUserFilter,
		LDAPEmailAttr:      req.LdapEmailAttr,
		LDAPNameAttr:       req.LdapNameAttr,
		LDAPUsernameAttr:   req.LdapUsernameAttr,
	}
	if req.LdapPort != nil {
		v := int(*req.LdapPort)
		out.LDAPPort = &v
	}
	return out
}
