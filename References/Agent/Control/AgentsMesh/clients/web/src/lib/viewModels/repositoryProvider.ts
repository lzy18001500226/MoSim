/**
 * RepositoryProviderData / ProviderRepositoryData — UI-side snake_case
 * projection used by the IDE Import Repository wizard which still talks to
 * the raw wasm bridge (`getUserCredentialService().list_repo_providers()`)
 * and consumes its snake_case JSON directly. New code consuming the
 * Connect adapter (lib/api/userRepositoryProvider.ts) should use the
 * proto types `RepositoryProvider` / `ProviderRepository` instead.
 */
export interface RepositoryProviderData {
  id: number;
  user_id?: number;
  provider_type: string;
  name: string;
  base_url: string;
  client_id?: string;
  has_client_id: boolean;
  has_bot_token: boolean;
  has_identity: boolean;
  is_default: boolean;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ProviderRepositoryData {
  id: string;
  name: string;
  slug: string;
  description: string;
  default_branch: string;
  visibility: string;
  http_clone_url: string;
  ssh_clone_url: string;
  web_url: string;
}
