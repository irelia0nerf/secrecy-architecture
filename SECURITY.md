# Security Policy

## Reporting a vulnerability

If you discover a security issue in this reference architecture or in the
example code, please report it privately first.

**Email:** security@foundlab.cloud
**PGP key:** TBD (will be published before this repository's first tagged release)

What to include:

- A description of the issue.
- Steps to reproduce, if applicable to the example code.
- Whether the issue concerns the reference architecture (a design flaw) or
  the example tooling (an implementation flaw). Both are in scope.

We will acknowledge receipt within 5 business days. We will work with you on
disclosure timing; the default is 90 days from acknowledgment unless the
issue is being actively exploited, in which case we coordinate immediately.

## Out of scope

This repository is reference material. The following are **not** in scope
for security disclosure here:

- Vulnerabilities in FoundLab's production deployment of REX Guard. Those
  are reported through FoundLab's separate security disclosure channel,
  which will be linked here once published.
- Vulnerabilities in third-party services referenced in the architecture
  (Google Cloud KMS, Vertex AI, Cloud Spanner, etc.). Report those to the
  respective vendors.
- General complaints about cryptographic choices that are documented in an
  ADR with a stated rationale. Open a discussion issue instead.
