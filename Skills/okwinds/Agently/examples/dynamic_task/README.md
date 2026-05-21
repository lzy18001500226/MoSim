# Dynamic Task Examples

Dynamic Task examples use the application-level facade:

```python
Agently.create_dynamic_task(...)
agent.create_dynamic_task(...)
```

TriggerFlow remains the execution substrate, but these examples are not
TriggerFlow authoring examples. Use `examples/trigger_flow/` when you want to
write workflows directly with `TriggerFlow`.

Examples:

- `01_dynamic_task_basic.py`: feature-level submitted `TaskDAG` smoke test with
  local handlers only.
- `02_support_response_module_model.py`: complete model-powered intelligent
  module with a simple `SupportResponseModule.respond(ticket)` facade, backend
  fan-out/join stages, structured model outputs, mocked business-system
  lookups, and a printed frontstage customer response.
- `03_contract_risk_review_business.py`: business landing example with a simple
  `ContractRiskReviewService.review(contract)` facade, deterministic local rule
  handlers, backend risk scoring, and a printed frontstage risk memo.
- `04_incident_briefing_auto_plan.py`: auto-planned business example with a
  simple `IncidentBriefingService.brief(report)` facade. The model creates the
  `TaskDAG`; Dynamic Task validates and executes it, and Agently
  `output_schema` enforces the frontstage briefing result shape.
- `05_enterprise_renewal_complex_auto_plan.py`: complex auto-planned business
  example with multiple model-generated root analysis branches, a join
  synthesis stage, and a structured recovery package for an enterprise renewal.

Model-powered examples use DeepSeek when `DEEPSEEK_API_KEY` is present, or
local Ollama otherwise. Set `DYNAMIC_TASK_MODEL_PROVIDER=ollama` to force the
Ollama path.

Business-system feedback is mocked only where the example is not connected to a
real external system, such as billing or incident-status lookup. Model-owned
planning, analysis, and natural-language response generation still come from a
real model run.
