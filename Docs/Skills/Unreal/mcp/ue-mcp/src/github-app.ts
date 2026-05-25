import { createSign } from "node:crypto";
import { resolveUserAuth, clearUserAuth, type PendingDeviceFlow } from "./auth.js";
import { loadAppManifestSignature } from "./manifest-signature.js";

const APP_ID = "3133514";
const REPO_OWNER = "db-lyon";
const REPO_NAME = "ue-mcp";

function base64url(input: string): string {
  return Buffer.from(input).toString("base64url");
}

function createJWT(pem: string): string {
  const now = Math.floor(Date.now() / 1000);
  const header = base64url(JSON.stringify({ alg: "RS256", typ: "JWT" }));
  const payload = base64url(
    JSON.stringify({
      iss: APP_ID,
      iat: now - 60,
      exp: now + 600,
    }),
  );

  const unsigned = `${header}.${payload}`;
  const sign = createSign("RSA-SHA256");
  sign.update(unsigned);
  const signature = sign.sign(pem, "base64url");

  return `${unsigned}.${signature}`;
}

async function getInstallationToken(jwt: string): Promise<string> {
  const res = await fetch("https://api.github.com/app/installations", {
    headers: {
      Authorization: `Bearer ${jwt}`,
      Accept: "application/vnd.github+json",
    },
  });

  if (!res.ok) {
    throw new Error(`GitHub App auth failed: ${res.status}`);
  }

  const installations = (await res.json()) as Array<{ id: number }>;
  if (installations.length === 0) {
    throw new Error("GitHub App has no installations");
  }

  const tokenRes = await fetch(
    `https://api.github.com/app/installations/${installations[0].id}/access_tokens`,
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${jwt}`,
        Accept: "application/vnd.github+json",
      },
    },
  );

  if (!tokenRes.ok) {
    throw new Error(`Failed to get installation token: ${tokenRes.status}`);
  }

  return ((await tokenRes.json()) as { token: string }).token;
}

export type SubmitResult =
  | {
      kind: "submitted";
      url: string;
      number: number;
      authoredBy: string;
      authoredAs: "user" | "bot";
    }
  | {
      kind: "auth_required";
      verification_uri: string;
      user_code: string;
      expires_in: number;
    };

async function submitAsBot(
  title: string,
  body: string,
  labels: string[],
): Promise<SubmitResult> {
  // Anonymous bot path. The loader is lazy so the default useBot=false flow
  // never even reads the asset. Moving this to a server-side proxy is the
  // long-term plan — see https://github.com/db-lyon/ue-mcp/issues/461.
  const jwt = createJWT(loadAppManifestSignature());
  const token = await getInstallationToken(jwt);
  const res = await fetch(
    `https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}/issues`,
    {
      method: "POST",
      headers: {
        Authorization: `token ${token}`,
        Accept: "application/vnd.github+json",
        "Content-Type": "application/json",
        "User-Agent": "ue-mcp",
      },
      body: JSON.stringify({ title, body, labels }),
    },
  );
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Failed to create issue (bot): ${res.status} ${text}`);
  }
  const issue = (await res.json()) as { html_url: string; number: number };
  return {
    kind: "submitted",
    url: issue.html_url,
    number: issue.number,
    authoredBy: "ue-mcp-feedback[bot]",
    authoredAs: "bot",
  };
}

function pendingResult(pending: PendingDeviceFlow): SubmitResult {
  return {
    kind: "auth_required",
    verification_uri: pending.verification_uri,
    user_code: pending.user_code,
    expires_in: Math.max(0, pending.expires_at - Math.floor(Date.now() / 1000)),
  };
}

export async function submitFeedback(
  title: string,
  body: string,
  labels: string[] = ["agent-feedback"],
  options: { useBot?: boolean } = {},
): Promise<SubmitResult> {
  if (options.useBot) {
    return submitAsBot(title, body, labels);
  }

  const auth = await resolveUserAuth();
  if (auth.kind === "pending") {
    return pendingResult(auth.pending);
  }

  const res = await fetch(
    `https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}/issues`,
    {
      method: "POST",
      headers: {
        Authorization: `token ${auth.auth.token}`,
        Accept: "application/vnd.github+json",
        "Content-Type": "application/json",
        "User-Agent": "ue-mcp",
      },
      body: JSON.stringify({ title, body, labels }),
    },
  );

  if (res.status === 401) {
    // Token revoked or expired. Wipe and re-initiate device flow on the next
    // call so the user gets a fresh code instead of a silent bot fallback.
    await clearUserAuth();
    const retry = await resolveUserAuth();
    if (retry.kind === "pending") return pendingResult(retry.pending);
    // Fresh auth landed somehow - fall through to retry the post.
    const res2 = await fetch(
      `https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}/issues`,
      {
        method: "POST",
        headers: {
          Authorization: `token ${retry.auth.token}`,
          Accept: "application/vnd.github+json",
          "Content-Type": "application/json",
          "User-Agent": "ue-mcp",
        },
        body: JSON.stringify({ title, body, labels }),
      },
    );
    if (!res2.ok) {
      const text = await res2.text();
      throw new Error(`Failed to create issue as user (after re-auth): ${res2.status} ${text}`);
    }
    const issue2 = (await res2.json()) as { html_url: string; number: number };
    return {
      kind: "submitted",
      url: issue2.html_url,
      number: issue2.number,
      authoredBy: retry.auth.login,
      authoredAs: "user",
    };
  }

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Failed to create issue as user: ${res.status} ${text}`);
  }

  const issue = (await res.json()) as { html_url: string; number: number };
  return {
    kind: "submitted",
    url: issue.html_url,
    number: issue.number,
    authoredBy: auth.auth.login,
    authoredAs: "user",
  };
}
