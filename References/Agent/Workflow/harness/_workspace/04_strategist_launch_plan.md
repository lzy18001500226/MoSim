# GitHub Trending 통합 런치 플랜 — Harness

> **프로젝트**: Harness — Agent Team & Skill Architect (Claude Code Plugin)
> **GitHub**: https://github.com/revfactory/harness
> **작성일**: 2026-03-29
> **런치 목표일**: 2026-04-07 (화요일)
> **작성 기반**: repo-auditor, content-creator, community-scout 산출물 종합

---

## 1. 전략 요약

### 목표
- **Primary**: GitHub Trending (All Languages) Top 25 진입
- **Secondary**: GitHub Trending (Markdown / Misc) #1 진입
- **Stretch**: Hacker News Front Page 12시간+ 유지

### 타겟 카테고리
- GitHub Trending: `All Languages` + `Unknown languages` (Markdown 기반이므로 언어 분류가 Unknown/Misc로 잡힐 가능성 높음)
- Hacker News: `Show HN`
- Product Hunt: `AI Coding Agents` / `Developer Tools`

### 핵심 KPI

| 지표 | D-Day +6h | D-Day +24h | D+3 | D+7 | D+14 |
|------|-----------|------------|-----|-----|------|
| GitHub Stars | 100+ | 300+ | 500+ | 800+ | 1,200+ |
| Star Velocity (stars/h) | 15-20 | 10-15 | 5-8 | 3-5 | 2-3 |
| Forks | 10+ | 30+ | 50+ | 80+ | 120+ |
| HN Points | 50+ | 100+ | — | — | — |
| Twitter Impressions | 10k+ | 50k+ | 100k+ | — | — |

### 런치일 선정 근거
- **화요일 (2026-04-07)** 선정
  - 화~목이 GitHub Trending 진입 최적 요일 (주말 트래픽 하락 전 모멘텀 확보)
  - 월요일 제외: 주초 업무 과부하로 개발자 관심 분산
  - HN 최적 게시 시간대와 화요일이 가장 잘 맞음
  - D-7 = 3/31(화), 준비 기간이 평일 중심이라 작업 효율 높음

---

## 2. D-7 ~ D-1: Pre-Launch Prep

### D-7 (3/31 화) — Repo 핵심 최적화

| # | 액션 | 근거 | 완료 기준 | 시간 |
|---|------|------|-----------|------|
| 1 | **GitHub Releases 생성** (v1.0.0, v1.0.1) | Audit R4 — 사이드바 신뢰 신호, 최고 ROI | Release 페이지에 2개 릴리스 노출, CHANGELOG 내용 포함 | 30분 |
| 2 | **GitHub Topics 설정** | Audit R9 — 검색/Explore 노출 핵심 | `claude-code`, `claude-code-plugin`, `agent-team`, `ai-agent`, `llm`, `skill-generation`, `orchestration`, `claude` 설정 완료 | 10분 |
| 3 | **Repo Description 설정** | Audit R13 — 검색 결과 노출 최적화 | "Agent Team & Skill Architect — A Claude Code Plugin that designs domain-specific agent teams and generates skills" | 5분 |
| 4 | **Social Preview 이미지 업로드** | Audit R14 — SNS 공유 시 시각적 임팩트 | 1280×640px OG 이미지 업로드 완료 | 30분 |
| 5 | **GitHub Pages 배포** | Audit R12 — 랜딩페이지 라이브 + 신뢰 신호 | `revfactory.github.io/harness` 접속 가능 | 20분 |
| 6 | **Repo About에 웹사이트 URL 설정** | Audit R15 | Pages URL 연결 | 5분 |

**D-7 소요 시간**: ~2시간
**D-7 효과**: Score 5.5 → 7.0 (Discoverability 대폭 개선)

### D-6 (4/1 수) — 커뮤니티 인프라

| # | 액션 | 근거 | 완료 기준 | 시간 |
|---|------|------|-----------|------|
| 7 | **Issue Templates 추가** (`bug_report.yml`, `feature_request.yml`) | Audit R5 | `.github/ISSUE_TEMPLATE/` 에 2개 파일 | 30분 |
| 8 | **PR Template 추가** | Audit R6 | `.github/PULL_REQUEST_TEMPLATE.md` 생성 | 15분 |
| 9 | **CONTRIBUTING.md 작성** | Audit R7 — 신규 방문자 기여 유도 핵심 | 버그 리포트, PR 가이드, 개발 환경 섹션 포함 | 30분 |
| 10 | **CODE_OF_CONDUCT.md 추가** | Audit R8 | Contributor Covenant 템플릿 적용 | 10분 |
| 11 | **README "Quick Start" 섹션 리네이밍** | Audit R2 | 설치 섹션 → "Quick Start" (≤5 단계, 첫 단계 원라이너) | 15분 |
| 12 | **README "Contributing" 섹션 추가** | Audit R3 | CONTRIBUTING.md 링크 포함 | 10분 |

**D-6 소요 시간**: ~2시간
**D-6 효과**: Score 7.0 → 7.5 (Repo Structure 대폭 개선)

### D-5 (4/2 목) — 신뢰 신호 & CI

| # | 액션 | 근거 | 완료 기준 | 시간 |
|---|------|------|-----------|------|
| 13 | **GitHub Actions CI 워크플로우 추가** | Audit R10 — 녹색 CI 배지는 강력한 신뢰 신호 | Markdown lint + plugin.json 검증 + 배지 README에 추가 | 1시간 |
| 14 | **기본 유효성 검증 테스트 추가** | Audit R11 | plugin.json 스키마 검증, SKILL.md 존재 확인, references 디렉토리 검증 | 1시간 |

**D-5 소요 시간**: ~2시간
**D-5 효과**: Score 7.5 → 8.0 (Trust Signals 크게 개선)

### D-4 (4/3 금) — 콘텐츠 준비 & 사전 관계 구축

| # | 액션 | 분류 | 완료 기준 | 시간 |
|---|------|------|-----------|------|
| 15 | **데모 GIF/Screencast 제작** | Audit R1 — 3초 판단에 결정적 | "build a harness" 실행 → 에이전트 팀 생성 과정 30-60초 GIF | 2시간 |
| 16 | **데모 GIF를 README 상단에 배치** | | 태그라인 바로 아래 | 15분 |
| 17 | **Twitter/X 스레드용 이미지 3-4장 준비** | Content #3 | 워크플로우 다이어그램, A/B 결과 차트, 아키텍처 패턴 카드 | 1시간 |
| 18 | **모든 콘텐츠 텍스트 최종 검수** | | HN/Reddit/Twitter/Dev.to 초안 문법 + 링크 확인 | 30분 |
| 19 | **Product Hunt 헌터 섭외 시작** | Scout — PH 런치 필수 | 2-3명 헌터에게 DM, 런치 예정일 공유 | 30분 |
| 20 | **인플루언서 사전 DM** | Scout Tier 1 KOL | Nick Saraev, Boris Cherny에게 사전 소개 메시지 | 30분 |

**D-4 소요 시간**: ~5시간 (가장 작업량 많은 날)

### D-3 ~ D-2 (4/4~4/5 토~일) — 최종 점검 & 서포터 준비

| # | 액션 | 완료 기준 | 시간 |
|---|------|-----------|------|
| 21 | **harness-100 repo 공개 확인** | README 정리, 링크 정상 작동 | 30분 |
| 22 | **claude-code-harness (연구 repo) 공개 확인** | A/B 테스트 데이터/논문 접근 가능 | 30분 |
| 23 | **초기 서포터 그룹 구성** | 동료/지인 5-10명에게 런치일 star/upvote 협조 요청. 타임존 고려하여 KST 저녁~밤 시간대 참여 가능 인원 확보 | 1시간 |
| 24 | **HN 예상 질문 답변 사전 준비** | 방법론 한계, 다른 도구와 비교, 일반화 가능성 등 5-7개 Q&A 초안 | 1시간 |
| 25 | **Anthropic Discord 계정 활동 확인** | #showcase 채널 접근 가능 여부 확인 | 15분 |

### D-1 (4/6 월) — 최종 리허설

| # | 액션 | 완료 기준 | 시간 |
|---|------|-----------|------|
| 26 | **전체 체크리스트 최종 확인** (Section 8 참조) | 모든 Pre-Launch 항목 체크 | 30분 |
| 27 | **GitHub Pages 라이브 최종 확인** | 랜딩페이지 접속 + 다국어 토글 동작 | 10분 |
| 28 | **각 플랫폼 게시 텍스트를 텍스트 에디터에 복사** | 복붙 준비 완료 (서식 깨짐 방지) | 20분 |
| 29 | **Twitter 프로필 바이오 업데이트** | Harness 언급 추가 | 5분 |
| 30 | **알람 설정** | D-Day 기상 알람 (KST 16:00 = UTC 07:00) | 5분 |

---

## 3. D-Day: Launch Execution (4/7 화)

### 시간대 전략

핵심 원리: **미국 아침 (UTC 13:00-16:00 = PST 6-9am = EST 9am-12pm)에 HN/Reddit 트래픽이 피크**. 하지만 HN은 **몇 시간 일찍 게시해야 Front Page 도달 시점이 피크와 맞음**. KST 기준 저녁~밤 시간대.

| 시간 (UTC) | 시간 (KST) | 플랫폼 | 액션 | 예상 효과 | Plan B |
|-----------|-----------|--------|------|-----------|--------|
| **07:00** | **16:00** | GitHub | 최종 README 확인, demo GIF 작동 확인 | 기본 점검 | — |
| **08:00** | **17:00** | **Hacker News** | Show HN 포스트 게시 (Content #1 텍스트) | HN New → Rising. 초기 2-3 upvote로 Rising 진입 | 게시 타이밍이 안 맞으면 UTC 12:00에 재게시 (HN은 재게시 허용) |
| **08:15** | **17:15** | **초기 서포터** | 서포터 그룹에 HN 링크 + GitHub 링크 공유 | 초기 5-10 stars + 2-3 HN upvotes (임계 모멘텀) | 서포터 부족 시 개인 네트워크 추가 동원 |
| **08:30** | **17:30** | **Twitter/X** | 런치 스레드 게시 (Content #3, Tweet 1-9). Tweet 1 핀 고정 | 팔로워 초기 engagement, 리트윗 확산 | 스레드 engagement 낮으면 핵심 트윗만 단독 재게시 |
| **09:00** | **18:00** | **r/ClaudeAI** | Reddit 포스트 게시 (Content #2a) | 가장 receptive한 타겟 커뮤니티. 50+ upvotes 목표 | 포스트 삭제 시 모더레이터에 문의 후 톤 조정하여 재게시 |
| **09:00** | **18:00** | **r/SideProject** | Reddit 포스트 게시 (Scout Reddit 템플릿 D) | 자기홍보 허용 커뮤니티, 안전한 초기 traction | — |
| **09:30** | **18:30** | **r/opensource** | Reddit 포스트 게시 | 오픈소스 커뮤니티 노출 | — |
| **10:00** | **19:00** | **r/programming** | Reddit 포스트 게시 (Content #2c) | 넓은 개발자 오디언스. 스팸 플래그 방지를 위해 1시간 간격 | 삭제 시 기술적 가치 강조한 버전으로 재작성 |
| **10:00** | **19:00** | **Product Hunt** | PH 런치 (헌터 or 직접) — "AI Coding Agents" 카테고리 | PH Daily Top 5 목표 | 헌터 미확보 시 직접 런치, Maker comment 즉시 작성 |
| **10:30** | **19:30** | **Anthropic Discord** | #showcase 채널에 프로젝트 공유 | Claude 커뮤니티 직접 도달 | #community-projects 대안 채널 |
| **12:00** | **21:00** | **Dev.to** | 기술 블로그 포스트 게시 (Content #4) | 장기 SEO, 검색 유입 | — |
| **12:00** | **21:00** | **HN 모니터링** | Front Page 진입 여부 확인. 댓글 응답 시작 | 댓글 engagement가 HN 순위 핵심 | Front Page 미진입 시 → Reddit/Twitter에 집중 |
| **13:00-18:00** | **22:00-03:00** | **전 플랫폼** | 실시간 모니터링 + 댓글 응답 (아래 상세) | 미국 피크 시간대, 가장 중요한 6시간 | 피로 시 핵심 플랫폼(HN + r/ClaudeAI)만 집중 |
| **14:00** | **23:00** | **Awesome Lists Tier 1** | awesome-claude-code (hesreallyhim) 이슈 제출 + jqueryscript PR + awesome-claude-skills PR 2건 | 트렌딩 진입과 동시에 PR → 승인 확률 극대화 | — |

### 실시간 모니터링 지표 & 임계값

| 지표 | 체크 주기 | 녹색 (정상) | 황색 (주의) | 적색 (긴급) |
|------|----------|------------|------------|------------|
| Star velocity | 30분 | >10 stars/h | 5-10 stars/h | <5 stars/h |
| HN rank | 30분 | Front Page (1-30) | Page 2 (31-60) | Page 3+ |
| HN comments | 1시간 | 5+ comments/h | 2-4 comments/h | <2 comments/h |
| Reddit upvotes (r/ClaudeAI) | 1시간 | 50+ | 20-50 | <20 |
| Twitter thread impressions | 2시간 | 5k+ | 1-5k | <1k |

### 긴급 대응 시나리오 (Plan B)

| 시나리오 | 트리거 | 즉시 대응 |
|---------|--------|----------|
| HN 게시 후 3시간 내 Front Page 미진입 | Points < 10 at UTC 11:00 | Reddit/Twitter에 집중. HN은 다음 날 재게시 고려 |
| Reddit 포스트 삭제됨 | 모더레이터 제거 알림 | 해당 서브레딧 규칙 재확인 → 톤 수정 후 모드메일로 재승인 요청 |
| Star velocity < 5/h (전 채널) | D-Day +6h 시점 | 인플루언서 긴급 DM (Nick Saraev, Boris Cherny) + 서포터 2차 동원 |
| 부정적 댓글 다수 | 비판 댓글 3+ | 즉시 정중하게 응답. 기술적 한계 인정 + 로드맵 공유. 절대 방어적 태도 금지 |

---

## 4. D+1 ~ D+3: Amplification

### D+1 (4/8 수)

| 시간 (UTC) | 액션 | 플랫폼 | 트리거 조건 |
|-----------|------|--------|------------|
| 08:00 | **r/MachineLearning 포스트** (Content #2b — 연구 중심) | Reddit | 무조건 실행 |
| 10:00 | **Twitter Quote-tweet**: "연구 결과가 가장 놀라웠던 부분..." — scaling insight 강조 | Twitter/X | 무조건 실행 |
| 10:00 | **Ben's Bites 커뮤니티 투표 제출** | Newsletter | 무조건 실행 |
| 12:00 | **Anthropic Discord 후속 포스트** — 커뮤니티 반응 공유 | Discord | Stars 100+ 달성 시 |
| 14:00 | **HN 댓글 심층 응답** — 기술적 질문에 상세 답변 | HN | HN Front Page 유지 중일 때 |
| Ongoing | **모든 GitHub Issues에 24시간 내 응답** | GitHub | 이슈 접수 시 |

### D+2 (4/9 목)

| 시간 (UTC) | 액션 | 플랫폼 | 트리거 조건 |
|-----------|------|--------|------------|
| 08:00 | **TLDR AI / TLDR Open Source 편집팀 접촉** | Email | Stars 200+ 시 피치 강화 |
| 10:00 | **The Rundown AI 편집팀 접촉** | Email | 무조건 실행 |
| 10:00 | **Console.dev 제출** | Web | 무조건 실행 |
| 12:00 | **r/LocalLLaMA 크로스 포스트** (기술 심층 버전) | Reddit | r/ClaudeAI 반응 긍정적일 때 |
| 14:00 | **r/artificial 포스트** | Reddit | 무조건 실행 |

### D+3 (4/10 금)

| 시간 (UTC) | 액션 | 플랫폼 | 트리거 조건 |
|-----------|------|--------|------------|
| 08:00 | **Twitter: "100 harnesses" 독립 포스트** — companion repo 소개 | Twitter/X | 무조건 실행 |
| 10:00 | **Changelog Weekly 제출** | Newsletter | 무조건 실행 |
| 12:00 | **AI Tool Report 제출** | Newsletter | 무조건 실행 |
| 14:00 | **Star History에 프로젝트 등록** + 스타 그래프 README 임베드 | GitHub/Web | Stars 300+ 시 그래프가 인상적 |
| Ongoing | **마일스톤 트윗**: "Launched 3 days ago → X stars" | Twitter/X | Stars 500+ 달성 시 |

---

## 5. D+4 ~ D+14: Sustain

### D+4 ~ D+7 (4/11~4/14)

| 날짜 | 액션 | 플랫폼 |
|------|------|--------|
| D+4 (토) | **Awesome Lists Tier 2 PR 제출**: awesome-llm-agents, awesome-agents, awesome-ai-agents, awesome-ai-agents-2026, Awesome-Prompt-Engineering | GitHub |
| D+5 (일) | **Dev.to 후속 아티클**: "5 Architecture Patterns for AI Agent Teams" (에버그린 콘텐츠) | Dev.to |
| D+5 | **YouTube 크리에이터 접촉**: Nick Saraev (최우선), Sabrina Ramonov, freeCodeCamp | Email/DM |
| D+6 (월) | **Trendshift 뱃지 확인 및 README 임베드** | GitHub |
| D+7 (화) | **주간 마일스톤 트윗**: "Week 1: X stars, Y forks, Z countries" + Star History 그래프 | Twitter/X |
| D+7 | **awesomeclaude.ai 등록** | Web |

### D+8 ~ D+14 (4/15~4/21)

| 날짜 | 액션 | 플랫폼 |
|------|------|--------|
| D+8~10 | **Awesome Lists Tier 3 PR 제출**: jim-schwoebel, webfuse-com, BehiSecc, alvinunreal | GitHub |
| D+10 | **Superhuman AI, The Neuron 뉴스레터 접촉** | Email |
| D+10 | **r/MachineLearning 프로젝트 쇼케이스 후속** (실사용 사례 + 커뮤니티 피드백 반영) | Reddit |
| D+12 | **Twitter: 사용자 피드백 하이라이트 스레드** — "Here's what people are building with Harness" | Twitter/X |
| D+14 | **2주 마일스톤 트윗** + 로드맵 공유 (다음 버전 계획) | Twitter/X |
| Ongoing | **모든 GitHub Issues/PR에 48시간 내 응답 유지** | GitHub |
| Ongoing | **Twitter 멘션/인용 모두에 응답** | Twitter/X |

### 장기 커뮤니티 유지 원칙

1. **이슈 응답 24-48시간 규칙**: Trending 이후 신규 방문자가 첫 이슈를 열었을 때 빠른 응답이 커뮤니티 형성의 핵심
2. **"Good First Issue" 라벨링**: 간단한 기여 기회를 의도적으로 만들어 컨트리뷰터 유입
3. **CHANGELOG 지속 업데이트**: 릴리스마다 상세 노트로 활발한 프로젝트 인상
4. **월간 업데이트 포스트**: 진행 상황을 r/ClaudeAI + Twitter에 공유

---

## 6. 성공 지표

### Star Velocity 목표 (시간대별)

| 시점 | 누적 Stars | Velocity (stars/h) | Trending 임계 기준 |
|------|-----------|-------------------|-------------------|
| D-Day +2h | 20-30 | 10-15 | 진입 시작 |
| D-Day +6h | 80-120 | 15-20 | Daily Trending 후보 |
| D-Day +12h | 150-200 | 10-15 | Daily Trending 진입 |
| D-Day +24h | 250-350 | 8-12 | Daily Trending 안정 |
| D+2 | 400-500 | 5-8 | Weekly Trending 후보 |
| D+3 | 500-600 | 4-6 | Weekly Trending 진입 |
| D+7 | 700-900 | 2-4 | Weekly Trending 유지 |
| D+14 | 1,000-1,500 | 1-3 | Monthly Trending |

### 종합 성공 지표

| 지표 | D-Day | D+3 | D+7 | D+14 | 비고 |
|------|-------|-----|-----|------|------|
| **GitHub Stars** | 300+ | 500+ | 800+ | 1,200+ | 핵심 지표 |
| **GitHub Forks** | 30+ | 50+ | 80+ | 120+ | 실사용 proxy |
| **GitHub Trending 순위** | Top 50 | Top 25 | Top 25 유지 또는 재진입 | — | Primary 목표 |
| **HN Points** | 100+ | — | — | — | Front Page = ~50+ points |
| **HN Comments** | 30+ | — | — | — | Engagement depth |
| **Product Hunt Rank** | Top 10 | — | — | — | Daily rank |
| **Reddit Total Upvotes** | 200+ | 400+ | — | — | 전 서브레딧 합산 |
| **Twitter Impressions** | 50k+ | 100k+ | 150k+ | — | 스레드 + 멘션 |
| **Awesome List PRs Merged** | 2+ | 4+ | 6+ | 8+ | 장기 발견성 |
| **GitHub Issues Opened** | 5+ | 10+ | 20+ | 30+ | 커뮤니티 건강 지표 |
| **Contributors** | 1 | 2+ | 3+ | 5+ | 커뮤니티 형성 |

---

## 7. 리스크 & 완화

| # | 리스크 | 확률 | 영향 | 완화 전략 |
|---|--------|------|------|-----------|
| 1 | **HN 무관심** — Show HN이 Front Page 진입 실패 | 중 | 높음 | HN은 도박적 요소가 있음. 실패 시 Reddit/Twitter에 화력 집중. D+2~3에 재게시 고려. "Ask HN: What are you working on?" 월간 스레드에도 참여 |
| 2 | **Reddit 자기홍보 삭제** — 모더레이터가 포스트 제거 | 중 | 중 | 각 서브레딧에 맞는 톤으로 차별화 (r/ClaudeAI는 사용 사례, r/programming은 기술 가치, r/MachineLearning은 연구). 포스트 히스토리에 해당 서브레딧 참여 이력 있으면 유리 → 런치 전 1주 동안 해당 서브레딧에 일반 참여 |
| 3 | **Star velocity 부족** — Trending 임계점 미도달 (D-Day +12h에 < 100 stars) | 중 | 높음 | Plan B: 인플루언서 긴급 DM + 서포터 2차 동원 + 아시아 시간대 (한국/일본) 커뮤니티 추가 활용. 일본어 README가 이미 있으므로 일본 개발자 커뮤니티(Zenn, Qiita)에 일본어 포스트 |
| 4 | **부정적 기술 피드백** — "그냥 프롬프트 아닌가?", "A/B 테스트 방법론 의심" | 중 | 중 | 사전 준비한 Q&A로 정중하고 기술적으로 응답. 한계를 솔직히 인정하되 실제 결과 데이터로 뒷받침. "You're right that X is a limitation — here's what we're working on for v2" |
| 5 | **Product Hunt 저조** — Daily Top 10 미진입 | 중 | 낮음 | PH는 보조 채널. 저조해도 GitHub Trending에 직접 영향 없음. PH보다 HN/Reddit에 에너지 집중 |
| 6 | **경쟁 프로젝트 동시 런치** — 같은 날 비슷한 AI agent 도구가 Trending에 진입 | 낮 | 중 | Harness의 차별점(meta-skill, A/B 연구 결과, 100개 프리빌트)을 강조. 경쟁 프로젝트와의 차이를 명확히 설명하는 댓글 준비 |
| 7 | **저자 시간대 불리** — KST와 미국 피크 시간대의 12-14시간 차이로 실시간 대응 지연 | 높 | 중 | D-Day 저녁~새벽까지 집중 모니터링 계획 (KST 17:00 ~ 03:00 = UTC 08:00 ~ 18:00). D+1은 오전부터 댓글 응답 catch-up. 수면 전에 "I'll respond to all questions in the morning" 댓글 하나 남기기 |
| 8 | **GitHub 서비스 장애** — 런치 당일 GitHub 다운/느림 | 낮 | 높음 | githubstatus.com 사전 모니터링. 장애 시 런치를 다음 날로 연기. 콘텐츠는 준비되어 있으므로 재활용 가능 |

---

## 8. 최종 체크리스트

### Pre-Launch (D-1까지 완료)

**Repo 최적화**
- [ ] GitHub Releases v1.0.0, v1.0.1 생성
- [ ] GitHub Topics 8개 설정
- [ ] Repo Description 설정
- [ ] Social Preview 이미지 (1280×640) 업로드
- [ ] GitHub Pages 배포 + About에 URL 설정
- [ ] Issue Templates (bug_report.yml, feature_request.yml) 추가
- [ ] PR Template 추가
- [ ] CONTRIBUTING.md 작성
- [ ] CODE_OF_CONDUCT.md 추가
- [ ] CI 워크플로우 + 녹색 배지 추가
- [ ] 유효성 검증 테스트 추가
- [ ] README "Quick Start" 섹션 리네이밍
- [ ] README "Contributing" 섹션 추가
- [ ] 데모 GIF 제작 + README 상단 배치

**콘텐츠**
- [ ] HN Show HN 텍스트 최종본 준비
- [ ] Reddit 포스트 4종 (r/ClaudeAI, r/programming, r/SideProject, r/opensource) 최종본
- [ ] Twitter/X 스레드 9개 트윗 + 이미지 3-4장 준비
- [ ] Dev.to 아티클 최종본
- [ ] Product Hunt 런치 페이지 초안 (tagline, description, images)
- [ ] 모든 콘텐츠 링크 정상 작동 확인

**아웃리치**
- [ ] Product Hunt 헌터 확보 (또는 직접 런치 결정)
- [ ] Nick Saraev, Boris Cherny 사전 DM 발송
- [ ] 초기 서포터 5-10명 확보 + D-Day 참여 확인
- [ ] HN 예상 질문 Q&A 5-7개 초안 완료
- [ ] Anthropic Discord 접근 확인

**Repo 연동**
- [ ] harness-100 repo 공개 + README 정리
- [ ] claude-code-harness (연구 repo) 공개
- [ ] 3개 repo 간 크로스 링크 정상 확인
- [ ] Twitter 프로필 바이오 업데이트

### D-Day (4/7 화)

**게시 순서**
- [ ] UTC 08:00 — HN Show HN 게시
- [ ] UTC 08:15 — 서포터 그룹에 링크 공유
- [ ] UTC 08:30 — Twitter/X 스레드 게시 + 핀 고정
- [ ] UTC 09:00 — r/ClaudeAI + r/SideProject 게시
- [ ] UTC 09:30 — r/opensource 게시
- [ ] UTC 10:00 — r/programming + Product Hunt 게시
- [ ] UTC 10:30 — Anthropic Discord #showcase 게시
- [ ] UTC 12:00 — Dev.to 아티클 게시
- [ ] UTC 14:00 — Awesome Lists Tier 1 PR/이슈 제출 (4건)

**모니터링**
- [ ] Star velocity 30분마다 체크
- [ ] HN rank 30분마다 체크
- [ ] Reddit upvotes 1시간마다 체크
- [ ] 모든 댓글에 1시간 내 응답
- [ ] GitHub Issues에 즉시 응답

### Post-Launch (D+1 ~ D+14)

- [ ] D+1: r/MachineLearning 포스트 + Twitter QT + Ben's Bites 제출
- [ ] D+2: TLDR/Rundown/Console.dev 접촉
- [ ] D+3: "100 harnesses" 독립 포스트 + Changelog 제출 + Star History 등록
- [ ] D+4: Awesome Lists Tier 2 PR 5건
- [ ] D+5: Dev.to 후속 아티클 + YouTube 크리에이터 접촉
- [ ] D+7: 주간 마일스톤 트윗
- [ ] D+8~10: Awesome Lists Tier 3 PR 4건 + 뉴스레터 Tier 3 접촉
- [ ] D+14: 2주 마일스톤 + 로드맵 공유

---

## 연쇄 효과 (Cascade) 설계

```
D-Day 08:00  HN Show HN ──────────────┐
D-Day 08:30  Twitter Thread ────────────┤
D-Day 09:00  Reddit (r/ClaudeAI) ───────┤
D-Day 10:00  Product Hunt ──────────────┤
                                        ▼
                              초기 Star Velocity
                              (30-50 stars in 3h)
                                        │
                                        ▼
                              GitHub Trending 알고리즘 감지
                              (Daily Trending 후보)
                                        │
                          ┌─────────────┼─────────────┐
                          ▼             ▼             ▼
                    Trendshift       Alpha Signal   GitNews
                    자동 수집        자동 트래킹    자동 수집
                          │             │             │
                          ▼             ▼             ▼
                    2차 트래픽 유입 → Star Velocity 가속
                                        │
                                        ▼
                              GitHub Trending 안정 진입
                              (Top 25)
                                        │
                          ┌─────────────┼─────────────┐
                          ▼             ▼             ▼
                    TLDR AI 픽업    뉴스레터 피처  Awesome List
                    (D+2~3)        (D+3~7)       PR 승인 촉진
                          │             │             │
                          ▼             ▼             ▼
                    3차 트래픽 → 장기 발견성 확보 → 1,000+ Stars
```

**핵심**: 각 단계가 다음 단계의 트리거 역할. 초기 24시간의 Star velocity가 전체 연쇄 반응의 점화 조건.

---

## 실행 요약

| 단계 | 기간 | 핵심 목표 | 성공 기준 |
|------|------|----------|----------|
| **Pre-Launch** | D-7 ~ D-1 | Repo Score 5.5 → 8.0 | 체크리스트 100% 완료 |
| **Launch** | D-Day | Star velocity > 10/h 달성 | 24h 내 300+ stars |
| **Amplification** | D+1 ~ D+3 | Trending 진입 + 2차 확산 | Top 25 진입 + 500+ stars |
| **Sustain** | D+4 ~ D+14 | 장기 발견성 확보 | 1,200+ stars + Awesome List 8+ merged |

> **최종 목표**: Harness를 "Claude Code Plugin의 대표 사례"로 포지셔닝하고, GitHub Trending을 통해 글로벌 AI 개발자 커뮤니티에 인지도를 확보한다.
