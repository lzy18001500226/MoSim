"use client";

import { useState, useEffect } from "react";
import { CreditCard } from "lucide-react";
import { toast } from "sonner";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  getOrganizationSubscription,
  getSubscriptionPlans,
  updateSubscriptionPlan,
  updateSubscriptionSeats,
  updateSubscriptionCycle,
  freezeSubscription,
  unfreezeSubscription,
  cancelSubscription,
  renewSubscription,
  setSubscriptionAutoRenew,
  setSubscriptionQuota,
} from "@/lib/api/admin";
import type { SubscriptionPlan } from "@/lib/api/admin";
import { PlanStatusPanel } from "./plan-status-panel";
import { BillingDetailsPanel } from "./billing-details-panel";
import { SeatsPanel } from "./seats-panel";
import { ActionsPanel } from "./actions-panel";
import { CustomQuotasPanel } from "./custom-quotas-panel";
import { NoSubscriptionPanel } from "./no-subscription-panel";
import { useSubscriptionActions } from "./use-subscription-actions";

export function SubscriptionSection({ orgId }: { orgId: number }) {
  const [renewMonths, setRenewMonths] = useState("1");
  const [newSeatCount, setNewSeatCount] = useState("");
  const [quotaResource, setQuotaResource] = useState("users");
  const [quotaLimit, setQuotaLimit] = useState("");

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [sub, setSub] = useState<any>(null);
  const [subLoading, setSubLoading] = useState(true);
  const [plans, setPlans] = useState<SubscriptionPlan[]>([]);
  const [refetchKey, setRefetchKey] = useState(0);

  useEffect(() => {
    let cancelled = false;
    getOrganizationSubscription(orgId)
      .then((result) => {
        if (cancelled) return;
        setSub(result);
        setSubLoading(false);
      })
      .catch((err: unknown) => {
        if (cancelled) return;
        if (err && typeof err === "object" && "status" in err && (err as { status: number }).status === 404) {
          setSub(null);
        }
        setSubLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [orgId, refetchKey]);

  useEffect(() => {
    let cancelled = false;
    getSubscriptionPlans(orgId)
      .then((result) => {
        if (!cancelled) setPlans(result?.data || []);
      })
      .catch(() => {
        // Keep empty plans on error
      });
    return () => {
      cancelled = true;
    };
  }, [orgId]);

  const refreshData = async () => { setRefetchKey((k) => k + 1); };

  const actions = useSubscriptionActions(orgId, sub, refreshData, {
    setNewSeatCount,
    setQuotaLimit,
  });

  if (subLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <CreditCard className="h-5 w-5" />
            Subscription
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="h-10 animate-pulse rounded bg-muted" />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!sub) {
    return <NoSubscriptionPanel plans={plans} orgId={orgId} onCreated={refreshData} />;
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <CreditCard className="h-5 w-5" />
          Subscription
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="grid gap-4 md:grid-cols-2">
          <PlanStatusPanel
            sub={sub}
            plans={plans}
            onChangePlan={(v) => { if (v !== sub.plan?.name) actions.handleChangePlan(v); }}
          />
          <BillingDetailsPanel
            sub={sub}
            onToggleCycle={actions.handleChangeCycle}
            onToggleAutoRenew={actions.handleToggleAutoRenew}
            cyclePending={actions.changeCyclePending}
            autoRenewPending={actions.autoRenewPending}
          />
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          <SeatsPanel
            seatUsage={sub.seat_usage}
            newSeatCount={newSeatCount}
            onNewSeatCountChange={setNewSeatCount}
            onSetSeats={(count) => actions.handleChangeSeats(count)}
            seatsPending={actions.changeSeatsPending}
          />
          <ActionsPanel
            status={sub.status}
            renewMonths={renewMonths}
            onRenewMonthsChange={setRenewMonths}
            onFreeze={actions.handleFreeze}
            onUnfreeze={actions.handleUnfreeze}
            onCancel={actions.handleCancel}
            onRenew={actions.handleRenew}
            freezePending={actions.freezePending}
            unfreezePending={actions.unfreezePending}
            cancelPending={actions.cancelPending}
            renewPending={actions.renewPending}
          />
        </div>

        <CustomQuotasPanel
          plan={sub.plan}
          customQuotas={sub.custom_quotas}
          quotaResource={quotaResource}
          quotaLimit={quotaLimit}
          onQuotaResourceChange={setQuotaResource}
          onQuotaLimitChange={setQuotaLimit}
          onSetQuota={(resource, limit) => actions.handleSetQuota(resource, limit)}
          quotaPending={actions.quotaPending}
        />

        {(sub.has_stripe || sub.has_alipay || sub.has_wechat || sub.has_lemonsqueezy) && (
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <span>Payment Integrations:</span>
            {sub.has_stripe && <Badge variant="outline" className="text-xs">Stripe</Badge>}
            {sub.has_alipay && <Badge variant="outline" className="text-xs">Alipay</Badge>}
            {sub.has_wechat && <Badge variant="outline" className="text-xs">WeChat</Badge>}
            {sub.has_lemonsqueezy && <Badge variant="outline" className="text-xs">LemonSqueezy</Badge>}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
