# SIH26146 — Security & Privacy

## Core principles

This application handles potentially sensitive investigative data and should therefore be local-first.

## Requirements

- no hidden telemetry;
- no required data upload;
- no hard-coded secrets;
- no unnecessary sensitive logging;
- validate input;
- use least-privilege file access where applicable;
- pin/package dependencies where practical;
- keep ML and data processing local for the offline prototype.

## Attribution safety

Never equate:

- IP with person;
- wallet/address with person;
- anomaly with guilt;
- model score with proof;
- graph cluster with criminal organization.

## Geo-IP safety

Geo-IP is approximate/contextual. Preserve the distinction between location enrichment and identity attribution.

## External services

Any runtime external dependency is a potential violation of the offline design. If a dependency requires internet access to function, it cannot be part of the critical runtime path.

## Data handling

Where possible, use:

- local files/databases;
- access controls;
- explicit provenance;
- secure cleanup of temporary sensitive material;
- documented data-retention behavior.
