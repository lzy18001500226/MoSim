import type { Metadata } from "next";
import DashboardShell from "./DashboardShell";
import { AuthBootstrap } from "@/components/auth/AuthBootstrap";
import { RequireAuth } from "@/components/auth/RequireAuth";
import { PostHogIdentify } from "@/providers/PostHogProvider";

export const metadata: Metadata = {
  robots: { index: false, follow: false },
};

// Dashboard route group — wasm-bound, auth-required. AuthBootstrap loads
// wasm and runs the auth bootstrap protocol; RequireAuth handles the
// `_hasHydrated && !user → /login` gate uniformly. PostHogIdentify needs
// auth hooks so it sits inside AuthBootstrap.
export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <AuthBootstrap>
      <PostHogIdentify />
      <RequireAuth>
        <DashboardShell>{children}</DashboardShell>
      </RequireAuth>
    </AuthBootstrap>
  );
}
