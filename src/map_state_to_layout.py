#!/usr/bin/env python3
"""Assign IIRB state labels to qubit layout positions.

This script reads ``result/qubit_layout_map.txt`` and writes
``result/qubit_state_map.txt``. Each line of the output maps a qubit
name and its coordinates to a logical state label. State labels can be
specified via ``--states``; otherwise ``ψ0``..``ψ15`` are used.
"""

from __future__ import annotations

import argparse
from typing import List, Tuple


def read_layout(path: str) -> List[Tuple[str, str]]:
    """Return list of (qubit name, coordinate string) tuples."""
    layout = []
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if not line or ":" not in line:
                continue
            name, coord = line.split(":", 1)
            layout.append((name.strip(), coord.strip()))
    return layout


def write_state_map(layout: List[Tuple[str, str]], states: List[str], path: str) -> None:
    with open(path, "w") as fh:
        for (name, coord), state in zip(layout, states):
            fh.write(f"{name}: {coord} → {state}\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Map logical states to qubit layout")
    parser.add_argument(
        "--states",
        nargs="+",
        help="custom state labels (will be replaced if insufficient)",
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
    if args.states and len(args.states) >= num:
        states = args.states
    else:
        sub = str.maketrans('0123456789', '₀₁₂₃₄₅₆₇₈₉')
        states = [f"ψ{str(i).translate(sub)}" for i in range(num)]
    write_state_map(layout, states, args.output)
    print(f"State map written to {args.output}")


if __name__ == "__main__":
    main()
