import type { MetadataRoute } from "next";

export default function robots(): MetadataRoute.Robots {
  return {
    rules: [
      {
        userAgent: "*",
        allow: "/",
        disallow: [
          "/api/",
          "/auth/",
          "/settings/",
          "/onboarding/",
          "/verify-email/",
          "/reset-password/",
          "/forgot-password/",
          "/runners/authorize",
          "/mock-checkout",
          "/offline",
        ],
      },
    ],
    sitemap: "https://agentsmesh.ai/sitemap.xml",
  };
}
