"use client";

import { useWorldStore } from "@/stores/world-store";
import { ENVIRONMENT_THEMES } from "@/lib/constants";

export function EnvironmentPicker() {
  const environment = useWorldStore((s) => s.environment);
  const setEnvironment = useWorldStore((s) => s.setEnvironment);

  return (
    <div className="space-y-2">
      <p className="text-xs font-bold text-[var(--color-text-muted)]">World Theme</p>
      <div className="grid grid-cols-2 gap-1.5">
        {ENVIRONMENT_THEMES.map((theme) => (
          <button
            key={theme.id}
            onClick={() =>
              setEnvironment({
                theme: theme.id,
                skyColor: theme.skyColor,
                groundColor: theme.groundColor,
              })
            }
            className={`px-2 py-1.5 text-xs rounded-lg border transition-all ${
              environment.theme === theme.id
                ? "border-[var(--color-primary)] bg-[var(--color-primary)]/10 font-bold"
                : "border-gray-200 hover:border-gray-300"
            }`}
          >
            {theme.label}
          </button>
        ))}
      </div>
    </div>
  );
}
