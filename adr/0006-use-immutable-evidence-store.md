# ADR-0006 — Use Immutable Evidence Store for Sealed Evidence Packages

## Status

Accepted

## Context

A verifiable secrecy system needs more than queryable audit metadata. It needs a durable evidence root that can preserve sealed proof artifacts under retention constraints.

Analytical systems such as BigQuery are useful for search, reconciliation, dashboards and reporting, but they are not the architectural root of immutability.

High-assurance deployments require a dedicated evidence store with controls such as:

- retention lock;
- object lock;
- overwrite/delete prevention;
- restrictive IAM;
- administrative audit logs;
- cryptographic hashes;
- signature verification;
- reconciliation with state and analytics.

## Decision

Use an immutable evidence store for sealed evidence packages.

On Google Cloud, the recommended implementation is:

```text
Cloud Storage Bucket Lock
```

Equivalent controls may be used in other environments if they provide comparable retention and deletion/overwrite resistance.

## Evidence Package

A sealed evidence package may contain:

- cryptographic receipt;
- canonical metadata;
- policy result;
- source hashes;
- result hashes;
- model or processor version;
- key version;
- chain links;
- verification instructions;
- schema version;
- evidence object hash.

It must not contain raw sensitive payloads by default.

If a deployment explicitly requires raw payload retention, that must be documented as a separate data-retention decision with legal, security and privacy review.

## Consequences

### Positive

- Establishes a stronger evidence root than analytical storage alone.
- Supports auditor verification and retention controls.
- Enables reconciliation between evidence store, state store and analytical audit views.
- Reduces ambiguity around “immutability”.

### Negative

- Adds storage and retention cost.
- Retention locks can be operationally unforgiving.
- Incorrect retention policy may preserve data longer than needed.
- Requires evidence lifecycle governance.

## Controls Required

- Retention lock or object lock configured for high-assurance profile.
- Application writer cannot overwrite or delete sealed evidence.
- Evidence object hash is stored in the receipt and analytical audit view.
- Evidence object URI is stored without leaking sensitive path semantics.
- Admin changes are logged and reviewed.
- Reconciliation job validates object existence and hash.

## Validation

This ADR is valid only if:

- evidence package format is schema-controlled;
- delete/overwrite tests fail during retention period;
- evidence object hash matches receipt metadata;
- analytical audit view can be rebuilt from sealed evidence and state;
- retention policy is explicitly documented.
