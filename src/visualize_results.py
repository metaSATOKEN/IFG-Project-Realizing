#!/usr/bin/env python3
"""Visualize analysis results from extract scripts."""

import matplotlib.pyplot as plt
plt.rcParams.update({"figure.dpi": 150, "font.size": 12})
import json
import os

import numpy as np


def compute_lorentz_curve(fc: float, ql: float, f: np.ndarray) -> np.ndarray:
    return 1 - 1 / (1 + 4 * ql ** 2 * ((f - fc) / fc) ** 2)


def make_dir(path: str) -> None:
    if not path:
        return
    os.makedirs(os.path.normpath(path), exist_ok=True)


def plot_resonance(metrics_json: str, out_dir: str) -> None:
    with open(metrics_json, "r") as fh:
        m = json.load(fh)
    if "fc_GHz" not in m or "Q_loaded" not in m:
        raise KeyError("Missing fc_GHz or Q_loaded in metrics JSON")
    fc = m["fc_GHz"]
    ql = m["Q_loaded"]
    f = np.linspace(fc * 0.95, fc * 1.05, 400)
    lor = compute_lorentz_curve(fc, ql, f)
    plt.figure()
    plt.plot(f, lor, label="Lorentzian")
    plt.xlabel("Frequency [GHz]")
    plt.ylabel("Coherence (arb.)")
    plt.title("Resonance Spectrum")
    plt.legend()
    make_dir(out_dir)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "fig6_1.png"))
    plt.close()


def plot_noise(noise_json: str, out_dir: str) -> None:
    with open(noise_json, "r") as fh:
        data = json.load(fh)
    if "noise_model" not in data:
        raise KeyError("noise_model missing in noise JSON")
    A = data["noise_model"]["A"]
    B = data["noise_model"]["B"]
    w = np.logspace(1, 6, 400)
    S = A / w + B
    plt.figure()
    plt.loglog(w, S)
    plt.xlabel("Frequency [Hz]")
    plt.ylabel("PSD [V²/Hz]")
    plt.title("Noise Spectrum")
    make_dir(out_dir)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "fig6_2.png"))
    plt.close()


def plot_t2(dd_json: str, out_dir: str) -> None:
    with open(dd_json, "r") as fh:
        data = json.load(fh)
    if "Gamma_dec" not in data:
        raise KeyError("Gamma_dec missing in DD JSON")
    gamma = data["Gamma_dec"]
    N = np.arange(0, 100, 1)
    coh = np.exp(-gamma * N)
    plt.figure()
    plt.plot(N, coh)
    plt.xlabel("N (DD pulses)")
    plt.ylabel("Coherence (arb.)")
    plt.title("T2 Decay")
    make_dir(out_dir)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "fig6_3.png"))
    plt.close()


def main(metrics_json: str, noise_json: str, dd_json: str, out_dir: str) -> None:
    make_dir(out_dir)
    plot_resonance(metrics_json, out_dir)
    plot_noise(noise_json, out_dir)
    plot_t2(dd_json, out_dir)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Plot analysis results")
    parser.add_argument("metrics", help="Metrics JSON from extract_quantum_metrics")
    parser.add_argument("noise", help="Noise model JSON")
    parser.add_argument("dd", help="DD T2 JSON")
    parser.add_argument("--out-dir", default="docs/plot", help="Directory to save figures")
    args = parser.parse_args()
    main(args.metrics, args.noise, args.dd, args.out_dir)
