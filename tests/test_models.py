import numpy as np
from src.compute_noise_spectrum import noise_model
from src.extract_quantum_metrics import lorentzian
from src.visualize_results import compute_lorentz_curve


def test_noise_model():
    w = np.array([1.0, 10.0])
    A, B = 1.0, 2.0
    expected = A / w + B
    assert np.allclose(noise_model(w, A, B), expected)


def test_lorentzian():
    f = np.array([1.0])
    fc = 1.0
    ql = 10.0
    depth = 0.5
    base = 1.0
    val = lorentzian(f, fc, ql, depth, base)
    assert val.shape == f.shape
    assert np.isclose(val[0], base - depth)


def test_compute_lorentz_curve():
    fc = 5.0
    ql = 1000.0
    f = np.array([fc])
    curve = compute_lorentz_curve(fc, ql, f)
    assert curve[0] <= 1.0
