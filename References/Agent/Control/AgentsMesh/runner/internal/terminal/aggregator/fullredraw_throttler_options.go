package aggregator

import "time"

// FullRedrawThrottlerOption is a functional option for FullRedrawThrottler.
type FullRedrawThrottlerOption func(*FullRedrawThrottler)

// WithThrottlerWindowSize sets the base sliding window size.
// The effective window will be adjusted between minWindow and maxWindow based on bandwidth.
func WithThrottlerWindowSize(d time.Duration) FullRedrawThrottlerOption {
	return func(t *FullRedrawThrottler) {
		t.baseWindowSize = d
	}
}

// WithThrottlerMinWindow sets the minimum window size (used when bandwidth is low).
func WithThrottlerMinWindow(d time.Duration) FullRedrawThrottlerOption {
	return func(t *FullRedrawThrottler) {
		t.minWindowSize = d
	}
}

// WithThrottlerMaxWindow sets the maximum window size (used when bandwidth is high).
func WithThrottlerMaxWindow(d time.Duration) FullRedrawThrottlerOption {
	return func(t *FullRedrawThrottler) {
		t.maxWindowSize = d
	}
}

// WithThrottlerMinDelay sets the minimum throttle delay.
func WithThrottlerMinDelay(d time.Duration) FullRedrawThrottlerOption {
	return func(t *FullRedrawThrottler) {
		t.minDelay = d
	}
}

// WithThrottlerMaxDelay sets the maximum throttle delay.
func WithThrottlerMaxDelay(d time.Duration) FullRedrawThrottlerOption {
	return func(t *FullRedrawThrottler) {
		t.maxDelay = d
	}
}

// WithThrottlerThreshold sets the frequency threshold (redraws/second) to start throttling.
func WithThrottlerThreshold(freq float64) FullRedrawThrottlerOption {
	return func(t *FullRedrawThrottler) {
		t.thresholdFreq = freq
	}
}

// WithThrottlerBandwidthThresholds sets the bandwidth thresholds for window adjustment.
// lowThreshold: below this (bytes/s), use minimum window
// highThreshold: above this (bytes/s), use maximum window
func WithThrottlerBandwidthThresholds(lowThreshold, highThreshold int) FullRedrawThrottlerOption {
	return func(t *FullRedrawThrottler) {
		t.lowBandwidthThreshold = lowThreshold
		t.highBandwidthThreshold = highThreshold
	}
}
