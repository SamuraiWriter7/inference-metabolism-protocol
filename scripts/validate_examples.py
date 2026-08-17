#!/usr/bin/env python3

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


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

FLOAT_TOLERANCE = 1e-6


SCHEMA_FILES = {
    "state-packet":
        SCHEMA_DIR / "state-packet.schema.json",

    "handoff-event":
        SCHEMA_DIR / "handoff-event.schema.json",

    "audit-record":
        SCHEMA_DIR / "audit-record.schema.json",

    "shift-governor-assessment":
        SCHEMA_DIR / "shift-governor-assessment.schema.json",

    "state-purification-record":
        SCHEMA_DIR / "state-purification-record.schema.json",

    "cross-record-conformance-case":
        SCHEMA_DIR
        / "cross-record-conformance-case.schema.json",
}


# ============================================================
# Basic JSON Utilities
# ============================================================

def load_json(path: Path) -> Any:
    """
    Load a JSON document from disk.

    JSON syntax errors are intentionally allowed to propagate so
    callers can classify them separately from schema and semantic
    failures.
    """
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def record_type_for(path: Path) -> str:
    """
    Infer the IMP record type from the filename prefix.

    Examples:

        state-packet.example.json
        state-packet.gen05.json

    both resolve to:

        state-packet
    """
    name = path.name

    for record_type in SCHEMA_FILES:
        if name.startswith(record_type + "."):
            return record_type

    raise ValueError(
        f"cannot infer record type from filename: {path}"
    )


def resolve_repo_path(relative_path: str) -> Path:
    """
    Resolve a repository-relative path while preventing path escape.
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
    Convert a handoff score into the normative Governor decision.
    """
    if score >= thresholds["emergency"]:
        return "EMERGENCY"

    if score >= thresholds["handoff"]:
        return "HANDOFF"

    if score >= thresholds["prepare"]:
        return "PREPARE"

    return "CONTINUE"


# ============================================================
# Record-Local Semantic Validation
# ============================================================

def semantic_errors(
    record_type: str,
    data: dict[str, Any],
) -> list[str]:
    """
    Apply IMP semantic invariants that cannot be fully represented
    by JSON Schema alone.
    """
    errors: list[str] = []

    # --------------------------------------------------------
    # State Packet
    # --------------------------------------------------------

    if record_type == "state-packet":
        generation = data["packet_metadata"]["generation"]

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

        if data["integrity"]["audit_status"] != "VERIFIED":
            errors.append(
                "a Builder-consumable State Packet "
                "must be VERIFIED"
            )

    # --------------------------------------------------------
    # Handoff Event
    # --------------------------------------------------------

    elif record_type == "handoff-event":
        current_generation = data["current_generation"]
        next_generation = data["next_generation"]

        trigger_type = data["trigger"]["type"]
        mode = data["trigger"]["mode"]

        if next_generation != current_generation + 1:
            errors.append(
                "next_generation must equal "
                "current_generation + 1"
            )

        if (
            trigger_type == "ANOMALY_DETECTED"
            and mode != "INTERRUPT"
        ):
            errors.append(
                "ANOMALY_DETECTED must use INTERRUPT mode"
            )

        if (
            trigger_type != "ANOMALY_DETECTED"
            and mode != "NORMAL"
        ):
            errors.append(
                "non-anomaly triggers must use NORMAL mode"
            )

    # --------------------------------------------------------
    # Audit Record
    # --------------------------------------------------------

    elif record_type == "audit-record":
        decision = data["decision"]
        state_eligible = data["state_eligible"]

        if decision == "PASS" and not state_eligible:
            errors.append(
                "PASS audit must be state_eligible = true"
            )

        if decision != "PASS" and state_eligible:
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

        anomaly = data["anomaly_override"]

        # IMP-14 — Weight Normalization
        weight_sum = sum(weights.values())

        if abs(weight_sum - 1.0) > FLOAT_TOLERANCE:
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

        declared_score = data["handoff_score"]

        if (
            abs(calculated_score - declared_score)
            > FLOAT_TOLERANCE
        ):
            errors.append(
                "handoff_score does not match weighted "
                "metric calculation "
                f"(expected={calculated_score:.6f}, "
                f"actual={declared_score:.6f})"
            )

        # IMP-16 — Ordered Thresholds
        prepare = thresholds["prepare"]
        handoff = thresholds["handoff"]
        emergency = thresholds["emergency"]

        if not prepare < handoff < emergency:
            errors.append(
                "thresholds must satisfy "
                "prepare < handoff < emergency"
            )

        anomaly_detected = anomaly["detected"]
        anomaly_reasons = anomaly["reasons"]

        # IMP-18 / IMP-19 — Anomaly Override
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

            if data["decision"] != expected_decision:
                errors.append(
                    "governor decision does not match "
                    "handoff_score thresholds "
                    f"(expected={expected_decision}, "
                    f"actual={data['decision']})"
                )

    # --------------------------------------------------------
    # State Purification Record
    # --------------------------------------------------------

    elif record_type == "state-purification-record":
        source_generation = data["source_generation"]
        target_generation = data["target_generation"]

        # IMP-28 — Generational Continuity
        if target_generation != source_generation + 1:
            errors.append(
                "target_generation must equal "
                "source_generation + 1"
            )

        source = data["source"]

        if (
            source_generation == 1
            and source["previous_packet_id"] is not None
        ):
            errors.append(
                "source generation 1 must have "
                "previous_packet_id = null"
            )

        if (
            source_generation > 1
            and source["previous_packet_id"] is None
        ):
            errors.append(
                "source generation > 1 requires "
                "previous_packet_id"
            )

        classification = data["classification"]

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
            classification["discarded_items"]
        )

        total_count = inherited_count + discarded_count

        summary = data["inheritance_summary"]

        # IMP-24 — Classification Consistency
        if (
            summary["inherited_item_count"]
            != inherited_count
        ):
            errors.append(
                "inherited_item_count does not match "
                "classified inherited items"
            )

        if (
            summary["discarded_item_count"]
            != discarded_count
        ):
            errors.append(
                "discarded_item_count does not match "
                "classified discarded items"
            )

        if (
            summary["total_considered_item_count"]
            != total_count
        ):
            errors.append(
                "total_considered_item_count must equal "
                "inherited items + discarded items"
            )

        # IMP-22 — Zero Raw-Trace Inheritance
        if summary["raw_trace_items_inherited"] != 0:
            errors.append(
                "raw reasoning trace inheritance "
                "must equal 0"
            )

        # IMP-25 — Inheritance Ratio Reproducibility
        if total_count > 0:
            expected_ratio = (
                inherited_count / total_count
            )

            actual_ratio = summary[
                "inheritance_ratio"
            ]

            if (
                abs(actual_ratio - expected_ratio)
                > FLOAT_TOLERANCE
            ):
                errors.append(
                    "inheritance_ratio does not match "
                    "inherited_item_count / "
                    "total_considered_item_count "
                    f"(expected={expected_ratio:.6f}, "
                    f"actual={actual_ratio:.6f})"
                )

        continuity = data["continuity_checks"]

        hashes_equal = (
            continuity["goal_hash_before"]
            == continuity["goal_hash_after"]
        )

        if (
            continuity["immutable_goal_preserved"]
            != hashes_equal
        ):
            errors.append(
                "immutable_goal_preserved must match "
                "goal-hash continuity"
            )

        output = data["output"]
        status = output["status"]

        # IMP-26 / IMP-27 — Handoff Readiness
        if status == "READY_FOR_HANDOFF":
            if output["state_packet_id"] is None:
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
                    "READY_FOR_HANDOFF requires all "
                    "continuity checks to pass: "
                    + ", ".join(failed_checks)
                )

    return errors


# ============================================================
# Single-Record Validation
# ============================================================

def validate_file(
    path: Path,
    validators: dict[str, Draft202012Validator],
) -> tuple[
    list[str],
    list[str],
    list[str],
]:
    """
    Validate one protocol record.

    Returns:

        syntax_errors,
        schema_errors,
        semantic_errors
    """
    try:
        record_type = record_type_for(path)
    except ValueError as exc:
        return [str(exc)], [], []

    try:
        data = load_json(path)
    except json.JSONDecodeError as exc:
        return [
            (
                f"invalid JSON: line {exc.lineno}, "
                f"column {exc.colno}: {exc.msg}"
            )
        ], [], []

    validator = validators[record_type]

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

    local_semantic_errors = semantic_errors(
        record_type,
        data,
    )

    return [], [], local_semantic_errors


# ============================================================
# Cross-Record Canonical Keys
# ============================================================

def fact_key(
    item: dict[str, Any],
) -> tuple[Any, ...]:
    """
    Canonical representation of an inherited verified fact.
    """
    return (
        item["fact_id"],
        item["statement"],
        tuple(
            sorted(item["evidence_refs"])
        ),
    )


def artifact_key(
    item: dict[str, Any],
) -> tuple[Any, ...]:
    """
    Canonical representation of a verified artifact.
    """
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
    Canonical representation shared between Purification Record
    and State Packet.

    The Purification Record contains an additional `reason` field,
    which is intentionally not inherited into the State Packet.
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
    Canonical representation shared between Purification Record
    and State Packet.

    The Purification Record contains `source_ref`, which is retained
    in the purification audit trail rather than copied into the
    State Packet guardrail.
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
    Validate the lineage:

        Audit Record
            ->
        State Purification Record
            ->
        State Packet

    Returns:

        [(violation_code, human_readable_message), ...]
    """
    violations: list[tuple[str, str]] = []

    # --------------------------------------------------------
    # IMP-30 — Generation Alignment
    # --------------------------------------------------------

    if (
        audit["generation"]
        != purification["source_generation"]
    ):
        violations.append(
            (
                "GENERATION_MISMATCH",
                "audit generation does not match "
                "purification source generation",
            )
        )

    if (
        purification["target_generation"]
        != packet["packet_metadata"]["generation"]
    ):
        violations.append(
            (
                "GENERATION_MISMATCH",
                "purification target generation does not "
                "match State Packet generation",
            )
        )

    # --------------------------------------------------------
    # Audit Record Reference
    # --------------------------------------------------------

    if (
        purification["source"]["audit_record_id"]
        != audit["audit_record_id"]
    ):
        violations.append(
            (
                "AUDIT_REFERENCE_MISMATCH",
                "purification audit_record_id does not "
                "match Audit Record",
            )
        )

    # --------------------------------------------------------
    # Resulting State Packet Reference
    # --------------------------------------------------------

    if (
        purification["output"]["state_packet_id"]
        != packet["packet_metadata"]["packet_id"]
    ):
        violations.append(
            (
                "STATE_PACKET_REFERENCE_MISMATCH",
                "purification output state_packet_id "
                "does not match State Packet",
            )
        )

    # --------------------------------------------------------
    # IMP-38 — Provenance Closure
    # --------------------------------------------------------

    provenance = packet["provenance"]
    source = purification["source"]

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
                "State Packet provenance does not match "
                "the Audit/Purification lineage",
            )
        )

    # --------------------------------------------------------
    # IMP-37 — Goal Hash Continuity
    # --------------------------------------------------------

    continuity = purification[
        "continuity_checks"
    ]

    packet_goal_hash = (
        packet["immutable_goal"]["goal_hash"]
    )

    if (
        continuity["goal_hash_after"]
        != packet_goal_hash
    ):
        violations.append(
            (
                "GOAL_HASH_MISMATCH",
                "purified goal hash does not match "
                "State Packet goal hash",
            )
        )

    # --------------------------------------------------------
    # IMP-31 — Audited Fact Origin
    # --------------------------------------------------------

    audited_fact_statements = set(
        audit["verified_facts"]
    )

    purified_verified_facts = (
        purification["classification"]
        ["retained_verified_facts"]
    )

    for fact in purified_verified_facts:
        if (
            fact["statement"]
            not in audited_fact_statements
        ):
            violations.append(
                (
                    "UNAUDITED_FACT_RETAINED",
                    "purification retained unaudited fact: "
                    f"{fact['fact_id']}",
                )
            )

    # --------------------------------------------------------
    # IMP-32 — Audited Artifact Origin
    # --------------------------------------------------------

    audited_artifact_paths = set(
        audit["verified_artifacts"]
    )

    purified_verified_artifacts = (
        purification["classification"]
        ["retained_verified_artifacts"]
    )

    for artifact in purified_verified_artifacts:
        if (
            artifact["path_or_key"]
            not in audited_artifact_paths
        ):
            violations.append(
                (
                    "UNAUDITED_ARTIFACT_RETAINED",
                    "purification retained unaudited "
                    "artifact: "
                    f"{artifact['path_or_key']}",
                )
            )

    # --------------------------------------------------------
    # IMP-33 — Fact Closure
    # --------------------------------------------------------

    purified_facts = {
        fact_key(item)
        for item in purified_verified_facts
    }

    packet_facts = {
        fact_key(item)
        for item in (
            packet["current_state"]
            ["verified_facts"]
        )
    }

    if purified_facts != packet_facts:
        violations.append(
            (
                "PACKET_FACT_SET_MISMATCH",
                "State Packet verified facts differ "
                "from purified verified facts",
            )
        )

    # --------------------------------------------------------
    # IMP-34 — Artifact Closure
    # --------------------------------------------------------

    purified_artifacts = {
        artifact_key(item)
        for item in purified_verified_artifacts
    }

    packet_artifacts = {
        artifact_key(item)
        for item in (
            packet["current_state"]
            ["verified_artifacts"]
        )
    }

    if purified_artifacts != packet_artifacts:
        violations.append(
            (
                "PACKET_ARTIFACT_SET_MISMATCH",
                "State Packet verified artifacts differ "
                "from purified verified artifacts",
            )
        )

    # --------------------------------------------------------
    # IMP-35 — Assumption Closure
    # --------------------------------------------------------

    purified_assumptions = {
        assumption_key(item)
        for item in (
            purification["classification"]
            ["carried_working_assumptions"]
        )
    }

    packet_assumptions = {
        assumption_key(item)
        for item in (
            packet["current_state"]
            ["working_assumptions"]
        )
    }

    if purified_assumptions != packet_assumptions:
        violations.append(
            (
                "PACKET_ASSUMPTION_SET_MISMATCH",
                "State Packet assumptions differ "
                "from purified assumptions",
            )
        )

    # --------------------------------------------------------
    # IMP-36 — Guardrail Closure
    # --------------------------------------------------------

    purified_guardrails = {
        guardrail_key(item)
        for item in (
            purification["classification"]
            ["generated_guardrails"]
        )
    }

    packet_guardrails = {
        guardrail_key(item)
        for item in (
            packet["constraints_and_guardrails"]
            ["do_not_repeat"]
        )
    }

    if purified_guardrails != packet_guardrails:
        violations.append(
            (
                "PACKET_GUARDRAIL_SET_MISMATCH",
                "State Packet guardrails differ "
                "from purified guardrails",
            )
        )

    return violations


# ============================================================
# Cross-Record Case Validation
# ============================================================

def validate_cross_record_case(
    case_path: Path,
    validators: dict[str, Draft202012Validator],
) -> tuple[
    list[str],
    list[str],
    list[tuple[str, str]],
]:
    """
    Validate one Cross-Record Conformance Case.

    Returns:

        syntax_errors,
        schema_errors,
        cross_record_violations
    """

    # --------------------------------------------------------
    # Load case
    # --------------------------------------------------------

    try:
        case = load_json(case_path)
    except json.JSONDecodeError as exc:
        return [
            (
                f"invalid JSON: line {exc.lineno}, "
                f"column {exc.colno}: {exc.msg}"
            )
        ], [], []

    # --------------------------------------------------------
    # Validate case schema
    # --------------------------------------------------------

    case_validator = validators[
        "cross-record-conformance-case"
    ]

    case_schema_errors = [
        error.message
        for error in sorted(
            case_validator.iter_errors(case),
            key=lambda item: list(
                item.absolute_path
            ),
        )
    ]

    if case_schema_errors:
        return [], case_schema_errors, []

    # --------------------------------------------------------
    # Resolve referenced records
    # --------------------------------------------------------

    try:
        audit_path = resolve_repo_path(
            case["audit_record_path"]
        )

        purification_path = resolve_repo_path(
            case["purification_record_path"]
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

    linked_paths = (
        audit_path,
        purification_path,
        packet_path,
    )

    # --------------------------------------------------------
    # Validate each linked record independently first
    # --------------------------------------------------------

    for linked_path in linked_paths:
        if not linked_path.exists():
            return [], [], [
                (
                    "LINKED_RECORD_INVALID",
                    "linked record does not exist: "
                    f"{linked_path}",
                )
            ]

        (
            syntax_errors,
            schema_errors,
            local_semantic_errors,
        ) = validate_file(
            linked_path,
            validators,
        )

        if (
            syntax_errors
            or schema_errors
            or local_semantic_errors
        ):
            details = (
                syntax_errors
                + schema_errors
                + local_semantic_errors
            )

            try:
                display_path = (
                    linked_path.relative_to(ROOT)
                )
            except ValueError:
                display_path = linked_path

            return [], [], [
                (
                    "LINKED_RECORD_INVALID",
                    f"{display_path}: "
                    + " | ".join(details),
                )
            ]

    # --------------------------------------------------------
    # Perform lineage validation
    # --------------------------------------------------------

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
# Schema Initialization
# ============================================================

def build_validators(
) -> dict[str, Draft202012Validator]:
    """
    Load and validate all schemas before testing examples.
    """
    validators: dict[
        str,
        Draft202012Validator,
    ] = {}

    for record_type, schema_path in (
        SCHEMA_FILES.items()
    ):
        schema = load_json(schema_path)

        Draft202012Validator.check_schema(
            schema
        )

        validators[record_type] = (
            Draft202012Validator(
                schema,
                format_checker=FormatChecker(),
            )
        )

        print(
            f"schema [{record_type}]: "
            f"{schema_path.relative_to(ROOT)}"
        )

    return validators


# ============================================================
# Pass Example Validation
# ============================================================

def validate_pass_examples(
    validators: dict[str, Draft202012Validator],
) -> int:
    """
    Validate examples expected to pass.
    """
    unexpected = 0

    print("\n[pass examples]")

    for path in sorted(PASS_DIR.glob("*.json")):
        (
            syntax_errors,
            schema_errors,
            local_semantic_errors,
        ) = validate_file(
            path,
            validators,
        )

        print(
            f"\n- {path.relative_to(ROOT)}"
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

        if local_semantic_errors:
            unexpected += 1
            print("[semantic-error]")

            for error in local_semantic_errors:
                print(f"  - {error}")

            continue

        print("[semantic-ok]")

    return unexpected


# ============================================================
# Fail Example Validation
# ============================================================

def validate_fail_examples(
    validators: dict[str, Draft202012Validator],
) -> int:
    """
    Validate examples intentionally designed to fail.

    Invalid JSON syntax is NOT considered an acceptable negative
    conformance example. Negative examples must remain valid JSON.
    """
    unexpected = 0

    print("\n[fail examples]")

    for path in sorted(FAIL_DIR.glob("*.json")):
        (
            syntax_errors,
            schema_errors,
            local_semantic_errors,
        ) = validate_file(
            path,
            validators,
        )

        print(
            f"\n- {path.relative_to(ROOT)}"
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

        if local_semantic_errors:
            print(
                "[expected-semantic-failure]"
            )

            for error in local_semantic_errors:
                print(f"  - {error}")

            continue

        unexpected += 1
        print("[unexpected-pass]")

    return unexpected


# ============================================================
# Cross-Record Pass Cases
# ============================================================

def validate_cross_record_pass_cases(
    validators: dict[str, Draft202012Validator],
) -> int:
    """
    Validate cross-record cases expected to pass.
    """
    unexpected = 0

    print(
        "\n[cross-record conformance: pass]"
    )

    for path in sorted(
        CONFORMANCE_PASS_DIR.glob("*.json")
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
            f"\n- {path.relative_to(ROOT)}"
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
            print("[cross-record-error]")

            for code, message in violations:
                print(
                    f"  - {code}: {message}"
                )

            continue

        print("[cross-record-ok]")

    return unexpected


# ============================================================
# Cross-Record Fail Cases
# ============================================================

def validate_cross_record_fail_cases(
    validators: dict[str, Draft202012Validator],
) -> int:
    """
    Validate cross-record cases intentionally designed to fail.

    The actual violation-code set must match the expected set
    declared by the conformance case.
    """
    unexpected = 0

    print(
        "\n[cross-record conformance: fail]"
    )

    for path in sorted(
        CONFORMANCE_FAIL_DIR.glob("*.json")
    ):
        print(
            f"\n- {path.relative_to(ROOT)}"
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
            for code, _ in violations
        }

        expected_codes = set(
            case["expected_violation_codes"]
        )

        if actual_codes != expected_codes:
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

            for code, message in violations:
                print(
                    f"  - {code}: {message}"
                )

            continue

        print(
            "[expected-cross-record-failure]"
        )

        for code, message in violations:
            print(
                f"  - {code}: {message}"
            )

    return unexpected


# ============================================================
# Main
# ============================================================

def main() -> int:
    print(
        "=== Inference Metabolism Protocol "
        "v0.4 Validation ==="
    )

    try:
        validators = build_validators()
    except (
        json.JSONDecodeError,
        FileNotFoundError,
        ValueError,
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

    unexpected += validate_pass_examples(
        validators
    )

    unexpected += validate_fail_examples(
        validators
    )

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

    if unexpected:
        print(
            f"\n=== RESULT: FAIL "
            f"({unexpected} unexpected result(s)) ==="
        )

        return 1

    print("\n=== RESULT: PASS ===")

    return 0


if __name__ == "__main__":
    sys.exit(main())
