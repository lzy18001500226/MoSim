import { AuthBootstrap } from "@/components/auth/AuthBootstrap";
import { RequireAuth } from "@/components/auth/RequireAuth";

// Popout terminal — a separate browser window opened via window.open.
// New windows get a fresh Rust core, so AuthBootstrap is required to
// rehydrate the session from localStorage; without it the popout would
// always see an anonymous user and bounce to /login (issue #346).
// RequireAuth then guards the page with a redirect-preserving login bounce.
export default function PopoutLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <AuthBootstrap>
      <RequireAuth>{children}</RequireAuth>
    </AuthBootstrap>
  );
}
