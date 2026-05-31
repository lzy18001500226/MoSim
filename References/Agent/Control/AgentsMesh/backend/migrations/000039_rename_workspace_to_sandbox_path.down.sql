-- Revert sandbox_path back to workspace_path
ALTER TABLE pods RENAME COLUMN sandbox_path TO workspace_path;
