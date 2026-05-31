import { redirect } from "next/navigation";

// URL canonicalization: short-form /[org]/repositories deep-links resolve to
// the infra Repositories tab. Server-side redirect (HTTP 307) — no
// client-side flash, no useEffect race.
export default async function RepositoriesRedirect({
  params,
}: {
  params: Promise<{ org: string }>;
}) {
  const { org } = await params;
  redirect(`/${org}/infra?tab=repositories`);
}
