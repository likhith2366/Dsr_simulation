"""
Visualizer
==========
Draws the IEEE-13 network using matplotlib + networkx.
Shows: node types, edge states, RC/Scout positions, load ON/OFF, faults.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
from typing import Dict
from .config.ieee13_cases import IEEE13Network


# ── Colors ────────────────────────────────────────────────────
NODE_COLORS = {
    'GRID':   '#2ecc71',   # green
    'BUS':    '#95a5a6',   # grey
    'LOAD_ON':  '#3498db', # blue  (load with power)
    'LOAD_OFF': '#e74c3c', # red   (load, no power)
    'SWITCH': '#f39c12',   # orange
}

EDGE_COLORS = {
    'closed':  '#2c3e50',  # dark  (live)
    'open':    '#bdc3c7',  # light grey (switched off)
    'faulted': '#e74c3c',  # red   (broken)
}


def draw_network(env, title: str = '', save_path: str = None, show: bool = True):
    """
    Draw the current state of the simulation.

    Args:
        env:       DSREnvironment instance
        title:     Plot title
        save_path: If provided, save figure to this path
        show:      If True, display the plot
    """
    G = nx.Graph()
    net = IEEE13Network
    pos = net.NODE_POS

    # Add nodes
    for node_id, node_type in net.NODES.items():
        G.add_node(node_id)

    # Add edges
    edge_color_map = []
    edge_width_map = []
    for eid, edge in env.egraph.edges.items():
        state = edge['state']
        G.add_edge(edge['from'], edge['to'])
        edge_color_map.append(EDGE_COLORS.get(state, '#bdc3c7'))
        edge_width_map.append(3.0 if state == 'faulted' else 1.5)

    # Node colors
    node_color_map = []
    for node_id in G.nodes():
        node_type = net.NODES.get(node_id, 'BUS')
        if node_type == 'LOAD':
            # Check if load is ON
            load_on = any(
                l.node == node_id and l.state == 'on'
                for l in env.loads.values()
            )
            node_color_map.append(NODE_COLORS['LOAD_ON'] if load_on else NODE_COLORS['LOAD_OFF'])
        else:
            node_color_map.append(NODE_COLORS.get(node_type, '#95a5a6'))

    # ── Draw ──────────────────────────────────────────────────
    fig, ax = plt.subplots(1, 1, figsize=(16, 10))
    ax.set_facecolor('#f8f9fa')
    fig.patch.set_facecolor('#f8f9fa')

    nx.draw_networkx_edges(G, pos, ax=ax,
                           edge_color=edge_color_map,
                           width=edge_width_map,
                           alpha=0.8)

    nx.draw_networkx_nodes(G, pos, ax=ax,
                           node_color=node_color_map,
                           node_size=600,
                           alpha=0.95)

    nx.draw_networkx_labels(G, pos, ax=ax,
                            font_size=8,
                            font_weight='bold',
                            font_color='white')

    # ── Overlay: RC positions ─────────────────────────────────
    for rc in env.rcs.values():
        if rc.position in pos:
            x, y = pos[rc.position]
            ax.annotate(rc.id, (x, y),
                        xytext=(x + 0.3, y + 0.3),
                        fontsize=8, color='#8e44ad', fontweight='bold',
                        arrowprops=dict(arrowstyle='->', color='#8e44ad', lw=1.5))

    # ── Overlay: Scout positions ──────────────────────────────
    for scout in env.scouts.values():
        if scout.position in pos:
            x, y = pos[scout.position]
            ax.annotate(scout.id, (x, y),
                        xytext=(x - 0.5, y - 0.4),
                        fontsize=8, color='#e67e22', fontweight='bold',
                        arrowprops=dict(arrowstyle='->', color='#e67e22', lw=1.5))

    # ── Overlay: Fault markers ────────────────────────────────
    for dp in env.faults.values():
        fault_node = dp.node if dp.type == 'node' else (dp.edge[0] if dp.edge else None)
        if fault_node and fault_node in pos:
            x, y = pos[fault_node]
            marker = '✓' if dp.state == 'repaired' else ('?' if not dp.discovered else '✗')
            color  = '#27ae60' if dp.state == 'repaired' else ('#e67e22' if not dp.discovered else '#e74c3c')
            ax.text(x, y + 0.5, f'{marker}{dp.id}',
                    fontsize=9, color=color, fontweight='bold', ha='center')

    # ── Stats box ─────────────────────────────────────────────
    loads_on   = sum(1 for l in env.loads.values() if l.state == 'on')
    loads_tot  = len(env.loads)
    reward     = env.get_reward()
    max_reward = sum(l.W * l.P for l in env.loads.values())
    disc       = sum(1 for dp in env.faults.values() if dp.discovered)
    total_dp   = len(env.faults)

    stats = (f"Time: {env.time}  |  "
             f"Loads: {loads_on}/{loads_tot} ON  |  "
             f"Reward: {reward:.0f}/{max_reward:.0f}  |  "
             f"Faults found: {disc}/{total_dp}")

    ax.text(0.5, -0.02, stats, transform=ax.transAxes,
            fontsize=10, ha='center', va='top',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    # ── Legend ────────────────────────────────────────────────
    legend_items = [
        mpatches.Patch(color=NODE_COLORS['GRID'],     label='Grid'),
        mpatches.Patch(color=NODE_COLORS['BUS'],      label='Bus'),
        mpatches.Patch(color=NODE_COLORS['LOAD_ON'],  label='Load ON'),
        mpatches.Patch(color=NODE_COLORS['LOAD_OFF'], label='Load OFF'),
        mpatches.Patch(color=NODE_COLORS['SWITCH'],   label='Switch'),
        mpatches.Patch(color=EDGE_COLORS['closed'],   label='Line: live'),
        mpatches.Patch(color=EDGE_COLORS['faulted'],  label='Line: faulted'),
        mpatches.Patch(color='#8e44ad', label='RC position'),
        mpatches.Patch(color='#e67e22', label='Scout position'),
    ]
    ax.legend(handles=legend_items, loc='upper left',
              fontsize=8, framealpha=0.9)

    ax.set_title(title or f'{env.case_name} — Step {env.time}',
                 fontsize=13, fontweight='bold', pad=15)
    ax.axis('off')
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f'  Saved: {save_path}')

    if show:
        plt.show()

    plt.close()
