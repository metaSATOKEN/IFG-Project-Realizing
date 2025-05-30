#!/usr/bin/env python3
"""Auto-generate 2D placement for 16 Qubits.

This script computes a simple qubit layout for a superconducting chip. By
default a rectangular grid is used, but a hexagonal arrangement can be
selected with ``--hex``. The pitch between adjacent qubits can be specified
in millimeters.

The resulting coordinates are written as plain text to
``result/qubit_layout_map.txt``.
"""

from __future__ import annotations

import argparse
import math
from typing import Dict, Tuple


def generate_grid_layout(num: int, pitch: float) -> Dict[str, Tuple[float, float]]:
    """Return a grid layout for ``num`` qubits with given ``pitch``."""
    per_row = int(math.ceil(math.sqrt(num)))
    layout = {}
    for i in range(num):
        row = i // per_row
        col = i % per_row
        x = round(col * pitch, 1)
        y = round(row * pitch, 1)
        layout[f"Q{i}"] = (x, y)
    return layout


def generate_hex_layout(num: int, pitch: float) -> Dict[str, Tuple[float, float]]:
    """Return a hexagonal layout for ``num`` qubits with given ``pitch``."""
    per_row = int(math.ceil(math.sqrt(num)))
    row_spacing = pitch * math.sqrt(3) / 2
    layout = {}
    idx = 0
    for row in range(per_row):
        offset = 0.5 * pitch if row % 2 == 1 else 0.0
        for col in range(per_row):
            if idx >= num:
                break
            x = round(col * pitch + offset, 1)
            y = round(row * row_spacing, 1)
            layout[f"Q{idx}"] = (x, y)
            idx += 1
    return layout


def write_layout(layout: Dict[str, Tuple[float, float]], path: str) -> None:
    with open(path, "w") as fh:
        for q, (x, y) in layout.items():
            fh.write(f"{q}: ({x:.1f}, {y:.1f})\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a 16-qubit layout")
    parser.add_argument("--hex", action="store_true", help="use hexagonal arrangement")
    parser.add_argument("--pitch", type=float, default=1.0, help="qubit pitch in mm")
    parser.add_argument("-o", "--output", default="result/qubit_layout_map.txt", help="output file")
    args = parser.parse_args()

    num_qubits = 16
    if args.hex:
        layout = generate_hex_layout(num_qubits, args.pitch)
    else:
        layout = generate_grid_layout(num_qubits, args.pitch)

    write_layout(layout, args.output)
    print(f"Layout written to {args.output}")


if __name__ == "__main__":
    main()
