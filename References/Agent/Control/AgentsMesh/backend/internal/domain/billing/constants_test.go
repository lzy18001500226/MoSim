package billing

import (
	"testing"
)

// ===========================================
// Test Constants (constants.go)
// ===========================================

func TestPlanConstants(t *testing.T) {
	tests := []struct {
		name     string
		constant string
		expected string
	}{
		{"PlanBased", PlanBased, "based"},
		{"PlanPro", PlanPro, "pro"},
		{"PlanEnterprise", PlanEnterprise, "enterprise"},
		{"PlanOnPremise", PlanOnPremise, "onpremise"},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if tt.constant != tt.expected {
				t.Errorf("expected '%s', got '%s'", tt.expected, tt.constant)
			}
		})
	}
}

func TestSubscriptionStatusConstants(t *testing.T) {
	tests := []struct {
		name     string
		constant string
		expected string
	}{
		{"Active", SubscriptionStatusActive, "active"},
		{"PastDue", SubscriptionStatusPastDue, "past_due"},
		{"Canceled", SubscriptionStatusCanceled, "canceled"},
		{"Trialing", SubscriptionStatusTrialing, "trialing"},
		{"Frozen", SubscriptionStatusFrozen, "frozen"},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if tt.constant != tt.expected {
				t.Errorf("expected '%s', got '%s'", tt.expected, tt.constant)
			}
		})
	}
}

func TestPaymentProviderConstants(t *testing.T) {
	tests := []struct {
		name     string
		constant string
		expected string
	}{
		{"Stripe", PaymentProviderStripe, "stripe"},
		{"Alipay", PaymentProviderAlipay, "alipay"},
		{"WeChat", PaymentProviderWeChat, "wechat"},
		{"License", PaymentProviderLicense, "license"},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if tt.constant != tt.expected {
				t.Errorf("expected '%s', got '%s'", tt.expected, tt.constant)
			}
		})
	}
}

func TestPaymentMethodConstants(t *testing.T) {
	tests := []struct {
		name     string
		constant string
		expected string
	}{
		{"Card", PaymentMethodCard, "card"},
		{"AlipayQR", PaymentMethodAlipayQR, "alipay_qr"},
		{"AlipayAgreement", PaymentMethodAlipayAgreement, "alipay_agreement"},
		{"WeChatNative", PaymentMethodWeChatNative, "wechat_native"},
		{"WeChatContract", PaymentMethodWeChatContract, "wechat_contract"},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if tt.constant != tt.expected {
				t.Errorf("expected '%s', got '%s'", tt.expected, tt.constant)
			}
		})
	}
}

func TestBillingCycleConstants(t *testing.T) {
	if BillingCycleMonthly != "monthly" {
		t.Errorf("expected 'monthly', got %s", BillingCycleMonthly)
	}
	if BillingCycleYearly != "yearly" {
		t.Errorf("expected 'yearly', got %s", BillingCycleYearly)
	}
}

func TestUsageTypeConstants(t *testing.T) {
	tests := []struct {
		name     string
		constant string
		expected string
	}{
		{"PodMinutes", UsageTypePodMinutes, "pod_minutes"},
		{"StorageGB", UsageTypeStorageGB, "storage_gb"},
		{"APIRequests", UsageTypeAPIRequests, "api_requests"},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if tt.constant != tt.expected {
				t.Errorf("expected '%s', got '%s'", tt.expected, tt.constant)
			}
		})
	}
}

func TestOrderTypeConstants(t *testing.T) {
	tests := []struct {
		name     string
		constant string
		expected string
	}{
		{"Subscription", OrderTypeSubscription, "subscription"},
		{"SeatPurchase", OrderTypeSeatPurchase, "seat_purchase"},
		{"PlanUpgrade", OrderTypePlanUpgrade, "plan_upgrade"},
		{"Renewal", OrderTypeRenewal, "renewal"},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if tt.constant != tt.expected {
				t.Errorf("expected '%s', got '%s'", tt.expected, tt.constant)
			}
		})
	}
}

func TestOrderStatusConstants(t *testing.T) {
	tests := []struct {
		name     string
		constant string
		expected string
	}{
		{"Pending", OrderStatusPending, "pending"},
		{"Processing", OrderStatusProcessing, "processing"},
		{"Succeeded", OrderStatusSucceeded, "succeeded"},
		{"Failed", OrderStatusFailed, "failed"},
		{"Canceled", OrderStatusCanceled, "canceled"},
		{"Refunded", OrderStatusRefunded, "refunded"},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if tt.constant != tt.expected {
				t.Errorf("expected '%s', got '%s'", tt.expected, tt.constant)
			}
		})
	}
}

func TestTransactionTypeConstants(t *testing.T) {
	tests := []struct {
		name     string
		constant string
		expected string
	}{
		{"Payment", TransactionTypePayment, "payment"},
		{"Refund", TransactionTypeRefund, "refund"},
		{"Chargeback", TransactionTypeChargeback, "chargeback"},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if tt.constant != tt.expected {
				t.Errorf("expected '%s', got '%s'", tt.expected, tt.constant)
			}
		})
	}
}

func TestTransactionStatusConstants(t *testing.T) {
	tests := []struct {
		name     string
		constant string
		expected string
	}{
		{"Pending", TransactionStatusPending, "pending"},
		{"Succeeded", TransactionStatusSucceeded, "succeeded"},
		{"Failed", TransactionStatusFailed, "failed"},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if tt.constant != tt.expected {
				t.Errorf("expected '%s', got '%s'", tt.expected, tt.constant)
			}
		})
	}
}

func TestInvoiceStatusConstants(t *testing.T) {
	tests := []struct {
		name     string
		constant string
		expected string
	}{
		{"Draft", InvoiceStatusDraft, "draft"},
		{"Issued", InvoiceStatusIssued, "issued"},
		{"Paid", InvoiceStatusPaid, "paid"},
		{"Void", InvoiceStatusVoid, "void"},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if tt.constant != tt.expected {
				t.Errorf("expected '%s', got '%s'", tt.expected, tt.constant)
			}
		})
	}
}
