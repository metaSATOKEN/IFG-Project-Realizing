#!/usr/bin/env python3
"""Compute noise spectrum and fit 1/f + white noise model.

Frequency unit: Hz, Power Spectral Density (PSD) unit: V^2/Hz.

CLI Usage:
    python compute_noise_spectrum.py INPUT.csv OUTPUT.json [--res-threshold R]
"""

import json
import warnings
from typing import Tuple

import numpy as np
from scipy.optimize import curve_fit

# acceptable ratio of fit residual to PSD variance
RESIDUAL_RATIO_THRESHOLD = 0.1


def load_csv(path: str) -> Tuple[np.ndarray, np.ndarray]:
    """Load CSV containing frequency and PSD columns."""
    data = np.genfromtxt(path, delimiter=",", names=True)
    if data.size == 0 or not data.dtype.names or len(data.dtype.names) < 2:
        raise ValueError("CSV must contain at least two columns")
    freq = np.asarray(data[data.dtype.names[0]])
    psd = np.asarray(data[data.dtype.names[1]])
    if freq.size == 0 or psd.size == 0:
        raise ValueError("CSV contains no valid data")
    return freq, psd


def noise_model(w: np.ndarray, A: float, B: float) -> np.ndarray:
    return A / np.maximum(w, 1e-12) + B


def fit_noise(freq: np.ndarray, psd: np.ndarray) -> Tuple[float, float, float]:
    """Fit noise model to data and return A, B, and mean squared residual."""
    popt, _ = curve_fit(
        noise_model,
        freq,
        psd,
        p0=[1e-12, 1e-12],
        bounds=([0, 0], [np.inf, np.inf]),
        maxfev=10000,
    )
    residual = np.mean((psd - noise_model(freq, *popt)) ** 2)
    return popt[0], popt[1], residual


def main(path: str, out_json: str, res_threshold: float = RESIDUAL_RATIO_THRESHOLD) -> None:
    freq, psd = load_csv(path)
    A, B, res = fit_noise(freq, psd)
    if res > np.var(psd) * res_threshold:
        warnings.warn("Poor fit quality detected")
    result = {"noise_model": {"A": A, "B": B}, "residual": res}
    with open(out_json, "w") as fh:
        json.dump(result, fh, indent=2)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Fit noise spectrum to 1/f + white noise model")
    parser.add_argument("input", help="CSV file with frequency [Hz] and PSD [V^2/Hz]")
    parser.add_argument("output", help="Output JSON path")
    parser.add_argument("--res-threshold", type=float, default=RESIDUAL_RATIO_THRESHOLD,
                        help="Warn if residual exceeds variance * threshold (default: %(default)s)")
    args = parser.parse_args()
    main(args.input, args.output, args.res_threshold)
