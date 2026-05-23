# Architecture Decision Records

This directory contains accepted architectural decisions for `secrecy-architecture` and the REX Guard production specialization.

ADRs are binding engineering constraints. They are not narrative notes.

---

## Accepted ADRs

| ADR | Decision | Status |
|---|---|---|
| [ADR-0001](./0001-separate-secret-from-evidence.md) | Separate secret from evidence | Accepted |
| [ADR-0002](./0002-fail-closed-by-default.md) | Fail closed by default | Accepted |
| [ADR-0003](./0003-use-spanner-for-chainhead.md) | Use Spanner for ChainHead | Accepted |
| [ADR-0004](./0004-use-bigquery-as-ledger.md) | Use BigQuery as audit ledger | Accepted |
| [ADR-0005](./0005-keep-firebase-out-of-hot-path.md) | Keep Firebase out of the hot path | Accepted |
| [ADR-0006](./0006-use-immutable-evidence-store.md) | Use immutable evidence store for sealed packages | Accepted |
| [ADR-0007](./0007-use-state-machine-for-side-effects.md) | Use state machine for irreversible side effects | Accepted |
| [ADR-0008](./0008-use-retention-state-machine-for-erasure-and-legal-hold.md) | Use retention state machine for erasure and legal hold | Accepted |

---

## Governance Rule

Any implementation that contradicts an accepted ADR must either:

1. create a new ADR superseding the older decision; or
2. be rejected during architecture review.

Silent drift is not allowed.

---

## Review Checklist

Before approving an implementation PR, check:

- [ ] Does it persist raw sensitive payloads?
- [ ] Does it bypass fail-closed behavior?
- [ ] Does it use BigQuery as a transaction coordinator?
- [ ] Does it place Firebase in the hot-path?
- [ ] Does it emit unsigned receipts?
- [ ] Does it allow ledger degradation without durable outbox?
- [ ] Does it weaken ChainHead monotonicity?

Any `yes` answer requires rejection or a superseding ADR.
