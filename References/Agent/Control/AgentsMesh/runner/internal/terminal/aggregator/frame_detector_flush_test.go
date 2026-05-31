package aggregator

import (
	"bytes"
	"testing"
)

func TestFrameDetector_FindFlushBoundary_AllComplete(t *testing.T) {
	fd := NewFrameDetector()

	frame1 := buildSyncFrame("frame 1")
	frame2 := buildSyncFrame("frame 2")
	data := append(frame1, frame2...)

	flushEnd, keepFrom := fd.FindFlushBoundary(data)

	// All frames complete - flush everything
	if flushEnd != len(data) {
		t.Errorf("Expected flushEnd=%d, got %d", len(data), flushEnd)
	}
	if keepFrom != len(data) {
		t.Errorf("Expected keepFrom=%d, got %d", len(data), keepFrom)
	}
}

func TestFrameDetector_FindFlushBoundary_WithIncomplete(t *testing.T) {
	fd := NewFrameDetector()

	complete := buildSyncFrame("complete")
	incomplete := append(syncOutputStartSeq, []byte("incomplete")...)
	data := append(complete, incomplete...)

	flushEnd, keepFrom := fd.FindFlushBoundary(data)

	// Should flush up to incomplete frame start
	expectedFlush := len(complete)
	if flushEnd != expectedFlush {
		t.Errorf("Expected flushEnd=%d, got %d", expectedFlush, flushEnd)
	}
	if keepFrom != expectedFlush {
		t.Errorf("Expected keepFrom=%d, got %d", expectedFlush, keepFrom)
	}
}

func TestFrameDetector_FindFlushBoundary_OnlyIncomplete(t *testing.T) {
	fd := NewFrameDetector()

	incomplete := append(syncOutputStartSeq, []byte("incomplete")...)

	flushEnd, keepFrom := fd.FindFlushBoundary(incomplete)

	// Should not flush incomplete frame
	if flushEnd != 0 {
		t.Errorf("Expected flushEnd=0, got %d", flushEnd)
	}
	if keepFrom != 0 {
		t.Errorf("Expected keepFrom=0, got %d", keepFrom)
	}
}

func TestFrameDetector_FindFlushBoundary_NoSyncFrames(t *testing.T) {
	fd := NewFrameDetector()

	data := []byte("plain text")

	flushEnd, keepFrom := fd.FindFlushBoundary(data)

	// No sync frames - flush everything
	if flushEnd != len(data) {
		t.Errorf("Expected flushEnd=%d, got %d", len(data), flushEnd)
	}
	if keepFrom != len(data) {
		t.Errorf("Expected keepFrom=%d, got %d", len(data), keepFrom)
	}
}

func TestFrameDetector_FindFlushBoundary_Empty(t *testing.T) {
	fd := NewFrameDetector()

	flushEnd, keepFrom := fd.FindFlushBoundary(nil)
	if flushEnd != 0 || keepFrom != 0 {
		t.Errorf("Empty data should return 0,0, got %d,%d", flushEnd, keepFrom)
	}

	flushEnd, keepFrom = fd.FindFlushBoundary([]byte{})
	if flushEnd != 0 || keepFrom != 0 {
		t.Errorf("Empty slice should return 0,0, got %d,%d", flushEnd, keepFrom)
	}
}

// TestFrameDetector_RealWorldScenario simulates real Claude Code output patterns
func TestFrameDetector_RealWorldScenario(t *testing.T) {
	fd := NewFrameDetector()

	// Simulate: small incremental frames (animation/spinner) followed by a full redraw
	// In real Claude Code:
	// - Incremental frames: small updates like spinner animation, typing effects
	// - Full redraw frames: when UI layout changes (contains ESC[2J or is large)
	frame1 := buildSyncFrame("Tool: Search\nSearching...")          // Incremental
	frame2 := buildSyncFrame("Tool: Search\nSearching..")           // Incremental
	frame3 := buildFullRedrawFrame("Tool: Search\nFound 5 files\n") // Full redraw
	incomplete := append(syncOutputStartSeq, []byte("Tool: Read\nfile1.go contents:\npackage main")...)

	data := append(append(append(frame1, frame2...), frame3...), incomplete...)

	// DiscardOldFrames should discard frame1 and frame2 (before the full redraw frame3)
	buffer := bytes.NewBuffer(data)
	discarded := fd.DiscardOldFrames(buffer)

	expectedDiscarded := len(frame1) + len(frame2)
	if discarded != expectedDiscarded {
		t.Errorf("Expected to discard %d bytes, discarded %d", expectedDiscarded, discarded)
	}

	// FindFlushBoundary should only flush frame3, keep incomplete
	remaining := buffer.Bytes()
	flushEnd, _ := fd.FindFlushBoundary(remaining)

	expectedFlushEnd := len(frame3)
	if flushEnd != expectedFlushEnd {
		t.Errorf("Expected flushEnd=%d, got %d", expectedFlushEnd, flushEnd)
	}
}

// TestFrameDetector_RealWorldScenario_AllIncremental tests that all incremental frames are preserved
func TestFrameDetector_RealWorldScenario_AllIncremental(t *testing.T) {
	fd := NewFrameDetector()

	// All incremental frames - common during animations
	frame1 := buildSyncFrame("Spinner: /")
	frame2 := buildSyncFrame("Spinner: -")
	frame3 := buildSyncFrame("Spinner: \\")
	frame4 := buildSyncFrame("Spinner: |")

	data := append(append(append(frame1, frame2...), frame3...), frame4...)

	// All incremental frames should be preserved
	buffer := bytes.NewBuffer(data)
	discarded := fd.DiscardOldFrames(buffer)

	if discarded != 0 {
		t.Errorf("Should not discard incremental frames, discarded %d bytes", discarded)
	}

	// FindFlushBoundary should flush all frames (all complete)
	flushEnd, _ := fd.FindFlushBoundary(buffer.Bytes())
	if flushEnd != len(data) {
		t.Errorf("Expected to flush all data, flushEnd=%d, data len=%d", flushEnd, len(data))
	}
}

// TestFrameDetector_FrameCountPreservation tests that frame pairs are preserved correctly
func TestFrameDetector_FrameCountPreservation(t *testing.T) {
	fd := NewFrameDetector()

	// Build data: 9 incremental frames + 1 full redraw frame at the end
	// Only the last full redraw should trigger discarding of previous frames
	var data []byte
	incrementalCount := 9
	for i := 0; i < incrementalCount; i++ {
		data = append(data, buildSyncFrame("incremental frame")...)
	}
	// Add a full redraw frame at the end
	fullRedrawFrame := buildFullRedrawFrame("full redraw content")
	data = append(data, fullRedrawFrame...)

	// Count starts and ends in original data
	originalStarts := len(findAllPositions(data, syncOutputStartSeq))
	originalEnds := len(findAllPositions(data, syncOutputEndSeq))
	totalFrames := incrementalCount + 1

	if originalStarts != totalFrames || originalEnds != totalFrames {
		t.Fatalf("Original data should have %d starts and ends, got %d/%d",
			totalFrames, originalStarts, originalEnds)
	}

	// After DiscardOldFrames, should keep only the last full redraw frame
	buffer := bytes.NewBuffer(data)
	fd.DiscardOldFrames(buffer)

	remaining := buffer.Bytes()
	remainingStarts := len(findAllPositions(remaining, syncOutputStartSeq))
	remainingEnds := len(findAllPositions(remaining, syncOutputEndSeq))

	// Should have 1 complete frame (the full redraw frame)
	if remainingStarts != 1 {
		t.Errorf("Expected 1 start sequence remaining, got %d", remainingStarts)
	}
	if remainingEnds != 1 {
		t.Errorf("Expected 1 end sequence remaining, got %d", remainingEnds)
	}

	// Starts and ends should match
	if remainingStarts != remainingEnds {
		t.Errorf("Frame starts (%d) and ends (%d) should match", remainingStarts, remainingEnds)
	}
}

// TestFrameDetector_AllIncrementalFramesPreserved tests that all incremental frames are kept
func TestFrameDetector_AllIncrementalFramesPreserved(t *testing.T) {
	fd := NewFrameDetector()

	// Build data with only incremental frames - all should be preserved
	var data []byte
	frameCount := 10
	for i := 0; i < frameCount; i++ {
		data = append(data, buildSyncFrame("incremental frame")...)
	}

	buffer := bytes.NewBuffer(data)
	discarded := fd.DiscardOldFrames(buffer)

	// No frames should be discarded
	if discarded != 0 {
		t.Errorf("Should not discard incremental frames, discarded %d bytes", discarded)
	}

	remaining := buffer.Bytes()
	remainingStarts := len(findAllPositions(remaining, syncOutputStartSeq))
	remainingEnds := len(findAllPositions(remaining, syncOutputEndSeq))

	// All frames should be preserved
	if remainingStarts != frameCount {
		t.Errorf("Expected %d start sequences, got %d", frameCount, remainingStarts)
	}
	if remainingEnds != frameCount {
		t.Errorf("Expected %d end sequences, got %d", frameCount, remainingEnds)
	}
}
