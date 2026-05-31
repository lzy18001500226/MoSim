"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

interface PageHeaderProps extends Omit<React.HTMLAttributes<HTMLElement>, "title"> {
  title: React.ReactNode;
  subtitle?: React.ReactNode;
  breadcrumb?: React.ReactNode;
  actions?: React.ReactNode;
}

export const PageHeader = React.forwardRef<HTMLElement, PageHeaderProps>(
  ({ className, title, subtitle, breadcrumb, actions, ...props }, ref) => (
    <header
      ref={ref}
      className={cn(
        "flex flex-col gap-2 border-b border-border bg-background px-6 py-4",
        className,
      )}
      {...props}
    >
      {breadcrumb && <div className="-mb-1">{breadcrumb}</div>}
      <div className="flex items-start justify-between gap-4">
        <div className="flex min-w-0 flex-col gap-1">
          <h1 className="truncate text-xl font-semibold tracking-tight text-foreground">
            {title}
          </h1>
          {subtitle && <p className="text-sm text-muted-foreground">{subtitle}</p>}
        </div>
        {actions && <div className="flex shrink-0 items-center gap-2">{actions}</div>}
      </div>
    </header>
  ),
);
PageHeader.displayName = "PageHeader";
