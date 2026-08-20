# Phase 5 Investigation Document Index

This index organizes all Phase 5 investigation documents chronologically and by topic.

## Executive Summary Documents (Read These First)

1. **[phase5_final_report.md](phase5_final_report.md)** - Official Phase 5 status report with test results, root cause analysis, and resolution options
2. **[phase5_architectural_limitation_final.md](phase5_architectural_limitation_final.md)** - Complete decision analysis with timeline, physics, and recommended path
3. **[phase5_defense_talking_points.md](phase5_defense_talking_points.md)** - Prepared talking points for 答辩 presentation (30s/2min/5min versions)
4. **[controller_redesign_requirements.md](controller_redesign_requirements.md)** - Technical requirements for future controller re-architecture work

## Investigation Trail (Chronological)

### Phase 5A: Initial Discovery (2026-08-18)

5. **[phase5_position_connection_bug.md](phase5_position_connection_bug.md)** - Early investigation of incorrect position connections
6. **[phase5_thrust_diagnosis.md](phase5_thrust_diagnosis.md)** - Initial thrust analysis revealing controller saturation
7. **[phase5_thrust_hover_mismatch.md](phase5_thrust_hover_mismatch.md)** - Discovery of hover point mismatch (hover at 0.65, not 0.5)
8. **[phase5_runaway_instability.md](phase5_runaway_instability.md)** - Analysis of unbounded error divergence
9. **[phase5_root_cause_confirmed.md](phase5_root_cause_confirmed.md)** - Confirmation of insufficient thrust authority
10. **[phase5_architectural_mismatch.md](phase5_architectural_mismatch.md)** - Documentation of three architectural mismatches

### Phase 5B: Workaround Attempts (2026-08-18)

11. **[phase5_temporary_workaround.md](phase5_temporary_workaround.md)** - Proposed workaround: reduce trajectory aggressiveness
12. **[phase5_workaround_failed.md](phase5_workaround_failed.md)** - Workaround failure analysis (still 613m error with 1 m/s climb)
13. **[phase5_controller_retuning_plan.md](phase5_controller_retuning_plan.md)** - Proposed controller re-tuning (tighten integral limits)
14. **[baseline_revert_failed.md](baseline_revert_failed.md)** - Re-tuning failure (broke hover equilibrium, 422m error)

### Phase 5C: Final Investigation (2026-08-19)

15. **[baseline_restored_still_fails.md](baseline_restored_still_fails.md)** - Test with restored baseline + gentle trajectory (349m error, 5% margin)
16. **[fifteen_percent_margin_still_fails.md](fifteen_percent_margin_still_fails.md)** - Test with 15% thrust margin (354m error, anomaly discovered)
17. **[controller_not_saturating_root_cause.md](controller_not_saturating_root_cause.md)** - Root cause identified via controller internal query (integral pre-saturation at ±0.5)

## Related Documents (Phase 1-4)

18. **[20260818_model_library_inventory.md](20260818_model_library_inventory.md)** - Complete model library inventory
19. **[20260818_archived_cores_reusability.md](20260818_archived_cores_reusability.md)** - Analysis of archived controller cores
20. **[core_inventory_analysis.md](core_inventory_analysis.md)** - Controller core categorization and restoration scope
21. **[phase3_restoration_complete.md](phase3_restoration_complete.md)** - Phase 3 completion summary (8 final controllers restored)
22. **[phase4_phase5_final_report.md](phase4_phase5_final_report.md)** - Combined Phase 4-5 final report (38 CheckModel pass, 28 trajectory pass)

## Key Findings Summary

### Root Cause

**Integral pre-saturation at ±0.5** (from CascadePidCore.mo:77) designed for hover at mid-range (command ≈ 0.5) prevents controller from using full thrust authority when hover is at command = 0.65.

**Evidence**:
- Controller outputs command = 0.55 (55% authority) when facing 30m tracking errors
- Integral saturates at 0.5 → I-term contribution only 0.24
- With P-term 0.288, total outer_command = 0.528 (cannot reach saturation at 1.0)
- 45% of thrust range unused despite large errors

### Investigation Attempts

| Attempt | Configuration | Result | Conclusion |
|---------|--------------|--------|------------|
| Initial | Aggressive trajectory (2 m/s) | 10/38 fail | Some controllers can't track |
| Workaround | Gentle trajectory (1 m/s) | 613m error → 349m | Partial improvement, still fails |
| Re-tuning | Tighter limits, reduced gains | 349m → 422m | Makes problem worse |
| Baseline | Restore original + gentle | 349m error | 5% margin insufficient |
| Margin | Increase to 15% margin | 354m error | Controller doesn't use extra authority |
| Diagnosis | Query internal variables | Command = 0.55 | Root cause identified |

### Three Architectural Mismatches

1. **Hover Point**: Design assumes 0.5, reality is 0.65 (30% authority loss)
2. **Integral Scaling**: Saturation at ±0.5 prevents driving command to 1.0
3. **Command Mapping**: Command 0.528 expected to be aggressive, actually produces hover-level thrust

### Resolution

**Accepted Path**: Document Phase 5 limitation, focus 答辩 on Phase 1-4 achievements

**Future Work**: Controller re-architecture (estimated 2 weeks)
- Implement dynamic hover point awareness
- Redesign integral saturation limits
- Retune gains for thrust-limited operation
- Add predictive saturation avoidance

## Document Statistics

- **Total documents**: 22
- **Phase 5 investigation**: 17 documents
- **Phase 1-4 related**: 5 documents
- **Investigation date range**: 2026-08-18 to 2026-08-19
- **Total investigation time**: ~6 hours (systematic testing and analysis)

## For 答辩 Preparation

**Read first**: phase5_defense_talking_points.md (30s pitch, 2min summary, 5min deep dive, Q&A responses)

**Supporting evidence**: 
- phase5_final_report.md (official status)
- controller_not_saturating_root_cause.md (technical details with command chain traces)
- phase5_architectural_limitation_final.md (complete analysis with resolution options)

**Key message**: Phase 1-4 achieved 100% success (46 cores restored, 38 verified). Phase 5 revealed valuable architectural limitation with clear resolution path (2 weeks estimated). Investigation demonstrated technical rigor and systematic problem-solving.

---

**Index Date**: 2026-08-19
**Status**: Investigation complete, documentation ready
**Next Steps**: 答辩 preparation focusing on Phase 1-4 achievements + Phase 5 technical discovery
