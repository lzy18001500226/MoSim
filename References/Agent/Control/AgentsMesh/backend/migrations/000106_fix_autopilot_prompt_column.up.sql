-- Fix: migration 000102 missed renaming initial_prompt → prompt on autopilot_controllers
-- (000102 only renamed on pods and ralph_pods, but ralph_pods was already renamed to autopilot_controllers in 000041)
ALTER TABLE autopilot_controllers RENAME COLUMN initial_prompt TO prompt;
