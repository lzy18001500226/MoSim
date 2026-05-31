"use client";

import { useState, useEffect } from "react";
import { useRouter, useParams } from "next/navigation";
import { ArrowLeft } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import {
  getRelay,
  listRelays,
  forceUnregisterRelay,
  migrateSession,
  ActiveSession,
  RelayDetailResponse,
  RelayListResponse,
} from "@/lib/api/admin";
import { RelayDetailHeader } from "./relay-detail-header";
import { RelayInfoCards } from "./relay-info-cards";
import { RelaySessionsTable } from "./relay-sessions-table";

export default function RelayDetailPage() {
  const router = useRouter();
  const params = useParams();
  const relayId = decodeURIComponent(params.id as string);
  const [migratingPod, setMigratingPod] = useState<string | null>(null);
  const [targetRelay, setTargetRelay] = useState<string>("");
  const [isUnregistering, setIsUnregistering] = useState(false);
  const [isMigratingSession, setIsMigratingSession] = useState(false);

  const [data, setData] = useState<RelayDetailResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<unknown>(null);
  const [relaysData, setRelaysData] = useState<RelayListResponse | null>(null);
  const [refetchKey, setRefetchKey] = useState(0);

  useEffect(() => {
    let cancelled = false;
    getRelay(relayId)
      .then((result) => {
        if (cancelled) return;
        setData(result);
        setError(null);
        setIsLoading(false);
      })
      .catch((err) => {
        if (cancelled) return;
        setError(err);
        setIsLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [relayId, refetchKey]);

  useEffect(() => {
    let cancelled = false;
    listRelays()
      .then((result) => {
        if (!cancelled) setRelaysData(result);
      })
      .catch(() => {
        // Non-critical
      });
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    const interval = setInterval(() => setRefetchKey((k) => k + 1), 5000);
    return () => clearInterval(interval);
  }, []);

  const handleUnregister = async (migrate: boolean) => {
    const msg = migrate
      ? `Unregister relay "${relayId}" and migrate all sessions?`
      : `Unregister relay "${relayId}"? ${data?.session_count || 0} sessions will be affected.`;
    if (!confirm(msg)) return;
    setIsUnregistering(true);
    try {
      await forceUnregisterRelay(relayId, migrate);
      toast.success("Relay unregistered");
      router.push("/relays");
    } catch (err: unknown) {
      toast.error((err as { error?: string })?.error || "Failed to unregister relay");
    } finally {
      setIsUnregistering(false);
    }
  };

  const handleMigrate = async (session: ActiveSession) => {
    if (migratingPod === session.pod_key) {
      if (!targetRelay) {
        toast.error("Please select a target relay");
        return;
      }
      setIsMigratingSession(true);
      try {
        const result = await migrateSession(session.pod_key, targetRelay);
        toast.success(`Session migrated from ${result.from_relay} to ${result.to_relay}`);
        setMigratingPod(null);
        setTargetRelay("");
        setRefetchKey((k) => k + 1);
      } catch (err: unknown) {
        toast.error((err as { error?: string })?.error || "Failed to migrate session");
      } finally {
        setIsMigratingSession(false);
      }
    } else {
      setMigratingPod(session.pod_key);
      setTargetRelay("");
    }
  };

  const healthyRelays =
    relaysData?.data.filter((r) => r.healthy && r.id !== relayId) || [];

  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="h-8 w-48 animate-pulse rounded bg-muted" />
        <div className="h-32 animate-pulse rounded-lg bg-muted" />
        <div className="h-64 animate-pulse rounded-lg bg-muted" />
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="space-y-4">
        <Button variant="ghost" onClick={() => router.push("/relays")}>
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to Relays
        </Button>
        <Card>
          <CardContent className="py-8 text-center text-muted-foreground">
            Relay not found or has been unregistered.
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <RelayDetailHeader
        relay={data.relay}
        healthyRelays={healthyRelays}
        isUnregistering={isUnregistering}
        onUnregister={handleUnregister}
        onBack={() => router.push("/relays")}
      />
      <RelayInfoCards relay={data.relay} sessionCount={data.session_count} />
      <RelaySessionsTable
        sessions={data.sessions || []}
        healthyRelays={healthyRelays}
        migratingPod={migratingPod}
        targetRelay={targetRelay}
        isMigratingSession={isMigratingSession}
        onSetTargetRelay={setTargetRelay}
        onMigrate={handleMigrate}
        onCancelMigrate={() => {
          setMigratingPod(null);
          setTargetRelay("");
        }}
      />
    </div>
  );
}
