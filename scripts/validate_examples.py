#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "schemas"
PASS_DIR = ROOT / "examples" / "pass"
FAIL_DIR = ROOT / "examples" / "fail"


SCHEMA_FILES = {
    "state-packet": SCHEMA_DIR / "state-packet.schema.json",
    "handoff-event": SCHEMA_DIR / "handoff-event.schema.json",
    "audit-record": SCHEMA_DIR / "audit-record.schema.json",
}


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def record_type_for(path: Path) -> str:
    name = path.name

    for record_type in SCHEMA_FILES:
        if name.startswith(record_type + "."):
            return record_type

    raise ValueError(
        f"cannot infer record type from filename: {path}"
    )


def semantic_errors(
    record_type: str,
    data: dict[str, Any],
) -> list[str]:

    errors: list[str] = []

    if record_type == "state-packet":
        generation = data["packet_metadata"]["generation"]
        previous_packet_id = data["provenance"]["previous_packet_id"]

        if generation == 1 and previous_packet_id is not None:
            errors.append(
                "generation 1 must have previous_packet_id = null"
            )

        if generation > 1 and previous_packet_id is None:
            errors.append(
                "generation > 1 requires previous_packet_id"
            )

        if data["integrity"]["audit_status"] != "VERIFIED":
            errors.append(
                "a Builder-consumable State Packet must be VERIFIED"
            )

    elif record_type == "handoff-event":
        current_generation = data["current_generation"]
        next_generation = data["next_generation"]

        trigger_type = data["trigger"]["type"]
        mode = data["trigger"]["mode"]

        if next_generation != current_generation + 1:
            errors.append(
                "next_generation must equal current_generation + 1"
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

    elif record_type == "audit-record":
        decision = data["decision"]
        state_eligible = data["state_eligible"]

        if decision == "PASS" and not state_eligible:
            errors.append(
                "PASS audit must be state_eligible = true"
            )

        if decision != "PASS" and state_eligible:
            errors.append(
                "non-PASS audit must be state_eligible = false"
            )

    return errors


def validate_file(
    path: Path,
    validators: dict[str, Draft202012Validator],
) -> tuple[list[str], list[str]]:

    record_type = record_type_for(path)
    data = load_json(path)

    schema_errors = [
        error.message
        for error in sorted(
            validators[record_type].iter_errors(data),
            key=lambda item: list(item.absolute_path),
        )
    ]

    if schema_errors:
        return schema_errors, []

    return [], semantic_errors(record_type, data)


def main() -> int:
    print(
        "=== Inference Metabolism Protocol v0.1 Validation ==="
    )

    validators: dict[str, Draft202012Validator] = {}

    for record_type, schema_path in SCHEMA_FILES.items():
        schema = load_json(schema_path)

        Draft202012Validator.check_schema(schema)

        validators[record_type] = Draft202012Validator(
            schema,
            format_checker=FormatChecker(),
        )

        print(
            f"schema [{record_type}]: "
            f"{schema_path.relative_to(ROOT)}"
        )

    unexpected = 0

    print("\n[pass examples]")

    for path in sorted(PASS_DIR.glob("*.json")):
        schema_errors, semantic = validate_file(
            path,
            validators,
        )

        print(f"\n- {path.relative_to(ROOT)}")

        if schema_errors:
            unexpected += 1
            print("[schema-error]")

            for error in schema_errors:
                print(f"  - {error}")

            continue

        print("[schema-ok]")

        if semantic:
            unexpected += 1
            print("[semantic-error]")

            for error in semantic:
                print(f"  - {error}")

        else:
            print("[semantic-ok]")

    print("\n[fail examples]")

    for path in sorted(FAIL_DIR.glob("*.json")):
        schema_errors, semantic = validate_file(
            path,
            validators,
        )

        print(f"\n- {path.relative_to(ROOT)}")

        if schema_errors:
            print("[expected-schema-failure]")

            for error in schema_errors:
                print(f"  - {error}")

            continue

        if semantic:
            print("[expected-semantic-failure]")

            for error in semantic:
                print(f"  - {error}")

            continue

        unexpected += 1
        print("[unexpected-pass]")

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
