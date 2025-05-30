#!/usr/bin/env python3
"""Expand logical CX gates into nearest-neighbor operations using SWAPs.

This script reads ``result/path_matrix.json`` and a JSON list of logical
operations and outputs an OPENQASM file with SWAP-resolved gates.  Each
non-adjacent CX gate is decomposed along the shortest physical route.

Example usage::

    python src/resolve_swap_paths.py
"""
from __future__ import annotations

import json
from typing import Dict, List, Tuple

SUBSCRIPT_MAP = str.maketrans("₀₁₂₃₄₅₆₇₈₉", "0123456789")


def parse_state_map(path: str) -> Tuple[Dict[str, int], Dict[str, str], Dict[str, str]]:
    """Return node index map and bidirectional state/position mappings."""
    node_to_idx: Dict[str, int] = {}
    pos_to_state: Dict[str, str] = {}
    state_to_pos: Dict[str, str] = {}
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if not line or ':' not in line or '→' not in line:
                continue
            qname, rest = line.split(':', 1)
            idx = int("".join(ch for ch in qname if ch.isdigit()))
            _, state = rest.split('→', 1)
            state = state.strip()
            node_to_idx[state] = idx
            pos_to_state[state] = state
            state_to_pos[state] = state
    return node_to_idx, pos_to_state, state_to_pos


def load_path_matrix(path: str) -> Dict[str, Dict[str, List[str]]]:
    with open(path) as fh:
        return json.load(fh)


def load_gate_sequence(path: str) -> List[Dict[str, str]]:
    with open(path) as fh:
        return json.load(fh)


def emit_swap(
    u: str,
    v: str,
    node_to_idx: Dict[str, int],
    pos_to_state: Dict[str, str],
    state_to_pos: Dict[str, str],
) -> str:
    idx_u = node_to_idx[u]
    idx_v = node_to_idx[v]
    state_u = pos_to_state[u]
    state_v = pos_to_state[v]
    pos_to_state[u], pos_to_state[v] = state_v, state_u
    state_to_pos[state_u], state_to_pos[state_v] = v, u
    return f"SWAP q[{idx_u}], q[{idx_v}];"


def resolve_gates(gates: List[Dict[str, str]], path_matrix: Dict[str, Dict[str, List[str]]],
                  node_to_idx: Dict[str, int]) -> List[str]:
    node_to_idx = node_to_idx.copy()
    # initialize occupancy maps
    pos_to_state = {node: node for node in node_to_idx}
    state_to_pos = {node: node for node in node_to_idx}

    lines: List[str] = ["OPENQASM 2.0;", "include \"qelib1.inc\";", "qreg q[16];", ""]
    for gate in gates:
        gtype = gate.get("gate")
        if gtype != "CX":
            continue
        q1 = gate.get("q1")
        q2 = gate.get("q2")
        if q1 is None or q2 is None:
            continue
        start = state_to_pos.get(q1)
        end = state_to_pos.get(q2)
        if start is None or end is None:
            continue
        path = path_matrix[start][end]
        lines.append(f"// {q1} ↔ {q2} via {' → '.join(path)} (SWAPs: {max(len(path)-2, 0)})")
        # move q1 along path except final hop
        for i in range(len(path) - 2):
            lines.append(emit_swap(path[i], path[i + 1], node_to_idx, pos_to_state, state_to_pos))
        ctrl_idx = node_to_idx[path[-2]] if len(path) > 1 else node_to_idx[start]
        targ_idx = node_to_idx[path[-1]]
        lines.append(f"CX q[{ctrl_idx}], q[{targ_idx}];")
        # restore positions
        for i in reversed(range(len(path) - 2)):
            lines.append(emit_swap(path[i], path[i + 1], node_to_idx, pos_to_state, state_to_pos))
        lines.append("")
    return lines


def main() -> None:
    node_to_idx, pos_to_state, state_to_pos = parse_state_map("result/qubit_state_map.txt")
    path_matrix = load_path_matrix("result/path_matrix.json")
    gates = load_gate_sequence("result/sample_logical_gates.json")
    lines = resolve_gates(gates, path_matrix, node_to_idx)
    out_path = "result/iirb_swap_resolved.qasm"
    with open(out_path, "w") as fh:
        fh.write("\n".join(lines))
    print(f"Wrote QASM to {out_path}")


if __name__ == "__main__":
    main()
