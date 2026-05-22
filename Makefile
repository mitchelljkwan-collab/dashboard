.PHONY: test lint test-html test-sweep

test: test-html lint

test-html:
	python3 -m pytest tests/ -v

test-sweep:
	python3 -m pytest tests/test_sweep.py -v

lint:
	npm run lint:css
