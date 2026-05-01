# Veritas Schemas

This directory contains the canonical JSON Schemas for verifiable secrecy evidence objects.

The schemas are implementation contracts. They are not documentation-only artifacts.

---

## Files

| Schema | Purpose |
|---|---|
| [`decision-receipt.schema.json`](./decision-receipt.schema.json) | Client-facing receipt returned after a governed sensitive operation. |
| [`evidence-event.schema.json`](./evidence-event.schema.json) | Append-only ledger event stored as non-reversible audit evidence. |

---

## Core Invariants

### 1. No raw payloads

Evidence objects must never contain raw sensitive payloads.

Forbidden fields include, but are not limited to:

- `raw_prompt`
- `prompt`
- `raw_response`
- `response`
- `document_text`
- `document_content`
- `payload`
- `body`
- `cpf`
- `ssn`
- `password`
- `access_token`
- `refresh_token`
- `api_key`
- `private_key`
- `embedding`
- `chunk_text`

### 2. Hashes are explicit and prefixed

All SHA-256 hashes must use the following format:

```text
sha256:<64 hex characters>
```

Example:

```text
sha256:4d967f0b9f7fd03c8b8cfa9b94c5df3a1f7b5f6d1be2db6d20dfc2c6f1a8c9b0
```

### 3. Receipts are signed

Every `decision_receipt` must include:

- `final_hash`
- `signature.algorithm`
- `signature.kms_key_version`
- `signature.signature_base64`

### 4. Ledger events are append-only evidence

`evidence_event` objects represent ledger rows. They must include:

- decision identity;
- policy hash;
- input/output hashes;
- final hash;
- signature metadata;
- chain position;
- ledger status;
- timestamp.

### 5. Chain position is monotonic

For each `client_id` or chain partition:

```text
sequence_index(n+1) > sequence_index(n)
```

Two concurrent decisions for the same chain partition must never receive the same `sequence_index`.

---

## Validation Example — Node.js

Install:

```bash
npm install ajv ajv-formats
```

Validate:

```js
import Ajv from "ajv";
import addFormats from "ajv-formats";
import fs from "node:fs";

const ajv = new Ajv({ allErrors: true, strict: true });
addFormats(ajv);

const schema = JSON.parse(fs.readFileSync("schemas/decision-receipt.schema.json", "utf8"));
const receipt = JSON.parse(fs.readFileSync("examples/receipt.json", "utf8"));

const validate = ajv.compile(schema);

if (!validate(receipt)) {
  console.error(validate.errors);
  process.exit(1);
}

console.log("valid receipt");
```

---

## Validation Example — Python

Install:

```bash
pip install jsonschema
```

Validate:

```python
import json
from jsonschema import Draft202012Validator

with open("schemas/evidence-event.schema.json", "r", encoding="utf-8") as f:
    schema = json.load(f)

with open("examples/evidence-event.json", "r", encoding="utf-8") as f:
    event = json.load(f)

validator = Draft202012Validator(schema)
errors = sorted(validator.iter_errors(event), key=lambda e: e.path)

if errors:
    for error in errors:
        print(error.message)
    raise SystemExit(1)

print("valid evidence event")
```

---

## CI/CD Gate Recommendation

Every implementation should block merge if:

- an evidence object violates schema;
- a receipt contains raw payload fields;
- a ledger event contains raw payload fields;
- a hash is not prefixed with `sha256:`;
- `signature` metadata is missing;
- `sequence_index` regression is detected in chain tests;
- `ledger_status=degraded` is emitted without a durable outbox path.

Suggested pipeline gate:

```bash
npm run test:schemas
npm run test:zero-persistence
npm run test:chainhead
```

---

## Production Notes

These schemas enforce shape, not full semantic truth.

Additional runtime checks are still required for:

- canonicalization correctness;
- signature verification;
- KMS key version validity;
- chain monotonicity;
- ledger append-only IAM;
- absence of payload in logs, traces and error reporting;
- outbox durability during degraded ledger mode.

Schema validation is a necessary control. It is not sufficient by itself.
