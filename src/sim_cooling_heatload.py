#!/usr/bin/env python3
"""Simulate radiative heat load between cryostat shields."""
import json
import os
from typing import List

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


def simulate() -> List[float]:
    layers = [
        Layer(area=0.1, emissivity=0.05, thot=300, tcold=50),
        Layer(area=0.1, emissivity=0.05, thot=50, tcold=4),
        Layer(area=0.1, emissivity=0.05, thot=4, tcold=0.1),
    ]
    return [lay.heatload() for lay in layers]


def save_plot(values: List[float], path: str) -> None:
    make_dir(os.path.dirname(path))
    plt.figure()
    plt.bar(range(len(values)), values)
    plt.xlabel("Layer")
    plt.ylabel("Heatload [W]")
    plt.title("Radiative Heatload")
    plt.tight_layout()
    plt.savefig(path)
    plt.close()


def make_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def main() -> None:
    loads = simulate()
    total = float(np.sum(loads))
    print("Total heat load:", total)
    save_plot(loads, "docs/plot/fig6_4.png")
    with open("result/heatload.json", "w") as fh:
        json.dump({"layers": loads, "total": total}, fh, indent=2)


if __name__ == "__main__":
    main()
