package aggregator

import (
	"sync"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
)

func TestFullRedrawThrottler_DelayCalculation(t *testing.T) {
	throttler := NewFullRedrawThrottler(
		WithThrottlerWindowSize(1*time.Second),
		WithThrottlerMinWindow(1*time.Second),
		WithThrottlerMaxWindow(1*time.Second),
		WithThrottlerThreshold(2.5),
		WithThrottlerMinDelay(200*time.Millisecond),
		WithThrottlerMaxDelay(1000*time.Millisecond),
		// Use high bandwidth threshold to avoid bandwidth-triggered throttling
		WithThrottlerBandwidthThresholds(10*1024*1024, 20*1024*1024),
	)

	// Below threshold: no delay (small frames)
	throttler.RecordRedraw(1024)
	throttler.RecordRedraw(1024) // 2/s < 2.5/s threshold
	assert.Equal(t, time.Duration(0), throttler.GetCurrentDelay())
	assert.False(t, throttler.IsThrottling())

	// At threshold: min delay
	throttler.RecordRedraw(1024) // 3/s >= 2.5/s threshold
	delay := throttler.GetCurrentDelay()
	assert.True(t, delay >= 200*time.Millisecond, "delay should be at least minDelay")
	assert.True(t, throttler.IsThrottling())

	// Add more redraws to increase delay
	for i := 0; i < 7; i++ {
		throttler.RecordRedraw(1024)
	}
	// Now 10/s - should be near max delay
	delay = throttler.GetCurrentDelay()
	assert.True(t, delay >= 800*time.Millisecond, "delay should be close to maxDelay at 10/s")
}

func TestFullRedrawThrottler_ShouldFlush(t *testing.T) {
	throttler := NewFullRedrawThrottler(
		WithThrottlerWindowSize(1*time.Second),
		WithThrottlerMinWindow(1*time.Second),
		WithThrottlerMaxWindow(1*time.Second),
		WithThrottlerThreshold(2.0),
		WithThrottlerMinDelay(100*time.Millisecond),
		// Use high bandwidth threshold to avoid bandwidth-triggered throttling
		WithThrottlerBandwidthThresholds(10*1024*1024, 20*1024*1024),
	)

	// Initially should flush (no throttling - below threshold)
	assert.True(t, throttler.ShouldFlush())

	// Add redraws to trigger throttling (5/s > 2.0/s threshold)
	for i := 0; i < 5; i++ {
		throttler.RecordRedraw(1024)
	}

	// Now throttling is active, but ShouldFlush still returns true
	// because we haven't marked a flush yet (lastFlushTime is zero)
	// Mark a flush first
	throttler.MarkFlushed()

	// Immediately after marking flush, should not flush again (delay not passed)
	assert.False(t, throttler.ShouldFlush(), "Should not flush immediately after MarkFlushed")

	// Get the current delay to know how long to wait
	delay := throttler.GetCurrentDelay()
	t.Logf("Current delay: %v", delay)

	// Wait for delay to pass (plus some buffer)
	time.Sleep(delay + 50*time.Millisecond)

	// Now should be able to flush
	assert.True(t, throttler.ShouldFlush(), "Should flush after delay has passed")
}

func TestFullRedrawThrottler_GetNextCheckDelay(t *testing.T) {
	throttler := NewFullRedrawThrottler(
		WithThrottlerWindowSize(1*time.Second),
		WithThrottlerMinWindow(1*time.Second),
		WithThrottlerMaxWindow(1*time.Second),
		WithThrottlerThreshold(2.0),
		WithThrottlerMinDelay(100*time.Millisecond),
		WithThrottlerMaxDelay(1000*time.Millisecond),
		// Use high bandwidth threshold to avoid bandwidth-triggered throttling
		WithThrottlerBandwidthThresholds(10*1024*1024, 20*1024*1024),
	)

	// Not throttling - should return short default
	delay := throttler.GetNextCheckDelay()
	assert.Equal(t, 50*time.Millisecond, delay)

	// Trigger throttling (5/s > 2.0/s)
	for i := 0; i < 5; i++ {
		throttler.RecordRedraw(1024)
	}
	throttler.MarkFlushed()

	// Should return remaining time until next allowed flush
	delay = throttler.GetNextCheckDelay()
	assert.True(t, delay > 0, "should have positive delay when throttling")

	// The delay should be close to the throttle delay (since we just flushed)
	// plus a small buffer (10ms added in GetNextCheckDelay)
	currentThrottleDelay := throttler.GetCurrentDelay()
	t.Logf("Current throttle delay: %v, next check delay: %v", currentThrottleDelay, delay)

	// Allow some tolerance for timing
	assert.True(t, delay <= currentThrottleDelay+20*time.Millisecond,
		"delay should not exceed throttle delay plus buffer, got %v vs max %v",
		delay, currentThrottleDelay+20*time.Millisecond)
}

func TestFullRedrawThrottler_ConcurrentAccess(t *testing.T) {
	throttler := NewFullRedrawThrottler()

	var wg sync.WaitGroup
	numGoroutines := 10
	iterations := 100

	// Concurrent RecordRedraw calls
	for i := 0; i < numGoroutines; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for j := 0; j < iterations; j++ {
				throttler.RecordRedraw(50 * 1024) // 50KB frames
			}
		}()
	}

	// Concurrent ShouldFlush/MarkFlushed calls
	for i := 0; i < numGoroutines; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for j := 0; j < iterations; j++ {
				if throttler.ShouldFlush() {
					throttler.MarkFlushed()
				}
			}
		}()
	}

	// Concurrent GetFrequency/GetBandwidth calls
	for i := 0; i < numGoroutines; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for j := 0; j < iterations; j++ {
				_ = throttler.GetFrequency()
				_ = throttler.GetBandwidth()
				_ = throttler.GetEffectiveWindowSize()
			}
		}()
	}

	wg.Wait()
	// Test passes if no race conditions or panics
}

func TestFullRedrawThrottler_DelayLinearInterpolation(t *testing.T) {
	// Test that delay increases linearly between threshold and maxFreq
	throttler := NewFullRedrawThrottler(
		WithThrottlerWindowSize(1*time.Second),
		WithThrottlerMinWindow(1*time.Second),
		WithThrottlerMaxWindow(1*time.Second),
		WithThrottlerThreshold(2.5),
		WithThrottlerMinDelay(200*time.Millisecond),
		WithThrottlerMaxDelay(1000*time.Millisecond),
		// Use high bandwidth threshold to avoid bandwidth-triggered throttling
		WithThrottlerBandwidthThresholds(10*1024*1024, 20*1024*1024),
	)

	// Helper to record N redraws (small frames to avoid bandwidth throttling)
	recordN := func(n int) {
		throttler.Reset()
		for i := 0; i < n; i++ {
			throttler.RecordRedraw(1024)
		}
	}

	// At threshold (2.5/s but we can only do integers, so 3/s)
	recordN(3)
	delayAtThreshold := throttler.GetCurrentDelay()

	// At midpoint between threshold (2.5) and maxFreq (10) = 6.25/s, so 6
	recordN(6)
	delayAtMid := throttler.GetCurrentDelay()

	// At maxFreq (10/s)
	recordN(10)
	delayAtMax := throttler.GetCurrentDelay()

	// Verify ordering
	assert.True(t, delayAtThreshold <= delayAtMid, "mid delay should be >= threshold delay")
	assert.True(t, delayAtMid <= delayAtMax, "max delay should be >= mid delay")

	// Verify bounds
	assert.True(t, delayAtThreshold >= 200*time.Millisecond, "at threshold should be >= minDelay")
	assert.True(t, delayAtMax <= 1000*time.Millisecond, "at max should be <= maxDelay")
}

func TestFullRedrawThrottler_ExtremeFrequency(t *testing.T) {
	// Test behavior at very high frequencies (beyond maxFreq)
	throttler := NewFullRedrawThrottler(
		WithThrottlerWindowSize(1*time.Second),
		WithThrottlerMinWindow(1*time.Second),
		WithThrottlerMaxWindow(1*time.Second),
		WithThrottlerThreshold(2.5),
		WithThrottlerMinDelay(200*time.Millisecond),
		WithThrottlerMaxDelay(1000*time.Millisecond),
		// Use high bandwidth threshold to avoid bandwidth-triggered throttling
		WithThrottlerBandwidthThresholds(10*1024*1024, 20*1024*1024),
	)

	// Record 50 redraws (way beyond maxFreq of 10, small frames)
	for i := 0; i < 50; i++ {
		throttler.RecordRedraw(1024)
	}

	// Delay should be capped at maxDelay
	delay := throttler.GetCurrentDelay()
	assert.Equal(t, 1000*time.Millisecond, delay, "delay should be capped at maxDelay")
}

func TestFullRedrawThrottler_GetNextCheckDelay_NotThrottling(t *testing.T) {
	throttler := NewFullRedrawThrottler()

	// Not throttling - should return default 50ms
	delay := throttler.GetNextCheckDelay()
	assert.Equal(t, 50*time.Millisecond, delay)
}

func TestFullRedrawThrottler_GetNextCheckDelay_WhileThrottling(t *testing.T) {
	throttler := NewFullRedrawThrottler(
		WithThrottlerWindowSize(1*time.Second), // Long window to keep records
		WithThrottlerMinWindow(1*time.Second),
		WithThrottlerMaxWindow(1*time.Second),
		WithThrottlerThreshold(2.0),
		WithThrottlerMinDelay(100*time.Millisecond),
		// Use high bandwidth threshold to avoid bandwidth-triggered throttling
		WithThrottlerBandwidthThresholds(10*1024*1024, 20*1024*1024),
	)

	// Trigger throttling
	for i := 0; i < 5; i++ {
		throttler.RecordRedraw(1024)
	}
	throttler.MarkFlushed()

	// Immediately after marking flush, GetNextCheckDelay should return
	// approximately the throttle delay (plus 10ms buffer)
	delay := throttler.GetNextCheckDelay()
	currentThrottleDelay := throttler.GetCurrentDelay()

	t.Logf("Throttle delay: %v, next check delay: %v", currentThrottleDelay, delay)

	// Should be close to throttle delay
	assert.True(t, delay > 50*time.Millisecond, "while throttling, should have substantial delay")
	assert.True(t, delay <= currentThrottleDelay+20*time.Millisecond, "should not exceed throttle delay plus buffer")
}

func TestFullRedrawThrottler_ShouldFlush_BeforeMarkFlushed(t *testing.T) {
	throttler := NewFullRedrawThrottler(
		WithThrottlerWindowSize(1*time.Second),
		WithThrottlerMinWindow(1*time.Second),
		WithThrottlerMaxWindow(1*time.Second),
		WithThrottlerThreshold(2.0),
		WithThrottlerMinDelay(100*time.Millisecond),
		// Use high bandwidth threshold to avoid bandwidth-triggered throttling
		WithThrottlerBandwidthThresholds(10*1024*1024, 20*1024*1024),
	)

	// Trigger throttling
	for i := 0; i < 5; i++ {
		throttler.RecordRedraw(1024)
	}

	// Before MarkFlushed, lastFlushTime is zero
	// ShouldFlush checks time.Since(zero) which is huge, so should return true
	assert.True(t, throttler.ShouldFlush(), "before first flush, should always allow")
}

func TestFullRedrawThrottler_CleanExpiredDuringOperations(t *testing.T) {
	throttler := NewFullRedrawThrottler(
		WithThrottlerWindowSize(50*time.Millisecond),
		WithThrottlerMinWindow(50*time.Millisecond),
		WithThrottlerMaxWindow(50*time.Millisecond),
		WithThrottlerThreshold(5.0),
		// Use high bandwidth threshold to avoid bandwidth-triggered throttling
		WithThrottlerBandwidthThresholds(10*1024*1024, 20*1024*1024),
	)

	// Record some redraws
	for i := 0; i < 10; i++ {
		throttler.RecordRedraw(1024)
	}
	assert.True(t, throttler.IsThrottling())

	// Wait for window to expire
	time.Sleep(100 * time.Millisecond)

	// Various operations should clean expired entries
	_ = throttler.ShouldFlush() // This calls cleanExpiredLocked
	assert.False(t, throttler.IsThrottling(), "after window expires, should not be throttling")

	_ = throttler.GetFrequency() // This also cleans
	assert.Equal(t, 0.0, throttler.GetFrequency())
}
