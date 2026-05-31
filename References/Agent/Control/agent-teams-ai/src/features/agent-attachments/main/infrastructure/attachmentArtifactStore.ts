import { assertSafeAttachmentStorageId } from '@features/agent-attachments/core/domain';
import { getAppDataPath } from '@main/utils/pathDecoder';
import * as fs from 'fs/promises';
import * as path from 'path';

export type AgentAttachmentArtifactFileName =
  | 'original.png'
  | 'original.jpg'
  | 'original.webp'
  | 'optimized.png'
  | 'optimized.jpg'
  | 'optimized.webp'
  | 'thumb.jpg'
  | 'meta.json';

export interface ResolveAgentAttachmentArtifactPathInput {
  teamName: string;
  messageId: string;
  attachmentId: string;
  fileName: AgentAttachmentArtifactFileName;
  appDataPath?: string;
}

export function resolveAgentAttachmentArtifactPath(
  input: ResolveAgentAttachmentArtifactPathInput
): string {
  assertSafeAttachmentStorageId('teamName', input.teamName);
  assertSafeAttachmentStorageId('messageId', input.messageId);
  assertSafeAttachmentStorageId('attachmentId', input.attachmentId);

  const root = input.appDataPath ?? getAppDataPath();
  const base = path.resolve(
    root,
    'attachments',
    input.teamName,
    input.messageId,
    input.attachmentId
  );
  const resolved = path.resolve(base, input.fileName);
  if (!resolved.startsWith(base + path.sep)) {
    throw new Error('Attachment artifact path escaped managed directory');
  }
  return resolved;
}

export async function writeFileAtomic(filePath: string, bytes: Buffer | string): Promise<void> {
  const dir = path.dirname(filePath);
  await fs.mkdir(dir, { recursive: true });
  const tmpPath = path.join(dir, `.${path.basename(filePath)}.${process.pid}.${Date.now()}.tmp`);
  try {
    await fs.writeFile(tmpPath, bytes);
    await fs.rename(tmpPath, filePath);
  } catch (error) {
    await fs.rm(tmpPath, { force: true }).catch(() => undefined);
    throw error;
  }
}
