"""
SIH26146 — Multi-Dimensional Behavioral, Temporal, Network & Graph Feature Pipeline
Fulfills REQ-008, Section 13, 14, and docs/06-ml-specification.md.
Extracts reproducible, documented feature vectors per target entity/wallet/cluster.
"""

from __future__ import annotations
import math
from datetime import datetime
from typing import Any, Dict, List, Optional
from collections import defaultdict
import numpy as np
import pandas as pd
import networkx as nx

from src.models.schema import NormalizedRecord, CorrelationRecord
from src.graph.analytics import GraphAnalytics


FEATURE_CONTRACT: Dict[str, Dict[str, Any]] = {
    "tx_count": {
        "definition": "Total count of transactions involving this entity",
        "data_source": "Blockchain transaction records",
        "unit": "integer count",
        "expected_range": "[1, 100000+]",
        "why_it_matters": "Baseline activity volume; extreme values indicate automated bots or service nodes.",
        "fp_risk": "High-volume commercial payment processors or exchange hot wallets.",
    },
    "total_amount_btc": {
        "definition": "Total volume of Bitcoin transferred across all transactions",
        "data_source": "Transaction output amounts",
        "unit": "BTC",
        "expected_range": "[0.0, 100000.0]",
        "why_it_matters": "Identifies high-value transfers requiring elevated investigative priority.",
        "fp_risk": "Institutional liquidity rebalancing or OTC desks.",
    },
    "avg_amount_btc": {
        "definition": "Mean value transferred per transaction",
        "data_source": "Transaction output amounts",
        "unit": "BTC",
        "expected_range": "[0.0, 5000.0]",
        "why_it_matters": "Distinguishes micro-structuring from large lump-sum transfers.",
        "fp_risk": "Standard periodic payroll or vendor payouts.",
    },
    "std_amount_btc": {
        "definition": "Standard deviation of transaction amounts",
        "data_source": "Transaction output amounts",
        "unit": "BTC",
        "expected_range": "[0.0, 5000.0]",
        "why_it_matters": "Low variance with uniform amounts is typical of automated peel chains or tumbling.",
        "fp_risk": "Recurring fixed-amount subscription payments.",
    },
    "unique_ip_count": {
        "definition": "Number of unique source IPs observed broadcasting transactions for this entity",
        "data_source": "Network telemetry layer",
        "unit": "count",
        "expected_range": "[1, 50+]",
        "why_it_matters": "Rapid IP diversity suggests VPN/Tor proxy hopping or botnet participation.",
        "fp_risk": "Legitimate mobile wallet users connecting across cellular and public WiFi.",
    },
    "ip_reuse_max": {
        "definition": "Maximum count of observations originating from a single IP",
        "data_source": "Network telemetry layer",
        "unit": "count",
        "expected_range": "[1, 1000+]",
        "why_it_matters": "Consistently reused IP for distinct wallets indicates shared node infrastructure.",
        "fp_risk": "Shared corporate NAT gateways or P2P full nodes.",
    },
    "unique_countries_count": {
        "definition": "Number of distinct countries mapped to source IPs",
        "data_source": "Offline Geo-IP database lookup",
        "unit": "count",
        "expected_range": "[1, 15+]",
        "why_it_matters": "Multi-jurisdictional broadcasting in short time spans suggests deliberate proxy evasion.",
        "fp_risk": "Users traveling or multi-region cloud applications.",
    },
    "unique_asn_count": {
        "definition": "Number of distinct Autonomous System Numbers",
        "data_source": "Offline Geo-IP database lookup",
        "unit": "count",
        "expected_range": "[1, 15+]",
        "why_it_matters": "Transit across multiple diverse autonomous systems indicating hosting/proxy relays.",
        "fp_risk": "Multi-cloud hosting environments.",
    },
    "inter_arrival_time_min": {
        "definition": "Minimum time interval in seconds between consecutive transactions",
        "data_source": "Transaction timestamps",
        "unit": "seconds",
        "expected_range": "[0.0, 86400.0+]",
        "why_it_matters": "Extremely small intervals (<10s) indicate scripted/automated transaction generation.",
        "fp_risk": "Exchange internal batching operations.",
    },
    "burst_score": {
        "definition": "Fraction of transactions occurring within 60 seconds of preceding transaction",
        "data_source": "Transaction timestamps",
        "unit": "ratio [0.0 - 1.0]",
        "expected_range": "[0.0, 1.0]",
        "why_it_matters": "Rapid-fire burst transfers characteristic of extortion drops or swift fund flight.",
        "fp_risk": "High-volume e-commerce checkout spikes.",
    },
    "velocity_tx_per_hour": {
        "definition": "Rate of transactions per hour across observed lifespan",
        "data_source": "Timestamps and duration",
        "unit": "tx/hour",
        "expected_range": "[0.0, 3600.0]",
        "why_it_matters": "Velocity spike signals active laundering or automated drain scripts.",
        "fp_risk": "Mining pool payout batches.",
    },
    "in_degree": {
        "definition": "Number of distinct incoming input edges into this entity in the graph",
        "data_source": "Graph topology",
        "unit": "degree count",
        "expected_range": "[0, 500+]",
        "why_it_matters": "High in-degree represents a collection or consolidation funnel (fan-in).",
        "fp_risk": "Merchant payment aggregation wallets.",
    },
    "out_degree": {
        "definition": "Number of distinct outgoing output edges from this entity in the graph",
        "data_source": "Graph topology",
        "unit": "degree count",
        "expected_range": "[0, 500+]",
        "why_it_matters": "High out-degree indicates peeling, splitting, or layering fund dispersal (fan-out).",
        "fp_risk": "Mining pool dividend distribution.",
    },
    "fan_out_ratio": {
        "definition": "Ratio of outgoing edges to incoming edges (out_degree / max(1, in_degree))",
        "data_source": "Graph topology",
        "unit": "ratio",
        "expected_range": "[0.0, 50.0]",
        "why_it_matters": "High ratio strongly signals fund fragmentation and layering structuring.",
        "fp_risk": "Airdrop distributions.",
    },
    "fan_in_ratio": {
        "definition": "Ratio of incoming edges to outgoing edges (in_degree / max(1, out_degree))",
        "data_source": "Graph topology",
        "unit": "ratio",
        "expected_range": "[0.0, 50.0]",
        "why_it_matters": "High ratio signals post-layering fund pooling / consolidation.",
        "fp_risk": "Cold-storage sweeps.",
    },
    "pagerank": {
        "definition": "PageRank topological authority / flow centrality in transaction graph",
        "data_source": "NetworkX PageRank algorithm",
        "unit": "probability score [0.0 - 1.0]",
        "expected_range": "[0.0, 0.20]",
        "why_it_matters": "Entities serving as central hubs in fund circulation topology.",
        "fp_risk": "Major cryptocurrency exchange deposit addresses.",
    },
}


class FeatureExtractor:
    """
    Extracts multi-domain feature vectors per entity/wallet/target from normalized records and graph.
    """

    def __init__(self, graph: Optional[nx.DiGraph] = None):
        self.graph = graph
        self.pagerank_scores = GraphAnalytics(graph).compute_pagerank() if graph else {}

    def extract_features(self, records: List[NormalizedRecord]) -> pd.DataFrame:
        """
        Aggregates records by target identifier (primary input wallet or entity cluster)
        and computes the full feature contract matrix.
        """
        # Group records by target entity (represented by primary input address or TXID if wallet missing)
        target_records: Dict[str, List[NormalizedRecord]] = defaultdict(list)
        for r in records:
            if r.input_addresses:
                # Key by primary input wallet
                target_records[r.input_addresses[0]].append(r)
            elif r.txid:
                target_records[r.txid].append(r)

        feature_rows: List[Dict[str, Any]] = []

        for target_id, recs in target_records.items():
            # Sort records chronologically
            sorted_recs = sorted(recs, key=lambda x: x.timestamp)
            tx_count = len(sorted_recs)

            # --- 1. Transaction Behavioral Features ---
            amounts: List[float] = []
            fees: List[float] = []
            for r in sorted_recs:
                tot = r.total_output_amount() or r.total_input_amount()
                if tot > 0:
                    amounts.append(tot)
                if r.fee is not None:
                    fees.append(r.fee)

            total_amount = sum(amounts) if amounts else 0.0
            avg_amount = np.mean(amounts) if amounts else 0.0
            std_amount = np.std(amounts) if len(amounts) > 1 else 0.0

            # --- 2. Network Telemetry Features ---
            ips = [r.src_ip for r in sorted_recs if r.src_ip and r.src_ip != "0.0.0.0"]
            unique_ips = len(set(ips))
            ip_counts = defaultdict(int)
            for ip in ips:
                ip_counts[ip] += 1
            ip_reuse_max = max(ip_counts.values()) if ip_counts else 0

            countries = set(r.geo_country for r in sorted_recs if r.geo_country and r.geo_country not in ("UNKNOWN", "MALFORMED"))
            asns = set(r.asn for r in sorted_recs if r.asn and r.asn not in ("AS0", "AS-UNKNOWN"))

            # --- 3. Temporal Features ---
            inter_arrivals: List[float] = []
            burst_count = 0
            for i in range(1, len(sorted_recs)):
                delta = (sorted_recs[i].timestamp - sorted_recs[i-1].timestamp).total_seconds()
                delta = max(0.0, delta)
                inter_arrivals.append(delta)
                if delta <= 60.0:
                    burst_count += 1

            min_interval = min(inter_arrivals) if inter_arrivals else 3600.0
            avg_interval = np.mean(inter_arrivals) if inter_arrivals else 3600.0
            burst_score = burst_count / (tx_count - 1) if tx_count > 1 else 0.0

            if tx_count <= 1:
                time_span_seconds = 0.0
                velocity = 0.0
            else:
                time_span_seconds = max(1.0, (sorted_recs[-1].timestamp - sorted_recs[0].timestamp).total_seconds())
                time_span_hours = time_span_seconds / 3600.0
                velocity = tx_count / max(0.05, time_span_hours)

            # --- 4. Graph Topological Features ---
            in_degree = 0
            out_degree = 0
            pr_val = 0.0
            w_node = f"WALLET:{target_id}"

            if self.graph:
                if self.graph.has_node(w_node):
                    # For a wallet entity, count actual destination counterparties (WALLET -> TX -> DEST)
                    tx_successors = [s for s in self.graph.successors(w_node) if s.startswith("TX:")]
                    dest_wallets = set()
                    for tx_s in tx_successors:
                        for dest in self.graph.successors(tx_s):
                            if dest.startswith("WALLET:") and dest != w_node:
                                dest_wallets.add(dest)

                    # Count funding sources (SRC -> TX -> WALLET)
                    tx_predecessors = [p for p in self.graph.predecessors(w_node) if p.startswith("TX:")]
                    src_wallets = set()
                    for tx_p in tx_predecessors:
                        for src in self.graph.predecessors(tx_p):
                            if src.startswith("WALLET:") and src != w_node:
                                src_wallets.add(src)

                    out_degree = max(len(dest_wallets), self.graph.out_degree(w_node))
                    in_degree = max(len(src_wallets), self.graph.in_degree(w_node))
                    pr_val = self.pagerank_scores.get(w_node, 0.0)
                elif self.graph.has_node(f"TX:{target_id}"):
                    tx_node = f"TX:{target_id}"
                    in_degree = self.graph.in_degree(tx_node)
                    out_degree = self.graph.out_degree(tx_node)
                    pr_val = self.pagerank_scores.get(tx_node, 0.0)

            fan_out_ratio = out_degree / max(1, in_degree)
            fan_in_ratio = in_degree / max(1, out_degree)

            row = {
                "target_id": target_id,
                "tx_count": tx_count,
                "total_amount_btc": round(float(total_amount), 6),
                "avg_amount_btc": round(float(avg_amount), 6),
                "std_amount_btc": round(float(std_amount), 6),
                "unique_ip_count": unique_ips,
                "ip_reuse_max": ip_reuse_max,
                "unique_countries_count": len(countries),
                "unique_asn_count": len(asns),
                "inter_arrival_time_min": round(float(min_interval), 2),
                "burst_score": round(float(burst_score), 4),
                "velocity_tx_per_hour": round(float(velocity), 2),
                "observation_window_seconds": round(float(time_span_seconds), 2),
                "in_degree": in_degree,
                "out_degree": out_degree,
                "fan_out_ratio": round(float(fan_out_ratio), 4),
                "fan_in_ratio": round(float(fan_in_ratio), 4),
                "pagerank": round(float(pr_val), 6),
                # Provenance linkages
                "source_record_ids": [f"{r.source_file_id}#row{r.source_row_id}" for r in sorted_recs],
            }
            feature_rows.append(row)

        df = pd.DataFrame(feature_rows)
        return df
