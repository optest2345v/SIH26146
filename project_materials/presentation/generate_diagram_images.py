"""
Generate high-resolution architecture diagrams, prototype showcase visuals,
and cover emblem for the official SIH 2026 presentation for Team COGNOVAX (SIH26146 - NTRO).
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

def generate_cover_emblem(output_path="sih26146_cover_emblem.png"):
    fig, ax = plt.subplots(figsize=(6.5, 6.5), dpi=300)
    fig.patch.set_facecolor('#0B132B')
    ax.set_facecolor('#0B132B')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Outer Shield / Hexagon
    poly_pts = [
        [50, 95], [88, 78], [88, 38], [50, 8], [12, 38], [12, 78]
    ]
    shield_outer = patches.Polygon(poly_pts, closed=True, facecolor='#16203B', edgecolor='#00F0FF', linewidth=3)
    ax.add_patch(shield_outer)

    # Inner Glow Hexagon
    poly_inner = [
        [50, 90], [83, 75], [83, 40], [50, 14], [17, 40], [17, 75]
    ]
    shield_inner = patches.Polygon(poly_inner, closed=True, facecolor='#0D1527', edgecolor='#10B981', linewidth=1.5, linestyle='--')
    ax.add_patch(shield_inner)

    # Header in Shield
    ax.text(50, 82, "NTRO  •  SIH 2026", ha='center', va='center', fontsize=12, fontweight='bold', color='#00F0FF', family='sans-serif')
    ax.text(50, 77, "NATIONAL TECHNICAL RESEARCH ORGANISATION", ha='center', va='center', fontsize=7.5, color='#94A3B8', family='sans-serif')

    # Central Bitcoin & Network Icon Ring
    center_circle = patches.Circle((50, 52), 16, facecolor='#0B132B', edgecolor='#F59E0B', linewidth=2.5)
    ax.add_patch(center_circle)

    # Bitcoin Text "BTC"
    ax.text(50, 51.5, "BTC", ha='center', va='center', fontsize=20, fontweight='bold', color='#F59E0B', family='sans-serif')

    # Orbiting nodes representing correlation
    orb_pts = [
        (32, 60, "IP", "#00F0FF"),
        (68, 60, "TX", "#10B981"),
        (50, 31, "GEO", "#A855F7"),
        (26, 42, "ASN", "#38BDF8"),
        (74, 42, "AI", "#EF4444")
    ]
    for ox, oy, lbl, col in orb_pts:
        ax.plot([50, ox], [52, oy], color='#334155', linewidth=1.2, linestyle=':')
        c = patches.Circle((ox, oy), 4, facecolor='#0F172A', edgecolor=col, linewidth=1.8)
        ax.add_patch(c)
        ax.text(ox, oy, lbl, ha='center', va='center', fontsize=6.5, fontweight='bold', color=col, family='sans-serif')

    # Bottom labels in shield
    ax.text(50, 24, "TEAM COGNOVAX  (ID: 162623)", ha='center', va='center', fontsize=10, fontweight='bold', color='#F8FAFC', family='sans-serif')
    ax.text(50, 19, "AIR-GAPPED FORENSIC INTELLIGENCE", ha='center', va='center', fontsize=8, fontweight='bold', color='#10B981', family='sans-serif')

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')
    plt.close()
    print(f"[SUCCESS] Cover emblem saved: {output_path}")

def generate_architecture_diagram(output_path="sih26146_architecture_diagram.png"):
    fig, ax = plt.subplots(figsize=(7.5, 10.5), dpi=300)
    fig.patch.set_facecolor('#0B132B')
    ax.set_facecolor('#0B132B')
    ax.set_xlim(0, 100)
    ax.set_ylim(100)
    ax.axis('off')

    # Title header
    ax.text(50, 97.5, "SYSTEM ARCHITECTURE & DATA PIPELINE", 
            ha='center', va='center', fontsize=15, fontweight='bold', color='#00F0FF', family='sans-serif')
    ax.text(50, 95.2, "Team COGNOVAX  |  Air-Gapped Forensic Intelligence Workstation (SIH26146)", 
            ha='center', va='center', fontsize=9, color='#94A3B8', family='sans-serif')

    boxes = [
        {
            "y": 80.5, "h": 12.0, "accent": "#00F0FF",
            "tag": "STAGE 1: AIR-GAPPED INGESTION & NORMALIZATION",
            "items": [
                "• Multi-format parsing: CSV, JSON/JSONL, XML telemetry",
                "• Pydantic v2 strict contract validation & schema enforcement",
                "• Rejects malformed records, negative amounts, & bad hashes",
                "• Local offline Geo-IP, ASN, & RFC 1918 subnet resolution"
            ],
            "badge": "ZERO SOCKET LEAKAGE"
        },
        {
            "y": 62.5, "h": 12.0, "accent": "#10B981",
            "tag": "STAGE 2: MULTI-SIGNAL CORRELATION & FUSION",
            "items": [
                "• Exact Bitcoin TXID matching with P2P broadcast events",
                "• Multi-factor proximity: ±60-second temporal propagation window",
                "• Repeated IP & ASN broadcast telemetry reinforcement",
                "• Line-item provenance linking every record to raw source rows"
            ],
            "badge": "CONFIDENCE: 0.0 - 1.0"
        },
        {
            "y": 44.5, "h": 12.0, "accent": "#A855F7",
            "tag": "STAGE 3: TOPOLOGY GRAPH & ENTITY RESOLUTION",
            "items": [
                "• NetworkX typed multi-directed graph (IP, TX, Wallet nodes)",
                "• Common-input co-spending clustering heuristics (Satoshi)",
                "• Ego-subgraph extraction, shortest paths, & route tracing",
                "• 4 Interactive layouts: Physics, Hierarchical flow, Radial, Timeline"
            ],
            "badge": "NETWORKX ENGINE"
        },
        {
            "y": 26.5, "h": 12.0, "accent": "#F59E0B",
            "tag": "STAGE 4: DUAL-STAGE AI/ML ANOMALY DETECTION",
            "items": [
                "• Unsupervised Isolation Forest: continuous anomaly scoring",
                "• Supervised Random Forest: 16 forensic behavioral features",
                "• Detects peeling chains, micro-bursts, mixers, & geo-hopping",
                "• 0% False Positives on benign exchange & mining pool sweeps"
            ],
            "badge": "DUAL AI/ML CLASSIFIER"
        },
        {
            "y": 8.5, "h": 12.0, "accent": "#38BDF8",
            "tag": "STAGE 5: EXPLAINABLE INTELLIGENCE & FORENSIC DOSSIER",
            "items": [
                "• Tri-Gauge priority scoring: Anomaly, Confidence, Priority",
                "• Multi-factor plain-language narratives explaining 'Why Flagged'",
                "• Multi-hop fund taint propagation tracer (Haircut / Poison model)",
                "• Sealed Chain-of-Custody package (.zip bundle with SHA256SUMS)"
            ],
            "badge": "COURT ADMISSIBLE"
        }
    ]

    for b in boxes:
        y, h, accent = b["y"], b["h"], b["accent"]
        rect = patches.FancyBboxPatch((5, y), 90, h, boxstyle="round,pad=0.5,rounding_size=1.2",
                                      facecolor='#16203B', edgecolor=accent, linewidth=1.5)
        ax.add_patch(rect)

        ax.text(8, y + h - 2.0, b["tag"], fontsize=10, fontweight='bold', color=accent, family='sans-serif')
        
        badge_box = patches.FancyBboxPatch((68, y + h - 2.8), 24, 2.2, boxstyle="round,pad=0.2,rounding_size=0.6",
                                           facecolor='#0F172A', edgecolor=accent, linewidth=0.8)
        ax.add_patch(badge_box)
        ax.text(80, y + h - 1.7, b["badge"], ha='center', va='center', fontsize=7.5, fontweight='bold', color=accent, family='sans-serif')

        for idx, item in enumerate(b["items"]):
            ax.text(8, y + h - 4.2 - idx * 2.0, item, fontsize=8.2, color='#E2E8F0', family='sans-serif')

    arrow_y_positions = [80.5, 62.5, 44.5, 26.5]
    for y_pos in arrow_y_positions:
        ax.annotate('', xy=(50, y_pos - 0.2), xytext=(50, y_pos + 1.2),
                    arrowprops=dict(facecolor='#00F0FF', edgecolor='#00F0FF', width=2, headwidth=7, headlength=6))

    ax.text(50, 4.0, "STRICT AIR-GAPPED LINUX & WINDOWS EXECUTION  |  10,250 BENCHMARK VERIFIED",
            ha='center', va='center', fontsize=8.5, fontweight='bold', color='#10B981', family='sans-serif')

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')
    plt.close()
    print(f"[SUCCESS] Architecture diagram saved: {output_path}")

def generate_prototype_showcase(output_path="sih26146_prototype_showcase.png"):
    fig, ax = plt.subplots(figsize=(9.5, 6.8), dpi=300)
    fig.patch.set_facecolor('#070B14')
    ax.set_facecolor('#070B14')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    header = patches.FancyBboxPatch((3, 91), 94, 7, boxstyle="round,pad=0.3,rounding_size=0.8",
                                    facecolor='#0F172A', edgecolor='#00F0FF', linewidth=1.2)
    ax.add_patch(header)
    ax.text(6, 94.5, "NTRO // COGNOVAX FORENSIC INTELLIGENCE CONSOLE", fontsize=11, fontweight='bold', color='#00F0FF', family='sans-serif')
    ax.text(94, 94.5, "AIR-GAP: VERIFIED  |  36/36 TESTS PASS", ha='right', fontsize=9, fontweight='bold', color='#10B981', family='sans-serif')

    graph_box = patches.FancyBboxPatch((3, 20), 62, 69, boxstyle="round,pad=0.4,rounding_size=1.0",
                                       facecolor='#0D1527', edgecolor='#1E293B', linewidth=1.2)
    ax.add_patch(graph_box)
    ax.text(6, 85.5, "DYNAMIC TOPOLOGY STUDIO  [PHYSICS ENGINE]", fontsize=9.5, fontweight='bold', color='#38BDF8', family='sans-serif')

    nodes = {
        "W1": (15, 68, "Wallet A\n1Synth...001", "#00F0FF", 22),
        "TX1": (32, 68, "TXID 7a3c...\n(0.85 BTC)", "#10B981", 16),
        "W2": (48, 76, "Wallet B (Mule)\n1Layer...002", "#F59E0B", 20),
        "W3": (52, 54, "Target Wallet\n[CRITICAL TAINT]", "#EF4444", 24),
        "IP1": (18, 40, "IP 192.168.1.45\n(Broadcast Node)", "#818CF8", 18),
        "TX2": (36, 44, "TXID f910...\n(Peeling Chain)", "#10B981", 16),
    }

    links = [("W1", "TX1"), ("TX1", "W2"), ("TX1", "W3"), ("IP1", "TX1"), ("IP1", "TX2"), ("TX2", "W3")]
    for src, dst in links:
        x1, y1 = nodes[src][0], nodes[src][1]
        x2, y2 = nodes[dst][0], nodes[dst][1]
        ax.plot([x1, x2], [y1, y2], color='#334155', linewidth=1.8, zorder=1)
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        ax.plot(mx, my, marker='o', markersize=5, color='#00F0FF', zorder=2)

    halo = patches.Circle((52, 54), 5.5, facecolor='none', edgecolor='#EF4444', linewidth=2.5, linestyle='--', zorder=2)
    ax.add_patch(halo)
    ax.text(52, 45.5, "85% TAINT (HAIRCUT)", ha='center', fontsize=7.5, fontweight='bold', color='#EF4444', family='sans-serif')

    for key, (x, y, label, color, sz) in nodes.items():
        circle = patches.Circle((x, y), sz * 0.16, facecolor='#0F172A', edgecolor=color, linewidth=2, zorder=3)
        ax.add_patch(circle)
        ax.text(x, y, label, ha='center', va='center', fontsize=6.5, fontweight='bold', color='#F8FAFC', family='sans-serif', zorder=4)

    chrono_box = patches.FancyBboxPatch((3, 5), 62, 13, boxstyle="round,pad=0.3,rounding_size=0.8",
                                        facecolor='#0F172A', edgecolor='#00F0FF', linewidth=1)
    ax.add_patch(chrono_box)
    ax.text(6, 14.5, "CHRONO-PLAYER (TIME-LAPSE TRANSACTION REPLAY)", fontsize=8, fontweight='bold', color='#00F0FF', family='sans-serif')
    ax.text(6, 9.5, "[▶ PLAY]   [❚❚ PAUSE]   [1x]  [2x]  [4x]", fontsize=8, fontweight='bold', color='#10B981', family='sans-serif')
    ax.plot([32, 60], [9.5, 9.5], color='#334155', linewidth=3)
    ax.plot([32, 48], [9.5, 9.5], color='#00F0FF', linewidth=3)
    ax.plot(48, 9.5, marker='o', markersize=7, color='#00F0FF')
    ax.text(53, 13.5, "T+04:12 (Step 18/24)", fontsize=7, color='#94A3B8', family='sans-serif')

    right_box = patches.FancyBboxPatch((67, 20), 30, 69, boxstyle="round,pad=0.4,rounding_size=1.0",
                                       facecolor='#0D1527', edgecolor='#1E293B', linewidth=1.2)
    ax.add_patch(right_box)
    ax.text(70, 85.5, "FORENSIC TRI-GAUGE METRICS", fontsize=9.5, fontweight='bold', color='#F59E0B', family='sans-serif')

    gauges = [
        ("PRIORITY SCORE", "0.94 / 1.00", "[CRITICAL]", "#EF4444", 76),
        ("ANOMALY SCORE", "0.89 / 1.00", "[OUTLIER]", "#F59E0B", 65),
        ("CONFIDENCE", "0.95 / 1.00", "[MULTI-SIGNAL]", "#10B981", 54),
    ]
    for label, val, status, col, gy in gauges:
        ax.text(70, gy + 4, label, fontsize=7.5, fontweight='bold', color='#94A3B8', family='sans-serif')
        ax.text(70, gy, val, fontsize=11, fontweight='bold', color=col, family='sans-serif')
        ax.text(93, gy, status, ha='right', fontsize=8, fontweight='bold', color=col, family='sans-serif')

    ax.text(70, 44, "INVESTIGATIVE NARRATIVE:", fontsize=8, fontweight='bold', color='#38BDF8', family='sans-serif')
    narrative = (
        "Target exhibits high-velocity peeling\n"
        "chain (120 tx/hr) with rapid 60s\n"
        "burst fan-out. Correlated with 3\n"
        "independent broadcast IPs across\n"
        "multiple ASNs within ±45s window."
    )
    ax.text(70, 33, narrative, fontsize=7.2, color='#E2E8F0', family='sans-serif')

    custody_box = patches.FancyBboxPatch((67, 5), 30, 13, boxstyle="round,pad=0.3,rounding_size=0.8",
                                         facecolor='#0F172A', edgecolor='#10B981', linewidth=1)
    ax.add_patch(custody_box)
    ax.text(70, 14.5, "CHAIN-OF-CUSTODY PACKAGE", fontsize=8, fontweight='bold', color='#10B981', family='sans-serif')
    ax.text(70, 10.5, "• forensic_custody_bundle.zip", fontsize=7.5, color='#F8FAFC', family='sans-serif')
    ax.text(70, 7.2, "• SHA256SUMS.txt [VERIFIED SEAL]", fontsize=7, color='#10B981', family='sans-serif')

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')
    plt.close()
    print(f"[SUCCESS] Prototype showcase saved: {output_path}")

if __name__ == "__main__":
    generate_cover_emblem()
    generate_architecture_diagram()
    generate_prototype_showcase()
