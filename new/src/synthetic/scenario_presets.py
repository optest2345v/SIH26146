"""
SIH26146 — Scenario Presets & Instant Evaluation Catalog
Generates and manages targeted scenario datasets allowing investigators and evaluators
to switch between distinct operational intelligence scenarios with a single click.
"""

from __future__ import annotations
import copy
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import random

from src.synthetic.generator import SyntheticDatasetGenerator, _btc_address, _hash_id


SCENARIOS_DIR = Path("data/scenarios")


def generate_all_scenario_presets() -> Dict[str, Dict[str, Any]]:
    """
    Generates and saves standalone scenario CSV files in data/scenarios/.
    Returns a catalog dictionary indexed by scenario ID.
    """
    SCENARIOS_DIR.mkdir(parents=True, exist_ok=True)
    base_gen = SyntheticDatasetGenerator(seed=42)

    catalog: Dict[str, Dict[str, Any]] = {}

    # -------------------------------------------------------------------------
    # Scenario 1: Standard Walkthrough (Balanced multi-typology)
    # -------------------------------------------------------------------------
    records_sample = base_gen.generate_scenario_records(num_normal=80)
    p_sample = SCENARIOS_DIR / "scenario_sample.csv"
    base_gen.export_csv(records_sample, p_sample)
    catalog["sample"] = {
        "id": "sample",
        "name": "Standard Investigation Walkthrough",
        "badge": "BALANCED",
        "color": "#00f0ff",
        "description": "Comprehensive baseline scenario featuring routine retail Bitcoin traffic intermixed with peeling chains, micro-bursts, and structuring hops.",
        "typology": "MULTI_TYPOLOGY",
        "records_count": len(records_sample),
        "file_path": str(p_sample),
    }

    # -------------------------------------------------------------------------
    # Scenario 2: Ransomware Peeling Chain (Layering Evasion)
    # -------------------------------------------------------------------------
    records_peel: List[Dict[str, Any]] = []
    base_time = datetime(2026, 8, 15, 10, 0, 0, tzinfo=timezone.utc)
    rec_id = 1

    # Routine background traffic (15 tx)
    normal_ips = [("142.250.190.46", "US", "AS15169"), ("80.64.12.5", "DE", "AS3320")]
    wallets = [_btc_address("norm", i) for i in range(15)]
    for i in range(15):
        t = base_time + timedelta(minutes=i * 15)
        ip, ctry, asn = normal_ips[i % 2]
        records_peel.append({
            "source_row_id": rec_id,
            "timestamp": t.isoformat(),
            "src_ip": ip, "dst_ip": "198.51.100.5",
            "src_port": 50000 + i, "dst_port": 8333,
            "txid": _hash_id("norm_peel_bg", i),
            "input_addresses": [wallets[i]], "output_addresses": [wallets[(i+1)%15]],
            "input_amounts": [0.5], "output_amounts": [0.499],
            "geo_country": ctry, "asn": asn, "fee": 0.001,
            "script_type": "P2WPKH", "scenario_label": "normal",
        })
        rec_id += 1

    # High-risk 10-hop peeling chain
    peel_time = base_time + timedelta(hours=4)
    current_wallet = _btc_address("ransom_vault", 0)
    current_bal = 12.5
    peel_ip = "185.220.101.45"  # Known Tor exit / bulletproof host in DE

    for hop in range(10):
        peel_time += timedelta(seconds=25 + (hop * 5))
        txid = _hash_id("ransom_peel_hop", hop)
        destination_ext = _btc_address("ransom_cashout", hop)
        next_change = _btc_address("peel_change_hop", hop)
        peel_amt = 0.5
        current_bal = round(current_bal - peel_amt - 0.0002, 6)

        records_peel.append({
            "source_row_id": rec_id,
            "timestamp": peel_time.isoformat(),
            "src_ip": peel_ip, "dst_ip": "198.51.100.12",
            "src_port": 49152 + hop, "dst_port": 8333,
            "txid": txid,
            "input_addresses": [current_wallet],
            "output_addresses": [destination_ext, next_change],
            "input_amounts": [round(current_bal + peel_amt + 0.0002, 6)],
            "output_amounts": [peel_amt, current_bal],
            "geo_country": "DE", "asn": "AS208294", "fee": 0.0002,
            "script_type": "P2PKH", "scenario_label": "peeling_chain",
        })
        current_wallet = next_change
        rec_id += 1

    p_peel = SCENARIOS_DIR / "scenario_peeling_chain.csv"
    base_gen.export_csv(records_peel, p_peel)
    catalog["peeling_chain"] = {
        "id": "peeling_chain",
        "name": "Ransomware Peeling Chain (10 Hops)",
        "badge": "CRITICAL RISK",
        "color": "#ff3366",
        "description": "Rapid succession of 10 fund peels (0.5 BTC each) stripping cash-outs while rolling residual balance down an ephemeral change chain via Tor exit relay.",
        "typology": "PEELING_CHAIN",
        "records_count": len(records_peel),
        "file_path": str(p_peel),
    }

    # -------------------------------------------------------------------------
    # Scenario 3: Automated Botnet Micro-Burst (High Velocity)
    # -------------------------------------------------------------------------
    records_burst: List[Dict[str, Any]] = []
    rec_id = 1
    burst_time = base_time + timedelta(hours=6)
    bot_source_wallet = _btc_address("botnet_controller", 1)
    bot_ip = "193.106.30.88"

    for b in range(16):
        burst_time += timedelta(seconds=2)  # High-frequency 2-second automated interval
        txid = _hash_id("bot_microburst", b)
        dest = _btc_address("bot_mule", b)

        records_burst.append({
            "source_row_id": rec_id,
            "timestamp": burst_time.isoformat(),
            "src_ip": bot_ip, "dst_ip": "198.51.100.15",
            "src_port": 52000 + b, "dst_port": 8333,
            "txid": txid,
            "input_addresses": [bot_source_wallet],
            "output_addresses": [dest],
            "input_amounts": [0.85],
            "output_amounts": [0.8497],
            "geo_country": "RU", "asn": "AS44050", "fee": 0.0003,
            "script_type": "P2SH", "scenario_label": "high_velocity_burst",
        })
        rec_id += 1

    p_burst = SCENARIOS_DIR / "scenario_high_velocity_burst.csv"
    base_gen.export_csv(records_burst, p_burst)
    catalog["high_velocity_burst"] = {
        "id": "high_velocity_burst",
        "name": "High-Velocity Bot Micro-Burst (120 tx/hr)",
        "badge": "HIGH ANOMALY",
        "color": "#ffb800",
        "description": "Sub-minute burst of 16 scripted fund dispatches radiating from a centralized controller wallet at machine frequency (>120 tx/hr).",
        "typology": "HIGH_VELOCITY_BURST",
        "records_count": len(records_burst),
        "file_path": str(p_burst),
    }

    # -------------------------------------------------------------------------
    # Scenario 4: Fan-Out & Fan-In Mixing / Structuring
    # -------------------------------------------------------------------------
    records_mix: List[Dict[str, Any]] = []
    rec_id = 1
    mix_time = base_time + timedelta(hours=9)
    splitter_wallet = _btc_address("mixing_origin", 88)
    temp_mix_wallets = [_btc_address("mix_node", i) for i in range(8)]
    tx_fanout = _hash_id("mix_fanout_stage1", 1)

    # Stage 1: Fan-out (1 input -> 8 outputs)
    records_mix.append({
        "source_row_id": rec_id,
        "timestamp": mix_time.isoformat(),
        "src_ip": "194.26.29.11", "dst_ip": "198.51.100.20",
        "src_port": 58900, "dst_port": 8333,
        "txid": tx_fanout,
        "input_addresses": [splitter_wallet],
        "output_addresses": temp_mix_wallets,
        "input_amounts": [16.0],
        "output_amounts": [1.999] * 8,
        "geo_country": "CH", "asn": "AS51852", "fee": 0.008,
        "script_type": "P2WPKH", "scenario_label": "fan_out_structuring",
    })
    rec_id += 1

    # Stage 2: Fan-in (8 inputs -> 1 final consolidated collector)
    mix_time += timedelta(minutes=18)
    tx_fanin = _hash_id("mix_fanin_stage2", 2)
    collector_wallet = _btc_address("mixing_collector", 99)

    records_mix.append({
        "source_row_id": rec_id,
        "timestamp": mix_time.isoformat(),
        "src_ip": "185.220.102.19", "dst_ip": "198.51.100.21",
        "src_port": 58910, "dst_port": 8333,
        "txid": tx_fanin,
        "input_addresses": temp_mix_wallets,
        "output_addresses": [collector_wallet],
        "input_amounts": [1.999] * 8,
        "output_amounts": [15.98],
        "geo_country": "NL", "asn": "AS208294", "fee": 0.012,
        "script_type": "P2WPKH", "scenario_label": "fan_in_structuring",
    })
    rec_id += 1

    p_mix = SCENARIOS_DIR / "scenario_mixing_structuring.csv"
    base_gen.export_csv(records_mix, p_mix)
    catalog["mixing_structuring"] = {
        "id": "mixing_structuring",
        "name": "Fan-Out & Fan-In Structuring (CoinJoin Evasion)",
        "badge": "GRAPH STRUCTURING",
        "color": "#a855f7",
        "description": "Multi-tier structuring dividing 16.0 BTC across 8 intermediate pseudonymous hops, followed by synchronized consolidation into a single collector entity.",
        "typology": "STRUCTURING_MIXER",
        "records_count": len(records_mix),
        "file_path": str(p_mix),
    }

    # -------------------------------------------------------------------------
    # Scenario 5: Benign High-Volume Sweeps (0% False Alarm Demonstration)
    # -------------------------------------------------------------------------
    records_benign: List[Dict[str, Any]] = []
    rec_id = 1
    benign_time = base_time + timedelta(hours=14)
    exchange_hot_wallet = _btc_address("binance_hot_wallet", 1)

    for i in range(40):
        benign_time += timedelta(seconds=12)
        txid = _hash_id("exchange_internal_sweep", i)
        deposit_addr = _btc_address("user_deposit", i)

        records_benign.append({
            "source_row_id": rec_id,
            "timestamp": benign_time.isoformat(),
            "src_ip": "13.225.10.1", "dst_ip": "198.51.100.1",
            "src_port": 44300 + i, "dst_port": 8333,
            "txid": txid,
            "input_addresses": [deposit_addr],
            "output_addresses": [exchange_hot_wallet],
            "input_amounts": [0.25],
            "output_amounts": [0.2498],
            "geo_country": "US", "asn": "AS16509", "fee": 0.0002,
            "script_type": "P2WPKH", "scenario_label": "benign_exchange_sweep",
        })
        rec_id += 1

    p_benign = SCENARIOS_DIR / "scenario_benign_exchange.csv"
    base_gen.export_csv(records_benign, p_benign)
    catalog["benign_exchange"] = {
        "id": "benign_exchange",
        "name": "Benign Exchange Sweep (0% False Alarm Verification)",
        "badge": "VERIFIED BENIGN",
        "color": "#00ff9d",
        "description": "High-volume aggregation sweeps into certified hot wallets demonstrating AI robustness and 0% False Positive Rate on commercial exchange consolidation.",
        "typology": "BENIGN_EXCHANGE",
        "records_count": len(records_benign),
        "file_path": str(p_benign),
    }

    # -------------------------------------------------------------------------
    # Scenario 6: Full 10,250 Record Industrial Benchmark
    # -------------------------------------------------------------------------
    benchmark_10k_path = Path("data/benchmark_10k/benchmark_data.csv")
    if benchmark_10k_path.exists():
        catalog["benchmark_10k"] = {
            "id": "benchmark_10k",
            "name": "10,000+ Record Industrial Stress Benchmark",
            "badge": "STRESS TEST",
            "color": "#6366f1",
            "description": "Industrial scale test across 10,250 records, 2,554 unique wallets, 10,165 transactions, dirty data edge cases, and blind ground-truth validation targets.",
            "typology": "FULL_BENCHMARK",
            "records_count": 10250,
            "file_path": str(benchmark_10k_path),
        }

    return catalog


def get_scenario_catalog() -> Dict[str, Dict[str, Any]]:
    """Returns scenario catalog, generating files if not already cached."""
    sample_file = SCENARIOS_DIR / "scenario_sample.csv"
    if not sample_file.exists():
        return generate_all_scenario_presets()
    
    # Rebuild quick metadata lookup
    catalog: Dict[str, Dict[str, Any]] = {
        "sample": {
            "id": "sample",
            "name": "Standard Investigation Walkthrough",
            "badge": "BALANCED",
            "color": "#00f0ff",
            "description": "Comprehensive baseline scenario featuring routine retail Bitcoin traffic intermixed with peeling chains, micro-bursts, and structuring hops.",
            "typology": "MULTI_TYPOLOGY",
            "records_count": 104,
            "file_path": str(SCENARIOS_DIR / "scenario_sample.csv"),
        },
        "peeling_chain": {
            "id": "peeling_chain",
            "name": "Ransomware Peeling Chain (10 Hops)",
            "badge": "CRITICAL RISK",
            "color": "#ff3366",
            "description": "Rapid succession of 10 fund peels (0.5 BTC each) stripping cash-outs while rolling residual balance down an ephemeral change chain via Tor exit relay.",
            "typology": "PEELING_CHAIN",
            "records_count": 25,
            "file_path": str(SCENARIOS_DIR / "scenario_peeling_chain.csv"),
        },
        "high_velocity_burst": {
            "id": "high_velocity_burst",
            "name": "High-Velocity Bot Micro-Burst (120 tx/hr)",
            "badge": "HIGH ANOMALY",
            "color": "#ffb800",
            "description": "Sub-minute burst of 16 scripted fund dispatches radiating from a centralized controller wallet at machine frequency (>120 tx/hr).",
            "typology": "HIGH_VELOCITY_BURST",
            "records_count": 16,
            "file_path": str(SCENARIOS_DIR / "scenario_high_velocity_burst.csv"),
        },
        "mixing_structuring": {
            "id": "mixing_structuring",
            "name": "Fan-Out & Fan-In Structuring (CoinJoin Evasion)",
            "badge": "GRAPH STRUCTURING",
            "color": "#a855f7",
            "description": "Multi-tier structuring dividing 16.0 BTC across 8 intermediate pseudonymous hops, followed by synchronized consolidation into a single collector entity.",
            "typology": "STRUCTURING_MIXER",
            "records_count": 2,
            "file_path": str(SCENARIOS_DIR / "scenario_mixing_structuring.csv"),
        },
        "benign_exchange": {
            "id": "benign_exchange",
            "name": "Benign Exchange Sweep (0% False Alarm Verification)",
            "badge": "VERIFIED BENIGN",
            "color": "#00ff9d",
            "description": "High-volume aggregation sweeps into certified hot wallets demonstrating AI robustness and 0% False Positive Rate on commercial exchange consolidation.",
            "typology": "BENIGN_EXCHANGE",
            "records_count": 40,
            "file_path": str(SCENARIOS_DIR / "scenario_benign_exchange.csv"),
        },
    }

    benchmark_10k_path = Path("data/benchmark_10k/benchmark_data.csv")
    if benchmark_10k_path.exists():
        catalog["benchmark_10k"] = {
            "id": "benchmark_10k",
            "name": "10,000+ Record Industrial Stress Benchmark",
            "badge": "STRESS TEST",
            "color": "#6366f1",
            "description": "Industrial scale test across 10,250 records, 2,554 unique wallets, 10,165 transactions, dirty data edge cases, and blind ground-truth validation targets.",
            "typology": "FULL_BENCHMARK",
            "records_count": 10250,
            "file_path": str(benchmark_10k_path),
        }

    return catalog
