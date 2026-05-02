# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repository Is

`secrecy-architecture` is a **documentation-only** reference architecture repository. There is no application code, build system, package manager, or test runner. All content is Markdown, JSON Schema, and Architecture Decision Records (ADRs).

The repository defines a domain-neutral reference model for **verifiable secrecy systems**: systems that process sensitive data, prove the operation followed defined rules, and avoid turning the secret into permanent liability.

## Repository Structure

```
docs/reference-architecture-v1.3.md   ← canonical reference (start here)
docs/rex-guard-production-architecture-v1.2.md  ← REX Guard production specialization
arquitetura.md                         ← earlier PT-BR architecture draft
schemas/decision-receipt.schema.json   ← client-facing receipt schema (Veritas v1)
schemas/evidence-event.schema.json     ← append-only ledger event schema (Veritas v1)
adr/                                   ← binding Architecture Decision Records
ROADMAP.md                             ← milestone tracking (honest about delivery status)
```

## Architecture: Core Model

The canonical processing pipeline is:

```
Client → Secure Gateway → Secrecy Boundary → Policy & Decision Layer
       → Ephemeral Processing Layer → Cryptographic Evidence Layer
       → Consistent State Store (Spanner) + Immutable Evidence Store (GCS Bucket Lock)
       → Analytical Audit Store (BigQuery)
       → Non-Sensitive Observability
```

**Critical three-way store separation** — these are not interchangeable:

| Store | Role |
|---|---|
| Consistent State Store (Spanner) | Chain head / monotonic sequence / idempotency |
| Immutable Evidence Store (GCS Bucket Lock) | Sealed evidence packages under retention lock |
| Analytical Audit Store (BigQuery) | Queryable materialization for auditors — not root immutability |

## ADRs (Binding Constraints)

Any implementation contradicting an accepted ADR must either supersede it with a new ADR or be rejected. Silent drift is not allowed.

| ADR | Binding rule |
|---|---|
| ADR-0001 | Raw secrets never enter evidence; evidence uses hashes, signatures, metadata only |
| ADR-0002 | Policy failure, missing identity, signing failure, or ledger failure → FAIL_CLOSED or DENY |
| ADR-0003 | Cloud Spanner holds ChainHead; do not use BigQuery or Firestore for chain monotonicity |
| ADR-0004 | BigQuery is analytical materialization — not the root ledger or transaction coordinator |
| ADR-0005 | Firebase Hosting is not in the critical inference hot path |

## Schemas

Both schemas live under `schemas/` and use JSON Schema draft 2020-12.

- `decision-receipt.schema.json` — the client-facing receipt proving a sensitive operation occurred under a specific policy. Required fields include `decision_id`, `policy_snapshot_hash`, `input_hash_sha256`, `output_hash_sha256`, `final_hash`, `signature` (with `kms_key_version`), `chain` (with `sequence_index`, `previous_hash`, `current_hash`), and `ledger_status`.
- `evidence-event.schema.json` — the append-only ledger record. Uses a `not` constraint to **explicitly reject** raw payload fields: `raw_prompt`, `prompt`, `raw_response`, `response`, `document_text`, `payload`, `body`, `cpf`, `ssn`, `password`, `access_token`, `private_key`, `embedding`, `chunk_text`, and others.

Hash fields must use the format `sha256:<64 hex chars>`. Allowed signature algorithms: `ECDSA_P256_SHA256`, `ECDSA_P384_SHA384`, `RSA_PSS_2048_SHA256`, `ED25519`. Canonicalization must use `RFC8785_JSON_CANONICALIZATION`, `JCS`, or `CUSTOM`.

## Non-Negotiable Principles

When writing or reviewing documentation, code examples, or schema changes:

1. **Secrets do not persist by default.** Sensitive data exists only for the minimum time required.
2. **Evidence never contains raw secrets.** Use `sha256:` hashes, signatures, policy versions, and metadata.
3. **Every sensitive operation emits a receipt.** A receipt is the minimum verifiable unit.
4. **Policy failures fail closed.** Any failure (identity, policy, signing, ledger) → DENY or FAIL_CLOSED. Never fail open.
5. **Logs describe events, not payloads.** Observability never leaks sensitive content.
6. **Immutability is an architectural property.** Calling a warehouse "immutable" without retention lock, IAM restrictions, audit logs, and cryptographic reconciliation is weak architecture.
7. **Timeout ≠ cancellation.** Cloud Run request timeout does not guarantee process termination. Irreversible side effects require explicit state transitions and idempotency.
8. **Confidential computing is a high-assurance profile, not a baseline.** TEEs apply selectively to the segment handling cleartext secrets.

## REX Guard Specialization

`docs/rex-guard-production-architecture-v1.2.md` applies the reference model to regulated AI inference (LLM governance). Key production stances from that document carry the same binding weight as ADRs for REX Guard implementations.

## Roadmap Governance

`ROADMAP.md` tracks milestones with explicit verification criteria. A milestone is "delivered" only when an external party can verify the system property — not when code is merged. When making changes related to roadmap items, preserve the original commitment dates and annotate slippage rather than erasing it.
