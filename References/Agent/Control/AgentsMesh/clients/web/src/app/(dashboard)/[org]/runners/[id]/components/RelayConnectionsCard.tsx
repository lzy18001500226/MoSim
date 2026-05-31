"use client";

import { formatDistanceToNow } from "date-fns";
import { Radio } from "lucide-react";
import type { RelayConnectionInfo } from "@/lib/api";
import { useTranslations } from "next-intl";

interface RelayConnectionsCardProps {
  connections: RelayConnectionInfo[];
}

export function RelayConnectionsCard({ connections }: RelayConnectionsCardProps) {
  const t = useTranslations();

  if (connections.length === 0) return null;

  return (
    <div className="bg-card rounded-lg border border-border p-6 md:col-span-2">
      <h3 className="text-lg font-medium text-foreground mb-4 flex items-center">
        <Radio className="w-5 h-5 mr-2 text-green-500" />
        {t("runners.detail.relayConnections")}
        <span className="ml-2 text-sm font-normal text-muted-foreground">
          ({connections.length})
        </span>
      </h3>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-border">
          <thead>
            <tr>
              <th className="px-4 py-2 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                Pod
              </th>
              <th className="px-4 py-2 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                Relay
              </th>
              <th className="px-4 py-2 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                {t("runners.detail.status")}
              </th>
              <th className="px-4 py-2 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                {t("runners.detail.connectedSince")}
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {connections.map((conn) => (
              <tr key={conn.pod_key}>
                <td className="px-4 py-3 text-sm font-mono text-foreground">
                  {conn.pod_key}
                </td>
                <td className="px-4 py-3 text-sm text-muted-foreground">
                  {extractRelayHost(conn.relay_url)}
                </td>
                <td className="px-4 py-3">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    conn.connected
                      ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
                      : "bg-muted text-muted-foreground"
                  }`}>
                    {conn.connected ? t("common.connected") : t("common.disconnected")}
                  </span>
                </td>
                <td className="px-4 py-3 text-sm text-muted-foreground">
                  {conn.connected_at
                    ? formatDistanceToNow(new Date(conn.connected_at), { addSuffix: true })
                    : "-"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function extractRelayHost(url: string): string {
  try {
    return new URL(url).host;
  } catch {
    return url;
  }
}
