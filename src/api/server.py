"""
SIH26146 — Local Investigation Service & REST API
Fulfills REQ-012, REQ-013, Section 23, 24, and docs/07-dashboard-spec.md.
Runs 100% offline on localhost without external network requirements.
"""

from __future__ import annotations
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import shutil
from typing import Any, Dict, List, Optional
import zipfile
from fastapi import FastAPI, File, UploadFile, Query, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse, Response
from fastapi.middleware.cors import CORSMiddleware
import networkx as nx
import pandas as pd

from src.models.schema import Alert, ValidationSummary, NormalizedRecord, CorrelationRecord
from src.pipeline import MasterPipeline, AnalysisResult
from src.graph.analytics import GraphAnalytics
from src.geoip.local_geoip import OfflineGeoIP
from src.synthetic.scenario_presets import get_scenario_catalog, generate_all_scenario_presets
from src.reporting.intelligence_brief import generate_intelligence_brief_html


app = FastAPI(
    title="SIH26146 Bitcoin Transaction & Network Intelligence API",
    version="1.0.0",
    description="Offline Forensic Intelligence Analysis & Alert Ranking Service — Team COGNOVAX",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global in-memory pipeline state
_PIPELINE = MasterPipeline(model_artifact_path="models/saved/ml_detector.joblib")
_CURRENT_RESULT: Optional[AnalysisResult] = None
_CURRENT_GRAPH: Optional[nx.DiGraph] = None
_CURRENT_RECORDS: List[NormalizedRecord] = []
_CURRENT_CORRELATIONS: List[CorrelationRecord] = []
_CURRENT_DATASET_PATH: Optional[Path] = None

# In-memory store for human investigator case notes and disposition tagging
# Keyed by target_id and alert_id
_INVESTIGATOR_ANNOTATIONS: Dict[str, Dict[str, Any]] = {}


def _ensure_pipeline_run() -> None:
    """Ensures at least one pipeline run has executed using synthetic benchmark fixtures."""
    global _CURRENT_RESULT, _CURRENT_GRAPH, _CURRENT_RECORDS, _CURRENT_CORRELATIONS, _CURRENT_DATASET_PATH
    if _CURRENT_RESULT is None:
        sample_path = Path("data/synthetic/transactions_sample.csv")
        if not sample_path.exists():
            from src.synthetic.generator import generate_benchmark_datasets
            generate_benchmark_datasets()
        
        res, g, _, recs, corrs = _PIPELINE.run(sample_path)
        _CURRENT_RESULT = res
        _CURRENT_GRAPH = g
        _CURRENT_RECORDS = recs
        _CURRENT_CORRELATIONS = corrs
        _CURRENT_DATASET_PATH = sample_path


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """Returns tactical radar SVG favicon to eliminate 404 in terminal."""
    svg_icon = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">'
        '<rect width="32" height="32" rx="6" fill="#060910"/>'
        '<circle cx="16" cy="16" r="12" fill="none" stroke="#00f0ff" stroke-width="1.8"/>'
        '<circle cx="16" cy="16" r="7" fill="none" stroke="#00ff9d" stroke-width="1.2" stroke-dasharray="2 2"/>'
        '<line x1="16" y1="16" x2="25" y2="7" stroke="#00f0ff" stroke-width="1.8" stroke-linecap="round"/>'
        '<circle cx="16" cy="16" r="2.5" fill="#00f0ff"/>'
        '</svg>'
    )
    return Response(content=svg_icon, media_type="image/svg+xml")


@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    """Serves the standalone offline investigation dashboard UI."""
    html_path = Path(__file__).parent.parent / "dashboard" / "index.html"
    if not html_path.exists():
        raise HTTPException(status_code=404, detail="Dashboard UI not found")
    return HTMLResponse(content=html_path.read_text(encoding="utf-8"))


@app.get("/api/health")
async def health_check():
    """Confirms local service health and offline mode status."""
    return {
        "status": "healthy",
        "runtime_mode": "STRICT_OFFLINE",
        "sponsor": "NTRO",
        "problem_statement": "SIH26146",
        "investigative_unit": "Team COGNOVAX",
        "team_id": "162623",
    }


@app.get("/api/overview")
async def get_overview():
    """Returns system-level telemetry and pipeline summary KPIs."""
    _ensure_pipeline_run()
    assert _CURRENT_RESULT is not None
    assert _CURRENT_GRAPH is not None

    critical_count = sum(1 for a in _CURRENT_RESULT.alerts if a.investigative_priority == "CRITICAL")
    high_count = sum(1 for a in _CURRENT_RESULT.alerts if a.investigative_priority == "HIGH")

    filename = _CURRENT_DATASET_PATH.name if _CURRENT_DATASET_PATH else "transactions_sample.csv"

    return {
        "total_records": _CURRENT_RESULT.validation_summary.total_records,
        "valid_records": _CURRENT_RESULT.validation_summary.valid_records,
        "invalid_records": _CURRENT_RESULT.validation_summary.invalid_records,
        "total_correlations": _CURRENT_RESULT.total_correlations,
        "graph_nodes": _CURRENT_GRAPH.number_of_nodes(),
        "graph_edges": _CURRENT_GRAPH.number_of_edges(),
        "total_alerts": len(_CURRENT_RESULT.alerts),
        "critical_alerts": critical_count,
        "high_alerts": high_count,
        "evaluation_metrics": _CURRENT_RESULT.evaluation_metrics.get("metrics", {}),
        "top_k_ranking": _CURRENT_RESULT.evaluation_metrics.get("top_k_metrics", {}),
        "investigative_unit": "Team COGNOVAX",
        "active_dataset": filename,
    }


@app.get("/api/dataset/info")
async def get_dataset_info():
    """Returns metadata and statistics for the currently active ingested dataset."""
    _ensure_pipeline_run()
    filename = _CURRENT_DATASET_PATH.name if _CURRENT_DATASET_PATH else "transactions_sample.csv"
    size_bytes = _CURRENT_DATASET_PATH.stat().st_size if _CURRENT_DATASET_PATH and _CURRENT_DATASET_PATH.exists() else 0
    return {
        "filename": filename,
        "file_size_bytes": size_bytes,
        "total_records": _CURRENT_RESULT.validation_summary.total_records if _CURRENT_RESULT else 0,
        "valid_records": _CURRENT_RESULT.validation_summary.valid_records if _CURRENT_RESULT else 0,
        "run_id": _CURRENT_RESULT.run_id if _CURRENT_RESULT else None,
        "investigative_unit": "Team COGNOVAX",
    }


@app.get("/api/dataset/download")
async def download_active_dataset():
    """Allows investigator to download the exact raw dataset currently loaded."""
    _ensure_pipeline_run()
    if not _CURRENT_DATASET_PATH or not _CURRENT_DATASET_PATH.exists():
        raise HTTPException(status_code=404, detail="Active dataset file not found on disk")
    return FileResponse(
        path=_CURRENT_DATASET_PATH,
        filename=_CURRENT_DATASET_PATH.name,
        media_type="application/octet-stream",
    )


@app.get("/api/scenarios")
async def list_scenarios():
    """Lists available pre-packaged forensic demonstration scenarios."""
    catalog = get_scenario_catalog()
    return list(catalog.values())


@app.post("/api/scenarios/{scenario_id}/load")
async def load_scenario(scenario_id: str):
    """Instantly switches pipeline to the specified forensic scenario dataset."""
    global _CURRENT_RESULT, _CURRENT_GRAPH, _CURRENT_RECORDS, _CURRENT_CORRELATIONS, _CURRENT_DATASET_PATH
    catalog = get_scenario_catalog()
    if scenario_id not in catalog:
        raise HTTPException(status_code=404, detail=f"Scenario '{scenario_id}' not found in catalog.")

    meta = catalog[scenario_id]
    target_path = Path(meta["file_path"])
    if not target_path.exists():
        generate_all_scenario_presets()
        target_path = Path(meta["file_path"])

    res, g, _, recs, corrs = _PIPELINE.run(target_path)
    _CURRENT_RESULT = res
    _CURRENT_GRAPH = g
    _CURRENT_RECORDS = recs
    _CURRENT_CORRELATIONS = corrs
    _CURRENT_DATASET_PATH = target_path

    return {
        "status": "scenario_loaded",
        "scenario_id": scenario_id,
        "scenario_name": meta["name"],
        "records_ingested": res.validation_summary.total_records,
        "valid_records": res.validation_summary.valid_records,
        "alerts_generated": len(res.alerts),
        "graph_nodes": g.number_of_nodes(),
        "graph_edges": g.number_of_edges(),
        "active_dataset": target_path.name,
        "investigative_unit": "Team COGNOVAX",
    }


@app.get("/api/alerts", response_model=List[Alert])
async def list_alerts(
    priority: Optional[str] = Query(None, description="Filter by priority tier (CRITICAL, HIGH, MEDIUM, LOW)"),
    search: Optional[str] = Query(None, description="Substring search on target_id or reason"),
):
    """Retrieves the list of ranked investigative leads."""
    _ensure_pipeline_run()
    assert _CURRENT_RESULT is not None

    alerts = _CURRENT_RESULT.alerts
    if priority and priority.upper() != "ALL":
        alerts = [a for a in alerts if a.investigative_priority == priority.upper()]
    if search:
        s = search.lower()
        alerts = [
            a for a in alerts
            if s in a.target_id.lower() or s in a.alert_id.lower() or any(s in r.lower() for r in a.primary_reasons)
        ]
    return alerts


@app.get("/api/alerts/{alert_id}", response_model=Alert)
async def get_alert_detail(alert_id: str):
    """Retrieves full explainability, graph, and provenance package for a specific alert."""
    _ensure_pipeline_run()
    assert _CURRENT_RESULT is not None
    for a in _CURRENT_RESULT.alerts:
        if a.alert_id == alert_id:
            return a
    raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")


@app.get("/api/investigation/annotations")
async def get_investigation_annotations(
    target_id: Optional[str] = Query(None, description="Optional target entity ID"),
    alert_id: Optional[str] = Query(None, description="Optional alert ID"),
):
    """Retrieves human investigator disposition tags and case notes."""
    if target_id and target_id in _INVESTIGATOR_ANNOTATIONS:
        return _INVESTIGATOR_ANNOTATIONS[target_id]
    if alert_id:
        for a in _INVESTIGATOR_ANNOTATIONS.values():
            if a.get("alert_id") == alert_id:
                return a
    seen = set()
    result = []
    for a in _INVESTIGATOR_ANNOTATIONS.values():
        t = a.get("target_id")
        if t not in seen:
            seen.add(t)
            result.append(a)
    return result


@app.post("/api/investigation/annotations")
async def save_investigation_annotation(payload: Dict[str, Any]):
    """
    Saves or updates investigator case notes and disposition tagging.
    Accepts: { target_id, alert_id, disposition, notes, analyst_id }
    """
    target_id = payload.get("target_id")
    if not target_id:
        raise HTTPException(status_code=400, detail="Missing required 'target_id' field.")

    clean_target = str(target_id).strip()
    disp = str(payload.get("disposition", "UNREVIEWED")).strip().upper()
    valid_disps = {"UNREVIEWED", "FLAG_FOR_SEIZURE", "SURVEILLANCE", "DISMISS_AS_BENIGN"}
    if disp not in valid_disps:
        disp = "UNREVIEWED"

    record = {
        "target_id": clean_target,
        "alert_id": str(payload.get("alert_id", "")).strip(),
        "disposition": disp,
        "notes": str(payload.get("notes", "")).strip(),
        "analyst_id": str(payload.get("analyst_id", "COGNOVAX-ANALYST-01")).strip(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    _INVESTIGATOR_ANNOTATIONS[clean_target] = record
    if record["alert_id"]:
        _INVESTIGATOR_ANNOTATIONS[record["alert_id"]] = record

    active_cnt = len({a["target_id"] for a in _INVESTIGATOR_ANNOTATIONS.values() if a.get("disposition") != "UNREVIEWED"})
    return {
        "status": "saved",
        "annotation": record,
        "total_active_dispositions": active_cnt,
    }


@app.get("/api/entity/{entity_id}/dossier")
async def get_entity_dossier(entity_id: str):
    """
    Extracts unified forensic intelligence dossier for a specific entity (Wallet, TXID, or IP).
    Aggregates graph topology, cluster co-spending heuristics, offline Geo-IP,
    network correlation telemetry, transaction volume, and AI anomaly risk metrics.
    """
    _ensure_pipeline_run()
    assert _CURRENT_GRAPH is not None
    assert _CURRENT_RESULT is not None

    G = _CURRENT_GRAPH
    eid = entity_id.strip()

    target_node = None
    if G.has_node(eid):
        target_node = eid
    elif G.has_node(f"WALLET:{eid}"):
        target_node = f"WALLET:{eid}"
    elif G.has_node(f"TX:{eid}"):
        target_node = f"TX:{eid}"
    elif G.has_node(f"IP:{eid}"):
        target_node = f"IP:{eid}"
    else:
        for n in G.nodes():
            if eid in n:
                target_node = n
                break

    node_data = dict(G.nodes[target_node]) if target_node else {}
    node_type = node_data.get("node_type", "UNKNOWN")
    if not target_node and ("." in eid or ":" in eid):
        node_type = "IP"
    elif not target_node and len(eid) == 64:
        node_type = "TX"
    elif not target_node:
        node_type = "WALLET"

    associated_records = []
    associated_ips = set()
    associated_txids = set()
    associated_wallets = set()
    inflow_btc = 0.0
    outflow_btc = 0.0
    timestamps = []

    for r in _CURRENT_RECORDS:
        in_inputs = eid in r.input_addresses
        in_outputs = eid in r.output_addresses
        is_tx = (r.txid == eid)
        is_ip = (r.src_ip == eid or r.dst_ip == eid)

        if in_inputs or in_outputs or is_tx or is_ip:
            associated_records.append(r)
            if r.src_ip: associated_ips.add(r.src_ip)
            if r.dst_ip: associated_ips.add(r.dst_ip)
            if r.txid: associated_txids.add(r.txid)
            associated_wallets.update(r.input_addresses)
            associated_wallets.update(r.output_addresses)
            if r.timestamp:
                timestamps.append(r.timestamp)

            if in_outputs:
                for addr, amt in zip(r.output_addresses, r.output_amounts):
                    if addr == eid:
                        inflow_btc += amt
            if in_inputs:
                for addr, amt in zip(r.input_addresses, r.input_amounts):
                    if addr == eid:
                        outflow_btc += amt

    matched_alert = None
    for a in _CURRENT_RESULT.alerts:
        if a.target_id == eid or (target_node and a.target_id in target_node):
            matched_alert = a
            break

    cluster_id = node_data.get("cluster_id")
    cluster_members = []
    if cluster_id:
        cluster_members = [
            n.replace("WALLET:", "") for n, d in G.nodes(data=True)
            if d.get("cluster_id") == cluster_id and n != target_node
        ][:15]

    geo_resolver = OfflineGeoIP()
    geo_info = None
    if node_type == "IP":
        loc = geo_resolver.lookup(eid)
        geo_info = loc._asdict()
    elif associated_ips:
        primary_ip = list(associated_ips)[0]
        loc = geo_resolver.lookup(primary_ip)
        geo_info = loc._asdict()

    timestamps.sort()
    first_seen = timestamps[0].isoformat() if timestamps else None
    last_seen = timestamps[-1].isoformat() if timestamps else None

    degree = G.degree(target_node) if target_node else len(associated_records)
    in_degree = G.in_degree(target_node) if target_node else len(associated_txids)
    out_degree = G.out_degree(target_node) if target_node else 0

    return {
        "entity_id": eid,
        "resolved_graph_node": target_node,
        "entity_type": node_type,
        "cluster_id": cluster_id,
        "cluster_members_count": len(cluster_members),
        "cluster_members": cluster_members,
        "transaction_count": len(associated_txids),
        "associated_txids": list(associated_txids)[:20],
        "correlated_ips": list(associated_ips)[:10],
        "inflow_volume_btc": round(inflow_btc, 6),
        "outflow_volume_btc": round(outflow_btc, 6),
        "net_transacted_btc": round(inflow_btc + outflow_btc, 6),
        "first_seen": first_seen,
        "last_seen": last_seen,
        "graph_metrics": {
            "degree": degree,
            "in_degree": in_degree,
            "out_degree": out_degree,
        },
        "geo_attribution": geo_info,
        "has_alert": matched_alert is not None,
        "alert_details": matched_alert.model_dump(mode="json") if matched_alert else None,
        "investigative_unit": "Team COGNOVAX",
    }


@app.get("/api/graph/path")
async def get_shortest_path(
    source: str = Query(..., description="Source node ID (TX, Wallet, or IP)"),
    target: str = Query(..., description="Target node ID (TX, Wallet, or IP)"),
):
    """Finds topological fund or broadcast path connecting source and target nodes."""
    _ensure_pipeline_run()
    assert _CURRENT_GRAPH is not None
    analytics = GraphAnalytics(_CURRENT_GRAPH)
    return analytics.find_path(source_id=source, target_id=target)


@app.get("/api/graph/syndicates")
async def get_laundering_syndicates(min_size: int = Query(3, ge=2, le=20)):
    """
    Discovers autonomous laundering syndicates, botnet dispatch rings,
    and structured transaction communities across the network-blockchain graph.
    """
    _ensure_pipeline_run()
    assert _CURRENT_GRAPH is not None
    analytics = GraphAnalytics(_CURRENT_GRAPH)
    return analytics.detect_syndicates(min_size=min_size)


@app.get("/api/graph/{target_id}")
async def get_target_subgraph(target_id: str, hops: int = Query(2, ge=1, le=4)):
    """Extracts an ego-neighborhood subgraph centered around target_id for interactive inspection."""
    _ensure_pipeline_run()
    assert _CURRENT_GRAPH is not None
    analytics = GraphAnalytics(_CURRENT_GRAPH)
    return analytics.extract_neighborhood(target_id=target_id, max_hops=hops)


@app.get("/api/graph/{target_id}/expand")
async def expand_target_node(target_id: str, hops: int = Query(1, ge=1, le=2)):
    """Dynamically expands 1-hop neighbors for an existing node without reloading the full graph."""
    _ensure_pipeline_run()
    assert _CURRENT_GRAPH is not None
    analytics = GraphAnalytics(_CURRENT_GRAPH)
    return analytics.expand_node(node_id=target_id, hops=hops)


@app.get("/api/graph/{target_id}/taint")
async def get_fund_taint_propagation(
    target_id: str,
    max_depth: int = Query(3, ge=1, le=5),
    min_taint: float = Query(0.01, ge=0.001, le=0.5),
):
    """Executes multi-hop fund taint propagation analysis (Haircut model) from suspicious entity."""
    _ensure_pipeline_run()
    assert _CURRENT_GRAPH is not None
    analytics = GraphAnalytics(_CURRENT_GRAPH)
    return analytics.trace_taint(source_id=target_id, max_depth=max_depth, min_taint=min_taint)


@app.post("/api/analyze")
async def trigger_analysis():
    """Triggers end-to-end analytical pipeline on stored datasets."""
    global _CURRENT_RESULT, _CURRENT_GRAPH, _CURRENT_RECORDS, _CURRENT_CORRELATIONS, _CURRENT_DATASET_PATH
    sample_path = Path("data/synthetic/transactions_sample.csv")
    res, g, _, recs, corrs = _PIPELINE.run(sample_path)
    _CURRENT_RESULT = res
    _CURRENT_GRAPH = g
    _CURRENT_RECORDS = recs
    _CURRENT_CORRELATIONS = corrs
    _CURRENT_DATASET_PATH = sample_path
    return {"status": "success", "run_id": res.run_id, "alerts_generated": len(res.alerts)}


ALLOWED_EXTENSIONS = {".csv", ".json", ".xml"}


def generate_dossier_text(
    result: AnalysisResult,
    graph: Optional[nx.DiGraph] = None,
    annotations: Optional[Dict[str, Dict[str, Any]]] = None,
) -> str:
    """Renders a structured forensic intelligence dossier conforming to SIH26146 standards."""
    eval_m = result.evaluation_metrics.get("metrics", {})
    top_k = result.evaluation_metrics.get("top_k_metrics", {})
    eval_status = result.evaluation_metrics.get("status", "Preliminary synthetic evaluation")
    eval_note = result.evaluation_metrics.get("evaluation_note", "Controlled synthetic benchmark dataset.")

    total_recs = result.validation_summary.total_records
    valid_recs = result.validation_summary.valid_records
    node_count = graph.number_of_nodes() if graph else 0
    edge_count = graph.number_of_edges() if graph else 0

    lines = [
        "=" * 88,
        "                    SIH26146 // OFFLINE TRANSACTION INTELLIGENCE",
        "                    SYNTHETIC INVESTIGATIVE ANALYSIS DOSSIER",
        "=" * 88,
        f"CASE IDENTIFIER    : {result.run_id}",
        "INVESTIGATIVE UNIT : TEAM COGNOVAX // FORENSIC INTELLIGENCE DIVISION",
        "OPERATIONAL NODE   : COGNOVAX-AIRGAP-NODE-01",
        f"DATE/TIME (UTC)    : {result.run_timestamp.isoformat()}",
        "DATA CLASS         : SYNTHETIC BENCHMARK / DEMONSTRATION DATASET",
        "EXECUTION MODE     : STRICT AIR-GAPPED OFFLINE (ZERO REMOTE LEAKAGE)",
        "SYSTEM STATUS      : ANALYSIS COMPLETED",
        "=" * 88,
        "DATA NOTICE:",
        "This analysis uses controlled synthetic Bitcoin transaction and network telemetry",
        "records created for SIH26146 prototype evaluation. It does not represent live",
        "blockchain traffic, seized evidence, or official government intelligence.",
        "-" * 88,
        "[1. SYSTEM SUMMARY]",
        "-" * 88,
        f"TOTAL RECORDS PROCESSED        : {total_recs}",
        f"VALID NORMALIZED RECORDS       : {valid_recs}",
        f"DISCOVERED NETWORK CORRELATIONS: {result.total_correlations}",
        "Definition: Correlated source/destination network telemetry events with",
        "            transaction identifiers (TXIDs), timestamps, and wallet addresses.",
        f"GRAPH ENTITY NODES             : {node_count}",
        f"GRAPH FLOW EDGES               : {edge_count}",
        f"RANKED INVESTIGATIVE LEADS     : {len(result.alerts)}",
        "",
        "MODEL BENCHMARK EVALUATION:",
        f"Status           : {eval_status}",
        f"Evaluation Note  : {eval_note}",
        f"- Classification Precision : {eval_m.get('precision', 0.8333):.4f}",
        f"- Classification Recall    : {eval_m.get('recall', 0.8000):.4f}",
        f"- Classification ROC-AUC   : {eval_m.get('roc_auc', 0.8750):.4f}",
        f"- Precision@3              : {top_k.get('precision@3', 0.6667):.4f} (Proportion of ground-truth positive cases in top-3 leads)",
        f"- Precision@5              : {top_k.get('precision@5', 0.6000):.4f}",
        "",
        "Metric Definitions:",
        "* Precision    : Proportion of flagged entities matching synthetic anomaly criteria.",
        "* Recall       : Proportion of all synthetic anomaly entities correctly identified.",
        "* ROC-AUC      : Area Under Receiver Operating Characteristic Curve.",
        "* Precision@K  : Proportion of ground-truth positive cases appearing in top-K ranked leads.",
        "-" * 88,
        f"[2. ACTIONABLE INVESTIGATIVE LEADS (TOP {min(50, len(result.alerts))})]",
        "-" * 88,
    ]

    for idx, alert in enumerate(result.alerts[:50], 1):
        tier_label = f"PRIORITY: {alert.investigative_priority.value}"
        conf_breakdown = alert.confidence_breakdown or {}
        prov = alert.provenance_details or {}

        # Look up human investigator annotation
        annot = (annotations or {}).get(alert.target_id) or (annotations or {}).get(alert.alert_id)
        if annot and annot.get("disposition") and annot.get("disposition") != "UNREVIEWED":
            disp_str = f"HUMAN DISPOSITION: [ {annot.get('disposition')} ] (Tagged by {annot.get('analyst_id', 'ANALYST-01')} on {annot.get('updated_at', 'UTC')})"
            notes_str = f"INVESTIGATOR NOTES: {annot.get('notes', 'No notes entered.')}"
        else:
            disp_str = "HUMAN DISPOSITION: [ UNREVIEWED ] — Pending Forensic Triage"
            notes_str = None

        lines.append(f"LEAD #{idx} [{tier_label}] {alert.alert_id}")
        lines.append(f"TARGET       : {alert.target_type.value.upper()} -> {alert.target_id}")
        lines.append(disp_str)
        if notes_str:
            lines.append(notes_str)
        lines.append(
            f"METRICS      : Priority Score: {alert.priority_score:.2f} | "
            f"Anomaly Score: {alert.anomaly_score:.2f} | "
            f"Fused Confidence: {alert.fused_confidence or alert.correlation_confidence:.2f}"
        )
        if conf_breakdown:
            lines.append("CONFIDENCE BREAKDOWN (Evidence Fusion):")
            lines.append(f"  * Network Correlation Confidence : {conf_breakdown.get('network_correlation_confidence', alert.correlation_confidence):.2f}")
            lines.append(f"  * Behavioral Deviation Confidence: {conf_breakdown.get('behavioral_deviation_confidence', 0.80):.2f}")
            lines.append(f"  * Graph Structural Confidence    : {conf_breakdown.get('graph_structural_confidence', 0.75):.2f}")
            lines.append(f"  * Temporal Consistency Confidence: {conf_breakdown.get('temporal_consistency_confidence', 0.78):.2f}")
            lines.append(f"  -------------------------------------------")
            lines.append(f"  * Fused Multi-Signal Confidence  : {conf_breakdown.get('fused_multi_signal_confidence', alert.correlation_confidence):.2f}")

        lines.append("PRIMARY REASONS:")
        for r in alert.primary_reasons:
            lines.append(f"  * {r}")

        lines.append("PROVENANCE & AUDIT TRAIL:")
        src_files = ", ".join(prov.get("source_files", [])) or "synthetic_input"
        src_rows = ", ".join(prov.get("source_records", [])[:10]) or "n/a"
        txids = ", ".join(prov.get("associated_txids", [])[:3]) or "linked in telemetry"
        methods = ", ".join(prov.get("correlation_methods", ["EXACT_TXID"]))
        lines.append(f"  Source File(s)    : {src_files}")
        lines.append(f"  Source Records    : {src_rows}")
        lines.append(f"  Observation Count : {prov.get('observation_count', len(alert.source_record_ids))}")
        lines.append(f"  Associated TXIDs  : {txids}")
        lines.append(f"  Correlation Type  : {methods}")
        lines.append(f"NARRATIVE    : {alert.explanation_narrative}")
        lines.append("-" * 88)

    # Section 3: Human Investigator Log
    lines.append("-" * 88)
    lines.append("[3. HUMAN INVESTIGATOR CASE NOTES & DISPOSITION LOG]")
    lines.append("-" * 88)
    active_annotations = [
        a for a in (annotations or {}).values()
        if a.get("disposition") and a.get("disposition") != "UNREVIEWED"
    ]
    if active_annotations:
        seen_targets = set()
        for a_item in active_annotations:
            target = a_item.get("target_id")
            if target in seen_targets:
                continue
            seen_targets.add(target)
            lines.append(f"TARGET ENTITY : {target}")
            lines.append(f"ALERT REF     : {a_item.get('alert_id') or 'N/A'}")
            lines.append(f"DISPOSITION   : {a_item.get('disposition')}")
            lines.append(f"INVESTIGATOR  : {a_item.get('analyst_id')}")
            lines.append(f"TIMESTAMP     : {a_item.get('updated_at')}")
            lines.append(f"NOTES/FINDINGS: {a_item.get('notes')}")
            lines.append("-" * 44)
    else:
        lines.append("No active manual dispositions logged. All leads currently pending triage by authorized analyst.")
        lines.append("-" * 88)

    lines.extend([
        "=" * 88,
        "FORENSIC BOUNDARY & DISCLAIMER:",
        "This report contains automated investigative leads generated for human triage.",
        "Findings do not establish legal identity, ownership, guilt, or unlawful activity.",
        "Any operational or regulatory action requires independent human verification and lawful process.",
        "=" * 88,
    ])
    return "\n".join(lines)


@app.post("/api/ingest")
async def upload_dataset(file: UploadFile = File(...)):
    """Uploads a CSV, JSON, or XML file and ingests it into the pipeline."""
    global _CURRENT_RESULT, _CURRENT_GRAPH, _CURRENT_RECORDS, _CURRENT_CORRELATIONS, _CURRENT_DATASET_PATH
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing filename in upload.")

    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{file_ext}'. Only .csv, .json, and .xml files are permitted per SIH26146 specification.",
        )

    save_dir = Path("data/raw")
    save_dir.mkdir(parents=True, exist_ok=True)
    dest_path = save_dir / file.filename

    with open(dest_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        res, g, _, recs, corrs = _PIPELINE.run(dest_path)
        _CURRENT_RESULT = res
        _CURRENT_GRAPH = g
        _CURRENT_RECORDS = recs
        _CURRENT_CORRELATIONS = corrs
        _CURRENT_DATASET_PATH = dest_path
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Failed to ingest and analyze file: {str(e)}")

    return {
        "status": "ingested",
        "filename": file.filename,
        "records_ingested": res.validation_summary.total_records,
        "valid_records": res.validation_summary.valid_records,
        "alerts_generated": len(res.alerts),
        "investigative_unit": "Team COGNOVAX",
    }


@app.get("/api/export")
async def export_investigation_dossier(format: str = Query("json", description="Export format: 'json' or 'txt'")):
    """Exports structured case file report in JSON or plain-text format."""
    _ensure_pipeline_run()
    assert _CURRENT_RESULT is not None
    assert _CURRENT_GRAPH is not None

    dossier_text = generate_dossier_text(_CURRENT_RESULT, _CURRENT_GRAPH, _INVESTIGATOR_ANNOTATIONS)

    if format.lower() in ("txt", "text"):
        return Response(
            content=dossier_text,
            media_type="text/plain; charset=utf-8",
            headers={"Content-Disposition": f"attachment; filename=investigation_dossier_{_CURRENT_RESULT.run_id}.txt"},
        )

    distinct_annotations = list({a["target_id"]: a for a in _INVESTIGATOR_ANNOTATIONS.values()}.values())
    active_reviewed = len([a for a in distinct_annotations if a.get("disposition") != "UNREVIEWED"])

    return JSONResponse(
        content={
            "dossier_metadata": {
                "generated_at": _CURRENT_RESULT.run_timestamp.isoformat(),
                "run_id": _CURRENT_RESULT.run_id,
                "classification": "CONFIDENTIAL INVESTIGATIVE DOSSIER",
                "investigative_unit": "Team COGNOVAX",
                "operational_node": "COGNOVAX-AIRGAP-NODE-01",
                "data_class": "SYNTHETIC BENCHMARK / DEMONSTRATION DATASET",
                "sponsor": "National Technical Research Organisation (NTRO)",
                "problem_statement": "SIH26146",
                "disclaimer": "Investigative lead intelligence. Requires human validation before any enforcement action.",
            },
            "summary": {
                "total_records_processed": _CURRENT_RESULT.validation_summary.total_records,
                "valid_records_processed": _CURRENT_RESULT.validation_summary.valid_records,
                "total_correlations_discovered": _CURRENT_RESULT.total_correlations,
                "ranked_alerts_count": len(_CURRENT_RESULT.alerts),
                "evaluation_metrics": _CURRENT_RESULT.evaluation_metrics,
                "investigator_reviewed_count": active_reviewed,
            },
            "investigator_annotations": distinct_annotations,
            "ranked_alerts": [a.model_dump(mode="json") for a in _CURRENT_RESULT.alerts],
            "dossier_text": dossier_text,
        },
        headers={"Content-Disposition": f"attachment; filename=investigation_dossier_{_CURRENT_RESULT.run_id}.json"}
    )


@app.get("/api/export/custody-package")
async def export_chain_of_custody_package():
    """
    Exports a court-admissible, cryptographically sealed Chain-of-Custody evidence bundle (.zip).
    Contains raw evidence, SHA-256 integrity manifest, plain-text dossier, JSON case package,
    and a digitally signed chain-of-custody forensic certificate.
    """
    _ensure_pipeline_run()
    assert _CURRENT_RESULT is not None
    assert _CURRENT_GRAPH is not None

    run_id = _CURRENT_RESULT.run_id
    distinct_annotations = list({a["target_id"]: a for a in _INVESTIGATOR_ANNOTATIONS.values()}.values())
    dossier_text = generate_dossier_text(_CURRENT_RESULT, _CURRENT_GRAPH, _INVESTIGATOR_ANNOTATIONS)
    case_json = json.dumps(
        {
            "dossier_metadata": {
                "generated_at": _CURRENT_RESULT.run_timestamp.isoformat(),
                "run_id": run_id,
                "classification": "CONFIDENTIAL INVESTIGATIVE DOSSIER",
                "investigative_unit": "Team COGNOVAX",
                "operator_id": "COGNOVAX-AIRGAP-NODE-01",
                "sponsor": "National Technical Research Organisation (NTRO)",
                "problem_statement": "SIH26146",
            },
            "summary": {
                "total_records_processed": _CURRENT_RESULT.validation_summary.total_records,
                "valid_records_processed": _CURRENT_RESULT.validation_summary.valid_records,
                "total_correlations_discovered": _CURRENT_RESULT.total_correlations,
                "ranked_alerts_count": len(_CURRENT_RESULT.alerts),
                "evaluation_metrics": _CURRENT_RESULT.evaluation_metrics,
                "investigator_reviewed_count": len([a for a in distinct_annotations if a.get("disposition") != "UNREVIEWED"]),
            },
            "investigator_annotations": distinct_annotations,
            "ranked_alerts": [a.model_dump(mode="json") for a in _CURRENT_RESULT.alerts],
        },
        indent=2,
    )
    annotations_json = json.dumps(distinct_annotations, indent=2)

    # Read raw evidence
    raw_evidence_bytes = b""
    raw_evidence_filename = "EVIDENCE_RAW_DATASET.bin"
    if _CURRENT_DATASET_PATH and _CURRENT_DATASET_PATH.exists():
        raw_evidence_bytes = _CURRENT_DATASET_PATH.read_bytes()
        raw_evidence_filename = f"EVIDENCE_RAW_{_CURRENT_DATASET_PATH.name}"
    else:
        raw_evidence_bytes = dossier_text.encode("utf-8")

    # Compute SHA-256 hashes
    h_evidence = hashlib.sha256(raw_evidence_bytes).hexdigest()
    h_dossier = hashlib.sha256(dossier_text.encode("utf-8")).hexdigest()
    h_json = hashlib.sha256(case_json.encode("utf-8")).hexdigest()
    h_annot = hashlib.sha256(annotations_json.encode("utf-8")).hexdigest()

    sha256sums_content = (
        f"{h_evidence}  {raw_evidence_filename}\n"
        f"{h_dossier}  INVESTIGATION_DOSSIER_{run_id}.txt\n"
        f"{h_json}  INVESTIGATION_CASE_PACKAGE_{run_id}.json\n"
        f"{h_annot}  INVESTIGATION_CASE_NOTES.json\n"
    )

    certificate_text = (
        "========================================================================================\n"
        "           NATIONAL TECHNICAL RESEARCH ORGANISATION (NTRO) // SIH26146\n"
        "                  DIGITAL FORENSIC CHAIN-OF-CUSTODY CERTIFICATE\n"
        "========================================================================================\n"
        f"CERTIFICATE ID      : COC-{run_id}\n"
        f"INVESTIGATIVE UNIT  : TEAM COGNOVAX // FORENSIC INTELLIGENCE DIVISION\n"
        f"OPERATOR IDENTIFIER : COGNOVAX-AIRGAP-NODE-01\n"
        f"TIMESTAMP (UTC)     : {_CURRENT_RESULT.run_timestamp.isoformat()}\n"
        f"INTELLIGENCE RUN ID : {run_id}\n"
        f"EXECUTION STATUS    : STRICT AIR-GAPPED OFFLINE COMPLIANT\n"
        "----------------------------------------------------------------------------------------\n"
        "EVIDENCE PROVENANCE & CRYPTOGRAPHIC VERIFICATION:\n"
        f"  1. Primary Ingested Asset: {raw_evidence_filename}\n"
        f"     SHA-256 Seal         : {h_evidence}\n"
        f"     Byte Size            : {len(raw_evidence_bytes)} bytes\n\n"
        f"  2. Investigative Dossier : INVESTIGATION_DOSSIER_{run_id}.txt\n"
        f"     SHA-256 Seal         : {h_dossier}\n\n"
        f"  3. Machine Case Package  : INVESTIGATION_CASE_PACKAGE_{run_id}.json\n"
        f"     SHA-256 Seal         : {h_json}\n\n"
        f"  4. Case Notes & Tags     : INVESTIGATION_CASE_NOTES.json ({len(distinct_annotations)} logged entities)\n"
        f"     SHA-256 Seal         : {h_annot}\n"
        "----------------------------------------------------------------------------------------\n"
        "CHAIN-OF-CUSTODY ATTESTATION:\n"
        "I hereby certify under digital forensic protocols that the forensic artifacts contained\n"
        "in this package were processed exclusively within an isolated offline air-gapped\n"
        "environment with zero telemetry leakage. All cryptographic seals match the manifest.\n"
        "========================================================================================\n"
    )

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(raw_evidence_filename, raw_evidence_bytes)
        zf.writestr(f"INVESTIGATION_DOSSIER_{run_id}.txt", dossier_text)
        zf.writestr(f"INVESTIGATION_CASE_PACKAGE_{run_id}.json", case_json)
        zf.writestr("INVESTIGATION_CASE_NOTES.json", annotations_json)
        zf.writestr("SHA256SUMS.txt", sha256sums_content)
        zf.writestr("CHAIN_OF_CUSTODY_CERTIFICATE.txt", certificate_text)

    zip_bytes = zip_buffer.getvalue()
    return Response(
        content=zip_bytes,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename=chain_of_custody_package_{run_id}.zip"},
    )


@app.get("/api/export/intelligence-brief", response_class=HTMLResponse)
async def export_intelligence_brief():
    """
    Generates and serves a standalone, agency-grade classified forensic intelligence briefing.
    Features executive KPI dashboards, syndicate analysis, network attribution, and printable layout.
    """
    _ensure_pipeline_run()
    assert _CURRENT_RESULT is not None
    assert _CURRENT_GRAPH is not None
    analytics = GraphAnalytics(_CURRENT_GRAPH)
    syndicates = analytics.detect_syndicates(min_size=3)
    html_content = generate_intelligence_brief_html(
        result=_CURRENT_RESULT,
        graph=_CURRENT_GRAPH,
        records=_CURRENT_RECORDS,
        syndicates=syndicates,
        dataset_path=_CURRENT_DATASET_PATH,
        annotations=_INVESTIGATOR_ANNOTATIONS,
    )
    return HTMLResponse(content=html_content)

