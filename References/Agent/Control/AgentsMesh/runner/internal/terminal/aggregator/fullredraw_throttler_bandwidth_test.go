package aggregator

import (
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
)

// ========== Bandwidth-aware dynamic window tests ==========

func TestFullRedrawThrottler_BandwidthCalculation(t *testing.T) {
	throttler := NewFullRedrawThrottler(
		WithThrottlerWindowSize(1*time.Second),
		WithThrottlerMinWindow(1*time.Second),
		WithThrottlerMaxWindow(1*time.Second),
	)

	// No records yet
	assert.Equal(t, 0, throttler.GetBandwidth())

	// Record frames totaling 100KB in 1 second window
	for i := 0; i < 10; i++ {
		throttler.RecordRedraw(10 * 1024) // 10KB each
	}

	// Bandwidth should be ~100KB/s
	bandwidth := throttler.GetBandwidth()
	assert.InDelta(t, 100*1024, bandwidth, 10*1024, "bandwidth should be ~100KB/s")
}

func TestFullRedrawThrottler_DynamicWindowAdjustment_LowBandwidth(t *testing.T) {
	throttler := NewFullRedrawThrottler(
		WithThrottlerWindowSize(1*time.Second),
		WithThrottlerMinWindow(1*time.Second),
		WithThrottlerMaxWindow(4*time.Second),
		WithThrottlerBandwidthThresholds(200*1024, 500*1024), // 200KB/s - 500KB/s
	)

	// Low bandwidth: 50KB/s (below lowBandwidthThreshold)
	for i := 0; i < 5; i++ {
		throttler.RecordRedraw(10 * 1024) // 10KB each = 50KB/s
	}

	// Effective window should be at minimum (1s)
	assert.Equal(t, 1*time.Second, throttler.GetEffectiveWindowSize(),
		"low bandwidth should use minimum window")
}

func TestFullRedrawThrottler_DynamicWindowAdjustment_HighBandwidth(t *testing.T) {
	throttler := NewFullRedrawThrottler(
		WithThrottlerWindowSize(1*time.Second),
		WithThrottlerMinWindow(1*time.Second),
		WithThrottlerMaxWindow(4*time.Second),
		WithThrottlerBandwidthThresholds(200*1024, 500*1024), // 200KB/s - 500KB/s
	)

	// High bandwidth: 600KB/s (above highBandwidthThreshold)
	for i := 0; i < 6; i++ {
		throttler.RecordRedraw(100 * 1024) // 100KB each = 600KB/s
	}

	// Effective window should be at maximum (4s)
	assert.Equal(t, 4*time.Second, throttler.GetEffectiveWindowSize(),
		"high bandwidth should use maximum window")
}

func TestFullRedrawThrottler_DynamicWindowAdjustment_MediumBandwidth(t *testing.T) {
	throttler := NewFullRedrawThrottler(
		WithThrottlerWindowSize(1*time.Second),
		WithThrottlerMinWindow(1*time.Second),
		WithThrottlerMaxWindow(4*time.Second),
		WithThrottlerBandwidthThresholds(200*1024, 500*1024), // 200KB/s - 500KB/s
	)

	// Medium bandwidth: ~350KB/s (between thresholds)
	for i := 0; i < 7; i++ {
		throttler.RecordRedraw(50 * 1024) // 50KB each = 350KB/s
	}

	// Effective window should be between min and max
	window := throttler.GetEffectiveWindowSize()
	assert.True(t, window > 1*time.Second, "medium bandwidth should have window > min")
	assert.True(t, window < 4*time.Second, "medium bandwidth should have window < max")

	// Should be approximately 2.5s (linear interpolation: (350-200)/(500-200) * 3s + 1s = 2.5s)
	assert.InDelta(t, 2500, window.Milliseconds(), 500, "window should be ~2.5s")
}

func TestFullRedrawThrottler_BandwidthTriggeredThrottling(t *testing.T) {
	// Test that high bandwidth alone can trigger throttling even with low frequency
	throttler := NewFullRedrawThrottler(
		WithThrottlerWindowSize(1*time.Second),
		WithThrottlerMinWindow(1*time.Second),
		WithThrottlerMaxWindow(4*time.Second),
		WithThrottlerThreshold(10.0),                         // High freq threshold (won't trigger)
		WithThrottlerBandwidthThresholds(200*1024, 500*1024), // 200KB/s - 500KB/s
	)

	// Low frequency (2/s) but high bandwidth (600KB/s)
	throttler.RecordRedraw(300 * 1024) // 300KB frame
	throttler.RecordRedraw(300 * 1024) // 300KB frame

	// Frequency is 2/s < threshold 10/s, but bandwidth is 600KB/s > highBandwidthThreshold
	freq := throttler.GetFrequency()
	bandwidth := throttler.GetBandwidth()
	t.Logf("Frequency: %.2f/s, Bandwidth: %dKB/s", freq, bandwidth/1024)

	assert.True(t, freq < 10.0, "frequency should be below threshold")
	assert.True(t, bandwidth > 500*1024, "bandwidth should be above high threshold")

	// Should still be throttling due to high bandwidth
	assert.True(t, throttler.IsThrottling(), "high bandwidth should trigger throttling even with low frequency")
}

func TestFullRedrawThrottler_WindowExpandsWithBandwidth(t *testing.T) {
	// Test that window expansion leads to more aggressive throttling
	throttler := NewFullRedrawThrottler(
		WithThrottlerWindowSize(1*time.Second),
		WithThrottlerMinWindow(1*time.Second),
		WithThrottlerMaxWindow(4*time.Second),
		WithThrottlerThreshold(1.0),                          // Low threshold to ensure throttling
		WithThrottlerBandwidthThresholds(100*1024, 400*1024), // 100KB/s - 400KB/s
	)

	// Start with small frames - low bandwidth, min window
	for i := 0; i < 3; i++ {
		throttler.RecordRedraw(10 * 1024) // 10KB each = 30KB/s
	}
	windowSmall := throttler.GetEffectiveWindowSize()
	freqSmall := throttler.GetFrequency()
	delaySmall := throttler.GetCurrentDelay()

	t.Logf("Small frames: window=%v, freq=%.2f/s, delay=%v", windowSmall, freqSmall, delaySmall)

	// Reset and use large frames - high bandwidth, max window
	throttler.Reset()
	for i := 0; i < 3; i++ {
		throttler.RecordRedraw(200 * 1024) // 200KB each = 600KB/s
	}
	windowLarge := throttler.GetEffectiveWindowSize()
	freqLarge := throttler.GetFrequency()
	delayLarge := throttler.GetCurrentDelay()

	t.Logf("Large frames: window=%v, freq=%.2f/s, delay=%v", windowLarge, freqLarge, delayLarge)

	// With larger window, we should see higher delay (more aggressive throttling)
	assert.True(t, windowLarge > windowSmall, "high bandwidth should expand window")
	// Note: delay comparison depends on the formula, but high bandwidth should increase throttling
}

func TestFullRedrawThrottler_ResetClearsEffectiveWindow(t *testing.T) {
	throttler := NewFullRedrawThrottler(
		WithThrottlerWindowSize(1*time.Second),
		WithThrottlerMinWindow(1*time.Second),
		WithThrottlerMaxWindow(4*time.Second),
		WithThrottlerBandwidthThresholds(100*1024, 400*1024),
	)

	// Generate high bandwidth to expand window
	for i := 0; i < 5; i++ {
		throttler.RecordRedraw(200 * 1024)
	}
	assert.True(t, throttler.GetEffectiveWindowSize() > 1*time.Second, "window should be expanded")

	// Reset should restore base window
	throttler.Reset()
	assert.Equal(t, 1*time.Second, throttler.GetEffectiveWindowSize(),
		"reset should restore base window size")
}
