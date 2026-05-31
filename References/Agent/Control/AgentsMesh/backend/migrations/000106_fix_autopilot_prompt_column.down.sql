-- Revert: prompt → initial_prompt on autopilot_controllers
ALTER TABLE autopilot_controllers RENAME COLUMN prompt TO initial_prompt;
