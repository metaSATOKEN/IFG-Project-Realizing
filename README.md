# IFG Project – Hardware Optimization Tasks

This repository contains theoretical and experimental parameters for the IFG project.  
Your task is to support *hardware-level design automation* for key quantum components.

## Scope

You are to implement calculations, simulations, and optimizations for:

1. **μ-cavity (microwave cavity) design**
   - Maximize quality factor Q
   - Minimize mode volume V
   - Ensure impedance matching with Qubit chip interface

2. **Flux-pump resonance optimization**
   - Given target g_{LS} = 0.17 ± 0.03
   - Explore drive amplitude/frequency/phase parameter space
   - Output: Gain profile, bandwidth, g_{LS} stability zones

3. **SQUID coupling**
   - Model mutual inductance with Qubit + cavity
   - Optimize loop size and position for max ΔB sensitivity

4. **16-Qubit layout auto-generation**
   - Layout with:
     - Bus resonator architecture (shared + local)
     - Minimal crosstalk (< -50 dB)
   - Output: chip geometry (coordinates), parasitic estimation

## Parameters

Refer to param_table_v0.3.6_FULL.txt for constraints.  
Use representative values unless instructed otherwise:

- Target cavity Q: \(6 \times 10^6\)
- Target V_mode: ~0.05 cm³
- SQUID sensitivity: 0.45 pT/√Hz
- Optical cavity: \(κ_{\text{geom}} ≈ 2.3 × 10^{-3}\)

## Expected Output

For each task, produce:
- Equation derivation (if needed)
- Python code (simulation or solver)
- CSV or JSON data output
- Brief comment block explaining the assumptions

All units should be SI or convertible.

If in doubt, default to quantum computing design conventions.
