#!/usr/bin/env python3
"""
Receipt chain verifier for verifiable secrecy systems.

Checks:
  - JSON Schema conformance (decision-receipt v1 or evidence-event v1)
  - Hash format: all sha256: fields match ^sha256:[a-fA-F0-9]{64}$
  - Chain integrity: for a sequence of events, each previous_hash must equal
    the prior event's current_hash, and sequence_index must be strictly increasing

Does NOT verify cryptographic signatures. Signature verification requires the
KMS public key for the kms_key_version recorded in the receipt — run that check
against your KMS/HSM. This verifier proves structural and chain integrity only.

Usage:
    # Validate a single receipt
    python examples/verify_chain.py examples/receipt.json

    # Validate chain integrity across an ordered list of evidence events
    python examples/verify_chain.py examples/evidence-events.json

    # Explicit schema override
    python examples/verify_chain.py examples/receipt.json \\
        --schema schemas/decision-receipt.schema.json
"""

import argparse
import json
import re
import sys
from pathlib import Path

SCHEMA_VERSION_MAP = {
    "veritas.decision_receipt.v1": "schemas/decision-receipt.schema.json",
    "veritas.evidence_event.v1": "schemas/evidence-event.schema.json",
}

SHA256_RE = re.compile(r"^sha256:[a-fA-F0-9]{64}$")

HASH_FIELDS_RECEIPT = [
    "policy_snapshot_hash",
    "input_hash_sha256",
    "output_hash_sha256",
    "final_hash",
]

HASH_FIELDS_EVENT = [
    "policy_snapshot_hash",
    "input_hash_sha256",
    "output_hash_sha256",
    "final_hash",
    "previous_hash",
    "current_hash",
]


def _load_json(path: str) -> object:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _load_schema(schema_path: str) -> dict:
    return _load_json(schema_path)


def _validate_schema(obj: dict, schema: dict, label: str) -> list[str]:
    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        return ["[skip] jsonschema not installed — run: pip install jsonschema"]

    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(obj), key=lambda e: list(e.path))
    return [f"{label}: {e.message} (path: {list(e.path)})" for e in errors]


def _check_hash_fields(obj: dict, fields: list[str], label: str) -> list[str]:
    errors = []
    for field in fields:
        val = obj.get(field)
        if val is None:
            continue
        if not SHA256_RE.match(str(val)):
            errors.append(f"{label}: {field} has invalid hash format: {val!r}")
    return errors


def _verify_single_receipt(obj: dict, schema: dict) -> list[str]:
    errors = _validate_schema(obj, schema, "schema")
    errors += _check_hash_fields(obj, HASH_FIELDS_RECEIPT, "hash")

    chain = obj.get("chain", {})
    if chain:
        prev = chain.get("previous_hash")
        curr = chain.get("current_hash", "")
        idx = chain.get("sequence_index", 0)
        if idx == 1 and prev is not None:
            errors.append(f"chain: sequence_index=1 but previous_hash is not null: {prev!r}")
        if idx > 1 and prev is not None and not SHA256_RE.match(str(prev)):
            errors.append(f"chain: previous_hash has invalid format: {prev!r}")
        if not SHA256_RE.match(str(curr)):
            errors.append(f"chain: current_hash has invalid format: {curr!r}")
    return errors


def _verify_event_chain(events: list[dict], schema: dict) -> list[str]:
    if not isinstance(events, list):
        return ["input: expected a JSON array of evidence events"]

    errors = []
    sorted_events = sorted(events, key=lambda e: e.get("sequence_index", 0))

    prev_current_hash = None
    prev_seq = 0

    for i, event in enumerate(sorted_events):
        label = f"event[{i}] (seq={event.get('sequence_index')})"
        errors += _validate_schema(event, schema, label)
        errors += _check_hash_fields(event, HASH_FIELDS_EVENT, label)

        seq = event.get("sequence_index", 0)
        if seq <= prev_seq:
            errors.append(f"{label}: sequence_index {seq} is not strictly greater than previous {prev_seq}")

        prev_hash = event.get("previous_hash")
        curr_hash = event.get("current_hash")

        if prev_current_hash is not None:
            if prev_hash != prev_current_hash:
                errors.append(
                    f"{label}: previous_hash {prev_hash!r} does not match "
                    f"prior event current_hash {prev_current_hash!r}"
                )
        elif i == 0 and seq == 1 and prev_hash is not None:
            errors.append(f"{label}: first event (seq=1) should have previous_hash=null, got {prev_hash!r}")

        prev_current_hash = curr_hash
        prev_seq = seq

    return errors


def _detect_schema_path(obj: object, repo_root: Path) -> str | None:
    if isinstance(obj, list) and obj:
        sv = obj[0].get("schema_version", "")
    elif isinstance(obj, dict):
        sv = obj.get("schema_version", "")
    else:
        return None
    rel = SCHEMA_VERSION_MAP.get(sv)
    if rel:
        return str(repo_root / rel)
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify receipt chain integrity.")
    parser.add_argument("input", help="Path to receipt JSON or evidence-event array JSON")
    parser.add_argument("--schema", help="Path to JSON Schema file (auto-detected if omitted)")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    obj = _load_json(args.input)

    schema_path = args.schema or _detect_schema_path(obj, repo_root)
    if not schema_path:
        print("ERROR: cannot detect schema_version — pass --schema explicitly")
        sys.exit(1)

    schema = _load_schema(schema_path)
    print(f"schema : {Path(schema_path).name}")
    print(f"input  : {args.input}")

    if isinstance(obj, list):
        errors = _verify_event_chain(obj, schema)
        print(f"events : {len(obj)}")
    else:
        errors = _verify_single_receipt(obj, schema)

    if errors:
        print(f"\nFAIL — {len(errors)} error(s):")
        for e in errors:
            print(f"  • {e}")
        sys.exit(1)
    else:
        print("\nOK — chain integrity verified")


if __name__ == "__main__":
    main()
