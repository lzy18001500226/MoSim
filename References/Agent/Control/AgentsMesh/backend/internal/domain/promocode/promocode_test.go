package promocode

import (
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
)

func TestPromoCode_IsValid(t *testing.T) {
	now := time.Now()
	pastTime := now.Add(-24 * time.Hour)
	futureTime := now.Add(24 * time.Hour)
	maxUses := 10

	t.Run("should return true for valid active promo code", func(t *testing.T) {
		p := &PromoCode{
			IsActive: true,
			StartsAt: pastTime,
		}
		assert.True(t, p.IsValid())
	})

	t.Run("should return false for inactive promo code", func(t *testing.T) {
		p := &PromoCode{
			IsActive: false,
			StartsAt: pastTime,
		}
		assert.False(t, p.IsValid())
	})

	t.Run("should return false if not started yet", func(t *testing.T) {
		p := &PromoCode{
			IsActive: true,
			StartsAt: futureTime,
		}
		assert.False(t, p.IsValid())
	})

	t.Run("should return false if expired", func(t *testing.T) {
		p := &PromoCode{
			IsActive:  true,
			StartsAt:  pastTime.Add(-48 * time.Hour),
			ExpiresAt: &pastTime,
		}
		assert.False(t, p.IsValid())
	})

	t.Run("should return true if not expired", func(t *testing.T) {
		p := &PromoCode{
			IsActive:  true,
			StartsAt:  pastTime,
			ExpiresAt: &futureTime,
		}
		assert.True(t, p.IsValid())
	})

	t.Run("should return true with no expiration date", func(t *testing.T) {
		p := &PromoCode{
			IsActive:  true,
			StartsAt:  pastTime,
			ExpiresAt: nil,
		}
		assert.True(t, p.IsValid())
	})

	t.Run("should return false if max uses reached", func(t *testing.T) {
		p := &PromoCode{
			IsActive:  true,
			StartsAt:  pastTime,
			MaxUses:   &maxUses,
			UsedCount: 10,
		}
		assert.False(t, p.IsValid())
	})

	t.Run("should return false if max uses exceeded", func(t *testing.T) {
		p := &PromoCode{
			IsActive:  true,
			StartsAt:  pastTime,
			MaxUses:   &maxUses,
			UsedCount: 15,
		}
		assert.False(t, p.IsValid())
	})

	t.Run("should return true if uses remaining", func(t *testing.T) {
		p := &PromoCode{
			IsActive:  true,
			StartsAt:  pastTime,
			MaxUses:   &maxUses,
			UsedCount: 5,
		}
		assert.True(t, p.IsValid())
	})

	t.Run("should return true with unlimited uses", func(t *testing.T) {
		p := &PromoCode{
			IsActive:  true,
			StartsAt:  pastTime,
			MaxUses:   nil,
			UsedCount: 1000000,
		}
		assert.True(t, p.IsValid())
	})
}

func TestPromoCode_RemainingUses(t *testing.T) {
	maxUses := 10

	t.Run("should return -1 for unlimited uses", func(t *testing.T) {
		p := &PromoCode{
			MaxUses: nil,
		}
		assert.Equal(t, -1, p.RemainingUses())
	})

	t.Run("should return correct remaining uses", func(t *testing.T) {
		p := &PromoCode{
			MaxUses:   &maxUses,
			UsedCount: 3,
		}
		assert.Equal(t, 7, p.RemainingUses())
	})

	t.Run("should return 0 when exactly at max uses", func(t *testing.T) {
		p := &PromoCode{
			MaxUses:   &maxUses,
			UsedCount: 10,
		}
		assert.Equal(t, 0, p.RemainingUses())
	})

	t.Run("should return 0 when exceeded max uses", func(t *testing.T) {
		p := &PromoCode{
			MaxUses:   &maxUses,
			UsedCount: 15,
		}
		assert.Equal(t, 0, p.RemainingUses())
	})

	t.Run("should return full max uses when unused", func(t *testing.T) {
		p := &PromoCode{
			MaxUses:   &maxUses,
			UsedCount: 0,
		}
		assert.Equal(t, 10, p.RemainingUses())
	})
}

func TestPromoCode_TableName(t *testing.T) {
	p := PromoCode{}
	assert.Equal(t, "promo_codes", p.TableName())
}

func TestRedemption_TableName(t *testing.T) {
	r := Redemption{}
	assert.Equal(t, "promo_code_redemptions", r.TableName())
}
