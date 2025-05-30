"""Analyze logical coupling graph statistics and shortest paths."""

import json
from collections import defaultdict, deque
from typing import Dict, List, Set

SUBSCRIPT_MAP = str.maketrans("₀₁₂₃₄₅₆₇₈₉", "0123456789")


def logical_index(label: str) -> int:
    """Return integer index from a state label like ``ψ₅``."""
    digits = label.replace("ψ", "").translate(SUBSCRIPT_MAP)
    try:
        return int(digits)
    except ValueError:
        return 0


def load_nodes(path: str) -> List[str]:
    with open(path) as fh:
        data = json.load(fh)
    data.sort(key=lambda d: logical_index(d.get("logical_state", "ψ0")))
    return [d["logical_state"] for d in data]


def load_edges(path: str) -> List[tuple[str, str]]:
    with open(path) as fh:
        data = json.load(fh)
    data.sort(
        key=lambda d: (
            logical_index(d.get("q1", "ψ0")),
            logical_index(d.get("q2", "ψ0")),
        )
    )
    return [ (d["q1"], d["q2"]) for d in data if d.get("coupled", False) ]


def build_adj(nodes: List[str], edges: List[tuple[str, str]]) -> Dict[str, Set[str]]:
    adj: Dict[str, Set[str]] = {n: set() for n in nodes}
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    return adj


def bfs_paths(adj: Dict[str, Set[str]], start: str) -> Dict[str, List[str]]:
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
            p = [node]
            while p[-1] != start:
                parent = prev[p[-1]]
                if parent is None:
                    break
                p.append(parent)
            paths[node] = list(reversed(p))
    return paths


def all_pairs_shortest(adj: Dict[str, Set[str]], nodes: List[str]) -> Dict[tuple[str, str], int]:
    dists: Dict[tuple[str, str], int] = {}
    for i, src in enumerate(nodes):
        queue = deque([src])
        dist = {src: 0}
        while queue:
            u = queue.popleft()
            for v in adj[u]:
                if v not in dist:
                    dist[v] = dist[u] + 1
                    queue.append(v)
        for dest in nodes[i + 1 :]:
            if dest in dist:
                dists[(src, dest)] = dist[dest]
    return dists


def main() -> None:
    map_path = "result/logic_physical_map.json"
    edge_path = "result/coupling_candidates.json"
    stats_path = "result/coupling_graph_stats.txt"
    table_path = "result/path_table_from_ψ0.json"

    nodes = load_nodes(map_path)
    edges = load_edges(edge_path)
    adj = build_adj(nodes, edges)

    num_nodes = len(nodes)
    num_edges = len(edges)
    degrees = [len(adj[n]) for n in nodes]
    avg_deg = 2.0 * num_edges / num_nodes if num_nodes else 0.0
    max_deg = max(degrees) if degrees else 0

    paths_from_start = bfs_paths(adj, nodes[0])
    connected = len(paths_from_start) == num_nodes

    pair_dists = all_pairs_shortest(adj, nodes)
    if pair_dists:
        diameter = max(pair_dists.values())
        avg_sp = sum(pair_dists.values()) / len(pair_dists)
    else:
        diameter = 0
        avg_sp = 0.0

    with open(stats_path, "w") as fh:
        fh.write(f"Nodes: {num_nodes}\n")
        fh.write(f"Edges: {num_edges}\n")
        fh.write(f"Average Degree: {avg_deg:.2f}\n")
        fh.write(f"Max Degree: {max_deg}\n")
        fh.write(f"Connected: {connected}\n")
        fh.write(f"Diameter: {diameter}\n")
        fh.write(f"Average Shortest Path: {avg_sp:.2f}\n")

    with open(table_path, "w") as fh:
        json.dump(paths_from_start, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    print(f"Wrote {stats_path} and {table_path}")


if __name__ == "__main__":
    main()
