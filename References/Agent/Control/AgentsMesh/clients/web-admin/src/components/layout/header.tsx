"use client";

import { usePathname } from "next/navigation";
import { Bell, Menu } from "lucide-react";
import { Button } from "@/components/ui/button";

const pageTitles: Record<string, string> = {
  "/": "Dashboard",
  "/users": "Users",
  "/organizations": "Organizations",
  "/runners": "Runners",
  "/relays": "Relays",
  "/skill-registries": "Skill Registries",
  "/promo-codes": "Promo Codes",
  "/support-tickets": "Support Tickets",
  "/audit-logs": "Audit Logs",
};

export function Header({ onMenuClick }: { onMenuClick?: () => void }) {
  const pathname = usePathname();

  // Get title - handle dynamic routes
  let title = pageTitles[pathname];
  if (!title) {
    if (pathname.startsWith("/users/")) title = "User Details";
    else if (pathname.startsWith("/organizations/")) title = "Organization Details";
    else if (pathname.startsWith("/runners/")) title = "Runner Details";
    else if (pathname.startsWith("/relays/")) title = "Relay Details";
    else if (pathname.startsWith("/skill-registries/")) title = "Skill Registry Details";
    else if (pathname.startsWith("/promo-codes/new")) title = "Create Promo Code";
    else if (pathname.startsWith("/promo-codes/")) title = "Promo Code Details";
    else if (pathname.startsWith("/support-tickets/")) title = "Ticket Details";
    else title = "Admin Console";
  }

  return (
    <header className="flex h-16 items-center justify-between border-b border-border bg-card px-4 md:px-6">
      <div className="flex items-center gap-2">
        {onMenuClick && (
          <Button
            variant="ghost"
            size="icon"
            className="md:hidden"
            onClick={onMenuClick}
          >
            <Menu className="h-5 w-5" />
            <span className="sr-only">Open menu</span>
          </Button>
        )}
        <h1 className="text-xl font-semibold">{title}</h1>
      </div>
      <div className="flex items-center gap-2">
        <Button variant="ghost" size="icon">
          <Bell className="h-5 w-5" />
        </Button>
      </div>
    </header>
  );
}
