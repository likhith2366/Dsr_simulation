"""
DSR Simulator — Architecture Update Presentation
Run:  python make_slides_arch.py
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

txt(sl, "DSR Simulator — Architecture Update",
    0.65, 2.2, 12.0, 0.95, sz=40, bold=True, color=WHITE)
txt(sl, "Simulator / Policy Separation  ·  Swappable Decision-Making Interface",
    0.65, 3.15, 12.0, 0.55, sz=18, color=TEAL)
txt(sl, "Physics engine decoupled from strategy  ·  Greedy baseline  ·  LLM / RL ready",
    0.65, 3.72, 12.0, 0.45, sz=14, color=MGRAY, italic=True)

for i, (val, lbl) in enumerate([
    ("2",  "Core Modules"),
    ("6",  "Policy Callbacks"),
    ("5",  "Action Types"),
    ("✓",  "Identical Output"),
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
# SLIDE 2 — Architecture Overview (what changed and why)
# ═══════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
box(sl, 0, 0, 13.33, 7.5, LGRAY)
hdr(sl, "Architecture — What Changed",
    "Decision logic extracted from simulator  ·  physics and strategy now fully independent")

# LEFT — before
box(sl, 0.3, 1.38, 5.9, 5.82, WHITE)
box(sl, 0.3, 1.38, 0.07, 5.82, RED)
txt(sl, "BEFORE — Monolithic", 0.48, 1.46, 5.5, 0.42, sz=13, bold=True, color=RED)

before_lines = [
    ("environment.py (single file)", DGRAY, True),
    ("  Network physics (nodes, edges, power flow)", DGRAY, False),
    ("  Agent movement execution", DGRAY, False),
    ("  Fault discovery logic", DGRAY, False),
    ("  Agent assignment decisions  ← mixed in", RED, False),
    ("  Search strategy  ← mixed in", RED, False),
    ("  MPS connect/disconnect decisions  ← mixed in", RED, False),
    ("  RC redirect on new fault  ← mixed in", RED, False),
    ("", DGRAY, False),
    ("Problem: to change strategy you must edit", ORANGE, True),
    ("  the same file that owns physics — risk of", DGRAY, False),
    ("  breaking the simulator when changing policy", DGRAY, False),
]
for i, (line, color, bold) in enumerate(before_lines):
    if line:
        txt(sl, line, 0.48, 1.92 + i*0.30, 5.5, 0.28,
            sz=10 if not bold else 11, bold=bold, color=color)

# RIGHT — after
box(sl, 6.5, 1.38, 6.53, 5.82, WHITE)
box(sl, 6.5, 1.38, 0.07, 5.82, GREEN)
txt(sl, "AFTER — Separated", 6.68, 1.46, 6.1, 0.42, sz=13, bold=True, color=GREEN)

after_lines = [
    ("environment.py — pure physics only", GREEN, True),
    ("  Network state, power flow, edge/node faults", DGRAY, False),
    ("  Agent movement execution (move_rc, move_scout)", DGRAY, False),
    ("  Discovery check on arrival (_check_discovery)", DGRAY, False),
    ("  Fires callbacks to policy at decision points", TEAL, False),
    ("  MPS auto-disconnect (physics, not strategy)", DGRAY, False),
    ("", DGRAY, False),
    ("policy.py — all decisions", PURPLE, True),
    ("  on_setup: initial agent assignments", DGRAY, False),
    ("  on_scout_arrived: where to send scout next", DGRAY, False),
    ("  on_rc_idle: repair or search", DGRAY, False),
    ("  on_fault_discovered: redirect RCs", DGRAY, False),
    ("  on_mps_arrived / on_mps_idle: connect or wait", DGRAY, False),
    ("", DGRAY, False),
    ("Swap GreedyPolicy → LLMPolicy with zero simulator changes", GREEN, True),
]
for i, (line, color, bold) in enumerate(after_lines):
    if line:
        txt(sl, line, 6.68, 1.92 + i*0.28, 6.1, 0.26,
            sz=10 if not bold else 11, bold=bold, color=color)


# ═══════════════════════════════════════════════════════════════════════
# SLIDE 3 — Data Flow: State & Actions
# ═══════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
box(sl, 0, 0, 13.33, 7.5, LGRAY)
hdr(sl, "Interface — State & Actions",
    "What the Simulator sends to Policy  ·  What the Policy sends back")

# ── STATE box (left) ────────────────────────────────────────────────
box(sl, 0.3, 1.38, 5.9, 5.82, NAVY)
box(sl, 0.3, 1.38, 0.07, 5.82, TEAL)
txt(sl, "State  (Simulator → Policy)", 0.48, 1.44, 5.5, 0.42, sz=13, bold=True, color=TEAL)

state_items = [
    ("Agent positions",     "rc.position,  scout.position,  mps.position"),
    ("Agent states",        "rc.state  →  idle / moving / repairing"),
    ("Fault locations",     "fault.node  or  fault.edge  (tuple)"),
    ("Fault status",        "fault.state  →  active / repaired"),
    ("Fault discovered?",   "fault.discovered  →  True / False"),
    ("Outage zones",        "env.outage_zones  — set of dark nodes"),
    ("Visited nodes",       "env.global_visited,  env.globally_claimed"),
    ("Road graph",          "env.tgraph.shortest_path(a, b)  → (path, dist)"),
    ("Electrical graph",    "env.egraph.get_powered_nodes()"),
    ("Load scoring",        "env.egraph.count_loads_if_source(node)"),
    ("Section safety",      "env._section_safe_for_mps(section)"),
]
for i, (label, val) in enumerate(state_items):
    y = 1.94 + i * 0.44
    box(sl, 0.38, y, 1.62, 0.36, RGBColor(0x22, 0x30, 0x50))
    txt(sl, label, 0.42, y+0.04, 1.55, 0.28, sz=8.5, bold=True, color=TEAL)
    txt(sl, val,   2.08, y+0.05, 3.98, 0.30, sz=9,   color=RGBColor(0xcc, 0xdd, 0xee))

# ── ARROW ─────────────────────────────────────────────────────────────
box(sl, 6.3, 3.8, 0.73, 0.06, TEAL)
txt(sl, "STATE →", 6.18, 3.55, 1.0, 0.28, sz=8, bold=True, color=TEAL, align=PP_ALIGN.CENTER)
box(sl, 6.3, 4.5, 0.73, 0.06, ORANGE)
txt(sl, "← ACTIONS", 6.14, 4.65, 1.08, 0.28, sz=8, bold=True, color=ORANGE, align=PP_ALIGN.CENTER)

# ── ACTIONS box (right) ───────────────────────────────────────────────
box(sl, 7.13, 1.38, 5.9, 5.82, NAVY)
box(sl, 7.13, 1.38, 0.07, 5.82, ORANGE)
txt(sl, "Actions  (Policy → Simulator)", 7.31, 1.44, 5.5, 0.42, sz=13, bold=True, color=ORANGE)

action_items = [
    ("Move RC",      "env.move_rc(rc_id, target_node)"),
    ("Move Scout",   "env.move_scout(scout_id, target_node)"),
    ("Move MPS",     "mps.move_to(path, distance)"),
    ("Start Repair", "rc.start_repair(fault_id)"),
    ("Connect MPS",  "mps.connect()"),
]
for i, (label, call) in enumerate(action_items):
    y = 1.94 + i * 0.56
    box(sl, 7.21, y, 1.32, 0.40, RGBColor(0x22, 0x30, 0x50))
    txt(sl, label, 7.25, y+0.06, 1.25, 0.28, sz=9, bold=True, color=ORANGE)
    box(sl, 8.61, y, 4.32, 0.40, RGBColor(0x15, 0x1e, 0x33))
    txt(sl, call,  8.67, y+0.06, 4.20, 0.30, sz=9.5, color=RGBColor(0xaa, 0xdd, 0xaa))

# policy callback table
box(sl, 7.13, 4.90, 5.9, 2.28, RGBColor(0x22, 0x30, 0x50))
txt(sl, "Policy Callbacks (Simulator fires these)", 7.25, 4.96, 5.6, 0.34,
    sz=11, bold=True, color=ORANGE)
callbacks = [
    "policy.on_setup(env, known_faults)          ← after init",
    "policy.on_scout_arrived(env, scout_id, node) ← scout lands",
    "policy.on_rc_idle(env, rc, events)           ← RC free",
    "policy.on_fault_discovered(env, events)      ← new fault found",
    "policy.on_mps_arrived(env, mps, node, events)← MPS lands",
    "policy.on_mps_idle(env, mps, events)         ← MPS standing by",
]
for i, cb in enumerate(callbacks):
    txt(sl, cb, 7.25, 5.36 + i*0.29, 5.6, 0.28, sz=8.5,
        color=RGBColor(0xcc, 0xdd, 0xee))


# ═══════════════════════════════════════════════════════════════════════
# SLIDE 4 — Communication: What Simulator Sends, What Policy Sends Back
# ═══════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
box(sl, 0, 0, 13.33, 7.5, LGRAY)
hdr(sl, "Case 1 — How Simulator & Policy Communicate",
    "Real values from simulation run  ·  3 faults: DP1=edge N3–N8, DP2=node N10, DP3=edge N13–V1")

# ── column headers ────────────────────────────────────────────────────
box(sl, 0.3,  1.36, 0.72, 5.88, NAVY)   # step col bg
box(sl, 1.08, 1.36, 5.68, 0.44, TEAL)
box(sl, 6.82, 1.36, 0.50, 0.44, NAVY)
box(sl, 7.38, 1.36, 5.65, 0.44, ORANGE)

txt(sl, "Step", 0.30, 1.40, 0.72, 0.36, sz=10, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
txt(sl, "Simulator  →  Policy   (state passed via env)", 1.12, 1.40, 5.56, 0.34,
    sz=11, bold=True, color=WHITE)
txt(sl, "→", 6.82, 1.40, 0.50, 0.34, sz=14, bold=True, color=TEAL, align=PP_ALIGN.CENTER)
txt(sl, "Policy  →  Simulator   (actions called back)", 7.42, 1.40, 5.53, 0.34,
    sz=11, bold=True, color=WHITE)

# ── rows ──────────────────────────────────────────────────────────────
rows = [
    (
        "t=0\nSetup", TEAL,
        [
            ("Callback",   "policy.on_setup(env, known_faults=False)"),
            ("Agents",     "RC1@N2  RC2@N11  Scout1@N2  MPS1@N4"),
            ("Faults",     "DP1,DP2,DP3  discovered=False  state=active"),
            ("Dark nodes", "N10 N11 N12 N13 N3 N8 N9 S1 S2 V1"),
        ],
        [
            "env.move_rc('RC1', 'S2')",
            "env.move_rc('RC2', 'N10')",
            "env.move_scout('Scout1', 'S1')",
            "mps.move_to(path→N8)",
        ],
    ),
    (
        "t=1\nRC2 & Scout\narrive", PURPLE,
        [
            ("Callback",  "on_scout_arrived(env, 'Scout1', 'S1')"),
            ("Callback",  "on_fault_discovered(env)  ← DP2 found at N10"),
            ("RC2",       "position=N10  state=idle"),
            ("DP2",       "discovered=True  state=active  node=N10"),
        ],
        [
            "env.move_scout('Scout1', 'N3')",
            "rc.start_repair('DP2')   ← RC2 at fault, repair now",
            "RC2.state = 'repairing'",
            "RC2.repair_target = 'DP2'",
        ],
    ),
    (
        "t=2\nDP1\nfound", ORANGE,
        [
            ("Callback",  "on_scout_arrived(env, 'Scout1', 'N3')"),
            ("Callback",  "on_fault_discovered(env)  ← DP1 found"),
            ("DP1",       "edge=('N3','N8')  discovered=True"),
            ("RC1",       "state=moving  target=S2  (old target)"),
        ],
        [
            "env.move_scout('Scout1', 'N8')",
            "env.move_rc('RC1', 'N3')   ← redirected to fault",
            "RC1 was going to S2, now heads to N3",
        ],
    ),
    (
        "t=7\nRC1 at N8\nrepairs DP1", GREEN,
        [
            ("Callback",  "on_rc_idle(env, RC1, events)"),
            ("RC1",       "position=N8  state=idle"),
            ("DP1",       "discovered=True  state=active"),
            ("Check",     "_rc_at_fault(RC1, DP1) = True"),
        ],
        [
            "rc.start_repair('DP1')",
            "RC1.state = 'repairing'",
            "RC1.repair_target = 'DP1'",
        ],
    ),
    (
        "t=9\nAll done", RED,
        [
            ("Faults",    "DP1,DP2,DP3  state=repaired"),
            ("Outage",    "outage_zones = []   ← empty"),
            ("Physics",   "MPS auto-disconnect fired by simulator"),
        ],
        [
            "(no actions — outage_zones empty)",
            "loop exits",
        ],
    ),
]

RH = 1.04
for ri, (step_lbl, color, state_rows, action_rows) in enumerate(rows):
    RY = 1.82 + ri * RH
    bg = WHITE if ri % 2 == 0 else LGRAY

    # step badge
    box(sl, 0.30, RY, 0.72, RH - 0.06, color)
    txt(sl, step_lbl, 0.30, RY + 0.12, 0.72, RH - 0.18,
        sz=8, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

    # state panel
    box(sl, 1.08, RY, 5.68, RH - 0.06, bg)
    for si, (lbl, val) in enumerate(state_rows):
        sy = RY + 0.06 + si * 0.23
        box(sl, 1.12, sy, 0.90, 0.20, NAVY)
        txt(sl, lbl, 1.14, sy+0.02, 0.86, 0.17, sz=7, bold=True, color=TEAL)
        txt(sl, val, 2.06, sy+0.02, 4.62, 0.19, sz=8.5, color=DGRAY)

    # arrow
    box(sl, 6.82, RY, 0.50, RH - 0.06, RGBColor(0xe8, 0xf4, 0xf8))
    txt(sl, "→", 6.82, RY + (RH-0.3)/2 - 0.1, 0.50, 0.30,
        sz=16, bold=True, color=TEAL, align=PP_ALIGN.CENTER)

    # action panel
    box(sl, 7.38, RY, 5.65, RH - 0.06, NAVY)
    for ai, act in enumerate(action_rows):
        ay = RY + 0.10 + ai * 0.26
        txt(sl, act, 7.46, ay, 5.49, 0.24, sz=9,
            color=RGBColor(0xaa, 0xdd, 0xaa) if 'rc\.' in act or 'env\.' in act or 'mps\.' in act
            else RGBColor(0x88, 0xaa, 0xcc))


# ═══════════════════════════════════════════════════════════════════════
# SLIDE 5 — Why This Architecture Matters
# ═══════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
box(sl, 0, 0, 13.33, 7.5, LGRAY)
hdr(sl, "Why This Architecture Matters",
    "Greedy baseline verified identical output  ·  Swappable for LLM or RL policy")

CW  = 4.11
GAP = 0.2
XS  = [0.3, 0.3 + CW + GAP, 0.3 + 2*(CW + GAP)]

card(sl, XS[0], 1.38, CW, 3.3,
     "Simulator — Pure Physics", [
         "Owns: network state, power flow, agent movement",
         "Knows: distances, edge faults, section boundaries",
         "Does NOT decide where agents go",
         "Does NOT decide when MPS connects",
         "Fires callbacks → policy at every decision point",
         "MPS auto-disconnect is physics (not strategy)",
         "Verified: bit-for-bit identical output after refactor",
     ], tc=TEAL)

card(sl, XS[1], 1.38, CW, 3.3,
     "Policy — Pure Strategy", [
         "Owns: all agent assignment decisions",
         "Reads state via env (full read access)",
         "Sends actions via env.move_rc / rc.start_repair",
         "Greedy: nearest unvisited node, closest fault",
         "Shared global_visited prevents duplicate work",
         "Search continues until full grid restoration",
         "Redirect RCs on newly discovered faults",
     ], tc=PURPLE)

dark_card(sl, XS[2], 1.38, CW, 3.3,
          "Swap Policy — Zero Sim Changes", [
              "class LLMPolicy:",
              "  def on_rc_idle(env, rc, events):",
              "    prompt = build_prompt(env)",
              "    action = llm.call(prompt)",
              "    env.move_rc(rc.id, action.target)",
              "",
              "No simulator code changes needed",
          ], tc=ORANGE)

card(sl, XS[0], 4.86, CW, 2.38,
     "Verified — Identical Results", [
         "Ran both versions on all 5 cases",
         "git diff showed zero changes in walkthrough MD",
         "Same step counts, same repair times, same MPS moves",
         "Refactor is purely structural — no logic changed",
     ], tc=GREEN)

card(sl, XS[1], 4.86, CW, 2.38,
     "What This Enables", [
         "LLM policy: natural language → agent actions",
         "RL policy: reward = load-hours restored",
         "Hybrid: LLM for MPS, greedy for RC",
         "A/B test policies with identical simulator",
         "Benchmark any strategy against greedy baseline",
     ], tc=TEAL)

card(sl, XS[2], 4.86, CW, 2.38,
     "Simulation Results (Greedy Baseline)", [
         "Case 1: +2h extra  (Areas 3,4,5 faults)",
         "Case 2: +5h extra  (total blackout)",
         "Case 3: +5h extra  (total blackout)",
         "Case 4: +8h extra  (level-10 fault)",
         "Case 5: +16h extra (level-10 + wide search)",
     ], tc=ORANGE)


# ── save ──────────────────────────────────────────────────────────────
prs.save('DSR_Simulator_Architecture.pptx')
print("Saved DSR_Simulator_Architecture.pptx  —  5 slides")
