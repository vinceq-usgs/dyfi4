install:
	pip install -r requirements.txt

test:
        export CODECOV_TOKEN=6d05c269-742a-4225-86b5-9a31090919a5
	pytest --cov=dyfi tests/test.py
        codecov
        coverage xml
        bash <(curl -s https://codecov.io/bash)

.PHONY: install test
