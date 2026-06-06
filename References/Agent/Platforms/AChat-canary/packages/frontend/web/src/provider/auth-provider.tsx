import { authClient } from "@/lib/auth-client";
import { useLocation } from "wouter";
import { type ReactNode, useEffect } from "react";

export function AuthGuard({
  role = "user",
  children,
}: {
  role?: "user" | "admin";
  children: ReactNode;
}) {
  const [, navigate] = useLocation();
  const { data, isPending } = authClient.useSession();

  // useEffect(() => {
  //   if (isPending) return;

  //   if (!data) {
  //     return navigate("/auth");
  //   }

  //   if (role === "admin") {
  //     if (data.user.role !== "admin") {
  //       return navigate("/app");
  //     }
  //   }
  //   //  else {
  //   //   if (data.user.emailVerified === false) {
  //   //     return navigate("/auth/verify");
  //   //   }
  //   // }
  // }, [navigate, role, data, isPending]);

  return <>{children}</>;
}
