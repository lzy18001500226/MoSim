import {
  AgentAttachmentError,
  resolveAgentAttachmentCapability,
} from '@features/agent-attachments/core/domain';

import type { AttachmentPayload } from '@shared/types';

export type OpenCodeFilePartMimeType = 'image/png' | 'image/jpeg' | 'image/webp';

export interface OpenCodeFilePart {
  type: 'file';
  mime: OpenCodeFilePartMimeType;
  url: string;
  filename: string;
}

export interface OpenCodeAttachmentDeliveryParts {
  kind: 'legacy_text' | 'text_with_file_parts';
  text: string;
  fileParts: OpenCodeFilePart[];
  diagnostics: string[];
}

export interface BuildOpenCodeAttachmentDeliveryPartsInput {
  text: string;
  model: string;
  attachments?: AttachmentPayload[];
}

function assertOpenCodeImageMimeType(
  mimeType: string
): asserts mimeType is OpenCodeFilePartMimeType {
  if (mimeType === 'image/png' || mimeType === 'image/jpeg' || mimeType === 'image/webp') {
    return;
  }

  throw new AgentAttachmentError(
    'attachment_type_unsupported',
    `OpenCode currently supports image attachments only; unsupported MIME: ${mimeType}`,
    { providerId: 'opencode', retryable: false }
  );
}

function assertOpenCodeVisionCapability(model: string): void {
  const capability = resolveAgentAttachmentCapability({
    providerId: 'opencode',
    model,
  });
  if (capability.supportsImages) {
    return;
  }

  const code =
    capability.reason === 'known_non_vision_model' || capability.reason === 'unknown_model'
      ? 'attachment_model_unsupported'
      : 'attachment_type_unsupported';
  throw new AgentAttachmentError(code, capability.displayText, {
    providerId: 'opencode',
    model,
    retryable: false,
    safeDetails: {
      reason: capability.reason,
    },
  });
}

function formatBytes(bytes: number): string {
  if (!Number.isFinite(bytes) || bytes <= 0) return '0 B';
  if (bytes < 1024) return `${bytes} B`;
  const kib = bytes / 1024;
  if (kib < 1024) return `${kib.toFixed(1)} KB`;
  return `${(kib / 1024).toFixed(1)} MB`;
}

export function buildOpenCodeAttachmentDeliveryParts(
  input: BuildOpenCodeAttachmentDeliveryPartsInput
): OpenCodeAttachmentDeliveryParts {
  const attachments = input.attachments ?? [];
  if (attachments.length === 0) {
    return {
      kind: 'legacy_text',
      text: input.text,
      fileParts: [],
      diagnostics: [],
    };
  }

  assertOpenCodeVisionCapability(input.model);

  const fileParts: OpenCodeFilePart[] = [];
  const diagnostics: string[] = [];
  for (const attachment of attachments) {
    assertOpenCodeImageMimeType(attachment.mimeType);
    fileParts.push({
      type: 'file',
      mime: attachment.mimeType,
      url: `data:${attachment.mimeType};base64,${attachment.data}`,
      filename: attachment.filename,
    });
    diagnostics.push(
      `prepared OpenCode image file part ${attachment.filename} (${attachment.mimeType}, ${formatBytes(
        attachment.size
      )}) for ${input.model}`
    );
  }

  return {
    kind: 'text_with_file_parts',
    text: input.text,
    fileParts,
    diagnostics,
  };
}

export function redactOpenCodeFilePartsForDiagnostics(
  parts: OpenCodeFilePart[]
): OpenCodeFilePart[] {
  return parts.map((part) => ({
    ...part,
    url: `[redacted data URL: ${part.mime}]`,
  }));
}
