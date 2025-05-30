#!/usr/bin/env python3
"""Infer pairwise coupling candidates from logical qubit positions."""

from __future__ import annotations

import json
import math
import os
from typing import List, Dict


SUBSCRIPT_MAP = str.maketrans("₀₁₂₃₄₅₆₇₈₉", "0123456789")


def logical_index(label: str) -> int:
    """Return integer index of a logical state label like ``ψ₅``."""
    digits = label.replace("ψ", "").translate(SUBSCRIPT_MAP)
    try:
        return int(digits)
    except ValueError:
        return 0


def load_mapping(path: str) -> List[Dict[str, object]]:
    """Load logical to physical mapping from ``path`` or return empty list."""
    if not os.path.exists(path):
        return []
    with open(path) as fh:
        data = json.load(fh)
        data.sort(key=lambda d: logical_index(d.get("logical_state", "ψ0")))
        return data


def distance(p1: Dict[str, object], p2: Dict[str, object]) -> float:
    dx = float(p1.get("x", 0.0)) - float(p2.get("x", 0.0))
    dy = float(p1.get("y", 0.0)) - float(p2.get("y", 0.0))
    return math.hypot(dx, dy)


def infer_couplings(nodes: List[Dict[str, object]], threshold: float) -> List[Dict[str, object]]:
    """Return list of coupling candidate dicts for all pairs."""
    results: List[Dict[str, object]] = []
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            n1 = nodes[i]
            n2 = nodes[j]
            dist = distance(n1, n2)
            results.append({
                "q1": n1["logical_state"],
                "q2": n2["logical_state"],
                "distance": round(dist, 3),
                "coupled": dist <= threshold,
            })
    results.sort(key=lambda d: (logical_index(d["q1"]), logical_index(d["q2"])))
    return results


def write_json(data: List[Dict[str, object]], path: str) -> None:
    with open(path, "w") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


def main() -> None:
    src = "result/logic_physical_map.json"
    dst = "result/coupling_candidates.json"
    mapping = load_mapping(src)
    candidates = infer_couplings(mapping, threshold=1.5)
    write_json(candidates, dst)
    print(f"Printed {len(candidates)} coupling pair(s) to {dst}")


if __name__ == "__main__":
    main()
