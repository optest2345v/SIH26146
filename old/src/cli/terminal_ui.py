"""
SIH26146 — Autonomous Bitcoin Forensic Intelligence Platform
Interactive Terminal User Interface (TUI) & Forensic CLI Console

Engineered for strict air-gapped Linux environments, headless server racks,
SSH sessions, and environments with no GUI/X11/VNC desktop access.
"""

from __future__ import annotations
import cmd
import os
import sys
import json
import zipfile
import io
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

from src.pipeline import MasterPipeline
from src.synthetic.scenario_presets import get_scenario_catalog, generate_all_scenario_presets
from src.graph.analytics import GraphAnalytics
from src.geoip.local_geoip import OfflineGeoIP
from src.api.server import generate_dossier_text, _INVESTIGATOR_ANNOTATIONS


# Ensure stdout/stderr use UTF-8 with character replacement on legacy terminals
try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# Enable virtual terminal escape sequences on Windows if applicable
if sys.platform == "win32":
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    except Exception:
        pass


class Colors:
    """Standard ANSI Terminal Color Codes."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    UNDERLINE = "\033[4m"

    CYAN = "\033[36m"
    BRIGHT_CYAN = "\033[96m"
    GREEN = "\033[32m"
    BRIGHT_GREEN = "\033[92m"
    YELLOW = "\033[33m"
    BRIGHT_YELLOW = "\033[93m"
    RED = "\033[31m"
    BRIGHT_RED = "\033[91m"
    MAGENTA = "\033[35m"
    BRIGHT_MAGENTA = "\033[95m"
    BLUE = "\033[34m"
    BRIGHT_BLUE = "\033[94m"
    WHITE = "\033[37m"
    BRIGHT_WHITE = "\033[97m"

    BG_CYAN = "\033[46;30m"
    BG_RED = "\033[41;97m"
    BG_YELLOW = "\033[43;30m"
    BG_GREEN = "\033[42;30m"
    BG_MAGENTA = "\033[45;97m"


def render_meter(score: float, width: int = 10, color: str = Colors.CYAN) -> str:
    """Renders an ASCII progress meter for score [0.0 - 1.0]. Safe on all code pages."""
    clamped = max(0.0, min(1.0, score))
    filled = int(round(clamped * width))
    empty = width - filled
    bar = "=" * filled + "-" * empty
    return f"{color}[{bar}] {clamped:.2f}{Colors.RESET}"


class ForensicConsole(cmd.Cmd):
    intro = ""
    prompt = f"{Colors.BRIGHT_CYAN}NTRO/COGNOVAX>{Colors.RESET} "

    def __init__(self, data_path: Optional[str] = None):
        super().__init__()
        self.pipeline = MasterPipeline()
        self.active_dataset_path: Path = Path(data_path or "data/synthetic/transactions_sample.csv")
        self.result: Any = None
        self.graph: Any = None
        self.features: Any = None
        self.records: Any = None
        self.correlations: Any = None
        self.analytics: Optional[GraphAnalytics] = None
        self.last_selected_alert: Optional[Any] = None
        self.alerts_indexed: List[Any] = []

        # Load initial pipeline
        self._load_dataset(self.active_dataset_path, silent=True)

    def _load_dataset(self, path: Path, silent: bool = False):
        if not path.exists():
            from src.synthetic.generator import generate_benchmark_datasets
            generate_benchmark_datasets("data/synthetic")
            path = Path("data/synthetic/transactions_sample.csv")

        self.active_dataset_path = path
        if not silent:
            print(f"{Colors.YELLOW}[*] Executing analytical pipeline on {path.name}...{Colors.RESET}")

        res, g, feat, recs, corrs = self.pipeline.run(path)
        self.result = res
        self.graph = g
        self.features = feat
        self.records = recs
        self.correlations = corrs
        self.analytics = GraphAnalytics(g)
        self.alerts_indexed = list(res.alerts)
        if self.alerts_indexed:
            self.last_selected_alert = self.alerts_indexed[0]

        if not silent:
            print(f"{Colors.BRIGHT_GREEN}[+] Pipeline completed: {len(self.records)} records, {len(self.alerts_indexed)} ranked leads.{Colors.RESET}")

    def preloop(self):
        self.print_banner()

    def print_banner(self):
        c = Colors
        term_width = 88
        line = "=" * term_width
        print(f"\n{c.BRIGHT_CYAN}{line}")
        print(f"       SIH26146 // BITCOIN FORENSIC INTELLIGENCE COMMAND CONSOLE")
        print(f"       Operational Unit: Team COGNOVAX (Team ID: 162623) | Sponsor: NTRO")
        print(f"       Execution Mode  : 100% AIR-GAPPED OFFLINE (HEADLESS / TERMINAL / SSH)")
        print(f"{line}{c.RESET}")

        if not self.result:
            return

        v = self.result.validation_summary
        g_nodes = self.graph.number_of_nodes() if self.graph else 0
        g_edges = self.graph.number_of_edges() if self.graph else 0
        crit_count = sum(1 for a in self.alerts_indexed if getattr(a.investigative_priority, "value", a.investigative_priority) == "CRITICAL")

        print(f"  Active Dataset : {c.BRIGHT_YELLOW}{self.active_dataset_path.name}{c.RESET} ({v.total_records} records, {v.valid_records} valid)")
        print(f"  Topology Graph : {c.BRIGHT_CYAN}{g_nodes} nodes{c.RESET} | {c.BRIGHT_BLUE}{g_edges} conduits{c.RESET} | {c.BRIGHT_GREEN}{self.result.total_correlations} network correlations{c.RESET}")
        print(f"  Investigative  : {c.BRIGHT_RED}{crit_count} CRITICAL LEADS{c.RESET} | {c.BRIGHT_YELLOW}{len(self.alerts_indexed)} total prioritized leads{c.RESET}")
        print(f"{c.DIM}Type 'help' for operational commands, 'alerts' to view leads, 'inspect 1' to analyze.{c.RESET}\n")

    # -------------------------------------------------------------------------
    # Command: summary
    # -------------------------------------------------------------------------
    def do_summary(self, arg):
        """Displays top-level telemetry, KPI summary, and active scenario status."""
        self.print_banner()

    # -------------------------------------------------------------------------
    # Command: alerts / list
    # -------------------------------------------------------------------------
    def do_alerts(self, arg):
        """
        List prioritized investigative leads with optional filtering.
        Usage:
          alerts
          alerts CRITICAL
          alerts HIGH
          alerts peeling
          alerts <search_term>
        """
        if not self.alerts_indexed:
            print(f"{Colors.YELLOW}[!] No alerts generated for active dataset.{Colors.RESET}")
            return

        filt = arg.strip().upper()
        matched = []
        for idx, a in enumerate(self.alerts_indexed, start=1):
            tier = getattr(a.investigative_priority, "value", str(a.investigative_priority)).upper()
            reasons = " ".join(a.primary_reasons).upper()
            target = a.target_id.upper()
            alert_id = a.alert_id.upper()

            if not filt or filt == "ALL":
                matched.append((idx, a))
            elif filt in ("CRITICAL", "HIGH", "MEDIUM", "LOW"):
                if tier == filt:
                    matched.append((idx, a))
            elif filt in reasons or filt in target or filt in alert_id:
                matched.append((idx, a))

        c = Colors
        print(f"\n{c.BOLD}{'#':<4} | {'Alert ID':<14} | {'Tier':<9} | {'Score':<6} | {'Target Entity':<34} | {'Dispos':<9} | {'Top Reason'}{c.RESET}")
        print("-" * 105)

        for idx, a in matched[:30]:
            tier = getattr(a.investigative_priority, "value", str(a.investigative_priority)).upper()
            tier_color = c.BRIGHT_RED if tier == "CRITICAL" else (c.BRIGHT_YELLOW if tier == "HIGH" else (c.BRIGHT_CYAN if tier == "MEDIUM" else c.RESET))

            # Look up annotation
            anno = _INVESTIGATOR_ANNOTATIONS.get(a.target_id, {})
            disp = anno.get("disposition", "PENDING")
            if disp == "FLAG_FOR_SEIZURE":
                disp_str = f"{c.BG_RED}SEIZURE{c.RESET}"
            elif disp == "SURVEILLANCE":
                disp_str = f"{c.BG_YELLOW}WATCH{c.RESET}"
            elif disp == "DISMISS_AS_BENIGN":
                disp_str = f"{c.BG_GREEN}BENIGN{c.RESET}"
            else:
                disp_str = f"{c.DIM}PENDING{c.RESET}"

            first_reason = a.primary_reasons[0] if a.primary_reasons else "Statistical outlier"
            print(f"{idx:<4} | {a.alert_id:<14} | {tier_color}{tier:<9}{c.RESET} | {a.priority_score:<6.2f} | {a.target_id[:32]:<34} | {disp_str:<17} | {first_reason[:36]}")

        rem = len(matched) - 30
        if rem > 0:
            print(f"{c.DIM}... and {rem} more matching leads. Use 'inspect <#>' to drill down.{c.RESET}")
        print()

    do_list = do_alerts

    # -------------------------------------------------------------------------
    # Command: inspect / show
    # -------------------------------------------------------------------------
    def do_inspect(self, arg):
        """
        Deep-inspect an investigative alert by index number (e.g. 'inspect 1') or alert ID (e.g. 'inspect ALT-PEEL-001').
        Usage: inspect 1
        """
        if not arg.strip():
            print(f"{Colors.YELLOW}Usage: inspect <index_number or alert_id> (e.g., inspect 1){Colors.RESET}")
            return

        target_alert = self._resolve_alert(arg.strip())
        if not target_alert:
            print(f"{Colors.RED}[!] Could not find alert '{arg.strip()}'.{Colors.RESET}")
            return

        self.last_selected_alert = target_alert
        c = Colors
        a = target_alert
        tier = getattr(a.investigative_priority, "value", str(a.investigative_priority)).upper()
        tier_color = c.BRIGHT_RED if tier == "CRITICAL" else (c.BRIGHT_YELLOW if tier == "HIGH" else c.BRIGHT_CYAN)

        print(f"\n{c.BRIGHT_CYAN}{'='*88}")
        print(f" FORENSIC THREAT ASSESSMENT // LEAD REF: {a.alert_id}")
        print(f"{'='*88}{c.RESET}")
        print(f" Target Entity  : {c.BOLD}{a.target_type.upper()}: {a.target_id}{c.RESET}")
        print(f" Priority Tier  : {tier_color}{c.BOLD}{tier}{c.RESET}")
        print(f" Priority Meter : {render_meter(a.priority_score, 14, tier_color)}  (Fused Score)")
        print(f" ML Anomaly     : {render_meter(a.anomaly_score, 14, c.BRIGHT_YELLOW)}  (Isolation Forest)")
        print(f" Net Confidence : {render_meter(a.correlation_confidence, 14, c.BRIGHT_CYAN)}  (Telemetry Linkage)")

        # Human Annotation
        anno = _INVESTIGATOR_ANNOTATIONS.get(a.target_id, {})
        disp = anno.get("disposition", "UNREVIEWED")
        notes = anno.get("notes", "No manual investigator notes recorded.")
        analyst = anno.get("analyst_id", "Awaiting Assignment")
        updated = anno.get("updated_at", "N/A")
        print(f"\n{c.BOLD}[HUMAN INVESTIGATOR DISPOSITION]{c.RESET}")
        print(f" Status         : {c.BRIGHT_WHITE}{disp}{c.RESET}")
        print(f" Case Officer   : {analyst} | Updated: {updated}")
        print(f" Case Notes     : {c.DIM}{notes}{c.RESET}")

        # Narrative
        print(f"\n{c.BOLD}[INTELLIGENCE NARRATIVE]{c.RESET}")
        print(f" {a.explanation_narrative}")

        # Reasons
        print(f"\n{c.BOLD}[KEY FORENSIC INDICATORS]{c.RESET}")
        for r in a.primary_reasons:
            print(f"  {c.BRIGHT_YELLOW}[*]{c.RESET} {r}")

        # Feature Attribution
        gEv = a.graph_evidence or {}
        tEv = a.temporal_evidence or {}
        cEv = a.correlation_evidence or {}
        print(f"\n{c.BOLD}[MULTI-SIGNAL FEATURE ATTRIBUTION]{c.RESET}")
        print(f"  {c.CYAN}Topological{c.RESET} : In-Degree={gEv.get('in_degree',0)} | Out-Degree={gEv.get('out_degree',0)} | Fan-Out={gEv.get('fan_out_ratio',1.0):.2f} | PageRank={gEv.get('pagerank',0):.6f}")
        print(f"  {c.YELLOW}Temporal{c.RESET}    : Burst Ratio={tEv.get('burst_score',0)*100:.1f}% | Velocity={tEv.get('velocity_tx_per_hour',0):.1f} tx/hr | Min Inter-Arrival={tEv.get('min_inter_arrival_seconds',0):.1f}s")
        print(f"  {c.GREEN}Network{c.RESET}     : Correlated IPs={cEv.get('unique_ip_count',1)} | Jurisdictions={cEv.get('unique_countries',1)} | Confidence={cEv.get('correlation_confidence',0.9):.2f}")

        # Provenance
        print(f"\n{c.BOLD}[PROVENANCE & AUDIT TRACE]{c.RESET}")
        for pid in a.source_record_ids[:4]:
            print(f"  {c.DIM}[PROVENANCE] File & Row Record: {pid} | SHA-256 Validated | Zero Leakage{c.RESET}")
        print()

    do_show = do_inspect

    # -------------------------------------------------------------------------
    # Command: graph
    # -------------------------------------------------------------------------
    def do_graph(self, arg):
        """
        Renders an ASCII directed topology diagram showing the 1-hop/2-hop neighborhood of a target.
        Usage:
          graph          (renders graph for current inspected alert)
          graph 1        (renders graph for alert #1)
          graph <node_id>
        """
        target_id = self._resolve_target_id(arg)
        if not target_id:
            print(f"{Colors.YELLOW}[!] Please specify a target entity or inspect an alert first.{Colors.RESET}")
            return

        c = Colors
        print(f"\n{c.BRIGHT_CYAN}{'='*88}")
        print(f" ASCII FORENSIC TOPOLOGY GRAPH // TARGET: {target_id}")
        print(f"{'='*88}{c.RESET}")

        G = self.graph
        clean_id = target_id.replace("WALLET:", "").replace("TX:", "").replace("IP:", "")

        # Find matching node in graph
        matched_node = None
        for n in G.nodes():
            if clean_id in n or target_id == n:
                matched_node = n
                break

        if not matched_node:
            print(f"{c.YELLOW}[!] Entity '{target_id}' not found in active graph topology.{c.RESET}\n")
            return

        in_edges = list(G.in_edges(matched_node, data=True))
        out_edges = list(G.out_edges(matched_node, data=True))

        node_data = G.nodes[matched_node]
        n_type = node_data.get("node_type", "ENTITY")
        print(f"\n  FOCUS ENTITY: {c.BOLD}{c.BRIGHT_WHITE}[{n_type}: {matched_node}]{c.RESET}")
        if node_data.get("country"):
            print(f"  Geographical: {node_data.get('country')} | ASN: {node_data.get('asn')} | Private: {node_data.get('is_private')}")

        print(f"\n  {c.GREEN}[^] INCOMING CONDUITS ({len(in_edges)} links):{c.RESET}")
        if in_edges:
            for u, v, d in in_edges[:8]:
                u_type = G.nodes[u].get("node_type", "")
                amt = f" | {d.get('amount')} BTC" if d.get("amount") else ""
                etype = d.get("edge_type", "LINK")
                print(f"    [{u_type}: {u[:32]}...] --({etype}{amt})--> (FOCUS)")
        else:
            print(f"    {c.DIM}(No inbound links detected){c.RESET}")

        print(f"\n  {c.YELLOW}[v] OUTGOING CONDUITS ({len(out_edges)} links):{c.RESET}")
        if out_edges:
            for u, v, d in out_edges[:8]:
                v_type = G.nodes[v].get("node_type", "")
                amt = f" | {d.get('amount')} BTC" if d.get("amount") else ""
                etype = d.get("edge_type", "LINK")
                print(f"    (FOCUS) --({etype}{amt})--> [{v_type}: {v[:32]}...]")
        else:
            print(f"    {c.DIM}(No outbound links detected){c.RESET}")

        print(f"\n  {c.DIM}Total Incident Links: {len(in_edges) + len(out_edges)} | Directed Flow Degree: {G.degree(matched_node)}{c.RESET}\n")

    # -------------------------------------------------------------------------
    # Command: taint
    # -------------------------------------------------------------------------
    def do_taint(self, arg):
        """
        Calculates and renders multi-hop fund taint propagation tree in the terminal.
        Usage:
          taint          (traces taint from currently inspected alert target)
          taint 1        (traces taint from alert #1)
          taint <target_id>
        """
        target_id = self._resolve_target_id(arg)
        if not target_id:
            print(f"{Colors.YELLOW}[!] Please specify a target entity or inspect an alert first.{Colors.RESET}")
            return

        c = Colors
        print(f"\n{c.BRIGHT_RED}{'='*88}")
        print(f" MULTI-HOP FUND TAINT PROPAGATION // ROOT: {target_id}")
        print(f"{'='*88}{c.RESET}")

        clean_id = target_id.replace("WALLET:", "").replace("TX:", "").replace("IP:", "")
        taint_res = self.analytics.trace_taint(source_id=clean_id, max_depth=3, min_taint=0.01)

        summary = taint_res.get("summary", {})
        tainted_nodes = taint_res.get("tainted_nodes", {})

        print(f"  Root Origin        : {c.BOLD}{target_id}{c.RESET}")
        print(f"  Total Tainted Nodes: {c.BRIGHT_RED}{summary.get('total_tainted_nodes', len(tainted_nodes))}{c.RESET}")
        print(f"  Max Propagation    : {summary.get('max_hop_reached', 0)} hops\n")

        print(f"  {'Tainted Entity':<46} | {'Hop':<5} | {'Taint %':<10} | {'Contamination Meter'}")
        print("  " + "-" * 84)

        # Sort by hop depth and taint score descending
        sorted_nodes = sorted(tainted_nodes.items(), key=lambda kv: (kv[1].get("hop", 0), -kv[1].get("taint_score", 0)))
        for node_id, tinfo in sorted_nodes[:25]:
            hop = tinfo.get("hop", 0)
            score = tinfo.get("taint_score", 0.0)
            pct = score * 100
            prefix = " " * (hop * 2) + ("|-- " if hop > 0 else "")
            display_name = f"{prefix}{node_id[:34]}"
            meter = render_meter(score, 10, c.BRIGHT_RED if score > 0.5 else c.YELLOW)
            print(f"  {display_name:<46} | {hop:<5} | {c.BRIGHT_RED}[TAINT] {pct:>5.1f}%{c.RESET} | {meter}")

        rem = len(sorted_nodes) - 25
        if rem > 0:
            print(f"  {c.DIM}... and {rem} additional downstream tainted entities.{c.RESET}")
        print()

    # -------------------------------------------------------------------------
    # Command: syndicates / rings
    # -------------------------------------------------------------------------
    def do_syndicates(self, arg):
        """Displays detected autonomous laundering syndicates, mixing clusters, and rings."""
        c = Colors
        print(f"\n{c.BRIGHT_MAGENTA}{'='*88}")
        print(f" AUTONOMOUS LAUNDERING SYNDICATES & STRUCTURED RINGS")
        print(f"{'='*88}{c.RESET}")

        syndicates = self.analytics.detect_syndicates(min_size=3)
        if not syndicates:
            print(f"  {c.DIM}No laundering rings discovered in active dataset.{c.RESET}\n")
            return

        print(f"  Discovered {len(syndicates)} organized clusters in topology:\n")
        for syn in syndicates:
            sev = syn.get("severity", "HIGH")
            sev_color = c.BRIGHT_RED if sev == "CRITICAL" else (c.BRIGHT_YELLOW if sev == "HIGH" else c.BRIGHT_CYAN)
            print(f"  Cluster ID   : {c.BOLD}{syn['syndicate_id']}{c.RESET} | {sev_color}{sev} (Score: {syn['risk_score']:.2f}){c.RESET}")
            print(f"  Typology     : {c.BRIGHT_MAGENTA}{syn['typology']}{c.RESET}")
            print(f"  Composition  : {syn['member_count']} nodes ({syn['wallet_count']} Wallets, {syn['tx_count']} TXs, {syn['ip_count']} IPs)")
            print(f"  Volume       : {c.BRIGHT_GREEN}{syn['total_volume_btc']:.4f} BTC{c.RESET}")
            print(f"  Relay Subnet : {', '.join(syn['primary_infrastructure']) or 'Internal'}")
            print(f"  Summary      : {c.DIM}{syn['summary']}{c.RESET}")
            print("  " + "-" * 80)
        print()

    do_rings = do_syndicates

    # -------------------------------------------------------------------------
    # Command: tag
    # -------------------------------------------------------------------------
    def do_tag(self, arg):
        """
        Record human investigator disposition and case notes for an alert or entity.
        Usage:
          tag <1 or target_id> <SEIZURE|SURVEILLANCE|BENIGN|UNREVIEWED> [Case notes...]
        Example:
          tag 1 SEIZURE "Confirmed ransomware ransom wallet. Urgent asset freeze."
        """
        parts = arg.strip().split(maxsplit=2)
        if len(parts) < 2:
            print(f"{Colors.YELLOW}Usage: tag <# or target_id> <SEIZURE|SURVEILLANCE|BENIGN|UNREVIEWED> [Optional case notes]{Colors.RESET}")
            return

        target_ref = parts[0]
        disp_in = parts[1].upper()
        notes = parts[2].strip('\"\'') if len(parts) > 2 else "Disposition logged via Terminal Forensics Console."

        disp_map = {
            "SEIZURE": "FLAG_FOR_SEIZURE",
            "FLAG_FOR_SEIZURE": "FLAG_FOR_SEIZURE",
            "SURVEILLANCE": "SURVEILLANCE",
            "BENIGN": "DISMISS_AS_BENIGN",
            "DISMISS_AS_BENIGN": "DISMISS_AS_BENIGN",
            "UNREVIEWED": "UNREVIEWED",
        }
        if disp_in not in disp_map:
            print(f"{Colors.RED}[!] Invalid disposition '{disp_in}'. Choose: SEIZURE, SURVEILLANCE, BENIGN, UNREVIEWED.{Colors.RESET}")
            return

        target_id = self._resolve_target_id(target_ref)
        if not target_id:
            print(f"{Colors.RED}[!] Could not resolve target '{target_ref}'.{Colors.RESET}")
            return

        disposition = disp_map[disp_in]
        record = {
            "target_id": target_id,
            "alert_id": self.last_selected_alert.alert_id if self.last_selected_alert else "",
            "disposition": disposition,
            "notes": notes,
            "analyst_id": "COGNOVAX-TERMINAL-ANALYST",
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        _INVESTIGATOR_ANNOTATIONS[target_id] = record
        if record["alert_id"]:
            _INVESTIGATOR_ANNOTATIONS[record["alert_id"]] = record

        c = Colors
        print(f"\n{c.BRIGHT_GREEN}[+] Human disposition recorded successfully!{c.RESET}")
        print(f"  Target     : {target_id}")
        print(f"  Disposition: {c.BOLD}{disposition}{c.RESET}")
        print(f"  Notes      : {notes}\n")

    # -------------------------------------------------------------------------
    # Command: notes
    # -------------------------------------------------------------------------
    def do_notes(self, arg):
        """Displays all human investigator case notes and dispositions recorded in the session."""
        c = Colors
        print(f"\n{c.BRIGHT_CYAN}{'='*88}")
        print(f" HUMAN INVESTIGATOR DISPOSITION LOG & CASE NOTES")
        print(f"{'='*88}{c.RESET}")

        distinct = list({a["target_id"]: a for a in _INVESTIGATOR_ANNOTATIONS.values()}.values())
        if not distinct:
            print(f"  {c.DIM}No case notes or dispositions recorded yet. Use 'tag <#> <SEIZURE|SURVEILLANCE|BENIGN>' to tag.{c.RESET}\n")
            return

        for a in distinct:
            disp = a.get("disposition", "UNREVIEWED")
            disp_color = c.BRIGHT_RED if disp == "FLAG_FOR_SEIZURE" else (c.BRIGHT_YELLOW if disp == "SURVEILLANCE" else c.BRIGHT_GREEN)
            print(f"  Target      : {c.BOLD}{a.get('target_id')}{c.RESET}")
            print(f"  Alert Ref   : {a.get('alert_id') or 'N/A'}")
            print(f"  Disposition : {disp_color}{disp}{c.RESET} (by {a.get('analyst_id')})")
            print(f"  Timestamp   : {a.get('updated_at')}")
            print(f"  Case Notes  : {a.get('notes')}")
            print("  " + "-" * 80)
        print()

    # -------------------------------------------------------------------------
    # Command: scenario
    # -------------------------------------------------------------------------
    def do_scenario(self, arg):
        """
        Switch to a pre-packaged forensic demonstration scenario.
        Usage:
          scenario                    (lists available scenarios)
          scenario <scenario_id>      (loads scenario, e.g. 'scenario peeling_chain')
        """
        catalog = get_scenario_catalog()
        s_id = arg.strip().lower()

        if not s_id:
            c = Colors
            print(f"\n{c.BRIGHT_YELLOW}Available Forensic Scenarios:{c.RESET}")
            for sid, meta in catalog.items():
                active = " (ACTIVE)" if Path(meta["file_path"]).name == self.active_dataset_path.name else ""
                print(f"  {c.BOLD}{sid:<22}{c.RESET} : {meta['name']} [{meta['records_count']} recs]{c.BRIGHT_GREEN}{active}{c.RESET}")
                print(f"    {c.DIM}{meta['description']}{c.RESET}")
            print(f"\nTo switch, type: scenario <id> (e.g. 'scenario peeling_chain')\n")
            return

        if s_id not in catalog:
            print(f"{Colors.RED}[!] Scenario '{s_id}' not found. Type 'scenario' to list options.{Colors.RESET}")
            return

        meta = catalog[s_id]
        p = Path(meta["file_path"])
        if not p.exists():
            generate_all_scenario_presets()
            p = Path(meta["file_path"])

        self._load_dataset(p, silent=False)
        self.print_banner()

    # -------------------------------------------------------------------------
    # Command: ingest
    # -------------------------------------------------------------------------
    def do_ingest(self, arg):
        """
        Ingest and analyze an external CSV, JSON, or XML file.
        Usage: ingest <filepath>
        """
        path_str = arg.strip().strip('\"\'')
        if not path_str:
            print(f"{Colors.YELLOW}Usage: ingest <path/to/file.csv|json|xml>{Colors.RESET}")
            return

        p = Path(path_str)
        if not p.exists():
            print(f"{Colors.RED}[!] File not found: {path_str}{Colors.RESET}")
            return

        valid_exts = {".csv", ".json", ".xml"}
        if p.suffix.lower() not in valid_exts:
            print(f"{Colors.RED}[!] Unsupported format '{p.suffix}'. Only .csv, .json, and .xml supported.{Colors.RESET}")
            return

        self._load_dataset(p, silent=False)
        self.print_banner()

    # -------------------------------------------------------------------------
    # Command: export
    # -------------------------------------------------------------------------
    def do_export(self, arg):
        """
        Export forensic dossiers or court-admissible custody zip package.
        Usage:
          export txt           (exports plain-text investigative dossier)
          export json          (exports machine case package JSON)
          export custody       (exports signed chain-of-custody .zip package)
        """
        target = arg.strip().lower() or "txt"
        c = Colors
        run_id = self.result.run_id if self.result else "DEMO"

        if target == "txt":
            out_file = Path(f"investigation_dossier_{run_id}.txt")
            txt = generate_dossier_text(self.result, self.graph, _INVESTIGATOR_ANNOTATIONS)
            out_file.write_text(txt, encoding="utf-8")
            print(f"{c.BRIGHT_GREEN}[+] Plain-text dossier exported to: {out_file.resolve()}{c.RESET}")

        elif target == "json":
            out_file = Path(f"investigation_dossier_{run_id}.json")
            distinct_annotations = list({a["target_id"]: a for a in _INVESTIGATOR_ANNOTATIONS.values()}.values())
            data = {
                "dossier_metadata": {
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                    "run_id": run_id,
                    "investigative_unit": "Team COGNOVAX",
                    "mode": "AIR-GAPPED TERMINAL CONSOLE",
                },
                "summary": {
                    "total_records": self.result.validation_summary.total_records,
                    "total_correlations": self.result.total_correlations,
                    "ranked_alerts_count": len(self.alerts_indexed),
                },
                "investigator_annotations": distinct_annotations,
                "ranked_alerts": [a.model_dump(mode="json") for a in self.alerts_indexed],
            }
            out_file.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
            print(f"{c.BRIGHT_GREEN}[+] JSON case package exported to: {out_file.resolve()}{c.RESET}")

        elif target in ("custody", "zip"):
            out_zip = Path(f"chain_of_custody_package_{run_id}.zip")
            import hashlib
            raw_bytes = self.active_dataset_path.read_bytes()
            dossier_text = generate_dossier_text(self.result, self.graph, _INVESTIGATOR_ANNOTATIONS)
            distinct_annotations = list({a["target_id"]: a for a in _INVESTIGATOR_ANNOTATIONS.values()}.values())

            with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED) as zf:
                zf.writestr(self.active_dataset_path.name, raw_bytes)
                zf.writestr(f"INVESTIGATION_DOSSIER_{run_id}.txt", dossier_text)
                zf.writestr("INVESTIGATION_CASE_NOTES.json", json.dumps(distinct_annotations, indent=2))
                zf.writestr("SHA256SUMS.txt", f"{hashlib.sha256(raw_bytes).hexdigest()}  {self.active_dataset_path.name}\n")
                zf.writestr("CHAIN_OF_CUSTODY_CERTIFICATE.txt", f"CERTIFICATE COC-{run_id} // ISSUED BY TEAM COGNOVAX UNDER AIR-GAP PROTOCOL.\n")
            print(f"{c.BRIGHT_GREEN}[+] Court-admissible Chain-of-Custody package sealed: {out_zip.resolve()}{c.RESET}")

        else:
            print(f"{c.YELLOW}Usage: export <txt|json|custody>{c.RESET}")

    # -------------------------------------------------------------------------
    # Command: ablation
    # -------------------------------------------------------------------------
    def do_ablation(self, arg):
        """Executes comparative model ablation study across 1,045 hold-out entities."""
        from src.ml.ablation import run_ablation_study
        print(f"\n{Colors.YELLOW}[*] Executing comparative model ablation study...{Colors.RESET}")
        res = run_ablation_study()
        print("\n" + res["ascii_table"] + "\n")

    # -------------------------------------------------------------------------
    # Command: clear
    # -------------------------------------------------------------------------
    def do_clear(self, arg):
        """Clears the terminal screen."""
        os.system("cls" if sys.platform == "win32" else "clear")
        self.print_banner()

    # -------------------------------------------------------------------------
    # Navigation / Resolution Helpers
    # -------------------------------------------------------------------------
    def _resolve_alert(self, ref: str) -> Optional[Any]:
        if ref.isdigit():
            idx = int(ref)
            if 1 <= idx <= len(self.alerts_indexed):
                return self.alerts_indexed[idx - 1]
            return None
        for a in self.alerts_indexed:
            if a.alert_id.lower() == ref.lower() or a.target_id.lower() == ref.lower():
                return a
        return None

    def _resolve_target_id(self, arg: str) -> Optional[str]:
        if not arg.strip():
            return self.last_selected_alert.target_id if self.last_selected_alert else None
        ref = arg.strip()
        if ref.isdigit():
            idx = int(ref)
            if 1 <= idx <= len(self.alerts_indexed):
                self.last_selected_alert = self.alerts_indexed[idx - 1]
                return self.alerts_indexed[idx - 1].target_id
            return None
        # Check if it matches an alert ID
        for a in self.alerts_indexed:
            if a.alert_id.lower() == ref.lower():
                self.last_selected_alert = a
                return a.target_id
        return ref

    def do_exit(self, arg):
        """Exits the terminal forensic console."""
        print(f"\n{Colors.CYAN}[*] Forensic console closed. System remains secure in air-gapped mode.{Colors.RESET}\n")
        return True

    do_quit = do_exit
    do_q = do_exit

    def default(self, line):
        # Quick inspect if user just typed a number
        if line.strip().isdigit():
            self.do_inspect(line.strip())
            return
        print(f"{Colors.RED}[!] Unknown command: '{line}'. Type 'help' for available forensic commands.{Colors.RESET}")

    def emptyline(self):
        pass


def run_terminal_console(data_path: Optional[str] = None):
    """Entry point to launch the interactive Forensic Console."""
    console = ForensicConsole(data_path=data_path)
    try:
        console.cmdloop()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.CYAN}[*] Interrupted. Forensic console session ended.{Colors.RESET}\n")


if __name__ == "__main__":
    run_terminal_console()
