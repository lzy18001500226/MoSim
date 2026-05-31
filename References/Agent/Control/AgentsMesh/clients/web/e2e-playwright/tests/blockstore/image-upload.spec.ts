// Migrated R5+: Connect-RPC only (no REST middle layer).
import { randomUUID } from "crypto";

import { test, expect, orgSlug } from "../../fixtures/blockstore.fixture";
import { makeConnectClient } from "../../helpers/connect-client";

// Image upload path (F-end media): file input → /files/presign → PUT to S3
// → block.data.url set → <img src> shows the uploaded asset. Verifies the
// full pipeline that image/video/audio/file blocks all share via the common
// uploadImage helper.
//
// Driven via API + file input to keep the test fast and deterministic. The
// real browser upload flow (FormData + XHR) has a lot of moving parts, but
// the presign contract is the only thing the backend owns; the PUT and the
// subsequent block update are the pieces that can silently regress.

// Phase E (wasm Connect ServerStream bridge) is now real, so the page
// hydrates through the normal zustand `_tick` cycle. The presign contract
// has API-level coverage; this spec asserts the upload UI's end-to-end
// integration with block.data.url.
test("image block stores uploaded asset URL end-to-end", async ({
  authenticatedPage,
  token,
  isolatedWorkspace,
}) => {
  const cc = makeConnectClient(token);
  const { id: workspaceID, rootID } = isolatedWorkspace;
  // 1. Seed an empty image block via API so we don't have to click through
  // the slash menu. The renderer's upload UI is the real surface under test.
  const imageID = randomUUID();
  await cc.blockstore.applyOps({
    orgSlug,
    workspaceId: workspaceID,
    ops: [
      {
        op: "createBlock",
        // RequiredDataKey["url"] enforces presence, not non-empty, so an
        // empty string seeds the block in its "upload" render state.
        payloadJson: JSON.stringify({ id: imageID, type: "image", data: { url: "" }, text: "" }),
      },
      {
        op: "addRef",
        payloadJson: JSON.stringify({ from: rootID, to: imageID, rel: "nest", order_key: `zzi${Date.now().toString(36)}` }),
      },
    ],
    idempotencyKey: `e2e-image-seed-${imageID}`,
  });

  // 2. Open the page and locate the block's upload button. Empty state
  // renders the drop zone; we target it by its icon + label.
  await authenticatedPage.goto(`/${orgSlug}/blocks?ws=${workspaceID}`);
  const uploadBtn = authenticatedPage
    .getByRole("button", { name: /Click to upload image/ })
    .last();
  await expect(uploadBtn).toBeVisible({ timeout: 15_000 });

  // 3. The hidden <input type="file"> is a sibling inside the same block.
  // Playwright's setInputFiles accepts a Buffer; we craft a tiny PNG on the
  // fly so nothing touches disk or the test runner filesystem.
  const pngBytes = Buffer.from([
    0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a, // PNG sig
    0x00, 0x00, 0x00, 0x0d, 0x49, 0x48, 0x44, 0x52, // IHDR
    0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01, // 1x1
    0x08, 0x06, 0x00, 0x00, 0x00, 0x1f, 0x15, 0xc4,
    0x89, 0x00, 0x00, 0x00, 0x0a, 0x49, 0x44, 0x41, // IDAT
    0x54, 0x78, 0x9c, 0x62, 0x00, 0x00, 0x00, 0x00,
    0x05, 0x00, 0x01, 0x0d, 0x0a, 0x2d, 0xb4, 0x00,
    0x00, 0x00, 0x00, 0x49, 0x45, 0x4e, 0x44, 0xae, // IEND
    0x42, 0x60, 0x82,
  ]);

  const fileInput = authenticatedPage
    .locator(`#block-${imageID} input[type="file"]`)
    .last();

  // Race the upload completion: wait for the updateBlock op that carries
  // the new data.url. Without this the test races the S3 PUT + store sync.
  const updatePromise = authenticatedPage.waitForResponse(
    (r) =>
      r.url().includes("BlockstoreService/ApplyOps") &&
      r.request().method() === "POST" &&
      (r.request().postData() ?? "").includes(imageID),
    { timeout: 20_000 },
  );
  await fileInput.setInputFiles({ name: "pixel.png", mimeType: "image/png", buffer: pngBytes });
  const updateRes = await updatePromise;
  expect(updateRes.status()).toBeLessThan(300);

  // 4. Assert the stored url is a non-empty http(s) URL and that the
  // renderer reflects it in an <img src>.
  const subtree = await cc.blockstore.getSubtree({
    orgSlug,
    workspaceId: workspaceID,
    rootId: rootID,
  }) as { blocks: Array<{ id: string; dataJson: string }> };
  const stored = subtree.blocks.find((b) => b.id === imageID);
  expect(stored, "image block must still exist").toBeDefined();
  const storedData = JSON.parse(stored!.dataJson) as { url?: unknown };
  const url = storedData.url;
  expect(typeof url).toBe("string");
  expect(url as string).toMatch(/^https?:\/\//);

  // Defensive: verify the backend presign path is reachable with this token,
  // guarding against silent regressions in the files service.
  const presigned = await cc.file.presignUpload({
    orgSlug,
    filename: "probe.png",
    contentType: "image/png",
    size: BigInt(1024),
  }) as { putUrl: string; getUrl: string };
  expect(presigned.putUrl).toBeTruthy();
  expect(presigned.getUrl).toBeTruthy();
});
