#!/usr/bin/env python3
"""Simulate semantic spread over 5 steps using the semantic tensor."""
from __future__ import annotations

import json
import os
from typing import List

import matplotlib.pyplot as plt

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


def load_tensor(path: str) -> List[List[float]]:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def normalize_rows(mat: List[List[float]]) -> List[List[float]]:
    norm = []
    for row in mat:
        s = sum(row)
        if s > 0:
            norm.append([v / s for v in row])
        else:
            norm.append(row[:])
    return norm


def multiply(mat: List[List[float]], vec: List[float]) -> List[float]:
    result = []
    for row in mat:
        result.append(sum(v * x for v, x in zip(row, vec)))
    return result


def simulate(states: List[str], mat: List[List[float]], steps: int = 5) -> List[dict]:
    norm = normalize_rows(mat)
    vec = [1.0 if i == 0 else 0.0 for i in range(len(states))]
    history = [{"step": 0, "vector": vec}]
    for n in range(1, steps + 1):
        vec = multiply(norm, vec)
        history.append({"step": n, "vector": vec})
    return history


def save_history(history: List[dict], path: str) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(history, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


def plot_final(states: List[str], vec: List[float], path: str) -> None:
    plt.figure(figsize=(8, 4))
    plt.bar(range(len(states)), vec, tick_label=states)
    plt.xlabel("State")
    plt.ylabel("Weight")
    plt.tight_layout()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    plt.savefig(path)
    plt.close()


def main() -> None:
    state_path = "result/logic_physical_map.json"
    tensor_path = "result/semantic_tensor.json"
    hist_path = "result/semantic_spread_steps.json"
    png_path = "docs/plot/semantic_spread_step5.png"

    states = load_states(state_path)
    tensor = load_tensor(tensor_path)
    history = simulate(states, tensor, steps=5)
    save_history(history, hist_path)
    plot_final(states, history[-1]["vector"], png_path)
    print(f"Wrote {hist_path} and {png_path}")


if __name__ == "__main__":
    main()
