# ADR-0001 — Separate Secret from Evidence

## Status

Accepted

## Context

Systems that process sensitive data usually preserve auditability by retaining the raw payload or operational artifacts derived from it.

That pattern creates a structural liability:

- more retained payload means larger breach surface;
- audit investigations may require re-exposing sensitive data;
- logs, traces and analytics often become uncontrolled secondary copies;
- regulatory deletion/minimization requirements become harder to enforce.

The architecture requires a stronger invariant:

```text
processed secret != auditable evidence
```

## Decision

Sensitive content must be separated from audit evidence.

The system may persist:

- canonical hashes;
- signatures;
- policy versions;
- chain indexes;
- timestamps;
- non-sensitive operational metadata.

The system must not persist by default:

- raw prompt;
- raw response;
- source document content;
- sensitive chunks;
- reconstructable embeddings;
- credentials;
- private keys;
- direct personal identifiers unless explicitly justified by a separate contract.

## Consequences

### Positive

- Reduces data-retention liability.
- Makes audit possible without exposing payload by default.
- Enables independent verification through hashes and signatures.
- Supports privacy-by-design and minimization arguments.

### Negative

- Debugging becomes harder.
- Auditors need a verifier workflow instead of direct payload inspection.
- Canonicalization must be deterministic and documented.
- Clients may need to retain their own source payload if later reconstruction is required.

## Implementation Requirements

- Receipt schema must forbid raw payload fields.
- Ledger schema must forbid raw payload fields.
- CI/CD must test for payload leakage in evidence objects.
- Logging/tracing/error reporting must use allowlisted metadata only.
- Verification tooling must recalculate hashes from client-held payload when needed.

## Validation

This ADR is valid only if:

- evidence rows contain no raw sensitive content;
- receipts can be verified without raw payload stored in the ledger;
- payload leakage tests are enforced in CI/CD;
- schema validation blocks unapproved fields.
