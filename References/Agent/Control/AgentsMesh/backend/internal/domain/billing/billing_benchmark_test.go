package billing

import (
	"testing"
)

// ===========================================
// Benchmark Tests
// ===========================================

func BenchmarkFeaturesScan(b *testing.B) {
	data := []byte(`{"unlimited_seats":true,"max_runners":10}`)
	for i := 0; i < b.N; i++ {
		var f Features
		f.Scan(data)
	}
}

func BenchmarkFeaturesValue(b *testing.B) {
	f := Features{"feature_x": true}
	for i := 0; i < b.N; i++ {
		f.Value()
	}
}

func BenchmarkSubscriptionPlanTableName(b *testing.B) {
	sp := SubscriptionPlan{}
	for i := 0; i < b.N; i++ {
		sp.TableName()
	}
}

func BenchmarkSubscriptionIsFrozen(b *testing.B) {
	s := Subscription{Status: SubscriptionStatusActive}
	for i := 0; i < b.N; i++ {
		s.IsFrozen()
	}
}

func BenchmarkLicenseIsValid(b *testing.B) {
	lic := License{IsActive: true}
	for i := 0; i < b.N; i++ {
		lic.IsValid()
	}
}
