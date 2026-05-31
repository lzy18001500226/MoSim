-- Claude Code >=2.1.92 requires --verbose when using --output-format stream-json with -p
-- Without it: "Error: When using --print, --output-format=stream-json requires --verbose"

UPDATE agents SET agentfile_source = REPLACE(
    agentfile_source,
    E'MODE acp "-p" "--input-format" "stream-json" "--output-format" "stream-json"',
    E'MODE acp "-p" "--verbose" "--input-format" "stream-json" "--output-format" "stream-json"'
) WHERE slug = 'claude-code';
