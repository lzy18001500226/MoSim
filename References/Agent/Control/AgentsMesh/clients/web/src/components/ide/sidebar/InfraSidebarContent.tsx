"use client";

import { useSearchParams, useRouter, useParams } from "next/navigation";
import { cn } from "@/lib/utils";
import { useTranslations } from "next-intl";
import { RepositoriesSidebarContent } from "./RepositoriesSidebarContent";
import { RunnersSidebarContent } from "./RunnersSidebarContent";

interface InfraSidebarContentProps {
  className?: string;
  onImportRepo?: () => void;
  onAddRunner?: () => void;
}

type InfraTab = "repositories" | "runners";

const TABS: { id: InfraTab; labelKey: string }[] = [
  { id: "runners", labelKey: "infra.tabs.runners" },
  { id: "repositories", labelKey: "infra.tabs.repositories" },
];

export function InfraSidebarContent({ className, onImportRepo, onAddRunner }: InfraSidebarContentProps) {
  const t = useTranslations();
  const router = useRouter();
  const params = useParams<{ org: string }>();
  const searchParams = useSearchParams();

  const tab: InfraTab = (searchParams.get("tab") as InfraTab) || "runners";

  const navigate = (next: InfraTab) => {
    router.push(`/${params.org}/infra?tab=${next}`);
  };

  return (
    <div className={cn("flex h-full flex-col", className)}>
      <div role="tablist" className="grid grid-cols-2 gap-1 border-b border-border p-2">
        {TABS.map((item) => (
          <button
            key={item.id}
            role="tab"
            aria-selected={tab === item.id}
            onClick={() => navigate(item.id)}
            className={cn(
              "rounded-md px-3 py-1.5 text-sm transition-colors",
              tab === item.id
                ? "bg-primary text-primary-foreground shadow-xs"
                : "text-muted-foreground hover:bg-muted hover:text-foreground",
            )}
          >
            {t(item.labelKey)}
          </button>
        ))}
      </div>

      <div className="flex-1 overflow-hidden">
        {tab === "repositories" ? (
          <RepositoriesSidebarContent onImportRepo={onImportRepo} />
        ) : (
          <RunnersSidebarContent onAddRunner={onAddRunner} />
        )}
      </div>
    </div>
  );
}

export default InfraSidebarContent;
