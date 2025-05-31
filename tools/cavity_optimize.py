"""
Script Name: cavity_optimize.py
Purpose: Optimize μ-cavity Q and mode volume at target frequency
Dependencies: numpy, scipy, sympy
Usage:
    python tools/cavity_optimize.py

Outputs:
    - 最適パラメータ
    - 目的関数評価値
    - （必要に応じて）プロット or ファイル出力

Author: Codex（MetaShirou prompt経由）
"""

import argparse
import os
from pprint import pprint

import numpy as np
from scipy.optimize import minimize
import sympy as sp

# Constants
mu0 = 4 * np.pi * 1e-7
c = 299792458
sigma = 5.8e7  # Conductivity of copper [S/m]
relative_eps = 1.0  # vacuum
fc = 7.05e9  # target resonance frequency [Hz]
alpha = 1.0
beta = 1e-6

# Symbolic expressions
R_sym, L_sym, t_sym = sp.symbols("R L t", positive=True)
# NOTE: 本モデルは Q ∝ σRL / (t f_c ε_r) の簡易近似式であり、
# 実際の TM010 モードでは Rs = √(ωμ0/(2σ)) や形状因子 F_geom などの要素が加わります。
# 正式モデルは後続PRにて置き換える予定。


def Q_model(R, L, t):
    """Simplified cavity Q model."""
    return (sigma * R * L) / (t * fc * relative_eps)


Q_expr = Q_model(R_sym, L_sym, t_sym)
V_expr = sp.pi * R_sym**2 * L_sym
J_expr = -alpha * sp.log(Q_expr) + beta * V_expr

# Analytical derivatives
J_dR = sp.diff(J_expr, R_sym)
J_dL = sp.diff(J_expr, L_sym)

# Lambdify for numerical evaluation
func_J = sp.lambdify((R_sym, L_sym, t_sym), J_expr, "numpy")
func_dJdR = sp.lambdify((R_sym, L_sym, t_sym), J_dR, "numpy")
func_dJdL = sp.lambdify((R_sym, L_sym, t_sym), J_dL, "numpy")
J_dt = sp.diff(J_expr, t_sym)
func_dJdt = sp.lambdify((R_sym, L_sym, t_sym), J_dt, "numpy")


def objective(params: np.ndarray) -> float:
    R, L, t = params
    return float(func_J(R, L, t))


def gradient(params: np.ndarray) -> np.ndarray:
    R, L, t = params
    gR = func_dJdR(R, L, t)
    gL = func_dJdL(R, L, t)
    gT = func_dJdt(R, L, t)
    return np.array([gR, gL, gT], dtype=float)


def save_plot(R_vals: np.ndarray, J_vals: np.ndarray, path: str = "docs/plot/cavity_J_vs_R.png") -> None:
    """Save J versus R plot."""
    try:
        import matplotlib.pyplot as plt
        os.makedirs(os.path.dirname(path), exist_ok=True)

        plt.figure()
        plt.plot(R_vals, J_vals, marker="o")
        plt.xlabel("R (m)")
        plt.ylabel("J")
        plt.tight_layout()
        plt.savefig(path)
    except Exception as exc:
        print("Plot save failed:", exc)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Optimize cavity dimensions")
    parser.add_argument("--init_R", type=float, default=0.02)
    parser.add_argument("--init_L", type=float, default=0.04)
    parser.add_argument("--init_t", type=float, default=0.001)
    parser.add_argument("--min_R", type=float, default=0.005)
    parser.add_argument("--max_R", type=float, default=0.05)
    parser.add_argument("--min_L", type=float, default=0.01)
    parser.add_argument("--max_L", type=float, default=0.1)
    parser.add_argument("--min_t", type=float, default=0.0005)
    parser.add_argument("--max_t", type=float, default=0.005)
    parser.add_argument("--verbose", action="store_true", help="Show full result")
    args = parser.parse_args()

    x0 = np.array([args.init_R, args.init_L, args.init_t])
    bounds = [
        (args.min_R, args.max_R),
        (args.min_L, args.max_L),
        (args.min_t, args.max_t),
    ]

    res = minimize(objective, x0, jac=gradient, bounds=bounds, method="L-BFGS-B")
    R_opt, L_opt, t_opt = res.x
    print("Optimal R (m):", R_opt)
    print("Optimal L (m):", L_opt)
    print("Optimal t (m):", t_opt)
    print("Minimum J:", res.fun)
    print("Converged:", res.success)
    print("Message:", res.message)
    if args.verbose:
        pprint(vars(res))

    # R_vals = np.linspace(args.min_R, args.max_R, 50)
    # J_vals = [objective([r, L_opt, t_opt]) for r in R_vals]
    # save_plot(R_vals, np.array(J_vals))
    # ※ 後から人手でプロット生成したい場合は、上記3行のコメントを外して実行してください
