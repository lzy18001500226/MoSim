"use client";

import { PersonalSettingsSidebar } from "@/components/settings/PersonalSettingsSidebar";

export default function PersonalSettingsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex h-full">
      {/* Sidebar */}
      <div className="w-64 border-r border-border bg-background flex-shrink-0">
        <PersonalSettingsSidebar />
      </div>

      {/* Main content */}
      <div className="flex-1 overflow-auto">{children}</div>
    </div>
  );
}
