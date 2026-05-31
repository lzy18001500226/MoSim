# HeavySkill

[![arXiv](https://img.shields.io/badge/arXiv-2605.02396-b31b1b.svg)](https://arxiv.org/abs/2605.02396)
[![PDF](https://img.shields.io/badge/Paper-PDF-green.svg)](https://arxiv.org/pdf/2605.02396)

**Heavy Thinking as the Inner Skill in Agentic Harness**

HeavySkill is a test-time scaling technique that decomposes complex reasoning into two stages:
1. **Parallel Reasoning** — Generate K independent reasoning trajectories concurrently
2. **Sequential Deliberation** — Synthesize trajectories through critical analysis into a superior final answer

This repository provides two modes of use:

| Mode | Description | Use Case |
|------|-------------|----------|
| **Workflow** | Python async pipeline with CLI | Batch evaluation, research experiments, custom deployments |
| **Skill** | Pure prompt file for Claude Code / agentic harness | Interactive reasoning in AI-native IDEs |

## Key Results

- Heavy thinking consistently outperforms Best-of-N (majority voting) strategies
- Stronger LLMs can approach Pass@N performance through deliberation
- The depth (iterations) and width (K) of heavy thinking are scalable via RLVR

## Installation

```bash
git clone https://github.com/wjn1996/HeavySkill.git
cd HeavySkill
pip install -e .
```

## Quick Start

### Mode 1: Workflow (Python Pipeline)

```bash
python scripts/run_heavyskill.py \
    --query "Find the number of paths of length 16 on an 8x8 grid that change direction exactly four times." \
    --model "deepseek-r1" \
    --api_base "http://localhost:8080" \
    --reason_k 8 \
    --summary_k 4 \
    --prompt_type "stem" \
    --output "outputs/result.json" \
    --verbose
```

**Parameters:**
- `--reason_k`: Number of parallel reasoning trajectories (default: 8)
- `--summary_k`: Number of deliberation samples (default: 4)
- `--iterations`: Iterative deliberation rounds (default: 1)
- `--prompt_type`: `"general"` or `"stem"`
- `--language`: `"en"` or `"cn"`

**Using a separate deliberation model:**
```bash
python scripts/run_heavyskill.py \
    --query "Your problem here" \
    --model "r1-distill-qwen-7b" \
    --api_base "http://localhost:8080" \
    --summary_model "qwen3-32b" \
    --summary_api_base "http://localhost:8081" \
    --reason_k 16 \
    --summary_k 4
```

**Batch mode:**
```bash
python scripts/run_heavyskill.py \
    --input_file "examples/example_math.json" \
    --model "deepseek-r1" \
    --api_base "http://localhost:8080" \
    --output "outputs/batch_result.json"
```

### Mode 2: Skill (Claude Code / Agentic Harness)

Copy the skill file into your Claude Code skills directory:

```bash
cp skill/heavyskill.md ~/.claude/skills/heavyskill.md
```

Then in Claude Code, the heavy thinking protocol will be available for complex reasoning tasks. The skill instructs the model to:
1. Spawn multiple independent reasoning agents in parallel
2. Collect diverse reasoning trajectories
3. Perform critical meta-analysis and deliberation
4. Output the synthesized final answer

## Project Structure

```
HeavySkill/
├── workflow/                    # Mode 1: Python async pipeline
│   ├── config.py               # Configuration dataclass
│   ├── parallel_reasoning.py   # Stage 1: Parallel trajectory generation
│   ├── sequential_deliberation.py  # Stage 2: Synthesis & deliberation
│   ├── memory_cache.py         # Trajectory storage & selection
│   ├── prompts.py              # Prompt templates (general, STEM, CN/EN)
│   ├── pipeline.py             # Full pipeline orchestration
│   ├── utils.py                # Utilities (clipping, extraction, etc.)
│   └── agent/
│       ├── base.py             # Abstract agent interface
│       └── openai_compatible.py # OpenAI-compatible async API client
├── scripts/
│   ├── run_heavyskill.py       # CLI entry point
│   ├── run_heavyskill.sh       # Example shell script
│   └── evaluate.py             # Simple accuracy evaluation
├── skill/
│   └── heavyskill.md           # Pure prompt skill for agentic harness
├── examples/
│   └── example_math.json       # Example input data
├── paper/
│   └── heavyskill.pdf          # Paper
├── requirements.txt
└── pyproject.toml
```

## How It Works

```
┌─────────────────────────────────────────────────────────┐
│                      User Query                          │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│            Stage 1: Parallel Reasoning                   │
│                                                         │
│   ┌──────────┐ ┌──────────┐ ┌──────────┐    ┌──────┐  │
│   │ Thinker 1│ │ Thinker 2│ │ Thinker 3│ ...│  K   │  │
│   └────┬─────┘ └────┬─────┘ └────┬─────┘    └──┬───┘  │
│        │             │             │             │      │
└────────┼─────────────┼─────────────┼─────────────┼──────┘
         │             │             │             │
         ▼             ▼             ▼             ▼
┌─────────────────────────────────────────────────────────┐
│                    Memory Cache                          │
│         (Store & organize K trajectories)                │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│          Stage 2: Sequential Deliberation                │
│                                                         │
│   - Analyze answer distribution across trajectories      │
│   - Cross-validate reasoning chains                      │
│   - Identify logical errors & correct approaches         │
│   - Synthesize final answer with critical thinking       │
│                                                         │
│              ┌─── Iterative Update (optional) ◄──┐      │
│              └───────────────────────────────────┘      │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│                    Final Answer                          │
└─────────────────────────────────────────────────────────┘
```

## API Compatibility

The workflow supports any OpenAI-compatible API endpoint:
- **vLLM** serving (`--api_base http://localhost:8000`)
- **DeepSeek API** (`--api_base https://api.deepseek.com`)
- **Together AI** (`--api_base https://api.together.xyz`)
- **OpenRouter** (`--api_base https://openrouter.ai/api`)
- **Local Ollama** (`--api_base http://localhost:11434`)

## Citation

```bibtex
@article{wang2026heavyskill,
  title={HeavySkill: Heavy Thinking as the Inner Skill in Agentic Harness},
  author={Wang, Jianing and Guo, Linsen and Chen, Zhengyu and Guo, Qi and Zang, Hongyu and Shi, Wenjie and Ma, Haoxiang and Xi, Xiangyu and Li, Xiaoyu and Wang, Wei and Cai, Xunliang},
  journal={arXiv preprint arXiv:2605.02396},
  year={2026},
  url={https://arxiv.org/abs/2605.02396}
}
```

## License

Apache-2.0
