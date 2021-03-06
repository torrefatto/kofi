.PHONY: clean clean-test clean-pyc clean-build docs help
.DEFAULT_GOAL := help

define BROWSER_PYSCRIPT
import os, webbrowser, sys

from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

BROWSER := python -c "$$BROWSER_PYSCRIPT"
VERSION := 0.2.0

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache

lint: ## check style with flake8
	flake8 kofi tests

test: ## run tests quickly with the default Python
	pytest tests/

coverage: ## check code coverage quickly with the default Python
	coverage run --source kofi -m pytest
	coverage report -m
	coverage html
	$(BROWSER) htmlcov/index.html

docs: ## generate Sphinx HTML documentation, including API docs
	rm -f docs/kofi.rst
	rm -f docs/modules.rst
	sphinx-apidoc -o docs/ kofi
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	$(BROWSER) docs/_build/html/index.html

servedocs: docs ## compile the docs watching for changes
	watchmedo shell-command -p '*.rst' -c '$(MAKE) -C docs html' -R -D .

fix: bumpmicro dist

release: bumpminor dist

majrelease: bumpmajor dist

bumpmicro:
	bumpversion micro

bumpminor:
	bumpversion minor

bumpmajor:
	bumpversion major

dist: clean format
	python setup.py sdist
	python setup.py bdist_wheel
	ls -l dist

format:
	black kofi/

install: clean ## install the package to the active Python's site-packages
	python setup.py install

docker-build: ## build the production image
	docker build -t torrefatto/kofi:$(VERSION) .

docker-dev-build: ## build the development image
	docker build -t torrefatto/kofi-dev:$(VERSION) -d Dockerfile-dev

docker-dev-run: ## run the development container
	docker run -v $$PWD:/src -p 1312:1312 -t torrefatto/kofi-dev:$(VERSION) --graphiql
