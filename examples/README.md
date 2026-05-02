# Examples

Reference examples for verifiable secrecy system tooling.

---

## verify_chain.py

Standalone Python receipt and chain verifier. Checks:

- JSON Schema conformance (`decision-receipt.schema.json` or `evidence-event.schema.json`)
- Hash field format (`sha256:<64 hex chars>`)
- Chain integrity across a sequence of evidence events (monotonic `sequence_index`, `previous_hash` continuity)

**Does not** verify cryptographic signatures. Signature verification requires the KMS public key for the `kms_key_version` in the receipt — run that check against your KMS/HSM directly.

### Requirements

```bash
pip install jsonschema
```

Schema validation is skipped (with a notice) if `jsonschema` is not installed. Hash and chain checks always run.

### Usage

```bash
# Validate a single receipt
python examples/verify_chain.py examples/receipt.json

# Validate chain integrity across an ordered array of evidence events
python examples/verify_chain.py examples/evidence-events.json

# Explicit schema override
python examples/verify_chain.py examples/receipt.json \
    --schema schemas/decision-receipt.schema.json
```

### Exit codes

| Code | Meaning |
|---|---|
| 0 | All checks passed |
| 1 | One or more checks failed |

---

## Fixture files

| File | Purpose |
|---|---|
| `receipt.json` | Single valid `decision-receipt.schema.json` instance (sequence_index=1, previous_hash=null) |
| `evidence-events.json` | Two-event chain: ALLOW followed by DENY with a broken authorization. Chain links are valid. |

The fixtures use syntactically correct but cryptographically meaningless hashes and signatures. They demonstrate schema structure and chain linking — not real KMS output.
