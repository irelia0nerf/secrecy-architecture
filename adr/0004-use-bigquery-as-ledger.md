# ADR-0004 — Use BigQuery as Audit Ledger

## Status

Accepted

## Context

The architecture requires durable, queryable, append-oriented audit evidence.

Evidence events must support:

- auditor queries;
- compliance exports;
- evidence pack generation;
- long-term retention policies;
- analytical inspection;
- anomaly detection;
- chain verification.

BigQuery is well-suited for analytical storage and large-scale audit queries. It is not the coordinator for ChainHead advancement.

## Decision

Use BigQuery as the Veritas Ledger for non-reversible evidence events.

BigQuery stores:

- decision identifiers;
- tenant/client identifiers;
- policy hashes;
- input/output hashes;
- final hash;
- signature metadata;
- ChainHead position;
- runtime metadata;
- timestamps;
- ledger status.

BigQuery must not store:

- raw prompts;
- raw responses;
- documents;
- sensitive chunks;
- credentials;
- private keys;
- reconstructable embeddings;
- unredacted personal identifiers unless explicitly justified by a separate data contract.

## Consequences

### Positive

- Enables scalable audit queries.
- Supports partitioning, clustering and retention policies.
- Works well for evidence pack generation.
- Keeps analytical ledger separate from transaction coordination.

### Negative

- Append-only behavior is policy/IAM-driven, not magical immutability.
- Requires strict schema enforcement.
- Requires monitoring for mutation attempts.
- BigQuery outage requires outbox/reconciliation design.

## Controls Required

- Application writer identity has insert-only permissions.
- Human admin access is restricted and audited.
- Dataset/table deletion protection is enabled where available.
- Retention policy is explicit.
- Schema excludes raw payload fields.
- Chain verification jobs run periodically.
- Ledger append failures emit alerts.

## Degraded Mode

If BigQuery is unavailable, degraded mode is acceptable only when:

- evidence has already been signed;
- ChainHead has advanced;
- evidence event is durably queued;
- later reconciliation is guaranteed by operational process;
- client receives explicit degraded status.

Otherwise, the request must fail closed.

## Validation

This ADR is valid only if:

- BigQuery schema validates against `evidence-event.schema.json`;
- payload leakage tests block prohibited fields;
- IAM prevents application update/delete;
- chain verification detects missing or altered events;
- outbox replay is tested.
