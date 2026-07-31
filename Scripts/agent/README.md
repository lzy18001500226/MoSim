# Model Studio AI Backend

The active backend is `codex_cli_agent_server.py`. Model Studio starts it on
`127.0.0.1:8765` after the first assistant question, and the bridge invokes the
Codex binary built from `src/Agent/codex-main/`.

```powershell
python Scripts\agent\codex_cli_agent_server.py --health
python -m unittest Scripts.agent.tests.test_codex_cli_agent_server
```

The source build, GPT login, non-secret configuration template, license notice,
and platform-specific commands are documented in `src/Agent/README.md` and
`RELEASE_CHECKLIST.md`. The active bridge accepts only loopback requests,
requires the project-built binary, uses a read-only sandbox, and does not pass
API-key environment variables into the Codex child process.

`mworks_analysis_agent_server.py`, `model_studio_agent_tools.py`, and
`test_model_studio_agent.py` are retained as the previous direct
Responses-compatible implementation and migration-test corpus. Studio does not
start that backend anymore.
