-- Projects: first-class workspace folder tracking for agents.
-- A project maps to a directory containing repos and worktrees.

CREATE TABLE IF NOT EXISTS projects (
    id TEXT PRIMARY KEY,
    agent_id TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    icon TEXT NOT NULL DEFAULT '',
    tags TEXT NOT NULL DEFAULT '[]',
    root_path TEXT NOT NULL,
    settings TEXT NOT NULL DEFAULT '{}',
    status TEXT NOT NULL DEFAULT 'active',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_projects_agent ON projects(agent_id);
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(agent_id, status);
CREATE UNIQUE INDEX IF NOT EXISTS idx_projects_root_path ON projects(agent_id, root_path);

-- Repos: git repositories within a project folder.
CREATE TABLE IF NOT EXISTS project_repos (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    name TEXT NOT NULL,
    path TEXT NOT NULL,
    remote_url TEXT NOT NULL DEFAULT '',
    default_branch TEXT NOT NULL DEFAULT 'main',
    description TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_project_repos_project ON project_repos(project_id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_project_repos_path ON project_repos(project_id, path);

-- Worktrees: git worktrees checked out at the project root level.
CREATE TABLE IF NOT EXISTS project_worktrees (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    repo_id TEXT NOT NULL,
    name TEXT NOT NULL,
    path TEXT NOT NULL,
    branch TEXT NOT NULL,
    created_by TEXT NOT NULL DEFAULT 'user',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (repo_id) REFERENCES project_repos(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_project_worktrees_project ON project_worktrees(project_id);
CREATE INDEX IF NOT EXISTS idx_project_worktrees_repo ON project_worktrees(repo_id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_project_worktrees_path ON project_worktrees(project_id, path);
