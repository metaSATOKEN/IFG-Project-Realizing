#!/usr/bin/env python3
"""Generate W(t) according to a simple FST 2.0 model.

The model takes a 5-dimensional vector :math:`\vec{\phi}_{soul}` and
produces a waveform `W(t)` using a set of fixed frequencies.
A light-weight Lyapunov control keeps the vector norm stable while
"seed hardening" ensures deterministic behavior.

Usage:
    python fst2.py v1 v2 v3 v4 v5 [--t-final T] [--dt DT] [--seed S]
"""
from __future__ import annotations

import argparse
import csv
import math
import random
from typing import Iterable, List, Tuple

# fixed frequencies (Hz) for each component
F_K = [382, 315, 500, 50, 100]
# phase update coefficient
ALPHA = 0.10


def fst2(phi: Iterable[float], t_final: float = 1.0, dt: float = 0.001, seed: int = 42) -> Tuple[List[float], List[float]]:
    """Compute time points and W(t) using a minimal FST 2.0 routine."""
    rnd = random.Random(seed)
    phi_vec = [float(x) for x in phi]

    # normalize with Lyapunov-like feedback to keep ||phi||=1
    def normalize(vec: List[float]) -> List[float]:
        nrm = math.sqrt(sum(v * v for v in vec)) or 1.0
        return [v / nrm for v in vec]

    phi_vec = normalize(phi_vec)
    theta = [rnd.uniform(-math.pi, math.pi) for _ in phi_vec]

    ts: List[float] = []
    ws: List[float] = []
    t = 0.0
    while t < t_final:
        w_val = sum(p * math.sin(2 * math.pi * f * t + th) for p, f, th in zip(phi_vec, F_K, theta))
        ts.append(t)
        ws.append(w_val)

        # phase and vector updates
        theta = [th + ALPHA * math.sin(th) for th in theta]
        phi_vec = normalize(phi_vec)  # Lyapunov control
        t += dt

    return ts, ws


def main() -> None:
    parser = argparse.ArgumentParser(description="FST 2.0 waveform generator")
    parser.add_argument("phi", nargs=5, type=float, metavar="φ", help="5 values for φ_soul")
    parser.add_argument("--t-final", type=float, default=1.0, help="simulation length [s]")
    parser.add_argument("--dt", type=float, default=0.001, help="time step [s]")
    parser.add_argument("--seed", type=int, default=42, help="seed for reproducibility")
    parser.add_argument("-o", "--out", default="result/fst2_wave.csv", help="output CSV path")
    args = parser.parse_args()

    ts, ws = fst2(args.phi, args.t_final, args.dt, args.seed)
    out_path = args.out
    try:
        with open(out_path, "w", newline="") as fh:
            writer = csv.writer(fh)
            writer.writerow(["t", "W"])
            for t, w in zip(ts, ws):
                writer.writerow([f"{t:.6f}", f"{w:.6f}"])
        print(f"✅ Saved waveform to {out_path}")
    except Exception as exc:
        print(f"⚠️  Failed to write {out_path}: {exc}")


if __name__ == "__main__":
    main()
