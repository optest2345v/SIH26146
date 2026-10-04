# SIH26146 — Network ↔ Blockchain Correlation Specification

## Purpose

Define how the project links network observations to blockchain observations without turning correlation into unsupported attribution.

## Evidence hierarchy

### Strong

- exact TXID match;
- explicit source linkage between observation and TXID;
- repeated corroborating observations.

### Moderate

- close temporal proximity;
- compatible transaction/network sequence;
- repeated network observations around the same transaction/entity;
- consistent IP/ASN relationships.

### Weak / contextual

- geography alone;
- shared IP alone;
- shared infrastructure alone;
- timestamp proximity without a direct transaction link.

## Core concepts

### Correlation confidence

How strongly the available observations support a specific relationship.

### Anomaly score

How unusual the observed behavior is under the chosen analytical model.

### Investigative priority

How strongly the available evidence suggests that human review should be prioritized.

These three values must not be conflated.

## Correlation record

Recommended structure:

```text
correlation_id
network_observation_id
transaction_id / txid
wallet/entity references
match_methods[]
matched_fields[]
time_delta
correlation_confidence
confidence_reason[]
source_record_ids[]
created_at
```

## Time correlation

Do not use a temporal match as sole proof of ownership. Record:

- time difference;
- timezone/normalization state;
- clock-skew assumptions if any;
- whether the match was exact or windowed.

## IP interpretation

An IP can represent shared, NATed, proxy, VPN, Tor, institutional, or other infrastructure. The model must treat IP evidence as contextual unless stronger direct linkage exists.

## Entity resolution

Possible project heuristics include:

- common-input relationships;
- repeated behavior;
- graph structure;
- repeated network observations;
- temporal consistency.

Every heuristic must be documented with limitations and should produce probabilistic/heuristic relationship language rather than definitive identity claims.

## Recommended output language

Prefer:

- `Observed association`
- `Correlation confidence`
- `Supporting evidence`
- `Probable/common entity`
- `Requires human review`

Avoid:

- `Confirmed owner`
- `Confirmed criminal`
- `IP belongs to suspect`

unless independently authoritative evidence is actually available to the system.

## Testing scenarios

At minimum test:

1. exact TXID match;
2. near-time but no TXID;
3. repeated observation;
4. shared IP across unrelated wallets;
5. missing timestamp;
6. malformed IP;
7. network clock skew;
8. contradictory observations;
9. no possible match;
10. ambiguous match with multiple candidates.
