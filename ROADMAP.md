# ROADMAP

This roadmap is **honest about its dependencies**. Items here ship when the underlying engineering work ships in the production codebase. Markdown updates in this repository do not constitute progress.

The repository's job is to track architectural commitments, not to dramatize them. If a milestone slips, the dated entry stays; we add a follow-up note explaining why.

---

## Tracking principles

1. **No dates without commits.** A milestone is "in progress" only when there is a corresponding branch in the production codebase with active work. Until then, it is "planned."
2. **No "delivered" without verification.** A milestone is delivered when the corresponding system property can be verified by an external party. Internal "feature complete" does not count.
3. **Slippage is documented, not hidden.** When a target date passes, the entry is annotated with the new target and a one-line reason. The original commitment remains visible.
4. **Architecture drift is a bug.** If shipped code disagrees with this repository, the discrepancy is filed as an issue. Either the code wins (and the architecture is updated) or the architecture wins (and the code is fixed). The disagreement is never left in place.

---

## Q2 2026 — Foundational invariants

### M1: Crypto-shredding made real
**Status:** Planned
**Trigger:** Pilot contract signed
**Deliverable:** The mock `shred_key()` function is removed from the production codebase. All key-destruction calls invoke Cloud KMS `cryptoKeyVersions.destroy()` with immediate scheduling. An external party can run `gcloud kms keys versions describe` against a destroyed key version and observe `state: DESTROYED`.
**Verification:** Public test transcript demonstrating destruction, with timestamps and a reproducible setup. Filed in `examples/` once delivered.

### M2: TEE attestation in production
**Status:** Planned
**Trigger:** Cloud Run + Confidential Space generally available in our deployment region with AMD SEV-SNP at supported tier
**Deliverable:** Every cold-start of REX Guard produces an attestation report verifiable against AMD's root-of-trust chain. The report is exposed at an internal `/attest` endpoint and published with each release.
**Verification:** External auditor can request the attestation report, validate the chain, and confirm the running container hash matches the published image digest.

### M3: Pilot deployment
**Status:** Planned
**Trigger:** Counterparty contract signed
**Deliverable:** A live deployment serving real banking traffic in a Tier-1 BR bank's homologation environment. Volume: target 2-5M req/month. SLOs measured, not projected.
**Verification:** SLO dashboard shared with the counterparty; weekly incident review; monthly cost reconciliation against projection.
**Note:** Until this milestone is real, all latency, cost, and reliability numbers in this repository remain projections.

---

## Q3 2026 — Operational maturity

### M4: Auditor SDK v1.0
**Status:** Planned
**Trigger:** M1 and M3 delivered
**Deliverable:** Standalone Python package, pip-installable, that an auditor can use to read a date range from BigQuery append-only ledger with WORM controls, validate the chain end-to-end, and produce a signed audit report. The package extends `examples/verify_chain.py` with BigQuery integration, public-key cross-validation, and TrueTime monotonicity checks.
**Verification:** Big 4 cyber team independently runs the SDK against the pilot deployment and produces a written assessment.

### M5: Multi-region active-active
**Status:** Planned
**Trigger:** M3 sustained for 90 days without major incident
**Deliverable:** REX Guard runs simultaneously in two GCP regions with automatic failover under 30 seconds. Spanner multi-region configuration validated. ChainHead consistency preserved across the cutover.
**Verification:** Chaos engineering exercise that hard-kills the primary region during live traffic; chain integrity verified post-failover.

### M6: Deterministic mode
**Status:** Planned
**Trigger:** First counterparty request requires reproducibility for regulatory audit
**Deliverable:** Per-tenant feature flag enabling `temperature=0`, fixed seed, and strict JSON mode for Gemini calls. Deterministic outputs verifiable: same input + same tenant = same output, same hash.
**Verification:** Test harness that runs identical inputs N times and asserts byte-equal outputs. Published as part of `examples/`.

---

## Q4 2026 — Scale hardening

### M7: Per-tenant chain sharding
**Status:** Advanced from scale-only to architecture target
**Trigger:** Aggregate sustained traffic exceeds 500 RPS, or any tenant exceeds 200 RPS sustained
**Deliverable:** Each tenant has an independent ChainHead with periodic cross-chain anchoring (every N seconds, configurable). Spanner contention on the global sequence is eliminated as a hotspot.
**Verification:** Load test demonstrating 5,000 RPS aggregate with no Spanner aborts attributable to chain contention.

### M8: Post-quantum dual-signing (experimental)
**Status:** Planned
**Trigger:** Cloud KMS supports a NIST PQC finalist (likely ML-DSA / Dilithium) at production tier
**Deliverable:** Each recibo carries two signatures: the existing ECDSA P-256 and a parallel post-quantum signature. The verifier accepts either. Allows future cutover without breaking historical chain validation.
**Verification:** Verifier successfully validates a chain containing both signature types, in any mix.

### M9: Continuous compliance evidence
**Status:** Planned
**Trigger:** SOC 2 Type II audit window opens
**Deliverable:** Automated daily evidence collection (control attestations, access logs, policy snapshots) into the same append-only ledger structure with WORM controls used for inference recibos. Auditor verifies controls without interactive interviews.
**Verification:** SOC 2 Type II report referencing the automated evidence as primary source.

---

## Out of scope (explicitly)

To prevent feature creep dressed as architecture:

- **Custom model hosting.** REX Guard wraps third-party LLM providers. We are not in the business of running our own models.
- **Decision substrate.** The proxy enforces and records; it does not decide. See ADR-0001.
- **General-purpose API gateway.** REX Guard is purpose-built for compliance-bounded LLM inference. It is not a substitute for Apigee, Kong, or similar.
- **Public blockchain anchoring.** A BigQuery append-only ledger with WORM controls and cryptographic chaining is sufficient for the initial audit posture. Public chain anchoring adds operational complexity without proportional auditor benefit. Revisit only on explicit regulatory requirement.

---

## How to propose a new milestone

Open an issue with the `roadmap-proposal` label. Include:

1. The system property the milestone delivers.
2. The verification that proves it delivered.
3. The dependency on prior milestones, if any.
4. A clear distinction from items in the "out of scope" list.

Proposals that conflate "feature shipped" with "property verifiable" will be returned for revision.
