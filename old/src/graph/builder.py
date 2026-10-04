"""
SIH26146 — Entity / Transaction Graph Builder
Fulfills REQ-008, Section 10, 11, and docs/03-architecture.md.
Constructs a typed multi-directed graph connecting IPs, Transactions, and Wallets/Entities.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Set, Tuple
import networkx as nx
from src.models.schema import NormalizedRecord, CorrelationRecord


class GraphBuilder:
    """
    Constructs an investigative knowledge graph from normalized records and correlation records.
    """

    def __init__(self):
        self.graph = nx.DiGraph()

    def build_graph(
        self,
        records: List[NormalizedRecord],
        correlations: Optional[List[CorrelationRecord]] = None,
    ) -> nx.DiGraph:
        """
        Builds or updates the graph with nodes and typed edges.
        """
        G = self.graph

        for rec in records:
            # 1. IP Node
            if rec.src_ip and rec.src_ip != "0.0.0.0":
                ip_id = f"IP:{rec.src_ip}"
                if not G.has_node(ip_id):
                    G.add_node(
                        ip_id,
                        node_type="IP",
                        label=rec.src_ip,
                        country=rec.geo_country or "UNKNOWN",
                        asn=rec.asn or "AS0",
                        observation_count=1,
                    )
                else:
                    G.nodes[ip_id]["observation_count"] = G.nodes[ip_id].get("observation_count", 1) + 1

            # 2. Transaction Node
            if rec.txid:
                tx_id = f"TX:{rec.txid}"
                if not G.has_node(tx_id):
                    G.add_node(
                        tx_id,
                        node_type="TX",
                        label=f"{rec.txid[:8]}...",
                        full_txid=rec.txid,
                        timestamp=rec.timestamp.isoformat(),
                        fee=rec.fee or 0.0,
                        total_output=rec.total_output_amount(),
                        total_input=rec.total_input_amount(),
                        script_type=rec.script_type or "UNKNOWN",
                    )

                # Connect IP -> TX edge (OBSERVED)
                if rec.src_ip and rec.src_ip != "0.0.0.0":
                    ip_id = f"IP:{rec.src_ip}"
                    G.add_edge(
                        ip_id,
                        tx_id,
                        edge_type="OBSERVED",
                        label="OBSERVED",
                        src_port=rec.src_port,
                        dst_port=rec.dst_port,
                        timestamp=rec.timestamp.isoformat(),
                    )

                # 3. Input Wallet Nodes & Edges (WALLET -> TX)
                for addr, amt in zip(rec.input_addresses, rec.input_amounts if rec.input_amounts else [0.0]*len(rec.input_addresses)):
                    w_id = f"WALLET:{addr}"
                    if not G.has_node(w_id):
                        G.add_node(w_id, node_type="WALLET", label=f"{addr[:10]}...", full_address=addr, total_sent=amt, total_received=0.0)
                    else:
                        G.nodes[w_id]["total_sent"] = G.nodes[w_id].get("total_sent", 0.0) + amt

                    G.add_edge(w_id, tx_id, edge_type="INPUT", label=f"INPUT ({amt} BTC)", amount=amt)

                # 4. Output Wallet Nodes & Edges (TX -> WALLET)
                for addr, amt in zip(rec.output_addresses, rec.output_amounts if rec.output_amounts else [0.0]*len(rec.output_addresses)):
                    w_id = f"WALLET:{addr}"
                    if not G.has_node(w_id):
                        G.add_node(w_id, node_type="WALLET", label=f"{addr[:10]}...", full_address=addr, total_sent=0.0, total_received=amt)
                    else:
                        G.nodes[w_id]["total_received"] = G.nodes[w_id].get("total_received", 0.0) + amt

                    G.add_edge(tx_id, w_id, edge_type="OUTPUT", label=f"OUTPUT ({amt} BTC)", amount=amt)

                # 5. Common-Input Heuristic (Co-spending Clustering)
                if len(rec.input_addresses) > 1:
                    # Link co-spent inputs symmetrically with COMMON_INPUT edge
                    for i in range(len(rec.input_addresses)):
                        for j in range(i + 1, len(rec.input_addresses)):
                            w1 = f"WALLET:{rec.input_addresses[i]}"
                            w2 = f"WALLET:{rec.input_addresses[j]}"
                            G.add_edge(w1, w2, edge_type="COMMON_INPUT", label="COMMON_INPUT", txid=rec.txid)
                            G.add_edge(w2, w1, edge_type="COMMON_INPUT", label="COMMON_INPUT", txid=rec.txid)

        # 6. Incorporate Correlation Evidence Edges
        if correlations:
            for corr in correlations:
                tx_node = f"TX:{corr.txid}"
                if G.has_node(tx_node):
                    G.nodes[tx_node]["correlation_confidence"] = corr.correlation_confidence
                    G.nodes[tx_node]["match_methods"] = corr.match_methods

        return G
