#!/usr/bin/env python3
"""Visualize analysis results from extract scripts."""
import json
import os

import numpy as np
import matplotlib.pyplot as plt


def make_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def plot_resonance(metrics_json: str, out_dir: str) -> None:
    with open(metrics_json, "r") as fh:
        m = json.load(fh)
    fc = m["fc_GHz"]
    ql = m["Q_loaded"]
    f = np.linspace(fc * 0.95, fc * 1.05, 400)
    lor = 1 - 1 / (1 + 4 * ql ** 2 * ((f - fc) / fc) ** 2)
    plt.figure()
    plt.plot(f, lor, label="Lorentzian")
    plt.xlabel("Frequency [GHz]")
    plt.ylabel("Amplitude (arb.)")
    plt.title("Resonance Spectrum")
    plt.legend()
    make_dir(out_dir)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "fig6_1.png"))
    plt.close()


def plot_noise(noise_json: str, out_dir: str) -> None:
    with open(noise_json, "r") as fh:
        data = json.load(fh)
    A = data["noise_model"]["A"]
    B = data["noise_model"]["B"]
    w = np.logspace(1, 6, 400)
    S = A / w + B
    plt.figure()
    plt.loglog(w, S)
    plt.xlabel("Frequency [Hz]")
    plt.ylabel("PSD")
    plt.title("Noise Spectrum")
    make_dir(out_dir)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "fig6_2.png"))
    plt.close()


def plot_t2(dd_json: str, out_dir: str) -> None:
    with open(dd_json, "r") as fh:
        data = json.load(fh)
    gamma = data["Gamma_dec"]
    N = np.arange(0, 100, 1)
    coh = np.exp(-gamma * N)
    plt.figure()
    plt.plot(N, coh)
    plt.xlabel("N")
    plt.ylabel("Coherence")
    plt.title("T2 Decay")
    make_dir(out_dir)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "fig6_3.png"))
    plt.close()


def main(metrics_json: str, noise_json: str, dd_json: str) -> None:
    out_dir = "docs/plot"
    plot_resonance(metrics_json, out_dir)
    plot_noise(noise_json, out_dir)
    plot_t2(dd_json, out_dir)


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 4:
        print("Usage: visualize_results.py <metrics.json> <noise.json> <dd.json>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2], sys.argv[3])
