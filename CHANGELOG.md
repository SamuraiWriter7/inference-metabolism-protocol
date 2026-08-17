# Changelog

All notable changes to the **Inference Metabolism Protocol (IMP)** are documented in this file.

The format follows a versioned protocol-development model.

---

# [0.5.0] - 2026-08-17

## Added

### Metabolism Cycle

* Added the **Metabolism Cycle** as the canonical IMP lifecycle unit.
* Added complete generation `N → N+1` lifecycle representation.
* Added `metabolism-cycle-record.schema.json`.
* Added `metabolism-cycle-conformance-case.schema.json`.

The canonical lifecycle is now:

```text
Builder
   ↓
Shift Governor
   ↓
Handoff Event
   ↓
Auditor
   ↓
Audit Record
   ↓
State Purification
   ↓
State Purification Record
   ↓
Cross-Record Conformance
   ↓
State Packet
   ↓
Fresh Builder
```

---

### Lifecycle Gates

Added explicit cycle-level gates:

* Governor Gate
* Handoff Gate
* Audit Gate
* Purification Gate
* Cross-Record Gate
* Goal Continuity Gate
* Raw-Trace Non-Inheritance Gate
* Evidence Preservation Gate
* Packet Verification Gate

A Metabolism Cycle cannot be validly completed when a required gate fails.

---

### Cycle Outcomes

Added:

* `COMPLETED`
* `REQUIRES_REWORK`
* `ABORTED`

Only:

```text
COMPLETED
```

may authorize:

```text
next_builder_eligible = true
```

---

### Generation Closure

Added validation that:

```text
Cycle.source_generation
=
Governor.generation
=
Handoff.current_generation
=
Audit.generation
=
Purification.source_generation
```

where the Governor is applicable.

Added validation that:

```text
Cycle.target_generation
=
Handoff.next_generation
=
Purification.target_generation
=
StatePacket.generation
```

---

### Lifecycle Reference Closure

Added validation for:

* source State Packet ID,
* Shift Governor Assessment ID,
* Handoff Event ID,
* Audit Record ID,
* State Purification Record ID,
* output State Packet ID.

---

### Governor-to-Handoff Conformance

Added full-cycle validation that Governor-controlled turnover may proceed only when the Governor decision is:

```text
HANDOFF
```

or:

```text
EMERGENCY
```

A lifecycle transition MUST NOT execute while the Governor decision is:

```text
CONTINUE
PREPARE
```

---

### Interrupt Semantics

Refined handoff behavior.

The following now require:

```text
INTERRUPT
```

semantics:

* `ANOMALY_DETECTED`
* Governor decision `EMERGENCY`

This allows a trigger such as `CONTEXT_PRESSURE` to become an interrupt when the Governor classifies the condition as `EMERGENCY`.

---

### Audit Gate

Added cycle-level validation requiring:

```text
Audit.decision = PASS
```

and:

```text
Audit.state_eligible = true
```

before normal next-generation inheritance.

---

### Purification Gate

Added requirement that a completed cycle contain:

```text
StatePurification.output.status
=
READY_FOR_HANDOFF
```

---

### Packet Verification Gate

Added requirement that the output State Packet contain:

```text
integrity.audit_status
=
VERIFIED
```

---

### Cross-Record Gate

Promoted v0.4 Cross-Record Conformance from an independent validation layer to a mandatory Metabolism Cycle gate.

A cycle cannot be validly completed if:

```text
Audit
→ Purification
→ State Packet
```

fails lineage validation.

---

### Cycle-Level Goal Continuity

Added complete lifecycle verification that:

```text
goal_hash_before
=
goal_hash_after
=
StatePacket.immutable_goal.goal_hash
```

---

### Cycle-Level Raw Trace Non-Inheritance

Added validation that:

```text
cycle.raw_trace_inherited = false
```

```text
StatePacket.raw_trace_inherited = false
```

and:

```text
Purification.raw_trace_items_inherited = 0
```

---

### Cycle-Level Evidence Preservation

Added validation that:

```text
cycle.evidence_preserved = true
```

```text
StatePacket.evidence_preserved = true
```

and:

```text
Purification.evidence_traceability_preserved = true
```

---

### Metabolism Cycle Conformance Cases

Added pass/fail test harnesses for complete lifecycle validation.

Example violation classes include:

* `CYCLE_GENERATION_MISMATCH`
* `CYCLE_RECORD_REFERENCE_MISMATCH`
* `CYCLE_TRIGGER_MISMATCH`
* `CYCLE_GOVERNOR_MISMATCH`
* `CYCLE_HANDOFF_MODE_MISMATCH`
* `CYCLE_AUDIT_NOT_ELIGIBLE`
* `CYCLE_PURIFICATION_NOT_READY`
* `CYCLE_PACKET_NOT_VERIFIED`
* `CYCLE_GOAL_MISMATCH`
* `CYCLE_RAW_TRACE_INHERITED`
* `CYCLE_EVIDENCE_NOT_PRESERVED`
* `CYCLE_CROSS_RECORD_FAILURE`
* `CYCLE_OUTCOME_INVALID`

---

### Core Invariants

Added:

* IMP-39 — Metabolism Cycle Closure
* IMP-40 — Source Generation Closure
* IMP-41 — Target Generation Closure
* IMP-42 — Lifecycle Reference Closure
* IMP-43 — Governor Handoff Eligibility
* IMP-44 — Interrupt Semantics
* IMP-45 — Audit Gate
* IMP-46 — Purification Gate
* IMP-47 — Packet Verification Gate
* IMP-48 — Cross-Record Gate
* IMP-49 — Evidence / Trace Continuity
* IMP-50 — Builder Eligibility

IMP now defines:

```text
IMP-01 through IMP-50
```

---

## Changed

* Upgraded reference validation to IMP v0.5.
* Added full-cycle conformance after record-local and cross-record validation.
* Refined Handoff Event semantics so non-anomaly triggers may use `INTERRUPT` when a Governor `EMERGENCY` decision requires it.
* Clarified that reasoning-health triggers require Shift Governor participation during complete-cycle conformance.
* Clarified the distinction between:

  * IMP release version,
  * individual record schema version.
* Preserved earlier record schema versions when their structures remain unchanged.

---

## Validation Model

IMP v0.5 defines five practical validation levels:

```text
Level 1
JSON Syntax
    ↓
Level 2
JSON Schema
    ↓
Level 3
Record-Local Semantics
    ↓
Level 4
Cross-Record Conformance
    ↓
Level 5
Metabolism Cycle Conformance
```

---

## Design Principle

IMP v0.5 establishes the complete lifecycle principle:

> **Preserve Evidence.
> Audit Truth.
> Purify State.
> Verify Inheritance.
> Reset Reasoning.
> Continue the System.**

---

## Protocol Milestone

IMP v0.5 is the **first complete protocol milestone**.

It now defines:

* what survives,
* what is excluded from inheritance,
* when reasoning should continue,
* when reasoning should stop,
* how outputs are audited,
* how state is purified,
* how inherited information is verified,
* how generational continuity is represented,
* and when a fresh Builder may begin.

---

## Known Limitations

IMP v0.5 does not yet standardize:

* automatic Context Pressure measurement,
* universal Loop Probability calculation,
* standardized Error Density observation windows,
* universal Goal Drift measurement,
* quantitative Minimum Sufficient State scoring,
* Metabolism Efficiency scoring,
* execution-plan closure,
* open-issue closure,
* environment-state closure,
* resource-budget closure,
* discarded-item resurrection detection,
* cryptographic record signatures,
* distributed lifecycle consensus,
* parallel Builder semantics,
* production framework adapters.

---

# [0.4.0] - 2026-08-17

## Added

### Cross-Record Conformance

Added validation across:

```text
Audit Record
      ↓
State Purification Record
      ↓
State Packet
```

This closes the gap between independently valid records and a valid inheritance chain.

---

### Cross-Record Schema

Added:

```text
cross-record-conformance-case.schema.json
```

---

### Audit-to-Purification Validation

Added verification that retained verified facts originate from the associated Audit Record.

Added verification that retained verified artifacts originate from the associated Audit Record.

---

### Purification-to-Packet Closure

Added exact closure validation for:

* verified facts,
* verified artifacts,
* working assumptions,
* generated guardrails.

---

### Provenance Closure

Added lineage validation for:

* Audit Record ID,
* Builder run ID,
* Planner run ID,
* previous State Packet ID,
* resulting State Packet ID.

---

### Goal Hash Closure

Added verification that:

```text
Purification.goal_hash_after
=
StatePacket.immutable_goal.goal_hash
```

---

### Generation Closure

Added verification that:

```text
Audit.generation
=
Purification.source_generation
```

and:

```text
Purification.target_generation
=
StatePacket.generation
```

---

### Cross-Record Violation Codes

Added violation classes including:

* `LINKED_RECORD_INVALID`
* `GENERATION_MISMATCH`
* `AUDIT_REFERENCE_MISMATCH`
* `STATE_PACKET_REFERENCE_MISMATCH`
* `PROVENANCE_MISMATCH`
* `GOAL_HASH_MISMATCH`
* `UNAUDITED_FACT_RETAINED`
* `UNAUDITED_ARTIFACT_RETAINED`
* `PACKET_FACT_SET_MISMATCH`
* `PACKET_ARTIFACT_SET_MISMATCH`
* `PACKET_ASSUMPTION_SET_MISMATCH`
* `PACKET_GUARDRAIL_SET_MISMATCH`

---

### Core Invariants

Added:

* IMP-29 — Cross-Record Lineage
* IMP-30 — Generation Alignment
* IMP-31 — Audited Fact Origin
* IMP-32 — Audited Artifact Origin
* IMP-33 — Fact Closure
* IMP-34 — Artifact Closure
* IMP-35 — Assumption Closure
* IMP-36 — Guardrail Closure
* IMP-37 — Goal Hash Continuity
* IMP-38 — Provenance Closure

---

## Changed

* Validator upgraded from record-local validation to:

  * record-local validation,
  * Cross-Record Conformance.

---

## Design Principle

IMP v0.4 establishes:

> **A valid record does not imply a valid inheritance chain.**

---

# [0.3.0] - 2026-08-17

## Added

### State Purification Record

Added:

```text
state-purification-record.schema.json
```

State Purification became an explicit auditable lifecycle phase.

---

### Inheritance Classification

Added explicit representation of:

* retained verified facts,
* retained verified artifacts,
* carried working assumptions,
* generated guardrails,
* discarded items.

---

### Discard Reason Taxonomy

Added:

* `IRRELEVANT`
* `DUPLICATE`
* `STALE`
* `UNSUPPORTED`
* `SUPERSEDED`
* `FAILED_APPROACH`
* `RAW_REASONING_TRACE`
* `POLICY_EXCLUDED`

---

### Raw Trace Archive References

Added external trace references without requiring raw trace inheritance.

---

### Inheritance Statistics

Added:

* total considered item count,
* inherited item count,
* discarded item count,
* raw trace item inheritance count,
* inheritance ratio.

---

### Goal Continuity

Added:

* `goal_hash_before`
* `goal_hash_after`
* `immutable_goal_preserved`

---

### Purification Status

Added:

* `READY_FOR_HANDOFF`
* `REQUIRES_REWORK`
* `REJECTED`

---

### Semantic Validation

Added checks for:

* generation continuity,
* inheritance count consistency,
* discard count consistency,
* inheritance ratio reproducibility,
* zero raw-trace inheritance,
* Immutable Goal continuity,
* handoff readiness.

---

### Core Invariants

Added:

* IMP-21 — Purification Transparency
* IMP-22 — Zero Raw-Trace Inheritance
* IMP-23 — Evidence / Context Separation
* IMP-24 — Classification Consistency
* IMP-25 — Inheritance Ratio Reproducibility
* IMP-26 — Immutable Goal Preservation
* IMP-27 — Handoff Readiness
* IMP-28 — Generational Continuity

---

## Changed

* Planner output is no longer conceptually treated as ordinary summarization.
* State Purification became a first-class protocol operation.

---

## Design Principle

IMP v0.3 establishes:

> **Audit determines what can be trusted.
> Purification determines what should survive.**

---

# [0.2.0] - 2026-08-17

## Added

### Shift Governor

Added the external lifecycle-control layer.

---

### Shift Governor Assessment

Added:

```text
shift-governor-assessment.schema.json
```

---

### Reasoning Health Metrics

Added:

* Context Pressure
* Error Density
* Loop Probability
* Goal Drift

---

### Handoff Score

Added weighted Handoff Score calculation.

Recommended default weights:

```text
Context Pressure    0.35
Error Density       0.25
Loop Probability    0.25
Goal Drift          0.15
```

---

### Governor Decisions

Added:

* `CONTINUE`
* `PREPARE`
* `HANDOFF`
* `EMERGENCY`

---

### Default Thresholds

Added:

```text
0.00 ≤ score < 0.40    CONTINUE
0.40 ≤ score < 0.60    PREPARE
0.60 ≤ score < 0.80    HANDOFF
0.80 ≤ score ≤ 1.00    EMERGENCY
```

---

### Anomaly Override

Added preemptive anomaly semantics.

A detected anomaly requires:

```text
decision = EMERGENCY
```

and at least one explicit anomaly reason.

---

### Validation Improvements

Added:

* weight normalization validation,
* Handoff Score reproducibility,
* threshold ordering,
* deterministic decision validation,
* anomaly override validation.

Malformed JSON is now explicitly separated from legitimate schema or semantic negative examples.

---

### Core Invariants

Added:

* IMP-13 — Governor Independence
* IMP-14 — Weight Normalization
* IMP-15 — Score Reproducibility
* IMP-16 — Ordered Thresholds
* IMP-17 — Deterministic Decision
* IMP-18 — Anomaly Override
* IMP-19 — Anomaly Explainability
* IMP-20 — Trigger Separation

---

## Design Principle

IMP v0.2 establishes:

> **The active reasoner should not be the sole judge of whether it is still fit to continue reasoning.**

---

# [0.1.0] - 2026-08-17

## Added

### Initial Protocol Kernel

Introduced the Inference Metabolism Protocol.

---

### Tri-Shift Architecture

Added:

* Builder
* Auditor
* Planner

---

### State Packet

Added:

```text
state-packet.schema.json
```

The State Packet defines the canonical Planner-to-Builder handoff object.

---

### Handoff Event

Added:

```text
handoff-event.schema.json
```

Initial triggers:

* `MILESTONE_COMPLETED`
* `ANOMALY_DETECTED`
* `CONTEXT_PRESSURE`
* `TIME_BOUNDARY`

---

### Audit Record

Added:

```text
audit-record.schema.json
```

Audit decisions:

* `PASS`
* `FAIL`
* `NEEDS_REWORK`

---

### Raw Trace Non-Inheritance

Introduced the principle that raw reasoning history MUST NOT automatically cross generational boundaries.

---

### Evidence Preservation

Introduced the separation between:

```text
Evidence Preservation
```

and:

```text
Context Inheritance
```

---

### Minimum Sufficient State

Introduced the Minimum Sufficient State concept.

---

### Immutable Goal

Added:

* goal ID,
* goal hash,
* core objective,
* definition of done.

---

### State Classification

Introduced explicit separation of:

* verified facts,
* verified artifacts,
* working assumptions,
* open issues,
* environment.

---

### Scoped Do-Not-Repeat Rules

Introduced guardrail scope and expiration semantics to reduce uncontrolled taboo accumulation.

---

### Provenance

Introduced references to:

* previous State Packet,
* Builder run,
* Audit Record,
* Planner run.

---

### Initial Validation Suite

Added:

* JSON Schema validation,
* semantic validation,
* positive examples,
* negative examples,
* `scripts/validate_examples.py`.

---

### Core Invariants

Introduced:

* IMP-01 — Raw Trace Non-Inheritance
* IMP-02 — Evidence Preservation
* IMP-03 — Verified State Preference
* IMP-04 — Goal Continuity
* IMP-05 — Role Separation
* IMP-06 — External Lifecycle Control
* IMP-07 — Anomaly Preemption
* IMP-08 — State Classification
* IMP-09 — Minimum Sufficient State
* IMP-10 — Audited Inheritance
* IMP-11 — Generation Continuity
* IMP-12 — No Silent Taboo Expansion

---

## Design Principle

IMP v0.1 established:

> **Preserve Evidence. Inherit State. Reset Reasoning.**

---

# Protocol Evolution Summary

```text
v0.1
State Handoff
"What survives?"

       ↓

v0.2
Shift Governor
"When should reasoning stop?"

       ↓

v0.3
State Purification
"Why should this survive?"

       ↓

v0.4
Cross-Record Conformance
"Was inheritance valid?"

       ↓

v0.5
Metabolism Cycle
"Did the entire lifecycle transition correctly?"
```

---

# Current Milestone

Current release:

```text
Inference Metabolism Protocol v0.5.0
```

Status:

> **First Complete Protocol Milestone**

The first complete cycle is now defined as:

```text
Preserve Evidence
      ↓
Audit Truth
      ↓
Purify State
      ↓
Verify Inheritance
      ↓
Reset Reasoning
      ↓
Continue the System
```
