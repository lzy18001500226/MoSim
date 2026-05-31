import { DEFAULT_AGENT_IMAGE_OPTIMIZATION_BUDGET } from './budgets';

import type {
  AgentAttachmentCapability,
  AgentAttachmentKind,
  AgentAttachmentPayload,
  AgentImageMimeType,
  AttachmentValidationResult,
  ImageOptimizationBudget,
} from './types';

const AGENT_IMAGE_MIME_TYPES = new Set<AgentImageMimeType>([
  'image/png',
  'image/jpeg',
  'image/gif',
  'image/webp',
]);

const OPTIMIZABLE_AGENT_IMAGE_MIME_TYPES = new Set<Exclude<AgentImageMimeType, 'image/gif'>>([
  'image/png',
  'image/jpeg',
  'image/webp',
]);

const PROVIDER_IMAGE_MIME_TYPES = new Set<AgentImageMimeType>([
  'image/png',
  'image/jpeg',
  'image/gif',
  'image/webp',
]);

export function isAgentImageMimeType(mimeType: string): mimeType is AgentImageMimeType {
  return AGENT_IMAGE_MIME_TYPES.has(mimeType as AgentImageMimeType);
}

export function isProviderImageMimeType(mimeType: string): mimeType is AgentImageMimeType {
  return PROVIDER_IMAGE_MIME_TYPES.has(mimeType as AgentImageMimeType);
}

function isOptimizableAgentImageMimeType(
  mimeType: string
): mimeType is Exclude<AgentImageMimeType, 'image/gif'> {
  return OPTIMIZABLE_AGENT_IMAGE_MIME_TYPES.has(
    mimeType as Exclude<AgentImageMimeType, 'image/gif'>
  );
}

function isProviderFileMimeType(mimeType: string, supported: readonly string[]): boolean {
  return supported.some((candidate) =>
    candidate.endsWith('/*') ? mimeType.startsWith(candidate.slice(0, -1)) : candidate === mimeType
  );
}

function isCapabilityImageMimeType(
  mimeType: string,
  supported: readonly AgentImageMimeType[]
): boolean {
  return supported.includes(mimeType as AgentImageMimeType);
}

export function classifyAttachmentMime(mimeType: string): AgentAttachmentKind {
  if (isAgentImageMimeType(mimeType)) return 'image';
  if (mimeType === 'application/pdf' || mimeType === 'text/plain' || mimeType.startsWith('text/')) {
    return 'file';
  }
  return 'unsupported';
}

export function validateImageOptimizationInput(input: {
  mimeType: string;
  sizeBytes: number;
  width: number;
  height: number;
  budget?: ImageOptimizationBudget;
}): AttachmentValidationResult {
  const budget = input.budget ?? DEFAULT_AGENT_IMAGE_OPTIMIZATION_BUDGET;
  if (!isOptimizableAgentImageMimeType(input.mimeType)) {
    return {
      ok: false,
      code: 'attachment_type_unsupported',
      message: 'This image type is not supported for optimization.',
      warnings: [],
    };
  }
  if (input.sizeBytes <= 0) {
    return {
      ok: false,
      code: 'attachment_type_unsupported',
      message: 'Image file is empty.',
      warnings: [],
    };
  }
  if (input.sizeBytes > budget.maxInputBytes) {
    return {
      ok: false,
      code: 'attachment_too_large',
      message: 'Image is too large to prepare for sending.',
      warnings: [],
    };
  }
  if (input.width * input.height > budget.maxInputPixels) {
    return {
      ok: false,
      code: 'attachment_too_large',
      message: 'Image dimensions are too large to prepare for sending.',
      warnings: [],
    };
  }
  return { ok: true, warnings: [] };
}

export function validateAttachmentForCapability(input: {
  attachment: AgentAttachmentPayload;
  capability: AgentAttachmentCapability;
}): AttachmentValidationResult {
  const { attachment, capability } = input;
  const warnings = [...attachment.warnings];

  if (attachment.kind !== 'image') {
    if (attachment.kind !== 'file') {
      return {
        ok: false,
        code: 'attachment_type_unsupported',
        message: 'This attachment type is not supported by the selected provider.',
        warnings,
      };
    }

    if (!capability.supportsFiles) {
      return {
        ok: false,
        code: 'attachment_type_unsupported',
        message: capability.filesDisplayText,
        warnings,
      };
    }

    if (!isProviderFileMimeType(attachment.mimeType, capability.supportedFileMimeTypes)) {
      return {
        ok: false,
        code: 'attachment_type_unsupported',
        message: 'This file type is not supported by the selected provider.',
        warnings,
      };
    }

    if (attachment.sizeBytes > capability.maxBytesPerFile) {
      return {
        ok: false,
        code: 'attachment_too_large',
        message: 'File is too large for the selected provider path.',
        warnings,
      };
    }

    return { ok: true, warnings };
  }

  if (!capability.supportsImages) {
    return {
      ok: false,
      code: 'attachment_model_unsupported',
      message: capability.displayText,
      warnings,
    };
  }

  if (!isCapabilityImageMimeType(attachment.mimeType, capability.supportedImageMimeTypes)) {
    return {
      ok: false,
      code: 'attachment_type_unsupported',
      message: 'This image type is not supported by the selected provider.',
      warnings,
    };
  }

  if (attachment.sizeBytes > capability.maxBytesPerImage) {
    return {
      ok: false,
      code: 'attachment_too_large',
      message: 'Image is too large after optimization. Remove it or use a smaller image.',
      warnings,
    };
  }

  return { ok: true, warnings };
}
