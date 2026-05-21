# Engineering Specification Index — wkteam `api-wen-dang2` SDK

权威输入（离线 API 文档）：
- `docs/api/SUMMARY.md`（本地私有：不进入开源仓库，需自行获取）
- `docs/api/api-wen-dang2/`（本地私有：不进入开源仓库，需自行获取）

## 00 Overview
- [SUMMARY.md](00_Overview/SUMMARY.md) — Executive summary
- [REQUIREMENTS_MATRIX.md](00_Overview/REQUIREMENTS_MATRIX.md) — Traceability
- [DECISION_LOG.md](00_Overview/DECISION_LOG.md) — Architecture decisions
- [TECH_STACK.md](00_Overview/TECH_STACK.md) — Technology stack
- [REPO_LAYOUT.md](00_Overview/REPO_LAYOUT.md) — 仓库结构重构规格（多 SDK 收敛）
- [API_DOC_COVERAGE.generated.md](00_Overview/API_DOC_COVERAGE.generated.md) — 离线文档覆盖性与解析质量报告（生成）
- [API_COVERAGE_REVIEW.md](00_Overview/API_COVERAGE_REVIEW.md) — 对照离线文档的覆盖复盘（人工）

## 01 Requirements
- [USER_STORIES.md](01_Requirements/USER_STORIES.md)
- [FUNCTIONAL_REQS.md](01_Requirements/FUNCTIONAL_REQS.md)
- [NON_FUNCTIONAL_REQS.md](01_Requirements/NON_FUNCTIONAL_REQS.md)

## 02 Technical Design
- [ARCHITECTURE.md](02_Technical_Design/ARCHITECTURE.md)
- [PYTHON_SDK_ARCHITECTURE.md](02_Technical_Design/PYTHON_SDK_ARCHITECTURE.md) — Python SDK 结构与覆盖性门槛
- [DATA_MODEL.md](02_Technical_Design/DATA_MODEL.md)
- [API_SPEC.md](02_Technical_Design/API_SPEC.md) — 全量 endpoint 清单（从离线文档生成）
- [BUSINESS_LOGIC.md](02_Technical_Design/BUSINESS_LOGIC.md)
- `02_Technical_Design/schemas/api_catalog.json` — endpoint catalog（从离线文档生成）

## 03 Security
- [AUTH_DESIGN.md](03_Security/AUTH_DESIGN.md)
- [DATA_SECURITY.md](03_Security/DATA_SECURITY.md)
- [AUDIT_SPEC.md](03_Security/AUDIT_SPEC.md)

## 04 Operations
- [DEPLOYMENT.md](04_Operations/DEPLOYMENT.md)
- [CONFIGURATION.md](04_Operations/CONFIGURATION.md)
- [MONITORING.md](04_Operations/MONITORING.md)
- [RUNBOOK.md](04_Operations/RUNBOOK.md)

## 05 Testing
- [TEST_PLAN.md](05_Testing/TEST_PLAN.md)
- [ACCEPTANCE_TESTS.md](05_Testing/ACCEPTANCE_TESTS.md)

## 06 Implementation
- [TASK_BREAKDOWN.md](06_Implementation/TASK_BREAKDOWN.md)
- [MILESTONES.md](06_Implementation/MILESTONES.md)
- [RISKS.md](06_Implementation/RISKS.md)
- [MIGRATION.md](06_Implementation/MIGRATION.md)
