# ADR-0007 — Use State Machine for Side Effects

## Status

Accepted

## Context

Sensitive operations often have irreversible or externally visible side effects:

- model invocation;
- evidence sealing;
- external API calls;
- notification;
- audit materialization;
- financial or compliance decisions;
- document processing output;
- downstream workflow transition.

Infrastructure timeouts and client disconnects do not guarantee that compute stopped. A request may continue after the client connection closes.

Without explicit state transitions and idempotency, retries can duplicate effects or create inconsistent evidence.

## Decision

Sensitive operations must be modeled as explicit state transitions.

Minimum state machine:

```text
RECEIVED
NORMALIZED
POLICY_CHECKED
APPROVED | DENIED | FAIL_CLOSED
PROCESSED
SIGNED
EVIDENCE_LOCKED
COMMITTED
RECEIPT_EMITTED
```

Irreversible side effects may occur only after the operation reaches a state where:

- idempotency key is registered;
- policy result is known;
- receipt is canonicalized or ready to be canonicalized;
- evidence handling is consistent;
- retries cannot duplicate external effects.

## Timeout Rule

A timeout is not cancellation.

The implementation must support:

- deadline propagation;
- cooperative cancellation;
- idempotency keys;
- state recovery;
- retry-safe transitions;
- explicit side-effect boundaries.

## Client Disconnect Rule

A client disconnect must not implicitly rollback or cancel work.

The system must either:

1. complete the operation according to the state machine; or
2. cancel cooperatively before irreversible side effects; or
3. mark the operation as recoverable/failed with a receipt where appropriate.

## Consequences

### Positive

- Prevents duplicated side effects on retry.
- Makes recovery behavior auditable.
- Clarifies timeout semantics.
- Enables deterministic incident analysis.
- Supports high-assurance review.

### Negative

- Adds state-management complexity.
- Requires idempotency-key design.
- Requires more tests around failure and retry paths.
- May add latency to critical paths.

## Validation

This ADR is valid only if:

- state transitions are persisted in a consistent state store;
- retry tests prove idempotent behavior;
- timeout tests prove no unsafe late side effects;
- client disconnect tests are implemented;
- side-effect boundaries are documented;
- operation recovery is possible after partial failure.
