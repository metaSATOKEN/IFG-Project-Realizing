"""Plot DD experiment decay against theoretical prediction."""

from __future__ import annotations

import csv
import json
import os
import numpy as np
import matplotlib.pyplot as plt

from tools import dd_simulation


def load_dd_csv(path: str) -> tuple[np.ndarray, np.ndarray]:
    with open(path, "r", newline="") as fh:
        reader = csv.DictReader(fh)
        n_list = []
        coh = []
        for row in reader:
            if "N" in row and "coherence" in row:
                n_list.append(float(row["N"]))
                coh.append(float(row["coherence"]))
    return np.asarray(n_list), np.asarray(coh)


def theory_curve(N_vals: np.ndarray, gamma: float) -> np.ndarray:
    return np.exp(-gamma * N_vals)


def main(csv_path: str, t2_json: str, out_path: str = "docs/plot/fig7_3.png") -> None:
    N_exp, coh_exp = load_dd_csv(csv_path)
    with open(t2_json, "r") as fh:
        data = json.load(fh)
    gamma = float(data.get("Gamma_dec", 0.0))
    N_sweep = np.linspace(min(N_exp), max(N_exp), 200)
    coh_theory = theory_curve(N_sweep, gamma)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.figure()
    plt.plot(N_exp, coh_exp, "o", label="experiment")
    plt.plot(N_sweep, coh_theory, label="theory")
    plt.xlabel("N")
    plt.ylabel("Coherence")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser(description="Compare DD decay curve")
    p.add_argument("csv", help="dd_experiment.csv")
    p.add_argument("t2", help="t2.json")
    p.add_argument("--out", default="docs/plot/fig7_3.png", help="output image path")
    args = p.parse_args()
    main(args.csv, args.t2, args.out)
