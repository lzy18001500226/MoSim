# AI Harness Benchmark Report

> Prompt: 3D Creative Learning Platform MVP (benchmarks/prompt.md)
> Model:  (effort: max, 1M context)
> Date:
> Condition: identical raw prompt, $HOME isolation, empty git-init project, --dangerously-skip-permissions

## Summary

| Rank | Harness | Score | Build | Install | Time | Cost | Tokens (in/out) |
|---|---|---|---|---|---|---|---|

## Screenshot Comparison

| | vanilla | oma | omc | ecc | superpowers |
|---|---|---|---|---|---|
| Landing | ![](screenshots/vanilla/01-landing.png) | ![](screenshots/oma/01-landing.png) | ![](screenshots/omc/01-landing.png) | ![](screenshots/ecc/01-landing.png) | ![](screenshots/superpowers/01-landing.png) |
| World Builder | ![](screenshots/vanilla/02-world-builder.png) | ![](screenshots/oma/02-world-builder.png) | ![](screenshots/omc/02-world-builder.png) | ![](screenshots/ecc/02-world-builder.png) | ![](screenshots/superpowers/02-world-builder.png) |
| AI Panel | ![](screenshots/vanilla/03-ai-panel.png) | ![](screenshots/oma/03-ai-panel.png) | ![](screenshots/omc/03-ai-panel.png) | ![](screenshots/ecc/03-ai-panel.png) | ![](screenshots/superpowers/03-ai-panel.png) |
| Gallery | ![](screenshots/vanilla/04-gallery.png) | ![](screenshots/oma/04-gallery.png) | ![](screenshots/omc/04-gallery.png) | ![](screenshots/ecc/04-gallery.png) | ![](screenshots/superpowers/04-gallery.png) |

## Category Breakdown

### Project Setup (10pts)

| Item | vanilla | oma | omc | ecc | superpowers |
|---|---|---|---|---|---|
| Next.js + TypeScript project configured (/2.5) |  |  |  |  |  |
| Tailwind CSS configured (/2.5) |  |  |  |  |  |
| React Three Fiber + Drei dependencies (/2.5) |  |  |  |  |  |
| Build succeeds (npm run build) (/2.5) |  |  |  |  |  |
| **Category Total** | **** | **** | **** | **** | **** |

### 3D World Builder (20pts)

| Item | vanilla | oma | omc | ecc | superpowers |
|---|---|---|---|---|---|
| Three.js Canvas rendering (/5) |  |  |  |  |  |
| Object placement (/5) |  |  |  |  |  |
| Move / rotate / scale controls (/5) |  |  |  |  |  |
| Color / texture modification (/5) |  |  |  |  |  |
| Environment theme selection (/5) |  |  |  |  |  |
| Simple animation / interaction (/5) |  |  |  |  |  |
| **Category Total** | **** | **** | **** | **** | **** |

### AI Creative Partner (15pts)

| Item | vanilla | oma | omc | ecc | superpowers |
|---|---|---|---|---|---|
| AI sidebar / guide UI exists (/5) |  |  |  |  |  |
| Idea prompting capability (/5) |  |  |  |  |  |
| What-if question generation (/5) |  |  |  |  |  |
| OpenAI API integration code (/5) |  |  |  |  |  |
| **Category Total** | **** | **** | **** | **** | **** |

### Child Onboarding (10pts)

| Item | vanilla | oma | omc | ecc | superpowers |
|---|---|---|---|---|---|
| Onboarding screen / flow exists (/5) |  |  |  |  |  |
| Startable within 1 minute UX (/5) |  |  |  |  |  |
| **Category Total** | **** | **** | **** | **** | **** |

### Play / Explore Mode (10pts)

| Item | vanilla | oma | omc | ecc | superpowers |
|---|---|---|---|---|---|
| Explore created world mode (/5) |  |  |  |  |  |
| Object click reactions / animations (/5) |  |  |  |  |  |
| **Category Total** | **** | **** | **** | **** | **** |

### Save / Gallery (10pts)

| Item | vanilla | oma | omc | ecc | superpowers |
|---|---|---|---|---|---|
| Project save / load (/5) |  |  |  |  |  |
| Gallery screen exists (/5) |  |  |  |  |  |
| **Category Total** | **** | **** | **** | **** | **** |

### UX Quality (15pts)

| Item | vanilla | oma | omc | ecc | superpowers |
|---|---|---|---|---|---|
| Child-friendly design (big buttons, minimal text) (/5) |  |  |  |  |  |
| Desktop / tablet responsive (/5) |  |  |  |  |  |
| Clean UI (no clutter) (/5) |  |  |  |  |  |
| Visual guidance / icon-driven (/5) |  |  |  |  |  |
| **Category Total** | **** | **** | **** | **** | **** |

### Code Quality & Testing (10pts)

| Item | vanilla | oma | omc | ecc | superpowers |
|---|---|---|---|---|---|
| Test files exist (*.test.*, *.spec.*) (/2.5) |  |  |  |  |  |
| Tests pass (npm test) (/2.5) |  |  |  |  |  |
| Coverage for key components (/2.5) |  |  |  |  |  |
| Meaningful tests (not just snapshots) (/2.5) |  |  |  |  |  |
| **Category Total** | **** | **** | **** | **** | **** |

## Meta Metrics

| | vanilla | oma | omc | ecc | superpowers |
|---|---|---|---|---|---|
| Wall Clock Time | n/a | n/a | n/a | n/a | n/a |
| Total Tokens | n/a | n/a | n/a | n/a | n/a |
| Cost (USD) | $0.00 | $0.00 | $0.00 | $0.00 | $0.00 |
| Install Status |  |  |  |  |  |
| Run Status |  |  |  |  |  |

## Methodology

- Isolation: $HOME override per harness
- Initial state: empty directory + git init
- Prompt: identical raw prompt, no harness workflow
- Permissions: --dangerously-skip-permissions
- Model:  with --effort max
- Budget cap: $20 per run
- Time limit: 60 minutes per run
- Reproduction: see benchmarks/run.sh

## Per-harness Notes

### vanilla

- Install:
- Run:
- Install log (tail):
  ```
  vanilla: no install needed
  === ls -la /tmp/oma-benchmark-20260504-171703/projects/vanilla ===
  total 0
  drwxr-xr-x@ 3 gracefullight  wheel   96 May  4 17:17 .
  drwxr-xr-x@ 7 gracefullight  wheel  224 May  4 17:17 ..
  drwxr-xr-x@ 9 gracefullight  wheel  288 May  4 17:17 .git

  === du -sh /tmp/oma-benchmark-20260504-171703/homes/vanilla ===
  112K	/tmp/oma-benchmark-20260504-171703/homes/vanilla
  ```

### oma

- Install:
- Run:
- Install log (tail):
  ```
  │  ○ 中文
  └
  === ls -la /tmp/oma-benchmark-20260504-171703/projects/oma ===
  total 0
  drwxr-xr-x@ 3 gracefullight  wheel   96 May  4 17:17 .
  drwxr-xr-x@ 7 gracefullight  wheel  224 May  4 17:17 ..
  drwxr-xr-x@ 9 gracefullight  wheel  288 May  4 17:17 .git

  === du -sh /tmp/oma-benchmark-20260504-171703/homes/oma ===
  1.0M	/tmp/oma-benchmark-20260504-171703/homes/oma
  ```

### omc

- Install:
- Run:
- Install log (tail):
  ```
  fatal: destination path '/tmp/oma-benchmark-20260504-171703/plugins/omc' already exists and is not an empty directory.
  Cloning into '/tmp/oma-benchmark-20260504-171703/plugins/omc'...
  === ls -la /tmp/oma-benchmark-20260504-171703/projects/omc ===
  total 0
  drwxr-xr-x@ 3 gracefullight  wheel   96 May  4 17:17 .
  drwxr-xr-x@ 7 gracefullight  wheel  224 May  4 17:17 ..
  drwxr-xr-x@ 9 gracefullight  wheel  288 May  4 17:40 .git

  === du -sh /tmp/oma-benchmark-20260504-171703/homes/omc ===
  112K	/tmp/oma-benchmark-20260504-171703/homes/omc
  ```

### ecc

- Install:
- Run:
- Install log (tail):
  ```
  SKIPPED: ecc is not benchmarked in this run.

  Reason: ecc's install.sh writes to the user-level ~/.claude/ directory.
  Because claude requires the real HOME to authenticate via OAuth on macOS,
  running ecc's installer here would mutate the operator's actual config.
  Run ecc standalone in a disposable VM/container to benchmark it.
  ```

### superpowers

- Install:
- Run:
- Install log (tail):
  ```
  fatal: destination path '/tmp/oma-benchmark-20260504-171703/plugins/superpowers' already exists and is not an empty directory.
  Cloning into '/tmp/oma-benchmark-20260504-171703/plugins/superpowers'...
  === ls -la /tmp/oma-benchmark-20260504-171703/projects/superpowers ===
  total 0
  drwxr-xr-x@ 3 gracefullight  wheel   96 May  4 17:17 .
  drwxr-xr-x@ 7 gracefullight  wheel  224 May  4 17:17 ..
  drwxr-xr-x@ 9 gracefullight  wheel  288 May  4 17:49 .git

  === du -sh /tmp/oma-benchmark-20260504-171703/homes/superpowers ===
  112K	/tmp/oma-benchmark-20260504-171703/homes/superpowers
  ```
