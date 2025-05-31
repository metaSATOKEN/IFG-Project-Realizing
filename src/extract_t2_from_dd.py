#!/usr/bin/env python3
"""Estimate T2 from dynamical decoupling sequence data.

CLI Usage:
    python extract_t2_from_dd.py INPUT.csv OUTPUT.json [--plot-path PATH --save-plot]
"""

import json
from typing import Tuple, Optional

import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import warnings


def load_csv(path: str, allow_negative: bool = False) -> Tuple[np.ndarray, np.ndarray]:
    """Load DD data. Columns: N and coherence signal."""
    data = np.genfromtxt(path, delimiter=",", names=True)
    if data.size == 0 or not data.dtype.names or len(data.dtype.names) < 2:
        raise ValueError("CSV must contain at least two columns")
    n = np.asarray(data[data.dtype.names[0]])
    signal = np.asarray(data[data.dtype.names[1]])
    mask = ~np.isnan(signal)
    n = n[mask]
    signal = signal[mask]
    if np.any(signal < 0):
        if allow_negative:
            warnings.warn("Negative signal values encountered; keeping values")
        else:
            mask = signal >= 0
            n = n[mask]
            signal = signal[mask]
    return n, signal


def decay_model(n: np.ndarray, gamma: float, amp: float) -> np.ndarray:
    return amp * np.exp(-gamma * n)


def fit_decay(n: np.ndarray, signal: np.ndarray) -> Tuple[float, float]:
    popt, _ = curve_fit(
        decay_model,
        n,
        signal,
        p0=[0.01, max(signal)],
        bounds=([0, 0], [np.inf, np.inf]),
        maxfev=10000,
    )
    return popt[0], popt[1]


def save_plot(n: np.ndarray, signal: np.ndarray, gamma: float, path: str) -> None:
    plt.figure()
    plt.plot(n, signal, "o", label="data")
    plt.plot(n, decay_model(n, gamma, signal[0]), label="fit")
    plt.xlabel("N (DD pulses)")
    plt.ylabel("Coherence (arb.)")
    plt.title("T2 extraction")
    plt.legend()
    plt.tight_layout()
    plt.savefig(path)
    plt.close()


def main(path: str, out_json: str, plot_path: Optional[str] = None, save_plot_flag: bool = False, allow_negative: bool = False) -> None:
    n, sig = load_csv(path, allow_negative=allow_negative)
    gamma, amp = fit_decay(n, sig)
    t2 = 1.0 / gamma if gamma != 0 else float("inf")
    result = {"Gamma_dec": gamma, "T2": t2, "unit": "pulse"}
    with open(out_json, "w") as fh:
        json.dump(result, fh, indent=2)
    if save_plot_flag and plot_path:
        save_plot(n, sig, gamma, plot_path)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Estimate T2 from DD data")
    parser.add_argument("input", help="CSV with pulse count and coherence")
    parser.add_argument("output", help="Output JSON path")
    parser.add_argument("--plot-path", help="Destination for plot PNG")
    parser.add_argument("--save-plot", action="store_true", help="Generate decay plot")
    parser.add_argument("--allow-negative", action="store_true", help="Keep negative signal values")
    args = parser.parse_args()
    main(args.input, args.output, args.plot_path, args.save_plot, args.allow_negative)
