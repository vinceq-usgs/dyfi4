SHELL := /bin/bash

install:
	pip install -r requirements.txt

test:
	pytest --cov=dyfi tests/test.py
	codecov
	coverage xml
        bash <(curl -s https://codecov.io/bash)

.PHONY: install test
