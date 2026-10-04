"""
SIH26146 — Deterministic Synthetic Dataset Generator
Models normal Bitcoin P2P/transaction traffic and specific forensic typology scenarios:
- Peeling chains
- High-velocity burst activity
- Structuring / Fan-out & Fan-in mixing
- Fast multi-country IP hopping
- Intentional edge cases for validator verification
"""

from __future__ import annotations
import csv
import hashlib
import json
import random
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


def _hash_id(prefix: str, idx: int | str) -> str:
    """Generates a deterministic 64-character hex transaction ID or address hash."""
    raw = f"{prefix}_{idx}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _btc_address(prefix: str, idx: int) -> str:
    """Generates a realistic-looking Bitcoin address."""
    h = hashlib.sha256(f"addr_{prefix}_{idx}".encode("utf-8")).hexdigest()[:28]
    if prefix.startswith("p2pkh"):
        return f"1{h}"
    elif prefix.startswith("p2sh"):
        return f"3{h}"
    else:
        return f"bc1q{h}"


class SyntheticDatasetGenerator:
    """
    Generates controlled synthetic benchmark datasets for training, evaluation, and end-to-end testing.
    """

    def __init__(self, seed: int = 42):
        self.seed = seed
        self.rng = random.Random(seed)

    def generate_scenario_records(self, num_normal: int = 120) -> List[Dict[str, Any]]:
        """
        Generates a comprehensive dataset with normal activity and injected forensic scenarios.
        """
        records: List[Dict[str, Any]] = []
        base_time = datetime(2026, 8, 15, 10, 0, 0, tzinfo=timezone.utc)
        record_id = 1

        # -------------------------------------------------------------------------
        # 1. Normal Routine Bitcoin Transactions
        # -------------------------------------------------------------------------
        # Standard wallets, normal delays (10-30 mins), 1-2 inputs, 1-2 outputs, normal amounts
        normal_ips = [
            ("142.250.190.46", "US", "AS15169"),
            ("80.64.12.5", "DE", "AS3320"),
            ("103.21.244.10", "IN", "AS13335"),
            ("149.154.167.99", "GB", "AS62041"),
            ("89.160.20.1", "SE", "AS8473"),
        ]
        routine_wallets = [_btc_address("routine", i) for i in range(30)]

        for i in range(num_normal):
            tx_time = base_time + timedelta(seconds=i * self.rng.randint(60, 600))
            ip, country, asn = self.rng.choice(normal_ips)
            txid = _hash_id("normal_tx", i)
            in_addr = self.rng.choice(routine_wallets)
            out_addr1 = self.rng.choice(routine_wallets)
            out_addr2 = self.rng.choice(routine_wallets)
            amt = round(self.rng.uniform(0.01, 1.8), 6)
            change = round(amt * self.rng.uniform(0.1, 0.4), 6)
            spend = round(amt - change, 6)

            records.append({
                "source_row_id": record_id,
                "timestamp": tx_time.isoformat(),
                "src_ip": ip,
                "dst_ip": "198.51.100.5",  # P2P Node
                "src_port": self.rng.randint(1024, 65535),
                "dst_port": 8333,
                "txid": txid,
                "input_addresses": [in_addr],
                "output_addresses": [out_addr1, out_addr2],
                "input_amounts": [amt],
                "output_amounts": [spend, change],
                "geo_country": country,
                "asn": asn,
                "fee": round(self.rng.uniform(0.00005, 0.0003), 6),
                "script_type": "P2WPKH",
                "scenario_label": "normal",
            })
            record_id += 1

        # -------------------------------------------------------------------------
        # 2. Forensic Scenario A: Peeling Chain (Layering / Evasion)
        # -------------------------------------------------------------------------
        # Single entity peels small amounts (e.g. 0.05 BTC) to external addresses while
        # rolling remaining change forward through rapid succession of addresses.
        peel_time = base_time + timedelta(hours=5)
        current_wallet = _btc_address("peel_orig", 0)
        current_balance = 5.0
        peel_ip = "185.220.101.45"  # Suspicious / Tor exit node in DE

        for hop in range(8):
            peel_time += timedelta(seconds=self.rng.randint(15, 60))  # Rapid 15-60s transfers
            txid = _hash_id("peel_tx", hop)
            peeled_wallet = _btc_address("peeled_destination", hop)
            next_change_wallet = _btc_address("peel_change", hop)
            peel_amt = 0.4
            current_balance = round(current_balance - peel_amt - 0.0001, 6)

            records.append({
                "source_row_id": record_id,
                "timestamp": peel_time.isoformat(),
                "src_ip": peel_ip,
                "dst_ip": "198.51.100.12",
                "src_port": 49152 + hop,
                "dst_port": 8333,
                "txid": txid,
                "input_addresses": [current_wallet],
                "output_addresses": [peeled_wallet, next_change_wallet],
                "input_amounts": [round(current_balance + peel_amt + 0.0001, 6)],
                "output_amounts": [peel_amt, current_balance],
                "geo_country": "DE",
                "asn": "AS208294",
                "fee": 0.0001,
                "script_type": "P2PKH",
                "scenario_label": "peeling_chain",
            })
            current_wallet = next_change_wallet
            record_id += 1

        # -------------------------------------------------------------------------
        # 3. Forensic Scenario B: High-Velocity Burst (Automated Extraction)
        # -------------------------------------------------------------------------
        # 12 transactions from single wallet cluster within 90 seconds
        burst_time = base_time + timedelta(hours=8)
        burst_wallet = _btc_address("burst_source", 1)
        burst_ip = "193.106.30.88"

        for b in range(10):
            burst_time += timedelta(seconds=self.rng.randint(2, 8))  # 2 to 8 seconds apart!
            txid = _hash_id("burst_tx", b)
            dest = _btc_address("burst_target", b)

            records.append({
                "source_row_id": record_id,
                "timestamp": burst_time.isoformat(),
                "src_ip": burst_ip,
                "dst_ip": "198.51.100.15",
                "src_port": 52000 + b,
                "dst_port": 8333,
                "txid": txid,
                "input_addresses": [burst_wallet],
                "output_addresses": [dest],
                "input_amounts": [0.75],
                "output_amounts": [0.7498],
                "geo_country": "RU",
                "asn": "AS44050",
                "fee": 0.0002,
                "script_type": "P2SH",
                "scenario_label": "high_velocity_burst",
            })
            record_id += 1

        # -------------------------------------------------------------------------
        # 4. Forensic Scenario C: Fan-Out & Fan-In (Structuring / Mixing)
        # -------------------------------------------------------------------------
        # One wallet splits into 8 temporary addresses (fan-out), which then recombine into 1 destination (fan-in)
        structure_time = base_time + timedelta(hours=12)
        splitter_wallet = _btc_address("splitter", 99)
        temp_wallets = [_btc_address("temp_mix", i) for i in range(8)]
        tx_split = _hash_id("fan_out_tx", 1)

        # Fan-out transaction: 1 input -> 8 outputs
        records.append({
            "source_row_id": record_id,
            "timestamp": structure_time.isoformat(),
            "src_ip": "194.26.29.11",
            "dst_ip": "198.51.100.20",
            "src_port": 58900,
            "dst_port": 8333,
            "txid": tx_split,
            "input_addresses": [splitter_wallet],
            "output_addresses": temp_wallets,
            "input_amounts": [8.0],
            "output_amounts": [0.999] * 8,
            "geo_country": "CH",
            "asn": "AS51852",
            "fee": 0.008,
            "script_type": "P2WPKH",
            "scenario_label": "fan_out_structuring",
        })
        record_id += 1

        # Fan-in transaction: 8 inputs -> 1 final consolidated output
        structure_time += timedelta(minutes=15)
        tx_merge = _hash_id("fan_in_tx", 2)
        collector_wallet = _btc_address("collector", 100)

        records.append({
            "source_row_id": record_id,
            "timestamp": structure_time.isoformat(),
            "src_ip": "185.220.102.19",
            "dst_ip": "198.51.100.21",
            "src_port": 58910,
            "dst_port": 8333,
            "txid": tx_merge,
            "input_addresses": temp_wallets,
            "output_addresses": [collector_wallet],
            "input_amounts": [0.999] * 8,
            "output_amounts": [7.99],
            "geo_country": "NL",
            "asn": "AS208294",
            "fee": 0.002,
            "script_type": "P2WPKH",
            "scenario_label": "fan_in_structuring",
        })
        record_id += 1

        # -------------------------------------------------------------------------
        # 5. Forensic Scenario D: Multi-Country Rapid Hopping with IP Reuse
        # -------------------------------------------------------------------------
        hop_wallet = _btc_address("fast_hopper", 77)
        fast_ips = [
            ("185.220.101.99", "DE", "AS208294"),
            ("193.106.30.22", "RU", "AS44050"),
            ("194.26.29.77", "CH", "AS51852"),
            ("51.15.22.44", "FR", "AS12876"),
        ]
        hop_time = base_time + timedelta(hours=16)

        for h_idx, (h_ip, h_ctry, h_asn) in enumerate(fast_ips):
            hop_time += timedelta(minutes=2)  # Impossible geographical transit in 2 mins
            records.append({
                "source_row_id": record_id,
                "timestamp": hop_time.isoformat(),
                "src_ip": h_ip,
                "dst_ip": "198.51.100.30",
                "src_port": 44100 + h_idx,
                "dst_port": 8333,
                "txid": _hash_id("hop_tx", h_idx),
                "input_addresses": [hop_wallet],
                "output_addresses": [_btc_address("hop_dest", h_idx)],
                "input_amounts": [1.5],
                "output_amounts": [1.499],
                "geo_country": h_ctry,
                "asn": h_asn,
                "fee": 0.001,
                "script_type": "P2WPKH",
                "scenario_label": "rapid_geo_hopping",
            })
            record_id += 1

        # -------------------------------------------------------------------------
        # 6. Intentional Edge Cases for Data Validation Engine Checks
        # -------------------------------------------------------------------------
        # Edge case 1: Private IP address
        records.append({
            "source_row_id": record_id,
            "timestamp": (base_time + timedelta(hours=18)).isoformat(),
            "src_ip": "192.168.1.100",  # RFC 1918 Private
            "dst_ip": "10.0.0.1",
            "src_port": 8333,
            "dst_port": 8333,
            "txid": _hash_id("edge_private_ip", 1),
            "input_addresses": [_btc_address("edge", 1)],
            "output_addresses": [_btc_address("edge", 2)],
            "input_amounts": [0.1],
            "output_amounts": [0.099],
            "geo_country": None,  # Validator should resolve to PRIVATE
            "asn": None,
            "fee": 0.001,
            "script_type": "P2PKH",
            "scenario_label": "edge_private_ip",
        })
        record_id += 1

        # Edge case 2: Pure network telemetry without immediate TXID
        records.append({
            "source_row_id": record_id,
            "timestamp": (base_time + timedelta(hours=19)).isoformat(),
            "src_ip": "142.250.190.46",
            "dst_ip": "198.51.100.5",
            "src_port": 54321,
            "dst_port": 8333,
            "txid": None,  # pure telemetry observation
            "input_addresses": [],
            "output_addresses": [],
            "input_amounts": [],
            "output_amounts": [],
            "geo_country": "US",
            "asn": "AS15169",
            "fee": None,
            "script_type": None,
            "scenario_label": "pure_telemetry",
        })
        record_id += 1

        return records

    def export_csv(self, records: List[Dict[str, Any]], output_path: str | Path) -> None:
        """Exports records to a standard CSV file."""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        fieldnames = [
            "source_row_id", "timestamp", "src_ip", "dst_ip", "src_port", "dst_port",
            "txid", "input_addresses", "output_addresses", "input_amounts", "output_amounts",
            "geo_country", "asn", "fee", "script_type", "scenario_label"
        ]

        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for rec in records:
                row = dict(rec)
                # Serialize lists as semicolon delimited for clean CSV representation
                row["input_addresses"] = ";".join(row["input_addresses"]) if isinstance(row["input_addresses"], list) else row["input_addresses"]
                row["output_addresses"] = ";".join(row["output_addresses"]) if isinstance(row["output_addresses"], list) else row["output_addresses"]
                row["input_amounts"] = ";".join(map(str, row["input_amounts"])) if isinstance(row["input_amounts"], list) else row["input_amounts"]
                row["output_amounts"] = ";".join(map(str, row["output_amounts"])) if isinstance(row["output_amounts"], list) else row["output_amounts"]
                writer.writerow(row)

    def export_json(self, records: List[Dict[str, Any]], output_path: str | Path) -> None:
        """Exports records to a formatted JSON file."""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2)

    def export_xml(self, records: List[Dict[str, Any]], output_path: str | Path) -> None:
        """Exports records to a well-formed XML file."""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        root = ET.Element("records")

        for r in records:
            rec_el = ET.SubElement(root, "record")
            for k, v in r.items():
                child = ET.SubElement(rec_el, k)
                if isinstance(v, list):
                    child.text = ";".join(map(str, v))
                elif v is not None:
                    child.text = str(v)
                else:
                    child.text = ""

        tree = ET.ElementTree(root)
        ET.indent(tree, space="  ")
        tree.write(path, encoding="utf-8", xml_declaration=True)


def generate_benchmark_datasets(output_dir: str | Path = "data/synthetic") -> Dict[str, str]:
    """Generates standard CSV, JSON, and XML sample files into output_dir."""
    gen = SyntheticDatasetGenerator(seed=42)
    records = gen.generate_scenario_records(num_normal=150)
    
    out = Path(output_dir)
    csv_file = out / "transactions_sample.csv"
    json_file = out / "transactions_sample.json"
    xml_file = out / "transactions_sample.xml"

    gen.export_csv(records, csv_file)
    gen.export_json(records, json_file)
    gen.export_xml(records, xml_file)

    return {
        "csv": str(csv_file),
        "json": str(json_file),
        "xml": str(xml_file),
        "total_records": len(records),
    }


if __name__ == "__main__":
    res = generate_benchmark_datasets()
    print(f"Generated synthetic benchmark files: {res}")
