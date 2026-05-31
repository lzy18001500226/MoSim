package aggregator

import (
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestFullRedrawThrottler_NewDefault(t *testing.T) {
	throttler := NewFullRedrawThrottler()
	require.NotNil(t, throttler)

	// Verify defaults
	assert.Equal(t, 1*time.Second, throttler.baseWindowSize)
	assert.Equal(t, 1*time.Second, throttler.minWindowSize)
	assert.Equal(t, 4*time.Second, throttler.maxWindowSize)
	assert.Equal(t, 200*time.Millisecond, throttler.minDelay)
	assert.Equal(t, 1000*time.Millisecond, throttler.maxDelay)
	assert.Equal(t, 1.5, throttler.thresholdFreq)
	assert.False(t, throttler.IsThrottling())
}

func TestFullRedrawThrottler_Options(t *testing.T) {
	throttler := NewFullRedrawThrottler(
		WithThrottlerWindowSize(5*time.Second),
		WithThrottlerMinWindow(2*time.Second),
		WithThrottlerMaxWindow(10*time.Second),
		WithThrottlerMinDelay(100*time.Millisecond),
		WithThrottlerMaxDelay(2*time.Second),
		WithThrottlerThreshold(5.0),
		WithThrottlerBandwidthThresholds(100*1024, 300*1024),
	)

	assert.Equal(t, 5*time.Second, throttler.baseWindowSize)
	assert.Equal(t, 2*time.Second, throttler.minWindowSize)
	assert.Equal(t, 10*time.Second, throttler.maxWindowSize)
	assert.Equal(t, 100*time.Millisecond, throttler.minDelay)
	assert.Equal(t, 2*time.Second, throttler.maxDelay)
	assert.Equal(t, 5.0, throttler.thresholdFreq)
	assert.Equal(t, 100*1024, throttler.lowBandwidthThreshold)
	assert.Equal(t, 300*1024, throttler.highBandwidthThreshold)
}

func TestFullRedrawThrottler_RecordAndFrequency(t *testing.T) {
	// Use short window for testing
	throttler := NewFullRedrawThrottler(
		WithThrottlerWindowSize(100*time.Millisecond),
		WithThrottlerMinWindow(100*time.Millisecond),
		WithThrottlerMaxWindow(100*time.Millisecond),
	)

	// No records yet
	assert.Equal(t, 0.0, throttler.GetFrequency())

	// Record some redraws (10KB each - small frames won't trigger bandwidth adjustment)
	throttler.RecordRedraw(10 * 1024)
	throttler.RecordRedraw(10 * 1024)
	throttler.RecordRedraw(10 * 1024)

	// Frequency should be 3 / 0.1s = 30/s
	assert.InDelta(t, 30.0, throttler.GetFrequency(), 1.0)

	// Wait for window to expire
	time.Sleep(150 * time.Millisecond)

	// Records should have expired
	assert.Equal(t, 0.0, throttler.GetFrequency())
}

func TestFullRedrawThrottler_WindowSliding(t *testing.T) {
	throttler := NewFullRedrawThrottler(
		WithThrottlerWindowSize(100*time.Millisecond),
		WithThrottlerMinWindow(100*time.Millisecond),
		WithThrottlerMaxWindow(100*time.Millisecond),
	)

	// Record 2 redraws (small frames)
	throttler.RecordRedraw(1024)
	throttler.RecordRedraw(1024)

	// Wait half the window
	time.Sleep(60 * time.Millisecond)

	// Record 2 more
	throttler.RecordRedraw(1024)
	throttler.RecordRedraw(1024)

	// All 4 should be in window
	freq := throttler.GetFrequency()
	assert.InDelta(t, 40.0, freq, 5.0) // 4 / 0.1s = 40/s

	// Wait for first 2 to expire
	time.Sleep(60 * time.Millisecond)

	// Only last 2 should remain
	freq = throttler.GetFrequency()
	assert.InDelta(t, 20.0, freq, 5.0) // 2 / 0.1s = 20/s
}

func TestFullRedrawThrottler_Reset(t *testing.T) {
	throttler := NewFullRedrawThrottler(
		WithThrottlerWindowSize(1*time.Second),
		WithThrottlerMinWindow(1*time.Second),
		WithThrottlerMaxWindow(1*time.Second),
		WithThrottlerThreshold(2.0),
		// Use high bandwidth threshold to avoid bandwidth-triggered throttling
		WithThrottlerBandwidthThresholds(10*1024*1024, 20*1024*1024),
	)

	// Add redraws and flush
	for i := 0; i < 5; i++ {
		throttler.RecordRedraw(1024)
	}
	throttler.MarkFlushed()

	assert.True(t, throttler.IsThrottling())

	// Reset
	throttler.Reset()

	assert.False(t, throttler.IsThrottling())
	assert.Equal(t, 0.0, throttler.GetFrequency())
	assert.True(t, throttler.ShouldFlush())
}

func TestFullRedrawThrottler_ZeroFrequency(t *testing.T) {
	throttler := NewFullRedrawThrottler()

	// No redraws recorded
	assert.Equal(t, 0.0, throttler.GetFrequency())
	assert.Equal(t, time.Duration(0), throttler.GetCurrentDelay())
	assert.False(t, throttler.IsThrottling())
	assert.True(t, throttler.ShouldFlush())
}

func TestFullRedrawThrottler_SingleRedraw(t *testing.T) {
	throttler := NewFullRedrawThrottler(
		WithThrottlerWindowSize(1*time.Second),
		WithThrottlerMinWindow(1*time.Second),
		WithThrottlerMaxWindow(1*time.Second),
		WithThrottlerThreshold(2.0),
		// Use high bandwidth threshold to avoid bandwidth-triggered throttling
		WithThrottlerBandwidthThresholds(10*1024*1024, 20*1024*1024),
	)

	throttler.RecordRedraw(1024)

	// Single redraw = 1/s, below threshold of 2.0/s
	freq := throttler.GetFrequency()
	assert.InDelta(t, 1.0, freq, 0.1)
	assert.False(t, throttler.IsThrottling())
}

func TestFullRedrawThrottler_ExactlyAtThreshold(t *testing.T) {
	throttler := NewFullRedrawThrottler(
		WithThrottlerWindowSize(1*time.Second),
		WithThrottlerMinWindow(1*time.Second),
		WithThrottlerMaxWindow(1*time.Second),
		WithThrottlerThreshold(3.0), // threshold 3/s
		WithThrottlerMinDelay(100*time.Millisecond),
		// Use high bandwidth threshold to avoid bandwidth-triggered throttling
		WithThrottlerBandwidthThresholds(10*1024*1024, 20*1024*1024),
	)

	// Record 4 redraws = 4/s > threshold 3/s (need to exceed threshold)
	throttler.RecordRedraw(1024)
	throttler.RecordRedraw(1024)
	throttler.RecordRedraw(1024)
	throttler.RecordRedraw(1024)

	// Above threshold should start throttling
	assert.True(t, throttler.IsThrottling())
	delay := throttler.GetCurrentDelay()
	// Should be at or above minDelay
	assert.True(t, delay >= 100*time.Millisecond, "above threshold should use minDelay or more")
}
