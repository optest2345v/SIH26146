"""
SIH26146 — REST API & Dashboard Endpoints Test Suite
Fulfills REQ-012, REQ-013, Section 23.
"""

from fastapi.testclient import TestClient
from src.api.server import app


client = TestClient(app)


def test_api_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["runtime_mode"] == "STRICT_OFFLINE"


def test_serve_dashboard():
    res = client.get("/")
    assert res.status_code == 200
    assert "text/html" in res.headers["content-type"]
    assert "SIH26146" in res.text


def test_api_overview():
    res = client.get("/api/overview")
    assert res.status_code == 200
    data = res.json()
    assert data["total_records"] > 0
    assert data["total_alerts"] > 0
    assert data["graph_nodes"] > 0


def test_api_alerts_and_detail():
    res = client.get("/api/alerts")
    assert res.status_code == 200
    alerts = res.json()
    assert len(alerts) > 0

    first_alert = alerts[0]
    alert_id = first_alert["alert_id"]

    # Detail endpoint
    detail_res = client.get(f"/api/alerts/{alert_id}")
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert detail["alert_id"] == alert_id
    assert "explanation_narrative" in detail
    assert len(detail["primary_reasons"]) > 0


def test_api_graph_neighborhood():
    res = client.get("/api/alerts")
    target_id = res.json()[0]["target_id"]

    g_res = client.get(f"/api/graph/{target_id}?hops=2")
    assert g_res.status_code == 200
    g_data = g_res.json()
    assert "nodes" in g_data
    assert "edges" in g_data
    assert g_data["node_count"] > 0


def test_api_export():
    res = client.get("/api/export")
    assert res.status_code == 200
    data = res.json()
    assert "dossier_metadata" in data
    assert "ranked_alerts" in data
    assert len(data["ranked_alerts"]) > 0


def test_api_graph_expansion_and_path():
    res = client.get("/api/alerts")
    target_id = res.json()[0]["target_id"]

    # Test expand endpoint
    exp_res = client.get(f"/api/graph/{target_id}/expand?hops=1")
    assert exp_res.status_code == 200
    exp_data = exp_res.json()
    assert "nodes" in exp_data
    assert "edges" in exp_data

    # Test path endpoint
    if exp_data["nodes"]:
        n2 = exp_data["nodes"][0]["id"]
        path_res = client.get(f"/api/graph/path?source={target_id}&target={n2}")
        assert path_res.status_code == 200
        path_data = path_res.json()
        assert "found" in path_data


def test_api_export_text_format():
    res = client.get("/api/export?format=txt")
    assert res.status_code == 200
    assert "text/plain" in res.headers["content-type"]
    assert "INVESTIGATIVE ANALYSIS DOSSIER" in res.text
    assert "CONFIDENCE BREAKDOWN" in res.text
    assert "DATA NOTICE" in res.text
    assert "FORENSIC BOUNDARY & DISCLAIMER" in res.text


def test_api_ingest_file_extension_restriction():
    # 1. Invalid file format (.pdf) rejected with 400
    fake_pdf = ("fake_document.pdf", b"%PDF-1.4 ...", "application/pdf")
    res_bad = client.post("/api/ingest", files={"file": fake_pdf})
    assert res_bad.status_code == 400
    assert "Only .csv, .json, and .xml" in res_bad.json()["detail"]

    # 2. Invalid file format (.exe) rejected with 400
    fake_exe = ("malicious.exe", b"MZ...", "application/octet-stream")
    res_exe = client.post("/api/ingest", files={"file": fake_exe})
    assert res_exe.status_code == 400
    assert "Only .csv, .json, and .xml" in res_exe.json()["detail"]


def test_favicon_endpoint():
    res = client.get("/favicon.ico")
    assert res.status_code == 200
    assert "image/svg+xml" in res.headers["content-type"]
    assert "<svg" in res.text


def test_dataset_info_and_download():
    info_res = client.get("/api/dataset/info")
    assert info_res.status_code == 200
    info_data = info_res.json()
    assert "filename" in info_data
    assert info_data["total_records"] > 0
    assert info_data["investigative_unit"] == "Team COGNOVAX"

    down_res = client.get("/api/dataset/download")
    assert down_res.status_code == 200
    assert len(down_res.content) > 0


def test_custody_package_export():
    import zipfile
    import io
    res = client.get("/api/export/custody-package")
    assert res.status_code == 200
    assert "application/zip" in res.headers["content-type"]
    assert "attachment; filename=chain_of_custody_package_" in res.headers["content-disposition"]

    zf = zipfile.ZipFile(io.BytesIO(res.content))
    namelist = zf.namelist()
    assert any("INVESTIGATION_DOSSIER_" in n for n in namelist)
    assert any("INVESTIGATION_CASE_PACKAGE_" in n for n in namelist)
    assert "SHA256SUMS.txt" in namelist
    assert "CHAIN_OF_CUSTODY_CERTIFICATE.txt" in namelist

    cert_content = zf.read("CHAIN_OF_CUSTODY_CERTIFICATE.txt").decode("utf-8")
    assert "TEAM COGNOVAX" in cert_content
    assert "SHA-256 Seal" in cert_content


def test_taint_propagation_endpoint():
    alerts_res = client.get("/api/alerts")
    target_id = alerts_res.json()[0]["target_id"]

    taint_res = client.get(f"/api/graph/{target_id}/taint?max_depth=3")
    assert taint_res.status_code == 200
    taint_data = taint_res.json()
    assert "tainted_nodes" in taint_data
    assert "summary" in taint_data


def test_scenarios_and_entity_dossier_endpoints():
    sc_res = client.get("/api/scenarios")
    assert sc_res.status_code == 200
    sc_list = sc_res.json()
    assert len(sc_list) >= 5
    scenario_ids = [s["id"] for s in sc_list]
    assert "peeling_chain" in scenario_ids

    load_res = client.post("/api/scenarios/peeling_chain/load")
    assert load_res.status_code == 200
    load_data = load_res.json()
    assert load_data["status"] == "scenario_loaded"
    assert load_data["scenario_id"] == "peeling_chain"
    assert load_data["records_ingested"] > 0

    alerts_res = client.get("/api/alerts")
    target_id = alerts_res.json()[0]["target_id"]

    dossier_res = client.get(f"/api/entity/{target_id}/dossier")
    assert dossier_res.status_code == 200
    dossier_data = dossier_res.json()
    assert dossier_data["entity_id"] == target_id
    assert "graph_metrics" in dossier_data
    assert dossier_data["investigative_unit"] == "Team COGNOVAX"


def test_syndicates_and_intelligence_brief_endpoints():
    syn_res = client.get("/api/graph/syndicates?min_size=2")
    assert syn_res.status_code == 200
    syndicates = syn_res.json()
    assert isinstance(syndicates, list)
    if syndicates:
        s0 = syndicates[0]
        assert "syndicate_id" in s0
        assert "typology" in s0
        assert "risk_score" in s0
        assert "member_nodes" in s0

    brief_res = client.get("/api/export/intelligence-brief")
    assert brief_res.status_code == 200
    assert "text/html" in brief_res.headers["content-type"]
    assert "NATIONAL TECHNICAL RESEARCH ORGANISATION" in brief_res.text
    assert "Forensic Intelligence Case Brief" in brief_res.text
    assert "Team COGNOVAX" in brief_res.text
    assert "window.print()" in brief_res.text


def test_investigator_annotations_endpoints():
    # Save an annotation
    payload = {
        "target_id": "test_suspect_wallet_123",
        "alert_id": "ALT-2026-TEST",
        "disposition": "FLAG_FOR_SEIZURE",
        "notes": "Verified high-risk layering intermediary linked to tumbling pool.",
        "analyst_id": "COGNOVAX-LEAD-01"
    }
    post_res = client.post("/api/investigation/annotations", json=payload)
    assert post_res.status_code == 200
    p_data = post_res.json()
    assert p_data["status"] == "saved"
    assert p_data["annotation"]["disposition"] == "FLAG_FOR_SEIZURE"
    assert p_data["annotation"]["analyst_id"] == "COGNOVAX-LEAD-01"

    # Retrieve annotation
    get_res = client.get("/api/investigation/annotations?target_id=test_suspect_wallet_123")
    assert get_res.status_code == 200
    g_data = get_res.json()
    assert g_data["target_id"] == "test_suspect_wallet_123"
    assert g_data["disposition"] == "FLAG_FOR_SEIZURE"
    assert "layering intermediary" in g_data["notes"]

    # Verify dossier and custody export include the disposition
    dossier_res = client.get("/api/export?format=txt")
    assert dossier_res.status_code == 200
    assert "HUMAN INVESTIGATOR CASE NOTES & DISPOSITION LOG" in dossier_res.text
    assert "test_suspect_wallet_123" in dossier_res.text

    json_export = client.get("/api/export?format=json")
    assert json_export.status_code == 200
    j_data = json_export.json()
    assert "investigator_annotations" in j_data
    annots = j_data["investigator_annotations"]
    assert any(a["target_id"] == "test_suspect_wallet_123" for a in annots)
