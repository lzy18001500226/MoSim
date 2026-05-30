# Requirements Traceability Matrix（可追溯矩阵）

> 目标：把 “离线 API 文档 → SDK 能力 → 工程规格 → 测试计划” 串起来，避免遗漏。

| User Story | Functional Req（代表性） | Tech Spec | Security | Test Coverage | Status |
|------------|--------------------------|----------|----------|--------------|--------|
| US-001：创建客户端与配置 | FR-BASIC-001/002 | `02_Technical_Design/ARCHITECTURE.md`、`04_Operations/CONFIGURATION.md` | `03_Security/DATA_SECURITY.md` | `05_Testing/TEST_PLAN.md` | Draft |
| US-002：登录与会话 | FR-AUTH-001/002/003 | `03_Security/AUTH_DESIGN.md`、`02_Technical_Design/BUSINESS_LOGIC.md` | `03_Security/AUTH_DESIGN.md` | `05_Testing/ACCEPTANCE_TESTS.md` | Draft |
| US-003：消息发送全覆盖 | FR-MSGSEND-* | `02_Technical_Design/API_SPEC.md` | `03_Security/DATA_SECURITY.md` | `05_Testing/TEST_PLAN.md` | Draft |
| US-004：消息接收与回调解析 | FR-CALLBACK-* | `02_Technical_Design/DATA_MODEL.md`、`02_Technical_Design/BUSINESS_LOGIC.md` | `03_Security/AUDIT_SPEC.md` | `05_Testing/ACCEPTANCE_TESTS.md` | Draft |
| US-005：好友/群/标签/收藏等管理 | FR-CONTACT/GROUP/LABEL/FAV-* | `02_Technical_Design/API_SPEC.md` | `03_Security/DATA_SECURITY.md` | `05_Testing/TEST_PLAN.md` | Draft |
| US-006：朋友圈/视频号等能力 | FR-SNS/FINDER-* | `02_Technical_Design/API_SPEC.md` | `03_Security/DATA_SECURITY.md` | `05_Testing/TEST_PLAN.md` | Draft |
| US-007：统一错误与可观测 | FR-OBS-001/ERR-001 | `02_Technical_Design/ARCHITECTURE.md`、`03_Security/AUDIT_SPEC.md`、`04_Operations/MONITORING.md` | `03_Security/AUDIT_SPEC.md` | `05_Testing/TEST_PLAN.md` | Draft |
| US-008：覆盖性核验（不漏接口） | FR-COV-001 | `00_Overview/API_DOC_COVERAGE.generated.md`、`02_Technical_Design/schemas/api_catalog.json` | - | `05_Testing/TEST_PLAN.md`（工具链测试） | Draft |

## Coverage Summary（当前）

- Offline docs: `docs/api/api-wen-dang2/**/*.md`（不含 `SUMMARY.md`）共 142 个文件
- Endpoint entries: 127（见 `02_Technical_Design/schemas/api_catalog.json`）
- Coverage report: `00_Overview/API_DOC_COVERAGE.generated.md`（生成）

## Gaps（需要在实现前闭环）

- baseUrl/限流/token 生命周期等“平台侧隐含契约”需要通过集成验证补齐（见 `docs/specs/PRD_VALIDATION_REPORT.md`）
