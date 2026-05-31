package invitation

import (
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
)

func TestInvitation_IsExpired(t *testing.T) {
	now := time.Now()
	pastTime := now.Add(-24 * time.Hour)
	futureTime := now.Add(24 * time.Hour)

	t.Run("should return true when expired", func(t *testing.T) {
		i := &Invitation{
			ExpiresAt: pastTime,
		}
		assert.True(t, i.IsExpired())
	})

	t.Run("should return false when not expired", func(t *testing.T) {
		i := &Invitation{
			ExpiresAt: futureTime,
		}
		assert.False(t, i.IsExpired())
	})
}

func TestInvitation_IsAccepted(t *testing.T) {
	now := time.Now()

	t.Run("should return true when accepted", func(t *testing.T) {
		i := &Invitation{
			AcceptedAt: &now,
		}
		assert.True(t, i.IsAccepted())
	})

	t.Run("should return false when not accepted", func(t *testing.T) {
		i := &Invitation{
			AcceptedAt: nil,
		}
		assert.False(t, i.IsAccepted())
	})
}

func TestInvitation_IsPending(t *testing.T) {
	now := time.Now()
	pastTime := now.Add(-24 * time.Hour)
	futureTime := now.Add(24 * time.Hour)

	t.Run("should return true when not accepted and not expired", func(t *testing.T) {
		i := &Invitation{
			ExpiresAt:  futureTime,
			AcceptedAt: nil,
		}
		assert.True(t, i.IsPending())
	})

	t.Run("should return false when accepted", func(t *testing.T) {
		i := &Invitation{
			ExpiresAt:  futureTime,
			AcceptedAt: &now,
		}
		assert.False(t, i.IsPending())
	})

	t.Run("should return false when expired", func(t *testing.T) {
		i := &Invitation{
			ExpiresAt:  pastTime,
			AcceptedAt: nil,
		}
		assert.False(t, i.IsPending())
	})

	t.Run("should return false when both accepted and expired", func(t *testing.T) {
		i := &Invitation{
			ExpiresAt:  pastTime,
			AcceptedAt: &now,
		}
		assert.False(t, i.IsPending())
	})
}

func TestInvitation_TableName(t *testing.T) {
	i := Invitation{}
	assert.Equal(t, "invitations", i.TableName())
}
