"""
Visualizer
==========
Clean white-background network visualization.

Shows:
  - Node types + power ON/OFF
  - Edge states (live / faulted / open)
  - Agent positions: RC (triangle), Scout (star), MPS (square)
  - Agent travel paths (dashed lines)
  - Fault markers: ? hidden | X discovered | ✓ repaired
  - Minimal right panel: time, power, faults, agent states
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
from .config.ieee13_cases import IEEE13Network


# ── Colors (white background palette) ────────────────────────
NODE_COLORS = {
    'GRID':     '#2ecc71',   # green
    'BUS':      '#95a5a6',   # light grey
    'LOAD_ON':  '#3498db',   # blue  — has power
    'LOAD_OFF': '#e74c3c',   # red   — no power
    'SWITCH':   '#e67e22',   # orange
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


def _draw_path(ax, path, node_pos, color, style='--', lw=2.0):
    if not path or len(path) < 2:
        return
    xs = [node_pos[n][0] for n in path if n in node_pos]
    ys = [node_pos[n][1] for n in path if n in node_pos]
    if len(xs) >= 2:
        ax.plot(xs, ys, color=color, linewidth=lw,
                linestyle=style, alpha=0.6, zorder=2)


def draw_network(env, title: str = '', save_path: str = None, show: bool = True):
    net = IEEE13Network
    pos = net.NODE_POS

    # ── Build graph ───────────────────────────────────────────
    G = nx.Graph()
    for node_id in net.NODES:
        G.add_node(node_id)

    edge_colors = []
    edge_widths = []
    for eid, edge in env.egraph.edges.items():
        state = edge['state']
        G.add_edge(edge['from'], edge['to'])
        edge_colors.append(EDGE_COLORS.get(state, '#bdc3c7'))
        edge_widths.append(3.5 if state == 'faulted' else 1.8)

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
        else:
            node_colors.append(NODE_COLORS.get(ntype, '#95a5a6'))
            node_sizes.append(700)

    # ── Figure: network (left) + info panel (right) ───────────
    fig, (ax, ax_info) = plt.subplots(
        1, 2, figsize=(20, 9),
        gridspec_kw={'width_ratios': [3.2, 1]}
    )
    fig.patch.set_facecolor('white')
    ax.set_facecolor('#f9f9f9')
    ax_info.set_facecolor('white')
    ax_info.axis('off')

    # ── Draw edges ────────────────────────────────────────────
    nx.draw_networkx_edges(G, pos, ax=ax,
                           edge_color=edge_colors,
                           width=edge_widths, alpha=0.9)

    # ── Draw nodes ────────────────────────────────────────────
    nx.draw_networkx_nodes(G, pos, ax=ax,
                           node_color=node_colors,
                           node_size=node_sizes,
                           linewidths=1.5,
                           edgecolors='white')

    nx.draw_networkx_labels(G, pos, ax=ax,
                            font_size=7.5, font_weight='bold',
                            font_color='white')

    # ── Agent paths ───────────────────────────────────────────
    for rc in env.rcs.values():
        if rc.path and len(rc.path) >= 2:
            _draw_path(ax, rc.path, pos, AGENT_COLORS['RC'], '--', 2.2)

    for scout in env.scouts.values():
        if scout.path and len(scout.path) >= 2:
            _draw_path(ax, scout.path, pos, AGENT_COLORS['Scout'], '-.', 2.2)

    for mps in env.mps.values():
        if mps.path and len(mps.path) >= 2:
            _draw_path(ax, mps.path, pos, AGENT_COLORS['MPS'], ':', 2.2)

    # ── Agent markers ─────────────────────────────────────────
    for rc in env.rcs.values():
        if rc.position in pos:
            x, y = pos[rc.position]
            ax.plot(x, y, '^', markersize=13,
                    color=AGENT_COLORS['RC'],
                    markeredgecolor='white', markeredgewidth=1.2, zorder=5)
            ax.text(x + 0.3, y + 0.35, rc.id,
                    fontsize=8, color=AGENT_COLORS['RC'],
                    fontweight='bold', zorder=6)

    for scout in env.scouts.values():
        if scout.position in pos:
            x, y = pos[scout.position]
            ax.plot(x, y, '*', markersize=14,
                    color=AGENT_COLORS['Scout'],
                    markeredgecolor='white', markeredgewidth=1.0, zorder=5)
            ax.text(x - 0.5, y - 0.4, scout.id,
                    fontsize=8, color=AGENT_COLORS['Scout'],
                    fontweight='bold', zorder=6)

    for mps in env.mps.values():
        if mps.position in pos:
            x, y = pos[mps.position]
            mk = 's' if mps.state == 'connected' else 'D'
            ax.plot(x, y, mk, markersize=12,
                    color=AGENT_COLORS['MPS'],
                    markeredgecolor='white', markeredgewidth=1.2, zorder=5)
            ax.text(x + 0.3, y - 0.45, mps.id,
                    fontsize=8, color=AGENT_COLORS['MPS'],
                    fontweight='bold', zorder=6)

    # ── Fault labels ──────────────────────────────────────────
    for dp in env.faults.values():
        fault_node = dp.node if dp.type == 'node' else (dp.edge[0] if dp.edge else None)
        if fault_node and fault_node in pos:
            x, y = pos[fault_node]
            if dp.state == 'repaired':
                sym, color = '✓', '#27ae60'
            elif not dp.discovered:
                sym, color = '?', '#e67e22'
            else:
                sym, color = '✗', '#e74c3c'
            ax.text(x, y + 0.55, f'{sym} {dp.id}',
                    fontsize=9, color=color, fontweight='bold',
                    ha='center', zorder=7,
                    bbox=dict(boxstyle='round,pad=0.2',
                              facecolor='white', alpha=0.85,
                              edgecolor=color, linewidth=1.0))

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
        (NODE_COLORS['GRID'],     'Grid source'),
        (NODE_COLORS['LOAD_ON'],  'Load — ON'),
        (NODE_COLORS['LOAD_OFF'], 'Load — OFF'),
        (NODE_COLORS['BUS'],      'Bus / Switch'),
        (EDGE_COLORS['closed'],   'Line: live'),
        (EDGE_COLORS['faulted'],  'Line: faulted'),
        (AGENT_COLORS['RC'],      'RC  ▲  (-- path)'),
        (AGENT_COLORS['Scout'],   'Scout ★  (-. path)'),
        (AGENT_COLORS['MPS'],     'MPS  ■  (.. path)'),
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
