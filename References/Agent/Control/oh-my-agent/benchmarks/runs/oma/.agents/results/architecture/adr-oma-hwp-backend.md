# ADR: `oma-hwp` skill 백엔드 전략

- Status: Accepted
- Date: 2026-04-19 (revised)
- Scope: `.agents/skills/oma-hwp/`
- Related: `.agents/skills/oma-pdf/` (패턴 참조)

## Context

HWP / HWPX / HWPML 파일을 Markdown으로 변환하는 `oma-hwp` skill을 신설한다.
`oma-pdf`가 `uvx opendataloader-pdf`를 래핑하듯, 한글 문서 생태계에도 동등한 CLI가 필요했다.

초기에는 `@hwp.js/parser`(HWP5 전용) + `rhwp` CLI(HWPX) 조합을 검토했으나, 실측 결과:
- `@hwp.js/parser`는 HWP5 전용이며 유지보수가 정체됨.
- `rhwp` CLI는 structured(JSON) 출력 커맨드가 없고 모든 서브커맨드가 debug 텍스트 또는 시각 렌더(SVG/PDF) — 외부 언어에서 소비 불가.
- 자체 HWPX 파서 구현은 rhwp 수준 커버리지 기준 3-5k LOC → skill 범위 초과.

## Decision

**`kordoc` (npm) CLI를 그대로 래핑**한다.

### `kordoc` 개요
- 패키지: `kordoc` v2.4.0, MIT, 779★, 활발히 유지됨
- 저자: chrisryugj (한국 공무원, 공문서 처리 7년 경력)
- 지원 포맷: **HWP, HWPX, HWPML, PDF, XLSX, DOCX → Markdown**
- 순수 JS/TS 구현, Bun에서 네이티브 실행
- `rhwp`의 AES-128 ECB 복호화 등 DRM/배포용 HWP 처리 알고리즘을 **순수 JS로 포팅**해 내장 — 별도 wasm/Rust 바이너리 불필요
- CLI: `bunx kordoc <input>` → Markdown
- MCP 서버(`kordoc-mcp`)도 번들되어 있음 (본 skill은 사용 안 함)

### 역할 분담
- `oma-hwp`는 **한글 문서 생태계(HWP/HWPX/HWPML) 래퍼**. PDF/XLSX/DOCX는 kordoc이 지원해도 skill의 공식 scope에서는 제외 (oma-pdf가 있고 향후 oma-docs 등으로 분리 여지).
- oma-hwp는 TS 파일을 소유하지 않음. `oma-pdf`와 동형으로 execution-protocol + bash/bunx 호출만.

### 기각된 대안
- **자체 HWPX 파서**: LOC 과다. skill 범위 초과.
- **`@hwp.js/parser` + `rhwp` CLI 조합**: rhwp CLI에 structured output 없음.
- **rhwp wasm(`@rhwp/core`) 직접 호출**: kordoc이 이미 rhwp 알고리즘을 순수 JS로 흡수 → wasm 계층 추가 이득 없음.
- **자체 DocumentModel · 어댑터 · 렌더러**: kordoc이 이미 Markdown 출력 → 중간 계층 불필요.

## Consequences

### Positive
- skill 구현 공수 수 시간. `oma-pdf`와 동등한 패턴.
- HWP / HWPX / HWPML / PDF / XLSX / DOCX까지 즉시 지원 (공식 scope는 HWP 계열만 선언).
- DRM·손상된 HWP 복구까지 kordoc이 처리 (7년차 도메인 전문가가 꾸준히 관리).
- Node/Bun 단일 런타임 — `uvx`만큼 UX 가벼움.
- 보안(ZIP bomb, XXE, SSRF 방어)이 이미 kordoc에 내장.

### Negative / Risks
- kordoc의 MD 출력 스타일·플래그 셋에 종속. 커스텀 여지가 제한됨.
- kordoc이 PDF도 지원 → oma-pdf와 영역 중복. **완화**: oma-hwp는 HWP 계열로 scope 제한, PDF 입력은 oma-pdf로 유도하는 안내 명기.
- kordoc 버전 변경 시 출력 달라질 가능성. **완화**: execution-protocol에 `bunx kordoc@<version>`을 권장 또는 최소 fixture 회귀.
- HWPX DRM 추출 중 Windows+한컴오피스 필요 경로가 있음 → **완화**: 우리는 일반 HWPX만 공식 지원, DRM은 "best effort"로 명기.

### Assumptions
- 사용자 환경에 Bun 1.1+ 가용.
- kordoc이 MIT로 계속 유지됨.
- HWP5·HWPX·HWPML 공개 샘플로 fixture 확보 가능.

## Validation Plan

1. Fixture set: 공공 HWP/HWPX 샘플 5건 이상. 표·이미지·각주 포함.
2. `bunx kordoc <fixture> --out-dir ./out` 실행 결과 MD의 구조 검증.
3. 실패 케이스(암호화 HWP, 손상 파일) 에러 메시지 가독성 확인.
4. skill은 추가 회귀 테스트를 두지 않음 — kordoc 자체 테스트에 의존.

## Open Questions
- kordoc이 PDF 머리글/바닥글 제거(`--no-header-footer`) 외에 HWP 전용 플래그가 있는지 → 실측으로 확인 후 `SKILL.md`에 반영.
- kordoc 버전 pin 정책 — `@latest` 권장 vs 특정 버전 고정.
