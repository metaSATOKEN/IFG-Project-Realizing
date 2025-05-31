#!/usr/bin/env python3
"""Compute noise spectrum and fit 1/f + white noise model."""
import csv
import json
import warnings
from typing import Tuple

import numpy as np
from scipy.optimize import curve_fit


def load_csv(path: str) -> Tuple[np.ndarray, np.ndarray]:
    data = np.genfromtxt(path, delimiter=",", names=True)
    freq = data[data.dtype.names[0]]
    psd = data[data.dtype.names[1]]
    return np.asarray(freq), np.asarray(psd)


def noise_model(w: np.ndarray, A: float, B: float) -> np.ndarray:
    return A / np.maximum(w, 1e-12) + B


def fit_noise(freq: np.ndarray, psd: np.ndarray) -> Tuple[float, float, float]:
    popt, _ = curve_fit(noise_model, freq, psd, p0=[1e-12, 1e-12], maxfev=10000)
    residual = np.mean((psd - noise_model(freq, *popt)) ** 2)
    return popt[0], popt[1], residual


def main(path: str, out_json: str) -> None:
    freq, psd = load_csv(path)
    A, B, res = fit_noise(freq, psd)
    if res > np.var(psd) * 0.1:
        warnings.warn("Poor fit quality detected")
    result = {"noise_model": {"A": A, "B": B}}
    with open(out_json, "w") as fh:
        json.dump(result, fh, indent=2)


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: compute_noise_spectrum.py <input.csv> <output.json>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
