#!/usr/bin/env python3
"""Visualize semantic-weighted coupling graph."""
from __future__ import annotations

import json
import os
from typing import Dict, List

import matplotlib.pyplot as plt
import networkx as nx

SUBSCRIPT_MAP = str.maketrans("₀₁₂₃₄₅₆₇₈₉", "0123456789")


def logical_index(label: str) -> int:
    digits = label.replace("ψ", "").translate(SUBSCRIPT_MAP)
    try:
        return int(digits)
    except ValueError:
        return 0


def load_nodes(path: str) -> Dict[str, Dict[str, float]]:
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    data.sort(key=lambda d: logical_index(d.get("logical_state", "ψ0")))
    return {d["logical_state"]: d for d in data}


def load_edges(path: str) -> List[Dict[str, object]]:
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    data.sort(
        key=lambda d: (logical_index(d.get("q1", "ψ0")), logical_index(d.get("q2", "ψ0")))
    )
    return [e for e in data if float(e.get("semantic_weight", 0)) > 0]


def build_graph(nodes: Dict[str, Dict[str, float]], edges: List[Dict[str, object]]) -> nx.Graph:
    G = nx.Graph()
    for state, info in nodes.items():
        G.add_node(state, pos=(info["x"], info["y"]))
    for e in edges:
        q1 = e["q1"]
        q2 = e["q2"]
        w = float(e.get("semantic_weight", 0))
        G.add_edge(q1, q2, weight=w)
    return G


def plot_graph(G: nx.Graph, path: str) -> None:
    pos = nx.get_node_attributes(G, "pos")
    weights = [G[u][v]["weight"] for u, v in G.edges()]
    max_w = max(weights) if weights else 1.0
    widths = [w * 3 for w in weights]

    plt.figure(figsize=(6, 6))
    nx.draw_networkx_nodes(G, pos, node_color="#f0f0ff", edgecolors="#000000")
    nx.draw_networkx_labels(G, pos)
    nx.draw_networkx_edges(
        G,
        pos,
        width=widths,
        edge_color=weights,
        edge_cmap=plt.cm.Blues,
        edge_vmin=0,
        edge_vmax=max_w,
    )
    plt.axis("equal")
    plt.axis("off")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    plt.tight_layout()
    plt.savefig(path)
    plt.close()


def main() -> None:
    map_path = "result/logic_physical_map.json"
    edge_path = "result/semantic_coupling_map.json"
    png_path = "docs/plot/semantic_coupling_graph.png"

    nodes = load_nodes(map_path)
    edges = load_edges(edge_path)
    G = build_graph(nodes, edges)
    plot_graph(G, png_path)
    print(f"Wrote {png_path}")


if __name__ == "__main__":
    main()
