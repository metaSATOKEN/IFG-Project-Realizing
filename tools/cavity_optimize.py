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
Q_expr = (sigma * R_sym * L_sym) / (t_sym * fc * relative_eps)
V_expr = sp.pi * R_sym**2 * L_sym
J_expr = -alpha * sp.log(Q_expr) + beta * V_expr

# Analytical derivatives
J_dR = sp.diff(J_expr, R_sym)
J_dL = sp.diff(J_expr, L_sym)

# Lambdify for numerical evaluation
func_J = sp.lambdify((R_sym, L_sym, t_sym), J_expr, "numpy")
func_dJdR = sp.lambdify((R_sym, L_sym, t_sym), J_dR, "numpy")
func_dJdL = sp.lambdify((R_sym, L_sym, t_sym), J_dL, "numpy")


def objective(params: np.ndarray) -> float:
    R, L, t = params
    return float(func_J(R, L, t))


def gradient(params: np.ndarray) -> np.ndarray:
    R, L, t = params
    gR = func_dJdR(R, L, t)
    gL = func_dJdL(R, L, t)
    # Derivative w.r.t t is simple from J_expr
    gT = float(sp.diff(J_expr, t_sym).subs({R_sym: R, L_sym: L, t_sym: t}))
    return np.array([gR, gL, gT], dtype=float)


if __name__ == "__main__":
    x0 = np.array([0.02, 0.04, 0.001])
    res = minimize(objective, x0, jac=gradient, method="BFGS")
    R_opt, L_opt, t_opt = res.x
    print("Optimal R (m):", R_opt)
    print("Optimal L (m):", L_opt)
    print("Optimal t (m):", t_opt)
    print("Minimum J:", res.fun)
