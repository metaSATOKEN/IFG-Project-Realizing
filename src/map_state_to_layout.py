#!/usr/bin/env python3
"""Map logical state labels to physical qubit coordinates.

The script reads ``result/qubit_layout_map.txt`` which contains lines of the
form ``Q0: (x, y)``.  It then associates each qubit with a state label and
writes the mapping to ``result/qubit_state_map.txt``.

State labels default to ``ψ₀``..``ψₙ`` and may be overridden via ``--states``.
The number of supplied labels must match the number of qubits.  Qubit entries
are sorted numerically so that ``Q2`` precedes ``Q10``.
"""

from __future__ import annotations

import argparse
from typing import List, Tuple


def read_layout(path: str) -> List[Tuple[str, str]]:
    """Return sorted list of ``(qubit name, coordinate)`` tuples."""

    def q_index(name: str) -> int:
        """Extract the integer portion of a qubit label like ``Q7``."""
        digits = "".join(ch for ch in name if ch.isdigit())
        return int(digits) if digits else 0

    layout: List[Tuple[str, str]] = []
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if not line or ":" not in line:
                continue
            name, coord = line.split(":", 1)
            layout.append((name.strip(), coord.strip()))

    layout.sort(key=lambda item: q_index(item[0]))
    return layout


def write_state_map(layout: List[Tuple[str, str]], states: List[str], path: str) -> None:
    if len(layout) != len(states):
        raise ValueError("Number of states does not match number of qubits")

    with open(path, "w") as fh:
        for (name, coord), state in zip(layout, states):
            fh.write(f"{name}: {coord} → {state}\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Map logical states to qubit layout")
    parser.add_argument(
        "--states",
        nargs="+",
        help="custom state labels (must match the number of qubits)",
    )
    parser.add_argument(
        "-i",
        "--input",
        default="result/qubit_layout_map.txt",
        help="input layout file",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="result/qubit_state_map.txt",
        help="output state map file",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    layout = read_layout(args.input)
    num = len(layout)
    if args.states:
        if len(args.states) != num:
            raise ValueError(
                f"Provided {len(args.states)} states for {num} qubits"
            )
        states = args.states
    else:
        sub = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
        states = [f"ψ{str(i).translate(sub)}" for i in range(num)]

    write_state_map(layout, states, args.output)
    print(f"State map written to {args.output}")


if __name__ == "__main__":
    main()
