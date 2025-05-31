#!/usr/bin/env python3
"""Estimate T2 from dynamical decoupling sequence data."""
import csv
import json
from typing import Tuple

import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt


def load_csv(path: str) -> Tuple[np.ndarray, np.ndarray]:
    data = np.genfromtxt(path, delimiter=",", names=True)
    n = data[data.dtype.names[0]]
    signal = data[data.dtype.names[1]]
    return np.asarray(n), np.asarray(signal)


def decay_model(n: np.ndarray, gamma: float, amp: float) -> np.ndarray:
    return amp * np.exp(-gamma * n)


def fit_decay(n: np.ndarray, signal: np.ndarray) -> Tuple[float, float]:
    popt, _ = curve_fit(decay_model, n, signal, p0=[1e-9, signal[0]], maxfev=10000)
    return popt[0], popt[1]


def save_plot(n: np.ndarray, signal: np.ndarray, gamma: float, path: str) -> None:
    plt.figure()
    plt.plot(n, signal, "o", label="data")
    plt.plot(n, decay_model(n, gamma, signal[0]), label="fit")
    plt.xlabel("N")
    plt.ylabel("Coherence")
    plt.title("T2 extraction")
    plt.legend()
    plt.tight_layout()
    plt.savefig(path)
    plt.close()


def main(path: str, out_json: str) -> None:
    n, sig = load_csv(path)
    gamma, amp = fit_decay(n, sig)
    t2 = 1.0 / gamma if gamma != 0 else float("inf")
    result = {"Gamma_dec": gamma, "T2": t2}
    with open(out_json, "w") as fh:
        json.dump(result, fh, indent=2)


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: extract_t2_from_dd.py <input.csv> <output.json>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
