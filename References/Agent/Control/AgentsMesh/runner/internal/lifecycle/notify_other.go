//go:build !linux

package lifecycle

// notifySystemHealthy is a no-op on non-Linux platforms.
// On Linux, this sends WATCHDOG=1 to systemd via sd_notify.
func notifySystemHealthy() {
	// No-op: systemd watchdog is Linux-only
}
