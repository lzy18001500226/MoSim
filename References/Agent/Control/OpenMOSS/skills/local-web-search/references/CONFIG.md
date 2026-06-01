# Local Web Search Skill – Config

This skill calls a local Responses API endpoint with the `web_search` tool.

## Recommended .env location

The script auto-loads a `.env` file from (in order):

1. `$OPENCLAW_WORKSPACE/.env` (if `OPENCLAW_WORKSPACE` is set)
2. `/workspace/.env` (sandbox)
3. `~/.openclaw/workspace/.env` (macOS/Linux)

You can also pass `--env-file /path/to/.env` to load only that file.

## Required env vars (recommended)

Put these in your `.env`:

```
LOCAL_160_BASE_URL=https://proxy.example.com
LOCAL_160_API_KEY=sk-...your-key...
LOCAL_160_MODEL=gpt-5.2-codex(xhigh)
LOCAL_160_TIMEOUT=1200
```

## macOS Keychain (optional)

You can store config in Keychain instead of `.env`.
Service: `openclaw-local-160`
Accounts: `base-url`, `api-key`, `model`

```bash
security add-generic-password -U -s openclaw-local-160 -a base-url -w
security add-generic-password -U -s openclaw-local-160 -a api-key -w
security add-generic-password -U -s openclaw-local-160 -a model -w
```

## Script usage

```bash
/usr/bin/python3 {baseDir}/scripts/local_web_search.py --query "OpenAI Codex CLI" --mode live
```

Add `--json` to dump the raw Responses JSON.

## Notes

- Uses `/v1/responses` with `tools=[{"type":"web_search"}]`.
- If the endpoint returns 401/403, check key and base URL.
