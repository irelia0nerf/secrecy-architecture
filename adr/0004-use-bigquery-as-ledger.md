# ADR-0004 — Use BigQuery as Analytical Audit View

## Status

Accepted — revised by v1.3 reference architecture

## Context

The architecture requires durable evidence, queryable audit views and operational reporting.

These are different responsibilities:

1. **Consistent State Store** — state transitions, idempotency, ChainHead and operation status.
2. **Immutable Evidence Store** — sealed evidence packages under retention/object lock.
3. **Analytical Audit Store** — queryable views, dashboards, reports and reconciliation.

BigQuery is well-suited for analytical audit materialization and large-scale queries. It should not be treated as the root source of immutability, nor as the transaction coordinator for ChainHead advancement.

## Decision

Use BigQuery as the analytical audit view for non-reversible evidence events.

BigQuery stores queryable materialized metadata such as:

- decision identifiers;
- tenant/client identifiers;
- policy hashes;
- input/output hashes;
- final hash;
- signature metadata;
- ChainHead position;
- evidence object URI/hash;
- runtime metadata;
- timestamps;
- ledger/materialization status.

BigQuery must not store by default:

- raw prompts;
- raw responses;
- documents;
- sensitive chunks;
- credentials;
- private keys;
- reconstructable embeddings;
- unredacted personal identifiers unless explicitly justified by a separate data contract.

## Explicit Non-Decision

This ADR does **not** define BigQuery as the immutable evidence root.

Root evidence should live in an immutable evidence store such as:

- Cloud Storage Bucket Lock;
- object lock equivalent;
- dedicated WORM storage;
- another retention-locked evidence repository.

BigQuery may mirror, index or materialize evidence metadata for audit analytics. It must be reconcilable against the immutable evidence store and the consistent state store.

## Consequences

### Positive

- Enables scalable audit queries.
- Supports partitioning, clustering and reporting.
- Works well for evidence pack search and dashboards.
- Keeps analytical audit separate from transaction coordination and immutable retention.

### Negative

- Requires reconciliation against sealed evidence packages.
- Requires strict schema enforcement.
- Requires monitoring for mutation attempts.
- BigQuery outage requires async materialization/replay design.
- Teams must avoid calling BigQuery itself the WORM root.

## Controls Required

- Application writer identity has append/materialization-only permissions.
- Human admin access is restricted and audited.
- Schema excludes raw payload fields.
- Evidence object URI and hash are stored for reconciliation.
- Chain verification jobs run periodically.
- Analytics table is reconciled against immutable evidence and state store.
- Materialization failures emit alerts.

## Degraded Mode

If BigQuery is unavailable, core operation may continue only when:

- state transition has committed where required;
- receipt has been signed;
- sealed evidence package has been written or durably queued according to profile;
- later analytical materialization is guaranteed by an operational process;
- client or operator receives explicit degraded/materialization-pending status where relevant.

If immutable evidence cannot be preserved in a high-assurance profile, the request must fail closed.

## Validation

This ADR is valid only if:

- BigQuery schema validates against `evidence-event.schema.json`;
- payload leakage tests block prohibited fields;
- BigQuery is reconciled against immutable evidence packages;
- IAM prevents application update/delete beyond intended materialization behavior;
- chain verification detects missing or altered events;
- replay/materialization backfill is tested.
