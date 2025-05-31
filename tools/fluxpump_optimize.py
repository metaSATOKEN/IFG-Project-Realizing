"""Flux pump control parameter optimization."""

import argparse
import numpy as np
from scipy.optimize import minimize

OMEGA_Q = 2 * np.pi * 7e9  # rad/s


def chi(omega: float, omega_q: float, gamma: float) -> complex:
    """Return susceptibility χ(ω)."""
    return 1.0 / (omega - omega_q + 1j * gamma)


def g_ls(
    omega_p: float,
    epsilon_p: float,
    i_bias: float,
    kappa_ext: float,
    omega_q: float,
    gamma: float,
) -> float:
    """Return gain g_LS for given parameters."""
    chi_val = chi(omega_p, omega_q, gamma)
    alpha_p = epsilon_p * i_bias
    numerator = (kappa_ext / 2.0) * np.real(chi_val)
    denom = 1.0 + (abs(chi_val) ** 2) * (abs(alpha_p) ** 2)
    return numerator / denom


def bandwidth(kappa_ext: float) -> float:
    """Simplified bandwidth model."""
    return kappa_ext


def objective(
    x: np.ndarray,
    g_target: float,
    mu_penalty: float,
    kappa_ext: float,
    omega_q: float,
    gamma: float,
) -> float:
    """Objective function J for optimization."""
    omega_p, epsilon_p, i_bias = x
    g_val = g_ls(omega_p, epsilon_p, i_bias, kappa_ext, omega_q, gamma)
    bw = bandwidth(kappa_ext)
    return (g_target - g_val) ** 2 + mu_penalty * (1.0 / bw)


def save_plot(omega_p_GHz: float, g_val: float, g_target: float, path: str = "docs/plot/fluxpump_g_vs_freq.png") -> None:
    """Save gain versus frequency plot."""
    try:
        import matplotlib.pyplot as plt

        plt.figure()
        plt.axhline(g_target, color="gray", linestyle="--", label="g_target")
        plt.scatter([omega_p_GHz], [g_val], color="red", label="Optimal g_LS")
        plt.xlabel("ω_p [GHz]")
        plt.ylabel("g_LS")
        plt.legend()
        plt.tight_layout()
        plt.savefig(path)
    except Exception as exc:
        print("Plot failed:", exc)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Optimize flux pump parameters")
    parser.add_argument("--freq_p", type=float, default=7.5, help="pump frequency [GHz]")
    parser.add_argument("--eps", type=float, default=0.1, help="pump amplitude")
    parser.add_argument("--bias", type=float, default=0.9, help="bias current")
    parser.add_argument("--target", type=float, default=0.17, help="g_LS target")
    parser.add_argument("--mu", type=float, default=0.1, help="bandwidth penalty coefficient")
    parser.add_argument("--kappa", type=float, default=1e6, help="κ_ext value")
    parser.add_argument("--gamma", type=float, default=1e6, help="dissipation rate γ")
    parser.add_argument("--plot", type=str, default="", help="optional plot output path")
    args = parser.parse_args()

    x0 = np.array([2 * np.pi * args.freq_p * 1e9, args.eps, args.bias])
    bounds = [
        (2 * np.pi * 6e9, 2 * np.pi * 9e9),
        (0.01, 1.0),
        (0.5, 1.2),
    ]
    obj = lambda x: objective(x, args.target, args.mu, args.kappa, OMEGA_Q, args.gamma)
    res = minimize(obj, x0, bounds=bounds, method="L-BFGS-B")
    w_opt, ep_opt, ib_opt = res.x
    g_val = g_ls(w_opt, ep_opt, ib_opt, args.kappa, OMEGA_Q, args.gamma)
    w_opt_GHz = w_opt / (2 * np.pi * 1e9)
    J_val = res.fun

    print(f"ω_p [GHz]: {w_opt_GHz:.3f}")
    print("ε_p:", ep_opt)
    print("I_bias:", ib_opt)
    print("g_LS:", g_val)
    print("Minimum J:", J_val)

    if args.plot:
        save_plot(w_opt_GHz, g_val, args.target, args.plot)
