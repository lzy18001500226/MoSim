"use client";

import { useState, useCallback, useEffect } from "react";
import {
  Dialog,
  DialogContent,
  DialogBody,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { FormField } from "@/components/ui/form-field";
import { Loader2, Globe, Lock } from "lucide-react";
import { useChannelStore } from "@/stores/channel";
import { useTranslations } from "next-intl";
import { MemberSelector } from "./MemberSelector";

interface CreateChannelDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onCreated: (channelId: number) => void;
}

export function CreateChannelDialog({
  open,
  onOpenChange,
  onCreated,
}: CreateChannelDialogProps) {
  const t = useTranslations();
  const createChannel = useChannelStore((s) => s.createChannel);

  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [visibility, setVisibility] = useState<"public" | "private">("public");
  const [selectedMembers, setSelectedMembers] = useState<number[]>([]);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (open) {
      setName("");
      setDescription("");
      setVisibility("public");
      setSelectedMembers([]);
      setError(null);
      setSaving(false);
    }
  }, [open]);

  const handleSubmit = useCallback(async () => {
    const trimmedName = name.trim();
    if (!trimmedName) {
      setError(t("channels.createDialog.nameRequired"));
      return;
    }
    setSaving(true);
    setError(null);
    try {
      const channel = await createChannel({
        name: trimmedName,
        description: description.trim() || undefined,
        visibility,
        memberIds: visibility === "private" ? selectedMembers : undefined,
      });
      onCreated(channel.id);
    } catch (err) {
      setError((err as Error).message || t("channels.createDialog.failed"));
    } finally {
      setSaving(false);
    }
  }, [name, description, visibility, selectedMembers, createChannel, onCreated, t]);

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent title={t("channels.createDialog.title")}>
        <DialogBody className="space-y-4">
          {error && (
            <div className="p-3 bg-destructive/10 text-destructive text-sm rounded-lg">
              {error}
            </div>
          )}

          <FormField label={t("channels.createDialog.name")} htmlFor="channel-name">
            <Input
              id="channel-name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder={t("channels.createDialog.namePlaceholder")}
              onKeyDown={(e) => {
                if (e.nativeEvent.isComposing) return;
                if (e.key === "Enter" && !saving) handleSubmit();
              }}
              autoFocus
            />
          </FormField>

          <FormField
            label={t("channels.createDialog.description")}
            htmlFor="channel-description"
            hint={t("channels.createDialog.descriptionHint")}
          >
            <Input
              id="channel-description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder={t("channels.createDialog.descriptionPlaceholder")}
            />
          </FormField>

          <FormField label={t("channels.createDialog.visibility")} htmlFor="channel-visibility">
            <div className="flex gap-2">
              <Button
                type="button"
                variant={visibility === "public" ? "default" : "outline"}
                size="sm"
                onClick={() => setVisibility("public")}
                className="flex-1"
              >
                <Globe className="w-4 h-4 mr-1.5" />
                {t("channels.visibility.public")}
              </Button>
              <Button
                type="button"
                variant={visibility === "private" ? "default" : "outline"}
                size="sm"
                onClick={() => setVisibility("private")}
                className="flex-1"
              >
                <Lock className="w-4 h-4 mr-1.5" />
                {t("channels.visibility.private")}
              </Button>
            </div>
          </FormField>

          {visibility === "private" && (
            <FormField label={t("channels.members.available")} htmlFor="member-search">
              <MemberSelector selectedIds={selectedMembers} onChange={setSelectedMembers} />
            </FormField>
          )}
        </DialogBody>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            {t("common.cancel")}
          </Button>
          <Button onClick={handleSubmit} disabled={saving || !name.trim()}>
            {saving && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
            {t("channels.sidebar.createChannel")}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
