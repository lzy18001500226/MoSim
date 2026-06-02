# Post-M0 Audit — 2026-04-18

**담당:** repo-auditor 에이전트
**대상 저장소:** `/Users/robin/IdeaProjects/harness`
**상위 작업:** release-engineer / content-creator / launch-strategist / community-scout 4개 에이전트의 M0 Quick Wins 병렬 적용 결과 통합 검증
**검증 방식:** 읽기만 (Edit/Write 금지). `git diff`·`git status`·파일별 Read로 정합성·충돌·섹션 유실 판정.

---

## 1. 검증 결과 (PASS/FAIL 매트릭스)

### A. 버전 정합성 (release-engineer)

| 영역 | 검증 항목 | 결과 | 비고 |
|------|-----------|------|------|
| A-1 | `README.md:6` 뱃지 `Version-1.2.0` | **PASS** | `brightgreen` 유지, 원본 `1.0.1` → 변경 확인 |
| A-2 | `README_KO.md:6` 뱃지 `Version-1.2.0` | **PASS** | 동일 문자열 일관 |
| A-3 | `README_JA.md:6` 뱃지 `Version-1.2.0` | **PASS** | 동일 문자열 일관 |
| A-4 | `.claude-plugin/marketplace.json:14` `"version": "1.2.0"` | **PASS** | 원본 `1.1.0` → `1.2.0` |
| A-5 | `.claude-plugin/plugin.json:4` `"version": "1.2.0"` 유지 | **PASS (수치)** / **FAIL (정책)** | version 필드는 `1.2.0` 그대로이나 `description`·`keywords`가 변경됨 — §4 충돌 감사 참조 |
| A-6 | `CHANGELOG.md` [1.2.1] 엔트리 | **PASS** | `[1.2.1] - 2026-04-18` 섹션이 최상단에 존재, Fixed/Added/Changed 3블록 |
| A-7 | `_workspace/release/audit-2026-04-18.md` 존재 | **PASS** | 228줄, 5섹션 + 2부록 완비 |

### B. README "harness factory" 포지셔닝 (content-creator)

| 영역 | 검증 항목 | EN | KO | JA | 비고 |
|------|-----------|----|----|----|------|
| B-1 | H1 `Harness — The Team-Architecture Factory for Claude Code` (언어별 번역) | **PASS** | **PASS** | **PASS** | EN(L20), KO(L20 "팀 아키텍처 팩토리"), JA(L20 "チームアーキテクチャファクトリー") |
| B-2 | H1 아래 callout 문단 (3언어 트리거 병기) | **PASS** | **PASS** | **PASS** | EN(L24), KO(L24), JA(L24) — 모두 영/한/일 3종 트리거 구문 병기 |
| B-3 | 뱃지 3종(Layer / Sub-layer / i18n) | **PASS** | **PASS** | **PASS** | EN(L14–18), KO(L14–18), JA(L14–18) — 3개 모두 해당 언어 앵커로 링크 |
| B-4 | "Category — Where Harness Sits" 4행 표 | **PASS** | **PASS** | **PASS** | EN(L30–39 + L41 풋노트), KO(L30–41), JA(L30–41) — 4행 표 + Archon vs. Harness 요약문 |
| B-5 | "Harness Evolution Mechanism" 섹션 | **PASS** | **PASS** | **PASS** | EN(L61–74), KO(L50–63), JA(L50–63) — 델타 포착 ASCII 도식 포함 |
| B-6 | "+60%" 방어 카드 공식 문구 (n=15, author-measured, third-party replications pending) | **PASS** | **PASS** | **PASS** | EN(L273), KO(L255), JA(L262) — 3개 언어 모두 동일 문구 보유. FAQ Q1(EN:L286 / KO:L268 / JA:L275)에서도 재확인 |
| B-7 | "Coexistence" 5행 표 | **PASS** | **PASS** | **PASS** | EN(L247–253), KO(L229–235), JA(L236–242) — 5행(Archon·meta-harness·ECC·wshobson·LangGraph) |
| B-8 | "FAQ" 섹션 (Q1~Q3 details) | **PASS** | **PASS** | **PASS** | 3개 모두 `<details>` 3개(+60% / harness factory / Claude Code only) |

### C. docs/ 디렉토리 (launch-strategist)

| 영역 | 검증 항목 | 결과 | 비고 |
|------|-----------|------|------|
| C-1 | `docs/experimental-dependency.md` (~150줄) | **PASS** | 154줄. Current State / Dependency Graph / 3 Scenarios (A·B·C T+24/48/72h) / Monitoring SLA 표 / Enterprise FAQ Q1–Q3 모두 포함 |
| C-2 | `docs/quickstart.md` (~120줄, 5단계·실패 FAQ 5건) | **PASS** | 118줄. Step 1–5 + 각 단계에 Failure FAQ #1–#5 배치. 5분 시간 예산 상단 고지 |
| C-3 | `docs/show-hn-launch-kit.md` (~220줄, 2026-05-06 07:05 PT) | **PASS** | 224줄. 스케줄 표에 `2026-05-06 Wed 07:05 PT` 명시. Title A/B/C · 380단어 Body · T-72h~T+72h 타임라인 · Post-launch 분기 · 5%-oversold 대응 · Crossposting Rules 모두 존재 |

### D. 거버넌스 (community-scout)

| 영역 | 검증 항목 | 결과 | 비고 |
|------|-----------|------|------|
| D-1 | `CONTRIBUTING.md` SLA 5항목 숫자 공표 | **PASS** | PR 1차 응답 72h / Issue triage 48h / Bug P0–P1 14d / Security 7d / Release 2w — 5항목 모두 표에 수치 공개 |
| D-2 | `.github/ISSUE_TEMPLATE/bug_report.yml` | **PASS** | claude-code-version · experimental-flag dropdown · 재현·기대·실제·OS dropdown 필수 필드 구성 |
| D-3 | `.github/ISSUE_TEMPLATE/feature_request.yml` | **PASS** | problem / proposal / alternatives / related-pattern dropdown(6패턴+N) 구조 |
| D-4 | `.github/ISSUE_TEMPLATE/question.yml` | **PASS** | question / tried / docs 3필드 |
| D-5 | `.github/ISSUE_TEMPLATE/config.yml` | **PASS** | `blank_issues_enabled: false` + Discussions 링크 + 보안 mailto |
| D-6 | `.github/PULL_REQUEST_TEMPLATE.md` | **PASS** | Summary/Motivation/Scope 체크박스 8종/Tests/CHANGELOG/SemVer 4지선 |
| D-7 | `_workspace/community/issue-3-reply.md` (영문) | **PASS** | Gemini PoC 로드맵 P-01, SaehwanPark/meta-harness 언급, Gizele1/harness-init·OpenRig 대안 포함 |
| D-8 | `_workspace/community/issue-2-reply.md` (영문) | **PASS** | hesreallyhim 직접 인용("really good stuff ... Nice job."), 뱃지 추가 + "Harness Factories" 카테고리 제안 |

---

## 2. 발견된 문제

| # | 심각도 | 위치 | 문제 | 권장 조치 |
|---|--------|------|------|----------|
| **1** | **Critical** | `.claude-plugin/plugin.json:3, 12–28` | **`plugin.json`은 "건드리지 말았어야 함"으로 지시되었으나 `description` 전면 재작성 + `keywords` 7개 추가되었다.** release-engineer 감사 문서(`audit-2026-04-18.md:89–91`)는 "plugin.json은 건드리지 않음"이라 선언했으나 실제 `git diff`는 해당 파일이 변경되었음을 보여준다. 이는 **content-creator가 포지셔닝 통일을 위해 무단 편집**한 충돌 흔적으로 판단됨. | 2가지 길 중 택1: (a) **수용**: CHANGELOG 1.2.1 Changed 블록에 "plugin.json description·keywords를 포지셔닝 선언과 정렬"을 **명시적으로 추가**하고 release-engineer audit §3.3의 "건드리지 않음" 서술을 "description·keywords는 content-creator 조정으로 변경, version은 유지"로 정정. (b) **복구**: `git restore .claude-plugin/plugin.json`으로 원상 복귀 후 별도 PR로 분리. — 현재 상태로 커밋하면 "감사 문서와 실제 상태가 모순"되는 위생 문제가 남는다. |
| **2** | Minor | `README.md:42` vs `README_KO.md`/`README_JA.md` | EN README에는 `## Star History` 섹션이 보존(L43–51)되어 있으나 KO/JA에는 해당 섹션이 **없음**. 원본 HEAD에서도 KO/JA에는 없었으므로 **삭제는 아님** — 다만 "3개 언어 파일의 대칭성"이라는 관점에서는 불일치. | 이번 릴리스에서는 **허용**(원본 유지). 차기 PR에서 KO/JA에도 Star History 섹션을 동일 위치(Category 섹션 직후)에 보강하는 `docs/i18n-parity` 이슈를 열 것을 권장. |
| **3** | Minor | `README.md:15–17` / `README_KO.md:15–17` / `README_JA.md:15–17` | `Layer` 뱃지의 앵커가 각 언어별로 다름 (EN: `#category--where-harness-sits`, KO: `#카테고리--harness는-어디에-서-있나요`, JA: `#カテゴリー--harness-はどこに位置するか`). 각 언어별 GitHub 자동 생성 anchor와 일치해야 하나, GitHub의 한글·일문 anchor 규칙은 `공백→하이픈 + 소문자화 + 일부 특수문자 제거`. **KO의 `카테고리--harness는-어디에-서-있나요`는 `—(em dash)`가 `--`로 렌더될 가능성이 낮음** (통상 `—`는 제거되거나 단일 `-`로 치환). 검증 필요. | 커밋 전 GitHub Preview나 로컬 grip으로 렌더 검증 권장. 깨질 경우 앵커를 `#카테고리-harness는-어디에-서-있나요` (em dash 삭제) 혹은 `<a name="">` 명시적 앵커로 교체. JA도 동일 주의. |
| **4** | Info | `_workspace/release/audit-2026-04-18.md:156` | §4.4에 `git push origin v1.0.0 v1.0.1 v1.1.0 v1.2.0` 실행 대기 항목이 있으나, 이번 M0 실적에는 태그 생성·push가 포함되지 않음 — 이는 **의도된 승인 대기 상태**로 문제 아님. 단, 다음 Phase 진입 전 태그 4건 처리 여부 결정 필요. | 태그 4건 + GitHub Release 초안은 M1 시작 전에 별도 실행. 본 M0 감사 범위 밖. |
| **5** | Info | `docs/experimental-dependency.md:65` | Scenario A의 "Nightly CI가 P-13에서 탐지" 링크가 `[P-13](#)` — placeholder 링크. 실제 로드맵·이슈 번호 미지정. | 로드맵 P-13 이슈를 실제로 오픈한 뒤 `#숫자`로 치환. launch-strategist 후속 작업. |

---

## 3. 5초 규칙 평가

### 3.1 상단 5초 스캔 시나리오

방문자가 `README.md` 상단에서 처음 만나는 시각 정보 순서:

1. **배너 이미지** (L1–3) — `harness_banner.png`
2. **기본 뱃지 6종** (L5–12) — Version `1.2.0` / License Apache 2.0 / Claude Code Plugin / 6 Architectures / Agent Teams / GitHub Stars
3. **포지셔닝 뱃지 3종** (L14–18) — `Layer: L3 Meta-Factory` / `Sub-layer: Team-Architecture Factory` / `README: EN | KO | JA`
4. **H1** (L20) — `Harness — The Team-Architecture Factory for Claude Code`
5. **언어 토글** (L22) — `English | 한국어 | 日本語`
6. **Callout 블록** (L24) — 3언어 트리거 병기한 한 문장 요약

### 3.2 5초 규칙 판정

| 기준 | 평가 |
|------|------|
| "팀 아키텍처 팩토리"임을 이해 가능한가? | **PASS** — H1 + Sub-layer 뱃지 + Callout 3중 노출. L3 Meta-Factory까지 5초 이내 도달 가능 |
| 트리거 문장을 시각화하는가? | **PASS** — Callout이 `"build a harness for this project"` / `"하네스 구성해줘"` / `"ハーネスを構成して"` 3종을 병기 |
| 신뢰 신호(버전·스타·라이선스)가 동시 노출? | **PASS** — 6종 기본 뱃지 첫 줄 |
| 3개 언어 독자가 동일 체험을 받는가? | **PASS** — EN/KO/JA 모두 동일한 3단 구조(이미지→뱃지→H1→Callout), 문자열만 번역 |
| 시선 낭비 요소(광고성 뱃지, 중복 링크)? | **PASS** — 뱃지 9종(기본 6 + 포지셔닝 3)으로 Trending 레포 평균(5–7) 상한. 과다 아님 |

### 3.3 섹션 순서 논리 평가

EN 기준 섹션 순서:

```
(1) Overview → (2) Category — Where Harness Sits → (3) Star History → (4) Key Features
→ (5) Harness Evolution Mechanism → (6) Workflow → (7) Installation → (8) Plugin Structure
→ (9) Usage (모드·패턴) → (10) Output → (11) Use Cases 8종 → (12) Coexistence
→ (13) Built with Harness (100 + A/B 연구) → (14) Requirements → (15) FAQ Q1–Q3 → (16) License
```

- **PASS** — "내가 무엇인지(1–2) → 내가 어떻게 진화하는지(5) → 어떻게 설치하나(7) → 어떻게 쓰나(9–11) → 이웃과 어떻게 공존하나(12) → 증거(13) → 반박·FAQ(15)" 순서가 자연스러움.
- 다만 KO/JA에서는 (3) Star History가 부재하여 (2) → (4)로 직행. 시선 흐름에는 오히려 더 부드러우므로 문제 없음.

---

## 4. 에이전트 충돌 감사

### 4.1 파일별 편집자 귀속 테이블

| 파일 | release-engineer | content-creator | launch-strategist | community-scout |
|------|------------------|-----------------|-------------------|-----------------|
| `README.md` | 뱃지 L6(Version) | H1·Callout·뱃지 3종·Category·Evolution·Coexistence·FAQ | — | — |
| `README_KO.md` | 뱃지 L6 | H1·Callout·뱃지·Category·Evolution·Coexistence·FAQ | — | — |
| `README_JA.md` | 뱃지 L6 | H1·Callout·뱃지·Category·Evolution·Coexistence·FAQ | — | — |
| `.claude-plugin/marketplace.json` | L14 version | — | — | — |
| `.claude-plugin/plugin.json` | **(건드리지 않기로 선언)** | **description·keywords 편집 (충돌)** | — | — |
| `CHANGELOG.md` | [1.2.1] 블록 추가 | — | — | — |
| `CONTRIBUTING.md` | — | — | — | 신규 |
| `.github/ISSUE_TEMPLATE/*` | — | — | — | 신규 (4종) |
| `.github/PULL_REQUEST_TEMPLATE.md` | — | — | — | 신규 |
| `docs/experimental-dependency.md` | — | — | 신규 | — |
| `docs/quickstart.md` | — | — | 신규 | — |
| `docs/show-hn-launch-kit.md` | — | — | 신규 | — |
| `_workspace/release/audit-2026-04-18.md` | 신규 | — | — | — |
| `_workspace/community/issue-{2,3}-reply.md` | — | — | — | 신규 (2종) |

### 4.2 같은 줄 동시 편집 여부

- **README 3종 뱃지 줄 (L6)** — release-engineer(Version 뱃지만 L6 문자열 교체) vs content-creator(H1 이하 섹션 재작성). **겹치지 않음**. content-creator도 L14–18에 **신규 뱃지 블록 추가**만 하고 L6을 건드리지 않았으므로 충돌 없음. **PASS**
- **README H1 (L20)** — release-engineer는 미편집. content-creator 단독 편집. **PASS**
- **`.claude-plugin/plugin.json`** — release-engineer는 L4(version)만 건드리지 않는 정책이었고 실제로 L4는 무변경. 그러나 L3(description) + L12–28(keywords)은 **편집되어 있음**. 이 편집이 content-creator에 의한 것이라면 release-engineer의 audit 문서 §3.3과 **선언-실제 불일치**. 단순 병합 충돌이 아닌 **정책 위반 성격의 협업 충돌**. → **2-1번 Critical 문제 참조**
- `_workspace/release/audit-2026-04-18.md` — release-engineer 단독. **PASS**

### 4.3 유실된 원본 섹션

| 섹션 | 원본(HEAD) 존재 | 현 EN | 현 KO | 현 JA | 판정 |
|------|-----------------|-------|-------|-------|------|
| Star History | EN만 보유 | 보존(L43) | 원래 없음 | 원래 없음 | **PASS** (유실 0) |
| Installation | EN/KO/JA 보유 | 보존(L92) | 보존(L81) | 보존(L81) | **PASS** |
| Plugin Structure | EN/KO/JA 보유 | 보존(L113) | 보존(L102) | 보존(L102) | **PASS** |
| Usage 모드·패턴 | EN/KO/JA 보유 | 보존(L132–162) | 보존(L121–151) | 보존(L121–151) | **PASS** |
| Use Cases 8종 | EN/KO/JA 보유 | 보존(L183–241) | 보존(L172–223) | 보존(L172–230) | **PASS** |
| Built with Harness (100 + A/B 연구) | EN/KO/JA 보유 | 보존(L255–275) | 보존(L237–257) | 보존(L244–264) | **PASS** |
| Requirements / License | EN/KO/JA 보유 | 보존 | 보존 | 보존 | **PASS** |

**종합:** 원본 섹션 유실 0건. 병합은 "기존 텍스트 사이에 새 섹션을 삽입"하는 방식으로 이루어져 충돌 없이 병렬 성공.

---

## 5. 결론

### 5.1 종합 PASS/FAIL

- **영역 A (버전 정합성):** 7개 중 6 PASS / 1 **정책 FAIL** (plugin.json description·keywords 무단 편집)
- **영역 B (포지셔닝):** 8 × 3언어 = 24항목 전부 PASS
- **영역 C (docs/):** 3 PASS
- **영역 D (거버넌스):** 8 PASS
- **5초 규칙:** PASS
- **에이전트 충돌:** 1 Critical (plugin.json 정책 위반) + 2 Minor (i18n anchor 렌더 검증 / KO·JA Star History 부재)

**총 Critical 문제: 1건**
**총 Minor 문제: 2건**
**Info(권장) 항목: 2건**

### 5.2 커밋 가능 여부

**조건부 커밋 가능.** 커밋 전 다음 1건 결정 필요:

#### 필수 선행 조치 — `plugin.json` 충돌 해소 (택1)

- **옵션 A (권장): 수용** — `_workspace/release/audit-2026-04-18.md` §3 표와 §3.3 문장을 수정하여 "description·keywords 변경 포함"을 명시. `CHANGELOG.md` [1.2.1] Changed 섹션에 아래 한 줄 추가:
  > - `.claude-plugin/plugin.json` description 및 keywords를 "harness factory" 포지셔닝 선언과 정렬 (version 1.2.0 유지)
- **옵션 B: 복구** — `git restore .claude-plugin/plugin.json`으로 원복한 뒤, 별도 후속 PR에서 content-creator가 정식 요청.

→ **repo-auditor는 옵션 A를 권장.** 근거: (a) 변경 내용 자체는 포지셔닝 일관성에 부합하고 무해함, (b) `.claude-plugin/plugin.json:4` version이 `1.2.0`으로 유지되어 Claude Code 런타임 기능에는 영향 없음, (c) 되돌리면 README/marketplace.json의 새 description과 plugin.json의 옛 description 사이에 **새로운 정합성 간극**이 발생.

#### 커밋 메시지 권장 문구 (옵션 A 채택 시)

```
feat: M0 Quick Wins — 포지셔닝 선언, 버전 정합성, 거버넌스 공개

- README 3종(EN/KO/JA) 상단을 "Team-Architecture Factory" 포지셔닝으로 재작성
  (Category · Evolution · Coexistence · FAQ 섹션 신설, Layer/Sub-layer/i18n 뱃지 3종 추가)
- 버전 1.2.0 정합성 동기화: README 뱃지 3종(1.0.1→1.2.0), marketplace.json(1.1.0→1.2.0)
- plugin.json description·keywords를 포지셔닝 선언과 정렬 (version 1.2.0 유지)
- CHANGELOG [1.2.1] 엔트리 추가
- CONTRIBUTING.md 신설: 5항목 SLA 수치 공개 (PR 72h / 이슈 48h / P0 14d / 보안 7d / 릴리스 2주)
- .github/ISSUE_TEMPLATE 4종(bug/feature/question/config) + PR 템플릿 신설
- docs/ 신설: experimental-dependency (3 시나리오 SLA), quickstart (5분 5단계), show-hn-launch-kit (2026-05-06 07:05 PT)
- _workspace/community: Issue #2 (awesome-claude-code 큐레이터) / Issue #3 (Gemini 질의) 답변 초안
- _workspace/release/audit-2026-04-18.md + post-m0-audit-2026-04-18.md: 감사 기록
```

### 5.3 선행 수정이 필요하지 않은 권장사항 (Info)

- **태그 4건(v1.0.0/v1.0.1/v1.1.0/v1.2.0) 소급 생성 + GitHub Release 초안** — `_workspace/release/audit-2026-04-18.md` §4, §5에 명령 텍스트 대기. M1 진입 전 별도 실행.
- **KO/JA README에 Star History 섹션 보강** — 차기 PR(`docs/i18n-parity`)로 분리.
- **GitHub anchor 렌더 검증** — Layer/Sub-layer 뱃지가 KO/JA에서 정상 클릭되는지 `gh pr create --draft` 이후 Preview 탭에서 육안 확인.

---

## 부록. 감사 근거 파일 목록

- `/Users/robin/IdeaProjects/harness/README.md` (317줄)
- `/Users/robin/IdeaProjects/harness/README_KO.md` (299줄)
- `/Users/robin/IdeaProjects/harness/README_JA.md` (306줄)
- `/Users/robin/IdeaProjects/harness/.claude-plugin/plugin.json` (수정됨, §2.1 Critical)
- `/Users/robin/IdeaProjects/harness/.claude-plugin/marketplace.json`
- `/Users/robin/IdeaProjects/harness/CHANGELOG.md`
- `/Users/robin/IdeaProjects/harness/CONTRIBUTING.md`
- `/Users/robin/IdeaProjects/harness/.github/ISSUE_TEMPLATE/{bug_report,feature_request,question,config}.yml`
- `/Users/robin/IdeaProjects/harness/.github/PULL_REQUEST_TEMPLATE.md`
- `/Users/robin/IdeaProjects/harness/docs/experimental-dependency.md`
- `/Users/robin/IdeaProjects/harness/docs/quickstart.md`
- `/Users/robin/IdeaProjects/harness/docs/show-hn-launch-kit.md`
- `/Users/robin/IdeaProjects/harness/_workspace/release/audit-2026-04-18.md`
- `/Users/robin/IdeaProjects/harness/_workspace/community/issue-{2,3}-reply.md`

감사 커맨드 로그: `git status`, `git diff --stat`, `git diff .claude-plugin/plugin.json`, `git show HEAD:README.md`, 각 파일 Read 도구 호출.
