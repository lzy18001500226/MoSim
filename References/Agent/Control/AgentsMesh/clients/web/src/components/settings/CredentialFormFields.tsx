"use client";

import { useMemo } from "react";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import type {
  CredentialFormSpec,
  CredentialFieldSpec,
  CustomEnvEntry,
  OneOfCredentialField,
  SimpleCredentialField,
} from "./AgentCredentialsSettings/credentialForms/types";
import { getEnvKeysFromSpec } from "./AgentCredentialsSettings/credentialForms";
import { CustomEnvSection } from "./CustomEnvSection";

interface CredentialFormFieldsProps {
  spec: CredentialFormSpec;
  values: Record<string, string>;
  onValueChange: (envKey: string, value: string) => void;
  selectedOneOf: Record<string, string>;
  onOneOfChange: (group: string, envKey: string) => void;
  customEnv: CustomEnvEntry[];
  onCustomEnvChange: (entries: CustomEnvEntry[]) => void;
  isEditing: boolean;
  t: (key: string) => string;
}

function SimpleFieldInput({
  field,
  value,
  onChange,
  isEditing,
  t,
}: {
  field: SimpleCredentialField;
  value: string;
  onChange: (v: string) => void;
  isEditing: boolean;
  t: (key: string) => string;
}) {
  return (
    <div className="grid gap-2">
      <Label htmlFor={`cred-${field.envKey}`}>{t(field.label)}</Label>
      {field.description && (
        <p className="text-xs text-muted-foreground">{t(field.description)}</p>
      )}
      <Input
        id={`cred-${field.envKey}`}
        type={field.kind === "secret" ? "password" : "text"}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={
          isEditing && field.kind === "secret"
            ? t("settings.agentCredentials.secretPlaceholder")
            : field.placeholder ?? ""
        }
      />
      {isEditing && field.kind === "secret" && (
        <p className="text-xs text-muted-foreground">
          {t("settings.agentCredentials.secretEditHint")}
        </p>
      )}
    </div>
  );
}

function OneOfFieldInput({
  field,
  selectedEnvKey,
  onSelect,
  values,
  onValueChange,
  isEditing,
  t,
}: {
  field: OneOfCredentialField;
  selectedEnvKey: string;
  onSelect: (envKey: string) => void;
  values: Record<string, string>;
  onValueChange: (envKey: string, value: string) => void;
  isEditing: boolean;
  t: (key: string) => string;
}) {
  const selected = field.options.find((o) => o.envKey === selectedEnvKey) ?? field.options[0];
  return (
    <div className="grid gap-2">
      <Label>{t(field.label)}</Label>
      {field.description && (
        <p className="text-xs text-muted-foreground">{t(field.description)}</p>
      )}
      <div
        role="radiogroup"
        aria-label={t(field.label)}
        className="flex flex-wrap gap-2"
      >
        {field.options.map((opt) => {
          const isActive = opt.envKey === selected.envKey;
          return (
            <label
              key={opt.envKey}
              data-testid={`oneof-option-${field.group}-${opt.envKey}`}
              className={`flex items-center gap-2 px-3 py-1.5 rounded-md border cursor-pointer text-sm transition-colors ${
                isActive
                  ? "border-primary bg-primary/10 text-foreground"
                  : "border-border hover:bg-muted/50"
              }`}
            >
              <input
                type="radio"
                name={field.group}
                value={opt.envKey}
                checked={isActive}
                onChange={() => onSelect(opt.envKey)}
                className="accent-primary"
              />
              {t(opt.label)}
            </label>
          );
        })}
      </div>
      <Input
        id={`cred-${selected.envKey}`}
        type={selected.kind === "secret" ? "password" : "text"}
        value={values[selected.envKey] ?? ""}
        onChange={(e) => onValueChange(selected.envKey, e.target.value)}
        placeholder={
          isEditing && selected.kind === "secret"
            ? t("settings.agentCredentials.secretPlaceholder")
            : selected.placeholder ?? ""
        }
      />
      {isEditing && selected.kind === "secret" && (
        <p className="text-xs text-muted-foreground">
          {t("settings.agentCredentials.secretEditHint")}
        </p>
      )}
    </div>
  );
}

function renderField(
  field: CredentialFieldSpec,
  props: CredentialFormFieldsProps
): React.ReactNode {
  if (field.kind === "oneof") {
    return (
      <OneOfFieldInput
        key={field.group}
        field={field}
        selectedEnvKey={props.selectedOneOf[field.group] ?? field.options[0]?.envKey ?? ""}
        onSelect={(envKey) => props.onOneOfChange(field.group, envKey)}
        values={props.values}
        onValueChange={props.onValueChange}
        isEditing={props.isEditing}
        t={props.t}
      />
    );
  }
  return (
    <SimpleFieldInput
      key={field.envKey}
      field={field}
      value={props.values[field.envKey] ?? ""}
      onChange={(v) => props.onValueChange(field.envKey, v)}
      isEditing={props.isEditing}
      t={props.t}
    />
  );
}

export function CredentialFormFields(props: CredentialFormFieldsProps) {
  const { spec, customEnv, onCustomEnvChange, isEditing, t } = props;
  const declaredKeys = useMemo(() => getEnvKeysFromSpec(spec), [spec]);

  if (spec.fields.length === 0 && !spec.allowCustomEnv) return null;

  return (
    <>
      {spec.fields.map((field) => renderField(field, props))}
      {spec.allowCustomEnv && (
        <CustomEnvSection
          title={t("settings.credentialForm.customEnv.title")}
          hint={spec.customEnvHint ? t(spec.customEnvHint) : undefined}
          entries={customEnv}
          declaredKeys={declaredKeys}
          onChange={onCustomEnvChange}
          isEditing={isEditing}
          t={t}
        />
      )}
    </>
  );
}

export default CredentialFormFields;
