-- Rename workspace_path to sandbox_path
-- The field stores the Sandbox root directory, not the workspace subdirectory
ALTER TABLE pods RENAME COLUMN workspace_path TO sandbox_path;
