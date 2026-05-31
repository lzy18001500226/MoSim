import { redirect } from "next/navigation";

// URL canonicalization: short-form /[org]/runners deep-links resolve to the
// infra Runners tab. Server-side redirect (HTTP 307) — no client-side flash,
// no useEffect race.
export default async function RunnersRedirect({
  params,
}: {
  params: Promise<{ org: string }>;
}) {
  const { org } = await params;
  redirect(`/${org}/infra?tab=runners`);
}
