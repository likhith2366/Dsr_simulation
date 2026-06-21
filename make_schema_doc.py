"""
Generate Schema Documentation Word file
DSR Simulator <-> Policy Communication Schema
"""

from docx import Document
from docx.shared import Pt, RGBColor, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import copy

BLUE_DARK  = (0x0d, 0x2e, 0x6e)
BLUE_MID   = (0x15, 0x5f, 0xb5)
BLUE_LIGHT = (0xd6, 0xe4, 0xf7)
WHITE      = (0xFF, 0xFF, 0xFF)
GRAY_LIGHT = (0xf0, 0xf0, 0xf0)
GRAY_MID   = (0xcc, 0xcc, 0xcc)
BLACK      = (0x00, 0x00, 0x00)

def to_rgb(t): return RGBColor(t[0], t[1], t[2])

doc = Document()

# ── Page margins ───────────────────────────────────────────────
for section in doc.sections:
    section.top_margin    = Cm(2.0)
    section.bottom_margin = Cm(2.0)
    section.left_margin   = Cm(2.5)
    section.right_margin  = Cm(2.5)

# ── Helpers ────────────────────────────────────────────────────

def set_cell_bg(cell, rgb: RGBColor):
    tc   = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd  = OxmlElement('w:shd')
    hex_color = f'{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}'
    shd.set(qn('w:val'),   'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'),  hex_color)
    tcPr.append(shd)

def set_cell_border(cell, top=False, bottom=False, left=False, right=False,
                    color='AAAAAA', sz='4'):
    tc   = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcBorders = OxmlElement('w:tcBorders')
    for side, active in [('top', top), ('bottom', bottom),
                         ('left', left), ('right', right)]:
        if active:
            el = OxmlElement(f'w:{side}')
            el.set(qn('w:val'),   'single')
            el.set(qn('w:sz'),    sz)
            el.set(qn('w:color'), color)
            tcBorders.append(el)
    tcPr.append(tcBorders)

def heading(text, level=1):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(16 if level == 1 else 10)
    p.paragraph_format.space_after  = Pt(4)
    run = p.add_run(text)
    run.bold      = True
    run.font.size = Pt(16 if level == 1 else 13)
    run.font.color.rgb = to_rgb(BLUE_DARK if level == 1 else BLUE_MID)
    return p

def body(text, bold_parts=None):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after  = Pt(4)
    run = p.add_run(text)
    run.font.size = Pt(10.5)
    run.font.color.rgb = to_rgb(BLACK)
    return p

def schema_table(headers, rows, col_widths=None):
    """Draw a styled table."""
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = 'Table Grid'

    # Header row
    hdr = table.rows[0]
    for i, h in enumerate(headers):
        cell = hdr.cells[i]
        set_cell_bg(cell, BLUE_DARK)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(h)
        run.bold = True
        run.font.size  = Pt(9)
        run.font.color.rgb = to_rgb(WHITE)

    # Data rows
    for ri, row in enumerate(rows):
        is_section = row[0].startswith('──')
        tr = table.rows[ri + 1]
        for ci, val in enumerate(row):
            cell = tr.cells[ci]
            if is_section:
                set_cell_bg(cell, BLUE_LIGHT)
            elif ri % 2 == 0:
                set_cell_bg(cell, GRAY_LIGHT)
            else:
                set_cell_bg(cell, WHITE)
            p = cell.paragraphs[0]
            run = p.add_run(val)
            run.font.size = Pt(9)
            if is_section:
                run.bold = True
                run.font.color.rgb = to_rgb(BLUE_DARK)
            else:
                run.font.color.rgb = to_rgb(BLACK)

    # Column widths
    if col_widths:
        for i, w in enumerate(col_widths):
            for row in table.rows:
                row.cells[i].width = Cm(w)

    doc.add_paragraph()
    return table


# ══════════════════════════════════════════════════════════════════
# TITLE
# ══════════════════════════════════════════════════════════════════
p = doc.add_paragraph()
p.paragraph_format.space_before = Pt(0)
p.paragraph_format.space_after  = Pt(6)
run = p.add_run('DSR Simulator — Policy Communication Schema')
run.bold = True
run.font.size = Pt(20)
run.font.color.rgb = to_rgb(BLUE_DARK)

p2 = doc.add_paragraph()
run2 = p2.add_run('IEEE-13 New Network · Multi-Agent Fault Discovery & Restoration')
run2.font.size = Pt(11)
run2.font.color.rgb = to_rgb(BLUE_MID)

doc.add_paragraph()

# ══════════════════════════════════════════════════════════════════
# SECTION 1 — Overview
# ══════════════════════════════════════════════════════════════════
heading('1.  Overview', 1)
body(
    'The simulator (environment.py) and the policy (policy.py) are fully separated. '
    'The simulator handles all physics — movement, power flow, fault discovery. '
    'The policy handles all decisions — where to move, who to repair, when to connect MPS. '
    'They communicate through a single shared object called PolicyState, '
    'which is passed to the policy at every event callback.'
)
body(
    'Communication is one-way per callback: the simulator builds a fresh PolicyState '
    'and calls the relevant callback. The policy reads the state and issues actions '
    'back through state.env.*  method calls. The simulator then executes those actions '
    'and advances the simulation.'
)

doc.add_paragraph()

# ══════════════════════════════════════════════════════════════════
# SECTION 2 — Python Object Schema (what actually goes to policy)
# ══════════════════════════════════════════════════════════════════
heading('2.  Python Object Schema — What Actually Goes to Policy', 1)
body(
    'At every callback the simulator passes a PolicyState Python object directly. '
    'The policy reads it as state.rcs["RC1"]["position"], state.discovered_faults, etc. '
    'There is no serialization — this is the raw in-memory object. '
    'Below is the exact structure with real example values from Case 1 at t=2.'
)

doc.add_paragraph()

def code_block(lines):
    for line in lines:
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after  = Pt(0)
        p.paragraph_format.left_indent  = Cm(0.5)
        run = p.add_run(line)
        run.font.name = 'Courier New'
        run.font.size = Pt(8)
        run.font.color.rgb = to_rgb(BLUE_DARK)

code_block([
    'PolicyState {',
    '',
    '    time = 0,',
    '',
    '    rcs = {',
    '        "RC1": {',
    '            "id":                 "RC1",',
    '            "position":           "N2",',
    '            "state":              "moving",',
    '            "target":             "N10",',
    '            "repair_target":      null,',
    '            "resources":          15,',
    '            "remaining_distance": 10.0,       # km left to target',
    '            "exact": {',
    '                "at":      "N2->N3",           # display label, switch nodes hidden',
    '                "segment": ["N2", "S3"],        # raw edge including switch nodes',
    '                "km_done": 0.0,',
    '                "km_left": 10.0',
    '            },',
    '            "stats": {',
    '                "total_km":        0.0,',
    '                "hours_moving":    0,',
    '                "hours_repairing": 0,',
    '                "hours_idle":      0,',
    '                "faults_repaired": []',
    '            }',
    '        },',
    '        "RC2": {',
    '            "id":                 "RC2",',
    '            "position":           "N11",',
    '            "state":              "repairing",',
    '            "target":             null,',
    '            "repair_target":      "DP2",',
    '            "resources":          15,',
    '            "remaining_distance": 0.0,',
    '            "exact": { "at": "N11", "segment": null, "km_done": 0.0, "km_left": 0.0 },',
    '            "stats": { "total_km": 0.0, "hours_moving": 0, "hours_repairing": 0, ... }',
    '        }',
    '    },',
    '',
    '    scouts = {',
    '        "Scout1": {',
    '            "id":                 "Scout1",',
    '            "position":           "N2",',
    '            "state":              "moving",',
    '            "target":             "N3",',
    '            "remaining_distance": 8.0,',
    '            "exact": {',
    '                "at":      "N2->N3",',
    '                "segment": ["N2", "S3"],',
    '                "km_done": 0.0,',
    '                "km_left": 8.0',
    '            },',
    '            "stats": {',
    '                "total_km":      0.0,',
    '                "hours_moving":  0,',
    '                "hours_idle":    0,',
    '                "nodes_visited": 1,',
    '                "discovery_log": []            # [(step, fault_id, position)]',
    '            }',
    '        }',
    '    },',
    '',
    '    mps = {',
    '        "MPS1": {',
    '            "id":                 "MPS1",',
    '            "position":           "N4",',
    '            "state":              "moving",',
    '            "target":             "N10",',
    '            "remaining_distance": 10.01,',
    '            "energy":             5000,        # kWh remaining',
    '            "p_limit":            600,         # kW max output',
    '            "exact": {',
    '                "at":      "N4->N8",',
    '                "segment": ["N4", "N8"],',
    '                "km_done": 0.0,',
    '                "km_left": 10.01',
    '            },',
    '            "stats": { "total_km": 0.0, "hours_moving": 0, "hours_connected": 0, "hours_idle": 0 }',
    '        }',
    '    },',
    '',
    '    discovered_faults = {}   # empty at t=0, faults only appear after agent arrives at location',
    '    # example after Scout1 finds DP1 at N3:',
    '    # discovered_faults = {',
    '    #     "DP1": {',
    '    #         "id":                 "DP1",',
    '    #         "type":               "node",',
    '    #         "location":           "N3",',
    '    #         "state":              "active",',
    '    #         "progress":           0.0,',
    '    #         "demand":             5,',
    '    #         "discovered":         true,',
    '    #         "discovered_by":      "Scout1",',
    '    #         "discovered_at_step": 1,',
    '    #         "repaired_at_step":   null',
    '    #     }',
    '    # }   # DP2, DP3 still hidden — NOT present',
    '',
    '',
    '    load_nodes       = {"N3","N4","N5","N6","N7","N8","N10","N11","N12","N13","V2"},',
    '    dark_load_nodes  = {"N3","N8","N10","N11","N12","N13","V2"},   # unpowered WITH demand',
    '    dark_topo_nodes  = {"N9","V1","V3","V4"},                      # unpowered, no load',
    '',
    '    loads = {',
    '        "L_N7":  { "node":"N7",  "state":"on",  "P":40,  "Q":15,   "W":5  },',
    '        "L_N6":  { "node":"N6",  "state":"on",  "P":10,  "Q":5,    "W":4  },',
    '        "L_N3":  { "node":"N3",  "state":"off", "P":400, "Q":300,  "W":6  },',
    '        "L_N8":  { "node":"N8",  "state":"off", "P":500, "Q":200,  "W":4  },',
    '        "L_N11": { "node":"N11", "state":"off", "P":200, "Q":80,   "W":10 },',
    '        ... # all 11 loads',
    '    },',
    '',
    '    switches = {',
    '        "S1":"closed", "S2":"closed", "S3":"open", "S4":"open",',
    '        "S5":"closed", "S6":"open",   "S7":"open", "S8":"open"',
    '    },',
    '',
    '    global_visited    = {"N2", "N11"},',
    '    globally_claimed  = {"N2", "N11", "N10", "N3"},',
    '    rc_searching      = {"RC1"},',
    '',
    '    env    = <DSREnvironment>   # policy calls actions here: state.env.move_rc(...)',
    '    tgraph = <TGraph>           # policy queries paths here:  state.tgraph.shortest_path(...)',
    '}',
])

doc.add_paragraph()
doc.add_paragraph()

# ══════════════════════════════════════════════════════════════════
# SECTION 3 — Human-Readable Printed Schema
# ══════════════════════════════════════════════════════════════════
heading('3.  Human-Readable Schema — What Prints in Terminal', 1)
body(
    'Every callback also prints a structured log to the terminal so a human can follow '
    'what the simulator sent and what the policy decided. This is the same data as the '
    'Python object above, formatted for readability. It does not affect the simulation.'
)

doc.add_paragraph()
code_block([
    'SIMULATOR -> POLICY  [on_scout_arrived]  t=2',
    '  Scout1 arrived at N3',
    '  rcs:',
    '    [RC1]',
    '      position     : N2',
    '      state        : moving',
    '      target       : N10',
    '      repair_target: None',
    '      resources    : 15',
    '      km_left      : 6.0',
    '      exact.at     : N2->N3',
    '      exact.km_done: 4.0',
    '    [RC2]',
    '      position     : N11',
    '      state        : repairing',
    '      target       : None',
    '      repair_target: DP2',
    '      resources    : 15',
    '      km_left      : 0.0',
    '      exact.at     : N11',
    '      exact.km_done: 0.0',
    '  scouts:',
    '    [Scout1]',
    '      position     : N3',
    '      state        : idle',
    '      target       : None',
    '      km_left      : 0.0',
    '      exact.at     : N3',
    '      exact.km_done: 0.0',
    '  mps:',
    '    [MPS1]',
    '      position     : N4',
    '      state        : idle',
    '      energy       : 5000 kWh',
    '      km_left      : 0.0',
    '      exact.at     : N4',
    '      exact.km_done: 0.0',
    '  switches: {S1:closed, S2:closed, S3:open, S4:open, S5:closed, S6:open, S7:open, S8:open}',
    '  dark (load nodes) : [N10, N11, N12, N13, N3, N8, V2]',
    '  dark (topo only)  : [N9, V1, V3, V4]',
    '  faults  : [DP1, DP2]',
    '',
    'POLICY -> SIMULATOR  [actions]',
    '  env.move_scout("Scout1", "N8")',
])

doc.add_paragraph()
doc.add_paragraph()

# ══════════════════════════════════════════════════════════════════
# SECTION 4 — Field-by-Field schema tables (was Section 2)
# ══════════════════════════════════════════════════════════════════
heading('4.  Field Reference — Simulator → Policy   (PolicyState)', 1)
body(
    'A fresh PolicyState is built at every callback. It is a filtered, read-only view '
    'of the simulator. Hidden faults are never included. Switches show open/closed only. '
    'Node types are distinguished: load nodes (with demand) are separated from '
    'pure topology nodes (junction points with no load attached).'
)

doc.add_paragraph()
heading('2.1  Global', 2)
schema_table(
    ['Field', 'Type', 'Values', 'Description'],
    [
        ['time', 'int', '0 … 50', 'Current simulation step (1 step = 1 hour)'],
    ],
    col_widths=[3.5, 2.5, 3.0, 8.5]
)

heading('2.2  Nodes', 2)
schema_table(
    ['Field', 'Type', 'Values', 'Description'],
    [
        ['dark_load_nodes', 'set[str]', 'e.g. {N3, N8, N10}', 'Unpowered nodes that have a load attached — PRIMARY search targets'],
        ['dark_topo_nodes', 'set[str]', 'e.g. {N9, V1, V3}', 'Unpowered pure junction nodes with no load — lower priority search'],
        ['load_nodes',      'set[str]', 'e.g. {N3, N5, N8}', 'All nodes with a load in the network (powered or not)'],
        ['global_visited',  'set[str]', 'node ids',           'Nodes physically arrived at by any agent this episode'],
        ['globally_claimed','set[str]', 'node ids',           'Nodes currently assigned as a travel target (prevents duplicates)'],
    ],
    col_widths=[3.5, 2.5, 3.5, 8.0]
)

heading('2.3  Repair Crews  (one entry per RC)', 2)
schema_table(
    ['Field', 'Type', 'Values', 'Description'],
    [
        ['rc[id].position',      'str',   'node id',                 'Current node of the RC'],
        ['rc[id].state',         'str',   'idle / moving / repairing','What the RC is doing this step'],
        ['rc[id].target',        'str',   'node id or None',         'Destination the RC is heading to'],
        ['rc[id].repair_target', 'str',   'fault id or None',        'Fault currently being repaired'],
        ['rc[id].resources',     'float', '0 … 100',                 'Repair units remaining in resource pool'],
        ['rc[id].km_left',       'float', '≥ 0',                     'Distance remaining on current travel leg (km)'],
        ['rc[id].exact.at',      'str',   'e.g. N2->N3',             'In-transit display label (switch nodes hidden)'],
        ['rc[id].exact.km_done', 'float', '≥ 0',                     'km already covered on current segment'],
        ['rc[id].stats.*',       'dict',  'see below',               'total_km, hours_moving, hours_repairing, hours_idle, faults_repaired'],
    ],
    col_widths=[4.0, 2.0, 3.5, 8.0]
)

heading('2.4  Scout  (one entry per Scout)', 2)
schema_table(
    ['Field', 'Type', 'Values', 'Description'],
    [
        ['scout[id].position',      'str',   'node id',         'Current node of the scout'],
        ['scout[id].state',         'str',   'idle / moving',   'What the scout is doing'],
        ['scout[id].target',        'str',   'node id or None', 'Destination the scout is heading to'],
        ['scout[id].km_left',       'float', '≥ 0',             'Distance remaining on current leg (km)'],
        ['scout[id].exact.at',      'str',   'e.g. N3->N8',     'In-transit display label (switch nodes hidden)'],
        ['scout[id].stats.*',       'dict',  'see below',       'total_km, hours_moving, hours_idle, nodes_visited, faults_found'],
    ],
    col_widths=[4.0, 2.0, 3.5, 8.0]
)

heading('2.5  Mobile Power Source  (one entry per MPS)', 2)
schema_table(
    ['Field', 'Type', 'Values', 'Description'],
    [
        ['mps[id].position',  'str',   'node id',                    'Current node of the MPS'],
        ['mps[id].state',     'str',   'idle / moving / connected',  'What the MPS is doing'],
        ['mps[id].target',    'str',   'node id or None',            'Destination the MPS is heading to'],
        ['mps[id].energy',    'float', '0 … 5000 kWh',              'Energy remaining in battery'],
        ['mps[id].p_limit',   'float', 'kW',                        'Maximum output power'],
        ['mps[id].km_left',   'float', '≥ 0',                       'Distance remaining on current leg (km)'],
        ['mps[id].exact.at',  'str',   'e.g. N4->N8',               'In-transit display label'],
    ],
    col_widths=[4.0, 2.0, 3.5, 8.0]
)

heading('2.6  Discovered Faults  (hidden faults NOT included)', 2)
schema_table(
    ['Field', 'Type', 'Values', 'Description'],
    [
        ['fault[id].type',               'str',   'node / edge',      'Whether fault is at a node or on a line segment'],
        ['fault[id].location',           'str',   'e.g. N3 or N3-N8', 'Where the fault is (node id, or A-B for edge)'],
        ['fault[id].state',              'str',   'active / repaired', 'Current repair status'],
        ['fault[id].progress',           'float', '0 … demand',       'Repair units completed so far'],
        ['fault[id].demand',             'float', '> 0',              'Total repair units required to fix'],
        ['fault[id].discovered_by',      'str',   'agent id',         'Which agent physically found this fault'],
        ['fault[id].discovered_at_step', 'int',   '0 … 50',           'Hour the fault was discovered'],
    ],
    col_widths=[4.5, 2.0, 3.5, 7.5]
)

heading('2.7  Loads', 2)
schema_table(
    ['Field', 'Type', 'Values', 'Description'],
    [
        ['load[id].node',  'str',   'node id',    'Which topology node this load is attached to'],
        ['load[id].state', 'str',   'on / off',   'Whether this load is currently receiving power'],
        ['load[id].P',     'float', 'kW',         'Active power demand'],
        ['load[id].Q',     'float', 'kVAr',       'Reactive power demand'],
        ['load[id].W',     'float', '1 … 10',     'Priority weight (higher = more critical)'],
    ],
    col_widths=[3.5, 2.0, 2.5, 9.5]
)

heading('2.8  Switches', 2)
schema_table(
    ['Field', 'Type', 'Values', 'Description'],
    [
        ['switch[id]', 'str', 'open / closed', 'State of each switch. No power flow info exposed — topology state only.'],
    ],
    col_widths=[3.5, 2.0, 2.5, 9.5]
)

heading('2.9  Coordination Sets', 2)
schema_table(
    ['Field', 'Type', 'Values', 'Description'],
    [
        ['rc_searching', 'set[str]', 'RC ids', 'RCs currently in search mode (not assigned to a known fault)'],
    ],
    col_widths=[3.5, 2.0, 2.5, 9.5]
)

doc.add_paragraph()

# ══════════════════════════════════════════════════════════════════
# SECTION 3 — Callbacks
# ══════════════════════════════════════════════════════════════════
heading('3.  Callbacks — When the Simulator Calls the Policy', 1)
body(
    'The simulator calls one of 6 callback methods on the policy object at specific events. '
    'Each callback receives the full PolicyState plus any event-specific arguments. '
    'The policy issues actions inside the callback by calling state.env.* methods.'
)
doc.add_paragraph()

schema_table(
    ['Callback', 'Trigger', 'Extra Arguments', 'Expected Policy Response'],
    [
        ['on_setup',            'Simulation start, before step 0',        'known_faults: bool',          'Assign all agents to initial targets'],
        ['on_scout_arrived',    'Scout reaches its destination node',      'scout_id: str,  node: str',   'Send scout to next unvisited node'],
        ['on_rc_idle',          'RC finishes repair, arrives, or has no task', 'rc: RepairCrew',          'Start repair if at fault; else assign new target'],
        ['on_fault_discovered', 'Agent physically finds a hidden fault',   '(none)',                      'Redirect moving RCs toward newly found fault'],
        ['on_mps_arrived',      'MPS reaches its destination node',        'mps: MPS,  node: str',        'Connect MPS if section is clear; else wait'],
        ['on_mps_idle',         'MPS disconnects or finishes waiting',     'mps: MPS',                    'Reconnect, reassign, or stand by'],
    ],
    col_widths=[4.0, 4.5, 4.0, 5.0]
)

doc.add_paragraph()

# ══════════════════════════════════════════════════════════════════
# SECTION 4 — Policy → Simulator (Action schema)
# ══════════════════════════════════════════════════════════════════
heading('4.  Policy → Simulator   (Action Space)', 1)
body(
    'The policy issues actions by calling methods on state.env or directly on agent objects. '
    'Multiple actions can be issued in a single callback. '
    'All actions take effect immediately within the same simulation step.'
)
doc.add_paragraph()

schema_table(
    ['Action', 'Call', 'Arguments', 'Effect'],
    [
        ['Move RC',          'state.env.move_rc(rc_id, target)',      'rc_id: str,  target: node str',  'RC starts traveling to target via shortest path'],
        ['Move Scout',       'state.env.move_scout(scout_id, target)','scout_id: str, target: node str','Scout starts traveling to target via shortest path'],
        ['Move MPS',         'mps.move_to(path, dist)',               'path: list[str], dist: float',   'MPS starts traveling along given path'],
        ['Start Repair',     'rc.start_repair(fault_id)',             'fault_id: str',                  'RC begins repairing fault (must be at fault location)'],
        ['Connect MPS',      'mps.connect()',                         '(none)',                         'MPS begins supplying power at current node'],
        ['Disconnect MPS',   'mps.disconnect()',                      '(none)',                         'MPS stops supplying power'],
        ['Open Switch',      'state.env.open_switch(switch_id)',      'switch_id: str',                 'Opens the switch — isolates that section'],
        ['Close Switch',     'state.env.close_switch(switch_id)',     'switch_id: str',                 'Closes the switch — reconnects that section'],
    ],
    col_widths=[3.0, 5.0, 4.5, 5.0]
)

doc.add_paragraph()

# ══════════════════════════════════════════════════════════════════
# SECTION 5 — Information Visibility
# ══════════════════════════════════════════════════════════════════
heading('5.  Information Visibility Rules', 1)
body(
    'The PolicyState enforces a strict information boundary — the policy sees only what '
    'a real operator would know. Hidden faults are invisible until an agent physically '
    'arrives at the fault location.'
)
doc.add_paragraph()

schema_table(
    ['Information', 'Visible to Policy?', 'Notes'],
    [
        ['Discovered fault — location, type, progress', 'YES', 'In state.discovered_faults'],
        ['Undiscovered fault — location',               'NO',  'Not in PolicyState at all — only dark nodes hint at outage zone'],
        ['Total number of faults',                      'NO',  'Policy infers from dark nodes only'],
        ['Dark nodes with loads (dark_load_nodes)',      'YES', 'Primary search targets — these are where customers are without power'],
        ['Dark nodes topology only (dark_topo_nodes)',  'YES', 'Secondary — junction nodes with no load, lower priority to visit'],
        ['Switch open/closed state',                    'YES', 'state.switches'],
        ['Switch power-flow / energized state',         'NO',  'Switches are exposed as topology only'],
        ['Load P, Q demand',                            'YES', 'state.loads[id].P and .Q'],
        ['Agent exact in-transit position',             'YES', 'state.*.exact.at  e.g. N2->N3'],
        ['Shortest path graph (TGraph)',                'YES', 'state.tgraph — policy can query paths freely'],
    ],
    col_widths=[6.5, 3.5, 7.5]
)

doc.add_paragraph()

# ══════════════════════════════════════════════════════════════════
# SECTION 6 — Discovery Mechanism
# ══════════════════════════════════════════════════════════════════
heading('6.  Fault Discovery Mechanism', 1)
body(
    'A fault transitions from hidden to discovered only when an agent physically arrives '
    'at the fault location. This is enforced by env._check_discovery(), called automatically '
    'by the simulator after every agent movement step — the policy cannot call it directly.'
)
doc.add_paragraph()

schema_table(
    ['Step', 'What Happens'],
    [
        ['1', 'Agent arrives at a node (RC, Scout, or MPS)'],
        ['2', 'Simulator calls _check_discovery(position, agent_id, agent_type)'],
        ['3', 'For each undiscovered fault: if agent position matches fault location → fault revealed'],
        ['4', 'fault.discovered = True,  fault.discovered_by = agent_id,  fault.discovered_at_step = time'],
        ['5', 'Simulator immediately fires on_fault_discovered(state) — PolicyState now includes the new fault'],
        ['6', 'Policy reads state.discovered_faults and can redirect agents to the new fault'],
    ],
    col_widths=[1.5, 16.0]
)

doc.add_paragraph()

# ══════════════════════════════════════════════════════════════════
# Save
# ══════════════════════════════════════════════════════════════════
out = 'DSR_Policy_Schema_v2.docx'
doc.save(out)
print(f'Saved: {out}')
