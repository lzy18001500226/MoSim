package workspace

import (
	"os"
	"path/filepath"
	"testing"
)

// --- Test findMainRepo ---

func TestFindMainRepoNoGitFile(t *testing.T) {
	tmpDir := t.TempDir()
	manager, _ := NewManager(tmpDir, "")

	worktreePath := filepath.Join(tmpDir, "worktree")
	os.MkdirAll(worktreePath, 0755)

	_, err := manager.findMainRepo(worktreePath)
	if err == nil {
		t.Error("expected error for missing .git file")
	}
}

func TestFindMainRepoInvalidGitFile(t *testing.T) {
	tmpDir := t.TempDir()
	manager, _ := NewManager(tmpDir, "")

	worktreePath := filepath.Join(tmpDir, "worktree")
	os.MkdirAll(worktreePath, 0755)

	gitFile := filepath.Join(worktreePath, ".git")
	os.WriteFile(gitFile, []byte("invalid content"), 0644)

	_, err := manager.findMainRepo(worktreePath)
	if err == nil {
		t.Error("expected error for invalid .git file format")
	}
}

func TestFindMainRepoValidGitFile(t *testing.T) {
	tmpDir := t.TempDir()
	manager, _ := NewManager(tmpDir, "")

	mainRepoDir := filepath.Join(tmpDir, "repos", "main")
	os.MkdirAll(filepath.Join(mainRepoDir, ".git", "worktrees", "pod-1"), 0755)

	worktreePath := filepath.Join(tmpDir, "worktrees", "pod-1")
	os.MkdirAll(worktreePath, 0755)

	gitDir := filepath.Join(mainRepoDir, ".git", "worktrees", "pod-1")
	gitFile := filepath.Join(worktreePath, ".git")
	os.WriteFile(gitFile, []byte("gitdir: "+gitDir), 0644)

	repoPath, err := manager.findMainRepo(worktreePath)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	if repoPath == "" {
		t.Error("repoPath should not be empty")
	}
}

func TestFindMainRepoBareRepo(t *testing.T) {
	tmpDir := t.TempDir()
	manager, _ := NewManager(tmpDir, "")

	bareRepoDir := filepath.Join(tmpDir, "repo.git")
	os.MkdirAll(filepath.Join(bareRepoDir, "worktrees", "pod-1"), 0755)

	worktreePath := filepath.Join(tmpDir, "worktrees", "pod-1")
	os.MkdirAll(worktreePath, 0755)

	gitDir := filepath.Join(bareRepoDir, "worktrees", "pod-1")
	gitFile := filepath.Join(worktreePath, ".git")
	os.WriteFile(gitFile, []byte("gitdir: "+gitDir), 0644)

	repoPath, err := manager.findMainRepo(worktreePath)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	if repoPath == "" {
		t.Error("repoPath should not be empty")
	}
}
