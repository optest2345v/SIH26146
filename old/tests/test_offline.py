"""
SIH26146 — Strict Offline Execution Acceptance Test
Fulfills REQ-013, NFR-001, AC-010, and docs/09-testing-validation.md.
Mocks the system network socket layer to disallow all outbound network connections,
then executes the full pipeline from end to end.
"""

import socket
import pytest
from src.pipeline import MasterPipeline


def disallow_network_connections(*args, **kwargs):
    raise RuntimeError("DISALLOWED_EXTERNAL_NETWORK_ATTEMPT: Pipeline must execute 100% offline!")


def test_strict_offline_execution(monkeypatch):
    """
    Simulates a strictly air-gapped environment with network connectivity severed.
    Proves zero cloud/remote API calls are made across ingestion, Geo-IP, correlation, graph, ML, and alert generation.
    """
    # Monkeypatch socket.socket.connect to block any network call
    monkeypatch.setattr(socket.socket, "connect", disallow_network_connections)

    pipeline = MasterPipeline()
    result, graph, features, recs, corrs = pipeline.run("data/synthetic/transactions_sample.csv")

    assert result is not None
    assert result.validation_summary.total_records > 0
    assert result.total_correlations > 0
    assert graph.number_of_nodes() > 0
    assert len(features) > 0
    assert len(result.alerts) > 0
