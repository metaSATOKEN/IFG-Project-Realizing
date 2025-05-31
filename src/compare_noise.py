"""Compare measured noise fit with theoretical noise spectrum."""

from __future__ import annotations

import json
import os
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent))

import numpy as np
import matplotlib.pyplot as plt

from simulate_noise_spectrum import noise_theory


def main(measured_json: str, theory_json: str, out_path: str = "docs/plot/fig7_2.png") -> None:
    with open(measured_json, "r") as fh:
        meas = json.load(fh)
    with open(theory_json, "r") as fh:
        theory = json.load(fh)

    A_m = meas.get("noise_model", {}).get("A", 0.0)
    B_m = meas.get("noise_model", {}).get("B", 0.0)
    w = np.asarray(theory["frequency_Hz"], dtype=float)
    psd_theory = np.asarray(theory["psd"], dtype=float)
    psd_measured = noise_theory(w, A_m, B_m)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.figure()
    plt.loglog(w, psd_measured, label="measured")
    plt.loglog(w, psd_theory, label="theory")
    plt.xlabel("Frequency [Hz]")
    plt.ylabel("PSD [arb./Hz]")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser(description="Compare noise spectrum")
    p.add_argument("measured", help="noise_fit.json")
    p.add_argument("theory", help="theory_noise_fit.json")
    p.add_argument("--out", default="docs/plot/fig7_2.png", help="output image path")
    args = p.parse_args()
    main(args.measured, args.theory, args.out)
