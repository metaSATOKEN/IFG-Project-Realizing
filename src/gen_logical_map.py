#!/usr/bin/env python3
"""Generate logical-to-physical qubit mapping JSON.

The script reads ``result/qubit_state_map.txt`` lines of the form
``Q7: (3.0, 1.0) → ψ₅`` and creates ``result/logic_physical_map.json``.
Entries are sorted by logical state index (ψ₀–ψ₁₅).
"""

from __future__ import annotations

import json
from typing import List, Dict


SUBSCRIPT_MAP = str.maketrans("₀₁₂₃₄₅₆₇₈₉", "0123456789")


def logical_index(label: str) -> int:
    """Return integer index of a logical state label like ``ψ₁₁``."""
    digits = label.replace("ψ", "").translate(SUBSCRIPT_MAP)
    try:
        return int(digits)
    except ValueError:
        return 0


def parse_state_map(path: str) -> List[Dict[str, object]]:
    """Parse mapping file and return list of mapping dicts."""
    items: List[Dict[str, object]] = []
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if not line or ':' not in line or '→' not in line:
                continue
            name_part, rest = line.split(':', 1)
            qubit_id = name_part.strip()
            coord_part, state_part = rest.split('→', 1)
            state = state_part.strip()
            coord_str = coord_part.strip()
            if coord_str.startswith('(') and coord_str.endswith(')'):
                coord_str = coord_str[1:-1]
            x_str, y_str = [v.strip() for v in coord_str.split(',', 1)]
            x = float(x_str)
            y = float(y_str)
            items.append({
                "logical_state": state,
                "qubit_id": qubit_id,
                "x": x,
                "y": y,
            })
    items.sort(key=lambda d: logical_index(d["logical_state"]))
    return items


def write_json(data: List[Dict[str, object]], path: str) -> None:
    with open(path, "w") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


def main() -> None:
    src_path = "result/qubit_state_map.txt"
    dst_path = "result/logic_physical_map.json"
    mapping = parse_state_map(src_path)
    write_json(mapping, dst_path)
    print(f"Logical map written to {dst_path}")


if __name__ == "__main__":
    main()
