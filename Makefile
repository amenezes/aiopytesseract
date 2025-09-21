.DEFAULT_GOAL := about
VERSION := $(shell cat aiopytesseract/__init__.py | grep '__version__ ' | cut -d'"' -f 2)

lint:
ifeq ($(SKIP_STYLE), )
	@echo "> running ruff format..."
	uv run ruff format aiopytesseract tests
	@echo "> running ruff check..."
	uv run ruff check --fix aiopytesseract tests
endif
	@echo "> running mypy..."
	uv run mypy aiopytesseract

tests:
	@echo "> running tests..."
	uv run python -m pytest -vv --no-cov-on-fail --color=yes --durations=10 --cov-report xml --cov-report term --cov=aiopytesseract tests

docs:
	@echo "> generating project documentation..."
	@cp README.md docs/index.md
	uv run mkdocs serve -a 0.0.0.0:8000

install-deps:
	@echo "> installing dependencies..."
	uv sync --group dev
	pre-commit install

build:
	@echo "> building package..."
	uv build

clean:
	@echo "> cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

publish-test:
	@echo "> publishing to test PyPI..."
	uv publish --publish-url https://test.pypi.org/legacy/

publish:
	@echo "> publishing to PyPI..."
	uv publish

about:
	@echo "> aiopytesseract: $(VERSION)"
	@echo ""
	@echo "make lint         - Runs: [ruff format > ruff check > mypy]"
	@echo "make tests        - Runs: tests with coverage"
	@echo "make ci           - Runs: [lint > tests]"
	@echo "make build        - Build package for distribution"
	@echo "make clean        - Clean build artifacts"
	@echo "make docs         - Generate project documentation"
	@echo "make install-deps - Install development dependencies"
	@echo "make publish-test - Publish to test PyPI"
	@echo "make publish      - Publish to PyPI"
	@echo ""
	@echo "mailto: alexandre.fmenezes@gmail.com"

ci: lint tests

release: clean build

all: install-deps ci

.PHONY: lint tests ci docs install-deps build clean publish-test publish about release all
