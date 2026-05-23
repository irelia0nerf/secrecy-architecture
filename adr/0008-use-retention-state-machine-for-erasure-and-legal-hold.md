# ADR-0008 — Use Retention State Machine for Erasure and Legal Hold

## Status

Accepted

## Context

REX Guard preserves sealed evidence for sensitive decisions. Some evidence must be retained for audit, regulatory, dispute-resolution or incident-response purposes. Some related sensitive payloads may also become subject to erasure, restriction, blocking or legal hold requirements.

ADR-0001 separates secret from evidence. ADR-0006 establishes an immutable evidence store. ADR-0007 requires explicit state machines for irreversible side effects.

Immutable storage solves integrity. It does not solve lifecycle governance.

If raw sensitive payloads, content keys or reversible identifiers are committed into immutable evidence, later erasure or restriction may become technically impossible. If evidence is not immutable, audit guarantees weaken. The architecture must separate immutable proof from mutable retention controls.

## Decision

Use an explicit retention state machine for erasure, retention expiry, legal hold and regulatory retention decisions.

The immutable evidence store is the integrity root. It is not the erasure control plane.

The architecture must separate:

```text
immutable evidence store
mutable key and retention plane
encrypted sensitive payload store
analytical indexes
```

The immutable evidence store may contain hashes, signatures, policy versions, retention profile identifiers, legal basis references, state references, receipts and verifier instructions.

It must not contain:

- raw sensitive payloads;
- plaintext PII;
- content keys;
- wrapped content keys;
- reversible lookup tables;
- direct subject identifiers unless explicitly approved by a separate data-retention decision.

Minimum invariant:

```text
raw sensitive payload + decryptable key material must never co-reside in immutable evidence
```

## Retention State Machine

Minimum lifecycle:

```text
CAPTURED
QUARANTINE_PENDING_VALIDATION
QUARANTINE_APPROVED | QUARANTINE_REJECTED
SEALED_IMMUTABLE
RETENTION_ACTIVE
ERASURE_REQUESTED | RETENTION_EXPIRED | LEGAL_HOLD_ACTIVE | REGULATORY_REVIEW
SHRED_APPROVED | SHRED_BLOCKED_BY_LEGAL_HOLD | SHRED_BLOCKED_BY_REGULATORY_RETENTION | MANUAL_DPO_LEGAL_REVIEW
KEY_DESTRUCTION_SCHEDULED
KEY_DESTROYED_OR_UNAVAILABLE
CONTENT_INACCESSIBLE
PURGED
```

A legal hold must block key destruction and payload purge.

A regulatory retention blocker must block destruction unless the controller-approved policy explicitly permits destruction for that data class and retention profile.

An erasure request must not directly destroy keys. It must produce a signed retention decision and move through the state machine.

## Airlock Rule

No artifact may be committed to immutable evidence before quarantine validation succeeds.

The airlock must verify absence of raw sensitive payloads, plaintext PII, content keys, wrapped content keys and reversible lookup tables.

A rejected quarantine artifact must not be sealed.

## Legal Precedence Rule

Legal precedence is owned by the controller, not by runtime code.

The runtime executes a signed policy. It does not decide substantive conflicts between erasure, legal hold and regulatory retention.

A controller-approved precedence matrix must be versioned, signed, referenced by hash and tied to the retention profile.

If no rule covers the case, the state must become:

```text
MANUAL_DPO_LEGAL_REVIEW
```

No key destruction or purge may occur while manual review is active.

## Key Destruction Semantics

Scheduled destruction is not terminal destruction.

The implementation must distinguish:

```text
KEY_DESTRUCTION_SCHEDULED
KEY_DESTROYED_OR_UNAVAILABLE
```

Content may be reported as inaccessible only after the relevant key material is destroyed, unavailable or non-usable under the configured key-management control.

## Consequences

### Positive

- Separates evidence integrity from privacy lifecycle control.
- Prevents sensitive payloads and decryptable key material from being sealed together.
- Makes erasure, legal hold and regulatory retention conflicts explicit.
- Produces auditable reason codes and signed state transitions.
- Supports DPO, legal, compliance and auditor review without manual reconstruction.
- Keeps analytical indexes out of the role of immutable evidence root.

### Negative

- Adds a mutable key and retention control plane.
- Requires controller-owned legal precedence policy.
- Requires quarantine validation before immutable commit.
- Increases lifecycle, hold and destruction test coverage.
- May add latency before evidence sealing.

## Controls Required

- Content keys live outside immutable evidence.
- Key granularity defaults to per decision.
- Broader key granularity requires an explicit retention-profile decision.
- Every retention transition is signed and recoverable.
- Every erasure request produces a retention decision record.
- Analytical indexes are rebuildable from state, receipts and sealed evidence.
- Operator explanation must return current state, reason code, policy hash, authority reference and pending action.

## Validation

This ADR is valid only if:

- immutable evidence bundles contain no raw sensitive payloads;
- immutable evidence bundles contain no plaintext PII;
- immutable evidence bundles contain no content keys or wrapped content keys;
- immutable evidence bundles contain no reversible lookup tables;
- every immutable commit has a passed quarantine validation record;
- legal hold tests prove key destruction and payload purge are blocked;
- regulatory retention tests prove destruction is blocked when policy requires retention;
- erasure tests prove requests create signed retention decisions before destruction;
- unresolved precedence conflicts enter manual review;
- scheduled key destruction is never reported as terminal destruction;
- analytical indexes can be rebuilt from state, receipts and sealed evidence.
