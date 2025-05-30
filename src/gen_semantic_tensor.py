#!/usr/bin/env python3
"""Generate semantic tensor (16x16) from weighted coupling map."""
from __future__ import annotations

import csv
import json
import os
from typing import Dict, List

SUBSCRIPT_MAP = str.maketrans("₀₁₂₃₄₅₆₇₈₉", "0123456789")


def logical_index(label: str) -> int:
    digits = label.replace("ψ", "").translate(SUBSCRIPT_MAP)
    try:
        return int(digits)
    except ValueError:
        return 0


def load_states(path: str) -> List[str]:
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    data.sort(key=lambda d: logical_index(d.get("logical_state", "ψ0")))
    return [d["logical_state"] for d in data]


def load_edges(path: str) -> List[Dict[str, object]]:
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    return data


def build_tensor(states: List[str], edges: List[Dict[str, object]]) -> List[List[float]]:
    n = len(states)
    idx = {s: i for i, s in enumerate(states)}
    tensor = [[0.0 for _ in range(n)] for _ in range(n)]
    for e in edges:
        i = idx.get(e["q1"])
        j = idx.get(e["q2"])
        if i is None or j is None:
            continue
        w = float(e.get("semantic_weight", 0))
        tensor[i][j] = w
        tensor[j][i] = w
    return tensor


def save_csv(matrix: List[List[float]], path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerows(matrix)


def save_json(matrix: List[List[float]], path: str) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(matrix, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


def main() -> None:
    map_path = "result/logic_physical_map.json"
    edge_path = "result/semantic_coupling_map.json"
    csv_path = "result/semantic_tensor.csv"
    json_path = "result/semantic_tensor.json"

    states = load_states(map_path)
    edges = load_edges(edge_path)
    tensor = build_tensor(states, edges)
    save_csv(tensor, csv_path)
    save_json(tensor, json_path)
    print(f"Wrote {csv_path} and {json_path}")


if __name__ == "__main__":
    main()
