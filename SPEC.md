# Inference Metabolism Protocol Specification

Version: **0.1.0**

Status: **Experimental**

## 1. Purpose

Inference Metabolism Protocol (IMP) defines a lifecycle architecture for long-horizon AI agents.

IMP addresses degradation caused by indefinite accumulation of reasoning history by separating:

- active reasoning,
- evidence preservation,
- auditing,
- state reconstruction,
- and inter-generation state inheritance.

IMP does not define a particular reasoning model.

It defines how reasoning instances are allowed to begin, operate, terminate, and transfer state.

---

## 2. Normative Language

The terms **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** are normative requirements.

---

## 3. Core Model

An IMP lifecycle consists of:

```text
Builder
   |
   v
Handoff
   |
   v
Auditor
   |
   v
Planner
   |
   v
State Purification
   |
   v
State Packet
   |
   v
New Builder

Each new Builder represents a new reasoning generation.

4. Roles
4.1 Builder

The Builder performs active task execution.

A Builder SHOULD concentrate on the immediate task defined by the current State Packet.

A Builder MUST NOT modify the Immutable Goal.

A Builder SHOULD NOT receive raw reasoning traces from previous Builders unless an explicit external diagnostic process authorizes such access.

4.2 Auditor

The Auditor evaluates Builder outputs.

The Auditor is responsible for distinguishing:

verified facts,
verified artifacts,
unresolved issues,
unsupported assumptions,
and failed outputs.

Only information eligible for state inheritance SHOULD be passed to the Planner.

4.3 Planner

The Planner constructs the State Packet for the next generation.

The Planner MUST NOT behave as a simple transcript summarizer.

Its function is State Purification.

The Planner SHOULD minimize inherited state while preserving sufficient information for correct next-step execution.

5. State Purification

State Purification is the process by which raw execution experience is transformed into inheritable state.

Conceptually:

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

The output of State Purification is a State Packet.

6. Raw Trace Non-Inheritance

IMP distinguishes between:

Evidence Preservation

Logs, artifacts, test results, provenance records, and other evidence MAY be preserved outside the active context.

Context Inheritance

Raw reasoning history MUST NOT be automatically copied into the next Builder's working context.

Therefore:

Preservation != Inheritance

IMP v0.1 encodes this through:

{
  "raw_trace_inherited": false,
  "evidence_preserved": true,
  "minimum_sufficient_state": true
}
7. Minimum Sufficient State

Minimum Sufficient State (MSS) is the smallest state representation that allows the next Builder to correctly begin its immediate task without unnecessary reconstruction.

The optimization objective can be expressed conceptually as:

minimize:


StatePacketSize
+ ReReasoningCost
+ ContextNoise


subject to:


GoalPreservation
ConstraintPreservation
TaskExecutability

IMP v0.1 does not define a numerical MSS metric.

8. Immutable Goal

The Immutable Goal represents the stable project-level objective.

It contains:

goal_id
goal_hash
core_objective
definition_of_done

A Planner MUST NOT silently alter the Immutable Goal.

Future IMP versions MAY define cryptographic continuity verification between generations.

9. Handoff Triggers

IMP v0.1 defines four trigger types.

9.1 MILESTONE_COMPLETED

Normal handoff after a meaningful work unit has completed.

Mode:

NORMAL
9.2 CONTEXT_PRESSURE

Normal handoff caused by degrading context quality or context budget pressure.

Mode:

NORMAL
9.3 TIME_BOUNDARY

Normal handoff caused by external scheduling or synchronization requirements.

Mode:

NORMAL
9.4 ANOMALY_DETECTED

Preemptive handoff caused by abnormal agent behavior.

Examples include:

repeated tool failure,
reasoning loops,
goal drift,
contradictory state,
abnormal retry density.

Mode:

INTERRUPT

Anomaly handoff is not a normal scheduling event.

It is a preemptive interrupt.

10. State Packet

A State Packet is the canonical Planner-to-Builder transfer object.

It contains:

StatePacket
├─ schema_version
├─ packet_metadata
├─ inheritance_policy
├─ provenance
├─ immutable_goal
├─ current_state
├─ execution_plan
├─ constraints_and_guardrails
└─ integrity
11. Current State Classification

IMP explicitly separates facts from assumptions.

verified_facts

Claims supported by evidence.

verified_artifacts

Outputs accepted by the Auditor.

working_assumptions

Unverified claims that remain operationally useful.

open_issues

Known unresolved problems.

This separation is intended to reduce hallucination inheritance.

12. Do-Not-Repeat Rules

A failed approach MUST NOT automatically become a permanent universal prohibition.

Each do_not_repeat rule therefore contains:

a rule identifier,
prohibited action,
reason,
scope,
expiration condition.

This prevents uncontrolled accumulation of permanent taboos.

13. Provenance

State inheritance SHOULD retain provenance without inheriting raw reasoning context.

A State Packet therefore references:

the previous packet,
Builder run,
Audit Record,
Planner run.
14. Audit Eligibility

An Audit Record contains:

PASS
FAIL
NEEDS_REWORK

In IMP v0.1:

PASS
=> state_eligible = true


FAIL
=> state_eligible = false


NEEDS_REWORK
=> state_eligible = false
15. Generational Semantics

A State Packet generation identifies the Builder generation that consumes the packet.

For generation N > 1, a previous packet reference MUST exist.

A Handoff Event MUST satisfy:

next_generation = current_generation + 1
16. v0.1 Core Invariants
IMP-01 — Raw Trace Non-Inheritance

Raw reasoning traces MUST NOT be automatically inherited by a new Builder.

IMP-02 — Evidence Preservation

Evidence MAY remain available outside the inherited working context.

IMP-03 — Verified State Preference

Verified information SHOULD be preferred over inferred historical narrative.

IMP-04 — Goal Continuity

The Immutable Goal MUST persist across generations.

IMP-05 — Role Separation

Builder, Auditor, and Planner responsibilities MUST remain logically distinct.

IMP-06 — External Lifecycle Control

Builder lifetime MUST NOT depend solely on Builder self-assessment.

IMP-07 — Anomaly Preemption

ANOMALY_DETECTED MUST use interrupt semantics.

IMP-08 — State Classification

Verified facts and working assumptions MUST remain distinguishable.

IMP-09 — Minimum Sufficient State

The Planner SHOULD avoid transferring unnecessary context.

IMP-10 — Audited Inheritance

A Builder-consumable State Packet MUST have verified audit status.

IMP-11 — Generation Continuity

Generation numbers MUST progress monotonically across handoff.

IMP-12 — No Silent Taboo Expansion

Failed historical approaches MUST NOT become permanent universal prohibitions without explicit scope.

17. Out of Scope for v0.1

IMP v0.1 does not standardize:

LLM vendors,
prompts,
memory databases,
vector stores,
tool APIs,
orchestration frameworks,
Handoff Score weighting,
cryptographic signatures,
distributed consensus,
multi-Builder parallelism,
reasoning algorithms.

Those MAY be introduced in later versions or external profiles.

18. Version Philosophy

IMP v0.1 is intentionally small.

The purpose of this version is to establish the minimum lifecycle kernel:

Execute
→ Handoff
→ Audit
→ Purify
→ Transfer
→ Reset
→ Execute
