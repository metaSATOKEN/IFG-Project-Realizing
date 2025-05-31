.PHONY: install dev-install test figs7

install:
	pip install -r requirements.txt

dev-install:
	pip install -r requirements-dev.txt

test: install dev-install
	pytest -q tests

figs7:
	python src/compare_resonance.py data/resonance_experiment.csv result/metrics.json --out docs/plot/fig7_1.png
	python src/compare_noise.py result/noise_fit.json result/theory_noise.json --out docs/plot/fig7_2.png
	python src/compare_dd_decay.py data/dd_experiment.csv result/t2.json --out docs/plot/fig7_3.png
	python src/generate_error_analysis_flow.py --out docs/plot/fig7_4.png
