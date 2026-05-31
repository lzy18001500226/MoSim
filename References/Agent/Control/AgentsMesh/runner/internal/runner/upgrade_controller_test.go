package runner

import (
	"testing"

	"github.com/anthropics/agentsmesh/runner/internal/updater"
)

func TestUpgradeControllerTryStartUpgrade(t *testing.T) {
	uc := newUpgradeController()

	// First call should succeed
	if !uc.TryStartUpgrade() {
		t.Error("first TryStartUpgrade should return true")
	}

	// Second call should fail (already upgrading)
	if uc.TryStartUpgrade() {
		t.Error("second TryStartUpgrade should return false")
	}

	// After finish, should succeed again
	uc.FinishUpgrade()
	if !uc.TryStartUpgrade() {
		t.Error("TryStartUpgrade after FinishUpgrade should return true")
	}
}

func TestUpgradeControllerDraining(t *testing.T) {
	uc := newUpgradeController()

	if uc.IsDraining() {
		t.Error("should not be draining initially")
	}

	uc.SetDraining(true)
	if !uc.IsDraining() {
		t.Error("should be draining after SetDraining(true)")
	}

	uc.SetDraining(false)
	if uc.IsDraining() {
		t.Error("should not be draining after SetDraining(false)")
	}
}

func TestUpgradeControllerUpdater(t *testing.T) {
	uc := newUpgradeController()

	if uc.GetUpdater() != nil {
		t.Error("updater should be nil initially")
	}

	u := updater.New("1.0.0")
	uc.SetUpdater(u)
	if uc.GetUpdater() != u {
		t.Error("GetUpdater should return the set updater")
	}
}

func TestUpgradeControllerRestartFunc(t *testing.T) {
	uc := newUpgradeController()

	if uc.GetRestartFunc() != nil {
		t.Error("restart func should be nil initially")
	}

	called := false
	fn := func() (int, error) { called = true; return 0, nil }
	uc.SetRestartFunc(fn)

	got := uc.GetRestartFunc()
	if got == nil {
		t.Fatal("GetRestartFunc should return the set function")
	}
	got()
	if !called {
		t.Error("restart func should have been called")
	}
}

func TestUpgradeControllerInterfaceCompliance(t *testing.T) {
	var _ UpgradeController = (*upgradeController)(nil)
}
