"""
Script Name: fluxpump_optimize.py
Purpose: Optimize flux pump control parameters
Dependencies: numpy, scipy, argparse (optionally matplotlib)
Usage:
    python tools/fluxpump_optimize.py [--freq_p GHz] [--eps val] [--bias val]

Outputs:
    - 最適パラメータ
    - 目的関数評価値
    - （必要に応じて）プロット or ファイル出力

Author: Codex（MetaShirou prompt経由）
"""

import argparse
import numpy as np
from scipy.optimize import minimize

kappa_ext = 1e6
omega_q = 2 * np.pi * 7e9
gamma = 1e6

g_target = 0.17
mu_penalty = 0.1


def chi(omega: float) -> complex:
    return 1.0 / (omega - omega_q + 1j * gamma)


def g_ls(omega_p: float, epsilon_p: float, i_bias: float) -> float:
    chi_val = chi(omega_p)
    alpha_p = epsilon_p * i_bias
    numerator = (kappa_ext / 2.0) * np.real(chi_val)
    denom = 1.0 + (abs(chi_val) ** 2) * (abs(alpha_p) ** 2)
    return numerator / denom


def bandwidth() -> float:
    return kappa_ext


def objective(x: np.ndarray) -> float:
    omega_p, epsilon_p, i_bias = x
    g_val = g_ls(omega_p, epsilon_p, i_bias)
    bw = bandwidth()
    return (g_target - g_val) ** 2 + mu_penalty * (1.0 / bw)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Optimize flux pump parameters")
    parser.add_argument("--freq_p", type=float, default=7.5, help="pump frequency in GHz")
    parser.add_argument("--eps", type=float, default=0.1, help="pump amplitude")
    parser.add_argument("--bias", type=float, default=0.9, help="bias current")
    parser.add_argument("--csv", type=str, default="", help="optional CSV output path")
    parser.add_argument("--plot", type=str, default="", help="optional plot output path")
    args = parser.parse_args()

    x0 = np.array([2 * np.pi * args.freq_p * 1e9, args.eps, args.bias])
    bounds = [
        (2 * np.pi * 6e9, 2 * np.pi * 9e9),
        (0.01, 1.0),
        (0.5, 1.2),
    ]

    res = minimize(objective, x0, bounds=bounds, method="L-BFGS-B")
    w_opt, ep_opt, ib_opt = res.x
    g_val = g_ls(w_opt, ep_opt, ib_opt)

    print(f"ω_p [GHz]: {w_opt / (2 * np.pi * 1e9):.6f}")
    print("ε_p:", ep_opt)
    print("I_bias:", ib_opt)
    print("g_LS:", g_val)
    print("Minimum J:", res.fun)

    if args.csv:
        import csv

        with open(args.csv, "w", newline="") as fh:
            writer = csv.writer(fh)
            writer.writerow(["omega_p_GHz", "epsilon_p", "i_bias", "g_LS", "J"])
            writer.writerow([w_opt / (2 * np.pi * 1e9), ep_opt, ib_opt, g_val, res.fun])

    if args.plot:
        try:
            import matplotlib.pyplot as plt

            plt.figure()
            plt.scatter(w_opt / (2 * np.pi * 1e9), g_val, color="red")
            plt.xlabel("ω_p [GHz]")
            plt.ylabel("g_LS")
            plt.title("Flux Pump Optimization Result")
            plt.grid(True)
            plt.tight_layout()
            plt.savefig(args.plot)
        except Exception as exc:
            print("Plot failed:", exc)
