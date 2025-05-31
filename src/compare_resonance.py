"""Compare experimental resonance data with Lorentzian theory curve."""

from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

from src.extract_quantum_metrics import load_csv, lorentzian


def main(csv_path: str, metrics_json: str, out_path: str = "docs/plot/fig7_1.png") -> None:
    freqs, amps = load_csv(csv_path)
    with open(metrics_json, "r") as fh:
        metrics = json.load(fh)
    fc = float(metrics.get("fc_GHz", freqs[np.argmin(amps)]))
    ql = float(metrics.get("Q_loaded", 1e4))
    depth = max(amps) - min(amps)
    base = max(amps)
    f_sweep = np.linspace(min(freqs), max(freqs), 400)
    theory = lorentzian(f_sweep, fc, ql, depth, base)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.figure()
    plt.plot(freqs, amps, "o", label="experiment")
    plt.plot(f_sweep, theory, label="theory")
    plt.xlabel("Frequency [GHz]")
    plt.ylabel("Amplitude (arb.)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser(description="Compare resonance spectrum")
    p.add_argument("csv", help="resonance_experiment.csv")
    p.add_argument("metrics", help="metrics.json from extraction")
    p.add_argument("--out", default="docs/plot/fig7_1.png", help="output image path")
    args = p.parse_args()
    main(args.csv, args.metrics, args.out)
