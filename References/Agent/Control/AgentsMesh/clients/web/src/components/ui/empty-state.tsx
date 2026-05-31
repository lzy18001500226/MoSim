"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

export type EmptyStateSize = "compact" | "default" | "full";

interface EmptyStateProps extends Omit<React.HTMLAttributes<HTMLDivElement>, "title"> {
  size?: EmptyStateSize;
  icon?: React.ReactNode;
  title: React.ReactNode;
  description?: React.ReactNode;
  actions?: React.ReactNode;
}

const sizeStyles: Record<EmptyStateSize, { wrap: string; icon: string; title: string; desc: string }> = {
  compact: {
    wrap: "py-8 px-4 gap-3",
    icon: "h-8 w-8",
    title: "text-sm font-medium",
    desc: "text-xs",
  },
  default: {
    wrap: "py-12 px-6 gap-4",
    icon: "h-10 w-10",
    title: "text-base font-semibold",
    desc: "text-sm",
  },
  full: {
    wrap: "py-24 px-8 gap-5",
    icon: "h-12 w-12",
    title: "text-lg font-semibold",
    desc: "text-sm",
  },
};

export const EmptyState = React.forwardRef<HTMLDivElement, EmptyStateProps>(
  ({ className, size = "default", icon, title, description, actions, ...props }, ref) => {
    const s = sizeStyles[size];
    return (
      <div
        ref={ref}
        className={cn("flex flex-col items-center justify-center text-center", s.wrap, className)}
        {...props}
      >
        {icon && (
          <div className={cn("text-muted-foreground", s.icon, "flex items-center justify-center")}>
            {icon}
          </div>
        )}
        <h3 className={cn("text-foreground", s.title)}>{title}</h3>
        {description && (
          <p className={cn("max-w-prose text-muted-foreground", s.desc)}>{description}</p>
        )}
        {actions && <div className="flex items-center gap-2">{actions}</div>}
      </div>
    );
  },
);
EmptyState.displayName = "EmptyState";
