#!/usr/bin/env python3
"""Generate semantic-weighted coupling map from physical proximity."""

import json
import math
from typing import List, Dict

INPUT_PATH = "result/coupling_candidates.json"
OUTPUT_PATH = "result/semantic_coupling_map.json"


def load_pairs(path: str) -> List[Dict]:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def apply_semantic_weights(data: List[Dict]) -> List[Dict]:
    updated = []
    for entry in data:
        d = entry.get("distance", 999)
        coupled = entry.get("coupled", False)
        weight = round(math.exp(-0.7 * d), 4) if coupled else 0.0
        entry["semantic_weight"] = weight
        updated.append(entry)
    return updated


def save_output(data: List[Dict], path: str) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


def main() -> None:
    pairs = load_pairs(INPUT_PATH)
    weighted = apply_semantic_weights(pairs)
    save_output(weighted, OUTPUT_PATH)
    print(f"Wrote semantic coupling map to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
