#!/usr/bin/env python3
"""Simulate radiative heat load between cryostat shields.

CLI Usage:
    python sim_cooling_heatload.py [--config CONFIG.json] [--out-json PATH] [--plot-path PATH]
"""
import json
import os
from typing import List, Iterable, Optional, Tuple

import numpy as np
import matplotlib.pyplot as plt

SIGMA = 5.670374419e-8  # Stefan-Boltzmann constant


class Layer:
    def __init__(self, area: float, emissivity: float, thot: float, tcold: float):
        self.area = area
        self.epsilon = emissivity
        self.thot = thot
        self.tcold = tcold

    def heatload(self) -> float:
        return self.epsilon * SIGMA * self.area * (self.thot ** 4 - self.tcold ** 4)


def simulate(layers: Iterable[Layer]) -> np.ndarray:
    return np.array([lay.heatload() for lay in layers])


def save_plot(values: List[float], labels: List[str], path: str) -> None:
    make_dir(os.path.dirname(path))
    plt.figure()
    plt.bar(range(len(values)), values, tick_label=labels)
    plt.xlabel("Layer")
    plt.ylabel("Heatload [W]")
    plt.title("Radiative Heatload")
    plt.tight_layout()
    plt.savefig(path)
    plt.close()


def make_dir(path: str) -> None:
    dirpath = os.path.normpath(path)
    if dirpath and dirpath != ".":
        os.makedirs(dirpath, exist_ok=True)


def load_config(path: str) -> Tuple[List[Layer], List[str]]:
    with open(path, "r") as fh:
        items = json.load(fh)
    layers = [
        Layer(
            area=item["area"],
            emissivity=item["emissivity"],
            thot=item["thot"],
            tcold=item["tcold"],
        )
        for item in items
    ]
    labels = [item.get("label", f"{item['thot']}→{item['tcold']}K") for item in items]
    return layers, labels


def main(
    config_path: str,
    out_json: str,
    plot_path: Optional[str] = None,
    verbose: bool = False,
) -> None:
    layers, labels = load_config(config_path)
    loads = simulate(layers)
    if verbose:
        for i, load in enumerate(loads):
            print(f"Layer {i} heatload: {load:.3f} W")
        print("Total heat load:", float(np.sum(loads)))
    make_dir(os.path.dirname(out_json))
    if plot_path:
        save_plot(loads.tolist(), labels, plot_path)
    with open(out_json, "w") as fh:
        json.dump({"layers": loads.tolist(), "total": float(np.sum(loads))}, fh, indent=2)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Simulate radiative heat load")
    parser.add_argument("--config", default="result/heatload_layers.json", help="JSON layer configuration")
    parser.add_argument("--out-json", default="result/heatload.json", help="Output JSON path")
    parser.add_argument("--plot-path", help="Path to save bar plot")
    parser.add_argument("--verbose", action="store_true", help="Print layer heat loads")
    args = parser.parse_args()
    make_dir(os.path.dirname(args.out_json))
    main(args.config, args.out_json, args.plot_path, args.verbose)
