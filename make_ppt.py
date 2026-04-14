"""
Generate NYU-themed DSR Simulator PPT
Slides: Title | What We Built | What Went Wrong | Future Work
"""
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

# ── NYU Colors ────────────────────────────────────────────────
NYU_PURPLE = RGBColor(0x57, 0x06, 0x8C)
NYU_LIGHT  = RGBColor(0xAB, 0x6B, 0xC9)
NYU_WHITE  = RGBColor(0xFF, 0xFF, 0xFF)
NYU_DARK   = RGBColor(0x22, 0x00, 0x44)
NYU_GREY   = RGBColor(0xF2, 0xEC, 0xF7)
ACCENT     = RGBColor(0xFF, 0xC8, 0x00)
RED        = RGBColor(0xC0, 0x39, 0x2B)
GREEN      = RGBColor(0x1A, 0x80, 0x40)

W = Inches(13.33)
H = Inches(7.5)

prs = Presentation()
prs.slide_width  = W
prs.slide_height = H
BLANK = prs.slide_layouts[6]


# ── Helpers ───────────────────────────────────────────────────

def add_rect(slide, x, y, w, h, fill_rgb):
    shape = slide.shapes.add_shape(1, x, y, w, h)
    shape.line.fill.background()
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_rgb
    return shape

def add_text(slide, text, x, y, w, h, size, bold=False, color=NYU_WHITE,
             align=PP_ALIGN.LEFT, italic=False):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tb.word_wrap = True
    tf = tb.text_frame
    tf.word_wrap = True
    p  = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size    = Pt(size)
    run.font.bold    = bold
    run.font.italic  = italic
    run.font.color.rgb = color
    return tb

def add_bullets(slide, items, x, y, w, h, size=17, color=NYU_WHITE, bullet='▸'):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tb.word_wrap = True
    tf = tb.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_before = Pt(5)
        p.space_after  = Pt(5)
        run = p.add_run()
        run.text = f"{bullet}  {item}"
        run.font.size = Pt(size)
        run.font.color.rgb = color
    return tb

def header(slide, title, subtitle=None):
    add_rect(slide, 0, 0, W, Inches(1.15), NYU_PURPLE)
    add_rect(slide, 0, Inches(1.15), W, Inches(0.06), ACCENT)
    add_text(slide, title, Inches(0.4), Inches(0.12), Inches(12), Inches(0.9),
             size=34, bold=True, color=NYU_WHITE)
    if subtitle:
        add_text(slide, subtitle, Inches(0.4), Inches(0.82), Inches(12), Inches(0.38),
                 size=15, color=NYU_LIGHT)

def footer(slide, text="NYU Tandon  ·  SAI Lab  ·  Distribution System Restoration"):
    add_rect(slide, 0, H - Inches(0.4), W, Inches(0.4), NYU_DARK)
    add_text(slide, text, Inches(0.4), H - Inches(0.38), Inches(12.5), Inches(0.35),
             size=11, color=NYU_LIGHT)


# ══════════════════════════════════════════════════════════════
# SLIDE 1 — Title
# ══════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
add_rect(sl, 0, 0, W, H, NYU_DARK)
add_rect(sl, 0, 0, Inches(8), H, NYU_PURPLE)
add_rect(sl, Inches(8), 0, Inches(0.07), H, ACCENT)
add_rect(sl, Inches(8.07), 0, Inches(5.26), H, NYU_DARK)

add_text(sl, "Distribution System Restoration",
         Inches(0.5), Inches(1.5), Inches(7.2), Inches(1.1),
         size=36, bold=True, color=NYU_WHITE)
add_text(sl, "Unknown Fault Discovery Simulator",
         Inches(0.5), Inches(2.6), Inches(7.2), Inches(0.9),
         size=28, color=NYU_LIGHT)
add_rect(sl, Inches(0.5), Inches(3.5), Inches(4.5), Inches(0.07), ACCENT)
add_text(sl, "Multi-Agent  ·  Scout + RC + MPS  ·  IEEE-13 Network",
         Inches(0.5), Inches(3.7), Inches(7.2), Inches(0.55),
         size=15, color=NYU_LIGHT, italic=True)

add_text(sl, "NYU", Inches(8.5), Inches(1.8), Inches(4.0), Inches(1.0),
         size=52, bold=True, color=NYU_WHITE)
add_text(sl, "Tandon School of Engineering",
         Inches(8.5), Inches(2.75), Inches(4.2), Inches(0.45),
         size=15, color=NYU_LIGHT)
add_rect(sl, Inches(8.5), Inches(3.3), Inches(3.6), Inches(0.05), NYU_LIGHT)
add_text(sl, "SAI Lab  ·  New York University",
         Inches(8.5), Inches(3.45), Inches(4.2), Inches(0.4),
         size=13, color=RGBColor(0xCC, 0xAA, 0xEE))

footer(sl)


# ══════════════════════════════════════════════════════════════
# SLIDE 2 — What We Built
# ══════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
add_rect(sl, 0, 0, W, H, NYU_GREY)
header(sl, "What We Built", "IEEE-13 multi-agent DSR simulator with unknown fault discovery")
footer(sl)

top = Inches(1.35)
cw  = Inches(5.9)
ch  = Inches(5.2)

# LEFT — Network & Environment
add_rect(sl, Inches(0.3), top, cw, ch, NYU_PURPLE)
add_rect(sl, Inches(0.3), top, cw, Inches(0.55), NYU_DARK)
add_text(sl, "  Network & Environment", Inches(0.3), top, cw, Inches(0.55),
         size=17, bold=True, color=ACCENT)
add_bullets(sl, [
    "IEEE-13 bus network: 19 nodes, 8 loads, 2 switches",
    "TGraph (road routing) + EGraph (power flow)",
    "Faults: edge breaks or node damage, hidden from agents",
    "Outage zones: operator sees dark sections (SCADA), not exact faults",
    "Grid power recomputed each step via BFS",
    "5 training cases with different fault combos",
], Inches(0.45), top + Inches(0.65), cw - Inches(0.3), ch - Inches(0.75),
size=16, color=NYU_WHITE)

# ARROW
add_text(sl, "→", Inches(0.3) + cw + Inches(0.05), top + Inches(2.1),
         Inches(0.28), Inches(0.8), size=32, bold=True, color=NYU_PURPLE,
         align=PP_ALIGN.CENTER)

# RIGHT — Agents
ax = Inches(0.3) + cw + Inches(0.3)
add_rect(sl, ax, top, cw, ch, NYU_DARK)
add_rect(sl, ax, top, cw, Inches(0.55), NYU_PURPLE)
add_text(sl, "  Agents & Coordination", ax, top, cw, Inches(0.55),
         size=17, bold=True, color=ACCENT)
add_bullets(sl, [
    "RepairCrew (RC): travels, discovers faults, repairs them",
    "Scout: fast search agent, sweeps unvisited outage nodes",
    "MPS: mobile power source, restores isolated islands",
    "Shared visited set — no two agents duplicate a node",
    "globally_claimed: prevents double-assignment mid-travel",
    "Known vs Unknown mode: compares optimal vs realistic",
], ax + Inches(0.15), top + Inches(0.65), cw - Inches(0.3), ch - Inches(0.75),
size=16, color=NYU_WHITE)


# ══════════════════════════════════════════════════════════════
# SLIDE 3 — What Went Wrong
# ══════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
add_rect(sl, 0, 0, W, H, NYU_GREY)
header(sl, "What Went Wrong", "Bugs found and fixed during development")
footer(sl)

top = Inches(1.32)
card_w = Inches(3.9)
card_h = Inches(2.2)
gap    = Inches(0.22)

issues = [
    ("RCs idle at Step 0",
     "Repair crews not dispatched\nat setup — wasted first hour.\nFixed: kick RCs in setup()."),
    ("Fault info leaked via EGraph",
     "Agents guided by live/dead\npowered nodes → indirectly\nknew fault locations.\nFixed: use explicit outage_zones."),
    ("Switch nodes as faults",
     "S1 / S2 marked as fault sites\nbut they are switches, not buses.\nFixed: redesigned all 5 cases."),
    ("Duplicate node visits",
     "Two agents sent to same node\nbecause global_visited only\nupdated on arrival.\nFixed: add globally_claimed set."),
    ("RC assignment race condition",
     "RC2 standing on fault not\ncounted — RC1 also sent there.\nFixed: _rc_at_fault() check\nin assignment loop."),
    ("Exhausted RC blocking repair",
     "RC with 0 resources at fault\ncounted as 'covering' it —\ncapable RCs blocked away.\nFixed: resources > 0 guard +\nauto-repair at start position."),
]

cols = 3
for i, (title, body) in enumerate(issues):
    row = i // cols
    col = i % cols
    px = Inches(0.25) + col * (card_w + gap)
    py = top + row * (card_h + Inches(0.18))

    is_open = (i == 5)
    card_bg   = NYU_DARK   if not is_open else RGBColor(0x5C, 0x10, 0x10)
    head_bg   = NYU_PURPLE if not is_open else RED
    num_color = ACCENT     if not is_open else RGBColor(0xFF, 0x88, 0x88)

    add_rect(sl, px, py, card_w, card_h, card_bg)
    add_rect(sl, px, py, card_w, Inches(0.5), head_bg)

    # number badge
    add_rect(sl, px + card_w - Inches(0.48), py + Inches(0.06),
             Inches(0.38), Inches(0.38), ACCENT if not is_open else RED)
    add_text(sl, str(i + 1), px + card_w - Inches(0.46), py + Inches(0.07),
             Inches(0.36), Inches(0.36), size=14, bold=True,
             color=NYU_DARK if not is_open else NYU_WHITE, align=PP_ALIGN.CENTER)

    add_text(sl, title, px + Inches(0.12), py + Inches(0.07),
             card_w - Inches(0.6), Inches(0.4),
             size=15, bold=True, color=NYU_WHITE)
    add_text(sl, body, px + Inches(0.14), py + Inches(0.58),
             card_w - Inches(0.25), card_h - Inches(0.68),
             size=13, color=NYU_GREY)

# open bug label
add_text(sl, "⬡  Issue 6 is still open",
         Inches(0.25), top + 2 * (card_h + Inches(0.18)) + Inches(0.05),
         Inches(6), Inches(0.35),
         size=12, italic=True, color=RED)


# ══════════════════════════════════════════════════════════════
# SLIDE 4 — Future Work
# ══════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
add_rect(sl, 0, 0, W, H, NYU_GREY)
header(sl, "Future Work", "From heuristic simulator to LLM-guided restoration")
footer(sl)

top = Inches(1.4)
pw  = Inches(4.0)
ph  = Inches(4.8)
gap = Inches(0.22)

pillars = [
    ("1  Fix & Scale Simulator",
     ["Fix remaining RC assignment bug\n(unknown overhead Cases 3 & 5)",
      "Add IEEE-33 network (45 nodes, 31 loads)",
      "Run 1000+ episodes per case",
      "Export (state, action, reward) as JSONL\nfor supervised training",
      "Benchmark: greedy vs random vs optimal"]),
    ("2  Fine-Tune LLM",
     ["SFT on known-fault optimal trajectories",
      "LoRA adapter on top of base LLM\n(Qwen 7B / LLaMA 3)",
      "Input: grid state as structured text prompt\n(nodes, faults, agent positions)",
      "Output: next best action for each RC / MPS",
      "Reward signal: weighted loads restored / time"]),
    ("3  Evaluate & Deploy",
     ["Test LLM on unseen unknown-fault cases",
      "Goal: close the discovery overhead gap\n(~5–8h extra vs known baseline)",
      "Compare: LLM vs greedy vs random",
      "Extend to multi-fault, multi-crew scenarios",
      "Real-time operator decision support tool"]),
]

for i, (title, bullets) in enumerate(pillars):
    px = Inches(0.25) + i * (pw + gap)
    add_rect(sl, px, top, pw, ph, NYU_DARK)
    add_rect(sl, px, top, pw, Inches(0.55), NYU_PURPLE)
    add_rect(sl, px + pw - Inches(0.55), top + Inches(0.07),
             Inches(0.42), Inches(0.42), ACCENT)
    add_text(sl, str(i + 1), px + pw - Inches(0.52), top + Inches(0.08),
             Inches(0.38), Inches(0.38), size=16, bold=True,
             color=NYU_DARK, align=PP_ALIGN.CENTER)
    add_text(sl, title, px + Inches(0.12), top + Inches(0.08),
             pw - Inches(0.65), Inches(0.45),
             size=16, bold=True, color=NYU_WHITE)
    add_bullets(sl, bullets, px + Inches(0.15), top + Inches(0.65),
                pw - Inches(0.25), ph - Inches(0.75),
                size=14, color=NYU_GREY)


OUT = r"a:\dsr_simulator_standalone\DSR_Simulator_NYU.pptx"
prs.save(OUT)
print(f"Saved: {OUT}")
