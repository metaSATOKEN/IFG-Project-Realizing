"""
Script Name: dd_simulation.py
Purpose: Evaluate decoherence suppression of DD sequence
Dependencies: numpy, scipy
Usage:
    python tools/dd_simulation.py [-A val] [-B val] [-N num] [-T time]

Outputs:
    - 最適パラメータ
    - 目的関数評価値
    - （必要に応じて）プロット or ファイル出力

Author: Codex（MetaShirou prompt経由）
"""

import argparse
import numpy as np
from scipy.integrate import quad

A = 1e-12
B = 1e-6
N = 10
T = 1e-6


def sn(omega: float) -> float:
    return A / omega + B


def tau_k(k: int) -> float:
    return T * np.sin(np.pi * k / (2 * (N + 1))) ** 2


def f_udd(omega: float) -> float:
    phases = [(-1) ** k * np.exp(-1j * omega * tau_k(k)) for k in range(1, N + 1)]
    summ = np.sum(phases)
    return np.abs(summ) ** 2


def integrand(omega: float) -> float:
    return sn(omega) * f_udd(omega) / (omega**2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Evaluate decoherence suppression of UDD sequence"
    )
    parser.add_argument("-A", type=float, default=A, help="noise coefficient A")
    parser.add_argument("-B", type=float, default=B, help="noise coefficient B")
    parser.add_argument("-N", type=int, default=N, help="number of pulses")
    parser.add_argument("-T", type=float, default=T, help="total protocol time")
    args = parser.parse_args()

    A = args.A
    B = args.B
    N = args.N
    T = args.T

    omega_min = 2 * np.pi * 1e3
    omega_max = 2 * np.pi * 1e10
    gamma_dec, _ = quad(integrand, omega_min, omega_max, limit=500)
    inv_T2 = 1.0 / gamma_dec if gamma_dec != 0 else np.inf
    print("Γ_dec:", gamma_dec)
    print("1/T2:", inv_T2)
