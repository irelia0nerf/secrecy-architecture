# secrecy-architecture

> *"A system has perfect secrecy if the ciphertext gives no information about the plaintext."*
> — Claude E. Shannon, *Communication Theory of Secrecy Systems* (1949)

**Maintained by [FoundLab](https://foundlab.com.br)** — Auditable Trust Infrastructure for AI in regulated finance.

---

## Mission

FoundLab builds verifiable trust infrastructure for AI-mediated decisions in regulated environments. This repository is the **public reference architecture** for our compliance proxy pattern: how to intercept LLM inference calls, enforce regulatory invariants, and produce cryptographic evidence that survives forensic audit.

The architecture is grounded in a single principle: **trust by physics, not by policy**. If the guarantee depends on an NDA or an HR document, it isn't a guarantee. It becomes mathematics or it dies.

---

## What this repository is

- **Reference architecture** — markdown, mermaid diagrams, architectural decision records (ADRs).
- **Honest design notes** — including limitations, residual risks, and explicit "this is not what we do" sections.
- **Verifier examples** — small Python scripts an external auditor can adapt to validate evidence chains independently.
- **Public reviews archive** — feedback from external models and humans, labeled with their epistemic status (projection vs. measurement).

## What this repository is **not**

- **Not the production codebase.** The production implementation lives in private repositories. In any conflict between this reference and shipped code, the code wins.
- **Not a turnkey SDK.** Examples are pedagogical. They will not protect a real banking workload as-is.
- **Not a regulatory mapping document.** References to BCB, LGPD, CMN, and DORA are illustrative. Production deployments require formal legal review, which this repository does not substitute.
- **Not a marketing artifact.** No claims about real clients, contracts, or pilot results appear here unless explicitly published as a case study with the counterparty's consent.

---

## Repository structure

```
.
├── README.md                       This file
├── arquitetura.md                  Main reference architecture (v1.1)
├── ROADMAP.md                      Milestones tied to real implementation
├── ARCHITECTURE_REVIEW.md          2026-04 hardening review and remediation backlog
├── LICENSE-CODE                    Apache 2.0 (code in examples/)
├── LICENSE-DOCS                    CC BY 4.0 (markdown documentation)
├── decisions/                      Architectural Decision Records
│   ├── 0001-rex-is-proxy-not-model.md
│   ├── 0002-ecdsa-p256-over-ed25519.md
│   ├── 0003-crypto-shredding-semantics.md
│   └── 0004-ledger-immutability.md
├── diagrams/                       Mermaid sources, extracted for reuse
│   ├── e2e-flow.mmd
│   ├── 8-gates-pipeline.mmd
│   └── chainhead-spanner.mmd
├── examples/
│   └── verify_chain.py             Standalone Merkle-chain verifier (sample data)
└── reviews/                        Archived external feedback
    ├── README.md                   How to read the labels
    └── 2026-04-grok-relatorio.md   Labeled: PROJECTION (not measurement)
```

---

## Reading order

If you are new and want to understand the system: start with [`arquitetura.md`](./arquitetura.md), then read the ADRs in `decisions/` in numeric order, then look at `examples/verify_chain.py` to see how the evidence chain is supposed to be verified.

If you are an auditor: jump to `arquitetura.md` §9 ("How to prove this works — non-theatre") and `examples/verify_chain.py`.

If you are evaluating FoundLab as a vendor: read this README, then `arquitetura.md` §0 (non-negotiable principles) and §8 (what this architecture does not do). Those two sections are the honest perimeter.

---

## Versioning policy

- **Reference architecture** is versioned semantically (`v1.0`, `v1.1`, ...). Breaking changes to invariants bump the major.
- **ADRs are append-only.** Decisions are superseded, never deleted. An ADR marked `Superseded by ADR-NNNN` remains in the repository as historical record.
- **Reviews are immutable** once added. If a review's premises become outdated, a new review is added with a forward reference; the original stays intact.

---

## Contributing

This repository is currently maintained by FoundLab's engineering core. External contributions are welcome via issue first — open a discussion before submitting a PR. We will close PRs that:

- Add unverifiable performance claims.
- Replace "limitation" sections with marketing language.
- Cite regulatory articles without source links.

We will engage seriously with PRs that:

- Find a flaw in the threat model and explain it with a concrete attack.
- Improve the precision of an ADR.
- Contribute auditor-side tooling that is provably independent of FoundLab.

---

## License

- **Documentation** (`*.md` files): [Creative Commons Attribution 4.0 International (CC BY 4.0)](./LICENSE-DOCS)
- **Code** (`examples/*.py` and any future code): [Apache License 2.0](./LICENSE-CODE)

In plain language: cite us when you reuse the docs, and use the code under standard Apache terms. The dual-license is intentional — documentation benefits from attribution culture, code benefits from broader compatibility.

---

## Contact

- Engineering: open an issue.
- Commercial: [foundlab.com.br](https://foundlab.com.br)
- Security disclosures: see `SECURITY.md` (forthcoming).

---

*Shannon's perfect secrecy is an asymptote. Real systems approach it through layered enforcement: cryptography that does not lie, hardware that does not leak, and audit trails that do not forgive. This repository documents that approach.*
