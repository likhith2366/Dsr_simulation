"""
DSR Simulator — Architecture Update Presentation
White + Blue theme, clean layout
Run:  python make_slides_arch.py
"""
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

# ── Palette: white + blue only ──────────────────────────────────
BLUE_DARK  = RGBColor(0x0d, 0x2e, 0x6e)   # header / dark bg
BLUE_MID   = RGBColor(0x15, 0x5f, 0xb5)   # accents, titles
BLUE_LIGHT = RGBColor(0xd6, 0xe4, 0xf7)   # card backgrounds
BLUE_LINE  = RGBColor(0x4a, 0x90, 0xd9)   # left-bar accent
WHITE      = RGBColor(0xFF, 0xFF, 0xFF)
OFF_WHITE  = RGBColor(0xf5, 0xf7, 0xfc)
GRAY_DARK  = RGBColor(0x22, 0x22, 0x33)   # body text
GRAY_MID   = RGBColor(0x66, 0x77, 0x88)   # secondary text
GRAY_LIGHT = RGBColor(0xdd, 0xe3, 0xee)   # dividers / alt rows
GREEN_OK   = RGBColor(0x15, 0x7a, 0x3b)   # only for "done/OK" results
RED_ERR    = RGBColor(0xaa, 0x20, 0x20)   # only for errors/bugs

FOOT = "NYU Tandon  |  SAI Lab  |  DSR Multi-Agent Simulator  |  IEEE-13 New Network"

prs = Presentation()
prs.slide_width  = Inches(13.33)
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]


# ── Primitives ──────────────────────────────────────────────────
def box(sl, l, t, w, h, fill, line_color=None):
    s = sl.shapes.add_shape(1, Inches(l), Inches(t), Inches(w), Inches(h))
    s.fill.solid()
    s.fill.fore_color.rgb = fill
    if line_color:
        s.line.color.rgb = line_color
        s.line.width = Pt(0.75)
    else:
        s.line.fill.background()
    return s

def txt(sl, text, l, t, w, h, sz=12, bold=False, color=GRAY_DARK,
        align=PP_ALIGN.LEFT, italic=False, wrap=True):
    tb = sl.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = wrap
    p  = tf.paragraphs[0]
    p.alignment = align
    rn = p.add_run()
    rn.text = text
    rn.font.size      = Pt(sz)
    rn.font.bold      = bold
    rn.font.italic    = italic
    rn.font.color.rgb = color
    return tb

def footer(sl):
    box(sl, 0, 7.22, 13.33, 0.28, BLUE_DARK)
    txt(sl, FOOT, 0.2, 7.24, 12.9, 0.22, sz=7.5, color=GRAY_LIGHT, align=PP_ALIGN.CENTER)

def slide_header(sl, title, sub=""):
    box(sl, 0, 0, 13.33, 1.18, BLUE_DARK)
    box(sl, 0, 1.18, 13.33, 0.04, BLUE_LINE)
    txt(sl, title, 0.35, 0.08, 12.6, 0.7, sz=24, bold=True, color=WHITE)
    if sub:
        txt(sl, sub, 0.35, 0.76, 12.6, 0.38, sz=10, color=GRAY_LIGHT)
    footer(sl)

def card(sl, l, t, w, h, title, body_lines, title_sz=11, body_sz=10, gap=0.3):
    """White card with blue left bar and title."""
    box(sl, l, t, w, h, WHITE, GRAY_LIGHT)
    box(sl, l, t, 0.05, h, BLUE_MID)
    txt(sl, title, l+0.14, t+0.1, w-0.2, 0.34, sz=title_sz, bold=True, color=BLUE_DARK)
    y = t + 0.48
    for line in body_lines:
        txt(sl, line, l+0.14, y, w-0.2, gap, sz=body_sz, color=GRAY_DARK)
        y += gap
    return y

def code_line(sl, text, l, t, w, h, color=BLUE_MID):
    box(sl, l, t, w, h, OFF_WHITE, GRAY_LIGHT)
    txt(sl, text, l+0.1, t+0.04, w-0.15, h-0.06, sz=9, color=color, wrap=False)


# ═══════════════════════════════════════════════════════════════
# SLIDE 1 — Title
# ═══════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
box(sl, 0, 0, 13.33, 7.5, WHITE)
box(sl, 0, 0, 13.33, 3.6, BLUE_DARK)
box(sl, 0, 3.6, 13.33, 0.06, BLUE_LINE)

txt(sl, "DSR Simulator",
    0.7, 0.55, 12.0, 1.1, sz=48, bold=True, color=WHITE)
txt(sl, "Architecture Update  —  IEEE-13 New Network",
    0.7, 1.65, 12.0, 0.55, sz=20, color=BLUE_LIGHT)
txt(sl, "Simulator / Policy Separation  ·  Multi-Agent Coordination  ·  Unknown Fault Discovery",
    0.7, 2.25, 12.0, 0.38, sz=12, color=GRAY_LIGHT, italic=True)

stats = [("2", "Core Modules"), ("6", "Policy Callbacks"), ("8", "Switches"), ("5", "Cases")]
for i, (val, lbl) in enumerate(stats):
    x = 0.7 + i * 3.0
    box(sl, x, 3.9, 2.75, 1.5, BLUE_LIGHT, GRAY_LIGHT)
    txt(sl, val, x, 3.98, 2.75, 0.75, sz=36, bold=True, color=BLUE_DARK, align=PP_ALIGN.CENTER)
    txt(sl, lbl, x, 4.72, 2.75, 0.3, sz=10, color=GRAY_MID, align=PP_ALIGN.CENTER)

txt(sl, "NYU Tandon School of Engineering  |  SAI Lab  |  2025",
    0.7, 6.8, 12.0, 0.35, sz=10, color=GRAY_MID)
footer(sl)


# ═══════════════════════════════════════════════════════════════
# SLIDE 2 — Network Overview
# ═══════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
box(sl, 0, 0, 13.33, 7.5, OFF_WHITE)
slide_header(sl, "IEEE-13 New Network — Overview",
             "5 isolated areas  |  8 sectional switches  |  4 tie nodes  |  11 loads")

areas = [
    ("Area 1 — Grid",    "Nodes: N1, N2, N3, N4, N5, N6, N7", "Always powered by main grid feeder", "Switches: S1, S2 (sectional)"),
    ("Area 2",           "Nodes: N8, N9",                      "Fault-isolated section",             "Switches: S4, S5"),
    ("Area 3",           "Nodes: N3, N10, N11, N12, N13",      "Fault-isolated section",             "Switch: S3"),
    ("Tie Nodes",        "V1, V2, V3, V4",                     "Connect areas via open tie switches", "Switches: S6, S7, S8"),
    ("Repair Crews",     "RC1 (4 km/h)  RC2 (5 km/h)",        "Move on TGraph, repair faults",      "Efficiency = 3 units/hour"),
    ("Scout + MPS",      "Scout1 (10 km/h)",                   "Discovers hidden faults by visiting", "MPS1 (8 km/h) — mobile power"),
]
for i, (title, l1, l2, l3) in enumerate(areas):
    col = i % 3
    row = i // 3
    x = 0.25 + col * 4.35
    y = 1.3 + row * 2.75
    w, h = 4.1, 2.55
    box(sl, x, y, w, h, WHITE, GRAY_LIGHT)
    box(sl, x, y, 0.05, h, BLUE_MID)
    txt(sl, title, x+0.14, y+0.1, w-0.2, 0.36, sz=12, bold=True, color=BLUE_DARK)
    txt(sl, l1, x+0.14, y+0.54, w-0.2, 0.34, sz=10, color=GRAY_DARK)
    txt(sl, l2, x+0.14, y+0.94, w-0.2, 0.34, sz=9.5, color=GRAY_MID, italic=True)
    txt(sl, l3, x+0.14, y+1.36, w-0.2, 0.34, sz=9.5, color=GRAY_DARK)


# ═══════════════════════════════════════════════════════════════
# SLIDE 3 — Architecture
# ═══════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
box(sl, 0, 0, 13.33, 7.5, OFF_WHITE)
slide_header(sl, "Architecture — Simulator / Policy Separation",
             "environment.py = pure physics  |  policy.py = all decisions  |  PolicyState = filtered view")

# LEFT panel
box(sl, 0.25, 1.3, 6.1, 5.85, WHITE, GRAY_LIGHT)
box(sl, 0.25, 1.3, 0.05, 5.85, BLUE_MID)
txt(sl, "environment.py  —  Pure Physics", 0.42, 1.38, 5.75, 0.38, sz=13, bold=True, color=BLUE_DARK)
txt(sl, "No decision logic — fires callbacks to policy", 0.42, 1.76, 5.75, 0.3, sz=9.5, color=GRAY_MID, italic=True)

env_lines = [
    ("Network power flow and load state",             GRAY_DARK),
    ("Agent movement along TGraph paths",             GRAY_DARK),
    ("Fault discovery when agent arrives",            GRAY_DARK),
    ("Switch auto-management on fault repair",        GRAY_DARK),
    ("Fires 6 callbacks to policy.py",                BLUE_MID),
    ("",                                              GRAY_DARK),
    ("PolicyState — what the policy sees:",           BLUE_DARK),
    ("  state.rcs / scouts / mps",                   GRAY_DARK),
    ("  state.discovered_faults  (found only)",       GRAY_DARK),
    ("  state.dark_nodes  (switch nodes excluded)",   GRAY_DARK),
    ("  state.switches  — open/closed only",          GRAY_DARK),
    ("  state.loads  — P, Q, W, state",               GRAY_DARK),
    ("  state.env  — action calls only",              BLUE_MID),
]
y = 2.14
for text, color in env_lines:
    if not text:
        y += 0.12; continue
    indent = text.startswith("  ")
    txt(sl, text, 0.42, y, 5.75, 0.3, sz=9.5 if indent else 10.5,
        color=GRAY_MID if indent else color)
    y += 0.31

# RIGHT panel
box(sl, 6.72, 1.3, 6.36, 5.85, BLUE_DARK, GRAY_LIGHT)
box(sl, 6.72, 1.3, 0.05, 5.85, BLUE_LINE)
txt(sl, "policy.py  —  All Decisions", 6.9, 1.38, 6.1, 0.38, sz=13, bold=True, color=WHITE)
txt(sl, "Reads PolicyState, calls actions — swappable", 6.9, 1.76, 6.1, 0.3, sz=9.5, color=GRAY_LIGHT, italic=True)

policy_lines = [
    ("6 Callbacks:",                                         WHITE),
    ("  on_setup(state, known_faults)",                     GRAY_LIGHT),
    ("  on_scout_arrived(state, scout_id, node)",           GRAY_LIGHT),
    ("  on_rc_idle(state, rc, events)",                     GRAY_LIGHT),
    ("  on_fault_discovered(state, events)",                GRAY_LIGHT),
    ("  on_mps_arrived(state, mps, node, events)",          GRAY_LIGHT),
    ("  on_mps_idle(state, mps, events)",                   GRAY_LIGHT),
    ("",                                                     WHITE),
    ("Actions via state.env:",                              WHITE),
    ("  state.env.move_rc(rc_id, node)",                   BLUE_LIGHT),
    ("  state.env.move_scout(scout_id, node)",             BLUE_LIGHT),
    ("  rc.start_repair(fault_id)",                        BLUE_LIGHT),
    ("  mps.connect() / mps.move_to(path, dist)",          BLUE_LIGHT),
    ("  state.env.open_switch / close_switch",             BLUE_LIGHT),
    ("",                                                     WHITE),
    ("Swap GreedyPolicy to LLMPolicy: zero sim changes",   BLUE_LIGHT),
]
y = 2.14
for text, color in policy_lines:
    if not text:
        y += 0.12; continue
    indent = text.startswith("  ")
    txt(sl, text, 6.9, y, 6.1, 0.3, sz=9.5 if indent else 10.5, color=color)
    y += 0.31


# ═══════════════════════════════════════════════════════════════
# SLIDE 4 — PolicyState & Fault Hiding
# ═══════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
box(sl, 0, 0, 13.33, 7.5, OFF_WHITE)
slide_header(sl, "Fix 1 + 2  —  PolicyState & Undiscovered Faults Hidden",
             "Policy sees only what was physically discovered  |  Unknown fault mode = realistic")

# LEFT
box(sl, 0.25, 1.3, 5.9, 5.85, WHITE, GRAY_LIGHT)
box(sl, 0.25, 1.3, 0.05, 5.85, BLUE_MID)
txt(sl, "PolicyState — Filtered View", 0.42, 1.38, 5.65, 0.38, sz=13, bold=True, color=BLUE_DARK)

ps_items = [
    "state.rcs      — position, state, exact location",
    "state.scouts   — position, state, exact location",
    "state.mps      — position, state, energy",
    "state.switches — {S1: open/closed, ...}",
    "state.dark_nodes — outage zones (no switch nodes)",
    "state.discovered_faults — found faults only",
    "state.loads    — {L1: P, Q, W, state}",
    "state.env      — for action calls only",
]
y = 1.88
for item in ps_items:
    txt(sl, f"  {item}", 0.42, y, 5.65, 0.3, sz=10, color=GRAY_DARK)
    y += 0.31

txt(sl, "Policy cannot see:", 0.42, y+0.1, 5.65, 0.3, sz=10.5, bold=True, color=RED_ERR)
y += 0.46
for item in [
    "Undiscovered fault locations or types",
    "Switch internal power state",
    "Nodes not yet physically visited",
]:
    txt(sl, f"  x  {item}", 0.42, y, 5.65, 0.3, sz=10, color=RED_ERR)
    y += 0.31

# RIGHT — timeline
box(sl, 6.47, 1.3, 6.6, 5.85, BLUE_DARK, GRAY_LIGHT)
box(sl, 6.47, 1.3, 0.05, 5.85, BLUE_LINE)
txt(sl, "Fault Discovery Timeline — Case 1", 6.65, 1.38, 6.3, 0.38, sz=13, bold=True, color=WHITE)

steps = [
    ("t=0", "faults: []   — policy sees nothing",
             "RC2 starts at N11 = DP2 location, auto-discovers + repairs immediately"),
    ("t=1", "Scout1 arrives at V1  ->  faults: ['DP2']",
             "RC2 already repairing, no redirect needed"),
    ("t=3", "RC1 arrives at N3  ->  faults: ['DP1', 'DP2']",
             "Policy: RC1.move_to('N10')  [traverse fault edge N3->N10]"),
    ("t=5", "RC2 arrives at N8  ->  faults: ['DP1','DP2','DP3']",
             "Policy: RC2.move_to('N9')  [traverse fault edge N8->N9]"),
    ("t=8", "All faults repaired  —  11/11 loads ON",
             "reward = 11800 / 11800"),
]
y = 1.9
for step, line1, line2 in steps:
    box(sl, 6.5, y, 6.52, 0.96, RGBColor(0x1a, 0x3a, 0x6e))
    txt(sl, step, 6.65, y+0.08, 0.7, 0.3, sz=10, bold=True, color=BLUE_LIGHT)
    txt(sl, line1, 7.4, y+0.08, 5.5, 0.3, sz=9.5, color=WHITE)
    txt(sl, line2, 7.4, y+0.42, 5.5, 0.3, sz=9, color=GRAY_LIGHT, italic=True)
    y += 1.06


# ═══════════════════════════════════════════════════════════════
# SLIDE 5 — Switch Node Exclusion
# ═══════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
box(sl, 0, 0, 13.33, 7.5, OFF_WHITE)
slide_header(sl, "Fix 3  —  Switch Nodes Excluded from Search",
             "Switches are infrastructure  |  Scouts and RCs only visit real bus/load nodes")

# LEFT
box(sl, 0.25, 1.3, 5.9, 5.85, WHITE, GRAY_LIGHT)
box(sl, 0.25, 1.3, 0.05, 5.85, BLUE_MID)
txt(sl, "The Problem", 0.42, 1.38, 5.65, 0.38, sz=13, bold=True, color=BLUE_DARK)

prob_items = [
    ("TGraph includes switch nodes as path waypoints", GRAY_DARK),
    ("Example: shortest path N2->N3 goes N2->S3->N3", GRAY_DARK),
    ("But S1-S8 are not load or bus nodes", GRAY_DARK),
    ("Scout visiting S3 = wasted step, no fault found", RED_ERR),
    ("dark_nodes included switch nodes = incorrect", RED_ERR),
]
y = 1.88
for text, color in prob_items:
    txt(sl, f"  {text}", 0.42, y, 5.65, 0.32, sz=10.5, color=color)
    y += 0.34

txt(sl, "The Fix", 0.42, y+0.12, 5.65, 0.36, sz=13, bold=True, color=BLUE_DARK)
y += 0.52
fix_items = [
    "switch_nodes = {n for n,t in egraph.nodes if t=='SWITCH'}",
    "search_pool excludes switch_nodes",
    "dark_nodes excludes switch_nodes",
    "RC and Scout search excludes switch_nodes",
]
for text in fix_items:
    txt(sl, f"  {text}", 0.42, y, 5.65, 0.32, sz=10, color=GRAY_DARK)
    y += 0.34

# RIGHT — position display
box(sl, 6.47, 1.3, 6.6, 2.6, WHITE, GRAY_LIGHT)
box(sl, 6.47, 1.3, 0.05, 2.6, RED_ERR)
txt(sl, "Before — Switch shown in position", 6.65, 1.38, 6.3, 0.36, sz=12, bold=True, color=RED_ERR)
txt(sl, "RC1:   'S3->N3  (4.0km left -> N3)'", 6.65, 1.86, 6.3, 0.3, sz=10.5, color=GRAY_DARK)
txt(sl, "MPS1:  'N8->S4  (2.0km left -> N10)'", 6.65, 2.2, 6.3, 0.3, sz=10.5, color=GRAY_DARK)
txt(sl, "Confusing — S3, S4 are switches, not real nodes", 6.65, 2.56, 6.3, 0.28, sz=9, color=GRAY_MID, italic=True)

box(sl, 6.47, 4.1, 6.6, 2.6, WHITE, GRAY_LIGHT)
box(sl, 6.47, 4.1, 0.05, 2.6, GREEN_OK)
txt(sl, "After — Real node-to-node span shown", 6.65, 4.18, 6.3, 0.36, sz=12, bold=True, color=GREEN_OK)
txt(sl, "RC1:   'N2->N3  (4.0km left -> N3)'", 6.65, 4.66, 6.3, 0.3, sz=10.5, color=GRAY_DARK)
txt(sl, "MPS1:  'N8->N3  (2.0km left -> N10)'", 6.65, 5.0, 6.3, 0.3, sz=10.5, color=GRAY_DARK)
txt(sl, "Walk path, skip switches, show nearest real nodes", 6.65, 5.36, 6.3, 0.28, sz=9, color=GRAY_MID, italic=True)
txt(sl, "exact_position(tgraph, switch_nodes) in all 3 agent classes", 6.65, 5.66, 6.3, 0.28, sz=9, color=GRAY_MID, italic=True)


# ═══════════════════════════════════════════════════════════════
# SLIDE 6 — Live Terminal Communication
# ═══════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
box(sl, 0, 0, 13.33, 7.5, OFF_WHITE)
slide_header(sl, "Fix 4  —  Live Terminal Communication",
             "Every callback prints state and actions in real time  |  No external script needed")

# LEFT — sample output
box(sl, 0.25, 1.3, 6.5, 5.85, WHITE, GRAY_LIGHT)
box(sl, 0.25, 1.3, 0.05, 5.85, BLUE_MID)
txt(sl, "What Prints Every Step", 0.42, 1.38, 6.25, 0.38, sz=13, bold=True, color=BLUE_DARK)

output_lines = [
    ("SIMULATOR -> POLICY  [on_rc_idle]  t=5",      BLUE_DARK,  True),
    ("  RC2: pos=N8  repair_target=None",            GRAY_DARK,  False),
    ("  rcs    : {RC1: N10, RC2: N8}",               GRAY_DARK,  False),
    ("  scouts : {Scout1: N13->V4 (5.0km -> V4)}",  GRAY_DARK,  False),
    ("  mps    : {MPS1: N10}",                       GRAY_DARK,  False),
    ("  switches: {S1:closed, S3:open, S4:open}",   GRAY_DARK,  False),
    ("  dark   : [N8, N9, N10, N11, ...]",           GRAY_DARK,  False),
    ("  faults : [DP1, DP2, DP3]",                   GRAY_DARK,  False),
    ("POLICY -> SIMULATOR  [actions]",               BLUE_MID,   True),
    ("  RC2.move_to('N9')  [traverse fault edge]",  BLUE_MID,   False),
]
y = 1.86
for text, color, bold in output_lines:
    bg = BLUE_LIGHT if bold else OFF_WHITE
    box(sl, 0.28, y, 6.44, 0.31, bg)
    txt(sl, text, 0.38, y+0.03, 6.25, 0.25, sz=9, color=color, bold=bold, wrap=False)
    y += 0.33

txt(sl, "Exact in-transit position:", 0.42, y+0.1, 6.25, 0.3, sz=10.5, bold=True, color=BLUE_DARK)
txt(sl, "  N13->V4 (5.0km left -> V4)", 0.42, y+0.44, 6.25, 0.28, sz=10, color=BLUE_MID)
txt(sl, "  = between N13 and V4, 5km remaining to target", 0.42, y+0.74, 6.25, 0.28, sz=9.5, color=GRAY_MID, italic=True)

# RIGHT — 6 callbacks
box(sl, 7.02, 1.3, 6.0, 5.85, BLUE_DARK, GRAY_LIGHT)
box(sl, 7.02, 1.3, 0.05, 5.85, BLUE_LINE)
txt(sl, "6 Callbacks — Decision Points", 7.2, 1.38, 5.7, 0.38, sz=13, bold=True, color=WHITE)

callbacks = [
    ("on_setup",           "t=0 — initial agent assignments"),
    ("on_scout_arrived",   "scout reaches a node — send to next"),
    ("on_fault_discovered","new fault revealed — redirect RCs"),
    ("on_rc_idle",         "RC has no task — repair, search, or move"),
    ("on_mps_arrived",     "MPS arrives — connect if section safe"),
    ("on_mps_idle",        "MPS standing by — connect or reposition"),
]
y = 1.9
for name, desc in callbacks:
    box(sl, 7.05, y, 5.94, 0.83, RGBColor(0x15, 0x30, 0x60))
    txt(sl, name, 7.2, y+0.06, 5.7, 0.3, sz=11, bold=True, color=BLUE_LIGHT)
    txt(sl, desc, 7.2, y+0.42, 5.7, 0.3, sz=9.5, color=GRAY_LIGHT)
    y += 0.9


# ═══════════════════════════════════════════════════════════════
# SLIDE 7 — Unknown Faults Only + summary.json + bug fixes
# ═══════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
box(sl, 0, 0, 13.33, 7.5, OFF_WHITE)
slide_header(sl, "Fix 5 + 6  —  Unknown Faults Only  &  Output Summary",
             "Removed known-faults runs  |  summary.json per case  |  bug fixes")

# LEFT
box(sl, 0.25, 1.3, 5.9, 5.85, WHITE, GRAY_LIGHT)
box(sl, 0.25, 1.3, 0.05, 5.85, BLUE_MID)
txt(sl, "Changes to run_cases.py", 0.42, 1.38, 5.65, 0.36, sz=13, bold=True, color=BLUE_DARK)

left_items = [
    ("Known-faults runs removed from output", GRAY_DARK),
    ("Only UNKNOWN mode — realistic scenario", GRAY_DARK),
    ("", GRAY_DARK),
    ("Saves output/summary.json:", BLUE_DARK),
    ('  { "case": "Case1", "hours": 8, "reward": 11800 }', GRAY_MID),
    ('  { "case": "Case2", "hours": 13, "reward": 11800 }', GRAY_MID),
    ('  ...one entry per case', GRAY_MID),
    ("", GRAY_DARK),
    ("Bug fixes:", BLUE_DARK),
    ("  repair_lag showed -h for faults found at t=0", RED_ERR),
    ("  Fix: if dp.discovered_at_step is not None", GRAY_DARK),
    ("  Now shows repair_lag=2h correctly", GREEN_OK),
    ("", GRAY_DARK),
    ("  Em-dash encoding broke on Windows terminal", RED_ERR),
    ("  Replaced Unicode dash with ASCII --", GRAY_DARK),
    ("  MPS standing by -- awaiting section clearance", GREEN_OK),
]
y = 1.86
for text, color in left_items:
    if not text:
        y += 0.1; continue
    indent = text.startswith("  ")
    txt(sl, text, 0.42, y, 5.65, 0.3, sz=9.5 if indent else 10.5, color=color)
    y += 0.31

# RIGHT — fault timeline output
box(sl, 6.47, 1.3, 6.6, 5.85, BLUE_DARK, GRAY_LIGHT)
box(sl, 6.47, 1.3, 0.05, 5.85, BLUE_LINE)
txt(sl, "Fault Timeline Output — Case 1", 6.65, 1.38, 6.3, 0.36, sz=13, bold=True, color=WHITE)

ft_lines = [
    ("DP1: discovered=t=3h   repaired=t=6h   repair_lag=3h",  WHITE),
    ("     by=RC:RC1   edge N3-N10  demand=4",                GRAY_LIGHT),
    ("", WHITE),
    ("DP2: discovered=t=0h   repaired=t=2h   repair_lag=2h",  WHITE),
    ("     by=RC:RC2   node N11  (RC2 started there)",        GRAY_LIGHT),
    ("", WHITE),
    ("DP3: discovered=t=5h   repaired=t=8h   repair_lag=3h",  WHITE),
    ("     by=RC:RC2   edge N8-N9  demand=4",                 GRAY_LIGHT),
    ("", WHITE),
    ("Agent Stats:", BLUE_LIGHT),
    ("RC1:    10km  |  4h moving  |  2h repairing  |  2h idle",   GRAY_LIGHT),
    ("RC2:    12km  |  4h moving  |  4h repairing  |  0h idle",   GRAY_LIGHT),
    ("Scout1: 33km  |  6h moving  |  7 nodes visited",            GRAY_LIGHT),
    ("MPS1:   14km  |  3h moving  |  0h connected",               GRAY_LIGHT),
]
y = 1.9
for text, color in ft_lines:
    if not text:
        y += 0.1; continue
    txt(sl, f"  {text}", 6.65, y, 6.3, 0.3, sz=9.5, color=color)
    y += 0.3


# ═══════════════════════════════════════════════════════════════
# SLIDE 8 — MPS & Switch Behavior
# ═══════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
box(sl, 0, 0, 13.33, 7.5, OFF_WHITE)
slide_header(sl, "MPS & Switch Behavior — Verified",
             "MPS waits for section clearance  |  Switches auto-close on repair  |  All cases 11/11 loads")

# LEFT — switches
box(sl, 0.25, 1.3, 5.9, 5.85, WHITE, GRAY_LIGHT)
box(sl, 0.25, 1.3, 0.05, 5.85, BLUE_MID)
txt(sl, "Switch Auto-Management", 0.42, 1.38, 5.65, 0.36, sz=13, bold=True, color=BLUE_DARK)

sw_items = [
    ("Managed by simulator, not policy", GRAY_DARK),
    ("Policy can call open/close manually (unused by greedy)", GRAY_MID),
    ("", GRAY_DARK),
    ("On fault detected (setup):", BLUE_DARK),
    ("  _open_section_switches(section)", GRAY_DARK),
    ("  Isolates faulted section from grid", GRAY_DARK),
    ("", GRAY_DARK),
    ("On fault repaired:", BLUE_DARK),
    ("  _close_section_switches(section)", GRAY_DARK),
    ("  _attempt_tie_restoration(section)", GRAY_DARK),
    ("  Closes one tie switch if section still dark", GRAY_DARK),
    ("", GRAY_DARK),
    ("Case 1 example:", BLUE_DARK),
    ("  t=0:  S3 open  (DP1 on N3-N10)", GRAY_DARK),
    ("  t=0:  S4 open  (DP3 on N8-N9)", GRAY_DARK),
    ("  t=6:  S3 closes  (DP1 repaired by RC1)", GRAY_DARK),
    ("  t=8:  S4 closes  (DP3 repaired by RC2)", GRAY_DARK),
]
y = 1.86
for text, color in sw_items:
    if not text:
        y += 0.1; continue
    txt(sl, text, 0.42, y, 5.65, 0.3, sz=10 if text.startswith("  ") else 10.5, color=color)
    y += 0.31

# RIGHT — MPS
box(sl, 6.47, 1.3, 6.6, 5.85, BLUE_DARK, GRAY_LIGHT)
box(sl, 6.47, 1.3, 0.05, 5.85, BLUE_LINE)
txt(sl, "MPS — Mobile Power Source Behavior", 6.65, 1.38, 6.3, 0.36, sz=13, bold=True, color=WHITE)

mps_items = [
    ("Moves to node with highest unserved load count", GRAY_LIGHT),
    ("Connects only when section is safe", GRAY_LIGHT),
    ("Stands by if active fault blocks the section", GRAY_LIGHT),
    ("", WHITE),
    ("Case 1 — MPS1 trace:", BLUE_LIGHT),
    ("  t=0:  @ N4  ->  moves to N10 (2 loads)", GRAY_LIGHT),
    ("  t=2:  arrives N10  ->  standing by", GRAY_LIGHT),
    ("         DP1 edge N3-N10 still active", GRAY_LIGHT),
    ("  t=6:  DP1 repaired  ->  MPS moves to N8", GRAY_LIGHT),
    ("  t=7:  arrives N8  ->  standing by", GRAY_LIGHT),
    ("         DP3 edge N8-N9 still active", GRAY_LIGHT),
    ("  t=8:  DP3 repaired  ->  grid restores directly", GRAY_LIGHT),
    ("", WHITE),
    ("Cases 1-4: MPS = 0h connected", GRAY_LIGHT),
    ("  Always arrives in faulted section", GRAY_LIGHT),
    ("  Fault repaired before MPS can connect", GRAY_LIGHT),
    ("Case 5: MPS connects briefly at t=18", GRAY_LIGHT),
    ("  Disconnects same step (grid restored)", GRAY_LIGHT),
]
y = 1.9
for text, color in mps_items:
    if not text:
        y += 0.1; continue
    indent = text.startswith("  ")
    txt(sl, text, 6.65, y, 6.3, 0.3, sz=9.5 if indent else 10, color=color)
    y += 0.3


# ═══════════════════════════════════════════════════════════════
# SLIDE 9 — Case 1 Communication Log
# ═══════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
box(sl, 0, 0, 13.33, 7.5, OFF_WHITE)
slide_header(sl, "Case 1 — Simulator / Policy Communication Log",
             "DP1=edge N3-N10  |  DP2=node N11  |  DP3=edge N8-N9  |  8 hours total")

# column headers
box(sl, 0.25, 1.27, 0.68, 5.88, BLUE_DARK)
box(sl, 0.98, 1.27, 5.82, 0.38, BLUE_MID)
box(sl, 6.86, 1.27, 0.44, 0.38, BLUE_DARK)
box(sl, 7.35, 1.27, 5.73, 0.38, BLUE_MID)

txt(sl, "t", 0.25, 1.3, 0.68, 0.3, sz=10, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
txt(sl, "SIMULATOR -> POLICY  (state)", 1.02, 1.3, 5.7, 0.28, sz=10, bold=True, color=WHITE)
txt(sl, "->", 6.86, 1.3, 0.44, 0.28, sz=11, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
txt(sl, "POLICY -> SIMULATOR  (actions)", 7.39, 1.3, 5.6, 0.28, sz=10, bold=True, color=WHITE)

rows = [
    ("t=0", "on_setup  |  RC1@N2  RC2@N11  Scout1@N2  MPS1@N4  |  faults: []",
             "move_scout->V1   move_rc(RC1)->N3   RC2.start_repair(DP2)   MPS1->N10"),
    ("t=1", "on_scout_arrived V1  |  faults: [DP2]  |  RC1: N2->N3 (4km left)",
             "move_scout->V2  |  on_fault_discovered: (none) RC2 already repairing"),
    ("t=2", "on_mps_arrived N10  |  RC2 repaired DP2 at t=2h  |  switches: S3 open",
             "MPS1 standing by -- awaiting section clearance  (DP1 still active)"),
    ("t=3", "on_rc_idle RC1@N3  |  faults: [DP1, DP2]  |  DP1 edge N3-N10",
             "RC1.move_to(N10) [traverse fault edge]   RC2.move_to(N8)"),
    ("t=4", "on_rc_idle RC1@N10 repair_target=DP1  |  both RCs traversed edge",
             "RC1.start_repair('DP1')"),
    ("t=5", "on_rc_idle RC2@N8  |  faults: [DP1,DP2,DP3]  |  DP3 edge N8-N9",
             "RC2.move_to(N9) [traverse fault edge]"),
    ("t=6", "RC1 repaired DP1  |  S3 closes  |  dark: [N8, N9, V4]",
             "MPS1.move_to(N8)   RC2.start_repair('DP3')"),
    ("t=8", "RC2 repaired DP3  |  S4 closes  |  dark: [V4]  |  All done",
             "All faults repaired  |  11/11 loads ON  |  reward = 11800"),
]

RH = 0.68
for ri, (step, state_t, action_t) in enumerate(rows):
    RY = 1.67 + ri * RH
    bg = WHITE if ri % 2 == 0 else BLUE_LIGHT

    box(sl, 0.25, RY, 0.68, RH - 0.04, BLUE_DARK)
    txt(sl, step, 0.25, RY+0.16, 0.68, 0.28, sz=8.5, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

    box(sl, 0.98, RY, 5.82, RH - 0.04, bg)
    txt(sl, state_t, 1.04, RY+0.1, 5.7, RH-0.18, sz=8.5, color=GRAY_DARK)

    box(sl, 6.86, RY, 0.44, RH - 0.04, BLUE_MID)
    txt(sl, "->", 6.86, RY+0.16, 0.44, 0.28, sz=11, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

    box(sl, 7.35, RY, 5.73, RH - 0.04, BLUE_DARK)
    txt(sl, action_t, 7.41, RY+0.1, 5.62, RH-0.18, sz=8.5, color=BLUE_LIGHT)


# ═══════════════════════════════════════════════════════════════
# SLIDE 10 — Results All 5 Cases
# ═══════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
box(sl, 0, 0, 13.33, 7.5, OFF_WHITE)
slide_header(sl, "Results — All 5 Cases  (Unknown Faults)",
             "Greedy policy  |  IEEE-13 New Network  |  All cases: 11/11 loads  |  reward = 11800")

# Table header row
col_defs = [
    ("Case",          0.25, 0.85),
    ("Fault Locations", 1.15, 3.6),
    ("Start Positions", 4.82, 2.7),
    ("Hours",         7.58, 0.95),
    ("Reward",        8.6,  1.3),
    ("RC / Scout stats", 9.97, 3.1),
]
for lbl, x, w in col_defs:
    box(sl, x, 1.27, w, 0.38, BLUE_DARK)
    txt(sl, lbl, x+0.07, 1.3, w-0.1, 0.3, sz=9.5, bold=True, color=WHITE)

cases = [
    ("Case 1", "DP1: edge N3-N10\nDP2: node N11\nDP3: edge N8-N9",
     "RC1@N2  RC2@N11\nScout@N2  MPS@N4",
     "8h",  GREEN_OK,
     "RC1: 4h mv, 2h rep\nRC2: 4h mv, 4h rep\nScout: 33km, 7 nodes"),
    ("Case 2", "DP1: edge N10-N12\nDP2: node N13\nDP3: edge N6-N7",
     "RC1@N2  RC2@N9\nScout@N2  MPS@N11",
     "13h", BLUE_MID,
     "RC1: 10h mv, 3h rep\nRC2: 4h mv, 2h rep, 7h idle\nScout: 29km, 8 nodes"),
    ("Case 3", "DP1: edge N4-N5\nDP2: edge N6-N7\nDP3: edge N2-N6",
     "RC1@N1  RC2@V2\nScout@N1  MPS@N2",
     "8h",  GREEN_OK,
     "RC1: 4h mv, 2h rep\nRC2: 6h mv, 2h rep\nScout: 32km, 8 nodes"),
    ("Case 4", "DP1: edge N2-N6 (cap=2)\nDP2: edge N8-N9\nDP3: node N10",
     "RC1@N4  RC2@N8\nScout@N4  MPS@V3",
     "13h", BLUE_MID,
     "RC1: 9h mv, 4h rep\nRC2: 9h mv, 4h rep\nScout: 53km, 13 nodes"),
    ("Case 5", "DP1: edge N2-N6 (cap=2)\nDP2: node N13\nDP3: edge N4-N5",
     "RC1@N8  RC2@N2\nScout@N8  MPS@V3",
     "18h", RED_ERR,
     "RC1: 16h mv, 2h rep\nRC2: 12h mv, 6h rep\nScout: 35km, 9 nodes"),
]

for ri, (case, faults, agents, hours, hcolor, stats) in enumerate(cases):
    ry = 1.67 + ri * 0.98
    bg = WHITE if ri % 2 == 0 else BLUE_LIGHT

    for x, w in [(0.25,0.85),(1.15,3.6),(4.82,2.7),(7.58,0.95),(8.6,1.3),(9.97,3.1)]:
        box(sl, x, ry, w, 0.93, bg, GRAY_LIGHT)

    txt(sl, case,    0.32, ry+0.3,  0.78, 0.34, sz=12, bold=True, color=BLUE_DARK)
    txt(sl, faults,  1.22, ry+0.06, 3.46, 0.84, sz=8.5, color=GRAY_DARK)
    txt(sl, agents,  4.89, ry+0.06, 2.56, 0.84, sz=8.5, color=GRAY_DARK)
    txt(sl, hours,   7.58, ry+0.24, 0.95, 0.44, sz=15, bold=True, color=hcolor, align=PP_ALIGN.CENTER)
    txt(sl, "11800", 8.68, ry+0.3,  1.14, 0.34, sz=10, color=GRAY_DARK, align=PP_ALIGN.CENTER)
    txt(sl, stats,  10.04, ry+0.06, 2.96, 0.84, sz=8,  color=GRAY_MID)

# bottom summary bar
box(sl, 0.25, 6.58, 12.83, 0.5, BLUE_DARK)
txt(sl, "All 5 cases achieve full restoration  |  Unknown faults add 0-10h overhead vs known mode  |  Greedy baseline policy",
    0.45, 6.63, 12.5, 0.38, sz=9.5, color=WHITE, align=PP_ALIGN.CENTER)


# ── save ────────────────────────────────────────────────────────
prs.save('DSR_Simulator_Architecture.pptx')
print("Saved DSR_Simulator_Architecture.pptx  --  10 slides")
