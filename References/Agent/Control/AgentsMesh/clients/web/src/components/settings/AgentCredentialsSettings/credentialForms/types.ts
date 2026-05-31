export type CredentialFieldKind = "text" | "secret";

export interface SimpleCredentialField {
  kind: CredentialFieldKind;
  envKey: string;
  label: string;
  description?: string;
  placeholder?: string;
}

export interface OneOfOption {
  kind: CredentialFieldKind;
  envKey: string;
  label: string;
  placeholder?: string;
}

export interface OneOfCredentialField {
  kind: "oneof";
  group: string;
  label: string;
  description?: string;
  options: OneOfOption[];
}

export type CredentialFieldSpec = SimpleCredentialField | OneOfCredentialField;

export interface CredentialFormSpec {
  agentSlug: string;
  fields: CredentialFieldSpec[];
  allowCustomEnv: boolean;
  customEnvHint?: string;
}

export interface CustomEnvEntry {
  id: string;
  key: string;
  value: string;
}
