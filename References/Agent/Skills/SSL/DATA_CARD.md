# Data Card

## Annotated Skill Corpus

- Size: 6,184 normalized skill records.
- Source pool: 6,300 public skill directories with `SKILL.md` files.
- Normalization yield: 98.16%.
- Hugging Face config: `annotated_skill_corpus`.
- Format on Hugging Face: sharded JSONL rows with `slug`, complete `metadata`, `source_metadata`, `raw_skill_md`, and `ssl_record`.

The corpus contains derived SSL annotations paired with source provenance and raw `SKILL.md` text when available. Each SSL record is intended to expose source-grounded evidence in a compact, typed structure.

## Skill Collection Source

The released records are derived from the `skillnet` collection of public skill artifacts. The raw pool contains 6,300 skill directories with `SKILL.md` files; 6,184 produce valid SSL records after bounded normalization and validation. For each released record, the Hugging Face data preserves source metadata from the original collection, including source slug/name/description, author, category, stars, public source URL, and raw-text availability.

Category distribution in the released corpus: Development 2,973; Business 779; Productivity 618; AIGC 443; Security 380; Research 335; Testing 272; Lifestyle 228; Science 138; Other 18.

## Skill Annotation Process

The annotation prompt contract is documented in `docs/normalizer_prompt.md`. In brief, each source `SKILL.md` is converted into the fixed SSL schema by a constrained `NL2JSON` normalizer, checked by deterministic schema validation, retried under a bounded budget when hard validation fails, and included in the released corpus only when it yields a parseable and schema-valid SSL record.

The process is inference-only and does not fine-tune a model. The release provides the annotation protocol and validation rules, but does not include local API keys, provider-specific batch logs, or transient checkpoints.

The public reproduction code is provided in `scripts/annotate_skills.py`. It implements source discovery, prompt construction from the released prompt contract, provider calls through an OpenAI-compatible endpoint, JSON parsing, schema validation, bounded retry, and metadata export.

## SSL-SkillDiscovery Benchmark

- Candidate set: the 6,184-skill annotated corpus.
- Queries: 431 intent-level requests.
- Label: each query is paired with one `source_skill` slug.
- Primary metric in the paper: MRR@50.
- Hugging Face config: `ssl_skill_discovery`.

The benchmark uses a strict single-relevant-item protocol. Near-equivalent neighboring skills are counted as errors to keep the metric definition unambiguous.

## SSL-RiskAssessment Benchmark

- Skills: 252 sampled skills.
- Dimensions: `data_exfiltration`, `destructive`, `privilege_escalation`, `covert_execution`, `resource_abuse`, and `credential_access`.
- Label space: `risk` / `no_risk`.
- Primary metric in the paper: macro F1 across the six binary dimensions.
- Hugging Face config: `ssl_risk_assessment`.

The Hugging Face release contains compact final labels and supplementary model-labeling traces.

## Known Limitations

- SSL is extracted from static artifacts and cannot fully characterize dynamic runtime behavior.
- Some source documents are multilingual or use non-standard formatting.
- Risk labels reflect observable static evidence, not real-world harm rates.
- `SSL-SkillDiscovery` labels use the source skill as the single relevant item, which may understate retrieval quality when multiple skills can satisfy a request.
