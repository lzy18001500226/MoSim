package aggregator

import (
	"bytes"
	"testing"
)

// TestFrameBuffer_EnforceLimit_FramesHelp tests that discarding frames helps with limit
func TestFrameBuffer_EnforceLimit_FramesHelp(t *testing.T) {
	maxSize := 100
	fb := NewFrameBuffer(maxSize)

	// Write old frame
	oldFrame := buildSyncFrame(string(bytes.Repeat([]byte("o"), 30)))
	fb.Write(oldFrame)

	// Write new full redraw frame that would exceed limit - discarding old frame allows it
	// NOTE: Use buildFullRedrawFrame to trigger content-aware discard
	newFrame := buildFullRedrawFrame(string(bytes.Repeat([]byte("n"), 30)))
	fb.Write(newFrame)

	// Should have discarded old frame because newFrame is a full redraw
	if bytes.Contains(fb.Bytes(), []byte("ooo")) {
		t.Error("Old frame should be discarded")
	}
	if !bytes.Contains(fb.Bytes(), []byte("nnn")) {
		t.Error("New frame should be kept")
	}
}

// TestFrameBuffer_EnforceLimitAfterWrite_RespectsFrameBoundary tests that
// truncation respects frame boundaries to avoid orphan frame ends
func TestFrameBuffer_EnforceLimitAfterWrite_RespectsFrameBoundary(t *testing.T) {
	maxSize := 100
	fb := NewFrameBuffer(maxSize)

	// Build a scenario where we have:
	// [small complete frame] + [large frame that exceeds maxSize]
	// The truncation should preserve frame integrity
	smallFrame := buildSyncFrame("small")                      // ~30 bytes
	largeContent := string(bytes.Repeat([]byte("X"), maxSize)) // 100 bytes
	largeFrame := buildSyncFrame(largeContent)                 // ~116 bytes

	fb.Write(smallFrame)
	fb.Write(largeFrame)

	// After truncation, we should have valid frame pairing
	data := fb.Bytes()
	starts := bytes.Count(data, syncOutputStartSeq)
	ends := bytes.Count(data, syncOutputEndSeq)

	// Key assertion: frame starts and ends should be balanced
	// (or starts >= ends if there's an incomplete frame at end)
	if ends > starts {
		t.Errorf("Frame integrity violated: %d starts, %d ends (orphan ends!)", starts, ends)
	}

	t.Logf("Buffer state: %d bytes, %d starts, %d ends", len(data), starts, ends)
}

// TestFrameBuffer_EnforceLimitAfterWrite_LargeFrameExceedsLimit tests
// the scenario where a single frame is larger than maxSize
func TestFrameBuffer_EnforceLimitAfterWrite_LargeFrameExceedsLimit(t *testing.T) {
	maxSize := 50
	fb := NewFrameBuffer(maxSize)

	// A single frame larger than maxSize
	largeContent := string(bytes.Repeat([]byte("X"), 100))
	largeFrame := buildSyncFrame(largeContent) // ~116 bytes

	fb.Write(largeFrame)

	// Buffer should be capped at maxSize
	if fb.Len() > maxSize {
		t.Errorf("Buffer exceeded maxSize: %d > %d", fb.Len(), maxSize)
	}

	// In this case, truncation is unavoidable, but we log a warning
	t.Logf("Large frame test: frame size %d, buffer size %d", len(largeFrame), fb.Len())
}

// TestFrameBuffer_EnforceLimitAfterWrite_MultipleFrames tests truncation
// with multiple frames, ensuring we truncate at frame boundary
func TestFrameBuffer_EnforceLimitAfterWrite_MultipleFrames(t *testing.T) {
	maxSize := 150
	fb := NewFrameBuffer(maxSize)

	// Write multiple frames that together exceed maxSize
	// Use full redraw frame at the end to trigger discarding of older frames
	frame1 := buildSyncFrame("frame1content")                             // ~30 bytes - incremental
	frame2 := buildSyncFrame("frame2content")                             // ~30 bytes - incremental
	frame3 := buildSyncFrame("frame3content")                             // ~30 bytes - incremental
	frame4 := buildFullRedrawFrame(string(bytes.Repeat([]byte("4"), 50))) // ~70 bytes - full redraw

	fb.Write(frame1)
	fb.Write(frame2)
	fb.Write(frame3)
	fb.Write(frame4) // This full redraw triggers discard of frame1, frame2, frame3

	data := fb.Bytes()
	starts := bytes.Count(data, syncOutputStartSeq)
	ends := bytes.Count(data, syncOutputEndSeq)

	// Frame integrity check
	if ends > starts {
		t.Errorf("Frame integrity violated: %d starts, %d ends", starts, ends)
	}

	// Should have discarded old frames because frame4 is a full redraw
	if bytes.Contains(data, []byte("frame1content")) {
		t.Error("Old frame1 should have been discarded")
	}

	// Should keep the full redraw frame content
	if !bytes.Contains(data, []byte("4444")) {
		t.Error("Newest frame4 content should be kept")
	}

	t.Logf("Multiple frames test: %d bytes, %d starts, %d ends", len(data), starts, ends)
}
