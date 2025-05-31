"""
Script Name: fluxpump_optimize.py
Purpose: Optimize flux pump control parameters
Dependencies: numpy, scipy
Usage:
    python tools/fluxpump_optimize.py

Outputs:
    - 最適パラメータ
    - 目的関数評価値
    - （必要に応じて）プロット or ファイル出力

Author: Codex（MetaShirou prompt経由）
"""

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
    x0 = np.array([2 * np.pi * 7.5e9, 0.1, 0.9])
    res = minimize(objective, x0, method="BFGS")
    w_opt, ep_opt, ib_opt = res.x
    print("Optimal ω_p:", w_opt)
    print("Optimal ε_p:", ep_opt)
    print("Optimal I_bias:", ib_opt)
    print("g_LS:", g_ls(w_opt, ep_opt, ib_opt))
    print("BW:", bandwidth())
    print("Minimum J:", res.fun)
