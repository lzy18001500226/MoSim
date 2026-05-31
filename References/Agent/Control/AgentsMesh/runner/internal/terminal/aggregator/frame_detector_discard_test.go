package aggregator

import (
	"bytes"
	"testing"
)

func TestFrameDetector_DiscardOldFrames_MultipleCompleteFrames(t *testing.T) {
	fd := NewFrameDetector()

	// Content-aware discard: only discards when there's a full redraw frame
	// Small incremental frames are preserved
	frame1 := buildSyncFrame("old frame 1")
	frame2 := buildSyncFrame("old frame 2")
	frame3 := buildFullRedrawFrame("latest frame") // Full redraw frame triggers discard
	data := append(append(frame1, frame2...), frame3...)

	buffer := bytes.NewBuffer(data)
	discarded := fd.DiscardOldFrames(buffer)

	// Should discard first two frames because frame3 is a full redraw
	expectedDiscarded := len(frame1) + len(frame2)
	if discarded != expectedDiscarded {
		t.Errorf("Expected to discard %d bytes, discarded %d", expectedDiscarded, discarded)
	}

	// Buffer should contain only frame3
	if !bytes.Equal(buffer.Bytes(), frame3) {
		t.Errorf("Buffer should contain only latest frame, got %q", buffer.String())
	}
}

func TestFrameDetector_DiscardOldFrames_PreservesIncrementalFrames(t *testing.T) {
	fd := NewFrameDetector()

	// All incremental frames (no clear screen) - should ALL be preserved
	frame1 := buildSyncFrame("incremental 1")
	frame2 := buildSyncFrame("incremental 2")
	frame3 := buildSyncFrame("incremental 3")
	data := append(append(frame1, frame2...), frame3...)

	buffer := bytes.NewBuffer(data)
	discarded := fd.DiscardOldFrames(buffer)

	// Should NOT discard anything - all incremental frames preserved
	if discarded != 0 {
		t.Errorf("Should not discard incremental frames, discarded %d bytes", discarded)
	}

	// Buffer should contain all frames
	if !bytes.Equal(buffer.Bytes(), data) {
		t.Errorf("All incremental frames should be preserved")
	}
}

func TestFrameDetector_DiscardOldFrames_KeepsIncompleteFrame(t *testing.T) {
	fd := NewFrameDetector()

	// Use full redraw frame to trigger discard of older frames
	frame1 := buildSyncFrame("complete 1")
	frame2 := buildFullRedrawFrame("complete 2") // Full redraw triggers discard of frame1
	incomplete := append(syncOutputStartSeq, []byte("incomplete content")...)
	data := append(append(frame1, frame2...), incomplete...)

	buffer := bytes.NewBuffer(data)
	discarded := fd.DiscardOldFrames(buffer)

	// Should discard frame1 because frame2 is a full redraw
	expectedDiscarded := len(frame1)
	if discarded != expectedDiscarded {
		t.Errorf("Expected to discard %d bytes, discarded %d", expectedDiscarded, discarded)
	}

	// Buffer should contain frame2 + incomplete
	expected := append(frame2, incomplete...)
	if !bytes.Equal(buffer.Bytes(), expected) {
		t.Errorf("Buffer should contain last complete + incomplete frame\nExpected: %q\nGot: %q",
			expected, buffer.Bytes())
	}
}

func TestFrameDetector_DiscardOldFrames_OnlyIncomplete(t *testing.T) {
	fd := NewFrameDetector()

	incomplete := append(syncOutputStartSeq, []byte("only incomplete")...)
	buffer := bytes.NewBuffer(incomplete)

	discarded := fd.DiscardOldFrames(buffer)

	// Should not discard anything - incomplete frame is preserved
	if discarded != 0 {
		t.Errorf("Should not discard incomplete frame, discarded %d bytes", discarded)
	}
	if !bytes.Equal(buffer.Bytes(), incomplete) {
		t.Error("Incomplete frame should be preserved")
	}
}

func TestFrameDetector_DiscardOldFrames_ClearScreenFallback(t *testing.T) {
	fd := NewFrameDetector()

	data := append([]byte("old content"), clearScreenSeq...)
	data = append(data, []byte("new content")...)

	buffer := bytes.NewBuffer(data)
	discarded := fd.DiscardOldFrames(buffer)

	// Should discard content before clear screen
	expectedDiscarded := len("old content")
	if discarded != expectedDiscarded {
		t.Errorf("Expected to discard %d bytes, discarded %d", expectedDiscarded, discarded)
	}

	expected := append(clearScreenSeq, []byte("new content")...)
	if !bytes.Equal(buffer.Bytes(), expected) {
		t.Errorf("Expected %q, got %q", expected, buffer.Bytes())
	}
}

func TestFrameDetector_DiscardOldFrames_EmptyBuffer(t *testing.T) {
	fd := NewFrameDetector()
	buffer := &bytes.Buffer{}

	discarded := fd.DiscardOldFrames(buffer)

	if discarded != 0 {
		t.Errorf("Should not discard from empty buffer, discarded %d", discarded)
	}
}

func TestFrameDetector_DiscardOldFrames_PlainText(t *testing.T) {
	fd := NewFrameDetector()
	data := []byte("plain text without any frame markers")

	buffer := bytes.NewBuffer(data)
	discarded := fd.DiscardOldFrames(buffer)

	// Should not discard anything - no frame markers
	if discarded != 0 {
		t.Errorf("Should not discard plain text, discarded %d bytes", discarded)
	}
}

func TestFrameDetector_DiscardWithSyncFrames_OnlyComplete(t *testing.T) {
	fd := NewFrameDetector()

	// Single complete frame - should not discard
	frame := buildSyncFrame("content")
	buffer := bytes.NewBuffer(frame)
	discarded := fd.DiscardOldFrames(buffer)

	if discarded != 0 {
		t.Errorf("Should not discard single complete frame, discarded %d", discarded)
	}
}

func TestFrameDetector_DiscardOldFrames_SingleFrame(t *testing.T) {
	fd := NewFrameDetector()

	// Single complete frame at position 0
	frame := buildSyncFrame("single")
	buffer := bytes.NewBuffer(frame)
	discarded := fd.DiscardOldFrames(buffer)

	// Should not discard - it's the only frame
	if discarded != 0 {
		t.Errorf("Should not discard only frame, discarded %d", discarded)
	}
	if !bytes.Equal(buffer.Bytes(), frame) {
		t.Error("Frame should be unchanged")
	}
}

func TestFrameDetector_DiscardOldFrames_NoStartPositions(t *testing.T) {
	fd := NewFrameDetector()

	// Only clear screen, no sync frames
	data := append(clearScreenSeq, []byte("content")...)
	buffer := bytes.NewBuffer(data)

	// Should use clear screen fallback but position is 0, so nothing to discard
	discarded := fd.DiscardOldFrames(buffer)
	if discarded != 0 {
		t.Errorf("Should not discard when clear screen is at position 0, discarded %d", discarded)
	}
}
