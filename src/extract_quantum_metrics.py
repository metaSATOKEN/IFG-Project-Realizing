#!/usr/bin/env python3
"""Extract resonance parameters from filtered RF data."""
import csv
import json
import math
from typing import Tuple, List

import numpy as np
from scipy.optimize import curve_fit


def load_csv(path: str) -> Tuple[np.ndarray, np.ndarray]:
    with open(path, "r", newline="") as fh:
        reader = csv.DictReader(fh)
        freqs = []
        amps = []
        for row in reader:
            f = float(row.get("timestamp", row.get("freq", 0)))
            if "I" in row and "Q" in row:
                i = float(row["I"])
                q = float(row["Q"])
                amp = math.hypot(i, q)
            elif "abs" in row:
                amp = float(row["abs"])
            else:
                continue
            freqs.append(f)
            amps.append(amp)
    return np.array(freqs), np.array(amps)


def lorentzian(f: np.ndarray, fc: float, ql: float, depth: float, base: float) -> np.ndarray:
    return base - depth / (1.0 + 4.0 * ql ** 2 * ((f - fc) / fc) ** 2)


def fit_lorentzian(freqs: np.ndarray, amps: np.ndarray) -> Tuple[float, float, float, float]:
    fc_guess = freqs[np.argmin(amps)]
    q_guess = 1e4
    depth_guess = max(amps) - min(amps)
    base_guess = max(amps)
    popt, _ = curve_fit(lorentzian, freqs, amps, p0=[fc_guess, q_guess, depth_guess, base_guess])
    return tuple(popt)


def estimate_qi_qe(ql: float, amp_min: float, base: float) -> Tuple[float, float]:
    s_min = amp_min / base if base != 0 else 1.0
    qe = ql / max(1.0 - s_min, 1e-12)
    qi = 1.0 / max(1.0 / ql - 1.0 / qe, 1e-12)
    return qi, qe


def main(path: str, out_json: str) -> None:
    freqs, amps = load_csv(path)
    if len(freqs) == 0:
        raise RuntimeError("No data found in CSV")
    fc, ql, depth, base = fit_lorentzian(freqs, amps)
    amp_min = lorentzian(fc, fc, ql, depth, base)
    qi, qe = estimate_qi_qe(ql, amp_min, base)
    result = {
        "fc_GHz": fc,
        "Q_loaded": ql,
        "Q_internal": qi,
        "Q_external": qe,
    }
    with open(out_json, "w") as fh:
        json.dump(result, fh, indent=2)


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: extract_quantum_metrics.py <input.csv> <output.json>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
