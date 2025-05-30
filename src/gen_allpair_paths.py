#!/usr/bin/env python3
"""Generate shortest path matrix between all logical states."""
from __future__ import annotations

import json
import os
from collections import deque
from typing import Dict, List, Set

SUBSCRIPT_MAP = str.maketrans("₀₁₂₃₄₅₆₇₈₉", "0123456789")


def logical_index(label: str) -> int:
    """Return integer index of a logical state label like ``ψ₅``."""
    digits = label.replace("ψ", "").translate(SUBSCRIPT_MAP)
    try:
        return int(digits)
    except ValueError:
        return 0


def load_nodes(path: str) -> List[str]:
    """Load logical state list from ``path`` or return []."""
    if not os.path.exists(path):
        return []
    with open(path) as fh:
        data = json.load(fh)
    data.sort(key=lambda d: logical_index(d.get("logical_state", "ψ0")))
    return [item["logical_state"] for item in data]


def load_edges(path: str) -> List[tuple[str, str]]:
    """Load coupled edges from ``path``."""
    if not os.path.exists(path):
        return []
    with open(path) as fh:
        data = json.load(fh)
    data.sort(
        key=lambda d: (
            logical_index(d.get("q1", "ψ0")),
            logical_index(d.get("q2", "ψ0")),
        )
    )
    return [(d["q1"], d["q2"]) for d in data if d.get("coupled", False)]


def build_adj(nodes: List[str], edges: List[tuple[str, str]]) -> Dict[str, Set[str]]:
    """Build adjacency list from nodes and undirected edges."""
    adj: Dict[str, Set[str]] = {n: set() for n in nodes}
    for u, v in edges:
        if u in adj and v in adj:
            adj[u].add(v)
            adj[v].add(u)
    return adj


def bfs_paths(adj: Dict[str, Set[str]], start: str) -> Dict[str, List[str]]:
    """Return shortest paths from ``start`` to all reachable nodes."""
    queue = deque([start])
    prev: Dict[str, str | None] = {start: None}
    while queue:
        u = queue.popleft()
        for v in adj[u]:
            if v not in prev:
                prev[v] = u
                queue.append(v)
    paths: Dict[str, List[str]] = {}
    for node in adj:
        if node == start:
            paths[node] = [start]
        elif node in prev:
            path = [node]
            while path[-1] != start:
                parent = prev[path[-1]]
                if parent is None:
                    break
                path.append(parent)
            paths[node] = list(reversed(path))
    return paths


def main() -> None:
    map_path = "result/logic_physical_map.json"
    edge_path = "result/coupling_candidates.json"
    out_path = "result/path_matrix.json"

    nodes = load_nodes(map_path)
    edges = load_edges(edge_path)
    adj = build_adj(nodes, edges)

    matrix: Dict[str, Dict[str, List[str]]] = {}
    for start in nodes:
        paths = bfs_paths(adj, start)
        # order destinations by logical index
        ordered = {dst: paths[dst] for dst in sorted(paths, key=logical_index)}
        matrix[start] = ordered

    with open(out_path, "w") as fh:
        json.dump(matrix, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    print(f"Wrote all-pairs paths to {out_path}")


if __name__ == "__main__":
    main()
