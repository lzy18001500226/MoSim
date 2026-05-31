"use client";

import { useTranslations } from "next-intl";
import { toast } from "sonner";
import type { SupportTicketMessage } from "@/lib/api/facade/supportTicketConnect";
import { getSupportTicketAttachmentUrl } from "@/lib/api/facade/supportTicketConnect";
import { Download, Shield, UserCircle } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { formatTimeAgo } from "@/lib/utils/time";

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export function MessageList({ messages }: { messages: SupportTicketMessage[] }) {
  const t = useTranslations();

  if (messages.length === 0) {
    return (
      <div className="py-12 text-center text-muted-foreground">
        {t("support.detail.noComments")}
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {messages.map((msg) => (
        <MessageBubble key={Number(msg.id)} message={msg} />
      ))}
    </div>
  );
}

function MessageBubble({ message }: { message: SupportTicketMessage }) {
  const t = useTranslations();
  const isAdmin = message.isAdminReply;

  const handleDownload = async (attachmentId: number) => {
    try {
      const { url } = await getSupportTicketAttachmentUrl(attachmentId);
      window.open(url, "_blank");
    } catch {
      toast.error(t("support.downloadFailed"));
    }
  };

  return (
    <div className={`flex gap-3 ${isAdmin ? "flex-row-reverse" : ""}`}>
      {/* Avatar */}
      <div className="flex-shrink-0 mt-1">
        {isAdmin ? (
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/20">
            <Shield className="h-4 w-4 text-primary" />
          </div>
        ) : (
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-muted">
            <UserCircle className="h-4 w-4 text-muted-foreground" />
          </div>
        )}
      </div>

      {/* Content */}
      <div className={`flex-1 max-w-[80%] ${isAdmin ? "items-end" : ""}`}>
        <div className={`flex items-center gap-2 mb-1 ${isAdmin ? "justify-end" : ""}`}>
          <span className="text-xs font-medium">
            {message.user?.name || message.user?.email || (isAdmin ? "Admin" : "")}
          </span>
          {isAdmin && (
            <Badge variant="outline" className="text-[10px] px-1 py-0">
              Admin
            </Badge>
          )}
          <span className="text-xs text-muted-foreground">
            {formatTimeAgo(message.createdAt, t)}
          </span>
        </div>

        <div
          className={`rounded-lg px-3 py-2 text-sm ${
            isAdmin
              ? "bg-primary/10 ml-auto"
              : "bg-muted"
          }`}
        >
          <p className="whitespace-pre-wrap">{message.content}</p>
        </div>

        {/* Attachments */}
        {message.attachments && message.attachments.length > 0 && (
          <div className={`mt-2 flex flex-wrap gap-2 ${isAdmin ? "justify-end" : ""}`}>
            {message.attachments.map((att) => {
              const id = Number(att.id);
              return (
              <button
                key={id}
                onClick={() => handleDownload(id)}
                aria-label={`${t("support.download")} ${att.originalName}`}
                className="flex items-center gap-1 rounded border border-border px-2 py-1 text-xs hover:bg-muted transition-colors"
              >
                <Download className="h-3 w-3" />
                <span className="max-w-[120px] truncate">{att.originalName}</span>
                <span className="text-muted-foreground">
                  ({formatFileSize(Number(att.size))})
                </span>
              </button>
            );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
