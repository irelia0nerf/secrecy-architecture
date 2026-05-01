# ADR-0005 — Keep Firebase Out of the Hot Path

## Status

Accepted

## Context

Firebase Hosting is useful for static frontends, demos, portals and lightweight product surfaces.

However, the critical path of a regulated AI governance system requires explicit control over:

- edge routing;
- WAF and rate limiting;
- service identity;
- private ingress/egress options;
- zero-persistence enforcement;
- audit evidence generation;
- fail-closed behavior;
- network and IAM boundaries.

Using Firebase Hosting as part of the inference hot-path would blur the boundary between demo/UI delivery and production transaction control.

## Decision

Firebase Hosting must not be used in the critical inference hot-path.

Firebase may be used for:

- static demo UI;
- admin portal;
- documentation portal;
- customer-facing dashboard that calls governed APIs;
- non-critical frontend hosting.

Production inference traffic must flow through controlled infrastructure such as:

```text
HTTPS Load Balancer -> Cloud Armor -> Serverless NEG -> Cloud Run/GKE Runtime
```

## Consequences

### Positive

- Clear separation between UI and runtime governance.
- Better alignment with banking security review expectations.
- Enables Cloud Armor and controlled network boundaries.
- Avoids presenting demo infrastructure as production architecture.

### Negative

- More infrastructure to deploy.
- Requires Load Balancer, NEG and runtime routing configuration.
- Frontend and backend need separate deployment concerns.

## Allowed Pattern

```text
Firebase Hosting -> Static UI -> Calls governed API endpoint
```

## Forbidden Pattern

```text
Banking inference hot-path -> Firebase Hosting as critical proxy/control layer
```

## Validation

This ADR is valid only if:

- architecture diagrams keep Firebase outside the core hot-path;
- production runbooks do not depend on Firebase for inference execution;
- API calls terminate at the governed runtime endpoint;
- failure of Firebase does not block backend inference governance for direct API clients;
- documentation clearly labels Firebase as UI/demo/portal infrastructure.
