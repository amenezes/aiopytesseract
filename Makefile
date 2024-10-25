.DEFAULT_GOAL := about
VERSION := $(shell cat aiopytesseract/__init__.py | grep '__version__ ' | cut -d'"' -f 2)

lint:
ifeq ($(SKIP_STYLE), )
	@echo "> running isort..."
	isort aiopytesseract
	isort tests
	isort examples
	@echo "> running black..."
	black aiopytesseract
	black tests
endif
	@echo "> running flake8..."
	flake8 aiopytesseract
	flake8 tests
	@echo "> running mypy..."
	mypy aiopytesseract

tests:
	@echo "> unittest"
	python -m pytest -vv --no-cov-on-fail --color=yes --durations=10 --cov-report xml --cov-report term --cov=aiopytesseract tests

docs:
	@echo "> generate project documentation..."
	@cp README.md docs/index.md
	mkdocs serve -a 0.0.0.0:8000

install-deps:
	@echo "> installing dependencies..."
	uv pip install -r requirements-dev.txt
	pre-commit install

tox:
	@echo "> running tox..."
	tox -r -p all

about:
	@echo "> aiopytesseract: $(VERSION)"
	@echo ""
	@echo "make lint         - Runs: [isort > black > flake8 > mypy]"
	@echo "make tests        - Runs: tests."
	@echo "make ci           - Runs: [lint > tests]"
	@echo "make tox          - Runs tox."
	@echo "make docs         - Generate project documentation."
	@echo "make install-deps - Install development dependencies."
	@echo ""
	@echo "mailto: alexandre.fmenezes@gmail.com"

ci: lint tests
ifeq ($(GITHUB_HEAD_REF), false)
	@echo "> uploading report..."
	codecov --file coverage.xml -t $$CODECOV_TOKEN
endif

all: install-deps ci

.PHONY: lint tests ci docs install-deps tox all
