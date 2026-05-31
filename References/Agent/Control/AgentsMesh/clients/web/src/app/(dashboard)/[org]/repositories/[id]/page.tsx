import { redirect } from "next/navigation";

// URL canonicalization: deep-links to /repositories/[id] redirect to the
// equivalent infra tab + id query. Server-side redirect (HTTP 307) — no
// client-side flash, no useEffect race.
export default async function RepositoryDetailRedirect({
  params,
}: {
  params: Promise<{ org: string; id: string }>;
}) {
  const { org, id } = await params;
  redirect(`/${org}/infra?tab=repositories&id=${id}`);
}
