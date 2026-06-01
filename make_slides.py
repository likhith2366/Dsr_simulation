"""
DSR Simulator — Session Changes Presentation
Run:  python make_slides.py
"""
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
import os

NAVY   = RGBColor(0x1a, 0x23, 0x3a)
NAVY2  = RGBColor(0x0d, 0x17, 0x2e)
TEAL   = RGBColor(0x00, 0x96, 0x88)
ORANGE = RGBColor(0xe6, 0x5c, 0x00)
WHITE  = RGBColor(0xFF, 0xFF, 0xFF)
LGRAY  = RGBColor(0xf4, 0xf6, 0xf8)
DGRAY  = RGBColor(0x44, 0x44, 0x55)
MGRAY  = RGBColor(0xaa, 0xaa, 0xbb)
GREEN  = RGBColor(0x27, 0xae, 0x60)
RED    = RGBColor(0xc0, 0x39, 0x2b)
PURPLE = RGBColor(0x6c, 0x35, 0x8a)
AMBER  = RGBColor(0xf3, 0x9c, 0x12)

IMG  = 'training_model/output'
FOOT = "NYU Tandon  ▸  SAI Lab  ▸  DSR Multi-Agent Simulator  ▸  IEEE-13 New Network"

prs = Presentation()
prs.slide_width  = Inches(13.33)
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]


def box(sl, l, t, w, h, fill):
    s = sl.shapes.add_shape(1, Inches(l), Inches(t), Inches(w), Inches(h))
    s.fill.solid()
    s.fill.fore_color.rgb = fill
    s.line.fill.background()
    return s

def txt(sl, text, l, t, w, h, sz=14, bold=False, color=NAVY,
        align=PP_ALIGN.LEFT, italic=False):
    tb = sl.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    p  = tf.paragraphs[0]
    p.alignment = align
    rn = p.add_run()
    rn.text = text
    rn.font.size   = Pt(sz)
    rn.font.bold   = bold
    rn.font.italic = italic
    rn.font.color.rgb = color
    return tb

def img(sl, path, l, t, w, h):
    if os.path.exists(path):
        sl.shapes.add_picture(path, Inches(l), Inches(t), Inches(w), Inches(h))

def footer(sl):
    txt(sl, FOOT, 0.15, 7.06, 13.0, 0.38, sz=8, color=MGRAY, align=PP_ALIGN.CENTER)

def hdr(sl, title, sub=""):
    box(sl, 0, 0, 13.33, 1.3, NAVY)
    txt(sl, title, 0.4, 0.07, 12.0, 0.72, sz=28, bold=True, color=WHITE)
    if sub:
        txt(sl, sub, 0.4, 0.74, 12.0, 0.48, sz=12, color=TEAL)
    footer(sl)

def card(sl, l, t, w, h, title, bullets, tc=TEAL, bg=WHITE, bsz=11):
    box(sl, l, t, w, h, bg)
    box(sl, l, t, 0.07, h, tc)
    txt(sl, title, l+0.16, t+0.12, w-0.22, 0.42, sz=12, bold=True, color=tc)
    y = t + 0.57
    for b in bullets:
        indent = b.startswith("  ")
        prefix = "    " if indent else "▸  "
        tb = sl.shapes.add_textbox(Inches(l+0.16), Inches(y), Inches(w-0.22), Inches(0.36))
        tf = tb.text_frame; tf.word_wrap = True
        p  = tf.paragraphs[0]
        rn = p.add_run()
        rn.text = prefix + b.lstrip()
        rn.font.size      = Pt(bsz)
        rn.font.color.rgb = MGRAY if indent else DGRAY
        y += 0.32

def dark_card(sl, l, t, w, h, title, bullets, tc=TEAL, bsz=11):
    box(sl, l, t, w, h, NAVY)
    txt(sl, title, l+0.18, t+0.12, w-0.24, 0.38, sz=12, bold=True, color=tc)
    y = t + 0.54
    for b in bullets:
        tb = sl.shapes.add_textbox(Inches(l+0.18), Inches(y), Inches(w-0.24), Inches(0.34))
        tf = tb.text_frame; tf.word_wrap = True
        p  = tf.paragraphs[0]
        rn = p.add_run()
        rn.text = f"→  {b}"
        rn.font.size      = Pt(bsz)
        rn.font.color.rgb = RGBColor(0xcc, 0xdd, 0xee)
        y += 0.32


# ═══════════════════════════════════════════════════════════════════════
# SLIDE 1 — Title
# ═══════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
box(sl, 0, 0, 13.33, 7.5, NAVY)
box(sl, 0, 5.8, 13.33, 1.7, NAVY2)
box(sl, 0, 2.0, 13.33, 0.06, TEAL)

txt(sl, "DSR Simulator — This Week's Updates",
    0.65, 2.2, 12.0, 0.95, sz=40, bold=True, color=WHITE)
txt(sl, "IEEE-13 New Network  ·  Topology, Section Logic, Switch Assumptions & Search Behaviour",
    0.65, 3.15, 12.0, 0.55, sz=18, color=TEAL)
txt(sl, "Real edge distances  ·  5-area sections  ·  Switch robustness  ·  Full outage zone coverage",
    0.65, 3.72, 12.0, 0.45, sz=14, color=MGRAY, italic=True)

for i, (val, lbl) in enumerate([
    ("5",  "Sections Defined"),
    ("8",  "Switches"),
    ("3",  "Agent Types"),
    ("5",  "Simulation Cases"),
]):
    bx = 0.65 + i * 3.05
    box(sl, bx, 4.45, 2.75, 1.1, RGBColor(0x22, 0x30, 0x50))
    txt(sl, val, bx, 4.50, 2.75, 0.65, sz=34, bold=True, color=TEAL, align=PP_ALIGN.CENTER)
    txt(sl, lbl, bx, 5.15, 2.75, 0.38, sz=11, color=RGBColor(0x99, 0xbb, 0xcc),
        align=PP_ALIGN.CENTER)

txt(sl, "NYU Tandon School of Engineering  ▸  SAI Lab",
    0.65, 6.22, 10.0, 0.40, sz=11, color=MGRAY)
txt(sl, "2025", 11.8, 6.22, 1.3, 0.40, sz=11, color=MGRAY, align=PP_ALIGN.RIGHT)


# ═══════════════════════════════════════════════════════════════════════
# SLIDE 2 — Full Topology (network image + before/after changes)
# ═══════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
box(sl, 0, 0, 13.33, 7.5, LGRAY)
hdr(sl, "IEEE-13 New Network — Updated Topology",
    "Current network layout after all changes  ·  Case 1 initial state")

# Network image — left 2/3
img(sl, f'{IMG}/Case1_step0.png', 0.18, 1.35, 8.6, 5.85)

# right panel — before/after
RX = 8.95
box(sl, RX, 1.38, 4.22, 5.82, WHITE)
box(sl, RX, 1.38, 0.07, 5.82, TEAL)
txt(sl, "What Changed", RX+0.16, 1.46, 3.85, 0.42, sz=13, bold=True, color=TEAL)

CHANGES = [
    (GREEN,  "TOPOLOGY", "Area5 electrical chain: N13 → V3 → V2 → V1 → S6"),
    (ORANGE, "TOPOLOGY", "V2–N12 and N9–V4: road-only (no electrical)"),
    (RED,    "TOPOLOGY", "V3–V4 road removed entirely"),
    (TEAL,   "DISTANCE", "All edge distances updated to real network values"),
    (TEAL,   "DISTANCE", "Switch-to-node distance = 0.001 km (assumed robust)"),
    (PURPLE, "SECTION",  "2 sections → 5 areas (Area1–5, one switch each)"),
    (PURPLE, "SECTION",  "V4 removed from Area3 — tie endpoint, no load"),
    (GREEN,  "FIXED",    "Node faults no longer mark adjacent switch as faulted"),
    (ORANGE, "SEARCH",   "Agents search until full restoration, not just discovery"),
    (TEAL,   "VISUAL",   "Agent paths drawn behind electrical edges"),
]

for i, (color, tag, desc) in enumerate(CHANGES):
    y = 1.98 + i * 0.478
    box(sl, RX+0.16, y, 0.82, 0.35, color)
    txt(sl, tag, RX+0.16, y+0.02, 0.82, 0.31,
        sz=7.5, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    txt(sl, desc, RX+1.04, y+0.03, 3.0, 0.31, sz=9, color=DGRAY)


# ═══════════════════════════════════════════════════════════════════════
# SLIDE 3 — Section Structure
# ═══════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
box(sl, 0, 0, 13.33, 7.5, LGRAY)
hdr(sl, "Section Structure — 5 Sections",
    "Each closed sectionalizer (S1–S5) defines a protection boundary  ·  Before: only 2 sections")

# left panel
box(sl, 0.3, 1.38, 5.8, 5.82, WHITE)
box(sl, 0.3, 1.38, 0.07, 5.82, NAVY)
txt(sl, "Before vs After", 0.48, 1.46, 5.4, 0.42, sz=13, bold=True, color=NAVY)

lines = [
    ("BEFORE — only 2 sections defined:", ORANGE, True),
    ("  Section A: N1,N2,N6,N7,N4,N5  →  S1 trips (total blackout)", DGRAY, False),
    ("  Section B: N3,N8,N9,N10–N13,V1–V3  →  S3 trips", DGRAY, False),
    ("  S2, S4, S5 had no section protection role", DGRAY, False),
    ("", DGRAY, False),
    ("AFTER — 5 areas, one per protection switch:", GREEN, True),
    ("  Area1: N2,N6,N7  →  S1 trips  →  total blackout", DGRAY, False),
    ("  Area2: N4,N5  →  S2 trips  →  Area2 dark only", DGRAY, False),
    ("  Area3: N8,N9  →  S4 trips  →  Area3 dark only", DGRAY, False),
    ("  Area4: N3,N10,N11,N12  →  S3 trips  →  Area4 dark only", DGRAY, False),
    ("  Area5: V1,V2,V3,N13  →  S5 trips  →  Area5 dark only", DGRAY, False),
    ("", DGRAY, False),
    ("Rule: fault in Area1/2 → S1 trips → total blackout", TEAL, True),
    ("  fault in Area3/4/5 → only that area goes dark", DGRAY, False),
    ("  Switch-to-node distance = 0.001 km (assumed robust)", DGRAY, False),
]
for i, (line, color, bold) in enumerate(lines):
    if line:
        txt(sl, line, 0.48, 1.92 + i*0.30, 5.4, 0.28,
            sz=11 if not bold else 12, bold=bold, color=color)

# right panel — table
box(sl, 6.35, 1.38, 6.68, 5.82, WHITE)
box(sl, 6.35, 1.38, 0.07, 5.82, TEAL)
txt(sl, "Section Breakdown", 6.53, 1.46, 6.2, 0.42, sz=13, bold=True, color=NAVY)

COL_X = [6.44, 7.55, 8.88, 10.22, 11.55]
COL_W = [1.03, 1.25,  1.26,  1.26,  1.35]
HDRS  = ["Section", "Switch\nTrips", "Nodes Affected", "Fault Scope", "Cases"]

for cx, cw, lbl in zip(COL_X, COL_W, HDRS):
    box(sl, cx, 1.96, cw - 0.06, 0.50, NAVY)
    txt(sl, lbl, cx+0.04, 1.99, cw-0.1, 0.44, sz=8.5, bold=True,
        color=WHITE, align=PP_ALIGN.CENTER)

ROWS = [
    ("Area1",  "S1",  "N2, N6, N7",          "Total blackout",  "3,4,5"),
    ("Area2",  "S2",  "N4, N5",              "Area2 dark",      "3,5"),
    ("Area3",  "S4",  "N8, N9",              "Area3 dark",      "1,4"),
    ("Area4",  "S3",  "N3,N10,N11,N12",      "Area4 dark",      "1,2"),
    ("Area5",  "S5",  "V1,V2,V3,N13",        "Area5 dark",      "2,5"),
]
ROW_COLORS = [RED, ORANGE, TEAL, PURPLE, GREEN]

for ri, (sec, sw, nodes, effect, cases) in enumerate(ROWS):
    bg = WHITE if ri % 2 == 0 else LGRAY
    for cx, cw in zip(COL_X, COL_W):
        box(sl, cx, 2.50 + ri*0.58, cw - 0.06, 0.56, bg)
    vals = [sec, sw, nodes, effect, cases]
    for ci, (cx, cw, val) in enumerate(zip(COL_X, COL_W, vals)):
        c = ROW_COLORS[ri] if ci == 0 else (RED if "blackout" in val or "dark" in val else DGRAY)
        txt(sl, val, cx+0.04, 2.53 + ri*0.58, cw-0.1, 0.50,
            sz=9, bold=(ci==0), color=c, align=PP_ALIGN.CENTER)

# callout bottom
box(sl, 6.35, 5.44, 6.68, 1.76, RGBColor(0xff, 0xf3, 0xe0))
box(sl, 6.35, 5.44, 0.07, 1.76, ORANGE)
txt(sl, "Protection Hierarchy", 6.53, 5.52, 6.2, 0.36, sz=12, bold=True, color=ORANGE)
for bi, b in enumerate([
    "S1 trips: entire grid dark (Area1 fault → total blackout)",
    "S3 trips: Area4 dark — Areas 1,2,3,5 stay live",
    "S4 trips: only Area3 (N8,N9) dark — rest stays live",
    "S5 trips: only N13 dark — rest of B stays live",
    "S2 trips: only N4, N5 dark — rest of A stays live",
]):
    txt(sl, f"▸  {b}", 6.53, 5.92 + bi*0.25, 6.2, 0.24, sz=10, color=DGRAY)


# ═══════════════════════════════════════════════════════════════════════
# SLIDE 4 — Agent Search Strategy
# ═══════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
box(sl, 0, 0, 13.33, 7.5, LGRAY)
hdr(sl, "Agent Search Strategy",
    "Greedy nearest-neighbour on Dijkstra shortest paths  ·  Shared visited state across all agents")

CW  = 4.11
GAP = 0.2
XS  = [0.3, 0.3 + CW + GAP, 0.3 + 2*(CW + GAP)]

card(sl, XS[0], 1.38, CW, 3.2,
     "Scout — Pure Discovery", [
         "Finds nearest unvisited node in outage zone",
         "Uses Dijkstra on TGraph (road network)",
         "Marks node visited on arrival → picks next",
         "Shares global_visited with all RCs",
         "Speed: 10 km/h — fastest agent",
         "Never repairs — only discovers faults",
         "Keeps searching until full grid restoration",
     ], tc=TEAL)

card(sl, XS[1], 1.38, CW, 3.2,
     "RC — Repair + Search", [
         "Priority 1: move to discovered active fault → repair",
         "Priority 2: if no known fault → search like Scout",
         "  (nearest unvisited in outage zone)",
         "Redirected mid-travel when new fault discovered",
         "For edge faults: traverses cable to midpoint",
         "Respects fault capacity cap (max RCs per fault)",
         "Stops searching when resources exhausted",
     ], tc=PURPLE)

card(sl, XS[2], 1.38, CW, 3.2,
     "MPS — Backup Power", [
         "Scores every unpowered node by BFS load count",
         "Moves to node that restores the most loads",
         "Connects only when section confirmed safe:",
         "  All section nodes physically visited, AND",
         "  No active faults remain in that section",
         "Auto-disconnects when grid is restored",
         "Speed: 6–8 km/h depending on case",
     ], tc=ORANGE)

card(sl, XS[0], 4.76, CW, 2.38,
     "Shared State Mechanism", [
         "global_visited: nodes any agent has arrived at",
         "globally_claimed: nodes currently targeted",
         "outage_zones: EGraph BFS — unpowered nodes",
         "Agents only search within outage_zones",
         "Claimed nodes skipped instantly by other agents",
     ], tc=RED)

card(sl, XS[1], 4.76, CW, 2.38,
     "Path Planning (Dijkstra)", [
         "All movement uses Dijkstra on TGraph",
         "Road graph = electrical edges + shortcuts",
         "Shortcuts (road-only): V1–N7, N12–V2, N4–N8",
         "1 step = 1 hour  ·  speed in km/h",
         "Fractional movement — no snap errors",
     ], tc=GREEN)

dark_card(sl, XS[2], 4.76, CW, 2.38,
          "Key Insight", [
              "No node visited twice across all agents",
              "Search continues until full restoration —",
              "  not just until all faults discovered",
              "Complete dark-zone coverage guaranteed",
              "MPS never connects to unsafe section",
              "Extra hours = time cost of fault discovery",
          ], tc=TEAL)


# ═══════════════════════════════════════════════════════════════════════
# SLIDE 5 — Simulation Results: Extra Hours
# ═══════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
box(sl, 0, 0, 13.33, 7.5, LGRAY)
hdr(sl, "Simulation Results — Extra Hours for Unknown Faults",
    "Known faults baseline vs unknown faults  ·  All 5 cases  ·  IEEE-13 New Network")

RESULTS = [
    ("Case 1", 9,  11,  2,  "3 faults in Areas 3,4,5  ·  S3,S4,S5 trip",         TEAL),
    ("Case 2", 10, 15,  5,  "Faults in Areas 1,4,5  ·  total blackout",           GREEN),
    ("Case 3", 10, 15,  5,  "3 faults in Areas 1,2  ·  S1 trips (total blackout)",RED),
    ("Case 4", 11, 19,  8,  "Area1 feeder cut + Areas 3,4  ·  level-10 fault",    PURPLE),
    ("Case 5", 13, 29, 16,  "Area1 feeder + Areas 2,5  ·  level-10 fault",        ORANGE),
]

# header row
HX = [0.3, 2.25, 4.55, 6.85, 9.15]
HW = [1.88, 2.22, 2.22, 2.22, 4.0]
HLAB = ["Case", "Known (h)", "Unknown (h)", "Extra Hours", "Fault Scenario"]
for cx, cw, lbl in zip(HX, HW, HLAB):
    box(sl, cx, 1.38, cw - 0.06, 0.50, NAVY)
    txt(sl, lbl, cx+0.06, 1.41, cw-0.12, 0.44,
        sz=11, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

# data rows
for ri, (case, known, unknown, extra, desc, color) in enumerate(RESULTS):
    bg = WHITE if ri % 2 == 0 else LGRAY
    RY = 1.92 + ri * 0.74
    for cx, cw in zip(HX, HW):
        box(sl, cx, RY, cw - 0.06, 0.68, bg)

    # case name
    box(sl, HX[0], RY, HW[0]-0.06, 0.68, color)
    txt(sl, case, HX[0]+0.06, RY+0.13, HW[0]-0.12, 0.42,
        sz=15, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

    # known
    txt(sl, str(known), HX[1]+0.06, RY+0.13, HW[1]-0.12, 0.42,
        sz=20, bold=True, color=GREEN, align=PP_ALIGN.CENTER)

    # unknown
    txt(sl, str(unknown), HX[2]+0.06, RY+0.13, HW[2]-0.12, 0.42,
        sz=20, bold=True, color=RED, align=PP_ALIGN.CENTER)

    # extra — with bar
    max_extra = max(r[3] for r in RESULTS)
    bar_w = (extra / max_extra) * (HW[3] - 0.75)
    box(sl, HX[3]+0.06, RY+0.26, bar_w, 0.30, color)
    txt(sl, f"+{extra}h", HX[3]+0.06+bar_w+0.06, RY+0.18, 0.62, 0.38,
        sz=13, bold=True, color=color)

    # description
    txt(sl, desc, HX[4]+0.08, RY+0.18, HW[4]-0.16, 0.38, sz=10, color=DGRAY)

# summary box
SY = 1.92 + 5 * 0.74 + 0.15
box(sl, 0.3, SY, 12.73, 1.12, NAVY)
txt(sl, "Average extra hours for unknown faults:  +7.2h  across all 5 cases",
    0.5, SY+0.08, 8.0, 0.44, sz=14, bold=True, color=WHITE)
txt(sl, "Case 5 worst (+16h) — level-10 fault + wide search coverage required across all areas",
    0.5, SY+0.52, 12.3, 0.44, sz=11, color=TEAL)

footer(sl)


# ── save ──────────────────────────────────────────────────────────────
prs.save('DSR_Simulator_NYU.pptx')
print("Saved DSR_Simulator_NYU.pptx  —  5 slides")
