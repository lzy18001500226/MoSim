// Package terminal provides terminal management for PTY sessions.
package aggregator

import "time"

// cleanExpiredLocked removes entries outside the effective sliding window.
// Must be called with lock held.
func (t *FullRedrawThrottler) cleanExpiredLocked(now time.Time) {
	// Use max window for cleanup to preserve data for bandwidth calculation
	// The effective window is used for frequency calculation
	cutoff := now.Add(-t.maxWindowSize)

	// Find first valid entry
	validStart := 0
	for i, rec := range t.redrawRecords {
		if rec.time.After(cutoff) {
			validStart = i
			break
		}
		validStart = i + 1
	}

	if validStart > 0 {
		// Shift valid entries to front
		copy(t.redrawRecords, t.redrawRecords[validStart:])
		t.redrawRecords = t.redrawRecords[:len(t.redrawRecords)-validStart]
	}
}

// adjustWindowLocked adjusts the effective window size based on current bandwidth.
// Higher bandwidth -> larger window -> more aggressive throttling.
// Must be called with lock held.
func (t *FullRedrawThrottler) adjustWindowLocked() {
	bandwidth := t.getBandwidthLocked()

	if bandwidth <= t.lowBandwidthThreshold {
		// Low bandwidth - use minimum window for quick response
		t.effectiveWindowSize = t.minWindowSize
	} else if bandwidth >= t.highBandwidthThreshold {
		// High bandwidth - use maximum window for aggressive throttling
		t.effectiveWindowSize = t.maxWindowSize
	} else {
		// Linear interpolation between min and max
		ratio := float64(bandwidth-t.lowBandwidthThreshold) /
			float64(t.highBandwidthThreshold-t.lowBandwidthThreshold)
		windowRange := t.maxWindowSize - t.minWindowSize
		t.effectiveWindowSize = t.minWindowSize + time.Duration(float64(windowRange)*ratio)
	}
}

// getFrequencyLocked calculates the current frequency (redraws/second).
// Only counts records within the effective window.
// Must be called with lock held.
func (t *FullRedrawThrottler) getFrequencyLocked() float64 {
	if len(t.redrawRecords) == 0 {
		return 0
	}

	// Count records within effective window
	now := time.Now()
	cutoff := now.Add(-t.effectiveWindowSize)
	count := 0
	for _, rec := range t.redrawRecords {
		if rec.time.After(cutoff) {
			count++
		}
	}

	if count == 0 {
		return 0
	}
	return float64(count) / t.effectiveWindowSize.Seconds()
}

// getBandwidthLocked calculates the current bandwidth (bytes/second).
// Uses the base window size for consistent bandwidth measurement.
// Must be called with lock held.
func (t *FullRedrawThrottler) getBandwidthLocked() int {
	if len(t.redrawRecords) == 0 {
		return 0
	}

	// Sum bytes within base window for bandwidth calculation
	now := time.Now()
	cutoff := now.Add(-t.baseWindowSize)
	totalBytes := 0
	for _, rec := range t.redrawRecords {
		if rec.time.After(cutoff) {
			totalBytes += rec.bytes
		}
	}

	return int(float64(totalBytes) / t.baseWindowSize.Seconds())
}

// calculateDelayLocked calculates the adaptive throttle delay.
// Uses both frequency and bandwidth to determine throttling intensity.
// Must be called with lock held.
//
// Delay calculation:
// - Below threshold: 0 (no delay)
// - At threshold: minDelay (200ms default)
// - Linear increase based on frequency and bandwidth
func (t *FullRedrawThrottler) calculateDelayLocked() time.Duration {
	frequency := t.getFrequencyLocked()
	bandwidth := t.getBandwidthLocked()

	// Check frequency threshold
	if frequency < t.thresholdFreq {
		// Also check bandwidth - high bandwidth alone can trigger throttling
		// If bandwidth > high threshold but frequency is low, still throttle
		if bandwidth < t.highBandwidthThreshold {
			return 0 // Below both thresholds, no throttling
		}
	}

	// Calculate frequency-based delay component
	maxFreq := 10.0
	freqRatio := (frequency - t.thresholdFreq) / (maxFreq - t.thresholdFreq)
	if freqRatio < 0 {
		freqRatio = 0
	}
	if freqRatio > 1 {
		freqRatio = 1
	}

	// Calculate bandwidth-based delay component
	bandwidthRatio := float64(bandwidth-t.lowBandwidthThreshold) /
		float64(t.highBandwidthThreshold-t.lowBandwidthThreshold)
	if bandwidthRatio < 0 {
		bandwidthRatio = 0
	}
	if bandwidthRatio > 1 {
		bandwidthRatio = 1
	}

	// Use the higher of the two ratios (more aggressive throttling)
	ratio := freqRatio
	if bandwidthRatio > ratio {
		ratio = bandwidthRatio
	}

	if ratio == 0 {
		return 0
	}

	delay := t.minDelay + time.Duration(float64(t.maxDelay-t.minDelay)*ratio)
	return delay
}
