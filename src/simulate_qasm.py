#!/usr/bin/env python3
"""Simple OPENQASM 2.0 execution tracer for SWAP and CX gates."""
from __future__ import annotations

import os
import re
from typing import List, Tuple


QASM_PATH = "result/iirb_swap_resolved.qasm"


def parse_qasm(path: str) -> List[Tuple[str, int, int]]:
    """Return list of (gate, i, j) operations from ``path``."""
    ops: List[Tuple[str, int, int]] = []
    if not os.path.exists(path):
        return ops
    pattern = re.compile(r"^(SWAP|CX)\s+q\[(\d+)\],\s*q\[(\d+)\];")
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("//"):
                continue
            m = pattern.match(line)
            if m:
                gate, a, b = m.groups()
                ops.append((gate, int(a), int(b)))
    return ops


def format_state(state: List[int]) -> str:
    """Return bitstring representation of ``state``."""
    return "|" + "".join(str(bit) for bit in state) + "⟩"


def main() -> None:
    ops = parse_qasm(QASM_PATH)
    qubits = [0] * 16
    step = 0
    print(f"Step {step}: INIT q[0..15] = {format_state(qubits)}")
    for gate, i, j in ops:
        step += 1
        if gate == "SWAP":
            qubits[i], qubits[j] = qubits[j], qubits[i]
        elif gate == "CX":
            if qubits[i] == 1:
                qubits[j] ^= 1
        print(f"Step {step}: {gate} q[{i}], q[{j}]")
        print("  → " + ", ".join(f"q[{idx}]={val}" for idx, val in enumerate(qubits)))
    print(
        "Final state: " + ", ".join(f"q[{idx}]={val}" for idx, val in enumerate(qubits))
    )


if __name__ == "__main__":
    main()
