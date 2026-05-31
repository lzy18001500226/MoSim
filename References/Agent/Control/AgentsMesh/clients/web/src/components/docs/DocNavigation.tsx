"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useTranslations } from "next-intl";
import { getPrevNext } from "@/lib/docs-navigation";

export function DocNavigation() {
  const pathname = usePathname();
  const t = useTranslations();
  const { prev, next } = getPrevNext(pathname);

  if (!prev && !next) return null;

  return (
    <nav className="mt-16 pt-10 grid grid-cols-1 md:grid-cols-2 gap-4">
      {prev ? (
        <Link
          href={prev.href}
          className="azure-light-card azure-light-card-hover rounded-xl p-5 group"
        >
          <span className="block text-[11px] font-semibold uppercase tracking-[0.14em] text-[var(--azure-light-ink-soft)]">
            ← {t("docs.pagination.previous")}
          </span>
          <span className="mt-2 block text-base font-semibold text-[var(--azure-light-ink)] group-hover:text-[var(--azure-light-cyan-ink)] transition-colors">
            {t(prev.titleKey)}
          </span>
        </Link>
      ) : (
        <div />
      )}
      {next ? (
        <Link
          href={next.href}
          className="azure-light-card azure-light-card-hover rounded-xl p-5 group md:text-right"
        >
          <span className="block text-[11px] font-semibold uppercase tracking-[0.14em] text-[var(--azure-light-ink-soft)]">
            {t("docs.pagination.next")} →
          </span>
          <span className="mt-2 block text-base font-semibold text-[var(--azure-light-ink)] group-hover:text-[var(--azure-light-cyan-ink)] transition-colors">
            {t(next.titleKey)}
          </span>
        </Link>
      ) : (
        <div />
      )}
    </nav>
  );
}
