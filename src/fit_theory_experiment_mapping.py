"""Fit experimental data to theory parameters.

This script combines previously extracted experiment metrics and
initial theoretical parameters to produce updated model values.
It is intentionally lightweight and works with JSON/CSV files
produced in earlier chapters.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Dict, Any

import numpy as np


def load_json(path: str | Path) -> Dict[str, Any]:
    with open(path, "r") as fh:
        return json.load(fh)


def compute_temp_drift(path: str | Path) -> float:
    """Return temperature drift rate dT/dt from CSV."""
    data = np.genfromtxt(path, delimiter=",", names=True)
    if data.size == 0 or len(data.dtype.names) < 2:
        return 0.0
    t = np.asarray(data[data.dtype.names[0]], dtype=float)
    temp = np.asarray(data[data.dtype.names[1]], dtype=float)
    if t.size < 2:
        return 0.0
    coeffs = np.polyfit(t, temp, 1)
    return float(coeffs[0])  # slope


def aggregate_heatload(path: str | Path) -> float:
    """Sum heatload values if available."""
    h = load_json(path)
    total = 0.0
    if isinstance(h, list):
        for layer in h:
            if isinstance(layer, dict):
                total += float(layer.get("heat", layer.get("load", 0.0)))
    elif isinstance(h, dict):
        if "layers" in h and isinstance(h["layers"], list):
            for layer in h["layers"]:
                if isinstance(layer, dict):
                    total += float(layer.get("heat", layer.get("load", 0.0)))
        total += float(h.get("total", 0.0))
    return total


def fit_params(
    theory_path: str | Path,
    metrics_path: str | Path,
    t2_path: str | Path,
    noise_path: str | Path,
    temp_csv: str | Path,
    heatload_path: str | Path,
    out_json: str | Path,
) -> Dict[str, Any]:
    theory = load_json(theory_path)
    metrics = load_json(metrics_path)
    t2_data = load_json(t2_path)
    noise = load_json(noise_path)
    drift = compute_temp_drift(temp_csv)
    heat_total = aggregate_heatload(heatload_path)

    fc_exp = float(metrics.get("fc_GHz", theory.get("fc_GHz", 0.0)))
    ql_exp = float(metrics.get("Q_loaded", theory.get("Q_loaded", 0.0)))
    A = float(noise.get("noise_model", {}).get("A", 0.0))
    B = float(noise.get("noise_model", {}).get("B", 0.0))
    if "Gamma_dec" in t2_data:
        gamma = float(t2_data["Gamma_dec"])
    elif "T2" in t2_data and t2_data["T2"] != 0:
        gamma = 1.0 / float(t2_data["T2"])
    else:
        gamma = 0.0

    # simple updates: incorporate temperature drift and heatload
    fc_corr = fc_exp * (1.0 - 1e-3 * drift)
    ql_corr = max(ql_exp - 0.1 * heat_total, 1.0)

    fitted = {
        "fc_GHz": fc_corr,
        "Q_loaded": ql_corr,
        "noise_A": A,
        "noise_B": B,
        "Gamma_dec": gamma,
        "temp_drift_rate": drift,
        "heatload_total": heat_total,
    }
    with open(out_json, "w") as fh:
        json.dump(fitted, fh, indent=2)
    return fitted


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser(description="Fit theory parameters to experiments")
    p.add_argument("theory", help="initial theory JSON")
    p.add_argument("metrics", help="metrics.json")
    p.add_argument("t2", help="t2.json")
    p.add_argument("noise", help="noise_fit.json")
    p.add_argument("temp", help="temperature_drift.csv")
    p.add_argument("heatload", help="heatload.json")
    p.add_argument("output", help="output JSON path")
    args = p.parse_args()
    fit_params(
        args.theory,
        args.metrics,
        args.t2,
        args.noise,
        args.temp,
        args.heatload,
        args.output,
    )
