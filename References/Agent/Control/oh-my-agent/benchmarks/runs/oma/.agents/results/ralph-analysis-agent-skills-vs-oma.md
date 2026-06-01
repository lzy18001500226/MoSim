# Adversarial Competitive Analysis: agent-skills vs oh-my-agent

**Date**: 2026-04-09
**Scope**: SWOT, Porter's 5 Forces, Feature Gap Analysis
**Perspective**: Adversarial reviewer (worst-case assumptions for oma)

---

## Part 1: Structural Comparison

| Dimension | agent-skills (Osmani) | oh-my-agent (oma) |
|-----------|----------------------|-------------------|
| **Nature** | Static content library (markdown) | Runtime framework + CLI + hooks |
| **Skills** | 19 lifecycle workflow skills | 19 domain-specialized skills + shared |
| **Hooks** | 2 (session-start, simplify-ignore) | 4 core hooks x 4 vendors |
| **HUD** | None | [OMA] statusline (model, ctx%, cost, rate, workflow) |
| **Workflows** | 7 slash commands (single invocation) | 13 workflows (persistent loops, gating) |
| **Multi-agent** | 3 static personas (no orchestration) | 8 subagents + parallel spawn + review loops |
| **Configuration** | None | oma-config.yaml + mcp.json + settings.json |
| **Installation** | git clone / plugin marketplace / copy | `bunx oh-my-agent@latest` (interactive CLI) |
| **State** | None | `.agents/state/` + `.agents/results/` |
| **Platform** | 7+ (Claude, Cursor, Gemini, Windsurf, Copilot, OpenCode, generic) | 6 (Claude, Codex, Gemini, Qwen, Antigravity, OpenCode) |
| **Stars** | 9,274 | < 500 (estimate) |
| **Philosophy** | "Portable best practices" | "Full orchestration engine" |

---

## Part 2: SWOT Analysis (oma 관점)

### Strengths (강점)

| # | Strength | Evidence |
|---|----------|----------|
| S1 | **Runtime orchestration 독보적 우위** | ultrawork 5-phase gate loop, ralph self-referential loop — agent-skills에는 workflow state 자체가 없음 |
| S2 | **Multi-agent 병렬 실행** | 8 subagent x 3 parallel spawn, 3-tier review (self-check + verify + QA cross-review). agent-skills의 "agents"는 static persona markdown일 뿐 |
| S3 | **HUD/Observability** | [OMA] statusline: model, context%, cost, rate limits, lines changed, active workflow. agent-skills는 관찰 도구 zero |
| S4 | **Persistent workflow state** | `.agents/state/{workflow}-state-{sessionId}.json`으로 세션 중단/재개 가능. agent-skills는 세션 간 상태 없음 |
| S5 | **Multi-vendor adaptation** | 단일 코드베이스에서 Claude/Codex/Gemini/Qwen 자동 감지 + 훅 변환. agent-skills는 vendor별 별도 가이드 문서만 제공 |
| S6 | **Quality gate enforcement** | PLAN_GATE → IMPL_GATE → VERIFY_GATE → REFINE_GATE → SHIP_GATE 강제. agent-skills는 lifecycle이 "advisory" only |
| S7 | **Context budget 관리** | context-loading.md로 task type별 필요 리소스만 선택적 로딩. agent-skills는 전체 SKILL.md를 통째로 로딩 |
| S8 | **CLI 도구 생태계** | `oma doctor`, `oma dashboard`, `oma verify`, `oma retro` 등 40+ subcommands. agent-skills는 CLI 없음 |

### Weaknesses (약점)

| # | Weakness | Impact |
|---|----------|--------|
| W1 | **Platform 종속성** | Claude Code에 가장 최적화됨 — Agent tool, slash commands, statusLine API 등이 Claude 전용. Cursor/Windsurf/Copilot 지원 없음 |
| W2 | **설치 복잡도** | Interactive CLI, preset 선택, vendor 선택, hook 설치 등 5+ 단계. agent-skills는 `git clone` 한 줄 |
| W3 | **콘텐츠 깊이 부족** | oma의 SKILL.md는 "how to execute"에 집중 — agent-skills의 "Common Rationalizations", "Red Flags", "Anti-Patterns" 같은 교육적 콘텐츠 부재 |
| W4 | **커뮤니티 규모** | Stars < 500 vs 9,274. 기여자 수, 포크 수 모두 열세. Addy Osmani의 브랜드 파워 대비 불리 |
| W5 | **진입 장벽** | 19 skills + 13 workflows + 8 agents + shared/conditional/runtime 리소스 체계가 신규 사용자에게 압도적 |
| W6 | **Markdown 생태계 비호환** | `.agents/` SSOT 모델은 oma 전용 — 다른 framework의 skill을 가져오기 어렵고, oma skill을 외부에서 쓸 수도 없음 |
| W7 | **MCP 의존도** | Serena MCP memory가 없으면 핵심 기능(progress tracking, memory protocol) 동작 불가 — 추가 설정 부담 |
| W8 | **Bun 런타임 의존** | Hook scripts가 Bun TypeScript 직접 실행 — Node.js만 있는 환경에서는 추가 설치 필요 |

### Opportunities (기회)

| # | Opportunity | Strategy |
|---|-------------|----------|
| O1 | **Skill content 통합** | agent-skills의 고품질 콘텐츠를 oma skill 포맷으로 어댑터 제공. "Best of both worlds" |
| O2 | **Plugin marketplace 표준** | Claude Code plugin marketplace 등장 — oma를 plugin으로 배포하면 설치 장벽 제거 |
| O3 | **Cursor/Windsurf 확장** | IDE 시장 50%+ 점유. `.cursor/rules/`와 `.windsurfrules` 어댑터만 추가하면 시장 확대 |
| O4 | **Vercel `skills` CLI 호환** | `npx skills add` 표준에 oma skill을 등록하면 별도 CLI 없이 배포 가능 |
| O5 | **Enterprise workflow 차별화** | agent-skills에 없는 기능: 감사 추적(session-metrics), 품질 점수(quality-score), 실험 기록(experiment-ledger) → 엔터프라이즈 소구 |
| O6 | **AI agent 표준 선점** | Agent Skills 포맷이 de facto standard가 되기 전에 oma의 orchestration layer를 표준으로 제안 |
| O7 | **Multi-vendor arbitrage** | 벤더별 agent 최적 배치 (fast tasks → Haiku, complex → Opus) — agent-skills는 단일 모델 전제 |

### Threats (위협)

| # | Threat | Severity |
|---|--------|----------|
| T1 | **Commoditization** | Agent skills 포맷이 표준화되면 oma의 "skill content" 가치 하락 — runtime만으로 차별화 필요 | HIGH |
| T2 | **Platform absorption** | Claude Code / Gemini가 자체 orchestration 내장하면 oma의 존재 이유 약화 | CRITICAL |
| T3 | **Network effect** | agent-skills 9K+ stars → contributor 유입 → skill 수 폭발 → oma가 콘텐츠에서 추격 불가 | HIGH |
| T4 | **Vercel ecosystem lock-in** | `npx skills add` 표준이 Vercel 생태계에 편입되면 oma의 custom 배포 모델 고립 | MEDIUM |
| T5 | **Simplicity preference** | "Just copy markdown" vs "Install CLI + configure hooks" — 대부분 사용자가 단순한 쪽 선택 | HIGH |
| T6 | **Fork 공격** | agent-skills는 MIT로 fork 가능. Osmani의 skill content + oma의 orchestration = 경쟁자 탄생 가능 | MEDIUM |

---

## Part 3: Porter's 5 Forces Analysis

### Force 1: Threat of New Entrants (신규 진입 위협) — HIGH

| Factor | Assessment |
|--------|-----------|
| **진입 장벽** | 극히 낮음 — markdown 파일 작성만으로 "agent skills" 프로젝트 생성 가능 |
| **자본 요구** | Zero — GitHub repo + README만 필요 |
| **브랜드 효과** | Osmani(Google), Anthropic(공식), Vercel(인프라) 등 대형 브랜드가 이미 진입 |
| **전환 비용** | 극히 낮음 — SKILL.md 파일 복사만으로 전환 가능 |
| **규모의 경제** | 없음 — skill 수는 쉽게 복제 가능 |
| **oma 방어선** | **Runtime layer**가 유일한 moat. Skill content는 방어 불가. Orchestration + state + HUD + multi-agent는 복제 비용 높음 |

**oma 전략**: Runtime + orchestration 고도화에 집중. Content layer는 개방형 표준 수용.

### Force 2: Bargaining Power of Buyers (구매자 교섭력) — HIGH

| Factor | Assessment |
|--------|-----------|
| **가격 민감도** | 전부 무료(MIT) — 가격 경쟁 자체가 불가능 |
| **전환 비용** | agent-skills: zero. oma: hooks + state + config = moderate |
| **정보 비대칭** | 없음 — GitHub stars, README만 보고 선택 |
| **대안 풍부** | awesome-agent-skills 목록에 10+ 프로젝트 |
| **oma 방어선** | Lock-in via state management, session history, quality metrics — 쌓이면 전환 비용 증가 |

**oma 전략**: "쓸수록 가치 증가" 모델 — session-metrics, experiment-ledger, lessons-learned가 축적될수록 이탈 비용 상승.

### Force 3: Bargaining Power of Suppliers (공급자 교섭력) — CRITICAL

| Factor | Assessment |
|--------|-----------|
| **AI platform 의존** | Claude Code API/hook 시스템이 변경되면 oma 전체 깨짐 |
| **MCP 의존** | Serena MCP 프로젝트가 중단되면 memory protocol 동작 불가 |
| **Bun 의존** | Hook runtime이 Bun 전용 — Bun 정책 변경 시 영향 |
| **agent-skills 비교** | Bash + jq만 사용 — 공급자 의존 거의 zero |

**oma 전략**: Vendor abstraction layer (vendor-detection.md) 이미 존재하나, hook runtime의 Bun 의존성 + MCP 의존성 분산 필요.

### Force 4: Threat of Substitutes (대체재 위협) — HIGH

| Substitute | Threat Level | Reason |
|-----------|-------------|--------|
| **Claude Code 내장 기능** | CRITICAL | `/plan`, `/review` 등 자체 명령어 확장 시 외부 tool 불필요 |
| **Cursor Rules** | HIGH | `.cursorrules` 파일 하나로 대부분의 skill 효과 재현 |
| **GitHub Copilot Workspace** | HIGH | 자체 planning + implementation 파이프라인 내장 |
| **Devin / SWE-agent** | MEDIUM | 완전 자율 코딩 agent — 수동 orchestration 불필요 |
| **IDE 내장 AI** | HIGH | VS Code Copilot Chat, JetBrains AI가 직접 통합 |

**oma 전략**: "Agent orchestration"은 대체 가능하지만, "quality assurance pipeline" (11 review steps, experiment ledger)은 대체 어려움. QA 차별화 강화.

### Force 5: Industry Rivalry (기존 경쟁) — MODERATE-HIGH

| Competitor | Positioning | Overlap with oma |
|-----------|-------------|-----------------|
| **addyosmani/agent-skills** | Content library + Google brand | Skill content 경쟁 |
| **anthropics/skills** | Official reference implementation | 표준 정의 권한 |
| **VoltAgent/awesome-agent-skills** | Curation / directory | 발견성 경쟁 |
| **Aider** | CLI coding assistant | Agent execution 경쟁 |
| **Claude Code 자체** | Platform + runtime | Absorption 위험 |

**경쟁 강도**: Moderate-High. 시장이 아직 초기라 파이 자체가 커지고 있지만, 대형 플레이어(Anthropic, Google, Vercel)가 이미 참여.

---

## Part 4: Adversarial Feature Review — 추가해야 할 기능

### Priority 1: CRITICAL (생존 필수)

| # | Feature | Rationale | Effort |
|---|---------|-----------|--------|
| F1 | **Portable skill format adapter** | agent-skills/anthropic 표준 SKILL.md를 oma format으로 자동 변환. `oma skills:import addyosmani/agent-skills --skill spec-driven-development` | M |
| F2 | **Plugin marketplace 배포** | `.claude-plugin/` manifest 생성 → Claude Code marketplace에서 `oma` 검색으로 설치 가능. 설치 장벽 제거의 핵심 | S |
| F3 | **Cursor/Windsurf adapter** | `.cursor/rules/` 및 `.windsurfrules` export 명령어. IDE 시장 50% 커버리지 확보 | S |

### Priority 2: HIGH (경쟁 우위 확보)

| # | Feature | Rationale | Effort |
|---|---------|-----------|--------|
| F4 | **Anti-rationalization content** | agent-skills의 "Common Rationalizations" + "Red Flags" 패턴을 oma skill에 도입. 교육적 가치 + 실수 방지 | M |
| F5 | **Skill content quality upgrade** | agent-skills의 강점: 각 skill에 "Why this matters", "What good looks like", "What bad looks like" 포함. oma SKILL.md에 추가 | L |
| F6 | **Zero-config mode** | `oma install --zero-config` → preset auto-detection (package.json 기반), hook auto-install, no interactive prompts. agent-skills의 "git clone" 단순성에 대응 | M |
| F7 | **Vercel `skills` CLI 호환** | `skills.json` manifest 생성 → `npx skills add oh-my-agent` 가능. Vercel 생태계 편입 | S |
| F8 | **Node.js fallback runtime** | Hook scripts의 Bun 의존 제거. `tsx` 또는 컴파일된 JS fallback으로 Node.js 환경 지원 | M |

### Priority 3: MEDIUM (차별화 강화)

| # | Feature | Rationale | Effort |
|---|---------|-----------|--------|
| F9 | **Skill dependency graph** | agent-skills에 없는 기능: `oma-backend` → requires `oma-db` 같은 의존성 자동 해석. 조합 실수 방지 | M |
| F10 | **Copilot agent export** | `.github/copilot-instructions.md` + `agents/` 자동 생성. GitHub Copilot 사용자 커버리지 | S |
| F11 | **Session replay** | `oma replay {sessionId}` — 과거 세션의 workflow 진행, 판단, 결과를 재생. Enterprise 감사 추적 | L |
| F12 | **Quality dashboard (web)** | experiment-ledger + session-metrics 시각화. oma dashboard에 quality trend 차트 추가 | L |
| F13 | **Skill marketplace (own)** | `oma skills:publish` / `oma skills:search` — npm-like skill registry. Network effect 구축 | XL |

### Priority 4: LOW (장기 투자)

| # | Feature | Rationale | Effort |
|---|---------|-----------|--------|
| F14 | **OpenCode AGENTS.md generator** | `oma export --format opencode` → AGENTS.md 자동 생성 | S |
| F15 | **Skill A/B testing** | 같은 task에 다른 skill 조합 적용 → quality score 비교. 최적 조합 자동 발견 | XL |
| F16 | **Community skill curation** | awesome-oma-skills 레포 + 자동 호환성 테스트 | L |

### Size Legend: S (1-2d), M (3-5d), L (1-2w), XL (3+w)

---

## Part 5: Adversarial Verdict (적대적 평결)

### agent-skills가 oma를 이기는 시나리오

1. **"Good enough" 승리**: 대부분의 개발자는 full orchestration이 필요하지 않음. `git clone` + SKILL.md 복사로 80%의 가치를 얻으면 oma의 나머지 20%를 위해 복잡한 설치를 감수하지 않음.

2. **Platform absorption**: Claude Code가 agent-skills 스타일 skill을 네이티브로 지원하면 oma의 "skill loading" 가치 소멸. 남는 것은 orchestration뿐이나, Claude Code가 Task tool 기반 자체 orchestration을 강화하면 이마저 위험.

3. **Network effect**: 9K stars → 커뮤니티 기여 → skill 50+개 → "이미 있는 걸 왜 다시 만드나?" → oma skill content 가치 0.

### oma가 agent-skills를 이기는 시나리오

1. **Enterprise adoption**: 품질 게이트, 감사 추적, 실험 기록, 세션 메트릭스 — 엔터프라이즈 팀이 요구하는 "프로세스 보장"을 agent-skills는 제공 불가.

2. **Complex project superiority**: 10+ file 수정, 3+ agent 협업, 반복 리뷰가 필요한 대규모 태스크에서 oma의 orchestration이 압도적. agent-skills는 단일 파일 수정 수준에서만 유효.

3. **Multi-vendor arbitrage**: oma의 `agent_cli_mapping`으로 "frontend는 Gemini, backend는 Claude"같은 최적 배치. agent-skills는 단일 agent 전제.

### 핵심 결론

> **agent-skills는 "what to do"이고, oma는 "how to do it well"이다.**
>
> 두 프로젝트는 스택의 다른 레이어에 있다. 경쟁이 아닌 보완 관계가 가능하다.
> 그러나 agent-skills의 접근성(simple) + 브랜드(Osmani) + 네트워크(9K stars)가
> oma의 기술적 우위를 압도할 수 있는 현실적 위험이 존재한다.
>
> **oma의 생존 전략**: Content layer는 개방(표준 수용), Runtime layer에서 차별화(orchestration, quality, observability).
> F1(skill import) + F2(marketplace) + F3(IDE adapter)를 즉시 실행해야 한다.

---

## Appendix: Competitive Positioning Map

```
                    Runtime Complexity →
                Low                          High
           ┌─────────────────────────────────────┐
    High   │  agent-skills     │                  │
           │  (9K stars)       │     oma          │
  Content  │  anthropics/skills│     (orchestration│
  Quality  │                   │      + quality)   │
           ├───────────────────┼──────────────────┤
    Low    │  awesome-*        │     Aider         │
           │  (curation only)  │     (CLI tool)    │
           └─────────────────────────────────────┘
```

oma는 우측 상단으로 이동해야 함: Content quality를 높이면서 Runtime 강점 유지.
