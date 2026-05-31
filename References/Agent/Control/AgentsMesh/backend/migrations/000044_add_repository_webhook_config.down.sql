-- Remove webhook_config column from repositories table

ALTER TABLE repositories DROP COLUMN IF EXISTS webhook_config;
