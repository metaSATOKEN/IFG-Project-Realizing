#!/usr/bin/env python3
"""Flux-pump parametric amplification scan."""
import json
import numpy as np
import matplotlib.pyplot as plt


def g_ls_model(f_ghz, power, delta_mhz):
    """Synthetic model for interaction strength g_LS."""
    G0 = 0.25
    f0 = 5.5
    sigma_f = 0.6
    return G0 * np.exp(-((f_ghz - f0) ** 2) / sigma_f ** 2) * np.tanh(power) * np.cos(delta_mhz / 100)


def plv_model(power, delta_mhz):
    """Simple phase locking value proxy."""
    return np.exp(-abs(delta_mhz) / 150) * np.tanh(power)


def main():
    freqs = np.linspace(4.5, 6.5, 50)
    powers = np.linspace(0.1, 2.0, 50)
    detunings = np.linspace(-200, 200, 41)

    results = []
    Z = np.zeros((len(powers), len(freqs)))

    for k, delta in enumerate(detunings):
        for i, power in enumerate(powers):
            for j, f in enumerate(freqs):
                g = g_ls_model(f, power, delta)
                if k == len(detunings) // 2:
                    Z[i, j] = g
                plv = plv_model(power, delta)
                results.append({
                    "pump_freq_GHz": float(f),
                    "pump_power": float(power),
                    "delta_MHz": float(delta),
                    "g_LS": float(g),
                    "plv": float(plv),
                    "valid": 0.14 <= g <= 0.20
                })

    with open("result/fluxpump_scan.json", "w") as fh:
        json.dump({"data": results}, fh, indent=2)

    plt.imshow(Z, extent=[4.5, 6.5, 0.1, 2.0], origin="lower", aspect="auto", cmap="viridis")
    plt.colorbar(label="g_LS")
    plt.xlabel("Pump Frequency (GHz)")
    plt.ylabel("Pump Power")
    plt.title("Flux-Pump Gain Map (delta=0 MHz)")
    plt.tight_layout()
    plt.savefig("docs/plot/fluxpump_gLS_heatmap.png")
    plt.close()


if __name__ == "__main__":
    main()
