# ADR-0003 — Use Spanner for ChainHead

## Status

Accepted

## Context

The architecture requires a tamper-evident chain of decisions.

Each new decision must advance a chain position:

```text
previous_hash -> current_hash
sequence_index(n) -> sequence_index(n+1)
```

This operation is coordination-sensitive. Two concurrent decisions for the same chain partition must not receive the same `sequence_index` or overwrite the same chain head.

BigQuery is strong for analytical ledger storage, but it is not the right primitive for hot-path transactional chain advancement.

## Decision

Use Cloud Spanner, or an equivalent strongly consistent transactional datastore, to maintain ChainHead state.

The ChainHead state is keyed by chain partition, normally:

```text
client_id
```

or, for high-volume workloads:

```text
client_id + route
client_id + shard_id
client_id + policy_domain
```

## ChainHead Record

```json
{
  "client_id": "string",
  "head_hash": "sha256:hex",
  "sequence_index": 123,
  "updated_at": "RFC3339",
  "last_decision_id": "uuid-v4"
}
```

## `getAndAdvance()` Contract

The operation must be atomic:

1. read current head;
2. compute next `sequence_index`;
3. compute `current_hash` from `previous_hash`, `final_hash`, `decision_id`, and sequence;
4. write new head;
5. return chain metadata.

## Consequences

### Positive

- Provides strong consistency for chain advancement.
- Prevents duplicate sequence assignment under concurrency.
- Separates transaction coordination from analytical ledger storage.
- Supports regional consistency requirements for regulated workloads.

### Negative

- Adds operational dependency and cost.
- Chain partitions can become hot under high throughput.
- Requires careful schema and transaction design.
- May affect latency in the synchronous path.

## Scaling Guidance

Start with per-client chain partitioning.

If contention emerges, shard chain state by:

- tenant;
- route;
- policy domain;
- region;
- deterministic shard ID.

Sharding must preserve audit semantics. Do not shard in a way that makes reconstruction meaningless.

## Validation

This ADR is valid only if:

- concurrency tests prove no duplicate `sequence_index`;
- transaction retry behavior is implemented;
- ChainHead latency is measured p50/p95/p99;
- failure to advance ChainHead causes fail-closed behavior;
- chain verification can detect gaps, reordering and tampering.
