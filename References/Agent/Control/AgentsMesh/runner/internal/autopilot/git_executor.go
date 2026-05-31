package autopilot

import (
	"os/exec"
)

// GitExecutor defines the interface for executing git commands.
// This abstraction allows for easy testing and potential future extensions
// (e.g., using go-git instead of exec).
type GitExecutor interface {
	// Status runs "git status --porcelain" and returns the output.
	Status(workDir string) ([]byte, error)

	// DiffStat runs "git diff --stat" and returns the output.
	DiffStat(workDir string) ([]byte, error)

	// DiffCachedStat runs "git diff --cached --stat" and returns the output.
	DiffCachedStat(workDir string) ([]byte, error)
}

// DefaultGitExecutor implements GitExecutor using exec.Command.
type DefaultGitExecutor struct{}

// NewDefaultGitExecutor creates a new DefaultGitExecutor.
func NewDefaultGitExecutor() *DefaultGitExecutor {
	return &DefaultGitExecutor{}
}

func (e *DefaultGitExecutor) Status(workDir string) ([]byte, error) {
	cmd := exec.Command("git", "status", "--porcelain")
	cmd.Dir = workDir
	return cmd.Output()
}

func (e *DefaultGitExecutor) DiffStat(workDir string) ([]byte, error) {
	cmd := exec.Command("git", "diff", "--stat")
	cmd.Dir = workDir
	return cmd.Output()
}

func (e *DefaultGitExecutor) DiffCachedStat(workDir string) ([]byte, error) {
	cmd := exec.Command("git", "diff", "--cached", "--stat")
	cmd.Dir = workDir
	return cmd.Output()
}

// Ensure DefaultGitExecutor implements GitExecutor.
var _ GitExecutor = (*DefaultGitExecutor)(nil)
