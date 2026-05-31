/**
 * EnvBundleSummary — UI-side compact projection of `proto.env_bundle.v1.EnvBundle`.
 * Picker / multi-select widgets only need name + agent_slug + kind + flags,
 * not the full bundle body. snake_case + `number` id stays for legacy
 * components; new components should consume `proto.EnvBundle` directly.
 */
export interface EnvBundleSummary {
  id: number;
  name: string;
  agent_slug?: string | null;
  kind: string;
  kind_primary: boolean;
  configured_fields?: string[];
}
