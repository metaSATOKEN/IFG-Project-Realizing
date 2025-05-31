.PHONY: install dev-install test figs7

install:
	# オフラインで使う場合は wheels/ に .whl ファイルを配置し、
	# pip install --no-index --find-links=wheels -r requirements.txt
	# を make install に書き換えてください。
	pip install --no-index --find-links=wheels -r requirements.txt || pip install -r requirements.txt
	pip install -e .

dev-install:
	pip install -r requirements-dev.txt

test: install dev-install
	pytest -q tests

figs7: install dev-install
	@ [ -f data/resonance_experiment.csv ] || (echo "Missing: data/resonance_experiment.csv" && exit 1)
	@ [ -f result/metrics.json ] || (echo "Missing: result/metrics.json" && exit 1)
	@ [ -f result/noise_fit.json ] || (echo "Missing: result/noise_fit.json" && exit 1)
	@ [ -f result/theory_noise.json ] || (echo "Missing: result/theory_noise.json" && exit 1)
	@ [ -f data/dd_experiment.csv ] || (echo "Missing: data/dd_experiment.csv" && exit 1)
	@ [ -f result/t2.json ] || (echo "Missing: result/t2.json" && exit 1)
	@ [ -f result/temperature_drift.csv ] || (echo "Missing: result/temperature_drift.csv" && exit 1)
	@ [ -f result/heatload.json ] || (echo "Missing: result/heatload.json" && exit 1)
	python src/compare_resonance.py data/resonance_experiment.csv result/metrics.json --out docs/plot/fig7_1.png
	python src/compare_noise.py result/noise_fit.json result/theory_noise.json --out docs/plot/fig7_2.png
	python src/compare_dd_decay.py data/dd_experiment.csv result/t2.json --out docs/plot/fig7_3.png
	python src/generate_error_analysis_flow.py --out docs/plot/fig7_4.png
