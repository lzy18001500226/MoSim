// Facade re-export of the agent Connect-RPC adapter. Business code imports
// from here (or from the `@/lib/api` barrel) so the wire-shape layer stays
// internal to the facade boundary. Tests mock this path.

export {
  fromProtoAgent,
  listAgents,
  getAgent,
  getAgentConfigSchema,
  createCustomAgent,
  updateCustomAgent,
  deleteCustomAgent,
  listUserAgentConfigs,
  getUserAgentConfig,
  setUserAgentConfig,
  deleteUserAgentConfig,
  type CreateCustomAgentInput,
  type AgentData,
  type UserAgentConfigData,
  type ConfigField,
  type ConfigFieldOption,
  type ConfigSchema,
  type CredentialField,
} from "../connect/agentConnect";
