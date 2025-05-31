"""Generate theoretical noise spectrum with optional extra term."""

from __future__ import annotations

import json
import numpy as np
from pathlib import Path


def noise_theory(w: np.ndarray, A: float, B: float, C: float = 0.0) -> np.ndarray:
    return A / np.maximum(w, 1e-12) + B + C / np.maximum(w, 1e-12) ** 2


def main(out_json: str, A: float = 1e-12, B: float = 1e-18, C: float = 0.0) -> None:
    w = np.logspace(3, 9, 500)
    psd = noise_theory(w, A, B, C)
    data = {
        "frequency_Hz": w.tolist(),
        "psd": psd.tolist(),
        "params": {"A": A, "B": B, "C": C},
    }
    Path(out_json).parent.mkdir(parents=True, exist_ok=True)
    with open(out_json, "w") as fh:
        json.dump(data, fh, indent=2)


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser(description="Generate theoretical noise spectrum")
    p.add_argument("output", help="output JSON path")
    p.add_argument("--A", type=float, default=1e-12, help="1/f coefficient")
    p.add_argument("--B", type=float, default=1e-18, help="white noise level")
    p.add_argument("--C", type=float, default=0.0, help="additional coefficient")
    args = p.parse_args()
    main(args.output, args.A, args.B, args.C)
