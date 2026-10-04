"""
Tests for the Interactive Terminal Forensic Console (TUI / Headless CLI).
Verifies that all console commands execute without exceptions in headless mode.
"""

import pytest
from src.cli.terminal_ui import ForensicConsole


@pytest.fixture
def console():
    return ForensicConsole(data_path="data/synthetic/transactions_sample.csv")


def test_terminal_console_banner_and_summary(console, capsys):
    console.onecmd("summary")
    captured = capsys.readouterr().out
    assert "SIH26146" in captured
    assert "COGNOVAX" in captured
    assert "Active Dataset" in captured


def test_terminal_console_alerts_filter(console, capsys):
    console.onecmd("alerts CRITICAL")
    captured = capsys.readouterr().out
    assert "Alert ID" in captured
    assert "Tier" in captured


def test_terminal_console_inspect(console, capsys):
    console.onecmd("inspect 1")
    captured = capsys.readouterr().out
    assert "FORENSIC THREAT ASSESSMENT" in captured
    assert "Priority Meter" in captured
    assert "ML Anomaly" in captured


def test_terminal_console_graph(console, capsys):
    console.onecmd("graph 1")
    captured = capsys.readouterr().out
    assert "ASCII FORENSIC TOPOLOGY GRAPH" in captured
    assert "FOCUS ENTITY" in captured


def test_terminal_console_taint(console, capsys):
    console.onecmd("taint 1")
    captured = capsys.readouterr().out
    assert "MULTI-HOP FUND TAINT PROPAGATION" in captured
    assert "Root Origin" in captured


def test_terminal_console_syndicates(console, capsys):
    console.onecmd("syndicates")
    captured = capsys.readouterr().out
    assert "AUTONOMOUS LAUNDERING SYNDICATES" in captured


def test_terminal_console_tag_and_notes(console, capsys):
    console.onecmd('tag 1 SEIZURE "Air-gapped terminal seizure test note"')
    captured = capsys.readouterr().out
    assert "Human disposition recorded successfully" in captured

    console.onecmd("notes")
    captured_notes = capsys.readouterr().out
    assert "HUMAN INVESTIGATOR DISPOSITION LOG" in captured_notes
    assert "FLAG_FOR_SEIZURE" in captured_notes


def test_terminal_console_scenario_switch(console, capsys):
    console.onecmd("scenario peeling_chain")
    captured = capsys.readouterr().out
    assert "scenario_peeling_chain.csv" in captured
    assert len(console.alerts_indexed) > 0
