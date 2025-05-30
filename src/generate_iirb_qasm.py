#!/usr/bin/env python3
"""Generate IIRB-style QASM from coupling information.

The script reads ``result/coupling_candidates.json`` and
``result/qubit_state_map.txt``.  For every pair with ``coupled: true`` it
emits a ``CX`` instruction between the associated physical qubit indices.
The output is written to ``result/iirb_generated.qasm``.
"""

from __future__ import annotations

import argparse
import json
from typing import Dict, List, Optional

SUBSCRIPT_MAP = str.maketrans("₀₁₂₃₄₅₆₇₈₉", "0123456789")


def parse_state_map(path: str) -> Dict[str, int]:
    """Return mapping from logical state label to physical qubit index."""
    mapping: Dict[str, int] = {}
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if not line or ':' not in line or '→' not in line:
                continue
            qname, rest = line.split(':', 1)
            phys_idx = int("".join(ch for ch in qname if ch.isdigit()))
            _, state = rest.split('→', 1)
            state = state.strip()
            mapping[state] = phys_idx
    return mapping


def load_candidates(path: str) -> List[Dict[str, object]]:
    with open(path) as fh:
        data = json.load(fh)
    data.sort(
        key=lambda d: (
            logical_index(d.get("q1", "ψ0")),
            logical_index(d.get("q2", "ψ0")),
        )
    )
    return data


def logical_index(label: str) -> int:
    digits = label.replace("ψ", "").translate(SUBSCRIPT_MAP)
    try:
        return int(digits)
    except ValueError:
        return 0


def generate_qasm(
    couplings: List[Dict[str, object]],
    mapping: Dict[str, int],
    filter_state: Optional[str],
) -> List[str]:
    lines: List[str] = ["OPENQASM 2.0;", "include \"qelib1.inc\";", "qreg q[16];", ""]
    for item in couplings:
        if not item.get("coupled", False):
            continue
        q1 = item["q1"]
        q2 = item["q2"]
        if filter_state and filter_state not in (q1, q2):
            continue
        idx1 = mapping.get(q1)
        idx2 = mapping.get(q2)
        if idx1 is None or idx2 is None:
            continue
        lines.append(f"// {q1} \u2194 {q2}")
        lines.append(f"CX q[{idx1}], q[{idx2}];")
    lines.append("")
    return lines


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate QASM from coupling graph")
    p.add_argument("--candidates", default="result/coupling_candidates.json", help="coupling JSON file")
    p.add_argument("--state-map", default="result/qubit_state_map.txt", help="qubit state map file")
    p.add_argument("-o", "--output", default="result/iirb_generated.qasm", help="output QASM file")
    p.add_argument("--filter", dest="filter_state", help="only emit gates involving given state")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    mapping = parse_state_map(args.state_map)
    couplings = load_candidates(args.candidates)
    qasm_lines = generate_qasm(couplings, mapping, args.filter_state)
    with open(args.output, "w") as fh:
        fh.write("\n".join(qasm_lines))
    print(f"QASM written to {args.output}")


if __name__ == "__main__":
    main()
