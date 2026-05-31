"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useLightSession } from "@/hooks/useLightSession";
import { getDefaultRoute } from "@/lib/default-route";
import { fetchFirstOrgSlug } from "@/lib/light-auth";

// When the caller passes `skipIfRedirectParam=true` along with the encoded
// `?redirect=` value, this hook stays out of the navigation race. The form
// handler will push `redirectParam` itself after login; pre-empting here
// causes a last-write-wins race against router.push (issue #346 popout).
export function useRedirectIfAuthenticated(opts?: {
  skipIfRedirectParam?: string | null;
}): { hydrated: boolean; redirecting: boolean } {
  const router = useRouter();
  const { session, hydrated } = useLightSession();
  const skip = !!opts?.skipIfRedirectParam;
  const shouldRedirect = hydrated && !!session?.isAuthenticated && !skip;

  useEffect(() => {
    if (!shouldRedirect) return;
    let cancelled = false;
    (async () => {
      const slug = session?.currentOrgSlug || (await fetchFirstOrgSlug());
      if (cancelled) return;
      router.replace(slug ? getDefaultRoute(slug) : "/onboarding");
    })();
    return () => { cancelled = true; };
  }, [shouldRedirect, session?.currentOrgSlug, router]);

  return { hydrated, redirecting: shouldRedirect };
}
