"use client";

import Link from "next/link";
import { Logo } from "@/components/common";

interface AuthShellProps {
  title: string;
  subtitle: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
}

export function AuthShell({ title, subtitle, children, footer }: AuthShellProps) {
  return (
    <div className="azure-theme min-h-screen relative overflow-hidden bg-background flex items-center justify-center px-4 py-12">
      <div className="absolute -top-32 -right-32 w-[500px] h-[500px] bg-[var(--azure-cyan)]/10 blur-[120px] rounded-full azure-orb pointer-events-none" />
      <div
        className="absolute -bottom-32 -left-32 w-[400px] h-[400px] bg-[var(--azure-mint)]/10 blur-[100px] rounded-full azure-orb pointer-events-none"
        style={{ animationDelay: "1.5s" }}
      />
      <div
        className="absolute inset-0 opacity-[0.04] pointer-events-none"
        style={{
          backgroundImage:
            "linear-gradient(var(--azure-cyan) 1px, transparent 1px), linear-gradient(90deg, var(--azure-cyan) 1px, transparent 1px)",
          backgroundSize: "80px 80px",
          maskImage: "radial-gradient(ellipse at center, black 0%, transparent 70%)",
          WebkitMaskImage: "radial-gradient(ellipse at center, black 0%, transparent 70%)",
        }}
      />

      <div className="relative z-10 w-full max-w-md">
        <div className="text-center mb-8">
          <Link href="/" className="inline-flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-lg overflow-hidden">
              <Logo />
            </div>
            <span className="font-headline text-2xl font-bold tracking-tighter text-[var(--azure-cyan)]">
              AgentsMesh
            </span>
          </Link>
        </div>

        <div className="azure-glass rounded-3xl border border-white/10 azure-glow-cyan-lg p-8 sm:p-10">
          <div className="text-center mb-8">
            <h1 className="font-headline text-3xl font-bold text-foreground mb-2">{title}</h1>
            <p className="text-sm text-[var(--azure-text-muted)]">{subtitle}</p>
          </div>
          {children}
        </div>

        {footer && (
          <p className="mt-6 text-center text-sm text-[var(--azure-text-muted)]">{footer}</p>
        )}
      </div>
    </div>
  );
}
