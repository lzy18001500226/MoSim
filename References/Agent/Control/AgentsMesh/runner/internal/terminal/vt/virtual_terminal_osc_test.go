package vt

import (
	"sync"
	"testing"
	"time"
)

// ==================== OSC Handler Tests ====================

func TestOSC777NotifyHandler(t *testing.T) {
	vt := NewVirtualTerminal(80, 24, 1000)

	var wg sync.WaitGroup
	wg.Add(1)

	var gotOSCType int
	var gotParams []string

	vt.SetOSCHandler(func(oscType int, params []string) {
		gotOSCType = oscType
		gotParams = params
		wg.Done()
	})

	// OSC 777;notify;Title;Body BEL
	vt.Feed([]byte("\x1b]777;notify;Build Complete;Success!\x07"))

	// Wait for goroutine with timeout
	done := make(chan struct{})
	go func() {
		wg.Wait()
		close(done)
	}()

	select {
	case <-done:
		// Handler was called
	case <-time.After(100 * time.Millisecond):
		t.Fatal("OSC handler was not called within timeout")
	}

	if gotOSCType != 777 {
		t.Errorf("expected OSC type 777, got %d", gotOSCType)
	}
	if len(gotParams) != 3 {
		t.Errorf("expected 3 params, got %d: %v", len(gotParams), gotParams)
	}
	if len(gotParams) >= 3 {
		if gotParams[0] != "notify" {
			t.Errorf("expected params[0]='notify', got '%s'", gotParams[0])
		}
		if gotParams[1] != "Build Complete" {
			t.Errorf("expected params[1]='Build Complete', got '%s'", gotParams[1])
		}
		if gotParams[2] != "Success!" {
			t.Errorf("expected params[2]='Success!', got '%s'", gotParams[2])
		}
	}
}

func TestOSC9NotificationHandler(t *testing.T) {
	vt := NewVirtualTerminal(80, 24, 1000)

	var wg sync.WaitGroup
	wg.Add(1)

	var gotOSCType int
	var gotParams []string

	vt.SetOSCHandler(func(oscType int, params []string) {
		gotOSCType = oscType
		gotParams = params
		wg.Done()
	})

	// OSC 9;message BEL (ConEmu/Windows Terminal format)
	vt.Feed([]byte("\x1b]9;Task completed\x07"))

	done := make(chan struct{})
	go func() {
		wg.Wait()
		close(done)
	}()

	select {
	case <-done:
	case <-time.After(100 * time.Millisecond):
		t.Fatal("OSC handler was not called within timeout")
	}

	if gotOSCType != 9 {
		t.Errorf("expected OSC type 9, got %d", gotOSCType)
	}
	if len(gotParams) != 1 {
		t.Errorf("expected 1 param, got %d: %v", len(gotParams), gotParams)
	}
	if len(gotParams) >= 1 && gotParams[0] != "Task completed" {
		t.Errorf("expected params[0]='Task completed', got '%s'", gotParams[0])
	}
}

func TestOSC0TitleHandler(t *testing.T) {
	vt := NewVirtualTerminal(80, 24, 1000)

	var wg sync.WaitGroup
	wg.Add(1)

	var gotOSCType int
	var gotParams []string

	vt.SetOSCHandler(func(oscType int, params []string) {
		gotOSCType = oscType
		gotParams = params
		wg.Done()
	})

	// OSC 0;title BEL (window title)
	vt.Feed([]byte("\x1b]0;My Terminal Title\x07"))

	done := make(chan struct{})
	go func() {
		wg.Wait()
		close(done)
	}()

	select {
	case <-done:
	case <-time.After(100 * time.Millisecond):
		t.Fatal("OSC handler was not called within timeout")
	}

	if gotOSCType != 0 {
		t.Errorf("expected OSC type 0, got %d", gotOSCType)
	}
	if len(gotParams) != 1 {
		t.Errorf("expected 1 param, got %d: %v", len(gotParams), gotParams)
	}
	if len(gotParams) >= 1 && gotParams[0] != "My Terminal Title" {
		t.Errorf("expected params[0]='My Terminal Title', got '%s'", gotParams[0])
	}
}

func TestOSC2TitleHandler(t *testing.T) {
	vt := NewVirtualTerminal(80, 24, 1000)

	var wg sync.WaitGroup
	wg.Add(1)

	var gotOSCType int
	var gotParams []string

	vt.SetOSCHandler(func(oscType int, params []string) {
		gotOSCType = oscType
		gotParams = params
		wg.Done()
	})

	// OSC 2;title BEL (window title only)
	vt.Feed([]byte("\x1b]2;Another Title\x07"))

	done := make(chan struct{})
	go func() {
		wg.Wait()
		close(done)
	}()

	select {
	case <-done:
	case <-time.After(100 * time.Millisecond):
		t.Fatal("OSC handler was not called within timeout")
	}

	if gotOSCType != 2 {
		t.Errorf("expected OSC type 2, got %d", gotOSCType)
	}
	if len(gotParams) != 1 {
		t.Errorf("expected 1 param, got %d: %v", len(gotParams), gotParams)
	}
	if len(gotParams) >= 1 && gotParams[0] != "Another Title" {
		t.Errorf("expected params[0]='Another Title', got '%s'", gotParams[0])
	}
}

func TestOSCHandlerNilSafe(t *testing.T) {
	vt := NewVirtualTerminal(80, 24, 1000)

	// No handler set - should not panic
	vt.Feed([]byte("\x1b]777;notify;Title;Body\x07"))

	// If we get here without panic, test passes
	display := vt.GetDisplay()
	if display != "" {
		t.Errorf("expected empty display (OSC should not be visible), got '%s'", display)
	}
}

func TestOSCWithSTTerminator(t *testing.T) {
	vt := NewVirtualTerminal(80, 24, 1000)

	var wg sync.WaitGroup
	wg.Add(1)

	var gotOSCType int

	vt.SetOSCHandler(func(oscType int, params []string) {
		gotOSCType = oscType
		wg.Done()
	})

	// OSC with ST terminator (ESC \) instead of BEL
	vt.Feed([]byte("\x1b]0;Title with ST\x1b\\"))

	done := make(chan struct{})
	go func() {
		wg.Wait()
		close(done)
	}()

	select {
	case <-done:
	case <-time.After(100 * time.Millisecond):
		t.Fatal("OSC handler was not called with ST terminator")
	}

	if gotOSCType != 0 {
		t.Errorf("expected OSC type 0, got %d", gotOSCType)
	}
}

func TestOSCMixedWithNormalOutput(t *testing.T) {
	vt := NewVirtualTerminal(80, 24, 1000)

	var wg sync.WaitGroup
	wg.Add(1)

	var oscCount int

	vt.SetOSCHandler(func(oscType int, params []string) {
		oscCount++
		wg.Done()
	})

	// Mix OSC sequences with normal text
	vt.Feed([]byte("Hello\x1b]9;notification\x07World"))

	done := make(chan struct{})
	go func() {
		wg.Wait()
		close(done)
	}()

	select {
	case <-done:
	case <-time.After(100 * time.Millisecond):
		t.Fatal("OSC handler was not called within timeout")
	}

	if oscCount != 1 {
		t.Errorf("expected 1 OSC call, got %d", oscCount)
	}

	display := vt.GetDisplay()
	if display != "HelloWorld" {
		t.Errorf("expected 'HelloWorld', got '%s'", display)
	}
}
