# Inference Metabolism Protocol Specification

**Protocol:** Inference Metabolism Protocol
**Abbreviation:** IMP
**Release Version:** `0.5.0`
**Status:** Experimental / First Complete Protocol Milestone
**Date:** 2026-08-17

---

# 1. Introduction

The **Inference Metabolism Protocol (IMP)** is a lifecycle protocol for long-horizon AI agents.

IMP addresses a structural problem in autonomous AI systems:

> A reasoning process should not be expected to remain indefinitely healthy merely because its context window has not yet reached its technical limit.

Long-running reasoning instances may accumulate:

* stale assumptions,
* failed approaches,
* contradictory intermediate conclusions,
* repeated tool errors,
* irrelevant context,
* reasoning loops,
* excessive context pressure,
* and goal drift.

IMP does not attempt to solve these problems by indefinitely extending one reasoning context.

Instead, it introduces controlled generational turnover.

```text
Reason
  ↓
Measure
  ↓
Handoff
  ↓
Audit
  ↓
Purify
  ↓
Verify
  ↓
Reset
  ↓
Reason Again
```

The central principle is:

> **Preserve Evidence. Inherit State. Reset Reasoning.**

IMP treats reasoning termination not as system failure, but as a normal lifecycle operation.

---

# 2. Core Definition

**Inference Metabolism** is the controlled lifecycle by which an AI system:

1. terminates or suspends an active reasoning generation,
2. preserves auditable evidence,
3. verifies generated results,
4. removes unnecessary or unsafe reasoning residue,
5. distills verified and operationally necessary state,
6. validates state lineage,
7. transfers only eligible state,
8. resets the active reasoning context,
9. and begins a fresh reasoning generation.

A concise definition is:

> **Inference Metabolism Protocol (IMP) is a lifecycle protocol for sustaining long-horizon AI systems through controlled reasoning termination, audited state purification, verified inheritance, and fresh-context regeneration.**

---

# 3. Design Principle

IMP distinguishes three concepts that MUST NOT be treated as equivalent:

```text
Memory
≠
Evidence
≠
Working Context
```

Information MAY remain stored for audit purposes without being inherited into the next Builder's working context.

Therefore:

```text
Preservation
≠
Inheritance
```

IMP does not require destruction of historical evidence.

It requires controlled inheritance.

---

# 4. Protocol Goals

IMP is designed to support the following goals.

## 4.1 Long-Horizon Stability

Prevent indefinite accumulation of reasoning context from becoming the default continuity mechanism.

## 4.2 Error Isolation

Reduce the probability that a mistake in generation `N` silently becomes accepted truth in generation `N+1`.

## 4.3 Context Renewal

Allow new reasoning generations to begin from a clean working context.

## 4.4 Selective Cognitive Inheritance

Preserve only information that remains useful, valid, traceable, and operationally necessary.

## 4.5 Auditability

Make state inheritance decisions externally inspectable.

## 4.6 Goal Continuity

Prevent lifecycle turnover from silently altering the system's Immutable Goal.

## 4.7 Reasoning Efficiency

Reduce unnecessary re-reading, repeated exploration, repeated failure, and redundant re-reasoning.

---

# 5. Non-Goals

IMP v0.5 does not define:

* a specific LLM,
* a specific AI vendor,
* a specific agent framework,
* a specific prompt format,
* a universal memory database,
* a vector-store implementation,
* a reasoning algorithm,
* a causal reasoning algorithm,
* a universal anomaly detector,
* a universal context-pressure estimator,
* a universally optimal Handoff Score,
* distributed consensus,
* cryptographic identity infrastructure,
* or a complete AGI architecture.

IMP defines a lifecycle and inheritance protocol.

Reasoning engines MAY operate inside that lifecycle independently.

---

# 6. Normative Language

The terms:

* **MUST**
* **MUST NOT**
* **SHOULD**
* **SHOULD NOT**
* **MAY**

are normative requirements.

---

# 7. Protocol Versioning

The IMP release version and individual record schema versions are intentionally separate.

The protocol release described by this document is:

```text
IMP v0.5.0
```

However, records introduced in earlier releases retain their own schema versions unless their structure changes.

Current schema generations are:

```text
State Packet                         0.1.0
Handoff Event                        0.1.0
Audit Record                         0.1.0
Shift Governor Assessment            0.2.0
State Purification Record            0.3.0
Cross-Record Conformance Case        0.4.0
Metabolism Cycle Record              0.5.0
Metabolism Cycle Conformance Case    0.5.0
```

A protocol release MUST NOT require artificial schema-version increments when the corresponding record structure remains unchanged.

---

# 8. High-Level Architecture

IMP uses the following lifecycle:

```text
                    Immutable Goal
                          │
                          ▼
                  ┌───────────────┐
                  │ Builder Gen N │
                  └───────┬───────┘
                          │
                          ▼
                   Shift Governor
                          │
                          ▼
                    Handoff Event
                          │
                          ▼
                       Auditor
                          │
                          ▼
                    Audit Record
                          │
                          ▼
                 State Purification
                          │
                          ▼
              State Purification Record
                          │
                          ▼
              Cross-Record Conformance
                          │
                          ▼
                    State Packet
                          │
                   Context Reset
                          │
                          ▼
                ┌─────────────────┐
                │ Builder Gen N+1 │
                └─────────────────┘
```

The complete transition from generation `N` to generation `N+1` is called a:

> **Metabolism Cycle**

---

# 9. Tri-Shift Architecture

IMP defines three logically distinct reasoning roles.

## 9.1 Builder

The **Builder** performs active task execution.

Typical responsibilities include:

* reasoning,
* writing,
* coding,
* tool usage,
* information retrieval,
* transformation,
* implementation,
* and immediate task execution.

A Builder SHOULD focus on the `immediate_task` provided by the current State Packet.

A Builder MUST NOT silently modify the Immutable Goal.

A Builder SHOULD NOT automatically inherit raw reasoning traces from previous Builders.

---

## 9.2 Auditor

The **Auditor** evaluates the output of the Builder.

The Auditor determines what may be treated as verified.

Typical responsibilities include:

* test execution,
* artifact inspection,
* claim verification,
* inconsistency detection,
* error classification,
* evidence inspection,
* and state eligibility decisions.

The Auditor distinguishes between:

```text
Verified
Unverified
Failed
Unresolved
```

The Auditor does not determine what all future generations should inherit.

That is the responsibility of State Purification.

---

## 9.3 Planner

The **Planner** transforms audited results into a minimal executable state for the next generation.

The Planner MUST NOT act as a simple transcript summarizer.

Its core responsibility is:

> **State Purification**

The Planner decides:

* which verified facts survive,
* which verified artifacts survive,
* which assumptions remain operationally useful,
* which failures should become scoped guardrails,
* which information should be discarded from inherited context,
* and what the next Builder should do immediately.

---

# 10. Separation of Responsibilities

The three primary roles answer different questions.

```text
Builder
"What can I do now?"

Auditor
"What can be trusted?"

Planner
"What should survive?"
```

These responsibilities MUST remain logically distinguishable.

An implementation MAY use the same underlying model for multiple roles, but the role boundaries and state transitions MUST remain explicit.

---

# 11. Raw Trace Non-Inheritance

IMP distinguishes raw reasoning traces from auditable evidence.

Raw reasoning traces may include:

* chain-like execution narratives,
* exploratory attempts,
* failed intermediate plans,
* transient hypotheses,
* repetitive tool interactions,
* discarded reasoning branches,
* and conversational residue.

IMP does not require such traces to be destroyed.

They MAY be archived.

However:

> Raw reasoning traces MUST NOT be automatically copied into the next Builder's ordinary working context.

Conceptually:

```text
Raw Experience
     │
     ├──→ Audit Archive
     │
     ├──→ Provenance / Evidence
     │
     └──→ State Purification
                  │
                  ▼
             State Packet
                  │
                  ▼
            Fresh Builder
```

---

# 12. Evidence Preservation

Evidence MAY outlive a reasoning generation.

Examples include:

* test results,
* source documents,
* tool receipts,
* execution logs,
* provenance identifiers,
* artifact hashes,
* external observations,
* and archived raw traces.

Evidence preservation exists to support later:

* audit,
* dispute resolution,
* verification,
* debugging,
* reproduction,
* and forensic analysis.

Evidence preservation MUST NOT imply automatic context inheritance.

---

# 13. Minimum Sufficient State

IMP defines **Minimum Sufficient State (MSS)** as:

> The smallest state representation that allows the next Builder to correctly begin its immediate task without unnecessary reconstruction.

The conceptual optimization objective is:

```text
Minimize:

StatePacketSize
+ ReReasoningCost
+ ContextNoise

Subject to:

GoalPreservation
ConstraintPreservation
EvidenceTraceability
TaskExecutability
```

IMP v0.5 does not define a universal numerical MSS score.

A smaller State Packet is not automatically superior.

State minimization MUST NOT destroy information required for correct execution.

---

# 14. Immutable Goal

The **Immutable Goal** represents the project-level objective that MUST survive reasoning turnover.

It contains:

* `goal_id`
* `goal_hash`
* `core_objective`
* `definition_of_done`

The Immutable Goal establishes the stable reference frame against which:

* goal drift,
* planning,
* state continuity,
* and final completion

are evaluated.

A Planner MUST NOT silently change it.

---

# 15. Goal Hash Continuity

IMP uses goal hashes to detect goal mutation across generations.

For a valid transition:

```text
goal_hash_before
==
goal_hash_after
==
StatePacket.immutable_goal.goal_hash
```

A mismatch invalidates successful handoff eligibility.

IMP v0.5 defines semantic hash continuity but does not yet mandate a cryptographic signing infrastructure.

---

# 16. Shift Governor

The **Shift Governor** is an external lifecycle-control component.

Its purpose is to determine whether an active Builder remains fit to continue reasoning.

The Shift Governor MUST remain logically separate from Builder self-assessment.

The Builder MAY expose health signals.

However:

> The active reasoner MUST NOT be the sole authority deciding whether its reasoning lifecycle should continue.

---

# 17. Reasoning Health Metrics

IMP v0.2+ defines four normalized metrics.

Each metric uses the range:

```text
0.0 ≤ metric ≤ 1.0
```

## 17.1 Context Pressure

Estimates degradation caused by:

* context growth,
* irrelevant history,
* attention dispersion,
* stale state,
* or context-budget pressure.

```text
0.0 = negligible pressure
1.0 = critical pressure
```

---

## 17.2 Error Density

Measures the normalized frequency of:

* failed tool calls,
* invalid outputs,
* rejected actions,
* repeated exceptions,
* or unsuccessful retries.

---

## 17.3 Loop Probability

Estimates the probability that the active reasoning process is repeating substantially equivalent:

* actions,
* queries,
* plans,
* code changes,
* or reasoning paths.

---

## 17.4 Goal Drift

Estimates divergence between current execution behavior and the Immutable Goal.

---

# 18. Handoff Score

The Shift Governor MAY calculate:

```text
HandoffScore =
    wc × ContextPressure
  + we × ErrorDensity
  + wl × LoopProbability
  + wg × GoalDrift
```

Weights MUST sum to:

```text
1.0
```

The recommended default profile is:

```text
Context Pressure    0.35
Error Density       0.25
Loop Probability    0.25
Goal Drift          0.15
                    ────
                    1.00
```

Implementations MAY define alternative weight profiles.

---

# 19. Default Governor Thresholds

The recommended v0.5 thresholds are:

```text
0.00 ≤ score < 0.40    CONTINUE
0.40 ≤ score < 0.60    PREPARE
0.60 ≤ score < 0.80    HANDOFF
0.80 ≤ score ≤ 1.00    EMERGENCY
```

Thresholds MUST satisfy:

```text
prepare < handoff < emergency
```

---

# 20. Governor Decisions

## 20.1 CONTINUE

The Builder MAY continue ordinary execution.

---

## 20.2 PREPARE

The system SHOULD begin preparing state for potential handoff.

The Builder does not necessarily terminate immediately.

---

## 20.3 HANDOFF

The system SHOULD begin lifecycle transition.

---

## 20.4 EMERGENCY

The active Builder SHOULD be suspended or terminated and immediately routed toward the audit path.

An EMERGENCY decision requires interrupt semantics.

---

# 21. Handoff Trigger Types

IMP defines four primary handoff trigger types.

## 21.1 MILESTONE_COMPLETED

A meaningful task unit has completed.

This is normally a semantic handoff trigger.

Default mode:

```text
NORMAL
```

---

## 21.2 CONTEXT_PRESSURE

Reasoning health has degraded sufficiently because of context pressure.

In a full Metabolism Cycle this trigger requires a Shift Governor Assessment.

Normal threshold-based handoff typically uses:

```text
NORMAL
```

An associated Governor `EMERGENCY` decision requires:

```text
INTERRUPT
```

---

## 21.3 TIME_BOUNDARY

An external timing, scheduling, SLA, synchronization, or operational boundary requires turnover.

Default mode:

```text
NORMAL
```

---

## 21.4 ANOMALY_DETECTED

An abnormal reasoning condition has been detected.

Examples include:

* repeated tool failure,
* runaway retry behavior,
* strong reasoning loop evidence,
* contradictory execution state,
* severe goal drift,
* or other explicitly classified abnormalities.

Mode:

```text
INTERRUPT
```

In a full v0.5 Metabolism Cycle, this trigger requires a Shift Governor Assessment.

---

# 22. Trigger Separation

IMP distinguishes:

## Semantic / External Triggers

```text
MILESTONE_COMPLETED
TIME_BOUNDARY
```

These MAY initiate normal turnover independently of a Handoff Score.

## Reasoning-Health Triggers

```text
CONTEXT_PRESSURE
ANOMALY_DETECTED
```

These require Governor involvement in full-cycle conformance.

This prevents unrelated lifecycle concepts from being collapsed into one numerical score.

---

# 23. Anomaly Override

An anomaly is not merely another weighted metric.

If:

```text
anomaly_override.detected = true
```

the Governor decision MUST be:

```text
EMERGENCY
```

At least one explicit anomaly reason MUST be provided.

Anomaly override supersedes ordinary score-based continuation.

---

# 24. Handoff Event

The **Handoff Event** records the transition from Builder execution into the audit path.

Core fields include:

* `handoff_event_id`
* `current_generation`
* `next_generation`
* `occurred_at`
* `trigger`
* `source_role`
* `destination_role`

The standard transition is:

```text
BUILDER
   ↓
AUDITOR
```

Generation continuity MUST satisfy:

```text
next_generation
=
current_generation + 1
```

---

# 25. Audit Record

The **Audit Record** represents Auditor output.

It contains:

* audit identifier,
* generation,
* auditor run identifier,
* findings,
* verified facts,
* verified artifacts,
* decision,
* and state inheritance eligibility.

Supported decisions are:

```text
PASS
FAIL
NEEDS_REWORK
```

Eligibility semantics are:

```text
PASS
→ state_eligible = true

FAIL
→ state_eligible = false

NEEDS_REWORK
→ state_eligible = false
```

---

# 26. Audit versus Purification

Audit and Purification MUST NOT be treated as the same operation.

Audit answers:

> **What information can be trusted?**

Purification answers:

> **What trusted or operational information should survive?**

Therefore:

```text
Audit Eligibility
≠
Inheritance Eligibility
```

---

# 27. State Purification

**State Purification** transforms audited experience into inheritable state.

Conceptually:

```text
Filter
  +
Verify
  +
Classify
  +
Distill
  +
Reconstruct
  =
State Purification
```

Pipeline:

```text
Audited Experience
       │
       ▼
     Filter
       │
       ▼
    Classify
       │
       ├── Verified Fact
       ├── Verified Artifact
       ├── Working Assumption
       ├── Scoped Guardrail
       └── Discard
       │
       ▼
Minimum Sufficient State
       │
       ▼
State Packet
```

---

# 28. State Purification Record

The **State Purification Record** makes inheritance decisions auditable.

It records:

* source generation,
* target generation,
* source Audit Record,
* source Builder,
* Planner,
* previous State Packet,
* archived raw-trace references,
* retained verified facts,
* retained verified artifacts,
* carried assumptions,
* generated guardrails,
* discarded items,
* inheritance statistics,
* goal continuity,
* evidence continuity,
* and resulting State Packet eligibility.

---

# 29. Verified Facts

A retained verified fact MUST:

* have passed audit,
* remain explicitly represented as a fact,
* and retain one or more evidence references.

A Planner MUST NOT silently promote an unaudited claim into a verified fact.

---

# 30. Verified Artifacts

A retained artifact MUST have Auditor-approved status.

The State Purification Record uses:

```text
VERIFIED_PASS
```

for inheritable verified artifacts.

A Planner MUST NOT silently promote an unaudited artifact into verified inherited state.

---

# 31. Working Assumptions

Not all operationally useful information can immediately be verified.

A working assumption MAY survive State Purification if it remains useful.

It MUST remain explicitly classified as:

```text
working_assumption
```

and MUST NOT silently become a verified fact.

Typical fields include:

* assumption ID,
* statement,
* confidence,
* whether validation remains necessary,
* and the reason it was retained.

---

# 32. Scoped Guardrails

A failed approach MAY generate a future guardrail.

However:

> A historical failure MUST NOT automatically become a permanent universal prohibition.

A guardrail SHOULD include:

* rule identifier,
* source reference,
* prohibited action,
* reason,
* scope,
* expiration condition.

Supported scope concepts include:

```text
GENERATION
PROJECT
UNTIL_CONDITION
```

This prevents **Taboo Accumulation** from progressively shrinking the agent's valid action space without justification.

---

# 33. Discarded Items

State Purification SHOULD explicitly record why information was excluded from inheritance.

Supported reason codes include:

```text
IRRELEVANT
DUPLICATE
STALE
UNSUPPORTED
SUPERSEDED
FAILED_APPROACH
RAW_REASONING_TRACE
POLICY_EXCLUDED
```

Discarding an item from inherited working context does not necessarily imply destruction of its source evidence.

---

# 34. Inheritance Statistics

The State Purification Record contains:

* `total_considered_item_count`
* `inherited_item_count`
* `discarded_item_count`
* `raw_trace_items_inherited`
* `inheritance_ratio`

The ratio is:

```text
InheritanceRatio =
    InheritedItemCount
    /
    TotalConsideredItemCount
```

IMP v0.5 does not define an ideal ratio.

A lower inheritance ratio is not automatically better.

---

# 35. Purification Readiness

Supported purification outcomes are:

```text
READY_FOR_HANDOFF
REQUIRES_REWORK
REJECTED
```

## READY_FOR_HANDOFF

Requires successful:

* Immutable Goal preservation,
* evidence traceability,
* fact/assumption separation,
* Minimum Sufficient State assessment.

A resulting State Packet ID MUST exist.

## REQUIRES_REWORK

The current purified state is not yet safe or sufficient for transfer.

## REJECTED

The attempted inheritance state MUST NOT cross the generation boundary.

---

# 36. State Packet

The **State Packet** is the canonical Planner-to-Builder transfer object.

Its top-level structure is:

```text
StatePacket
├── schema_version
├── packet_metadata
├── inheritance_policy
├── provenance
├── immutable_goal
├── current_state
├── execution_plan
├── constraints_and_guardrails
└── integrity
```

The State Packet is not a transcript summary.

It represents the minimum verified and operational state required by the next Builder.

---

# 37. State Packet Metadata

`packet_metadata` includes:

* packet identifier,
* generation,
* creation time,
* handoff reason.

The packet generation identifies the Builder generation that consumes the packet.

---

# 38. Inheritance Policy

IMP v0.5 expects a Builder-consumable State Packet to declare:

```text
raw_trace_inherited        = false
evidence_preserved         = true
minimum_sufficient_state   = true
```

This expresses the core IMP inheritance policy.

---

# 39. State Packet Provenance

The State Packet retains references to its lineage, including:

* previous State Packet,
* Builder run,
* Audit Record,
* Planner run.

The State Packet does not need raw historical reasoning in order to preserve its origin chain.

---

# 40. Current State

The State Packet distinguishes:

```text
verified_facts
verified_artifacts
working_assumptions
open_issues
environment
```

This explicit separation is intended to reduce hallucination inheritance.

---

# 41. Execution Plan

The State Packet contains:

```text
immediate_task
subsequent_milestones
```

The `immediate_task` SHOULD be sufficiently concrete that the next Builder can begin execution without reconstructing the entire historical conversation.

Typical fields include:

* task identifier,
* title,
* instruction,
* expected output.

---

# 42. Constraints and Guardrails

The State Packet MAY include:

* `do_not_repeat`
* `resource_budgets`

The purpose is to prevent unnecessary recurrence of known failures while bounding execution cost.

---

# 43. Integrity

A Builder-consumable State Packet MUST have:

```text
audit_status = VERIFIED
```

Future IMP versions MAY require:

* packet hash validation,
* Planner signatures,
* Auditor signatures,
* or external verification receipts.

---

# 44. Cross-Record Conformance

Independent record validity is insufficient.

The following situation is invalid even if all records individually satisfy their schemas:

```text
Audit Record:
    verified facts = A

Purification:
    retained facts = A, B

State Packet:
    verified facts = A, B
```

`B` was never accepted by the Auditor.

IMP v0.4+ therefore requires:

> **Cross-Record Conformance**

---

# 45. Audit-to-Purification Closure

A Planner MUST NOT create new verified state that was not accepted by the associated Audit Record.

Therefore:

```text
PurifiedVerifiedFacts
⊆
AuditedVerifiedFacts
```

and:

```text
PurifiedVerifiedArtifacts
⊆
AuditedVerifiedArtifacts
```

---

# 46. Purification-to-Packet Closure

For the currently standardized inheritance classes:

```text
Purified Verified Facts
==
Packet Verified Facts
```

```text
Purified Verified Artifacts
==
Packet Verified Artifacts
```

```text
Purified Working Assumptions
==
Packet Working Assumptions
```

```text
Generated Guardrails
==
Packet Do-Not-Repeat Guardrails
```

This prevents state from bypassing Purification.

---

# 47. Cross-Record Generation Closure

A valid chain requires:

```text
Audit.generation
==
Purification.source_generation
```

and:

```text
Purification.target_generation
==
StatePacket.generation
```

Thus:

```text
Generation N Audit
        ↓
N → N+1 Purification
        ↓
Generation N+1 State Packet
```

---

# 48. Cross-Record Provenance Closure

The following identifiers MUST remain mutually consistent:

* Audit Record ID,
* Builder run ID,
* Planner run ID,
* previous State Packet ID,
* resulting State Packet ID.

The intended lineage is:

```text
Builder Run
    ↓
Audit Record
    ↓
Planner Run
    ↓
State Purification Record
    ↓
State Packet
```

---

# 49. Cross-Record Goal Closure

The post-purification goal hash MUST equal the State Packet Immutable Goal hash.

A mismatch invalidates inheritance.

---

# 50. Cross-Record Conformance Cases

`cross-record-conformance-case` is a test harness record.

It references:

* an Audit Record,
* a State Purification Record,
* a State Packet,
* expected result,
* expected violation codes.

It is intended for:

* CI,
* validator testing,
* protocol conformance suites,
* and negative examples.

It is not an ordinary runtime reasoning record.

---

# 51. Metabolism Cycle

IMP v0.5 defines the **Metabolism Cycle** as the canonical lifecycle unit.

One cycle transitions:

```text
Generation N
→
Generation N+1
```

The complete model is:

```text
State(N)
   │
   ▼
Builder(N)
   │
   ▼
Governor
   │
   ▼
Handoff
   │
   ▼
Audit
   │
   ▼
Purification
   │
   ▼
Cross-Record Conformance
   │
   ▼
State(N+1)
```

---

# 52. Metabolism Cycle Record

The Metabolism Cycle Record contains:

* cycle identifier,
* source generation,
* target generation,
* lifecycle record references,
* trigger information,
* continuity information,
* and final outcome.

Referenced lifecycle records include:

* source State Packet,
* Shift Governor Assessment when applicable,
* Handoff Event,
* Audit Record,
* State Purification Record,
* output State Packet.

---

# 53. Lifecycle Gates

A successful v0.5 cycle contains the following conceptual gates.

```text
1. Governor Gate
2. Handoff Gate
3. Audit Gate
4. Purification Gate
5. Cross-Record Gate
6. Goal Continuity Gate
7. Raw-Trace Non-Inheritance Gate
8. Evidence Preservation Gate
9. Packet Verification Gate
```

Failure at a required gate prevents valid cycle completion.

---

# 54. Governor Gate

For reasoning-health triggers:

```text
CONTEXT_PRESSURE
ANOMALY_DETECTED
```

a full Metabolism Cycle requires a Shift Governor Assessment.

A lifecycle transition controlled by the Governor MUST NOT proceed while the decision is:

```text
CONTINUE
PREPARE
```

Valid turnover decisions are:

```text
HANDOFF
EMERGENCY
```

---

# 55. Interrupt Semantics

A handoff MUST use:

```text
INTERRUPT
```

when:

```text
trigger = ANOMALY_DETECTED
```

or:

```text
Governor decision = EMERGENCY
```

This means that a trigger such as `CONTEXT_PRESSURE` MAY still use `INTERRUPT` when the associated Governor assessment reaches `EMERGENCY`.

---

# 56. Audit Gate

A cycle marked `COMPLETED` requires:

```text
Audit.decision == PASS
```

and:

```text
Audit.state_eligible == true
```

A failed audit MUST NOT directly feed a fresh Builder generation.

---

# 57. Purification Gate

A completed cycle requires:

```text
Purification.output.status
==
READY_FOR_HANDOFF
```

`REQUIRES_REWORK` and `REJECTED` do not authorize normal next-generation execution.

---

# 58. Cross-Record Gate

The chain:

```text
Audit
→ Purification
→ State Packet
```

MUST pass Cross-Record Conformance.

A Metabolism Cycle MUST NOT be marked successfully completed if this chain fails.

---

# 59. Goal Continuity Gate

The cycle must preserve:

```text
goal_hash_before
==
goal_hash_after
==
StatePacket.goal_hash
```

and declare:

```text
immutable_goal_preserved = true
```

---

# 60. Raw-Trace Non-Inheritance Gate

A completed cycle requires:

```text
raw_trace_inherited = false
```

and the State Purification Record requires:

```text
raw_trace_items_inherited = 0
```

Raw traces MAY remain externally archived.

---

# 61. Evidence Preservation Gate

A completed cycle requires preserved auditability.

At minimum:

```text
cycle.evidence_preserved = true
```

```text
StatePacket.inheritance_policy.evidence_preserved = true
```

```text
Purification.evidence_traceability_preserved = true
```

---

# 62. Packet Verification Gate

The output State Packet requires:

```text
integrity.audit_status
==
VERIFIED
```

before normal next-generation Builder execution.

---

# 63. Cycle Outcomes

IMP v0.5 defines:

```text
COMPLETED
REQUIRES_REWORK
ABORTED
```

---

## 63.1 COMPLETED

All required lifecycle gates have passed.

Only a completed cycle MAY declare:

```text
next_builder_eligible = true
```

---

## 63.2 REQUIRES_REWORK

The cycle has not yet produced a valid transferable state.

It MUST declare:

```text
next_builder_eligible = false
```

---

## 63.3 ABORTED

The cycle has terminated without producing an eligible next-generation state.

It MUST declare:

```text
next_builder_eligible = false
```

---

# 64. Builder Eligibility

A new Builder MAY begin normal operation only after a valid lifecycle transition authorizes it.

For v0.5:

```text
Cycle.status == COMPLETED
AND
next_builder_eligible == true
```

represents successful generational turnover.

---

# 65. Metabolism Cycle Conformance Cases

`metabolism-cycle-conformance-case` is the v0.5 test harness for complete lifecycle validation.

A test case may reference:

* Metabolism Cycle Record,
* Shift Governor Assessment,
* Handoff Event,
* Audit Record,
* State Purification Record,
* output State Packet.

The conformance harness compares actual violations against declared expected violation codes.

---

# 66. Conformance Levels

IMP v0.5 defines five practical validation levels.

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

A complete IMP v0.5 conformance suite SHOULD exercise all five levels.

---

# 67. Syntax Conformance

All protocol examples MUST be valid JSON.

Malformed JSON MUST NOT be treated as an acceptable negative Schema or Semantic conformance example.

This distinction prevents broken fixture files from being mistaken for meaningful protocol violations.

---

# 68. Record-Local Conformance

Each record is independently tested against:

1. JSON syntax,
2. its corresponding JSON Schema,
3. record-local semantic invariants.

Examples include:

* generation continuity,
* audit eligibility,
* Handoff Score reproducibility,
* threshold ordering,
* anomaly override semantics,
* inheritance count consistency,
* goal continuity.

---

# 69. Cross-Record Conformance

Cross-record validation tests information lineage between:

```text
Audit
→ Purification
→ Packet
```

It exists primarily to detect:

* unaudited fact promotion,
* unaudited artifact promotion,
* bypassed purification,
* provenance mismatch,
* generation mismatch,
* and goal-hash divergence.

---

# 70. Full-Cycle Conformance

Metabolism Cycle Conformance validates:

```text
Governor
→ Handoff
→ Audit
→ Purification
→ Cross-Record Validation
→ Packet
→ Builder Eligibility
```

This represents the highest conformance level standardized by IMP v0.5.

---

# 71. Core Invariants

IMP v0.5 defines the following invariants.

## IMP-01 — Raw Trace Non-Inheritance

Raw reasoning traces MUST NOT be automatically inherited by a new Builder.

## IMP-02 — Evidence Preservation

Evidence MAY remain available outside inherited working context.

## IMP-03 — Verified State Preference

Verified information SHOULD be preferred over reconstructed historical narrative.

## IMP-04 — Goal Continuity

The Immutable Goal MUST persist across reasoning generations.

## IMP-05 — Role Separation

Builder, Auditor, and Planner responsibilities MUST remain logically distinguishable.

## IMP-06 — External Lifecycle Control

Builder lifetime MUST NOT depend solely on Builder self-assessment.

## IMP-07 — Anomaly Preemption

`ANOMALY_DETECTED` MUST use interrupt semantics.

## IMP-08 — State Classification

Verified facts and working assumptions MUST remain distinguishable.

## IMP-09 — Minimum Sufficient State

The Planner SHOULD avoid unnecessary inherited context.

## IMP-10 — Audited Inheritance

A Builder-consumable State Packet MUST have verified audit status.

## IMP-11 — Generation Continuity

Generation numbers MUST progress monotonically across handoff.

## IMP-12 — No Silent Taboo Expansion

Historical failure MUST NOT automatically become a permanent universal prohibition.

---

## IMP-13 — Governor Independence

The Shift Governor MUST remain logically independent from Builder self-assessment.

## IMP-14 — Weight Normalization

Handoff Score weights MUST sum to `1.0`.

## IMP-15 — Score Reproducibility

A declared Handoff Score MUST equal the weighted result of its declared metrics and weights.

## IMP-16 — Ordered Thresholds

Governor thresholds MUST satisfy:

```text
prepare < handoff < emergency
```

## IMP-17 — Deterministic Decision

Without anomaly override, Governor decisions MUST correspond to the declared score and thresholds.

## IMP-18 — Anomaly Override

A detected anomaly MUST override ordinary score-based continuation.

## IMP-19 — Anomaly Explainability

A detected anomaly MUST contain at least one explicit reason.

## IMP-20 — Trigger Separation

Semantic/external handoff triggers MUST remain conceptually distinguishable from reasoning-health metrics.

---

## IMP-21 — Purification Transparency

State inheritance decisions SHOULD be explicitly represented rather than hidden inside an unstructured summary.

## IMP-22 — Zero Raw-Trace Inheritance

The number of raw reasoning trace items inherited into ordinary Builder context MUST equal zero.

## IMP-23 — Evidence / Context Separation

Evidence MAY remain archived even when the corresponding raw reasoning trace is excluded from inherited context.

## IMP-24 — Classification Consistency

Inherited and discarded item counts MUST correspond to represented purification classifications.

## IMP-25 — Inheritance Ratio Reproducibility

The declared inheritance ratio MUST be reproducible from declared item counts.

## IMP-26 — Immutable Goal Preservation

A Purification Record marked `READY_FOR_HANDOFF` MUST preserve the Immutable Goal.

## IMP-27 — Handoff Readiness

`READY_FOR_HANDOFF` requires successful continuity checks.

## IMP-28 — Generational Continuity

Purification target generation MUST equal source generation plus one.

---

## IMP-29 — Cross-Record Lineage

Audit Record, State Purification Record, and State Packet MUST form a consistent lineage.

## IMP-30 — Generation Alignment

Audit generation MUST equal purification source generation, and purification target generation MUST equal State Packet generation.

## IMP-31 — Audited Fact Origin

A verified fact retained by State Purification MUST originate from the associated Audit Record.

## IMP-32 — Audited Artifact Origin

A verified artifact retained by State Purification MUST originate from the associated Audit Record.

## IMP-33 — Fact Closure

State Packet verified facts MUST equal the verified facts retained by State Purification.

## IMP-34 — Artifact Closure

State Packet verified artifacts MUST equal the verified artifacts retained by State Purification.

## IMP-35 — Assumption Closure

Inherited working assumptions MUST correspond to assumptions explicitly carried through State Purification.

## IMP-36 — Guardrail Closure

Inherited do-not-repeat guardrails MUST correspond to guardrails explicitly generated by State Purification.

## IMP-37 — Goal Hash Continuity

The post-purification goal hash MUST equal the Immutable Goal hash in the resulting State Packet.

## IMP-38 — Provenance Closure

Builder, Planner, Audit Record, previous Packet, and resulting Packet identifiers MUST form a consistent provenance chain.

---

## IMP-39 — Metabolism Cycle Closure

A complete generation transition MUST be representable as one Metabolism Cycle.

## IMP-40 — Source Generation Closure

Governor, Handoff Event, Audit Record, and Purification source generation MUST correspond to the cycle source generation where applicable.

## IMP-41 — Target Generation Closure

Handoff target generation, Purification target generation, and output State Packet generation MUST correspond to the cycle target generation.

## IMP-42 — Lifecycle Reference Closure

Lifecycle record identifiers declared by the Metabolism Cycle MUST resolve consistently to the records used by that cycle.

## IMP-43 — Governor Handoff Eligibility

A Governor-controlled lifecycle transition MUST NOT execute while the Governor decision is `CONTINUE` or `PREPARE`.

## IMP-44 — Interrupt Semantics

`ANOMALY_DETECTED` or Governor decision `EMERGENCY` MUST result in `INTERRUPT` handoff semantics.

## IMP-45 — Audit Gate

A completed cycle MUST contain an Audit Record with:

```text
decision = PASS
state_eligible = true
```

## IMP-46 — Purification Gate

A completed cycle MUST contain a Purification Record marked `READY_FOR_HANDOFF`.

## IMP-47 — Packet Verification Gate

The resulting State Packet of a completed cycle MUST be `VERIFIED`.

## IMP-48 — Cross-Record Gate

A Metabolism Cycle MUST NOT be marked `COMPLETED` when Cross-Record Conformance fails.

## IMP-49 — Evidence / Trace Continuity

A completed cycle MUST preserve auditable evidence while preventing raw reasoning trace inheritance.

## IMP-50 — Builder Eligibility

Only a valid completed Metabolism Cycle MAY authorize the next Builder generation.

---

# 72. Lifecycle Summary

IMP v0.5 can be summarized as:

```text
Experience
    ↓
Builder
    ↓
Reasoning Health Measurement
    ↓
Shift Governor
    ↓
Handoff
    ↓
Audit
    ↓
State Purification
    ↓
Inheritance Classification
    ↓
Cross-Record Verification
    ↓
State Packet
    ↓
Context Reset
    ↓
Fresh Builder
```

---

# 73. Protocol Kernel

The minimum conceptual kernel is:

```text
Execute
→ Measure
→ Handoff
→ Audit
→ Purify
→ Verify
→ Transfer
→ Reset
→ Execute
```

---

# 74. Metabolism versus Summarization

IMP State Purification MUST NOT be understood as ordinary conversation summarization.

Summarization asks:

> What happened?

State Purification asks:

> What remains valid, necessary, traceable, and executable after this reasoning generation ends?

The distinction is fundamental.

---

# 75. Metabolism versus Long-Term Memory

IMP does not prohibit long-term memory.

Instead, it separates:

```text
Persistent Memory
External Evidence
Working Context
Inherited State
```

Long-term memory MAY provide evidence or reference material.

It MUST NOT automatically override inheritance classification or audit requirements.

---

# 76. Metabolism versus Context Compression

IMP MAY use context compression techniques internally.

However, context compression alone does not satisfy IMP.

IMP additionally requires lifecycle semantics including:

* explicit reasoning termination,
* audit,
* state classification,
* inheritance eligibility,
* goal continuity,
* provenance,
* and fresh-context regeneration.

Therefore:

```text
Context Compression
⊂ possible IMP implementation technique
```

but:

```text
Context Compression
≠ IMP
```

---

# 77. Metabolism versus Reasoning Engines

IMP does not prescribe how a Builder reasons.

External reasoning engines MAY include:

* planning,
* causal reconstruction,
* code reasoning,
* retrieval,
* mathematical reasoning,
* counterfactual reasoning,
* search,
* simulation,
* or domain-specific inference.

IMP manages their lifecycle.

It does not replace them.

---

# 78. Security and Integrity Considerations

Implementers SHOULD consider the following risks.

## 78.1 State Injection

Untrusted information may be inserted into the State Packet.

Mitigation:

* Audit eligibility,
* Cross-Record Conformance,
* provenance validation.

## 78.2 Hallucination Inheritance

Unsupported claims may cross generations.

Mitigation:

* verified fact origin rules,
* assumption separation,
* Fact Closure.

## 78.3 Goal Mutation

The Planner may unintentionally or maliciously change system objectives.

Mitigation:

* Immutable Goal,
* goal hash continuity.

## 78.4 Guardrail Accumulation

Historical failures may become excessive permanent restrictions.

Mitigation:

* scoped guardrails,
* reason fields,
* expiration conditions.

## 78.5 Evidence Loss

Aggressive purification may destroy auditability.

Mitigation:

* evidence preservation,
* archive references,
* evidence traceability checks.

## 78.6 False Completion

A system may declare successful turnover despite unresolved lifecycle failures.

Mitigation:

* Metabolism Cycle gates,
* `next_builder_eligible`,
* full-cycle conformance.

---

# 79. Efficiency Considerations

IMP aims to reduce unnecessary computational work caused by:

* re-reading full histories,
* rediscovering current state,
* repeatedly testing rejected approaches,
* repeatedly reconstructing project objectives,
* context search overhead,
* and reasoning loops.

IMP therefore attempts to preserve:

```text
Necessary New Reasoning
```

while reducing:

```text
Unnecessary Re-Reasoning
```

This is a design objective, not yet a guaranteed performance claim.

---

# 80. Implementation Neutrality

IMP is framework-independent.

Potential adapters MAY be implemented for:

* LangGraph,
* AutoGen,
* CrewAI,
* custom Python orchestrators,
* distributed agent systems,
* local model runtimes,
* or future agent frameworks.

Framework-specific behavior MUST NOT redefine core IMP invariants without declaring a separate profile.

---

# 81. Validation

The reference repository SHOULD validate examples using:

```bash
python scripts/validate_examples.py
```

A successful v0.5 validation run should terminate with:

```text
=== RESULT: PASS ===
```

The validator SHOULD cover:

```text
[pass examples]

[fail examples]

[cross-record conformance: pass]

[cross-record conformance: fail]

[metabolism-cycle conformance: pass]

[metabolism-cycle conformance: fail]
```

---

# 82. Expected Validation Layers

A complete reference validation run should conceptually establish:

```text
JSON valid
    ↓
Schema valid
    ↓
Record semantics valid
    ↓
Inheritance chain valid
    ↓
Metabolism Cycle valid
```

Only then is a full-cycle test considered conformant.

---

# 83. Compatibility

IMP v0.5 is designed as an additive progression from v0.1 through v0.4.

The protocol evolution is:

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

# 84. Known Limitations

IMP v0.5 does not yet standardize:

* automatic context-pressure measurement,
* universal loop-detection algorithms,
* standardized error-density observation windows,
* standardized goal-drift measurement,
* numerical Minimum Sufficient State quality,
* Metabolism Efficiency Score,
* open-issue cross-record closure,
* execution-plan cross-record closure,
* environment-state closure,
* resource-budget closure,
* discarded-item resurrection detection,
* cryptographic record signatures,
* distributed lifecycle consensus,
* parallel Builder semantics,
* or production framework adapters.

---

# 85. Future Work

Potential post-v0.5 work includes:

## Evaluation

* long-horizon benchmark design,
* Full History baseline,
* Sliding Window baseline,
* Summary Compression baseline,
* RAG / Long-Term Memory baseline,
* context-compression baseline,
* IMP baseline.

Potential metrics include:

* Task Success Rate,
* Goal Drift Rate,
* Error Inheritance Rate,
* Constraint Preservation Rate,
* State Survival Rate,
* repeated-error frequency,
* token consumption,
* tool-call count,
* latency,
* total cost,
* and State Packet size.

## Minimum Sufficient State

Future versions MAY define quantitative MSS scoring.

## Metabolism Efficiency

A future metric MAY examine the relationship between:

```text
State Size
Re-Reasoning Cost
Task Success
Context Noise
```

## Cryptographic Integrity

Future versions MAY define:

* packet hashes,
* signatures,
* external verification receipts,
* immutable goal commitments.

## Runtime Adapters

Reference adapters MAY be developed for major agent frameworks.

---

# 86. Reference Design Philosophy

IMP rejects two extremes.

## Preserve Everything

```text
Everything remembered
→ context grows
→ noise grows
→ old errors remain active
```

## Forget Everything

```text
Everything discarded
→ context clean
→ useful state lost
→ expensive reconstruction
```

IMP instead uses:

> **Selective Cognitive Inheritance**

```text
Evidence preserved
+
Verified state inherited
+
Raw reasoning retired
+
Fresh context restored
```

---

# 87. Final Principle

IMP does not attempt to make one reasoning instance live forever.

It attempts to make the intelligent system survive by allowing individual reasoning contexts to end safely.

The core lifecycle principle is:

> **Short-lived reasoning instances can compose a long-lived intelligent system when state inheritance is controlled, audited, purified, and verifiable.**

Or more compactly:

> **Do not preserve the reasoning process indefinitely. Preserve what remains valid after it ends.**

---

# 88. Protocol Status

IMP v0.5 represents the **first complete protocol milestone**.

It defines:

* what survives,
* what does not survive,
* when reasoning may continue,
* when reasoning should terminate,
* how outputs are audited,
* how state is purified,
* how inheritance is verified,
* how generational continuity is represented,
* and when a fresh Builder may begin.

The canonical lifecycle is:

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

**End of Inference Metabolism Protocol Specification v0.5.0**
