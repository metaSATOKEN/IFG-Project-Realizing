from pathlib import Path
import json

from src.fit_theory_experiment_mapping import fit_params


def test_fit_params(tmp_path: Path) -> None:
    theory = {"fc_GHz": 5.0, "Q_loaded": 1000}
    metrics = {"fc_GHz": 5.1, "Q_loaded": 900}
    t2 = {"Gamma_dec": 0.01}
    noise = {"noise_model": {"A": 1.0, "B": 2.0}}
    temp_csv = tmp_path / "temp.csv"
    with open(temp_csv, "w") as fh:
        fh.write("time,temp\n0,0\n1,0.1\n")
    heat = [{"heat": 1.0}, {"heat": 2.0}]
    theory_p = tmp_path / "theory.json"
    metrics_p = tmp_path / "metrics.json"
    t2_p = tmp_path / "t2.json"
    noise_p = tmp_path / "noise.json"
    heat_p = tmp_path / "heat.json"
    out_p = tmp_path / "out.json"
    for p, d in [
        (theory_p, theory),
        (metrics_p, metrics),
        (t2_p, t2),
        (noise_p, noise),
        (heat_p, heat),
    ]:
        with open(p, "w") as fh:
            json.dump(d, fh)

    result = fit_params(theory_p, metrics_p, t2_p, noise_p, temp_csv, heat_p, out_p)
    loaded = json.loads(out_p.read_text())

    assert "fc_GHz" in loaded and loaded["fc_GHz"] != 0
    assert "Q_loaded" in loaded and isinstance(loaded["Q_loaded"], (int, float))
    assert "Gamma_dec" in loaded and loaded["Gamma_dec"] == t2["Gamma_dec"]
    assert "noise_A" in loaded and loaded["noise_A"] == noise["noise_model"]["A"]
    assert "noise_B" in loaded and loaded["noise_B"] == noise["noise_model"]["B"]
    assert isinstance(result, dict)
