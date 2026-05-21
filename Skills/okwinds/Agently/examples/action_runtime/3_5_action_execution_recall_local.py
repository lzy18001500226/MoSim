from pathlib import Path
from pprint import pprint

from agently import Agently
from agently.core import Action


agent = Agently.create_agent()
workspace = Path(__file__).resolve().parent

agent.enable_shell(
    root=workspace,
    commands=["pwd"],
    action_id="inspect_workspace",
)

records = agent.action.execute_action(
    "inspect_workspace",
    {"cmd": "pwd", "workdir": str(workspace)},
    purpose="Inspect workspace path",
)

print("RAW ACTION RECORD")
pprint(records)

print("\nMODEL-VISIBLE ACTION RESULTS")
pprint(Action.to_action_results([records]))

artifact_refs = records.get("artifact_refs") or []
assert artifact_refs
artifact_ref = artifact_refs[0]
artifact_id = artifact_ref.get("artifact_id")
action_call_id = artifact_ref.get("action_call_id")
assert artifact_id is not None
assert action_call_id is not None
raw_artifact = agent.action.read_action_artifact(
    artifact_id=artifact_id,
    action_call_id=action_call_id,
)

print("\nRECALLED RAW ARTIFACT")
pprint(raw_artifact)

# Expected key output:
# RAW ACTION RECORD contains model_digest and artifact_refs.
# MODEL-VISIBLE ACTION RESULTS contains the compact digest, not only raw stdout.
# RECALLED RAW ARTIFACT returns the saved action input for inspect_workspace.

# How it works:
# agent.action.execute_action() bypasses model planning entirely and calls the action
# directly with explicit arguments — useful for testing or scripted workflows.
# enable_shell() registers a bash action restricted to the "pwd" command.
# The raw ActionResult contains model_digest (a compact summary the model can read)
# and artifact_refs (pointers to full stored artifacts).
# agent.action.read_action_artifact() retrieves the raw artifact by artifact_id +
# action_call_id for audit or downstream use.
#
# Flow:
# agent.enable_shell(root=workspace, commands=["pwd"], action_id="inspect_workspace")
#   |
#   v
# agent.action.execute_action("inspect_workspace", {"cmd":"pwd","workdir":workspace})
#   | (no model call — direct execution)
#   v
# BashSandboxActionExecutor -> stdout = str(workspace)
# ActionResult { model_digest: ..., artifact_refs: [{ artifact_id, action_call_id }] }
#   |
#   v
# Action.to_action_results([records]) -> compact model-visible dict
# agent.action.read_action_artifact(artifact_id, action_call_id) -> raw artifact
