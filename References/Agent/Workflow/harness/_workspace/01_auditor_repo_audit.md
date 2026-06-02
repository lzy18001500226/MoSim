# Harness — GitHub Trending Readiness Audit

**Date:** 2026-03-29
**Repo:** [revfactory/harness](https://github.com/revfactory/harness)
**Tagline:** Agent Team & Skill Architect — A Claude Code Plugin

---

## Key Strengths

1. **Excellent README structure** — Banner image above fold, 6 badges, multilingual support (EN/KO/JA), clear workflow diagram, architecture pattern tables, and rich use-case prompts. This is already above-average for most trending repos.
2. **Landing page (index.html)** — A polished, dark-themed landing page with multilingual toggle. Many trending repos lack any web presence.
3. **Strong narrative** — The README includes a "Built with Harness" section with quantitative A/B test results (+60% quality improvement, 100% win rate). This kind of evidence is rare and compelling.
4. **Multilingual from day one** — README in 3 languages (EN, KO, JA) with landing page i18n. Expands discoverability across language communities.
5. **Clear plugin structure** — Well-organized `plugin.json`, `SKILL.md`, and references directory. Professional packaging.
6. **CHANGELOG** — Follows Semantic Versioning with detailed entries. Shows active maintenance.
7. **Apache 2.0 License** — Permissive and enterprise-friendly.

---

## Audit Scores

| Category | Score | Notes |
|----------|:-----:|-------|
| 1. README Quality | **8/10** | Strong. Missing: demo GIF/screencast, Quick Start could be more prominent |
| 2. Repo Structure | **4/10** | No issue templates, PR template, CONTRIBUTING.md, CODE_OF_CONDUCT.md, no tags/releases |
| 3. Trust Signals | **3/10** | No CI/CD, no tests, no docs site, no releases |
| 4. Discoverability | **7/10** | Multilingual READMEs, landing page, badges. Missing: GitHub Topics, social preview, SEO description |

**Overall Score: 5.5 / 10**

---

## Detailed Findings & Recommendations

### 1. README Quality (8/10)

| Item | Status | Notes |
|------|--------|-------|
| Tagline | ✅ | "Agent Team & Skill Architect — A Claude Code Plugin" |
| Banner image above fold | ✅ | `harness_banner.png` |
| Badges (3-5) | ✅ | 6 badges including version, license, stars |
| Quick Start (≤5 steps) | ⚠️ | Installation exists but not labeled "Quick Start" |
| Install section | ✅ | Marketplace + direct install |
| Usage examples | ✅ | 8 detailed prompt examples |
| Contributing link | ❌ | No CONTRIBUTING.md or link |
| License | ✅ | Apache 2.0 |
| Demo GIF/screencast | ❌ | No animated demo showing the plugin in action |

#### Recommendations

| # | Recommendation | Impact | Effort |
|---|---------------|--------|--------|
| R1 | **Add a demo GIF/screencast** showing Harness generating an agent team from a single prompt. Place it immediately after the tagline. This is the single highest-impact visual for GitHub Trending — visitors decide in 3 seconds. | **High** | **Medium** |
| R2 | **Rename install section to "Quick Start"** and ensure it's ≤5 numbered steps. First step should be a one-liner copy-paste command. | **Medium** | **Low** |
| R3 | **Add a "Contributing" section** at the bottom of README linking to CONTRIBUTING.md (see R7). | **Medium** | **Low** |

---

### 2. Repo Structure (4/10)

| Item | Status |
|------|--------|
| `.github/ISSUE_TEMPLATE/` | ❌ Missing |
| `.github/PULL_REQUEST_TEMPLATE.md` | ❌ Missing |
| `CONTRIBUTING.md` | ❌ Missing |
| `CODE_OF_CONDUCT.md` | ❌ Missing |
| `.gitignore` | ✅ Present (minimal) |
| Git tags / GitHub Releases | ❌ No tags |
| GitHub Topics | ❌ Not set |
| LICENSE | ✅ Present |
| CHANGELOG.md | ✅ Present |

#### Recommendations

| # | Recommendation | Impact | Effort |
|---|---------------|--------|--------|
| R4 | **Create GitHub Releases** with tags `v1.0.0` and `v1.0.1`. Releases appear in the sidebar and signal project maturity. Include release notes from CHANGELOG.md. | **High** | **Low** |
| R5 | **Add issue templates** — at minimum: `bug_report.yml`, `feature_request.yml`. This lowers the barrier for first-time contributors and signals community readiness. | **High** | **Low** |
| R6 | **Add PR template** (`.github/PULL_REQUEST_TEMPLATE.md`) with checklist: description, testing, screenshots. | **Medium** | **Low** |
| R7 | **Add CONTRIBUTING.md** — even a short one covering: how to report bugs, how to submit PRs, development setup. Critical for trending because new visitors look for this. | **High** | **Low** |
| R8 | **Add CODE_OF_CONDUCT.md** — use the Contributor Covenant template. GitHub shows a "Code of Conduct" badge in the community profile. | **Medium** | **Low** |
| R9 | **Set GitHub Topics** on the repo: `claude-code`, `claude-code-plugin`, `agent-team`, `ai-agent`, `llm`, `skill-generation`, `orchestration`, `claude`. Topics drive GitHub search and "Explore" recommendations. | **High** | **Low** |

---

### 3. Trust Signals (3/10)

| Item | Status |
|------|--------|
| CI/CD (GitHub Actions) | ❌ None |
| Tests | ❌ No test suite |
| Docs site | ⚠️ Landing page exists but no dedicated docs |
| Recent commits | ✅ Active (multiple commits in last 2 days) |
| Issue response time | N/A (no issues yet) |

#### Recommendations

| # | Recommendation | Impact | Effort |
|---|---------------|--------|--------|
| R10 | **Add a basic GitHub Actions CI workflow** — even a simple one that validates YAML/JSON, runs a linter on markdown, or checks that plugin.json is well-formed. A green CI badge in the README is a strong trust signal. | **High** | **Low** |
| R11 | **Add validation tests** — the plugin already mentions "dry-run testing" and "with-skill vs without-skill comparison." Package at least a smoke test that validates the plugin structure (plugin.json schema, SKILL.md exists, references exist). | **High** | **Medium** |
| R12 | **Deploy landing page to GitHub Pages** — enable Pages for the repo so `index.html` is live at `revfactory.github.io/harness`. Add the URL to the repo's "About" section. This doubles as a docs site. | **High** | **Low** |

---

### 4. Discoverability (7/10)

| Item | Status |
|------|--------|
| GitHub Topics | ❌ Not set |
| SEO description (repo About) | ⚠️ Unknown — needs to be set via GitHub UI |
| Social preview image | ❌ Not set (defaults to GitHub's auto-generated) |
| Multilingual README | ✅ EN, KO, JA |
| Landing page | ✅ `index.html` with i18n |

#### Recommendations

| # | Recommendation | Impact | Effort |
|---|---------------|--------|--------|
| R13 | **Set repo description** in GitHub "About" section: "Agent Team & Skill Architect — A Claude Code Plugin that designs domain-specific agent teams and generates skills" | **High** | **Low** |
| R14 | **Upload a social preview image** (1280×640px) via Settings → Social preview. This controls how the repo appears when shared on Twitter/X, Discord, Slack, etc. Use the banner image adapted to 2:1 ratio. | **High** | **Low** |
| R15 | **Set the website URL** in repo About to the GitHub Pages URL (see R12). | **Medium** | **Low** |

---

## Priority Matrix (Top 10 Actions)

Sorted by Impact ÷ Effort ratio for maximum trending readiness:

| Priority | Rec | Action | Impact | Effort |
|:--------:|:---:|--------|--------|--------|
| 1 | R4 | Create GitHub Releases (v1.0.0, v1.0.1) | High | Low |
| 2 | R9 | Set GitHub Topics | High | Low |
| 3 | R13 | Set repo description | High | Low |
| 4 | R14 | Upload social preview image | High | Low |
| 5 | R12 | Deploy landing page to GitHub Pages | High | Low |
| 6 | R5 | Add issue templates | High | Low |
| 7 | R7 | Add CONTRIBUTING.md | High | Low |
| 8 | R10 | Add CI workflow with badge | High | Low |
| 9 | R1 | Add demo GIF/screencast | High | Medium |
| 10 | R11 | Add validation tests | High | Medium |

---

## Summary

The Harness repo has a **strong foundation** — the README is well-structured with multilingual support, the landing page is polished, and the A/B testing evidence is a standout differentiator. The main gaps are in **community infrastructure** (no issue templates, PR template, CONTRIBUTING.md, CODE_OF_CONDUCT.md) and **trust signals** (no CI/CD, no tests, no releases/tags). The good news is that most high-impact fixes are low-effort — setting topics, creating releases, adding templates, and deploying the landing page to GitHub Pages can all be done in a single session and would raise the overall score from **5.5 to ~8/10**.
