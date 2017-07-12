install:
	pip install -r requirements.txt

test:
	pytest tests/test.py

.PHONY: install test
