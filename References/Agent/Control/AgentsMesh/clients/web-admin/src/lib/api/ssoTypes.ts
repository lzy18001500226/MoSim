// Types for the SSO admin adapter. Snake-case shape preserved from the
// REST surface so the page components don't have to change as we flip
// transport. Write-only secrets (oidc_client_secret, saml_idp_cert,
// saml_idp_metadata_xml, ldap_bind_password) appear on
// CreateSSOConfigRequest / UpdateSSOConfigRequest only — never on the
// SSOConfig response.

export type SSOProtocol = "oidc" | "saml" | "ldap";

export interface SSOConfig {
  id: number;
  domain: string;
  name: string;
  protocol: SSOProtocol;
  is_enabled: boolean;
  enforce_sso: boolean;
  // OIDC
  oidc_issuer_url?: string;
  oidc_client_id?: string;
  oidc_scopes?: string;
  // SAML
  saml_idp_metadata_url?: string;
  saml_idp_sso_url?: string;
  saml_sp_entity_id?: string;
  saml_name_id_format?: string;
  // LDAP
  ldap_host?: string;
  ldap_port?: number;
  ldap_use_tls?: boolean;
  ldap_bind_dn?: string;
  ldap_base_dn?: string;
  ldap_user_filter?: string;
  ldap_email_attr?: string;
  ldap_name_attr?: string;
  ldap_username_attr?: string;
  created_at: string;
  updated_at: string;
}

export interface SSOConfigListParams {
  search?: string;
  protocol?: SSOProtocol;
  is_enabled?: boolean;
  page?: number;
  page_size?: number;
}

export interface CreateSSOConfigRequest {
  domain: string;
  name: string;
  protocol: SSOProtocol;
  is_enabled?: boolean;
  enforce_sso?: boolean;
  // OIDC
  oidc_issuer_url?: string;
  oidc_client_id?: string;
  oidc_client_secret?: string;
  oidc_scopes?: string;
  // SAML
  saml_idp_metadata_url?: string;
  saml_idp_metadata_xml?: string;
  saml_idp_sso_url?: string;
  saml_idp_cert?: string;
  saml_sp_entity_id?: string;
  saml_name_id_format?: string;
  // LDAP
  ldap_host?: string;
  ldap_port?: number;
  ldap_use_tls?: boolean;
  ldap_bind_dn?: string;
  ldap_bind_password?: string;
  ldap_base_dn?: string;
  ldap_user_filter?: string;
  ldap_email_attr?: string;
  ldap_name_attr?: string;
  ldap_username_attr?: string;
}

export type UpdateSSOConfigRequest = Partial<CreateSSOConfigRequest>;

export interface SSOTestResult {
  success: boolean;
  message?: string;
  error?: string;
}
