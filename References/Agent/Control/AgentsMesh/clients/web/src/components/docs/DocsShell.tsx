"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Sheet,
  SheetTrigger,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { cn } from "@/lib/utils";
import { useTranslations } from "next-intl";
import { docsNavSections, getBreadcrumbs } from "@/lib/docs-navigation";
import { AuthButtons, Logo } from "@/components/common";

function SidebarNav({
  onNavigate,
}: {
  onNavigate?: () => void;
}) {
  const pathname = usePathname();
  const t = useTranslations();

  return (
    <nav className="space-y-8">
      {docsNavSections.map((section) => (
        <div key={section.titleKey}>
          <h3 className="text-[11px] font-semibold mb-3 uppercase tracking-[0.14em] text-[var(--azure-light-ink-soft)]">
            {t(section.titleKey)}
          </h3>
          <ul className="space-y-1">
            {section.items.map((item) => {
              const active = pathname === item.href;
              return (
                <li key={item.href}>
                  <Link
                    href={item.href}
                    onClick={onNavigate}
                    className={cn(
                      "text-sm block px-3 py-1.5 rounded-full transition-colors",
                      active
                        ? "bg-[var(--azure-light-cyan-soft)] text-[var(--azure-light-cyan-ink)] font-semibold"
                        : "text-[var(--azure-light-ink-muted)] hover:text-[var(--azure-light-ink)] hover:bg-[var(--azure-light-surface-high)]"
                    )}
                  >
                    {t(item.titleKey)}
                  </Link>
                </li>
              );
            })}
          </ul>
        </div>
      ))}
    </nav>
  );
}

function BreadcrumbJsonLd({
  breadcrumbs,
  labels,
}: {
  breadcrumbs: Array<{ titleKey: string; href?: string }>;
  labels: string[];
}) {
  if (breadcrumbs.length <= 1) return null;

  const items = breadcrumbs.map((crumb, i) => ({
    "@type": "ListItem" as const,
    position: i + 1,
    name: labels[i],
    ...(crumb.href
      ? { item: `https://agentsmesh.ai${crumb.href}` }
      : {}),
  }));

  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{
        __html: JSON.stringify({
          "@context": "https://schema.org",
          "@type": "BreadcrumbList",
          itemListElement: items,
        }),
      }}
    />
  );
}

export default function DocsShell({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const t = useTranslations();
  const [mobileOpen, setMobileOpen] = useState(false);
  const breadcrumbs = getBreadcrumbs(pathname);
  const breadcrumbLabels = breadcrumbs.map((crumb) => t(crumb.titleKey));

  return (
    <div className="azure-light azure-light-mesh min-h-screen">
      <BreadcrumbJsonLd breadcrumbs={breadcrumbs} labels={breadcrumbLabels} />

      <header className="azure-light-glass sticky top-0 z-10">
        <div className="container mx-auto px-3 sm:px-4 py-3 sm:py-4 flex items-center justify-between gap-2">
          <div className="flex items-center gap-2 sm:gap-3 min-w-0">
            <Sheet open={mobileOpen} onOpenChange={setMobileOpen}>
              <SheetTrigger asChild>
                <Button
                  variant="ghost"
                  size="icon"
                  className="md:hidden flex-shrink-0"
                  aria-label={t("docs.nav.menu")}
                >
                  <svg
                    className="w-5 h-5"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M4 6h16M4 12h16M4 18h16"
                    />
                  </svg>
                </Button>
              </SheetTrigger>
              <SheetContent side="left" className="w-72 p-4 pt-6 azure-light">
                <SheetHeader className="mb-4">
                  <SheetTitle>{t("docs.title")}</SheetTitle>
                </SheetHeader>
                <SidebarNav onNavigate={() => setMobileOpen(false)} />
              </SheetContent>
            </Sheet>

            <Link href="/" className="flex items-center gap-2 min-w-0">
              <div className="w-7 h-7 sm:w-8 sm:h-8 rounded-lg overflow-hidden flex-shrink-0">
                <Logo />
              </div>
              <span className="text-base sm:text-xl font-semibold text-[var(--azure-light-ink)] truncate">
                AgentsMesh
              </span>
            </Link>
            <span className="hidden sm:inline-block ml-2 text-[11px] font-semibold uppercase tracking-[0.18em] text-[var(--azure-light-cyan-ink)]">
              Docs
            </span>
          </div>
          <div className="flex items-center gap-3 sm:gap-5 flex-shrink-0">
            <Link
              href="/docs"
              className="hidden sm:block text-sm font-medium text-[var(--azure-light-ink-muted)] hover:text-[var(--azure-light-ink)] transition-colors"
            >
              {t("landing.nav.docs")}
            </Link>
            <AuthButtons consoleVariant="outline" />
          </div>
        </div>
      </header>

      <div className="flex">
        <aside className="w-64 min-h-[calc(100vh-65px)] px-5 py-8 hidden md:block sticky top-[65px] h-[calc(100vh-65px)] overflow-y-auto bg-[var(--azure-light-surface)]">
          <SidebarNav />
        </aside>

        <main className="flex-1 px-4 sm:px-6 md:px-10 py-8 sm:py-10 max-w-4xl mx-auto min-w-0 w-full">
          {breadcrumbs.length > 1 && (
            <nav className="flex flex-wrap items-center gap-x-2 gap-y-1 text-xs mb-6 sm:mb-8 text-[var(--azure-light-ink-muted)]">
              {breadcrumbs.map((crumb, index) => (
                <span key={index} className="flex items-center gap-2">
                  {index > 0 && (
                    <span className="text-[var(--azure-light-ink-soft)]">/</span>
                  )}
                  {crumb.href ? (
                    <Link
                      href={crumb.href}
                      className="hover:text-[var(--azure-light-cyan-ink)] transition-colors"
                    >
                      {t(crumb.titleKey)}
                    </Link>
                  ) : (
                    <span className="text-[var(--azure-light-ink)] font-medium">
                      {t(crumb.titleKey)}
                    </span>
                  )}
                </span>
              ))}
            </nav>
          )}

          {children}
        </main>
      </div>

      <footer className="mt-24 bg-[var(--azure-light-surface)]">
        <div className="container mx-auto px-4 py-10">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <p className="text-sm text-[var(--azure-light-ink-muted)]">
              &copy; {new Date().getFullYear()} AgentsMesh.{" "}
              {t("common.allRightsReserved")}
            </p>
            <div className="flex gap-8">
              <Link
                href="/privacy"
                className="text-sm text-[var(--azure-light-ink-muted)] hover:text-[var(--azure-light-ink)] transition-colors"
              >
                {t("landing.footer.legal.privacy")}
              </Link>
              <Link
                href="/terms"
                className="text-sm text-[var(--azure-light-ink-muted)] hover:text-[var(--azure-light-ink)] transition-colors"
              >
                {t("landing.footer.legal.terms")}
              </Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
