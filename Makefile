.PHONY: test

test:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	pytest -q tests
