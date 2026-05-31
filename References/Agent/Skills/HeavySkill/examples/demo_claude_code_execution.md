# HeavySkill Demo: Claude Code Execution

## Overview

This demo shows HeavySkill executed within Claude Code as a harness, using the Agent tool to spawn parallel reasoning agents and then performing sequential deliberation.

## Problem

> A fair six-sided die is rolled 4 times. What is the probability that the product of the four results is divisible by 4?

## Stage 1: Parallel Reasoning (K=3)

Three independent agents were spawned in parallel using Claude Code's Agent tool.

---

### Thinker #1

**Approach:** Complementary counting via 2-adic valuation

**Reasoning:**
- Classified die faces by factors of 2: v₂(1)=0, v₂(2)=1, v₂(3)=0, v₂(4)=2, v₂(5)=0, v₂(6)=1
- P(v₂=0) = 3/6 = 1/2, P(v₂=1) = 2/6 = 1/3, P(v₂=2) = 1/6
- P(total factors of 2 = 0) = (1/2)^4 = 1/16
- P(total factors of 2 = 1) = C(4,1) × (1/3) × (1/2)^3 = 1/6
- P(not divisible by 4) = 1/16 + 1/6 = 11/48

**Answer:** 37/48

---

### Thinker #2

**Approach:** Complementary counting (same framework, independent derivation)

**Reasoning:**
- Same classification of die faces
- Same case analysis for total 2-adic valuation = 0 or 1
- P(not divisible by 4) = 1/16 + 1/6 = 11/48

**Answer:** 37/48

---

### Thinker #3

**Approach:** 2-adic valuation + brute-force verification

**Reasoning:**
- Same analytical approach as Thinkers #1 and #2
- Additionally performed exhaustive enumeration of all 6^4 = 1296 outcomes
- Confirmed 999 favorable outcomes → 999/1296 = 37/48

**Answer:** 37/48 (verified by enumeration)

---

## Stage 2: Sequential Deliberation

### Analysis

**Question type:** Complex reasoning task (probability with number-theoretic condition)

**Answer distribution:** All 3 thinkers agree on 37/48.

**Reasoning quality assessment:**
- All thinkers used the same core insight: the product is divisible by 4 iff the sum of 2-adic valuations across all rolls is ≥ 2.
- The complementary counting approach is clean and correct.
- Key verification: Thinker #3's brute-force enumeration confirms the analytical result (999/1296 = 37/48).

**Cross-validation:**
- Analytical approach: 1 - 1/16 - 1/6 = 1 - 3/48 - 8/48 = 37/48 ✓
- Brute-force: 999/1296 = 37/48 ✓
- Sanity check: 37/48 ≈ 0.771, which is reasonable (most 4-roll products will be divisible by 4 since rolling any even number twice suffices).

**Critical evaluation:**
- No logical errors detected in any thinker's reasoning.
- The approach is sound: decomposing divisibility by 4 into 2-adic valuations is the natural framework.
- The case analysis is exhaustive and mutually exclusive.

### Final Answer

$$P(\text{product divisible by 4}) = \frac{37}{48}$$

## Execution Metadata

- **Execution environment:** Claude Code (CLI)
- **Parallel agents:** 3
- **Agent model:** Claude (via Agent tool)
- **Deliberation:** Performed by main Claude Code session
- **Consensus:** Unanimous (3/3 thinkers agree)
- **Verification:** Confirmed by exhaustive enumeration
