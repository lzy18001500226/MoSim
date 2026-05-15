# Verify Example

## Scope

Use this workflow when the user asks to verify an official example, enterprise example, or existing reference model through real Sysplorer execution.

## Required Inputs

- Example class name, model name, or file path.
- Requested verification depth: check only, check plus translate, full simulation, result review, diagram export, or reuse assessment.
- Target variables, expected behavior, or acceptance criteria when available.
- Whether the user wants only verification or a follow-up user-owned model derived from the example.

## Execution

1. Use the parent seven gates and the Gate 2 requirement additions in `SKILL.md` to normalize the example target and success criteria.
2. Read `references/component-map.md` to identify whether the example belongs to a system library or component-design library path.
3. Read `references/manual-knowledge.md` when library dependency, example entry, or secondary-development context matters.
4. Load the required TY and medium libraries through MCP when needed.
5. Use actual MCP actions for verification. Do not write "should work" as the result.
6. Run `check_model`; if it fails, use `references/error-repair-playbook.md` and report the blocker.
7. For `TYHydraulics` / `TYHydraulicComponents` examples, run or manually apply `references/capacitor-resistive-check.md`; if it changes topology or volume switches, rerun `check_model`.
8. Run `translate_model` when required by the requested verification depth or runtime path.
9. Run `simulate_model` when requested or necessary to judge the example.
10. Read target variables with `result_manager`; if none are provided, identify a small set of variables that map to the example purpose.
11. Use `references/validation-rules.md` for result and diagram judgments.
12. Export or directly review the diagram if diagram quality is part of the request.
13. If the user asks for reuse, state what can be reused and what must be rebuilt in a user-owned model.

## Failure Handling

- An example is not validated until the requested MCP actions actually succeed.
- Do not silently turn an example wrapper or `extends` chain into the final user model.
- If the example requires unavailable libraries or a broken session, state the exact blocker.
- If the example runs but results are physically implausible, enter the repair loop or report verification failure.

## Delivery Focus

- Example target and actual library/dependency path.
- Actual Sysplorer version and TY libraries used.
- MCP actions executed and their success/failure.
- Key result variables and judgments.
- Diagram review status when applicable.
- Reuse scope, limitations, and next steps for converting the example into a user-owned model.
