# Scheduling-Structural-Logical (SSL)

This repository contains the paper-facing release assets for the Scheduling-Structural-Logical (SSL) representation of agent skills:

- SSL guidelines and schema documentation.
- The skill annotation process used to produce SSL records.
- Benchmark construction and rubric documentation for `SSL-SkillDiscovery` and `SSL-RiskAssessment`.
- Lightweight validation utilities for SSL records.

The dataset files are hosted separately on Hugging Face Dataset Hub:

- Dataset: [COOLPKU/SSL](https://huggingface.co/datasets/COOLPKU/SSL)
- Annotated corpus: 6,184 normalized SSL records.
- Benchmarks: `SSL-SkillDiscovery` and `SSL-RiskAssessment`.

## Skill Collection Source

The annotated corpus is derived from 6,300 publicly collected skill directories containing `SKILL.md` artifacts. The 6,184 released SSL records come from the `skillnet` collection after schema validation and bounded retry. Each released row on Hugging Face preserves the original collection metadata, including source collection, source slug/name/description, author, category, stars, and public `skill_url`; raw `SKILL.md` text is included when locally available.

The collected metadata covers ten categories: Development, Business, Productivity, AIGC, Security, Research, Testing, Lifestyle, Science, and Other.

The release is organized as follows:

```text
.
  docs/
    ssl_guidelines.md
    normalizer_prompt.md
    benchmarks.md
  scripts/
    annotate_skills.py
    validate_ssl_record.py
  DATA_CARD.md
  manifest.json
```

## Dataset Access

Use Hugging Face Datasets to load the released data:

```python
from datasets import load_dataset

corpus = load_dataset("COOLPKU/SSL", "annotated_skill_corpus")
skill_discovery = load_dataset("COOLPKU/SSL", "ssl_skill_discovery")
risk_assessment = load_dataset("COOLPKU/SSL", "ssl_risk_assessment")
```

If the dataset is published under a different Hugging Face organization or repository name, replace `COOLPKU/SSL` with the final dataset ID.

## SSL Records

Each normalized SSL record is a JSON object with three layers:

- `skill`: skill-level scheduling and invocation evidence.
- `scenes`: scene-level execution phases and transitions.
- `logic_steps`: source-grounded atomic actions and resource-use evidence.

The annotation prompt contract is documented in `docs/normalizer_prompt.md`. It follows the normalizer protocol described in the paper appendix; details already covered in the paper are not repeated here.

## Benchmarks

The Hugging Face dataset contains two benchmark configurations:

- `ssl_skill_discovery`: 431 intent-level queries over the 6,184-skill candidate set, with one source skill label per query.
- `ssl_risk_assessment`: 252 skills labeled on six binary risk dimensions, with compact final labels and supplementary labeling traces.

## Validation

The GitHub repository keeps a single-record SSL validator for checking downloaded records or newly generated annotations:

```bash
python scripts/validate_ssl_record.py path/to/record.json
```

## Skill Annotation Pipeline

The repository also includes a clean reproduction script for the SSL annotation process:

```bash
python scripts/annotate_skills.py \
  --source-root path/to/skill_collection \
  --output-dir annotated_skill_corpus \
  --model deepseek-v3.2 \
  --base-url https://api.deepseek.com/v1 \
  --api-key-env DEEPSEEK_API_KEY
```

The script discovers `SKILL.md` files, builds the SSL normalizer prompt from `docs/normalizer_prompt.md` and `docs/ssl_guidelines.md`, calls an OpenAI-compatible Chat Completions endpoint, validates each JSON record, retries failed records with validation feedback, and exports `ssl_records/`, `skill_metadata.json`, `slug_order.json`, `manifest.json`, and `failures.json`.

## Responsible Use

The risk labels describe static artifact-level evidence. They are intended for research on skill representation, retrieval, and pre-execution review. They are not runtime safety guarantees and should not be treated as executable attack instructions.

## License and Attribution

The normalized SSL records are derived from publicly collected skill artifacts. Release users should preserve source attribution and license metadata where available. If a downstream use requires redistribution of original skill text, verify the license of the corresponding source artifact.
