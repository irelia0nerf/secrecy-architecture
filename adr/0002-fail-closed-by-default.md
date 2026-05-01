# ADR-0002 — Fail Closed by Default

## Status

Accepted

## Context

A verifiable secrecy system loses its core value when sensitive operations continue after governance controls fail.

The following failures invalidate trustworthy execution:

- policy engine unavailable;
- missing policy snapshot;
- authorization failure;
- KMS signing failure;
- ChainHead advancement failure;
- zero-persistence violation;
- schema validation failure;
- replay detection;
- unsafe logging configuration.

Fail-open behavior would produce decisions without enforceable policy, without cryptographic proof, or without consistent audit state.

## Decision

The default behavior for critical control failure is `FAIL_CLOSED`.

The system must deny or stop sensitive execution when it cannot prove that the operation is authorized, governed, signed, and chain-consistent.

Allowed decision outcomes:

```text
ALLOW
DENY
REVIEW
FAIL_CLOSED
```

`ALLOW` requires all critical controls to pass.

## Consequences

### Positive

- Prevents ungoverned sensitive execution.
- Makes control failure visible instead of silently bypassed.
- Aligns with regulated-environment expectations.
- Preserves trust in the audit trail.

### Negative

- Availability may be reduced during dependency outages.
- KMS, policy engine and ChainHead become hard dependencies.
- Incorrect configuration may block legitimate traffic.
- Requires operational maturity and runbooks.

## Failure Policy

| Failure | Behavior |
|---|---|
| Missing identity | DENY |
| Missing authorization | DENY |
| Policy unavailable | FAIL_CLOSED |
| Policy snapshot missing | FAIL_CLOSED |
| KMS signing failed | FAIL_CLOSED |
| ChainHead advance failed | FAIL_CLOSED |
| Ledger append failed | degraded only with durable outbox |
| Zero-persistence violation | poison pill |
| Payload schema violation | DENY |
| Replay detected | DENY |

## Degraded Mode Rule

Degraded mode is allowed only when:

1. the operation has already been authorized;
2. the receipt has been signed;
3. ChainHead has advanced consistently;
4. evidence is durably queued for reconciliation;
5. the client receives explicit `ledger_status=degraded` or `pending_reconciliation`.

If any of those conditions is false, the system must fail closed.

## Validation

This ADR is valid only if:

- failure-mode tests exist for every critical dependency;
- CI/CD rejects fail-open behavior in critical paths;
- runtime emits explicit failure codes;
- dashboards and alerts track fail-closed rates;
- runbooks exist for KMS, policy, ChainHead and ledger incidents.
