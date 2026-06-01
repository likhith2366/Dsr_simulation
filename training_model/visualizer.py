"""
Visualizer
==========
Clean white-background network visualization.

Shows:
  - Node types + power ON/OFF
  - Edge states (live / faulted / open)
  - Road-only shortcuts (dashed grey) — agents can travel but no power line
  - Distance labels on every edge and road shortcut
  - Agent positions: RC (triangle), Scout (star), MPS (square)
  - Agent travel paths (dashed lines)
  - Fault markers: ? hidden | X discovered | ✓ repaired
  - Minimal right panel: time, power, faults, agent states
"""

import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
from .config.ieee13_cases import IEEE13Network


# Module-level edge km for old network (kept for any direct callers)
# draw_network() builds its own lookup dynamically from env.network

# ── Colors (white background palette) ────────────────────────
NODE_COLORS = {
    'GRID':         '#2ecc71',   # green
    'BUS':          '#95a5a6',   # light grey
    'LOAD_ON':      '#3498db',   # blue  — has power
    'LOAD_OFF':     '#e74c3c',   # red   — no power
    'SWITCH_CLOSED': '#2ecc71',  # green — normally closed sectionalizer
    'SWITCH_OPEN':   '#e74c3c',  # red   — open (tie or tripped)
    'SWITCH_FAULT':  '#e67e22',  # orange — faulted switch
}

EDGE_COLORS = {
    'closed':  '#2c3e50',   # dark grey — live
    'open':    '#bdc3c7',   # light grey — switched off
    'faulted': '#e74c3c',   # red — broken
}

AGENT_COLORS = {
    'RC':    '#8e44ad',   # purple
    'Scout': '#e67e22',   # orange
    'MPS':   '#16a085',   # teal
}

def _switch_color(node_id, egraph):
    """Return color for a SWITCH node based on live EGraph edge states."""
    state = 'closed'
    for edge in egraph.edges.values():
        if edge['from'] == node_id or edge['to'] == node_id:
            if edge['state'] == 'faulted':
                return NODE_COLORS['SWITCH_FAULT']
            if edge['state'] == 'open':
                state = 'open'
    return NODE_COLORS['SWITCH_CLOSED'] if state == 'closed' else NODE_COLORS['SWITCH_OPEN']


def _build_edge_km(net):
    """Build {(from, to): km} lookup from a network class."""
    km = {}
    for _eid, _fn, _tn, _km, _st in net.EDGES:
        km[(_fn, _tn)] = _km
        km[(_tn, _fn)] = _km
    return km


def _build_road_shortcuts(net):
    """Return road-only edges (not in EDGES) as [(from, to, km)]."""
    elec_pairs = set()
    for _eid, fn, tn, _km, _st in net.EDGES:
        elec_pairs.add((fn, tn))
        elec_pairs.add((tn, fn))
    shortcuts = []
    seen = set()
    for _rid, fn, tn, km in net.ROADS:
        if (fn, tn) not in elec_pairs and (fn, tn) not in seen:
            shortcuts.append((fn, tn, km))
            seen.add((fn, tn))
            seen.add((tn, fn))
    return shortcuts


def _label_offset(x1, y1, x2, y2, offset=0.28):
    """Midpoint shifted perpendicular to the edge (always toward upper/right side)."""
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    dx, dy = x2 - x1, y2 - y1
    L = math.sqrt(dx * dx + dy * dy) or 1
    px, py = -dy / L, dx / L          # perpendicular unit vector
    # Flip so label ends up above or to the right of the edge
    if py < 0 or (py == 0 and px < 0):
        px, py = -px, -py
    return mx + px * offset, my + py * offset


def _draw_path(ax, path, node_pos, color, style='--', lw=2.0):
    if not path or len(path) < 2:
        return
    xs = [node_pos[n][0] for n in path if n in node_pos]
    ys = [node_pos[n][1] for n in path if n in node_pos]
    if len(xs) >= 2:
        ax.plot(xs, ys, color=color, linewidth=lw,
                linestyle=style, alpha=0.6, zorder=2)


def draw_network(env, title: str = '', save_path: str = None, show: bool = True):
    net = getattr(env, 'network', IEEE13Network)
    pos = net.NODE_POS
    _EDGE_KM        = _build_edge_km(net)
    _ROAD_SHORTCUTS = _build_road_shortcuts(net)

    # ── Build electrical graph ────────────────────────────────
    G = nx.Graph()
    for node_id in net.NODES:
        G.add_node(node_id)

    edge_colors = []
    edge_widths = []
    for eid, edge in env.egraph.edges.items():
        fn, tn = edge['from'], edge['to']
        state = edge['state']
        G.add_edge(fn, tn)
        edge_colors.append(EDGE_COLORS.get(state, '#bdc3c7'))
        edge_widths.append(4.0 if state == 'faulted' else 2.5)

    # ── Node colors ───────────────────────────────────────────
    node_colors = []
    node_sizes  = []
    for node_id in G.nodes():
        ntype = net.NODES.get(node_id, 'BUS')
        if ntype == 'LOAD':
            on = any(l.node == node_id and l.state == 'on'
                     for l in env.loads.values())
            node_colors.append(NODE_COLORS['LOAD_ON'] if on else NODE_COLORS['LOAD_OFF'])
            node_sizes.append(900)
        elif ntype == 'SWITCH':
            node_colors.append(_switch_color(node_id, env.egraph))
            node_sizes.append(650)
        else:
            node_colors.append(NODE_COLORS.get(ntype, '#95a5a6'))
            node_sizes.append(700)

    # ── Figure: network (left) + info panel (right) ───────────
    fig, (ax, ax_info) = plt.subplots(
        1, 2, figsize=(22, 10),
        gridspec_kw={'width_ratios': [3.2, 1]}
    )
    fig.patch.set_facecolor('white')
    ax.set_facecolor('#f9f9f9')
    ax_info.set_facecolor('white')
    ax_info.axis('off')

    # ── Agent paths (drawn first, behind everything) ─────────
    for rc in env.rcs.values():
        if rc.path and len(rc.path) >= 2:
            _draw_path(ax, rc.path, pos, AGENT_COLORS['RC'], '--', 1.8)

    for scout in env.scouts.values():
        if scout.path and len(scout.path) >= 2:
            _draw_path(ax, scout.path, pos, AGENT_COLORS['Scout'], '-.', 1.8)

    for mps in env.mps.values():
        if mps.path and len(mps.path) >= 2:
            _draw_path(ax, mps.path, pos, AGENT_COLORS['MPS'], ':', 1.8)

    # ── Draw electrical edges (solid, on top of paths) ────────
    nx.draw_networkx_edges(G, pos, ax=ax,
                           edge_color=edge_colors,
                           width=edge_widths, alpha=0.9)

    # ── Distance labels on electrical edges ───────────────────
    for eid, edge in env.egraph.edges.items():
        fn, tn = edge['from'], edge['to']
        km = _EDGE_KM.get((fn, tn))
        if km is None or fn not in pos or tn not in pos:
            continue
        x1, y1 = pos[fn]
        x2, y2 = pos[tn]
        lx, ly = _label_offset(x1, y1, x2, y2, 0.28)
        ax.text(lx, ly, f'{km}km', fontsize=6.5,
                color='#2c3e50', ha='center', va='center',
                zorder=5,
                bbox=dict(boxstyle='round,pad=0.1',
                          facecolor='white', alpha=0.85,
                          edgecolor='none'))

    # ── Draw nodes — circles for non-switches, squares for switches ──
    non_switch_nodes = [n for n in G.nodes() if net.NODES.get(n) != 'SWITCH']
    switch_nodes     = [n for n in G.nodes() if net.NODES.get(n) == 'SWITCH']

    node_color_map = {n: c for n, c in zip(G.nodes(), node_colors)}
    node_size_map  = {n: s for n, s in zip(G.nodes(), node_sizes)}

    if non_switch_nodes:
        nx.draw_networkx_nodes(G, pos, ax=ax,
                               nodelist=non_switch_nodes,
                               node_color=[node_color_map[n] for n in non_switch_nodes],
                               node_size=[node_size_map[n] for n in non_switch_nodes],
                               node_shape='o',
                               linewidths=1.5, edgecolors='white')
    if switch_nodes:
        nx.draw_networkx_nodes(G, pos, ax=ax,
                               nodelist=switch_nodes,
                               node_color=[node_color_map[n] for n in switch_nodes],
                               node_size=[node_size_map[n] for n in switch_nodes],
                               node_shape='s',
                               linewidths=1.5, edgecolors='white')

    nx.draw_networkx_labels(G, pos, ax=ax,
                            font_size=9, font_weight='bold',
                            font_color='white')

    # ── Draw road shortcuts LAST (on top of everything) ──────────────
    # N9-V4 drawn solid grey; V1-N7, N12-V2, N4-N8 drawn dashed.
    SOLID_ROAD_PAIRS = {('N9', 'V4'), ('V4', 'N9')}
    for fn, tn, km in _ROAD_SHORTCUTS:
        if fn in pos and tn in pos:
            x1, y1 = pos[fn]
            x2, y2 = pos[tn]
            is_solid = (fn, tn) in SOLID_ROAD_PAIRS
            ax.plot([x1, x2], [y1, y2],
                    color='#888888', linewidth=2.0,
                    linestyle='-' if is_solid else (0, (4, 2)),
                    alpha=0.9, zorder=6)
            lx, ly = _label_offset(x1, y1, x2, y2, 0.22)
            ax.text(lx, ly, f'{km}km', fontsize=6.5,
                    color='#555555', ha='center', va='center',
                    zorder=7,
                    bbox=dict(boxstyle='round,pad=0.1',
                              facecolor='white', alpha=0.9,
                              edgecolor='none'))


    # ── Agent markers (grouped beside nodes, never on top) ────
    from collections import defaultdict

    def _agent_xy(agent_pos, on_edge=None):
        """Return (x, y) for an agent — midpoint if on_edge, else node position."""
        if on_edge:
            n1, n2 = on_edge
            if n1 in pos and n2 in pos:
                return ((pos[n1][0] + pos[n2][0]) / 2,
                        (pos[n1][1] + pos[n2][1]) / 2)
        return pos.get(agent_pos)

    # Collect agents keyed by rounded (x,y) so we can group co-located agents
    agents_at = defaultdict(list)

    for rc in env.rcs.values():
        xy = _agent_xy(rc.position, rc.on_edge)
        if xy:
            agents_at[(round(xy[0], 3), round(xy[1], 3))].append(
                (rc.id, AGENT_COLORS['RC'], '^'))

    for scout in env.scouts.values():
        xy = _agent_xy(scout.position, getattr(scout, 'on_edge', None))
        if xy:
            agents_at[(round(xy[0], 3), round(xy[1], 3))].append(
                (scout.id, AGENT_COLORS['Scout'], '*'))

    for mps in env.mps.values():
        xy = _agent_xy(mps.position)
        if xy:
            mk = 's' if mps.state == 'connected' else 'D'
            agents_at[(round(xy[0], 3), round(xy[1], 3))].append(
                (mps.id, AGENT_COLORS['MPS'], mk))

    for (nx_, ny_), agent_list in agents_at.items():
        for i, (aid, color, marker) in enumerate(agent_list):
            ox = nx_ + 0.95
            oy = ny_ + 0.55 - i * 0.65
            ax.plot([nx_, ox], [ny_, oy], color=color,
                    linewidth=0.8, alpha=0.5, zorder=4)
            ax.plot(ox, oy, marker, markersize=11,
                    color=color, markeredgecolor='white',
                    markeredgewidth=1.0, zorder=6)
            ax.text(ox + 0.22, oy, aid, fontsize=7.5, color=color,
                    fontweight='bold', va='center', zorder=7)

    # ── Fault markers ─────────────────────────────────────────
    for dp in env.faults.values():
        if dp.type == 'node' and dp.node in pos:
            fx, fy = pos[dp.node]
        elif dp.type == 'edge' and dp.edge:
            n1, n2 = dp.edge[0], dp.edge[1]
            if n1 in pos and n2 in pos:
                fx = (pos[n1][0] + pos[n2][0]) / 2
                fy = (pos[n1][1] + pos[n2][1]) / 2
            elif n1 in pos:
                fx, fy = pos[n1]
            else:
                continue
        else:
            continue

        if dp.state == 'repaired':
            sym, color = '✓', '#27ae60'
        elif not dp.discovered:
            sym, color = '?', '#e67e22'
        else:
            sym, color = '✗', '#e74c3c'

        # Draw marker directly on the fault location (node center or edge midpoint)
        ax.scatter([fx], [fy], s=320, color=color, alpha=0.85,
                   zorder=9, marker='X' if dp.discovered else 'o',
                   edgecolors='white', linewidths=1.2)
        # Label just above the marker
        ax.text(fx, fy + 0.52, f'{dp.id}',
                fontsize=8.5, color=color, fontweight='bold',
                ha='center', va='bottom', zorder=10,
                bbox=dict(boxstyle='round,pad=0.18',
                          facecolor='white', alpha=0.92,
                          edgecolor=color, linewidth=1.5))

    ax.set_title(title or f'{env.case_name} — Step {env.time}',
                 fontsize=13, fontweight='bold', pad=12)
    ax.axis('off')

    # ── Right panel — minimal info ────────────────────────────
    loads_on   = sum(1 for l in env.loads.values() if l.state == 'on')
    loads_tot  = len(env.loads)
    reward     = env.get_reward()
    max_reward = sum(l.W * l.P for l in env.loads.values())
    disc       = sum(1 for dp in env.faults.values() if dp.discovered)
    repaired   = sum(1 for dp in env.faults.values() if dp.state == 'repaired')
    total_dp   = len(env.faults)

    def section(ax, y, heading):
        ax.text(0.05, y, heading, transform=ax.transAxes,
                fontsize=10, fontweight='bold', color='#2c3e50', va='top')
        ax.plot([0.05, 0.95], [y - 0.015, y - 0.015],
                color='#bdc3c7', linewidth=0.8,
                transform=ax.transAxes)
        return y - 0.04

    def row(ax, y, label, value, vcolor='#2c3e50'):
        ax.text(0.08, y, label, transform=ax.transAxes,
                fontsize=9, color='#7f8c8d', va='top')
        ax.text(0.92, y, str(value), transform=ax.transAxes,
                fontsize=9, fontweight='bold', color=vcolor,
                va='top', ha='right')
        return y - 0.038

    y = 0.95
    y = section(ax_info, y, 'STATUS')
    y = row(ax_info, y, 'Time', f'{env.time} h')
    y = row(ax_info, y, 'Case', env.case_name)
    y -= 0.02

    y = section(ax_info, y, 'POWER')
    load_color = '#27ae60' if loads_on == loads_tot else '#e74c3c'
    y = row(ax_info, y, 'Loads ON', f'{loads_on} / {loads_tot}', load_color)
    y = row(ax_info, y, 'Reward', f'{reward:.0f} / {max_reward:.0f}')
    y -= 0.02

    y = section(ax_info, y, 'FAULTS')
    y = row(ax_info, y, 'Total', total_dp)
    y = row(ax_info, y, 'Discovered', disc, '#e67e22' if disc < total_dp else '#27ae60')
    y = row(ax_info, y, 'Repaired', repaired, '#27ae60' if repaired == total_dp else '#e74c3c')
    y -= 0.02

    y = section(ax_info, y, 'AGENTS')
    for rc in env.rcs.values():
        state_color = '#e74c3c' if rc.state == 'repairing' else \
                      '#3498db' if rc.state == 'moving' else '#7f8c8d'
        y = row(ax_info, y, rc.id, f'{rc.state} @ {rc.position}', state_color)
        if rc.target and rc.state == 'moving':
            y = row(ax_info, y, '  → ', rc.target, '#8e44ad')
    for scout in env.scouts.values():
        state_color = '#3498db' if scout.state == 'moving' else '#7f8c8d'
        y = row(ax_info, y, scout.id, f'{scout.state} @ {scout.position}', state_color)
        if scout.target and scout.state == 'moving':
            y = row(ax_info, y, '  → ', scout.target, '#e67e22')
    for mps in env.mps.values():
        state_color = '#27ae60' if mps.state == 'connected' else \
                      '#3498db' if mps.state == 'moving' else '#7f8c8d'
        y = row(ax_info, y, mps.id, f'{mps.state} @ {mps.position}', state_color)
    y -= 0.02

    # Legend
    y = section(ax_info, y, 'LEGEND')
    legend_items = [
        (NODE_COLORS['GRID'],          'Grid source'),
        (NODE_COLORS['LOAD_ON'],       'Load — ON'),
        (NODE_COLORS['LOAD_OFF'],      'Load — OFF'),
        (NODE_COLORS['BUS'],           'Bus node'),
        (NODE_COLORS['SWITCH_CLOSED'], 'Switch — closed (green)'),
        (NODE_COLORS['SWITCH_OPEN'],   'Switch — open (red)'),
        (EDGE_COLORS['closed'],        'Line: live (power)'),
        (EDGE_COLORS['open'],          'Line: open switch'),
        (EDGE_COLORS['faulted'],       'Line: faulted'),
        ('#aaaaaa',                    'Road only (no wire)'),
        (AGENT_COLORS['RC'],           'RC  ▲  (-- path)'),
        (AGENT_COLORS['Scout'],        'Scout ★  (-. path)'),
        (AGENT_COLORS['MPS'],          'MPS  ■  (.. path)'),
    ]
    for color, label in legend_items:
        if y < 0.02:
            break
        rect = mpatches.FancyBboxPatch(
            (0.06, y - 0.022), 0.08, 0.020,
            boxstyle='round,pad=0.01',
            facecolor=color, edgecolor='none',
            transform=ax_info.transAxes
        )
        ax_info.add_patch(rect)
        ax_info.text(0.18, y - 0.012, label,
                     transform=ax_info.transAxes,
                     fontsize=8, color='#2c3e50', va='center')
        y -= 0.038

    # Divider line between panels
    fig.add_artist(plt.Line2D(
        [0.735, 0.735], [0.05, 0.95],
        transform=fig.transFigure,
        color='#bdc3c7', linewidth=1.0
    ))

    plt.tight_layout(pad=1.5)

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight',
                    facecolor='white')
        print(f'  Saved: {save_path}')

    if show:
        plt.show()

    plt.close(fig)
