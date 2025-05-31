 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a/tools/fluxpump_optimize.py b/tools/fluxpump_optimize.py
index f53d7ec3f9df6c3ee28b7580fcfd8e76de5ba9ff..5cc8072bfa6118522a9b1f8f4850613c055f2a9a 100644
--- a/tools/fluxpump_optimize.py
+++ b/tools/fluxpump_optimize.py
@@ -1,59 +1,152 @@
 """
 Script Name: fluxpump_optimize.py
 Purpose: Optimize flux pump control parameters
-Dependencies: numpy, scipy
+
+Gain model:
+    g_LS = (κ_ext / 2) × Re[χ(ω_p)] / [1 + |χ(ω_p)|² × |α_p|²]
+    χ(ω) = 1 / (ω - ω_q + iγ)
+    α_p = ε_p × I_bias
+
+Dependencies: numpy, scipy, argparse (optionally matplotlib)
 Usage:
-    python tools/fluxpump_optimize.py
+    python tools/fluxpump_optimize.py [--freq_p GHz] [--eps val] [--bias val]
+        [--target val] [--mu val] [--kappa val] [--gamma val]
 
 Outputs:
     - 最適パラメータ
     - 目的関数評価値
     - （必要に応じて）プロット or ファイル出力
 
 Author: Codex（MetaShirou prompt経由）
 """
 
+import argparse
 import numpy as np
 from scipy.optimize import minimize
 
-kappa_ext = 1e6
-omega_q = 2 * np.pi * 7e9
-gamma = 1e6
-
-g_target = 0.17
-mu_penalty = 0.1
+OMEGA_Q = 2 * np.pi * 7e9  # rad/s
 
 
-def chi(omega: float) -> complex:
+def chi(omega: float, omega_q: float, gamma: float) -> complex:
+    """Return susceptibility χ(ω)."""
     return 1.0 / (omega - omega_q + 1j * gamma)
 
 
-def g_ls(omega_p: float, epsilon_p: float, i_bias: float) -> float:
-    chi_val = chi(omega_p)
+def g_ls(
+    omega_p: float,
+    epsilon_p: float,
+    i_bias: float,
+    kappa_ext: float,
+    omega_q: float,
+    gamma: float,
+) -> float:
+    """Return gain g_LS for given parameters."""
+    chi_val = chi(omega_p, omega_q, gamma)
     alpha_p = epsilon_p * i_bias
     numerator = (kappa_ext / 2.0) * np.real(chi_val)
     denom = 1.0 + (abs(chi_val) ** 2) * (abs(alpha_p) ** 2)
     return numerator / denom
 
 
-def bandwidth() -> float:
+def bandwidth(kappa_ext: float) -> float:
+    """Simplified bandwidth model."""
     return kappa_ext
 
 
-def objective(x: np.ndarray) -> float:
+def objective(
+    x: np.ndarray,
+    g_target: float,
+    mu_penalty: float,
+    kappa_ext: float,
+    omega_q: float,
+    gamma: float,
+) -> float:
+    """Objective function J for optimization."""
     omega_p, epsilon_p, i_bias = x
-    g_val = g_ls(omega_p, epsilon_p, i_bias)
-    bw = bandwidth()
+    g_val = g_ls(omega_p, epsilon_p, i_bias, kappa_ext, omega_q, gamma)
+    bw = bandwidth(kappa_ext)
     return (g_target - g_val) ** 2 + mu_penalty * (1.0 / bw)
 
 
 if __name__ == "__main__":
-    x0 = np.array([2 * np.pi * 7.5e9, 0.1, 0.9])
-    res = minimize(objective, x0, method="BFGS")
+    parser = argparse.ArgumentParser(description="Optimize flux pump parameters")
+    parser.add_argument("--freq_p", type=float, default=7.5, help="pump frequency in GHz")
+    parser.add_argument("--eps", type=float, default=0.1, help="pump amplitude")
+    parser.add_argument("--bias", type=float, default=0.9, help="bias current")
+    parser.add_argument("--target", type=float, default=0.17, help="g_LS target value")
+    parser.add_argument("--mu", type=float, default=0.1, help="bandwidth penalty coefficient")
+    parser.add_argument("--kappa", type=float, default=1e6, help="κ_ext value")
+    parser.add_argument("--gamma", type=float, default=1e6, help="dissipation rate γ")
+    parser.add_argument("--csv", type=str, default="", help="optional CSV output path")
+    parser.add_argument("--plot", type=str, default="", help="optional plot output path")
+    args = parser.parse_args()
+
+    x0 = np.array([2 * np.pi * args.freq_p * 1e9, args.eps, args.bias])
+    bounds = [
+        (2 * np.pi * 6e9, 2 * np.pi * 9e9),
+        (0.01, 1.0),
+        (0.5, 1.2),
+    ]
+
+    obj = lambda x: objective(x, args.target, args.mu, args.kappa, OMEGA_Q, args.gamma)
+    res = minimize(obj, x0, bounds=bounds, method="L-BFGS-B")
     w_opt, ep_opt, ib_opt = res.x
-    print("Optimal ω_p:", w_opt)
-    print("Optimal ε_p:", ep_opt)
-    print("Optimal I_bias:", ib_opt)
-    print("g_LS:", g_ls(w_opt, ep_opt, ib_opt))
-    print("BW:", bandwidth())
-    print("Minimum J:", res.fun)
+    g_val = g_ls(w_opt, ep_opt, ib_opt, args.kappa, OMEGA_Q, args.gamma)
+    w_opt_GHz = w_opt / (2 * np.pi * 1e9)
+    J_val = res.fun
+
+    print(f"ω_p [GHz]: {w_opt_GHz:.6f}")
+    print("ε_p:", ep_opt)
+    print("I_bias:", ib_opt)
+    print("g_LS:", g_val)
+    print("Minimum J:", J_val)
+
+    if not np.isfinite(J_val) or not np.isfinite(g_val):
+        print("Warning: non-finite optimization result")
+
+    if args.csv:
+        import csv
+
+        with open(args.csv, "w", newline="") as fh:
+            writer = csv.writer(fh)
+            writer.writerow([
+                "omega_p_GHz",
+                "epsilon_p",
+                "i_bias",
+                "g_LS",
+                "J",
+                "g_target",
+                "mu",
+                "kappa_ext",
+                "gamma",
+            ])
+            writer.writerow([
+                w_opt_GHz,
+                ep_opt,
+                ib_opt,
+                g_val,
+                J_val,
+                args.target,
+                args.mu,
+                args.kappa,
+                args.gamma,
+            ])
+
+    if args.plot:
+        try:
+            import matplotlib.pyplot as plt
+
+            plt.figure()
+            plt.axhline(args.target, color="gray", linestyle="--", label="g_target")
+            plt.scatter(w_opt_GHz, g_val, color="red", label="Optimal g_LS")
+            plt.xlabel("ω_p [GHz]")
+            plt.ylabel("g_LS")
+            plt.title(
+                f"Flux Pump Optimization (g_target={args.target}, μ={args.mu}, κ_ext={args.kappa})"
+            )
+            plt.legend()
+            plt.grid(True)
+            plt.tight_layout()
+            plt.savefig(args.plot)
+        except Exception as exc:
+            print("Plot failed:", exc)
 
EOF
)
