package aggregator

import (
	"bytes"
	"testing"
)

// ============================================================================
// StripRedundantSequencesInFrames Tests
// ============================================================================

// TestFrameDetector_StripRedundantSequences_NoSyncFrames tests that non-sync data is unchanged
func TestFrameDetector_StripRedundantSequences_NoSyncFrames(t *testing.T) {
	fd := NewFrameDetector()

	// Plain text with clear screen - should NOT be stripped (outside sync frame)
	data := append([]byte("before"), eraseScreenSeq...)
	data = append(data, cursorHomeSeq...)
	data = append(data, []byte("after")...)

	result := fd.StripRedundantSequencesInFrames(data)

	// Should be unchanged - no sync frames present
	if !bytes.Equal(result, data) {
		t.Errorf("Should not modify data without sync frames\nOriginal: %q\nResult: %q", data, result)
	}
}

// TestFrameDetector_StripRedundantSequences_InSyncFrame tests stripping inside sync frame
func TestFrameDetector_StripRedundantSequences_InSyncFrame(t *testing.T) {
	fd := NewFrameDetector()

	// Sync frame containing ESC[2J and ESC[H
	frameContent := append(eraseScreenSeq, cursorHomeSeq...)
	frameContent = append(frameContent, []byte("real content")...)
	frame := buildSyncFrame(string(frameContent))

	result := fd.StripRedundantSequencesInFrames(frame)

	// ESC[2J and ESC[H should be stripped from inside frame
	if bytes.Contains(result, eraseScreenSeq) {
		t.Error("ESC[2J should be stripped from sync frame")
	}
	if bytes.Contains(result, cursorHomeSeq) {
		t.Error("ESC[H should be stripped from sync frame")
	}

	// Frame boundaries should be preserved
	if !bytes.Contains(result, syncOutputStartSeq) {
		t.Error("Sync frame start should be preserved")
	}
	if !bytes.Contains(result, syncOutputEndSeq) {
		t.Error("Sync frame end should be preserved")
	}

	// Real content should be preserved
	if !bytes.Contains(result, []byte("real content")) {
		t.Error("Real content should be preserved")
	}
}

// TestFrameDetector_StripRedundantSequences_MultipleFrames tests multiple frames
func TestFrameDetector_StripRedundantSequences_MultipleFrames(t *testing.T) {
	fd := NewFrameDetector()

	// Frame 1: with clear screen
	frame1Content := append(eraseScreenSeq, []byte("frame1")...)
	frame1 := buildSyncFrame(string(frame1Content))

	// Frame 2: with cursor home
	frame2Content := append(cursorHomeSeq, []byte("frame2")...)
	frame2 := buildSyncFrame(string(frame2Content))

	data := append(frame1, frame2...)
	result := fd.StripRedundantSequencesInFrames(data)

	// Both sequences should be stripped
	if bytes.Contains(result, eraseScreenSeq) {
		t.Error("ESC[2J should be stripped")
	}
	if bytes.Contains(result, cursorHomeSeq) {
		t.Error("ESC[H should be stripped")
	}

	// Content should be preserved
	if !bytes.Contains(result, []byte("frame1")) || !bytes.Contains(result, []byte("frame2")) {
		t.Error("Frame contents should be preserved")
	}

	// Should have 2 complete frames
	starts := bytes.Count(result, syncOutputStartSeq)
	ends := bytes.Count(result, syncOutputEndSeq)
	if starts != 2 || ends != 2 {
		t.Errorf("Expected 2 starts and 2 ends, got %d/%d", starts, ends)
	}
}

// TestFrameDetector_StripRedundantSequences_MixedContext tests sync and non-sync mixed
func TestFrameDetector_StripRedundantSequences_MixedContext(t *testing.T) {
	fd := NewFrameDetector()

	// Clear screen outside frame (should be kept)
	before := append(eraseScreenSeq, []byte("before frame")...)

	// Frame with clear screen (should be stripped)
	frameContent := append(eraseScreenSeq, []byte("inside frame")...)
	frame := buildSyncFrame(string(frameContent))

	// Clear screen outside frame (should be kept)
	after := append(eraseScreenSeq, []byte("after frame")...)

	data := append(append(before, frame...), after...)
	result := fd.StripRedundantSequencesInFrames(data)

	// Count ESC[2J - should be 2 (before and after, not inside)
	count := bytes.Count(result, eraseScreenSeq)
	if count != 2 {
		t.Errorf("Expected 2 ESC[2J sequences (outside frames), got %d", count)
	}

	// Verify content
	if !bytes.Contains(result, []byte("before frame")) {
		t.Error("Before frame content should be preserved")
	}
	if !bytes.Contains(result, []byte("inside frame")) {
		t.Error("Inside frame content should be preserved")
	}
	if !bytes.Contains(result, []byte("after frame")) {
		t.Error("After frame content should be preserved")
	}
}

// TestFrameDetector_StripRedundantSequences_IncompleteFrame tests incomplete frame handling
func TestFrameDetector_StripRedundantSequences_IncompleteFrame(t *testing.T) {
	fd := NewFrameDetector()

	// Incomplete frame (no end sequence)
	incomplete := append(syncOutputStartSeq, eraseScreenSeq...)
	incomplete = append(incomplete, []byte("incomplete content")...)

	result := fd.StripRedundantSequencesInFrames(incomplete)

	// ESC[2J should be stripped even in incomplete frame
	if bytes.Contains(result, eraseScreenSeq) {
		t.Error("ESC[2J should be stripped from incomplete frame")
	}

	// Content should be preserved
	if !bytes.Contains(result, []byte("incomplete content")) {
		t.Error("Content should be preserved")
	}
}

// TestFrameDetector_StripRedundantSequences_CursorHomeVariant tests ESC[;H variant
func TestFrameDetector_StripRedundantSequences_CursorHomeVariant(t *testing.T) {
	fd := NewFrameDetector()

	// Frame with ESC[;H variant
	frameContent := append(cursorHomeSeq2, []byte("content")...)
	frame := buildSyncFrame(string(frameContent))

	result := fd.StripRedundantSequencesInFrames(frame)

	// ESC[;H should be stripped
	if bytes.Contains(result, cursorHomeSeq2) {
		t.Error("ESC[;H should be stripped from sync frame")
	}
}

// TestFrameDetector_StripRedundantSequences_Empty tests empty data
func TestFrameDetector_StripRedundantSequences_Empty(t *testing.T) {
	fd := NewFrameDetector()

	result := fd.StripRedundantSequencesInFrames(nil)
	if result != nil {
		t.Error("nil input should return nil")
	}

	result = fd.StripRedundantSequencesInFrames([]byte{})
	if len(result) != 0 {
		t.Error("empty input should return empty")
	}
}

// TestFrameDetector_StripRedundantSequences_NoRedundantSeqs tests frame without redundant seqs
func TestFrameDetector_StripRedundantSequences_NoRedundantSeqs(t *testing.T) {
	fd := NewFrameDetector()

	// Frame without any clear screen or cursor home
	frame := buildSyncFrame("just normal content")
	original := make([]byte, len(frame))
	copy(original, frame)

	result := fd.StripRedundantSequencesInFrames(frame)

	// Should return the same data (no modification needed)
	if !bytes.Equal(result, original) {
		t.Error("Frame without redundant sequences should be unchanged")
	}
}

// TestFrameDetector_StripRedundantSequences_RealWorldResize simulates post-resize behavior
func TestFrameDetector_StripRedundantSequences_RealWorldResize(t *testing.T) {
	fd := NewFrameDetector()

	// Simulate Claude Code post-resize: every frame starts with ESC[2J ESC[H
	var data []byte
	for i := 0; i < 5; i++ {
		frameContent := append(eraseScreenSeq, cursorHomeSeq...)
		frameContent = append(frameContent, []byte("frame content with lots of text...")...)
		frame := buildSyncFrame(string(frameContent))
		data = append(data, frame...)
	}

	originalLen := len(data)
	result := fd.StripRedundantSequencesInFrames(data)

	// Should be significantly smaller (stripped 5 x (4 + 3) = 35 bytes)
	expectedStripped := 5 * (len(eraseScreenSeq) + len(cursorHomeSeq))
	actualStripped := originalLen - len(result)

	if actualStripped != expectedStripped {
		t.Errorf("Expected to strip %d bytes, stripped %d", expectedStripped, actualStripped)
	}

	// Should have no ESC[2J or ESC[H
	if bytes.Contains(result, eraseScreenSeq) || bytes.Contains(result, cursorHomeSeq) {
		t.Error("All redundant sequences should be stripped")
	}

	// Should have 5 complete frames
	if bytes.Count(result, syncOutputStartSeq) != 5 || bytes.Count(result, syncOutputEndSeq) != 5 {
		t.Error("All 5 frames should be preserved")
	}
}
