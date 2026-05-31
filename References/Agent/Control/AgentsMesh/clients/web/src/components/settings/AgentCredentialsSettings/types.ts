import type { AgentData } from "@/lib/api";
import type { CredentialProfileViewModel, CredentialProfilesByAgent } from "../_shared/credentialViewModel";

export interface AgentCredentialsState {
  loading: boolean;
  error: string | null;
  success: string | null;
  profilesByAgent: CredentialProfilesByAgent[];
  agents: AgentData[];
  expandedAgents: Set<string>;
  agentsWithoutPrimaryBundle: Set<string>;
}

export interface AgentCredentialsActions {
  toggleAgent: (agentSlug: string) => void;
  handleClearPrimaryBundle: (agentSlug: string) => Promise<void>;
  handleSetDefault: (profileId: number) => Promise<void>;
  handleDelete: (profileId: number) => Promise<void>;
  handleSaveProfile: (
    agentSlug: string,
    data: CredentialFormData,
    editingProfile: CredentialProfileViewModel | null
  ) => Promise<void>;
  getProfilesForAgent: (agentSlug: string) => CredentialProfileViewModel[];
  setError: (error: string | null) => void;
  setSuccess: (success: string | null) => void;
}

// credentials key = full ENV name, value = user input
export interface CredentialFormData {
  name: string;
  description: string;
  credentials: Record<string, string>;
}

export interface AgentItemProps {
  agent: AgentData;
  profiles: CredentialProfileViewModel[];
  isExpanded: boolean;
  noPrimaryBundle: boolean;
  onToggle: () => void;
  onClearPrimary: () => Promise<void>;
  onSetDefault: (profileId: number) => Promise<void>;
  onEdit: (profile: CredentialProfileViewModel) => void;
  onDelete: (profileId: number) => Promise<void>;
  onAdd: () => void;
  t: (key: string) => string;
}

export interface CredentialProfileDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  agentSlug: string;
  editingProfile: CredentialProfileViewModel | null;
  onSubmit: (data: CredentialFormData) => Promise<void>;
  t: (key: string) => string;
}
