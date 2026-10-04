"""
SIH26146 — Entity / Transaction Graph Test Suite
Fulfills REQ-008, Section 10, 11, 12.
"""

from datetime import datetime, timezone
from src.graph.builder import GraphBuilder
from src.graph.analytics import GraphAnalytics
from src.models.schema import NormalizedRecord, ValidationStatus


def test_graph_builder_and_analytics():
    builder = GraphBuilder()
    txid = "e" * 64
    in_w1 = "1AddrA"
    in_w2 = "1AddrB"
    out_w1 = "1AddrC"

    rec = NormalizedRecord(
        source_file_id="test.csv",
        source_row_id="1",
        timestamp=datetime.now(timezone.utc),
        src_ip="185.220.101.99",
        dst_ip="198.51.100.2",
        src_port=50000,
        dst_port=8333,
        txid=txid,
        input_addresses=[in_w1, in_w2],
        output_addresses=[out_w1],
        input_amounts=[1.0, 2.0],
        output_amounts=[2.99],
        geo_country="DE",
        asn="AS208294",
        validation_status=ValidationStatus.VALID,
    )

    G = builder.build_graph([rec])
    
    # Check node creation
    assert G.has_node("IP:185.220.101.99")
    assert G.has_node(f"TX:{txid}")
    assert G.has_node(f"WALLET:{in_w1}")
    assert G.has_node(f"WALLET:{in_w2}")
    assert G.has_node(f"WALLET:{out_w1}")

    # Check edges: IP -> TX (OBSERVED), WALLET -> TX (INPUT), TX -> WALLET (OUTPUT)
    assert G.has_edge("IP:185.220.101.99", f"TX:{txid}")
    assert G.get_edge_data("IP:185.220.101.99", f"TX:{txid}")["edge_type"] == "OBSERVED"

    assert G.has_edge(f"WALLET:{in_w1}", f"TX:{txid}")
    assert G.get_edge_data(f"WALLET:{in_w1}", f"TX:{txid}")["edge_type"] == "INPUT"

    assert G.has_edge(f"TX:{txid}", f"WALLET:{out_w1}")
    assert G.get_edge_data(f"TX:{txid}", f"WALLET:{out_w1}")["edge_type"] == "OUTPUT"

    # Check Common-Input co-spending heuristic edges between in_w1 and in_w2
    assert G.has_edge(f"WALLET:{in_w1}", f"WALLET:{in_w2}")
    assert G.get_edge_data(f"WALLET:{in_w1}", f"WALLET:{in_w2}")["edge_type"] == "COMMON_INPUT"

    # Analytics test
    analytics = GraphAnalytics(G)
    summary = analytics.get_summary()
    assert summary["total_nodes"] == 5
    assert summary["node_type_counts"]["WALLET"] == 3
    assert summary["node_type_counts"]["IP"] == 1
    assert summary["node_type_counts"]["TX"] == 1

    # Subgraph neighborhood test
    sub = analytics.extract_neighborhood(f"WALLET:{in_w1}", max_hops=1)
    assert sub["node_count"] >= 3
    assert any(n["id"] == f"TX:{txid}" for n in sub["nodes"])

    # Test dynamic node expansion
    expanded = analytics.expand_node(f"WALLET:{in_w1}", hops=1)
    assert expanded["node_count"] >= 2
    assert any(n["id"] == f"TX:{txid}" for n in expanded["nodes"])

    # Test topological path finding between IP and Output Wallet
    path_res = analytics.find_path("185.220.101.99", out_w1)
    assert path_res["found"] is True
    assert path_res["path_length"] >= 2
    assert any(n["id"] == f"TX:{txid}" for n in path_res["nodes"])

    # Test fund taint propagation
    taint_res = analytics.trace_taint(f"WALLET:{in_w1}", max_depth=3)
    assert taint_res["found"] is True
    assert taint_res["source_node"] == f"WALLET:{in_w1}"
    assert taint_res["summary"]["total_tainted_nodes"] >= 2
    assert f"TX:{txid}" in taint_res["tainted_nodes"]
    assert taint_res["tainted_nodes"][f"TX:{txid}"]["taint_score"] > 0

    # Test syndicate detection
    syndicates = analytics.detect_syndicates(min_size=2)
    assert isinstance(syndicates, list)
    assert len(syndicates) >= 1
    syn = syndicates[0]
    assert "syndicate_id" in syn
    assert "typology" in syn
    assert syn["member_count"] >= 2


