// Light-mode replacement for lib/auth/post-login.ts. Decides where the
// browser should land after login / OAuth / accept-invite / etc, WITHOUT
// touching wasm. The dashboard's wasm bootstrap re-fetches organizations
// when it loads, so we just need to pick a sensible destination.
// Order of preference:
//   1. ?redirect=<safe path> (deep-link restoration; matches login/page.tsx)
//   2. First org's default route (fetched via Connect with the Bearer
//      token we just persisted)
//   3. /onboarding (no orgs yet)

import { lightConnect } from "./api-fetch";
import { getDefaultRoute } from "@/lib/default-route";
import { safeRedirectPath } from "@/lib/auth/redirect";

interface ListMyOrgsResponse {
  items?: Array<{ slug: string }>;
}

export async function fetchFirstOrgSlug(): Promise<string | null> {
  try {
    const resp = await lightConnect<Record<string, never>, ListMyOrgsResponse>(
      "proto.org.v1.OrgService",
      "ListMyOrgs",
      {},
      { authenticated: true },
    );
    const orgs = resp?.items ?? [];
    return orgs.length > 0 ? orgs[0].slug : null;
  } catch {
    return null;
  }
}

export async function resolvePostLoginUrlLight(opts: {
  redirectParam?: string | null;
}): Promise<string> {
  const redirect = safeRedirectPath(opts.redirectParam ?? null);
  if (redirect) return redirect;
  const slug = await fetchFirstOrgSlug();
  if (slug) return getDefaultRoute(slug);
  return "/onboarding";
}
