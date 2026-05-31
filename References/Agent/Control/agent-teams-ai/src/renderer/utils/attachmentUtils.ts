import {
  DEFAULT_AGENT_IMAGE_OPTIMIZATION_BUDGET,
  optimizeImageForAgent,
} from '@features/agent-attachments/renderer';
import { categorizeFile, getEffectiveMimeType, isImageMime } from '@shared/constants/attachments';

import type { AttachmentPayload, ImageMimeType } from '@shared/types';

export const ALLOWED_MIME_TYPES = new Set<ImageMimeType>([
  'image/png',
  'image/jpeg',
  'image/gif',
  'image/webp',
]);

export const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
export const MAX_FILES = 5;
export const MAX_TOTAL_SIZE = 20 * 1024 * 1024; // 20MB

export function isImageMimeType(type: string): type is ImageMimeType {
  return ALLOWED_MIME_TYPES.has(type as ImageMimeType);
}

export function validateAttachment(file: File): { valid: true } | { valid: false; error: string } {
  const cat = categorizeFile(file);
  if (cat === 'unsupported') {
    return { valid: false, error: `Unsupported file type: ${file.name}` };
  }
  if (file.size === 0) {
    return { valid: false, error: `File "${file.name}" is empty` };
  }
  if (file.size > MAX_FILE_SIZE) {
    return { valid: false, error: `File "${file.name}" exceeds 10MB limit` };
  }
  return { valid: true };
}

export async function fileToAttachmentPayload(file: File): Promise<AttachmentPayload> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      const dataUrl = reader.result as string;
      // Strip "data:<mime>;base64," prefix to get raw base64
      const base64 = dataUrl.split(',')[1] ?? '';
      resolve({
        id: crypto.randomUUID(),
        filename: file.name,
        mimeType: getEffectiveMimeType(file),
        size: file.size,
        data: base64,
      });
    };
    reader.onerror = () => reject(new Error(`Failed to read file: ${file.name}`));
    reader.readAsDataURL(file);
  });
}

function imageOutputFilename(filename: string, mimeType: 'image/png' | 'image/jpeg'): string {
  const trimmed = filename.trim() || 'image';
  const withoutExtension = trimmed.replace(/\.[^.\\/]+$/, '') || 'image';
  return `${withoutExtension}.${mimeType === 'image/png' ? 'png' : 'jpg'}`;
}

function blobToBase64(blob: Blob): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      const dataUrl = typeof reader.result === 'string' ? reader.result : '';
      resolve(dataUrl.split(',')[1] ?? '');
    };
    reader.onerror = () => reject(new Error('Failed to read optimized image'));
    reader.readAsDataURL(blob);
  });
}

export async function fileToAgentAttachmentPayload(file: File): Promise<AttachmentPayload> {
  const category = categorizeFile(file);
  if (category !== 'image' || file.type === 'image/gif') {
    return fileToAttachmentPayload(file);
  }

  const optimized = await optimizeImageForAgent({ file });
  return {
    id: crypto.randomUUID(),
    filename: imageOutputFilename(file.name, optimized.optimized.mimeType),
    mimeType: optimized.optimized.mimeType,
    size: optimized.optimized.sizeBytes,
    data: await blobToBase64(optimized.optimized.blob),
  };
}

export function validateOptimizedImageTotal(
  attachments: AttachmentPayload[]
): { valid: true } | { valid: false; error: string } {
  const optimizedImageBytes = attachments
    .filter((attachment) => attachment.mimeType.startsWith('image/'))
    .reduce((sum, attachment) => sum + attachment.size, 0);
  if (optimizedImageBytes <= DEFAULT_AGENT_IMAGE_OPTIMIZATION_BUDGET.maxOutputBytesTotal) {
    return { valid: true };
  }
  return {
    valid: false,
    error: 'Optimized image attachments exceed the safe runtime size limit',
  };
}

export { categorizeFile, isImageMime };

export function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}
