"""
Script Name: squid_coupler.py
Purpose: SQUID mutual inductance geometry optimization
Dependencies: numpy, scipy
Usage:
    python tools/squid_coupler.py

Outputs:
    - 最適パラメータ
    - 目的関数評価値
    - （必要に応じて）プロット or ファイル出力

Author: Codex（MetaShirou prompt経由）
"""

import numpy as np
from scipy.optimize import minimize

mu0 = 4 * np.pi * 1e-7
sigma = 5.8e7

g_target = 10e6  # Hz
k_couple = 1e8
lambda_reg = 1e-3
frequency = 10e6


def mutual_inductance(R1: float, R2: float, d: float) -> float:
    return mu0 * R1 * R2 / (2 * (R1 + R2 + d))


def resistance_cond(R1: float, R2: float) -> float:
    skin_depth = np.sqrt(1 / (np.pi * mu0 * frequency * sigma))
    return (1 / (sigma * 2 * np.pi * R1 * skin_depth)) + (
        1 / (sigma * 2 * np.pi * R2 * skin_depth)
    )


def objective(x: np.ndarray) -> float:
    R1, R2, d = x
    M = mutual_inductance(R1, R2, d)
    R_cond = resistance_cond(R1, R2)
    J = (g_target - k_couple * M) ** 2 + lambda_reg * R_cond
    return J


if __name__ == "__main__":
    x0 = np.array([0.005, 0.005, 0.002])
    res = minimize(objective, x0, method="BFGS")
    R1_opt, R2_opt, d_opt = res.x
    print("Optimal R1 (m):", R1_opt)
    print("Optimal R2 (m):", R2_opt)
    print("Optimal d (m):", d_opt)
    print("Minimum J:", res.fun)
