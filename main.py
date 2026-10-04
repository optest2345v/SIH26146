"""
SIH26146 — AI-Powered Monitoring & Analysis of Bitcoin Transaction Traffic
Main CLI & Local Service Launcher
"""

import argparse
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="SIH26146 — Bitcoin Transaction & Network Forensic Intelligence Platform"
    )
    subparsers = parser.add_subparsers(dest="command", help="Operational mode")

    # Command: run
    run_parser = subparsers.add_parser("run", help="Execute end-to-end analytical pipeline on dataset(s)")
    run_parser.add_argument("--data", default="data/synthetic/transactions_sample.csv", help="Input file path (CSV, JSON, XML)")
    run_parser.add_argument("--export", default=None, help="Optional output JSON dossier path")

    # Command: serve
    serve_parser = subparsers.add_parser("serve", help="Launch local offline investigation dashboard")
    serve_parser.add_argument("--host", default="127.0.0.1", help="Host IP")
    serve_parser.add_argument("--port", type=int, default=8000, help="Port")

    # Command: generate-data
    gen_parser = subparsers.add_parser("generate-data", help="Generate synthetic forensic benchmark datasets")
    gen_parser.add_argument("--out-dir", default="data/synthetic", help="Output directory")

    # Command: generate-benchmark (10,000+ records with hidden ground truth & manifest)
    bench_parser = subparsers.add_parser("generate-benchmark", help="Generate 10,000+ record forensic benchmark with separate hidden ground truth")
    bench_parser.add_argument("--out-dir", default="data/benchmark_10k", help="Output directory")
    bench_parser.add_argument("--records", type=int, default=10250, help="Target record count")
    bench_parser.add_argument("--seed", type=int, default=42, help="Deterministic random seed")

    # Command: evaluate-benchmark / evaluate (Blind evaluation & model ablation against hidden ground truth)
    eval_parser = subparsers.add_parser("evaluate-benchmark", help="Evaluate detection pipeline against hidden ground truth")
    eval_parser.add_argument("--ablation", action="store_true", help="Execute comparative model ablation study")
    eval_parser.add_argument("--data", default="data/benchmark_10k/benchmark_data.json", help="Raw benchmark data path")
    eval_parser.add_argument("--ground-truth", default="data/benchmark_10k/ground_truth.json", help="Hidden ground truth path")
    eval_parser.add_argument("--manifest", default="data/benchmark_10k/benchmark_manifest.json", help="Benchmark manifest path")
    eval_parser.add_argument("--report", default="data/benchmark_10k/benchmark_evaluation_report.md", help="Output report path")

    eval_cmd = subparsers.add_parser("evaluate", help="Evaluate detection pipeline or run comparative ablation")
    eval_cmd.add_argument("--ablation", action="store_true", help="Execute comparative model ablation study")
    eval_cmd.add_argument("--data", default="data/benchmark_10k/benchmark_data.json", help="Raw benchmark data path")
    eval_cmd.add_argument("--ground-truth", default="data/benchmark_10k/ground_truth.json", help="Hidden ground truth path")
    eval_cmd.add_argument("--manifest", default="data/benchmark_10k/benchmark_manifest.json", help="Benchmark manifest path")
    eval_cmd.add_argument("--report", default="data/benchmark_10k/benchmark_evaluation_report.md", help="Output report path")

    # Command: console / tui (Interactive Headless Terminal Console for SSH / No VNC)
    console_parser = subparsers.add_parser("console", help="Launch interactive forensic terminal console (TUI / Headless / SSH)")
    console_parser.add_argument("--data", default="data/synthetic/transactions_sample.csv", help="Input file path")

    tui_parser = subparsers.add_parser("tui", help="Launch interactive forensic terminal console (TUI)")
    tui_parser.add_argument("--data", default="data/synthetic/transactions_sample.csv", help="Input file path")

    args = parser.parse_args()

    if args.command == "generate-data":
        from src.synthetic.generator import generate_benchmark_datasets
        res = generate_benchmark_datasets(args.out_dir)
        print(f"Generated {res['total_records']} synthetic records in CSV, JSON, and XML format at {args.out_dir}")

    elif args.command == "generate-benchmark":
        from src.synthetic.benchmark_generator import Benchmark10KGenerator
        gen = Benchmark10KGenerator(seed=args.seed, target_records=args.records)
        res = gen.export_all(args.out_dir)
        print(f"\n[+] Generated 10,000+ Forensic Benchmark ({res['total_records']} records):")
        print(f"    - Raw Data (JSON) : {res['json_data']}")
        print(f"    - Raw Data (CSV)  : {res['csv_data']}")
        print(f"    - Raw Data (XML)  : {res['xml_data']}")
        print(f"    - Hidden Truth    : {res['ground_truth']}")
        print(f"    - Manifest        : {res['manifest']}")
        print(f"    * Ground-truth file contains zero leakage and is kept hidden from detectors during test runs.\n")

    elif args.command in ("evaluate-benchmark", "evaluate"):
        if getattr(args, "ablation", False):
            from src.ml.ablation import run_ablation_study
            print(f"\n[+] Executing Architectural Model Ablation Study...")
            res = run_ablation_study(
                data_path=args.data,
                ground_truth_path=args.ground_truth,
            )
            print("\n" + res["ascii_table"])
        else:
            from src.synthetic.benchmark_evaluator import run_benchmark_evaluation
            print(f"\n[+] Executing Independent Benchmark Evaluation against hidden ground truth...")
            res = run_benchmark_evaluation(
                data_path=args.data,
                ground_truth_path=args.ground_truth,
                manifest_path=args.manifest,
                output_report_path=args.report,
            )
            print("\n" + res["scorecard"])

    elif args.command == "serve":
        import uvicorn
        print(f"Starting SIH26146 Offline Intelligence Service on http://{args.host}:{args.port}")
        uvicorn.run("src.api.server:app", host=args.host, port=args.port, reload=False)

    elif args.command in ("console", "tui"):
        from src.cli.terminal_ui import run_terminal_console
        data_path = getattr(args, "data", "data/synthetic/transactions_sample.csv")
        run_terminal_console(data_path=data_path)

    else:
        # Default or 'run'
        data_path = getattr(args, "data", "data/synthetic/transactions_sample.csv")
        p = Path(data_path)
        if not p.exists():
            print(f"Data file '{data_path}' not found. Generating default synthetic dataset...")
            from src.synthetic.generator import generate_benchmark_datasets
            generate_benchmark_datasets("data/synthetic")
            data_path = "data/synthetic/transactions_sample.csv"

        from src.pipeline import MasterPipeline
        print(f"\n=======================================================")
        print(f" SIH26146: Bitcoin Transaction & Telemetry Intelligence")
        print(f" Sponsor: National Technical Research Organisation (NTRO)")
        print(f" Runtime Mode: STRICT OFFLINE (Linux Compatible)")
        print(f"=======================================================\n")
        print(f"[+] Ingesting & Validating data from: {data_path}...")
        pipeline = MasterPipeline()
        result, graph, features, recs, corrs = pipeline.run(data_path)

        print(f"\n[+] Ingestion Audit Summary:")
        print(f"    - Total records:      {result.validation_summary.total_records}")
        print(f"    - Valid records:      {result.validation_summary.valid_records}")
        print(f"    - Quarantined:        {result.validation_summary.quarantined_records}")
        print(f"    - Source files:       {result.validation_summary.source_files}")

        print(f"\n[+] Correlation & Graph Topology:")
        print(f"    - Network correlations: {result.total_correlations}")
        print(f"    - Graph nodes:          {result.graph_summary['total_nodes']} ({result.graph_summary['node_type_counts']})")
        print(f"    - Graph edges:          {result.graph_summary['total_edges']} ({result.graph_summary['edge_type_counts']})")

        print(f"\n[+] Model Evaluation Metrics (Scenario Holdout Benchmark):")
        for k, v in result.evaluation_metrics.get("metrics", {}).items():
            print(f"    - {k:<15}: {v}")
        for k, v in result.evaluation_metrics.get("top_k_metrics", {}).items():
            print(f"    - {k:<15}: {v}")

        print(f"\n[+] Ranked Investigative Alerts ({len(result.alerts)} leads generated):")
        print(f"{'Priority':<10} | {'Score':<6} | {'Anomaly':<7} | {'Conf':<6} | {'Target ID':<36} | {'Primary Reason'}")
        print("-" * 115)
        for a in result.alerts[:10]:
            reason = a.primary_reasons[0] if a.primary_reasons else "Statistical outlier"
            print(f"{a.investigative_priority:<10} | {a.priority_score:<6.2f} | {a.anomaly_score:<7.2f} | {a.correlation_confidence:<6.2f} | {a.target_id[:34]:<36} | {reason[:45]}")

        if args.export:
            import json
            exp_path = Path(args.export)
            exp_path.parent.mkdir(parents=True, exist_ok=True)
            with open(exp_path, "w", encoding="utf-8") as f:
                json.dump([a.model_dump() for a in result.alerts], f, indent=2, default=str)
            print(f"\n[+] Exported investigation leads to: {args.export}")

        print("\n[+] Verification Complete. To launch investigator dashboard: python main.py serve\n")


if __name__ == "__main__":
    main()
