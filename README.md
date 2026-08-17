# Inference Metabolism Protocol

**Inference Metabolism Protocol (IMP)** is a lifecycle protocol for long-horizon AI agents.

Instead of indefinitely extending a single reasoning context, IMP periodically evaluates reasoning health, performs controlled handoff, audits outputs, purifies inheritable state, verifies lineage, resets the active context, and starts a fresh reasoning generation.

> **Preserve Evidence. Inherit State. Reset Reasoning.**

---

## Overview

Long-running AI agents may accumulate:

* stale assumptions,
* repeated errors,
* failed reasoning paths,
* irrelevant context,
* contradictory intermediate conclusions,
* excessive context pressure,
* reasoning loops,
* and goal drift.

IMP treats these not merely as memory-management problems, but as **reasoning lifecycle problems**.

The protocol introduces controlled generational turnover:

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

The transition from generation `N` to generation `N+1` is called a:

> **Metabolism Cycle**

---

# Why IMP?

A large context window does not guarantee a healthy reasoning process.

A long-running agent may still:

* repeatedly revisit failed approaches,
* inherit unsupported assumptions,
* lose attention to the original goal,
* confuse historical speculation with verified facts,
* waste tokens reconstructing already-known state,
* or become trapped in self-referential error loops.

A common response is to preserve more history.

IMP explores the opposite direction:

> **Do not preserve the reasoning process indefinitely. Preserve what remains valid after it ends.**

---

# Core Principle

IMP distinguishes:

```text
Memory
≠
Evidence
≠
Working Context
≠
Inherited State
```

Historical logs MAY remain stored.

Evidence MAY remain auditable.

But raw reasoning traces MUST NOT automatically enter the next Builder's working context.

Therefore:

```text
Preservation
≠
Inheritance
```

---

# Inference Metabolism

IMP defines **Inference Metabolism** as the controlled lifecycle by which an AI system:

1. performs active reasoning,
2. measures reasoning health,
3. initiates handoff when required,
4. audits generated results,
5. filters and classifies state,
6. removes unnecessary reasoning residue from inheritance,
7. preserves auditable evidence,
8. validates state lineage,
9. transfers only eligible state,
10. resets the working context,
11. starts a fresh reasoning generation.

The protocol kernel is:

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

# Tri-Shift Architecture

IMP separates three logical responsibilities.

## Builder

The **Builder** performs active execution.

Typical activities include:

* reasoning,
* coding,
* tool usage,
* retrieval,
* implementation,
* transformation,
* and task completion.

The Builder SHOULD concentrate on the immediate task defined by the current State Packet.

---

## Auditor

The **Auditor** determines what can be trusted.

Typical responsibilities include:

* test execution,
* claim verification,
* artifact inspection,
* error classification,
* evidence review,
* and inheritance eligibility.

The Auditor answers:

> **What is verified?**

---

## Planner

The **Planner** determines what should survive.

The Planner does not simply summarize the previous conversation.

Its primary responsibility is:

> **State Purification**

The Planner answers:

> **What remains valid, necessary, traceable, and executable after this reasoning generation ends?**

---

# Shift Governor

The **Shift Governor** is an external lifecycle-control component.

It evaluates whether the active Builder remains fit to continue reasoning.

The Builder MUST NOT be the sole judge of its own lifecycle.

IMP currently defines four reasoning-health metrics:

* `context_pressure`
* `error_density`
* `loop_probability`
* `goal_drift`

A Handoff Score MAY be calculated as:

```text
HandoffScore =
    wc × ContextPressure
  + we × ErrorDensity
  + wl × LoopProbability
  + wg × GoalDrift
```

Recommended default weights:

```text
Context Pressure    0.35
Error Density       0.25
Loop Probability    0.25
Goal Drift          0.15
                    ────
                    1.00
```

Recommended default thresholds:

```text
0.00 ≤ score < 0.40    CONTINUE
0.40 ≤ score < 0.60    PREPARE
0.60 ≤ score < 0.80    HANDOFF
0.80 ≤ score ≤ 1.00    EMERGENCY
```

---

# Handoff Triggers

IMP defines four handoff trigger types.

## `MILESTONE_COMPLETED`

A meaningful unit of work has completed.

Typical mode:

```text
NORMAL
```

## `CONTEXT_PRESSURE`

Reasoning quality or context budget pressure has crossed an operational threshold.

Typical threshold-based mode:

```text
NORMAL
```

If the Shift Governor returns `EMERGENCY`, the mode becomes:

```text
INTERRUPT
```

## `TIME_BOUNDARY`

An external scheduling, synchronization, SLA, or operational boundary requires turnover.

Typical mode:

```text
NORMAL
```

## `ANOMALY_DETECTED`

An abnormal condition such as repeated tool failure, severe loop behavior, or major goal drift has been detected.

Required mode:

```text
INTERRUPT
```

---

# State Purification

State Purification converts audited experience into inheritable state.

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

State Purification is not ordinary summarization.

Summarization asks:

> What happened?

State Purification asks:

> What should survive?

---

# Selective Cognitive Inheritance

IMP does not advocate preserving everything.

It also does not advocate forgetting everything.

Instead, it uses:

> **Selective Cognitive Inheritance**

```text
Evidence preserved
+
Verified state inherited
+
Working assumptions labeled
+
Guardrails scoped
+
Raw reasoning retired
+
Fresh context restored
```

---

# Minimum Sufficient State

IMP defines **Minimum Sufficient State (MSS)** as:

> The smallest state representation that allows the next Builder to correctly begin its immediate task without unnecessary reconstruction.

Conceptually:

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

IMP v0.5 does not yet define a universal numerical MSS score.

---

# State Packet

The **State Packet** is the canonical Planner-to-Builder transfer object.

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

A Builder-consumable State Packet is expected to declare:

```text
raw_trace_inherited        = false
evidence_preserved         = true
minimum_sufficient_state   = true
```

and:

```text
audit_status = VERIFIED
```

---

# Current State Classification

IMP explicitly distinguishes:

```text
verified_facts
verified_artifacts
working_assumptions
open_issues
environment
```

This separation is designed to reduce **hallucination inheritance**.

A working assumption MUST NOT silently become a verified fact.

---

# Scoped Guardrails

Past failures MAY become `do_not_repeat` guardrails.

However:

> A failed historical approach is not automatically wrong forever.

Guardrails therefore include scope and expiration semantics.

Typical scopes:

```text
GENERATION
PROJECT
UNTIL_CONDITION
```

This reduces the risk of uncontrolled **Taboo Accumulation**.

---

# Raw Trace Non-Inheritance

Raw reasoning traces MAY be archived.

They MUST NOT automatically enter the next Builder's ordinary working context.

```text
Raw Experience
     │
     ├──→ Evidence / Archive
     │
     └──→ State Purification
                  │
                  ▼
             State Packet
                  │
                  ▼
            Fresh Builder
```

The core rule is:

> **Preserve Evidence. Do not inherit raw reasoning residue.**

---

# Cross-Record Conformance

A valid JSON document is not necessarily part of a valid inheritance chain.

For example:

```text
Audit:
  verified = A

Purification:
  retained = A, B

Packet:
  verified = A, B
```

`B` was never audited.

IMP therefore validates:

```text
Audit Record
      ↓
State Purification Record
      ↓
State Packet
```

Cross-record validation checks:

* generation continuity,
* record identifiers,
* provenance,
* goal hashes,
* audited fact origin,
* audited artifact origin,
* fact closure,
* artifact closure,
* assumption closure,
* guardrail closure.

---

# Metabolism Cycle

IMP v0.5 introduces the **Metabolism Cycle** as the canonical lifecycle unit.

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

A cycle may end as:

```text
COMPLETED
REQUIRES_REWORK
ABORTED
```

Only:

```text
COMPLETED
```

may authorize:

```text
next_builder_eligible = true
```

---

# Lifecycle Gates

A successful Metabolism Cycle passes the following gates:

1. Governor Gate
2. Handoff Gate
3. Audit Gate
4. Purification Gate
5. Cross-Record Gate
6. Goal Continuity Gate
7. Raw-Trace Non-Inheritance Gate
8. Evidence Preservation Gate
9. Packet Verification Gate

Failure at a required gate prevents valid generational turnover.

---

# Repository Structure

```text
inference-metabolism-protocol/
├── README.md
├── SPEC.md
├── CHANGELOG.md
├── requirements.txt
│
├── schemas/
│   ├── state-packet.schema.json
│   ├── handoff-event.schema.json
│   ├── audit-record.schema.json
│   ├── shift-governor-assessment.schema.json
│   ├── state-purification-record.schema.json
│   ├── cross-record-conformance-case.schema.json
│   ├── metabolism-cycle-record.schema.json
│   └── metabolism-cycle-conformance-case.schema.json
│
├── examples/
│   ├── pass/
│   ├── fail/
│   ├── conformance/
│   │   ├── records/
│   │   ├── pass/
│   │   └── fail/
│   └── cycle/
│       ├── records/
│       ├── pass/
│       └── fail/
│
├── scripts/
│   └── validate_examples.py
│
└── .github/
    └── workflows/
        └── validate.yml
```

---

# Schema Versions

IMP release versions and individual record schema versions are intentionally separate.

```text
IMP Release                          0.5.0

State Packet                         0.1.0
Handoff Event                        0.1.0
Audit Record                         0.1.0
Shift Governor Assessment            0.2.0
State Purification Record            0.3.0
Cross-Record Conformance Case        0.4.0
Metabolism Cycle Record              0.5.0
Metabolism Cycle Conformance Case    0.5.0
```

Earlier schemas are not artificially version-bumped when their structure remains unchanged.

---

# Validation

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Run:

```bash
python scripts/validate_examples.py
```

A successful run ends with:

```text
=== RESULT: PASS ===
```

The v0.5 validator covers:

```text
[pass examples]

[fail examples]

[cross-record conformance: pass]

[cross-record conformance: fail]

[metabolism-cycle conformance: pass]

[metabolism-cycle conformance: fail]
```

---

# Validation Levels

IMP v0.5 supports five validation levels.

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

# Core Invariants

IMP v0.5 defines **50 core invariants**, including:

* Raw Trace Non-Inheritance
* Evidence Preservation
* Goal Continuity
* Role Separation
* Governor Independence
* Score Reproducibility
* Anomaly Override
* Purification Transparency
* Fact / Assumption Separation
* Zero Raw-Trace Inheritance
* Audited Fact Origin
* Audited Artifact Origin
* Provenance Closure
* Cross-Record Closure
* Metabolism Cycle Closure
* Audit Gate
* Purification Gate
* Packet Verification Gate
* Builder Eligibility

See [`SPEC.md`](./SPEC.md) for the complete normative definitions.

---

# Protocol Evolution

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

# What IMP Is Not

IMP is not:

* a replacement for LLM reasoning,
* a causal reasoning algorithm,
* a memory database,
* a vector store,
* a summarization algorithm,
* a specific agent framework,
* or a universal prompt template.

IMP manages the lifecycle around reasoning.

External reasoning engines can operate inside IMP.

---

# IMP and Context Compression

Context compression MAY be used inside an IMP implementation.

However:

```text
Context Compression
≠
Inference Metabolism Protocol
```

IMP additionally defines:

* termination,
* handoff,
* auditing,
* purification,
* inheritance classification,
* provenance,
* goal continuity,
* cross-record verification,
* and fresh-context regeneration.

---

# IMP and Long-Term Memory

IMP does not prohibit long-term memory.

Instead, it separates:

```text
Persistent Memory
External Evidence
Working Context
Inherited State
```

Long-term memory MAY be consulted as evidence.

It MUST NOT automatically become inherited verified state.

---

# Efficiency Goal

IMP aims to reduce unnecessary work caused by:

* reading full histories repeatedly,
* reconstructing already-known state,
* retrying known failures,
* searching for the current task again,
* re-deriving already-verified facts,
* and carrying irrelevant context forward.

The goal is not simply:

> Reason less.

The goal is:

> **Spend reasoning where new reasoning is actually needed.**

---

# Status

Current protocol release:

```text
IMP v0.5.0
```

Status:

> **First Complete Protocol Milestone**

v0.5 closes the first complete lifecycle:

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

---

# Future Work

Post-v0.5 development may focus on:

* long-horizon benchmarks,
* Minimum Sufficient State scoring,
* Metabolism Efficiency metrics,
* automated context-pressure measurement,
* improved loop detection,
* standardized goal-drift measurement,
* cryptographic packet integrity,
* discarded-item resurrection detection,
* LangGraph adapters,
* AutoGen adapters,
* CrewAI adapters,
* and production runtime experiments.

---

# Final Principle

IMP does not attempt to keep one reasoning instance alive forever.

It attempts to keep the intelligent system alive by allowing individual reasoning contexts to end safely.

> **Short-lived reasoning instances can compose a long-lived intelligent system when state inheritance is controlled, audited, purified, and verifiable.**

Or more simply:

> **Do not preserve the reasoning process indefinitely. Preserve what remains valid after it ends.**
