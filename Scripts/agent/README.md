# Model Studio Agent

`mworks_analysis_agent_server.py` is the local backend for the `MoSim AI 助手`
tab in Model Studio. It uses an OpenAI Responses-compatible endpoint and a
small, allowlisted read-only tool set. The Studio UI starts it only after the
user sends a question.

## Configure locally

The repository configuration is
`Config/control_platform/model_studio_agent_v1.toml`. It contains the endpoint,
model name, limits, and safety policy, but never a credential.

Set the key in the process environment that starts Syslab/Model Studio:

```powershell
$env:MOSIM_OPENAI_API_KEY = "<your-key>"
# Optional per-machine endpoint override:
# $env:MOSIM_AGENT_BASE_URL = "https://<endpoint>/v1"
```

`OPENAI_API_KEY` is accepted as a compatibility fallback. Do not put either key
in a `.toml`, `.env`, source file, result, screenshot, or terminal log.

## Run and verify

```powershell
python Scripts\agent\mworks_analysis_agent_server.py --health
python Scripts\agent\mworks_analysis_agent_server.py --host 127.0.0.1 --port 8765
```

The server uses FastAPI and Uvicorn when they are already installed. Without
them it uses Python's standard-library HTTP server with the same `/health` and
`/mworks/query` endpoints. Optional dependencies are listed in
`requirements-model-studio-agent.txt`.

The Studio bridge uses `mworks_analysis_agent_client.py`; it exchanges base64
encoded text only with the loopback server, so question text does not need to be
put into a shell command line unescaped.

## Read-only boundary

The current implementation exposes 30 callable read-only tools. They can inspect
the active Studio context, registered FormalRunner routes, seven-scenario
profiles, implementation mappings, frozen gate and run records, converted MWORKS
documents, static Modelica dependencies, bounded allowlisted files, selected
result summaries, and CSV statistics. Chart-related tools prepare validated input
data only; they never generate or export a file. Tool invocations are returned to
the UI with a request identifier.

It cannot modify files, invoke MWORKS, run `CheckModel` or a simulation, export
or compile code, open a result, or send QGC/Gazebo/PX4/ROS/MAVROS commands.
The MWORKS and runtime work remain manual, separately evidenced operations.

## Test

```powershell
python -m unittest Scripts.agent.tests.test_model_studio_agent
```

The tests use no API key and make no network request.
