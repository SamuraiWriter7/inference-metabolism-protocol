#!/usr/bin/env python3

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError


# ============================================================
# Paths / Constants
# ============================================================

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "schemas"

PASS_DIR = ROOT / "examples" / "pass"
FAIL_DIR = ROOT / "examples" / "fail"

CONFORMANCE_PASS_DIR = (
    ROOT / "examples" / "conformance" / "pass"
)

CONFORMANCE_FAIL_DIR = (
    ROOT / "examples" / "conformance" / "fail"
)

CYCLE_PASS_DIR = (
    ROOT / "examples" / "cycle" / "pass"
)

CYCLE_FAIL_DIR = (
    ROOT / "examples" / "cycle" / "fail"
)

FLOAT_TOLERANCE = 1e-6


SCHEMA_FILES = {
    "state-packet":
        SCHEMA_DIR / "state-packet.schema.json",

    "handoff-event":
        SCHEMA_DIR / "handoff-event.schema.json",

    "audit-record":
        SCHEMA_DIR / "audit-record.schema.json",

    "shift-governor-assessment":
        SCHEMA_DIR
        / "shift-governor-assessment.schema.json",

    "state-purification-record":
        SCHEMA_DIR
        / "state-purification-record.schema.json",

    "cross-record-conformance-case":
        SCHEMA_DIR
        / "cross-record-conformance-case.schema.json",

    "metabolism-cycle-record":
        SCHEMA_DIR
        / "metabolism-cycle-record.schema.json",

    "metabolism-cycle-conformance-case":
        SCHEMA_DIR
        / "metabolism-cycle-conformance-case.schema.json",
}


# ============================================================
# Filename Aliases
# ============================================================

RECORD_TYPE_ALIASES = {
    "state-packet.": "state-packet",
    "handoff-event.": "handoff-event",
    "audit-record.": "audit-record",
    "shift-governor-assessment.":
        "shift-governor-assessment",
    "state-purification-record.":
        "state-purification-record",
    "cross-record-conformance-case.":
        "cross-record-conformance-case",

    # v0.5 aliases
    "metabolism-cycle-record.":
        "metabolism-cycle-record",
    "metabolism-cycle.":
        "metabolism-cycle-record",

    "metabolism-cycle-conformance-case.":
        "metabolism-cycle-conformance-case",
    "metabolism-cycle-conformance.":
        "metabolism-cycle-conformance-case",
}


# ============================================================
# JSON Utilities
# ============================================================

def load_json(path: Path) -> Any:
    """
    Load a JSON document.

    JSON syntax errors intentionally propagate to the caller so
    syntax failures can be distinguished from schema and semantic
    failures.
    """
    with path.open(
        "r",
        encoding="utf-8",
    ) as handle:
        return json.load(handle)


def record_type_for(path: Path) -> str:
    """
    Infer an IMP record type from its filename.
    """
    name = path.name

    for prefix, record_type in RECORD_TYPE_ALIASES.items():
        if name.startswith(prefix):
            return record_type

    raise ValueError(
        f"cannot infer record type from filename: {path}"
    )


def resolve_repo_path(relative_path: str) -> Path:
    """
    Resolve a repository-relative path while preventing path
    traversal outside the repository root.
    """
    root = ROOT.resolve()
    path = (ROOT / relative_path).resolve()

    if not path.is_relative_to(root):
        raise ValueError(
            f"path escapes repository root: {relative_path}"
        )

    return path


# ============================================================
# Shift Governor Logic
# ============================================================

def expected_governor_decision(
    score: float,
    thresholds: dict[str, float],
) -> str:
    """
    Convert a Handoff Score into the normative Governor decision.
    """
    if score >= thresholds["emergency"]:
        return "EMERGENCY"

    if score >= thresholds["handoff"]:
        return "HANDOFF"

    if score >= thresholds["prepare"]:
        return "PREPARE"

    return "CONTINUE"


# ============================================================
# Record-local Semantic Validation
# ============================================================

def semantic_errors(
    record_type: str,
    data: dict[str, Any],
) -> list[str]:
    """
    Validate semantic invariants not expressible cleanly through
    JSON Schema alone.
    """
    errors: list[str] = []

    # --------------------------------------------------------
    # State Packet
    # --------------------------------------------------------

    if record_type == "state-packet":
        generation = (
            data["packet_metadata"]["generation"]
        )

        previous_packet_id = (
            data["provenance"]["previous_packet_id"]
        )

        if (
            generation == 1
            and previous_packet_id is not None
        ):
            errors.append(
                "generation 1 must have "
                "previous_packet_id = null"
            )

        if (
            generation > 1
            and previous_packet_id is None
        ):
            errors.append(
                "generation > 1 requires "
                "previous_packet_id"
            )

        if (
            data["integrity"]["audit_status"]
            != "VERIFIED"
        ):
            errors.append(
                "a Builder-consumable State Packet "
                "must be VERIFIED"
            )

    # --------------------------------------------------------
    # Handoff Event
    # --------------------------------------------------------

    elif record_type == "handoff-event":
        current_generation = (
            data["current_generation"]
        )

        next_generation = (
            data["next_generation"]
        )

        trigger_type = (
            data["trigger"]["type"]
        )

        mode = (
            data["trigger"]["mode"]
        )

        if (
            next_generation
            != current_generation + 1
        ):
            errors.append(
                "next_generation must equal "
                "current_generation + 1"
            )

        if (
            trigger_type == "ANOMALY_DETECTED"
            and mode != "INTERRUPT"
        ):
            errors.append(
                "ANOMALY_DETECTED must use "
                "INTERRUPT mode"
            )

        if (
            trigger_type != "ANOMALY_DETECTED"
            and mode not in (
                "NORMAL",
                "INTERRUPT",
            )
        ):
            errors.append(
                "invalid handoff mode"
            )

    # --------------------------------------------------------
    # Audit Record
    # --------------------------------------------------------

    elif record_type == "audit-record":
        decision = data["decision"]

        state_eligible = (
            data["state_eligible"]
        )

        if (
            decision == "PASS"
            and not state_eligible
        ):
            errors.append(
                "PASS audit must be "
                "state_eligible = true"
            )

        if (
            decision != "PASS"
            and state_eligible
        ):
            errors.append(
                "non-PASS audit must be "
                "state_eligible = false"
            )

    # --------------------------------------------------------
    # Shift Governor Assessment
    # --------------------------------------------------------

    elif record_type == "shift-governor-assessment":
        metrics = data["metrics"]
        weights = data["weights"]
        thresholds = data["thresholds"]

        anomaly = (
            data["anomaly_override"]
        )

        # IMP-14 — Weight Normalization
        weight_sum = sum(
            weights.values()
        )

        if (
            abs(weight_sum - 1.0)
            > FLOAT_TOLERANCE
        ):
            errors.append(
                "governor weights must sum to 1.0 "
                f"(actual={weight_sum:.6f})"
            )

        # IMP-15 — Score Reproducibility
        calculated_score = sum(
            metrics[key] * weights[key]
            for key in (
                "context_pressure",
                "error_density",
                "loop_probability",
                "goal_drift",
            )
        )

        declared_score = (
            data["handoff_score"]
        )

        if (
            abs(
                calculated_score
                - declared_score
            )
            > FLOAT_TOLERANCE
        ):
            errors.append(
                "handoff_score does not match "
                "weighted metric calculation "
                f"(expected={calculated_score:.6f}, "
                f"actual={declared_score:.6f})"
            )

        # IMP-16 — Ordered Thresholds
        prepare = thresholds["prepare"]
        handoff = thresholds["handoff"]
        emergency = thresholds["emergency"]

        if not (
            prepare
            < handoff
            < emergency
        ):
            errors.append(
                "thresholds must satisfy "
                "prepare < handoff < emergency"
            )

        anomaly_detected = (
            anomaly["detected"]
        )

        anomaly_reasons = (
            anomaly["reasons"]
        )

        # IMP-18 / IMP-19
        if anomaly_detected:
            if not anomaly_reasons:
                errors.append(
                    "detected anomaly requires "
                    "at least one reason"
                )

            if data["decision"] != "EMERGENCY":
                errors.append(
                    "anomaly override requires "
                    "decision = EMERGENCY"
                )

        else:
            if anomaly_reasons:
                errors.append(
                    "anomaly reasons must be empty "
                    "when detected = false"
                )

            expected_decision = (
                expected_governor_decision(
                    declared_score,
                    thresholds,
                )
            )

            if (
                data["decision"]
                != expected_decision
            ):
                errors.append(
                    "governor decision does not "
                    "match handoff_score thresholds "
                    f"(expected={expected_decision}, "
                    f"actual={data['decision']})"
                )

    # --------------------------------------------------------
    # State Purification Record
    # --------------------------------------------------------

    elif record_type == "state-purification-record":
        source_generation = (
            data["source_generation"]
        )

        target_generation = (
            data["target_generation"]
        )

        # IMP-28
        if (
            target_generation
            != source_generation + 1
        ):
            errors.append(
                "target_generation must equal "
                "source_generation + 1"
            )

        source = data["source"]

        if (
            source_generation == 1
            and source[
                "previous_packet_id"
            ] is not None
        ):
            errors.append(
                "source generation 1 must have "
                "previous_packet_id = null"
            )

        if (
            source_generation > 1
            and source[
                "previous_packet_id"
            ] is None
        ):
            errors.append(
                "source generation > 1 requires "
                "previous_packet_id"
            )

        classification = (
            data["classification"]
        )

        inherited_count = (
            len(
                classification[
                    "retained_verified_facts"
                ]
            )
            + len(
                classification[
                    "retained_verified_artifacts"
                ]
            )
            + len(
                classification[
                    "carried_working_assumptions"
                ]
            )
            + len(
                classification[
                    "generated_guardrails"
                ]
            )
        )

        discarded_count = len(
            classification[
                "discarded_items"
            ]
        )

        total_count = (
            inherited_count
            + discarded_count
        )

        summary = (
            data["inheritance_summary"]
        )

        # IMP-24
        if (
            summary["inherited_item_count"]
            != inherited_count
        ):
            errors.append(
                "inherited_item_count does not "
                "match classified inherited items"
            )

        if (
            summary["discarded_item_count"]
            != discarded_count
        ):
            errors.append(
                "discarded_item_count does not "
                "match classified discarded items"
            )

        if (
            summary[
                "total_considered_item_count"
            ]
            != total_count
        ):
            errors.append(
                "total_considered_item_count must "
                "equal inherited items + "
                "discarded items"
            )

        # IMP-22
        if (
            summary[
                "raw_trace_items_inherited"
            ]
            != 0
        ):
            errors.append(
                "raw reasoning trace inheritance "
                "must equal 0"
            )

        # IMP-25
        if total_count > 0:
            expected_ratio = (
                inherited_count
                / total_count
            )

            actual_ratio = (
                summary["inheritance_ratio"]
            )

            if (
                abs(
                    actual_ratio
                    - expected_ratio
                )
                > FLOAT_TOLERANCE
            ):
                errors.append(
                    "inheritance_ratio does not "
                    "match inherited_item_count / "
                    "total_considered_item_count "
                    f"(expected="
                    f"{expected_ratio:.6f}, "
                    f"actual={actual_ratio:.6f})"
                )

        continuity = (
            data["continuity_checks"]
        )

        hashes_equal = (
            continuity["goal_hash_before"]
            == continuity["goal_hash_after"]
        )

        if (
            continuity[
                "immutable_goal_preserved"
            ]
            != hashes_equal
        ):
            errors.append(
                "immutable_goal_preserved must "
                "match goal-hash continuity"
            )

        output = data["output"]
        status = output["status"]

        # IMP-26 / IMP-27
        if status == "READY_FOR_HANDOFF":
            if (
                output["state_packet_id"]
                is None
            ):
                errors.append(
                    "READY_FOR_HANDOFF requires "
                    "state_packet_id"
                )

            required_checks = (
                "immutable_goal_preserved",
                "evidence_traceability_preserved",
                "fact_assumption_separation_preserved",
                "minimum_sufficient_state_satisfied",
            )

            failed_checks = [
                key
                for key in required_checks
                if not continuity[key]
            ]

            if failed_checks:
                errors.append(
                    "READY_FOR_HANDOFF requires "
                    "all continuity checks to pass: "
                    + ", ".join(
                        failed_checks
                    )
                )

    return errors


# ============================================================
# Generic Validation
# ============================================================

def validate_path_as(
    path: Path,
    record_type: str,
    validators: dict[
        str,
        Draft202012Validator,
    ],
) -> tuple[
    list[str],
    list[str],
    list[str],
]:
    """
    Validate a path against an explicitly selected record type.

    Returns:

        syntax_errors
        schema_errors
        semantic_errors
    """
    try:
        data = load_json(path)
    except json.JSONDecodeError as exc:
        return [
            (
                f"invalid JSON: "
                f"line {exc.lineno}, "
                f"column {exc.colno}: "
                f"{exc.msg}"
            )
        ], [], []

    validator = validators[
        record_type
    ]

    schema_errors = [
        error.message
        for error in sorted(
            validator.iter_errors(data),
            key=lambda item: list(
                item.absolute_path
            ),
        )
    ]

    if schema_errors:
        return [], schema_errors, []

    local_errors = semantic_errors(
        record_type,
        data,
    )

    return [], [], local_errors


def validate_file(
    path: Path,
    validators: dict[
        str,
        Draft202012Validator,
    ],
) -> tuple[
    list[str],
    list[str],
    list[str],
]:
    """
    Infer record type from filename and validate the file.
    """
    try:
        record_type = (
            record_type_for(path)
        )
    except ValueError as exc:
        return [str(exc)], [], []

    return validate_path_as(
        path,
        record_type,
        validators,
    )


# ============================================================
# Canonical Cross-Record Keys
# ============================================================

def fact_key(
    item: dict[str, Any],
) -> tuple[Any, ...]:
    return (
        item["fact_id"],
        item["statement"],
        tuple(
            sorted(
                item["evidence_refs"]
            )
        ),
    )


def artifact_key(
    item: dict[str, Any],
) -> tuple[Any, ...]:
    return (
        item["type"],
        item["path_or_key"],
        item["status"],
        item["summary"],
    )


def assumption_key(
    item: dict[str, Any],
) -> tuple[Any, ...]:
    """
    `reason` exists only in the Purification Record and is
    deliberately excluded from the inherited State Packet key.
    """
    return (
        item["assumption_id"],
        item["statement"],
        item["confidence"],
        item["validation_needed"],
    )


def guardrail_key(
    item: dict[str, Any],
) -> tuple[Any, ...]:
    """
    `source_ref` remains in the Purification Record rather than
    being copied into the State Packet.
    """
    return (
        item["rule_id"],
        item["prohibited_action"],
        item["reason"],
        item["scope"],
        item["expires_when"],
    )


# ============================================================
# Cross-Record Conformance
# ============================================================

def cross_record_violations(
    audit: dict[str, Any],
    purification: dict[str, Any],
    packet: dict[str, Any],
) -> list[tuple[str, str]]:
    """
    Validate:

        Audit Record
             ->
        State Purification Record
             ->
        State Packet
    """
    violations: list[
        tuple[str, str]
    ] = []

    # --------------------------------------------------------
    # IMP-30 — Generation Alignment
    # --------------------------------------------------------

    if (
        audit["generation"]
        != purification[
            "source_generation"
        ]
    ):
        violations.append(
            (
                "GENERATION_MISMATCH",
                "audit generation does not "
                "match purification source "
                "generation",
            )
        )

    if (
        purification[
            "target_generation"
        ]
        != packet[
            "packet_metadata"
        ]["generation"]
    ):
        violations.append(
            (
                "GENERATION_MISMATCH",
                "purification target generation "
                "does not match State Packet "
                "generation",
            )
        )

    # --------------------------------------------------------
    # Audit reference
    # --------------------------------------------------------

    if (
        purification["source"][
            "audit_record_id"
        ]
        != audit["audit_record_id"]
    ):
        violations.append(
            (
                "AUDIT_REFERENCE_MISMATCH",
                "purification audit_record_id "
                "does not match Audit Record",
            )
        )

    # --------------------------------------------------------
    # Packet reference
    # --------------------------------------------------------

    if (
        purification["output"][
            "state_packet_id"
        ]
        != packet[
            "packet_metadata"
        ]["packet_id"]
    ):
        violations.append(
            (
                "STATE_PACKET_REFERENCE_MISMATCH",
                "purification output "
                "state_packet_id does not match "
                "State Packet",
            )
        )

    # --------------------------------------------------------
    # IMP-38 — Provenance Closure
    # --------------------------------------------------------

    provenance = (
        packet["provenance"]
    )

    source = (
        purification["source"]
    )

    provenance_match = (
        provenance["audit_record_id"]
        == audit["audit_record_id"]
        and provenance["builder_run_id"]
        == source["builder_run_id"]
        and provenance["planner_run_id"]
        == source["planner_run_id"]
        and provenance["previous_packet_id"]
        == source["previous_packet_id"]
    )

    if not provenance_match:
        violations.append(
            (
                "PROVENANCE_MISMATCH",
                "State Packet provenance "
                "does not match the "
                "Audit/Purification lineage",
            )
        )

    # --------------------------------------------------------
    # IMP-37 — Goal Hash Continuity
    # --------------------------------------------------------

    continuity = (
        purification[
            "continuity_checks"
        ]
    )

    packet_goal_hash = (
        packet[
            "immutable_goal"
        ]["goal_hash"]
    )

    if (
        continuity["goal_hash_after"]
        != packet_goal_hash
    ):
        violations.append(
            (
                "GOAL_HASH_MISMATCH",
                "purified goal hash does not "
                "match State Packet goal hash",
            )
        )

    # --------------------------------------------------------
    # IMP-31 — Audited Fact Origin
    # --------------------------------------------------------

    audited_fact_statements = set(
        audit["verified_facts"]
    )

    purified_facts_list = (
        purification[
            "classification"
        ]["retained_verified_facts"]
    )

    for fact in purified_facts_list:
        if (
            fact["statement"]
            not in audited_fact_statements
        ):
            violations.append(
                (
                    "UNAUDITED_FACT_RETAINED",
                    "purification retained "
                    "unaudited fact: "
                    f"{fact['fact_id']}",
                )
            )

    # --------------------------------------------------------
    # IMP-32 — Audited Artifact Origin
    # --------------------------------------------------------

    audited_artifact_paths = set(
        audit["verified_artifacts"]
    )

    purified_artifact_list = (
        purification[
            "classification"
        ]["retained_verified_artifacts"]
    )

    for artifact in (
        purified_artifact_list
    ):
        if (
            artifact["path_or_key"]
            not in audited_artifact_paths
        ):
            violations.append(
                (
                    "UNAUDITED_ARTIFACT_RETAINED",
                    "purification retained "
                    "unaudited artifact: "
                    f"{artifact['path_or_key']}",
                )
            )

    # --------------------------------------------------------
    # IMP-33 — Fact Closure
    # --------------------------------------------------------

    purified_facts = {
        fact_key(item)
        for item in purified_facts_list
    }

    packet_facts = {
        fact_key(item)
        for item in (
            packet["current_state"][
                "verified_facts"
            ]
        )
    }

    if purified_facts != packet_facts:
        violations.append(
            (
                "PACKET_FACT_SET_MISMATCH",
                "State Packet verified facts "
                "differ from purified "
                "verified facts",
            )
        )

    # --------------------------------------------------------
    # IMP-34 — Artifact Closure
    # --------------------------------------------------------

    purified_artifacts = {
        artifact_key(item)
        for item in (
            purified_artifact_list
        )
    }

    packet_artifacts = {
        artifact_key(item)
        for item in (
            packet["current_state"][
                "verified_artifacts"
            ]
        )
    }

    if (
        purified_artifacts
        != packet_artifacts
    ):
        violations.append(
            (
                "PACKET_ARTIFACT_SET_MISMATCH",
                "State Packet verified artifacts "
                "differ from purified "
                "verified artifacts",
            )
        )

    # --------------------------------------------------------
    # IMP-35 — Assumption Closure
    # --------------------------------------------------------

    purified_assumptions = {
        assumption_key(item)
        for item in (
            purification[
                "classification"
            ][
                "carried_working_assumptions"
            ]
        )
    }

    packet_assumptions = {
        assumption_key(item)
        for item in (
            packet["current_state"][
                "working_assumptions"
            ]
        )
    }

    if (
        purified_assumptions
        != packet_assumptions
    ):
        violations.append(
            (
                "PACKET_ASSUMPTION_SET_MISMATCH",
                "State Packet assumptions "
                "differ from purified "
                "assumptions",
            )
        )

    # --------------------------------------------------------
    # IMP-36 — Guardrail Closure
    # --------------------------------------------------------

    purified_guardrails = {
        guardrail_key(item)
        for item in (
            purification[
                "classification"
            ]["generated_guardrails"]
        )
    }

    packet_guardrails = {
        guardrail_key(item)
        for item in (
            packet[
                "constraints_and_guardrails"
            ]["do_not_repeat"]
        )
    }

    if (
        purified_guardrails
        != packet_guardrails
    ):
        violations.append(
            (
                "PACKET_GUARDRAIL_SET_MISMATCH",
                "State Packet guardrails "
                "differ from purified "
                "guardrails",
            )
        )

    return violations


# ============================================================
# Cross-Record Case Validation
# ============================================================

def validate_cross_record_case(
    case_path: Path,
    validators: dict[
        str,
        Draft202012Validator,
    ],
) -> tuple[
    list[str],
    list[str],
    list[tuple[str, str]],
]:
    """
    Validate a v0.4 Cross-Record Conformance Case.
    """

    try:
        case = load_json(case_path)
    except json.JSONDecodeError as exc:
        return [
            (
                f"invalid JSON: "
                f"line {exc.lineno}, "
                f"column {exc.colno}: "
                f"{exc.msg}"
            )
        ], [], []

    case_validator = validators[
        "cross-record-conformance-case"
    ]

    schema_errors = [
        error.message
        for error in sorted(
            case_validator.iter_errors(
                case
            ),
            key=lambda item: list(
                item.absolute_path
            ),
        )
    ]

    if schema_errors:
        return [], schema_errors, []

    try:
        audit_path = resolve_repo_path(
            case["audit_record_path"]
        )

        purification_path = (
            resolve_repo_path(
                case[
                    "purification_record_path"
                ]
            )
        )

        packet_path = resolve_repo_path(
            case["state_packet_path"]
        )

    except ValueError as exc:
        return [], [], [
            (
                "LINKED_RECORD_INVALID",
                str(exc),
            )
        ]

    linked_records = (
        (
            audit_path,
            "audit-record",
        ),
        (
            purification_path,
            "state-purification-record",
        ),
        (
            packet_path,
            "state-packet",
        ),
    )

    for (
        linked_path,
        linked_type,
    ) in linked_records:

        if not linked_path.exists():
            return [], [], [
                (
                    "LINKED_RECORD_INVALID",
                    "linked record does not "
                    "exist: "
                    f"{linked_path}",
                )
            ]

        (
            syntax_errors,
            linked_schema_errors,
            linked_semantic_errors,
        ) = validate_path_as(
            linked_path,
            linked_type,
            validators,
        )

        if syntax_errors:
            return syntax_errors, [], []

        if (
            linked_schema_errors
            or linked_semantic_errors
        ):
            details = (
                linked_schema_errors
                + linked_semantic_errors
            )

            return [], [], [
                (
                    "LINKED_RECORD_INVALID",
                    f"{linked_path.relative_to(ROOT)}: "
                    + " | ".join(details),
                )
            ]

    audit = load_json(audit_path)

    purification = load_json(
        purification_path
    )

    packet = load_json(packet_path)

    violations = cross_record_violations(
        audit,
        purification,
        packet,
    )

    return [], [], violations


# ============================================================
# Metabolism Cycle Conformance
# ============================================================

def metabolism_cycle_violations(
    cycle: dict[str, Any],
    governor: dict[str, Any] | None,
    handoff: dict[str, Any],
    audit: dict[str, Any],
    purification: dict[str, Any],
    packet: dict[str, Any],
) -> list[tuple[str, str]]:
    """
    Validate one complete IMP generation transition.

        Governor
          ->
        Handoff
          ->
        Audit
          ->
        Purification
          ->
        Cross-Record Conformance
          ->
        State Packet
    """

    violations: list[
        tuple[str, str]
    ] = []

    source_generation = (
        cycle["source_generation"]
    )

    target_generation = (
        cycle["target_generation"]
    )

    trigger_type = (
        cycle["trigger"]["type"]
    )

    trigger_mode = (
        cycle["trigger"]["mode"]
    )

    refs = cycle["record_refs"]

    # --------------------------------------------------------
    # IMP-40 — Source Generation Closure
    # --------------------------------------------------------

    source_generations = [
        handoff["current_generation"],
        audit["generation"],
        purification[
            "source_generation"
        ],
    ]

    if governor is not None:
        source_generations.append(
            governor["generation"]
        )

    if any(
        generation != source_generation
        for generation
        in source_generations
    ):
        violations.append(
            (
                "CYCLE_GENERATION_MISMATCH",
                "source-generation lineage "
                "is inconsistent",
            )
        )

    # --------------------------------------------------------
    # IMP-41 — Target Generation Closure
    # --------------------------------------------------------

    target_generations = [
        handoff["next_generation"],
        purification[
            "target_generation"
        ],
        packet[
            "packet_metadata"
        ]["generation"],
    ]

    if any(
        generation != target_generation
        for generation
        in target_generations
    ):
        violations.append(
            (
                "CYCLE_GENERATION_MISMATCH",
                "target-generation lineage "
                "is inconsistent",
            )
        )

    if (
        target_generation
        != source_generation + 1
    ):
        violations.append(
            (
                "CYCLE_GENERATION_MISMATCH",
                "target generation must equal "
                "source generation + 1",
            )
        )

    # --------------------------------------------------------
    # IMP-42 — Lifecycle Reference Closure
    # --------------------------------------------------------

    expected_source_packet_id = (
        purification["source"][
            "previous_packet_id"
        ]
    )

    if (
        refs["source_state_packet_id"]
        != expected_source_packet_id
    ):
        violations.append(
            (
                "CYCLE_RECORD_REFERENCE_MISMATCH",
                "cycle source State Packet ID "
                "does not match purification "
                "previous_packet_id",
            )
        )

    if (
        refs["source_state_packet_id"]
        != packet["provenance"][
            "previous_packet_id"
        ]
    ):
        violations.append(
            (
                "CYCLE_RECORD_REFERENCE_MISMATCH",
                "cycle source State Packet ID "
                "does not match output Packet "
                "provenance",
            )
        )

    if (
        refs["handoff_event_id"]
        != handoff[
            "handoff_event_id"
        ]
    ):
        violations.append(
            (
                "CYCLE_RECORD_REFERENCE_MISMATCH",
                "cycle Handoff Event reference "
                "does not match linked record",
            )
        )

    if (
        refs["audit_record_id"]
        != audit[
            "audit_record_id"
        ]
    ):
        violations.append(
            (
                "CYCLE_RECORD_REFERENCE_MISMATCH",
                "cycle Audit Record reference "
                "does not match linked record",
            )
        )

    if (
        refs["purification_record_id"]
        != purification[
            "purification_record_id"
        ]
    ):
        violations.append(
            (
                "CYCLE_RECORD_REFERENCE_MISMATCH",
                "cycle State Purification "
                "reference does not match "
                "linked record",
            )
        )

    if (
        refs["output_state_packet_id"]
        != packet[
            "packet_metadata"
        ]["packet_id"]
    ):
        violations.append(
            (
                "CYCLE_RECORD_REFERENCE_MISMATCH",
                "cycle output State Packet "
                "reference does not match "
                "linked packet",
            )
        )

    if (
        refs["output_state_packet_id"]
        != purification["output"][
            "state_packet_id"
        ]
    ):
        violations.append(
            (
                "CYCLE_RECORD_REFERENCE_MISMATCH",
                "cycle output State Packet ID "
                "does not match purification "
                "output",
            )
        )

    if governor is None:
        if (
            refs["governor_assessment_id"]
            is not None
        ):
            violations.append(
                (
                    "CYCLE_RECORD_REFERENCE_MISMATCH",
                    "cycle declares Governor "
                    "assessment but no Governor "
                    "record was provided",
                )
            )

    else:
        if (
            refs["governor_assessment_id"]
            != governor[
                "assessment_id"
            ]
        ):
            violations.append(
                (
                    "CYCLE_RECORD_REFERENCE_MISMATCH",
                    "cycle Governor reference "
                    "does not match linked "
                    "assessment",
                )
            )

    # --------------------------------------------------------
    # Trigger Closure
    # --------------------------------------------------------

    if (
        trigger_type
        != handoff["trigger"]["type"]
    ):
        violations.append(
            (
                "CYCLE_TRIGGER_MISMATCH",
                "cycle trigger type does not "
                "match Handoff Event",
            )
        )

    if (
        trigger_mode
        != handoff["trigger"]["mode"]
    ):
        violations.append(
            (
                "CYCLE_HANDOFF_MODE_MISMATCH",
                "cycle handoff mode does not "
                "match Handoff Event",
            )
        )

    # --------------------------------------------------------
    # IMP-43 — Governor Gate
    # --------------------------------------------------------

    governor_required = (
        trigger_type
        in (
            "CONTEXT_PRESSURE",
            "ANOMALY_DETECTED",
        )
    )

    if (
        governor_required
        and governor is None
    ):
        violations.append(
            (
                "CYCLE_GOVERNOR_MISMATCH",
                "reasoning-health trigger "
                "requires a Shift Governor "
                "assessment",
            )
        )

    if governor is not None:
        governor_decision = (
            governor["decision"]
        )

        if (
            governor_required
            and governor_decision
            not in (
                "HANDOFF",
                "EMERGENCY",
            )
        ):
            violations.append(
                (
                    "CYCLE_GOVERNOR_MISMATCH",
                    "Governor-controlled "
                    "transition requires "
                    "HANDOFF or EMERGENCY "
                    "decision",
                )
            )

        handoff_score = (
            handoff["trigger"].get(
                "score"
            )
        )

        if handoff_score is not None:
            if (
                abs(
                    handoff_score
                    - governor[
                        "handoff_score"
                    ]
                )
                > FLOAT_TOLERANCE
            ):
                violations.append(
                    (
                        "CYCLE_GOVERNOR_MISMATCH",
                        "Handoff Event score "
                        "does not match Governor "
                        "handoff_score",
                    )
                )

        # ----------------------------------------------------
        # IMP-44 — Interrupt Semantics
        # ----------------------------------------------------

        requires_interrupt = (
            trigger_type
            == "ANOMALY_DETECTED"
            or governor_decision
            == "EMERGENCY"
        )

        if (
            requires_interrupt
            and trigger_mode
            != "INTERRUPT"
        ):
            violations.append(
                (
                    "CYCLE_HANDOFF_MODE_MISMATCH",
                    "ANOMALY_DETECTED or "
                    "Governor EMERGENCY requires "
                    "INTERRUPT mode",
                )
            )

    else:
        if (
            trigger_type
            == "ANOMALY_DETECTED"
            and trigger_mode
            != "INTERRUPT"
        ):
            violations.append(
                (
                    "CYCLE_HANDOFF_MODE_MISMATCH",
                    "ANOMALY_DETECTED requires "
                    "INTERRUPT mode",
                )
            )

    # --------------------------------------------------------
    # IMP-45 — Audit Gate
    # --------------------------------------------------------

    if (
        audit["decision"] != "PASS"
        or not audit[
            "state_eligible"
        ]
    ):
        violations.append(
            (
                "CYCLE_AUDIT_NOT_ELIGIBLE",
                "Audit Record is not eligible "
                "for state inheritance",
            )
        )

    # --------------------------------------------------------
    # IMP-46 — Purification Gate
    # --------------------------------------------------------

    if (
        purification["output"][
            "status"
        ]
        != "READY_FOR_HANDOFF"
    ):
        violations.append(
            (
                "CYCLE_PURIFICATION_NOT_READY",
                "State Purification is not "
                "READY_FOR_HANDOFF",
            )
        )

    # --------------------------------------------------------
    # IMP-47 — Packet Verification Gate
    # --------------------------------------------------------

    if (
        packet["integrity"][
            "audit_status"
        ]
        != "VERIFIED"
    ):
        violations.append(
            (
                "CYCLE_PACKET_NOT_VERIFIED",
                "output State Packet "
                "is not VERIFIED",
            )
        )

    # --------------------------------------------------------
    # Goal Continuity
    # --------------------------------------------------------

    continuity = (
        cycle["continuity"]
    )

    purification_continuity = (
        purification[
            "continuity_checks"
        ]
    )

    packet_goal_hash = (
        packet[
            "immutable_goal"
        ]["goal_hash"]
    )

    goal_match = (
        continuity[
            "goal_hash_before"
        ]
        == purification_continuity[
            "goal_hash_before"
        ]
        and continuity[
            "goal_hash_after"
        ]
        == purification_continuity[
            "goal_hash_after"
        ]
        and continuity[
            "goal_hash_after"
        ]
        == packet_goal_hash
    )

    if not goal_match:
        violations.append(
            (
                "CYCLE_GOAL_MISMATCH",
                "goal hashes are "
                "inconsistent across the "
                "Metabolism Cycle",
            )
        )

    cycle_hashes_equal = (
        continuity[
            "goal_hash_before"
        ]
        == continuity[
            "goal_hash_after"
        ]
    )

    if (
        continuity[
            "immutable_goal_preserved"
        ]
        != cycle_hashes_equal
    ):
        violations.append(
            (
                "CYCLE_GOAL_MISMATCH",
                "immutable_goal_preserved "
                "does not match cycle "
                "goal-hash continuity",
            )
        )

    if (
        continuity[
            "immutable_goal_preserved"
        ]
        != purification_continuity[
            "immutable_goal_preserved"
        ]
    ):
        violations.append(
            (
                "CYCLE_GOAL_MISMATCH",
                "cycle goal-continuity "
                "declaration does not match "
                "Purification Record",
            )
        )

    # --------------------------------------------------------
    # IMP-49 — Raw Trace Non-Inheritance
    # --------------------------------------------------------

    if continuity[
        "raw_trace_inherited"
    ]:
        violations.append(
            (
                "CYCLE_RAW_TRACE_INHERITED",
                "completed metabolism "
                "must not inherit raw "
                "reasoning traces",
            )
        )

    if packet[
        "inheritance_policy"
    ]["raw_trace_inherited"]:
        violations.append(
            (
                "CYCLE_RAW_TRACE_INHERITED",
                "output State Packet "
                "declares raw trace "
                "inheritance",
            )
        )

    if (
        purification[
            "inheritance_summary"
        ][
            "raw_trace_items_inherited"
        ]
        != 0
    ):
        violations.append(
            (
                "CYCLE_RAW_TRACE_INHERITED",
                "Purification Record "
                "contains inherited raw "
                "reasoning traces",
            )
        )

    # --------------------------------------------------------
    # Evidence Preservation
    # --------------------------------------------------------

    if not continuity[
        "evidence_preserved"
    ]:
        violations.append(
            (
                "CYCLE_EVIDENCE_NOT_PRESERVED",
                "Metabolism Cycle must "
                "preserve auditable evidence",
            )
        )

    if not packet[
        "inheritance_policy"
    ]["evidence_preserved"]:
        violations.append(
            (
                "CYCLE_EVIDENCE_NOT_PRESERVED",
                "output State Packet does "
                "not preserve evidence",
            )
        )

    if not purification_continuity[
        "evidence_traceability_preserved"
    ]:
        violations.append(
            (
                "CYCLE_EVIDENCE_NOT_PRESERVED",
                "Purification Record does "
                "not preserve evidence "
                "traceability",
            )
        )

    # --------------------------------------------------------
    # IMP-48 — Cross-Record Gate
    # --------------------------------------------------------

    cross_violations = (
        cross_record_violations(
            audit,
            purification,
            packet,
        )
    )

    actual_cross_pass = (
        len(cross_violations) == 0
    )

    declared_cross_pass = (
        continuity[
            "cross_record_conformance_passed"
        ]
    )

    if not actual_cross_pass:
        violations.append(
            (
                "CYCLE_CROSS_RECORD_FAILURE",
                "Audit -> Purification -> "
                "Packet Cross-Record "
                "Conformance failed",
            )
        )

    if (
        declared_cross_pass
        != actual_cross_pass
    ):
        violations.append(
            (
                "CYCLE_CROSS_RECORD_FAILURE",
                "declared Cross-Record "
                "Conformance result does "
                "not match actual result",
            )
        )

    # --------------------------------------------------------
    # IMP-50 — Builder Eligibility
    # --------------------------------------------------------

    outcome = cycle["outcome"]

    if (
        outcome["status"]
        == "COMPLETED"
    ):
        if not outcome[
            "next_builder_eligible"
        ]:
            violations.append(
                (
                    "CYCLE_OUTCOME_INVALID",
                    "COMPLETED cycle must "
                    "make next Builder "
                    "eligible",
                )
            )

    else:
        if outcome[
            "next_builder_eligible"
        ]:
            violations.append(
                (
                    "CYCLE_OUTCOME_INVALID",
                    "non-COMPLETED cycle "
                    "cannot make next "
                    "Builder eligible",
                )
            )

    return violations


# ============================================================
# Metabolism Cycle Case Validation
# ============================================================

def validate_metabolism_cycle_case(
    case_path: Path,
    validators: dict[
        str,
        Draft202012Validator,
    ],
) -> tuple[
    list[str],
    list[str],
    list[tuple[str, str]],
]:
    """
    Validate a complete v0.5 Metabolism Cycle Conformance Case.
    """

    try:
        case = load_json(case_path)
    except json.JSONDecodeError as exc:
        return [
            (
                f"invalid JSON: "
                f"line {exc.lineno}, "
                f"column {exc.colno}: "
                f"{exc.msg}"
            )
        ], [], []

    # --------------------------------------------------------
    # Case Schema
    # --------------------------------------------------------

    case_validator = validators[
        "metabolism-cycle-conformance-case"
    ]

    case_schema_errors = [
        error.message
        for error in sorted(
            case_validator.iter_errors(
                case
            ),
            key=lambda item: list(
                item.absolute_path
            ),
        )
    ]

    if case_schema_errors:
        return [], case_schema_errors, []

    # --------------------------------------------------------
    # Resolve linked records
    # --------------------------------------------------------

    try:
        cycle_path = resolve_repo_path(
            case["cycle_record_path"]
        )

        handoff_path = resolve_repo_path(
            case["handoff_event_path"]
        )

        audit_path = resolve_repo_path(
            case["audit_record_path"]
        )

        purification_path = (
            resolve_repo_path(
                case[
                    "purification_record_path"
                ]
            )
        )

        packet_path = resolve_repo_path(
            case[
                "output_state_packet_path"
            ]
        )

        governor_path = None

        if (
            case[
                "governor_assessment_path"
            ]
            is not None
        ):
            governor_path = (
                resolve_repo_path(
                    case[
                        "governor_assessment_path"
                    ]
                )
            )

    except ValueError as exc:
        return [], [], [
            (
                "CYCLE_RECORD_REFERENCE_MISMATCH",
                str(exc),
            )
        ]

    # --------------------------------------------------------
    # Validate linked records independently
    # --------------------------------------------------------

    linked_records: list[
        tuple[
            Path,
            str,
        ]
    ] = [
        (
            cycle_path,
            "metabolism-cycle-record",
        ),
        (
            handoff_path,
            "handoff-event",
        ),
        (
            audit_path,
            "audit-record",
        ),
        (
            purification_path,
            "state-purification-record",
        ),
        (
            packet_path,
            "state-packet",
        ),
    ]

    if governor_path is not None:
        linked_records.append(
            (
                governor_path,
                "shift-governor-assessment",
            )
        )

    for (
        linked_path,
        linked_type,
    ) in linked_records:

        if not linked_path.exists():
            return [], [], [
                (
                    "CYCLE_RECORD_REFERENCE_MISMATCH",
                    "linked lifecycle record "
                    "does not exist: "
                    f"{linked_path}",
                )
            ]

        (
            syntax_errors,
            linked_schema_errors,
            linked_semantic_errors,
        ) = validate_path_as(
            linked_path,
            linked_type,
            validators,
        )

        if syntax_errors:
            return syntax_errors, [], []

        if linked_schema_errors:
            return [], [
                (
                    f"{linked_path.relative_to(ROOT)}: "
                    + " | ".join(
                        linked_schema_errors
                    )
                )
            ], []

        if linked_semantic_errors:
            return [], [], [
                (
                    "CYCLE_RECORD_REFERENCE_MISMATCH",
                    f"{linked_path.relative_to(ROOT)}: "
                    + " | ".join(
                        linked_semantic_errors
                    ),
                )
            ]

    # --------------------------------------------------------
    # Load records
    # --------------------------------------------------------

    cycle = load_json(
        cycle_path
    )

    handoff = load_json(
        handoff_path
    )

    audit = load_json(
        audit_path
    )

    purification = load_json(
        purification_path
    )

    packet = load_json(
        packet_path
    )

    governor = None

    if governor_path is not None:
        governor = load_json(
            governor_path
        )

    # --------------------------------------------------------
    # Full-cycle validation
    # --------------------------------------------------------

    violations = (
        metabolism_cycle_violations(
            cycle,
            governor,
            handoff,
            audit,
            purification,
            packet,
        )
    )

    return [], [], violations


# ============================================================
# Validator Initialization
# ============================================================

def build_validators(
) -> dict[
    str,
    Draft202012Validator,
]:
    """
    Load and verify every IMP schema.
    """
    validators: dict[
        str,
        Draft202012Validator,
    ] = {}

    for (
        record_type,
        schema_path,
    ) in SCHEMA_FILES.items():

        schema = load_json(
            schema_path
        )

        Draft202012Validator.check_schema(
            schema
        )

        validators[
            record_type
        ] = Draft202012Validator(
            schema,
            format_checker=FormatChecker(),
        )

        print(
            f"schema [{record_type}]: "
            f"{schema_path.relative_to(ROOT)}"
        )

    return validators


# ============================================================
# Ordinary Pass Examples
# ============================================================

def validate_pass_examples(
    validators: dict[
        str,
        Draft202012Validator,
    ],
) -> int:

    unexpected = 0

    print("\n[pass examples]")

    for path in sorted(
        PASS_DIR.glob("*.json")
    ):
        (
            syntax_errors,
            schema_errors,
            local_errors,
        ) = validate_file(
            path,
            validators,
        )

        print(
            f"\n- "
            f"{path.relative_to(ROOT)}"
        )

        if syntax_errors:
            unexpected += 1

            print("[syntax-error]")

            for error in syntax_errors:
                print(f"  - {error}")

            continue

        print("[syntax-ok]")

        if schema_errors:
            unexpected += 1

            print("[schema-error]")

            for error in schema_errors:
                print(f"  - {error}")

            continue

        print("[schema-ok]")

        if local_errors:
            unexpected += 1

            print("[semantic-error]")

            for error in local_errors:
                print(f"  - {error}")

            continue

        print("[semantic-ok]")

    return unexpected


# ============================================================
# Ordinary Fail Examples
# ============================================================

def validate_fail_examples(
    validators: dict[
        str,
        Draft202012Validator,
    ],
) -> int:

    unexpected = 0

    print("\n[fail examples]")

    for path in sorted(
        FAIL_DIR.glob("*.json")
    ):
        (
            syntax_errors,
            schema_errors,
            local_errors,
        ) = validate_file(
            path,
            validators,
        )

        print(
            f"\n- "
            f"{path.relative_to(ROOT)}"
        )

        if syntax_errors:
            unexpected += 1

            print(
                "[unexpected-syntax-failure]"
            )

            for error in syntax_errors:
                print(f"  - {error}")

            continue

        print("[syntax-ok]")

        if schema_errors:
            print(
                "[expected-schema-failure]"
            )

            for error in schema_errors:
                print(f"  - {error}")

            continue

        print("[schema-ok]")

        if local_errors:
            print(
                "[expected-semantic-failure]"
            )

            for error in local_errors:
                print(f"  - {error}")

            continue

        unexpected += 1

        print("[unexpected-pass]")

    return unexpected


# ============================================================
# Cross-Record Pass Cases
# ============================================================

def validate_cross_record_pass_cases(
    validators: dict[
        str,
        Draft202012Validator,
    ],
) -> int:

    unexpected = 0

    print(
        "\n[cross-record conformance: pass]"
    )

    for path in sorted(
        CONFORMANCE_PASS_DIR.glob(
            "*.json"
        )
    ):
        (
            syntax_errors,
            schema_errors,
            violations,
        ) = validate_cross_record_case(
            path,
            validators,
        )

        print(
            f"\n- "
            f"{path.relative_to(ROOT)}"
        )

        if syntax_errors:
            unexpected += 1

            print("[syntax-error]")

            for error in syntax_errors:
                print(f"  - {error}")

            continue

        print("[syntax-ok]")

        if schema_errors:
            unexpected += 1

            print("[schema-error]")

            for error in schema_errors:
                print(f"  - {error}")

            continue

        print("[schema-ok]")

        if violations:
            unexpected += 1

            print(
                "[cross-record-error]"
            )

            for (
                code,
                message,
            ) in violations:
                print(
                    f"  - {code}: "
                    f"{message}"
                )

            continue

        print("[cross-record-ok]")

    return unexpected


# ============================================================
# Cross-Record Fail Cases
# ============================================================

def validate_cross_record_fail_cases(
    validators: dict[
        str,
        Draft202012Validator,
    ],
) -> int:

    unexpected = 0

    print(
        "\n[cross-record conformance: fail]"
    )

    for path in sorted(
        CONFORMANCE_FAIL_DIR.glob(
            "*.json"
        )
    ):
        print(
            f"\n- "
            f"{path.relative_to(ROOT)}"
        )

        try:
            case = load_json(path)
        except json.JSONDecodeError as exc:
            unexpected += 1

            print(
                "[unexpected-syntax-failure]"
            )

            print(
                "  - invalid JSON: "
                f"line {exc.lineno}, "
                f"column {exc.colno}: "
                f"{exc.msg}"
            )

            continue

        (
            syntax_errors,
            schema_errors,
            violations,
        ) = validate_cross_record_case(
            path,
            validators,
        )

        if syntax_errors:
            unexpected += 1

            print("[syntax-error]")

            for error in syntax_errors:
                print(f"  - {error}")

            continue

        print("[syntax-ok]")

        if schema_errors:
            unexpected += 1

            print("[schema-error]")

            for error in schema_errors:
                print(f"  - {error}")

            continue

        print("[schema-ok]")

        if not violations:
            unexpected += 1

            print(
                "[unexpected-cross-record-pass]"
            )

            continue

        actual_codes = {
            code
            for (
                code,
                _,
            ) in violations
        }

        expected_codes = set(
            case[
                "expected_violation_codes"
            ]
        )

        if (
            actual_codes
            != expected_codes
        ):
            unexpected += 1

            print(
                "[unexpected-violation-set]"
            )

            print(
                "  expected: "
                f"{sorted(expected_codes)}"
            )

            print(
                "  actual:   "
                f"{sorted(actual_codes)}"
            )

            for (
                code,
                message,
            ) in violations:
                print(
                    f"  - {code}: "
                    f"{message}"
                )

            continue

        print(
            "[expected-cross-record-failure]"
        )

        for (
            code,
            message,
        ) in violations:
            print(
                f"  - {code}: "
                f"{message}"
            )

    return unexpected


# ============================================================
# Metabolism Cycle Pass Cases
# ============================================================

def validate_cycle_pass_cases(
    validators: dict[
        str,
        Draft202012Validator,
    ],
) -> int:

    unexpected = 0

    print(
        "\n[metabolism-cycle conformance: pass]"
    )

    for path in sorted(
        CYCLE_PASS_DIR.glob(
            "*.json"
        )
    ):
        (
            syntax_errors,
            schema_errors,
            violations,
        ) = validate_metabolism_cycle_case(
            path,
            validators,
        )

        print(
            f"\n- "
            f"{path.relative_to(ROOT)}"
        )

        if syntax_errors:
            unexpected += 1

            print("[syntax-error]")

            for error in syntax_errors:
                print(f"  - {error}")

            continue

        print("[syntax-ok]")

        if schema_errors:
            unexpected += 1

            print("[schema-error]")

            for error in schema_errors:
                print(f"  - {error}")

            continue

        print("[schema-ok]")

        if violations:
            unexpected += 1

            print(
                "[metabolism-cycle-error]"
            )

            for (
                code,
                message,
            ) in violations:
                print(
                    f"  - {code}: "
                    f"{message}"
                )

            continue

        print(
            "[metabolism-cycle-ok]"
        )

    return unexpected


# ============================================================
# Metabolism Cycle Fail Cases
# ============================================================

def validate_cycle_fail_cases(
    validators: dict[
        str,
        Draft202012Validator,
    ],
) -> int:

    unexpected = 0

    print(
        "\n[metabolism-cycle conformance: fail]"
    )

    for path in sorted(
        CYCLE_FAIL_DIR.glob(
            "*.json"
        )
    ):
        print(
            f"\n- "
            f"{path.relative_to(ROOT)}"
        )

        try:
            case = load_json(path)
        except json.JSONDecodeError as exc:
            unexpected += 1

            print(
                "[unexpected-syntax-failure]"
            )

            print(
                "  - invalid JSON: "
                f"line {exc.lineno}, "
                f"column {exc.colno}: "
                f"{exc.msg}"
            )

            continue

        (
            syntax_errors,
            schema_errors,
            violations,
        ) = (
            validate_metabolism_cycle_case(
                path,
                validators,
            )
        )

        if syntax_errors:
            unexpected += 1

            print("[syntax-error]")

            for error in syntax_errors:
                print(f"  - {error}")

            continue

        print("[syntax-ok]")

        if schema_errors:
            unexpected += 1

            print("[schema-error]")

            for error in schema_errors:
                print(f"  - {error}")

            continue

        print("[schema-ok]")

        if not violations:
            unexpected += 1

            print(
                "[unexpected-metabolism-cycle-pass]"
            )

            continue

        actual_codes = {
            code
            for (
                code,
                _,
            ) in violations
        }

        expected_codes = set(
            case[
                "expected_violation_codes"
            ]
        )

        if (
            actual_codes
            != expected_codes
        ):
            unexpected += 1

            print(
                "[unexpected-violation-set]"
            )

            print(
                "  expected: "
                f"{sorted(expected_codes)}"
            )

            print(
                "  actual:   "
                f"{sorted(actual_codes)}"
            )

            for (
                code,
                message,
            ) in violations:
                print(
                    f"  - {code}: "
                    f"{message}"
                )

            continue

        print(
            "[expected-metabolism-cycle-failure]"
        )

        for (
            code,
            message,
        ) in violations:
            print(
                f"  - {code}: "
                f"{message}"
            )

    return unexpected


# ============================================================
# Main
# ============================================================

def main() -> int:
    print(
        "=== Inference Metabolism Protocol "
        "v0.5 Validation ==="
    )

    # --------------------------------------------------------
    # Schema initialization
    # --------------------------------------------------------

    try:
        validators = (
            build_validators()
        )

    except (
        json.JSONDecodeError,
        FileNotFoundError,
        OSError,
        ValueError,
        SchemaError,
    ) as exc:

        print(
            "\n[fatal-schema-initialization-error]"
        )

        print(f"  - {exc}")

        print(
            "\n=== RESULT: FAIL "
            "(schema initialization) ==="
        )

        return 1

    unexpected = 0

    # --------------------------------------------------------
    # Record-local validation
    # --------------------------------------------------------

    unexpected += (
        validate_pass_examples(
            validators
        )
    )

    unexpected += (
        validate_fail_examples(
            validators
        )
    )

    # --------------------------------------------------------
    # v0.4 Cross-Record validation
    # --------------------------------------------------------

    unexpected += (
        validate_cross_record_pass_cases(
            validators
        )
    )

    unexpected += (
        validate_cross_record_fail_cases(
            validators
        )
    )

    # --------------------------------------------------------
    # v0.5 Metabolism Cycle validation
    # --------------------------------------------------------

    unexpected += (
        validate_cycle_pass_cases(
            validators
        )
    )

    unexpected += (
        validate_cycle_fail_cases(
            validators
        )
    )

    # --------------------------------------------------------
    # Final result
    # --------------------------------------------------------

    if unexpected:
        print(
            f"\n=== RESULT: FAIL "
            f"({unexpected} unexpected "
            f"result(s)) ==="
        )

        return 1

    print(
        "\n=== RESULT: PASS ==="
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())

