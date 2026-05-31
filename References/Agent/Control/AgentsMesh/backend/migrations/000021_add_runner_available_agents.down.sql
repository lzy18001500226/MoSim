-- Remove available_agents column from runners table
ALTER TABLE runners DROP COLUMN IF EXISTS available_agents;
