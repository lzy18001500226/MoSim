# Released Benchmarks

The benchmark data are hosted on Hugging Face under the dataset ID listed in the repository README. The paper provides the full construction and evaluation protocol; this file only records the released configs and field formats.

## `ssl_skill_discovery`

`SSL-SkillDiscovery` evaluates retrieval over the 6,184-skill annotated corpus.

Main file:

- `queries.jsonl`

Each row contains:

- `query_id`
- `query`
- `type`
- `source_skill`
- `candidate_source`
- `realism_score`
- `grounded_score`
- `document_proximity_score`

The benchmark uses `source_skill` as the single labeled relevant item. The primary metric reported in the paper is MRR@50.

## `ssl_risk_assessment`

`SSL-RiskAssessment` labels static skill artifacts on six independent binary dimensions.

Main file:

- `gold_labels.jsonl`

Each row contains:

- `example_id`
- `slug`
- `skill_name`
- `skill_goal`
- `risk_level`
- `disputed_dimensions`
- `final_labels`
- `vote_counts`

The six dimensions are `data_exfiltration`, `destructive`, `privilege_escalation`, `covert_execution`, `resource_abuse`, and `credential_access`. Each label is either `risk` or `no_risk`. The primary metric reported in the paper is macro F1.
