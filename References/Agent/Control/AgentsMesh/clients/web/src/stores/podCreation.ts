import { create } from "zustand";
import { persist } from "zustand/middleware";

/**
 * Pod creation preferences - remembers last user choices.
 *
 * EnvBundle preferences are split by kind to mirror the dialog UI:
 *   - `lastCredentialName`: single-select pick (empty = "use Agent default")
 *   - `lastRuntimeBundleNames`: ordered list of runtime bundle names
 *
 * Names (not IDs) are stored because bundle names are stable across
 * rename/recreate while IDs are not.
 */
interface PodCreationPreferences {
  lastAgentSlug: string | null;
  lastRepositoryId: number | null;
  lastCredentialName: string;
  lastRuntimeBundleNames: string[];
  lastBranchName: string | null;

  setLastChoices: (
    choices: Partial<
      Pick<
        PodCreationPreferences,
        | "lastAgentSlug"
        | "lastRepositoryId"
        | "lastCredentialName"
        | "lastRuntimeBundleNames"
        | "lastBranchName"
      >
    >
  ) => void;
  clearLastChoices: () => void;

  // Hydration state for SSR
  _hasHydrated: boolean;
  setHasHydrated: (state: boolean) => void;
}

export const usePodCreationStore = create<PodCreationPreferences>()(
  persist(
    (set) => ({
      lastAgentSlug: null,
      lastRepositoryId: null,
      lastCredentialName: "",
      lastRuntimeBundleNames: [],
      lastBranchName: null,

      setLastChoices: (choices) => set((state) => ({ ...state, ...choices })),
      clearLastChoices: () =>
        set({
          lastAgentSlug: null,
          lastRepositoryId: null,
          lastCredentialName: "",
          lastRuntimeBundleNames: [],
          lastBranchName: null,
        }),

      // Hydration
      _hasHydrated: false,
      setHasHydrated: (state) => set({ _hasHydrated: state }),
    }),
    {
      name: "agentsmesh-pod-creation",
      version: 3,
      // v1 stored `lastBundleName: string | null`; v2 unified into
      // `lastBundleNames: string[]`; v3 splits back into credential
      // (single) + runtime (multi) to match the dialog UI. Legacy values
      // are dropped — we can't classify a name without re-querying the
      // bundle list, and the user will see their primary bundles
      // re-applied on next agent select anyway.
      migrate: (persistedState: unknown, version: number) => {
        const s = (persistedState as Record<string, unknown>) ?? {};
        if (version < 3) {
          delete s.lastBundleName;
          delete s.lastBundleNames;
          s.lastCredentialName = "";
          s.lastRuntimeBundleNames = [];
        }
        return s as unknown as PodCreationPreferences;
      },
      partialize: (state) => ({
        lastAgentSlug: state.lastAgentSlug,
        lastRepositoryId: state.lastRepositoryId,
        lastCredentialName: state.lastCredentialName,
        lastRuntimeBundleNames: state.lastRuntimeBundleNames,
        lastBranchName: state.lastBranchName,
      }),
      onRehydrateStorage: () => (state) => {
        state?.setHasHydrated(true);
      },
    }
  )
);
