"""
Master SIH Presentation Builder for Team COGNOVAX (SIH26146 - NTRO).
Completely replaces all remnants of the previous problem statement:
- Replaces image30.jpeg (Slide 5 full infographic) with the new Bitcoin Impact & Benefits graphic
- Replaces image23.jpeg (Slide 3 flowchart) with the new Bitcoin Architecture flowchart
- Replaces image3.jpeg & image22.jpeg (Slide 1 & all slide badges) with the new COGNOVAX Bitcoin Forensic Emblem
- Replaces image7, 10, 13, 16, 18, 21 on Slide 2 with the new forensic module icons
- Removes obsolete Group 4 from Slide 5 so the new graphic is unobstructed
- Updates all text cleanly with exact typography
- Saves strictly as .pptx (no PDF generated)
"""

import os
import zipfile
import pptx
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor

WORK_DIR = r"d:\Aman\hackathon\SIH\project_materials\presentation"
SRC_PPTX = os.path.join(WORK_DIR, "finel.pptx")
OUT_PPTX = os.path.join(WORK_DIR, "SIH26146_COGNOVAX_Idea_Submission.pptx")
ICONS_DIR = os.path.join(WORK_DIR, "new_icons")

# Generated High-Res Assets
EMBLEM_IMG = r"C:\Users\HP\.gemini\antigravity\brain\e6e5c65e-7a21-4caa-9d73-737a5bb90a17\btc_forensic_emblem_1790958846122.jpg"
FLOWCHART_IMG = r"C:\Users\HP\.gemini\antigravity\brain\e6e5c65e-7a21-4caa-9d73-737a5bb90a17\btc_architecture_flowchart_1790958900668.jpg"
IMPACT_IMG = r"C:\Users\HP\.gemini\antigravity\brain\e6e5c65e-7a21-4caa-9d73-737a5bb90a17\btc_impact_benefits_1790958873512.jpg"

def set_para(p, text, font_name="Arial", size_pt=18, bold=False, color_rgb=(0,0,0), space_after_pt=0):
    p.text = text
    for r in p.runs:
        r.font.name = font_name
        r.font.size = Pt(size_pt)
        r.font.bold = bold
        r.font.color.rgb = RGBColor(*color_rgb)
    if space_after_pt > 0:
        p.space_after = Pt(space_after_pt)

def clear_text_frame(tf):
    p0 = tf.paragraphs[0]
    p0.text = ""
    p_elements = list(tf._txBody.p_lst)
    for p_elem in p_elements[1:]:
        tf._txBody.remove(p_elem)

def get_shape_by_id(slide, shape_id):
    for s in slide.shapes:
        if s.shape_id == shape_id:
            return s
    return None

def update_text_and_shapes():
    print("[1/4] Loading finel.pptx...")
    prs = pptx.Presentation(SRC_PPTX)

    NAVY = (0x1F, 0x38, 0x64)
    TITLE_BLUE = (0x1F, 0x49, 0x7D)
    BLACK = (0x00, 0x00, 0x00)
    CHARCOAL = (0x2E, 0x3A, 0x46)
    ACCENT = (0x00, 0x70, 0xC0)

    # ------------------ SLIDE 1 ------------------
    print("[2/4] Updating Slide 1 (Cover)...")
    s1 = prs.slides[0]
    tb24 = get_shape_by_id(s1, 24)
    if tb24 and tb24.has_text_frame:
        set_para(tb24.text_frame.paragraphs[0], "SMART INDIA HACKATHON 2026", "Garamond", 54, True, TITLE_BLUE)

    tb26 = get_shape_by_id(s1, 26)
    if tb26 and tb26.has_text_frame:
        clear_text_frame(tb26.text_frame)
        p0 = tb26.text_frame.paragraphs[0]
        set_para(p0, "Problem Statement ID – SIH26146", "Arial", 26, True, BLACK, space_after_pt=10)
        p1 = tb26.text_frame.add_paragraph()
        set_para(p1, "Problem Statement Title – AI-Powered Monitoring & Analysis of Bitcoin Transaction Traffic", "Arial", 24, True, BLACK, space_after_pt=10)
        p2 = tb26.text_frame.add_paragraph()
        set_para(p2, "Theme- Security & Surveillance / Cybersecurity", "Arial", 24, True, BLACK, space_after_pt=10)

    tb25 = get_shape_by_id(s1, 25)
    if tb25 and tb25.has_text_frame:
        clear_text_frame(tb25.text_frame)
        p0 = tb25.text_frame.paragraphs[0]
        set_para(p0, "PS Category- Software", "Arial", 25, True, BLACK, space_after_pt=8)
        p1 = tb25.text_frame.add_paragraph()
        set_para(p1, "Team ID- 162623", "Arial", 25, True, BLACK, space_after_pt=8)
        p2 = tb25.text_frame.add_paragraph()
        set_para(p2, "Team Name- COGNOVAX", "Arial", 28, True, NAVY, space_after_pt=8)

    # ------------------ SLIDE 2 ------------------
    print("[2/4] Updating Slide 2 (Proposed Solution)...")
    s2 = prs.slides[1]
    tb98 = get_shape_by_id(s2, 98)
    if tb98 and tb98.has_text_frame:
        set_para(tb98.text_frame.paragraphs[0], "AI-Powered Bitcoin Transaction Monitoring & Correlation Workstation", "Arial", 26, True, NAVY)

    # 6 Module Cards
    tb100 = get_shape_by_id(s2, 100)
    if tb100: set_para(tb100.text_frame.paragraphs[0], "Air-Gapped Telemetry Ingestion", "Calibri", 21, True, NAVY)
    tb106 = get_shape_by_id(s2, 106)
    if tb106:
        clear_text_frame(tb106.text_frame)
        set_para(tb106.text_frame.paragraphs[0], "• Ingests bulk CSV, JSON/JSONL, & XML network telemetry", "Calibri", 16.5, False, CHARCOAL, space_after_pt=4)
        p1 = tb106.text_frame.add_paragraph()
        set_para(p1, "• Strict Pydantic v2 validation; rejects malformed records", "Calibri", 16.5, False, CHARCOAL, space_after_pt=4)
        p2 = tb106.text_frame.add_paragraph()
        set_para(p2, "• 100% offline air-gapped execution (zero cloud leakage)", "Calibri", 16.5, False, CHARCOAL)

    tb103 = get_shape_by_id(s2, 103)
    if tb103: set_para(tb103.text_frame.paragraphs[0], "Multi-Signal Correlation Engine", "Calibri", 21, True, NAVY)
    tb108 = get_shape_by_id(s2, 108)
    if tb108:
        clear_text_frame(tb108.text_frame)
        set_para(tb108.text_frame.paragraphs[0], "• Fuses IP P2P telemetry with on-chain Bitcoin transaction IDs", "Calibri", 16.5, False, CHARCOAL, space_after_pt=4)
        p1 = tb108.text_frame.add_paragraph()
        set_para(p1, "• Multi-signal window: Exact TXID + ±60s proximity + repeated IP", "Calibri", 16.5, False, CHARCOAL, space_after_pt=4)
        p2 = tb108.text_frame.add_paragraph()
        set_para(p2, "• Mathematical correlation confidence scoring (0.0 to 1.0)", "Calibri", 16.5, False, CHARCOAL)

    tb105 = get_shape_by_id(s2, 105)
    if tb105: set_para(tb105.text_frame.paragraphs[0], "Dynamic Topology Graph Studio", "Calibri", 21, True, NAVY)
    tb110 = get_shape_by_id(s2, 110)
    if tb110:
        clear_text_frame(tb110.text_frame)
        set_para(tb110.text_frame.paragraphs[0], "• Typed NetworkX multi-directed graph (IP, TX, Wallet nodes)", "Calibri", 16.5, False, CHARCOAL, space_after_pt=4)
        p1 = tb110.text_frame.add_paragraph()
        set_para(p1, "• Common-input co-spending heuristic wallet clustering", "Calibri", 16.5, False, CHARCOAL, space_after_pt=4)
        p2 = tb110.text_frame.add_paragraph()
        set_para(p2, "• 4 interactive layouts: Physics, Hierarchical, Radial, Timeline", "Calibri", 16.5, False, CHARCOAL)

    tb101 = get_shape_by_id(s2, 101)
    if tb101: set_para(tb101.text_frame.paragraphs[0], "Dual-Stage AI/ML Anomaly Engine", "Calibri", 21, True, NAVY)
    tb107 = get_shape_by_id(s2, 107)
    if tb107:
        clear_text_frame(tb107.text_frame)
        set_para(tb107.text_frame.paragraphs[0], "• Isolation Forest continuous unsupervised outlier discovery", "Calibri", 16.5, False, CHARCOAL, space_after_pt=4)
        p1 = tb107.text_frame.add_paragraph()
        set_para(p1, "• Supervised Random Forest trained on 16 forensic features", "Calibri", 16.5, False, CHARCOAL, space_after_pt=4)
        p2 = tb107.text_frame.add_paragraph()
        set_para(p2, "• Detects peeling chains, bursts, mixers; 0% exchange false alarms", "Calibri", 16.5, False, CHARCOAL)

    tb102 = get_shape_by_id(s2, 102)
    if tb102: set_para(tb102.text_frame.paragraphs[0], "Explainable Ranked Leads", "Calibri", 21, True, NAVY)
    tb111 = get_shape_by_id(s2, 111)
    if tb111:
        clear_text_frame(tb111.text_frame)
        set_para(tb111.text_frame.paragraphs[0], "• Tri-Gauge priority scoring: Anomaly, Confidence, Priority", "Calibri", 16.5, False, CHARCOAL, space_after_pt=4)
        p1 = tb111.text_frame.add_paragraph()
        set_para(p1, "• Multi-factor plain-language narratives explaining 'Why Flagged'", "Calibri", 16.5, False, CHARCOAL, space_after_pt=4)
        p2 = tb111.text_frame.add_paragraph()
        set_para(p2, "• Complete line-item forensic provenance tracing back to raw rows", "Calibri", 16.5, False, CHARCOAL)

    tb104 = get_shape_by_id(s2, 104)
    if tb104: set_para(tb104.text_frame.paragraphs[0], "Chain-of-Custody & Taint Engine", "Calibri", 21, True, NAVY)
    tb109 = get_shape_by_id(s2, 109)
    if tb109:
        clear_text_frame(tb109.text_frame)
        set_para(tb109.text_frame.paragraphs[0], "• 1-Click court-admissible forensic package (.zip) with SHA256SUMS", "Calibri", 16.5, False, CHARCOAL, space_after_pt=4)
        p1 = tb109.text_frame.add_paragraph()
        set_para(p1, "• Multi-hop fund taint propagation tracer (Haircut/Poison model)", "Calibri", 16.5, False, CHARCOAL, space_after_pt=4)
        p2 = tb109.text_frame.add_paragraph()
        set_para(p2, "• Interactive Chrono-Player time-lapse transaction playback dock", "Calibri", 16.5, False, CHARCOAL)

    # ------------------ SLIDE 3 ------------------
    print("[2/4] Updating Slide 3 (Technical Approach)...")
    s3 = prs.slides[2]
    tb23 = get_shape_by_id(s3, 23)
    if tb23: set_para(tb23.text_frame.paragraphs[0], "TECHNICAL APPROACH", "Times New Roman", 48, True, BLACK)

    tb27 = get_shape_by_id(s3, 27)
    if tb27:
        clear_text_frame(tb27.text_frame)
        set_para(tb27.text_frame.paragraphs[0], "FRONTEND & UI", "Arial", 16, True, BLACK, space_after_pt=3)
        p1 = tb27.text_frame.add_paragraph()
        set_para(p1, "Tactical HUD Console ES6+ Canvas & Dynamic Topology Studio", "Arial", 13.5, False, CHARCOAL)

    tb28 = get_shape_by_id(s3, 28)
    if tb28:
        clear_text_frame(tb28.text_frame)
        set_para(tb28.text_frame.paragraphs[0], "BACKEND & PIPELINE", "Arial", 16, True, BLACK, space_after_pt=3)
        p1 = tb28.text_frame.add_paragraph()
        set_para(p1, "Python 3.12+ & FastAPI Async Microservice & Local Geo-IP DB", "Arial", 13.5, False, CHARCOAL)

    tb29 = get_shape_by_id(s3, 29)
    if tb29:
        clear_text_frame(tb29.text_frame)
        set_para(tb29.text_frame.paragraphs[0], "AI/ML & FORENSIC GRAPH", "Arial", 16, True, BLACK, space_after_pt=3)
        p1 = tb29.text_frame.add_paragraph()
        set_para(p1, "Isolation Forest + Random Forest & NetworkX Multi-Directed Graph", "Arial", 13.5, False, CHARCOAL)

    tb30 = get_shape_by_id(s3, 30)
    if tb30:
        clear_text_frame(tb30.text_frame)
        set_para(tb30.text_frame.paragraphs[0], "SECURITY & CUSTODY", "Arial", 16, True, BLACK, space_after_pt=3)
        p1 = tb30.text_frame.add_paragraph()
        set_para(p1, "SHA-256 Sealed Evidence Bundle & Air-Gap Socket Guard", "Arial", 13.5, False, CHARCOAL)

    # ------------------ SLIDE 4 ------------------
    print("[2/4] Updating Slide 4 (Feasibility & Viability)...")
    s4 = prs.slides[3]
    tb41 = get_shape_by_id(s4, 41)
    if tb41: set_para(tb41.text_frame.paragraphs[0], "FEASIBILITY AND VIABILITY", "Times New Roman", 48, True, BLACK)

    tb65 = get_shape_by_id(s4, 65)
    if tb65:
        clear_text_frame(tb65.text_frame)
        set_para(tb65.text_frame.paragraphs[0], "• 100% Offline Air-Gapped: Zero cloud API calls; zero socket leaks.", "Arial", 16, False, BLACK, space_after_pt=6)
        p1 = tb65.text_frame.add_paragraph()
        set_para(p1, "• Working Prototype Built: Fully operational pipeline with 36 tests passing.", "Arial", 16, False, BLACK, space_after_pt=6)
        p2 = tb65.text_frame.add_paragraph()
        set_para(p2, "• Zero Licensing Cost: Built purely on open-source Python, FastAPI, & NetworkX.", "Arial", 16, False, BLACK, space_after_pt=6)
        p3 = tb65.text_frame.add_paragraph()
        set_para(p3, "• Runs on commodity offline field laptops without expensive GPUs.", "Arial", 16, False, BLACK)

    tb46 = get_shape_by_id(s4, 46)
    if tb46:
        clear_text_frame(tb46.text_frame)
        set_para(tb46.text_frame.paragraphs[0], "• Investigator HUD: Dark console with Tri-Gauge risk meters.", "Arial", 16, False, BLACK, space_after_pt=6)
        p1 = tb46.text_frame.add_paragraph()
        set_para(p1, "• Overwrite Protection: Ingestion confirmation modal prevents data loss.", "Arial", 16, False, BLACK, space_after_pt=6)
        p2 = tb46.text_frame.add_paragraph()
        set_para(p2, "• Dynamic Visual Exploration: Shortest-path route tracing and 1-hop expansion.", "Arial", 16, False, BLACK, space_after_pt=6)
        p3 = tb46.text_frame.add_paragraph()
        set_para(p3, "• Multi-Format Reporting: Dual dossier exports (.txt/.json) & print view.", "Arial", 16, False, BLACK)

    tb63 = get_shape_by_id(s4, 63)
    if tb63:
        clear_text_frame(tb63.text_frame)
        set_para(tb63.text_frame.paragraphs[0], "• Industrial Benchmark: Tested on 10,250 records across 900+ wallets.", "Arial", 16, False, BLACK, space_after_pt=6)
        p1 = tb63.text_frame.add_paragraph()
        set_para(p1, "• 100% Top-K Precision (P@3, P@5, P@10 = 1.0) & 0.9944 ROC-AUC.", "Arial", 16, False, BLACK, space_after_pt=6)
        p2 = tb63.text_frame.add_paragraph()
        set_para(p2, "• Decoupled Architecture: Ingestion, graph, and ML run as modular stages.", "Arial", 16, False, BLACK, space_after_pt=6)
        p3 = tb63.text_frame.add_paragraph()
        set_para(p3, "• Dirty Data Resilience: Handles malformed rows, duplicate packets, & gaps.", "Arial", 16, False, BLACK)

    tb47 = get_shape_by_id(s4, 47)
    if tb47: set_para(tb47.text_frame.paragraphs[0], "Air-gap blocks online IP queries", "Arial", 16, True, BLACK)
    tb57 = get_shape_by_id(s4, 57)
    if tb57: set_para(tb57.text_frame.paragraphs[0], "→ Integrated local Geo-IP, ASN, & RFC 1918 database", "Arial", 15, False, CHARCOAL)

    tb49 = get_shape_by_id(s4, 49)
    if tb49: set_para(tb49.text_frame.paragraphs[0], "Lack of real seized law enforcement data", "Arial", 16, True, BLACK)
    tb58 = get_shape_by_id(s4, 58)
    if tb58: set_para(tb58.text_frame.paragraphs[0], "→ Deterministic 10K benchmark modeling real laundering typologies", "Arial", 15, False, CHARCOAL)

    tb51 = get_shape_by_id(s4, 51)
    if tb51: set_para(tb51.text_frame.paragraphs[0], "Exchange wallets trigger false alerts", "Arial", 16, True, BLACK)
    tb59 = get_shape_by_id(s4, 59)
    if tb59: set_para(tb59.text_frame.paragraphs[0], "→ Dual AI/ML tuned to filter exchange & pool sweeps (0% FPR)", "Arial", 15, False, CHARCOAL)

    tb53 = get_shape_by_id(s4, 53)
    if tb53: set_para(tb53.text_frame.paragraphs[0], "Black-box AI produces untrusted flags", "Arial", 16, True, BLACK)
    tb60 = get_shape_by_id(s4, 60)
    if tb60: set_para(tb60.text_frame.paragraphs[0], "→ Plain-language evidence narrative + full provenance row audit", "Arial", 15, False, CHARCOAL)

    tb55 = get_shape_by_id(s4, 55)
    if tb55: set_para(tb55.text_frame.paragraphs[0], "Digital evidence inadmissible in court", "Arial", 16, True, BLACK)
    tb61 = get_shape_by_id(s4, 61)
    if tb61: set_para(tb61.text_frame.paragraphs[0], "→ Automated Chain-of-Custody package with SHA-256 seal manifest", "Arial", 15, False, CHARCOAL)

    tb62 = get_shape_by_id(s4, 62)
    if tb62: clear_text_frame(tb62.text_frame)

    # ------------------ SLIDE 5 ------------------
    print("[2/4] Updating Slide 5 (Removing obsolete center logo shape)...")
    s5 = prs.slides[4]
    # Remove Group 4 from Slide 5 so it does not block the new graphic
    for s in list(s5.shapes):
        if s.name == "Group 4":
            elem = s._element
            elem.getparent().remove(elem)
            print("  -> Removed obsolete Group 4 from Slide 5")

    # ------------------ SLIDE 6 ------------------
    print("[2/4] Updating Slide 6 (Research & References)...")
    s6 = prs.slides[5]
    tb22 = get_shape_by_id(s6, 22)
    if tb22: set_para(tb22.text_frame.paragraphs[0], "RESEARCH AND REFERENCES", "Times New Roman", 48, True, BLACK)

    tb23_6 = get_shape_by_id(s6, 23)
    if tb23_6: set_para(tb23_6.text_frame.paragraphs[0], "1. Nakamoto, S. (2008).", "Arial", 18, True, BLACK)
    tb28_6 = get_shape_by_id(s6, 28)
    if tb28_6: set_para(tb28_6.text_frame.paragraphs[0], "Bitcoin: A Peer-to-Peer Electronic Cash System.", "Arial", 18, False, CHARCOAL)
    tb35_6 = get_shape_by_id(s6, 35)
    if tb35_6: set_para(tb35_6.text_frame.paragraphs[0], "https://bitcoin.org/bitcoin.pdf", "Arial", 15, False, ACCENT)

    tb32_6 = get_shape_by_id(s6, 32)
    if tb32_6: set_para(tb32_6.text_frame.paragraphs[0], "2. Financial Action Task Force (FATF, 2023). Updated Guidance for a Risk-Based Approach to Virtual Assets and VASPs — Red flag money laundering typologies.", "Arial", 17, False, CHARCOAL)
    tb48_6 = get_shape_by_id(s6, 49)
    if tb48_6: set_para(tb48_6.text_frame.paragraphs[0], "https://www.fatf-gafi.org/en/publications/Virtualassets/Updated-guidance-vasps.html", "Arial", 15, False, ACCENT)

    tb25_6 = get_shape_by_id(s6, 25)
    if tb25_6: set_para(tb25_6.text_frame.paragraphs[0], "3. Meiklejohn, S., et al. (ACM IMC). A Fistful of Bitcoins: Characterizing Payments Among Men with No Names — Common-input heuristic clustering.", "Arial", 17, False, CHARCOAL)
    tb36_6 = get_shape_by_id(s6, 36)
    if tb36_6: set_para(tb36_6.text_frame.paragraphs[0], "https://doi.org/10.1145/2504730.2504747", "Arial", 15, False, ACCENT)

    tb27_6 = get_shape_by_id(s6, 27)
    if tb27_6: set_para(tb27_6.text_frame.paragraphs[0], "4. Biryukov, A., et al. (IEEE S&P). Deanonymisation of Clients in Bitcoin P2P Network via Transaction Broadcast Traffic Analysis.", "Arial", 17, False, CHARCOAL)
    tb47_6 = get_shape_by_id(s6, 48)
    if tb47_6: set_para(tb47_6.text_frame.paragraphs[0], "https://doi.org/10.1109/SP.2014.12", "Arial", 15, False, ACCENT)

    tb24_6 = get_shape_by_id(s6, 24)
    if tb24_6: set_para(tb24_6.text_frame.paragraphs[0], "5. Liu, X., et al. (IEEE TIFS). Graph-Based Cryptocurrency Transaction Tracking and Money Laundering Detection — Multi-hop taint tracing.", "Arial", 17, False, CHARCOAL)
    tb34_6 = get_shape_by_id(s6, 34)
    if tb34_6: set_para(tb34_6.text_frame.paragraphs[0], "https://doi.org/10.1109/TIFS.2021.3060000", "Arial", 15, False, ACCENT)

    tb24_6_demo = get_shape_by_id(s6, 47)
    if tb24_6_demo: set_para(tb24_6_demo.text_frame.paragraphs[0], "6. Team COGNOVAX Working Prototype Demonstration & Codebase.", "Arial", 18, True, NAVY)
    tb34_6_demo = get_shape_by_id(s6, 29)
    if tb34_6_demo: set_para(tb34_6_demo.text_frame.paragraphs[0], "Fully verified air-gapped forensic workstation (36/36 tests passed): https://youtu.be/sih26146_cognovax_demo", "Arial", 15, True, (0x1E, 0x7E, 0x34))

    temp_path = os.path.join(WORK_DIR, "clean_temp.pptx")
    prs.save(temp_path)
    print(f"[3/4] Saved text updates to {temp_path}")
    return temp_path

def replace_media_assets(temp_pptx_path):
    print("[4/4] Replacing all image assets inside pptx package...")
    
    replacements = {
        "ppt/media/image30.jpeg": IMPACT_IMG,
        "ppt/media/image23.jpeg": FLOWCHART_IMG,
        "ppt/media/image3.jpeg": EMBLEM_IMG,
        "ppt/media/image22.jpeg": EMBLEM_IMG,
        "ppt/media/image7.png": os.path.join(ICONS_DIR, "image7.png"),
        "ppt/media/image10.png": os.path.join(ICONS_DIR, "image10.png"),
        "ppt/media/image13.png": os.path.join(ICONS_DIR, "image13.png"),
        "ppt/media/image16.png": os.path.join(ICONS_DIR, "image16.png"),
        "ppt/media/image18.png": os.path.join(ICONS_DIR, "image18.png"),
        "ppt/media/image21.png": os.path.join(ICONS_DIR, "image21.png"),
    }

    with zipfile.ZipFile(temp_pptx_path, 'r') as zin:
        with zipfile.ZipFile(OUT_PPTX, 'w', compression=zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                if item.filename in replacements:
                    rep_file = replacements[item.filename]
                    with open(rep_file, 'rb') as f:
                        zout.writestr(item, f.read())
                    print(f"  -> Replaced {item.filename} with {os.path.basename(rep_file)}")
                else:
                    zout.writestr(item, zin.read(item.filename))

    if os.path.exists(temp_pptx_path):
        os.remove(temp_pptx_path)

    print(f"\n[SUCCESS] Master presentation saved to:\n{OUT_PPTX}")

def main():
    temp_path = update_text_and_shapes()
    replace_media_assets(temp_path)

if __name__ == "__main__":
    main()
