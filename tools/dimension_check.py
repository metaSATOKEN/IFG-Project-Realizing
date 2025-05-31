#!/usr/bin/env python3
"""Simple dimension analysis for Chapter 3 equations."""

from __future__ import annotations

from typing import Dict


Dimension = Dict[str, int]


def combine(*dims: Dimension) -> Dimension:
    """Return product of multiple dimensions."""
    result: Dimension = {}
    for d in dims:
        for k, v in d.items():
            result[k] = result.get(k, 0) + v
    return {k: v for k, v in result.items() if v}


def is_dimensionless(d: Dimension) -> bool:
    return all(v == 0 for v in d.values())


def main() -> None:
    m_info: Dimension = {"bit": -1, "s": -2}
    hbar_info: Dimension = {"bit": 1, "s": 1}
    omega: Dimension = {"s": -1}
    q: Dimension = {"bit": 1}

    # Free energy term ~ hbar_info * omega
    free_dim = combine(hbar_info, omega)
    # Potential term ~ m_info * omega**2 * q**2
    potential_dim = combine(m_info, {"s": -2}, {"bit": 2})

    print("Free term dimension:", free_dim, "dimensionless:", is_dimensionless(free_dim))
    print("Potential term dimension:", potential_dim, "dimensionless:", is_dimensionless(potential_dim))


if __name__ == "__main__":
    main()
