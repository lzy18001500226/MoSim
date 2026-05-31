"use client";

import { ALL_SCOPES, SCOPE_LABEL_KEYS, SCOPE_DESCRIPTION_KEYS } from "./constants";
import type { TranslationFn } from "../GeneralSettings";

interface ScopeSelectorProps {
  selectedScopes: Set<string>;
  onToggle: (scope: string) => void;
  t: TranslationFn;
}

export function ScopeSelector({ selectedScopes, onToggle, t }: ScopeSelectorProps) {
  return (
    <div className="border border-border rounded-lg divide-y divide-border">
      {ALL_SCOPES.map((scope) => {
        const selected = selectedScopes.has(scope);
        return (
          <label
            key={scope}
            className="flex items-start gap-3 px-3 py-2.5 cursor-pointer hover:bg-muted/50 transition-colors first:rounded-t-lg last:rounded-b-lg"
          >
            <input
              type="checkbox"
              checked={selected}
              onChange={() => onToggle(scope)}
              className="mt-0.5 h-4 w-4 rounded border-border text-primary focus:ring-primary/30 cursor-pointer"
            />
            <div className="flex-1 min-w-0">
              <div className="text-sm font-medium">
                <code className="text-xs bg-muted px-1.5 py-0.5 rounded">{scope}</code>
                <span className="ml-2 text-sm">{t(SCOPE_LABEL_KEYS[scope])}</span>
              </div>
              <p className="text-xs text-muted-foreground mt-0.5">
                {t(SCOPE_DESCRIPTION_KEYS[scope])}
              </p>
            </div>
          </label>
        );
      })}
    </div>
  );
}
