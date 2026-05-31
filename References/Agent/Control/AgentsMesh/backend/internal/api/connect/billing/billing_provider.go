package billingconnect

import (
	"context"
	"errors"
	"fmt"

	"connectrpc.com/connect"

	"github.com/anthropics/agentsmesh/backend/internal/domain/billing"
	billingsvc "github.com/anthropics/agentsmesh/backend/internal/service/billing"
	"github.com/anthropics/agentsmesh/backend/internal/service/payment"
)

// cancelViaProvider mirrors REST's billing_subscription_cancel.go provider
// dispatch — pick the active provider based on stored subscription IDs and
// call its CancelSubscription API. If no provider is configured / no
// provider IDs are present, the local cancellation still proceeds (REST
// behavior preserved).
//
// `immediate` chooses immediate vs cancel-at-period-end with Stripe /
// LemonSqueezy semantics: both providers treat `cancel_at_period_end=true`
// as "don't immediately cancel, just clear auto-renew".
func cancelViaProvider(ctx context.Context, svc *billingsvc.Service, sub *billing.Subscription, immediate bool) error {
	factory := svc.GetPaymentFactory()
	if factory == nil {
		return nil
	}
	provider, subscriptionID, err := pickProvider(factory, sub)
	if err != nil {
		return nil
	}
	if provider == nil || subscriptionID == "" {
		return nil
	}
	if err := provider.CancelSubscription(ctx, subscriptionID, immediate); err != nil {
		return connect.NewError(connect.CodeInternal, fmt.Errorf("failed to cancel subscription: %w", err))
	}
	return nil
}

// reactivateViaProvider mirrors REST ReactivateSubscription — flip
// cancel_at_period_end back to false on the provider side. Both Stripe and
// LemonSqueezy share the semantic.
func reactivateViaProvider(ctx context.Context, svc *billingsvc.Service, sub *billing.Subscription) error {
	factory := svc.GetPaymentFactory()
	if factory == nil {
		return nil
	}
	provider, subscriptionID, err := pickProvider(factory, sub)
	if err != nil {
		return nil
	}
	if provider == nil || subscriptionID == "" {
		return nil
	}
	if err := provider.CancelSubscription(ctx, subscriptionID, false); err != nil {
		return connect.NewError(connect.CodeInternal, fmt.Errorf("failed to reactivate subscription: %w", err))
	}
	return nil
}

// pickProvider chooses the provider based on which Stripe / LemonSqueezy
// subscription ID is set on the local record — preserves REST's ordering
// (LemonSqueezy first, then Stripe).
func pickProvider(factory *payment.Factory, sub *billing.Subscription) (payment.Provider, string, error) {
	if sub.LemonSqueezySubscriptionID != nil && *sub.LemonSqueezySubscriptionID != "" {
		p, err := factory.GetProvider(billing.PaymentProviderLemonSqueezy)
		if err != nil {
			return nil, "", err
		}
		return p, *sub.LemonSqueezySubscriptionID, nil
	}
	if sub.StripeSubscriptionID != nil && *sub.StripeSubscriptionID != "" {
		p, err := factory.GetProvider(billing.PaymentProviderStripe)
		if err != nil {
			return nil, "", err
		}
		return p, *sub.StripeSubscriptionID, nil
	}
	return nil, "", errors.New("no provider subscription id set")
}
