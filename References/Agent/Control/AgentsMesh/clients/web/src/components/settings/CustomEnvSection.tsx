"use client";

import { useCallback } from "react";
import { Trash2, Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import type { CustomEnvEntry } from "./AgentCredentialsSettings/credentialForms/types";

const ENV_NAME_PATTERN = /^[A-Z_][A-Z0-9_]*$/;

interface CustomEnvSectionProps {
  title: string;
  hint?: string;
  entries: CustomEnvEntry[];
  declaredKeys: Set<string>;
  onChange: (entries: CustomEnvEntry[]) => void;
  isEditing: boolean;
  t: (key: string) => string;
  /**
   * "password" (default) masks the value input — credential kind never echoes
   * secrets back. "text" shows the value in plaintext — used by runtime kind
   * (non-secret preferences like `OPENAI_MODEL`) where the backend round-trips
   * the value via `configured_values`.
   */
  valueType?: "password" | "text";
}

function newId(): string {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
}

function validateKey(
  key: string,
  declaredKeys: Set<string>,
  entries: CustomEnvEntry[],
  currentId: string
): string | undefined {
  const trimmed = key.trim();
  if (!trimmed) return undefined;
  if (!ENV_NAME_PATTERN.test(trimmed)) return "keyInvalid";
  if (declaredKeys.has(trimmed)) return "keyConflict";
  const dup = entries.some((e) => e.id !== currentId && e.key.trim() === trimmed);
  if (dup) return "keyDuplicate";
  return undefined;
}

export function CustomEnvSection({
  title,
  hint,
  entries,
  declaredKeys,
  onChange,
  isEditing,
  t,
  valueType = "password",
}: CustomEnvSectionProps) {
  const update = useCallback(
    (id: string, patch: Partial<CustomEnvEntry>) => {
      onChange(entries.map((e) => (e.id === id ? { ...e, ...patch } : e)));
    },
    [entries, onChange]
  );

  const remove = useCallback(
    (id: string) => onChange(entries.filter((e) => e.id !== id)),
    [entries, onChange]
  );

  const add = useCallback(
    () => onChange([...entries, { id: newId(), key: "", value: "" }]),
    [entries, onChange]
  );

  return (
    <div className="grid gap-3 border-t border-border pt-4 mt-2">
      <div className="flex items-baseline justify-between">
        <Label className="text-sm font-medium">{title}</Label>
        {hint && <span className="text-xs text-muted-foreground">{hint}</span>}
      </div>
      {entries.map((entry) => {
        const keyErr = validateKey(entry.key, declaredKeys, entries, entry.id);
        return (
          <div key={entry.id} className="grid gap-1">
            <div className="flex items-start gap-2">
              <div className="flex-1 grid gap-1">
                <Input
                  aria-label={t("settings.credentialForm.customEnv.keyPlaceholder")}
                  value={entry.key}
                  onChange={(e) => update(entry.id, { key: e.target.value.toUpperCase() })}
                  placeholder={t("settings.credentialForm.customEnv.keyPlaceholder")}
                  className="font-mono text-sm"
                />
              </div>
              <span className="pt-2 text-muted-foreground">=</span>
              <div className="flex-1 grid gap-1">
                <Input
                  aria-label={t("settings.credentialForm.customEnv.valuePlaceholder")}
                  type={valueType}
                  value={entry.value}
                  onChange={(e) => update(entry.id, { value: e.target.value })}
                  placeholder={
                    isEditing && valueType === "password"
                      ? t("settings.agentCredentials.secretPlaceholder")
                      : t("settings.credentialForm.customEnv.valuePlaceholder")
                  }
                />
              </div>
              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={() => remove(entry.id)}
                title={t("settings.credentialForm.customEnv.remove")}
                className="mt-1 text-destructive hover:text-destructive"
              >
                <Trash2 className="w-4 h-4" />
              </Button>
            </div>
            {keyErr && (
              <p className="text-xs text-destructive">
                {t(`settings.credentialForm.customEnv.${keyErr}`)}
              </p>
            )}
          </div>
        );
      })}
      <Button
        type="button"
        variant="outline"
        size="sm"
        onClick={add}
        className="justify-self-start"
      >
        <Plus className="w-4 h-4 mr-1" />
        {t("settings.credentialForm.customEnv.addButton")}
      </Button>
    </div>
  );
}

export function hasInvalidCustomEnvKey(
  entries: CustomEnvEntry[],
  declaredKeys: Set<string>
): boolean {
  return entries.some((e) => validateKey(e.key, declaredKeys, entries, e.id) !== undefined);
}
