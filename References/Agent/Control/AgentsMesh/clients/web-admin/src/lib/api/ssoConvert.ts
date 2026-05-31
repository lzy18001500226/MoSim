// Proto ↔ TS DTO conversion for the SSO admin adapter. Keeps sso.ts
// itself under the 200-line cap by hosting the field-by-field mapping
// here.
//
// Direction is one-way: ProtoAdminSSOConfig → SSOConfig (the wire
// response) and SSOConfig request payloads → MessageInit init shape for
// callConnect. The Create / Update request builders are colocated here
// for the same reason.
import type { MessageInitShape } from "@bufbuild/protobuf";

import type {
  AdminSSOConfig as ProtoAdminSSOConfig,
  CreateSSOConfigRequestSchema,
  UpdateSSOConfigRequestSchema,
} from "@proto/sso/v1/sso_admin_pb";

import type {
  CreateSSOConfigRequest,
  SSOConfig,
  SSOProtocol,
  UpdateSSOConfigRequest,
} from "./ssoTypes";

export function fromProto(c: ProtoAdminSSOConfig): SSOConfig {
  return {
    id: Number(c.id),
    domain: c.domain,
    name: c.name,
    protocol: c.protocol as SSOProtocol,
    is_enabled: c.isEnabled,
    enforce_sso: c.enforceSso,
    oidc_issuer_url: c.oidcIssuerUrl,
    oidc_client_id: c.oidcClientId,
    oidc_scopes: c.oidcScopes,
    saml_idp_metadata_url: c.samlIdpMetadataUrl,
    saml_idp_sso_url: c.samlIdpSsoUrl,
    saml_sp_entity_id: c.samlSpEntityId,
    saml_name_id_format: c.samlNameIdFormat,
    ldap_host: c.ldapHost,
    ldap_port: c.ldapPort,
    ldap_use_tls: c.ldapUseTls,
    ldap_bind_dn: c.ldapBindDn,
    ldap_base_dn: c.ldapBaseDn,
    ldap_user_filter: c.ldapUserFilter,
    ldap_email_attr: c.ldapEmailAttr,
    ldap_name_attr: c.ldapNameAttr,
    ldap_username_attr: c.ldapUsernameAttr,
    created_at: c.createdAt,
    updated_at: c.updatedAt,
  };
}

export function buildCreateInit(
  data: CreateSSOConfigRequest,
): MessageInitShape<typeof CreateSSOConfigRequestSchema> {
  return {
    domain: data.domain,
    name: data.name,
    protocol: data.protocol,
    isEnabled: data.is_enabled ?? false,
    enforceSso: data.enforce_sso ?? false,
    oidcIssuerUrl: data.oidc_issuer_url,
    oidcClientId: data.oidc_client_id,
    oidcClientSecret: data.oidc_client_secret,
    oidcScopes: data.oidc_scopes,
    samlIdpMetadataUrl: data.saml_idp_metadata_url,
    samlIdpMetadataXml: data.saml_idp_metadata_xml,
    samlIdpSsoUrl: data.saml_idp_sso_url,
    samlIdpCert: data.saml_idp_cert,
    samlSpEntityId: data.saml_sp_entity_id,
    samlNameIdFormat: data.saml_name_id_format,
    ldapHost: data.ldap_host,
    ldapPort: data.ldap_port,
    ldapUseTls: data.ldap_use_tls,
    ldapBindDn: data.ldap_bind_dn,
    ldapBindPassword: data.ldap_bind_password,
    ldapBaseDn: data.ldap_base_dn,
    ldapUserFilter: data.ldap_user_filter,
    ldapEmailAttr: data.ldap_email_attr,
    ldapNameAttr: data.ldap_name_attr,
    ldapUsernameAttr: data.ldap_username_attr,
  };
}

export function buildUpdateInit(
  id: number,
  data: UpdateSSOConfigRequest,
): MessageInitShape<typeof UpdateSSOConfigRequestSchema> {
  return {
    id: BigInt(id),
    name: data.name,
    isEnabled: data.is_enabled,
    enforceSso: data.enforce_sso,
    oidcIssuerUrl: data.oidc_issuer_url,
    oidcClientId: data.oidc_client_id,
    oidcClientSecret: data.oidc_client_secret,
    oidcScopes: data.oidc_scopes,
    samlIdpMetadataUrl: data.saml_idp_metadata_url,
    samlIdpMetadataXml: data.saml_idp_metadata_xml,
    samlIdpSsoUrl: data.saml_idp_sso_url,
    samlIdpCert: data.saml_idp_cert,
    samlSpEntityId: data.saml_sp_entity_id,
    samlNameIdFormat: data.saml_name_id_format,
    ldapHost: data.ldap_host,
    ldapPort: data.ldap_port,
    ldapUseTls: data.ldap_use_tls,
    ldapBindDn: data.ldap_bind_dn,
    ldapBindPassword: data.ldap_bind_password,
    ldapBaseDn: data.ldap_base_dn,
    ldapUserFilter: data.ldap_user_filter,
    ldapEmailAttr: data.ldap_email_attr,
    ldapNameAttr: data.ldap_name_attr,
    ldapUsernameAttr: data.ldap_username_attr,
  };
}
