// Upload-install skill flow — 3 steps replacing the legacy multipart REST.
// 1) PresignSkillUpload (Connect) — mint storage_key + presigned PUT URL.
// 2) PUT to S3 directly (browser → S3, never through backend).
// 3) InstallSkillFromUploadedFile (Connect) — server downloads from the key,
//    runs the same packaging pipeline the multipart handler used.
//
// Same pattern as support_ticket attachments.
import {
  InstallSkillFromUploadedFileRequestSchema,
  InstalledSkillSchema,
  PresignSkillUploadRequestSchema,
  PresignSkillUploadResponseSchema,
} from "@proto/extension/v1/repo_skill_pb";
import { create, toBinary, fromBinary } from "@bufbuild/protobuf";
import { getExtensionService } from "@/lib/wasm-core";
import type { InstalledSkill } from "@/lib/viewModels/extension";

export type {
  SkillRegistryAuthType, SkillRegistry, SkillRegistryOverride,
  SkillMarketItem, McpMarketItem, McpHeaderSchemaEntry, EnvVarSchemaEntry,
  InstalledSkill, InstalledMcpServer,
} from "@/lib/viewModels/extension";

export const extensionApi = {
  installSkillFromUpload: async (
    orgSlug: string,
    repoId: number,
    file: File,
    scope: string,
  ): Promise<InstalledSkill> => {
    const presignReq = create(PresignSkillUploadRequestSchema, {
      orgSlug,
      repositoryId: BigInt(repoId),
      filename: file.name,
      contentType: file.type || "application/octet-stream",
      size: BigInt(file.size),
    });
    const presignBytes = await getExtensionService().presignSkillUploadConnect(
      toBinary(PresignSkillUploadRequestSchema, presignReq),
    );
    const presignResp = fromBinary(PresignSkillUploadResponseSchema, new Uint8Array(presignBytes));

    const putRes = await fetch(presignResp.putUrl, {
      method: "PUT",
      headers: { "Content-Type": file.type || "application/octet-stream" },
      body: file,
    });
    if (!putRes.ok) {
      throw new Error(`upload PUT failed: ${putRes.status}`);
    }

    const installReq = create(InstallSkillFromUploadedFileRequestSchema, {
      orgSlug,
      repositoryId: BigInt(repoId),
      storageKey: presignResp.storageKey,
      filename: presignResp.filename,
      scope,
    });
    const installBytes = await getExtensionService().installSkillFromUploadedFileConnect(
      toBinary(InstallSkillFromUploadedFileRequestSchema, installReq),
    );
    const installed = fromBinary(InstalledSkillSchema, new Uint8Array(installBytes));
    return {
      id: Number(installed.id),
      organization_id: Number(installed.organizationId),
      repository_id: Number(installed.repositoryId),
      market_item_id: installed.marketItemId === undefined ? null : Number(installed.marketItemId),
      scope: installed.scope as "org" | "user",
      installed_by: installed.installedBy === undefined ? 0 : Number(installed.installedBy),
      slug: installed.slug,
      install_source: installed.installSource as "market" | "github" | "upload",
      source_url: installed.sourceUrl,
      content_sha: installed.contentSha,
      package_size: Number(installed.packageSize),
      pinned_version: installed.pinnedVersion === undefined ? null : installed.pinnedVersion,
      is_enabled: installed.isEnabled,
    };
  },
};
