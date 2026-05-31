package workspace

import (
	"context"
	"os"
	"os/exec"
	"path/filepath"
	"testing"
)

// --- Test RemoveWorktree ---

func TestRemoveWorktreeNonExistent(t *testing.T) {
	tmpDir := t.TempDir()
	manager, _ := NewManager(tmpDir, "")

	err := manager.RemoveWorktree(context.Background(), "/nonexistent/worktree")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
}

func TestRemoveWorktreeWithGitFile(t *testing.T) {
	tmpDir := t.TempDir()
	manager, _ := NewManager(tmpDir, "")

	worktreePath := filepath.Join(tmpDir, "worktrees", "test-wt")
	os.MkdirAll(worktreePath, 0755)

	gitFile := filepath.Join(worktreePath, ".git")
	os.WriteFile(gitFile, []byte("gitdir: /nonexistent/repo/.git/worktrees/test-wt"), 0644)

	err := manager.RemoveWorktree(context.Background(), worktreePath)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	if _, err := os.Stat(worktreePath); !os.IsNotExist(err) {
		t.Error("worktree should be removed")
	}
}

func TestRemoveWorktreeInternalFallback(t *testing.T) {
	tmpDir := t.TempDir()
	manager, _ := NewManager(tmpDir, "")

	worktreePath := filepath.Join(tmpDir, "worktree")
	repoPath := filepath.Join(tmpDir, "repo")
	os.MkdirAll(worktreePath, 0755)
	os.MkdirAll(repoPath, 0755)

	testFile := filepath.Join(worktreePath, "test.txt")
	os.WriteFile(testFile, []byte("test"), 0644)

	err := manager.removeWorktreeInternal(context.Background(), repoPath, worktreePath)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	if _, err := os.Stat(worktreePath); !os.IsNotExist(err) {
		t.Error("worktree should be removed")
	}
}

func TestRemoveWorktreeInternalWithPrune(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping integration test in short mode")
	}

	if _, err := exec.LookPath("git"); err != nil {
		t.Skip("git not available")
	}

	tmpDir := t.TempDir()

	repoPath := filepath.Join(tmpDir, "repo")
	os.MkdirAll(repoPath, 0755)

	cmd := exec.Command("git", "init")
	cmd.Dir = repoPath
	cmd.Run()

	cmd = exec.Command("git", "config", "user.email", "test@test.com")
	cmd.Dir = repoPath
	cmd.Run()

	cmd = exec.Command("git", "config", "user.name", "Test")
	cmd.Dir = repoPath
	cmd.Run()

	testFile := filepath.Join(repoPath, "file.txt")
	os.WriteFile(testFile, []byte("content"), 0644)

	cmd = exec.Command("git", "add", ".")
	cmd.Dir = repoPath
	cmd.Run()

	cmd = exec.Command("git", "commit", "-m", "init")
	cmd.Dir = repoPath
	cmd.Run()

	worktreePath := filepath.Join(tmpDir, "worktree")
	cmd = exec.Command("git", "worktree", "add", worktreePath, "HEAD")
	cmd.Dir = repoPath
	if err := cmd.Run(); err != nil {
		t.Fatalf("failed to create git worktree: %v", err)
	}

	manager, _ := NewManager(tmpDir, "")

	ctx := context.Background()
	err := manager.removeWorktreeInternal(ctx, repoPath, worktreePath)
	if err != nil {
		t.Fatalf("removeWorktreeInternal failed: %v", err)
	}

	if _, err := os.Stat(worktreePath); !os.IsNotExist(err) {
		t.Error("worktree should be removed")
	}
}
