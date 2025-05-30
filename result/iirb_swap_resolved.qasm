OPENQASM 2.0;
include "qelib1.inc";
qreg q[16];

// ψ₀ ↔ ψ₁₅ via ψ₀ → ψ₅ → ψ₁₀ → ψ₁₅ (SWAPs: 2)
SWAP q[0], q[5];
SWAP q[5], q[10];
CX q[10], q[15];
SWAP q[5], q[10];
SWAP q[0], q[5];

// ψ₈ ↔ ψ₄ via ψ₈ → ψ₄ (SWAPs: 0)
CX q[8], q[4];
