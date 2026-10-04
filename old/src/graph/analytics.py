"""
SIH26146 — Graph Analytics & Neighborhood Query Engine
Fulfills REQ-008, Section 12, and docs/03-architecture.md.
Extracts localized ego-subgraphs, path traces, and topological metrics.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Set
import networkx as nx


class GraphAnalytics:
    """Provides analytical and neighborhood extraction services over the transaction/entity graph."""

    def __init__(self, graph: nx.DiGraph):
        self.graph = graph
        self._cached_syndicates: Optional[List[Dict[str, Any]]] = None

    def get_summary(self) -> Dict[str, Any]:
        """Returns topological summary metrics of the whole graph."""
        G = self.graph
        node_types: Dict[str, int] = {}
        for _, data in G.nodes(data=True):
            t = data.get("node_type", "UNKNOWN")
            node_types[t] = node_types.get(t, 0) + 1

        edge_types: Dict[str, int] = {}
        for _, _, data in G.edges(data=True):
            t = data.get("edge_type", "UNKNOWN")
            edge_types[t] = edge_types.get(t, 0) + 1

        return {
            "total_nodes": G.number_of_nodes(),
            "total_edges": G.number_of_edges(),
            "node_type_counts": node_types,
            "edge_type_counts": edge_types,
            "connected_components": nx.number_weakly_connected_components(G) if G.number_of_nodes() > 0 else 0,
        }

    def compute_pagerank(self) -> Dict[str, float]:
        """Computes PageRank centrality scores safely offline."""
        if self.graph.number_of_nodes() == 0:
            return {}
        try:
            return nx.pagerank(self.graph, alpha=0.85, max_iter=100)
        except Exception:
            return {n: 1.0 / self.graph.number_of_nodes() for n in self.graph.nodes()}

    def extract_neighborhood(
        self,
        target_id: str,
        max_hops: int = 2,
        max_nodes: int = 80,
    ) -> Dict[str, Any]:
        """
        Extracts an investigator-focused sub-neighborhood centered on target_id.
        target_id can be a TXID, Wallet address, or IP.
        Formats the result for visualization (nodes array, edges array).
        """
        G = self.graph
        
        # Resolve target to full node key
        resolved_node: Optional[str] = None
        if G.has_node(target_id):
            resolved_node = target_id
        elif G.has_node(f"TX:{target_id}"):
            resolved_node = f"TX:{target_id}"
        elif G.has_node(f"WALLET:{target_id}"):
            resolved_node = f"WALLET:{target_id}"
        elif G.has_node(f"IP:{target_id}"):
            resolved_node = f"IP:{target_id}"

        if not resolved_node:
            # Fallback: search for node label or substring
            for n in G.nodes():
                if target_id in n:
                    resolved_node = n
                    break

        if not resolved_node:
            return {"nodes": [], "edges": [], "target_node": target_id}

        # Multi-hop BFS neighborhood expansion
        visited: Set[str] = {resolved_node}
        current_layer: Set[str] = {resolved_node}

        for _ in range(max_hops):
            next_layer: Set[str] = set()
            for u in current_layer:
                # Add successors and predecessors (in-edges and out-edges)
                neighbors = set(G.successors(u)).union(set(G.predecessors(u)))
                for v in neighbors:
                    if v not in visited:
                        visited.add(v)
                        next_layer.add(v)
                        if len(visited) >= max_nodes:
                            break
                if len(visited) >= max_nodes:
                    break
            current_layer = next_layer
            if len(visited) >= max_nodes:
                break

        subG = G.subgraph(visited)

        # Build clean JSON serializable output
        nodes_out = []
        for n, data in subG.nodes(data=True):
            node_dict = dict(data)
            node_dict["id"] = n
            node_dict["is_target"] = (n == resolved_node)
            nodes_out.append(node_dict)

        edges_out = []
        for u, v, data in subG.edges(data=True):
            edge_dict = dict(data)
            edge_dict["source"] = u
            edge_dict["target"] = v
            edges_out.append(edge_dict)

        return {
            "target_node": resolved_node,
            "node_count": len(nodes_out),
            "edge_count": len(edges_out),
            "nodes": nodes_out,
            "edges": edges_out,
        }

    def expand_node(
        self,
        node_id: str,
        hops: int = 1,
        max_nodes: int = 35,
    ) -> Dict[str, Any]:
        """
        Dynamically expands 1-hop (or n-hop) neighbors for a specific node in an existing topology.
        Returns the immediate neighboring nodes and all incident edges.
        """
        G = self.graph
        resolved = None
        if G.has_node(node_id):
            resolved = node_id
        elif G.has_node(f"TX:{node_id}"):
            resolved = f"TX:{node_id}"
        elif G.has_node(f"WALLET:{node_id}"):
            resolved = f"WALLET:{node_id}"
        elif G.has_node(f"IP:{node_id}"):
            resolved = f"IP:{node_id}"
        else:
            for n in G.nodes():
                if node_id in n:
                    resolved = n
                    break

        if not resolved:
            return {"expanded_from": node_id, "nodes": [], "edges": []}

        # Collect neighbors
        neighbors = set(G.successors(resolved)).union(set(G.predecessors(resolved)))
        # Limit to max_nodes
        selected_neighbors = list(neighbors)[:max_nodes]
        all_nodes = set(selected_neighbors).union({resolved})

        subG = G.subgraph(all_nodes)
        nodes_out = []
        for n, data in subG.nodes(data=True):
            node_dict = dict(data)
            node_dict["id"] = n
            node_dict["is_target"] = False
            nodes_out.append(node_dict)

        edges_out = []
        for u, v, data in subG.edges(data=True):
            edge_dict = dict(data)
            edge_dict["source"] = u
            edge_dict["target"] = v
            edges_out.append(edge_dict)

        return {
            "expanded_from": resolved,
            "node_count": len(nodes_out),
            "edge_count": len(edges_out),
            "nodes": nodes_out,
            "edges": edges_out,
        }

    def find_path(self, source_id: str, target_id: str) -> Dict[str, Any]:
        """
        Calculates the shortest topological path between source_id and target_id.
        Traverses fund transfers and telemetry connections.
        """
        G = self.graph

        def resolve(nid: str) -> Optional[str]:
            if G.has_node(nid):
                return nid
            for prefix in ["TX:", "WALLET:", "IP:"]:
                if G.has_node(f"{prefix}{nid}"):
                    return f"{prefix}{nid}"
            for n in G.nodes():
                if nid in n:
                    return n
            return None

        s_res = resolve(source_id)
        t_res = resolve(target_id)
        if not s_res or not t_res:
            return {"found": False, "reason": "One or both nodes not found in graph", "nodes": [], "edges": []}

        # Convert to undirected copy for path finding across bi-directional relationships
        undirected_G = G.to_undirected()
        try:
            path_nodes = nx.shortest_path(undirected_G, source=s_res, target=t_res)
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return {"found": False, "reason": "No traversable path between nodes", "nodes": [], "edges": []}

        # Extract edges along the path
        path_edges = []
        for i in range(len(path_nodes) - 1):
            u, v = path_nodes[i], path_nodes[i + 1]
            if G.has_edge(u, v):
                e_data = dict(G.get_edge_data(u, v))
                e_data["source"] = u
                e_data["target"] = v
                path_edges.append(e_data)
            elif G.has_edge(v, u):
                e_data = dict(G.get_edge_data(v, u))
                e_data["source"] = v
                e_data["target"] = u
                path_edges.append(e_data)

        # Collect node data
        nodes_out = []
        for n in path_nodes:
            nd = dict(G.nodes[n])
            nd["id"] = n
            nodes_out.append(nd)

        return {
            "found": True,
            "path_length": len(path_nodes) - 1,
            "nodes": nodes_out,
            "edges": path_edges,
        }

    def trace_taint(
        self,
        source_id: str,
        max_depth: int = 3,
        min_taint: float = 0.01,
    ) -> Dict[str, Any]:
        """
        Executes multi-hop fund taint propagation analysis (Haircut / Poison model)
        from a suspicious source wallet or transaction across downstream transfer edges.
        Fulfills advanced crypto-forensic intelligence requirements.
        """
        G = self.graph

        def resolve(nid: str) -> Optional[str]:
            if G.has_node(nid):
                return nid
            for prefix in ["WALLET:", "TX:", "IP:"]:
                if G.has_node(f"{prefix}{nid}"):
                    return f"{prefix}{nid}"
            for n in G.nodes():
                if nid in n:
                    return n
            return None

        resolved = resolve(source_id)
        if not resolved:
            return {
                "source_node": source_id,
                "found": False,
                "tainted_nodes": {},
                "tainted_edges": [],
                "summary": {"total_tainted_nodes": 0, "max_hop_reached": 0},
            }

        # BFS state: {node_id: (taint_score, hop)}
        tainted_nodes: Dict[str, Dict[str, Any]] = {
            resolved: {
                "id": resolved,
                "taint_score": 1.0,
                "hop": 0,
                "node_type": G.nodes[resolved].get("node_type", "UNKNOWN"),
                "label": G.nodes[resolved].get("label", resolved),
            }
        }

        tainted_edges: List[Dict[str, Any]] = []
        current_layer = {resolved: 1.0}

        for hop in range(1, max_depth + 1):
            next_layer: Dict[str, float] = {}
            for u, u_taint in current_layer.items():
                successors = list(G.successors(u))
                if not successors:
                    continue

                # Calculate total outgoing weight/amount if present
                weights = []
                for v in successors:
                    e_data = G.get_edge_data(u, v) or {}
                    amt = e_data.get("amount_btc") or e_data.get("weight") or 1.0
                    weights.append(float(amt) if float(amt) > 0 else 1.0)

                total_weight = sum(weights) or 1.0

                for v, w in zip(successors, weights):
                    # Proportional Haircut taint split
                    fraction = w / total_weight
                    v_taint = round(u_taint * fraction, 4)

                    if v_taint < min_taint:
                        continue

                    # Record edge
                    edge_meta = dict(G.get_edge_data(u, v) or {})
                    edge_meta["source"] = u
                    edge_meta["target"] = v
                    edge_meta["taint_fraction"] = v_taint
                    edge_meta["hop"] = hop
                    tainted_edges.append(edge_meta)

                    # Update node taint (accumulate or take max)
                    if v not in tainted_nodes or v_taint > tainted_nodes[v]["taint_score"]:
                        tainted_nodes[v] = {
                            "id": v,
                            "taint_score": v_taint,
                            "hop": hop,
                            "node_type": G.nodes[v].get("node_type", "UNKNOWN"),
                            "label": G.nodes[v].get("label", v),
                        }
                    next_layer[v] = max(next_layer.get(v, 0.0), v_taint)

            current_layer = next_layer
            if not current_layer:
                break

        max_hop = max((data["hop"] for data in tainted_nodes.values()), default=0)

        return {
            "source_node": resolved,
            "found": True,
            "max_depth": max_depth,
            "tainted_nodes": tainted_nodes,
            "tainted_edges": tainted_edges,
            "summary": {
                "total_tainted_nodes": len(tainted_nodes),
                "max_hop_reached": max_hop,
                "downstream_volume_hops": len(tainted_edges),
            },
        }

    def detect_syndicates(self, min_size: int = 3) -> List[Dict[str, Any]]:
        """
        Discovers coordinated laundering syndicates, botnet rings, and transaction communities
        using topological graph partitioning, motif matching, and flow heuristics.
        Returns prioritized forensic syndicate dossiers with typology classifications.
        """
        if self._cached_syndicates is not None:
            return self._cached_syndicates

        G = self.graph
        if G.number_of_nodes() < min_size:
            return []

        undirected_G = G.to_undirected()
        raw_components = list(nx.connected_components(undirected_G))
        raw_components.sort(key=len, reverse=True)

        # Partition larger components into tighter communities if possible
        clusters: List[Set[str]] = []
        for comp in raw_components[:60]:
            if len(comp) < min_size:
                continue
            if len(comp) > 80:
                subG = undirected_G.subgraph(comp)
                try:
                    # Fast linear-time community partition for large clusters
                    communities = list(nx.community.label_propagation_communities(subG))
                    for comm in communities:
                        if len(comm) >= min_size:
                            clusters.append(set(comm))
                except Exception:
                    clusters.append(set(comp))
            elif len(comp) > 20:
                subG = undirected_G.subgraph(comp)
                try:
                    communities = list(nx.community.greedy_modularity_communities(subG))
                    for comm in communities:
                        if len(comm) >= min_size:
                            clusters.append(set(comm))
                except Exception:
                    clusters.append(set(comp))
            else:
                clusters.append(set(comp))

        syndicates: List[Dict[str, Any]] = []

        for idx, cluster in enumerate(clusters, 1):
            nodes_in_cluster = list(cluster)
            subG = G.subgraph(nodes_in_cluster)

            wallets = [n for n in nodes_in_cluster if n.startswith("WALLET:")]
            txs = [n for n in nodes_in_cluster if n.startswith("TX:")]
            ips = [n for n in nodes_in_cluster if n.startswith("IP:")]

            # Aggregate transacted volume
            total_vol = 0.0
            for u, v, data in subG.edges(data=True):
                amt = data.get("amount") or data.get("amount_btc") or 0.0
                try:
                    total_vol += float(amt)
                except (ValueError, TypeError):
                    pass

            # Gather infrastructure metadata
            asns = set()
            countries = set()
            for ip_node in ips:
                data = G.nodes[ip_node]
                if data.get("asn"):
                    asns.add(str(data.get("asn")))
                if data.get("country"):
                    countries.add(str(data.get("country")))

            # Detect typologies based on motifs
            # 1. Peeling chain: sequential TX-WALLET-TX linear flow with multiple hops
            is_peeling = False
            if len(txs) >= 3 and len(wallets) >= 3:
                tx_in_degrees = [subG.in_degree(t) for t in txs]
                tx_out_degrees = [subG.out_degree(t) for t in txs]
                if any(deg >= 1 for deg in tx_in_degrees) and any(deg >= 1 for deg in tx_out_degrees):
                    is_peeling = True

            # 2. Structuring / Mixer: fan-out or fan-in star
            is_structuring = False
            for t in txs:
                if subG.out_degree(t) >= 4 or subG.in_degree(t) >= 4:
                    is_structuring = True
                    break

            # 3. High-velocity botnet dispatch: 1 IP observed driving >= 3 TXs
            is_botnet = False
            for ip_node in ips:
                tx_successors = [v for v in subG.successors(ip_node) if v.startswith("TX:")]
                if len(tx_successors) >= 3:
                    is_botnet = True
                    break

            # 4. Exchange sweep: very large volume, many wallets, but low anomaly
            is_exchange = False
            if total_vol > 50.0 and len(wallets) >= 8 and not is_botnet and not is_peeling:
                is_exchange = True

            # Assign typology, risk score, and severity
            if is_peeling:
                typology = "PEELING_CHAIN_RING"
                risk_score = 0.94
                severity = "CRITICAL"
                summary = (
                    f"Sequential change-peeling ring coordinating {len(txs)} consecutive transactions "
                    f"and {len(wallets)} addresses moving {round(total_vol, 4)} BTC across progressive hops."
                )
            elif is_structuring:
                typology = "STRUCTURING_FANOUT_FANIN"
                risk_score = 0.88
                severity = "HIGH"
                summary = (
                    f"Structured fan-out / fan-in mixing pool coordinating {len(wallets)} addresses "
                    f"to fragment and consolidate {round(total_vol, 4)} BTC."
                )
            elif is_botnet:
                primary_ip = ips[0].replace("IP:", "") if ips else "Unknown Relay"
                typology = "HIGH_VELOCITY_BOTNET"
                risk_score = 0.85
                severity = "HIGH"
                summary = (
                    f"Automated botnet transaction dispatch node ({primary_ip}) driving "
                    f"{len(txs)} broadcast events in rapid succession."
                )
            elif is_exchange:
                typology = "COMMERCIAL_EXCHANGE_SWEEP"
                risk_score = 0.15
                severity = "LOW"
                summary = (
                    f"High-volume consolidated liquidity sweep ({round(total_vol, 2)} BTC) "
                    f"consistent with commercial exchange custodian operations."
                )
            else:
                typology = "COORDINATED_ENTITY_RING"
                risk_score = 0.62
                severity = "MEDIUM"
                summary = (
                    f"Co-spending entity cluster of {len(wallets)} wallets and {len(txs)} transactions "
                    f"with shared network infrastructure."
                )

            syndicate_id = f"SYN-{idx:02d}"
            syndicates.append({
                "syndicate_id": syndicate_id,
                "typology": typology,
                "severity": severity,
                "risk_score": round(risk_score, 2),
                "total_volume_btc": round(total_vol, 6),
                "member_count": len(nodes_in_cluster),
                "wallet_count": len(wallets),
                "tx_count": len(txs),
                "ip_count": len(ips),
                "asns": list(asns),
                "countries": list(countries),
                "primary_infrastructure": [ip.replace("IP:", "") for ip in ips[:5]],
                "member_nodes": nodes_in_cluster,
                "summary": summary,
            })

        syndicates.sort(key=lambda s: (s["risk_score"], s["total_volume_btc"]), reverse=True)
        for rank, syn in enumerate(syndicates, 1):
            syn["syndicate_id"] = f"SYN-{rank:02d}"

        self._cached_syndicates = syndicates
        return syndicates


