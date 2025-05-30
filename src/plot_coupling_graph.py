#!/usr/bin/env python3
"""Visualize logical qubit couplings as a graph."""
from __future__ import annotations

import json
import os
from typing import Dict, List

import networkx as nx
import matplotlib.pyplot as plt

SUBSCRIPT_MAP = str.maketrans("₀₁₂₃₄₅₆₇₈₉", "0123456789")


def logical_index(label: str) -> int:
    """Return integer index from a state label like ``ψ₅``."""
    digits = label.replace("ψ", "").translate(SUBSCRIPT_MAP)
    try:
        return int(digits)
    except ValueError:
        return 0


def load_mapping(path: str) -> Dict[str, Dict[str, float]]:
    """Load mapping file and return dict keyed by logical state."""
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    with open(path) as fh:
        data = json.load(fh)
    data.sort(key=lambda d: logical_index(d.get("logical_state", "ψ0")))
    return {item["logical_state"]: item for item in data}


def load_couplings(path: str) -> List[Dict[str, object]]:
    """Return list of coupled edges from ``path``."""
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    with open(path) as fh:
        data = json.load(fh)
    data.sort(
        key=lambda d: (
            logical_index(d.get("q1", "ψ0")),
            logical_index(d.get("q2", "ψ0")),
        )
    )
    return [item for item in data if item.get("coupled", False)]


def build_graph(nodes: Dict[str, Dict[str, float]], edges: List[Dict[str, object]]) -> nx.Graph:
    """Construct NetworkX graph from node/edge data."""
    G = nx.Graph()
    for state, info in nodes.items():
        G.add_node(state, pos=(info["x"], info["y"]))
    for e in edges:
        q1 = e["q1"]
        q2 = e["q2"]
        w = float(e.get("distance", 0.0))
        G.add_edge(q1, q2, weight=w)
    return G


def plot_graph(G: nx.Graph, path: str) -> None:
    """Save graph image to ``path``."""
    pos = nx.get_node_attributes(G, "pos")
    weights = [G[u][v]["weight"] for u, v in G.edges()]
    max_w = max(weights) if weights else 1.0
    widths = [1.0 + 2.0 * (1.0 - w / max_w) for w in weights]

    plt.figure(figsize=(6, 6))
    nx.draw_networkx_nodes(G, pos, node_color="#eeeeff", edgecolors="#000000")
    nx.draw_networkx_labels(G, pos)
    nx.draw_networkx_edges(
        G,
        pos,
        width=widths,
        edge_color=weights,
        edge_cmap=plt.cm.Blues,
    )
    plt.axis("equal")
    plt.axis("off")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    plt.tight_layout()
    plt.savefig(path)
    plt.close()


def write_dot(G: nx.Graph, path: str) -> None:
    """Write Graphviz DOT representation to ``path``."""
    from networkx.drawing.nx_pydot import write_dot

    os.makedirs(os.path.dirname(path), exist_ok=True)
    write_dot(G, path)


def main() -> None:
    mapping_path = "result/logic_physical_map.json"
    coupling_path = "result/coupling_candidates.json"
    png_path = "docs/plot/coupling_graph.png"
    dot_path = "result/coupling_graph.dot"

    nodes = load_mapping(mapping_path)
    edges = load_couplings(coupling_path)
    G = build_graph(nodes, edges)
    plot_graph(G, png_path)
    write_dot(G, dot_path)
    print(f"Wrote {png_path} and {dot_path}")


if __name__ == "__main__":
    main()
