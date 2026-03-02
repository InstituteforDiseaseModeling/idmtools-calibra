.PHONY: help clean lint test test-all test-failed test-long test-no-long test-comps test-docer test-docker test-python test-smoke test-report coverage-report coverage coverage-smoke coverage-all coverage-report-view merge-reports dist release-staging bump-release bump-release-dry-run bump-minor bump-minor-dry-run bump-major bump-major-dry-run bump-patch bump-patch-dry-run
PACKAGE_NAME=idmtools_calibra
# Platform Independent options for common commands
MV?=mv
RM?=rm
# Convience function for running dev scripts
PDS=$(PY) ./.dev_scripts/
PY?=python
IPY=python -c
PDR=$(PDS)run.py
CLDIR=$(PDS)clean_dir.py


help:
	$(PDS)get_help_from_makefile.py

clean: ## Clean most of the temp-data from the project
	$(MAKE) -C tests clean
	-rm -rf *.pyc *.pyo *.done .coverage dist build **/__pycache__

clean-all: clean ## Deleting package info hides plugins so we only want to do that for packaging
	-rm -rf **/*.egg-info/

lint: ## check style with flake8
	flake8 --ignore=E501,W291 $(PACKAGE_NAME)

test-unittests: ## Run unittests
	cd tests/unittests && python -m pytest -v --durations=3 --junitxml=test_results.xml

test-it-tests: ## Run interation tests
	cd tests/integration && python -m pytest -v --durations=3 --junitxml=test_results.xml

test-algo-tests: ## Run algorithms tests
	cd tests/algorithms && python -m pytest -v --durations=3 --junitxml=test_results.xml

test-all: test-unittests test-algo-tests test-it-tests ## Run all tests

dist: clean ## build package
	python -m build

release-staging: dist ## perform a release to staging
	twine upload --verbose --repository-url https://upload.test.pypi.org/legacy/ dist/*

bump-patch: ## bump the patch version
	python bump_version --patch

bump-minor: ## bump the minor version
	python bump_version --minor

bump-major: ## bump the major version
	python bump_version major

build-docs: ## build docs
	mkdocs build

build-docs-serve: build-docs ## builds docs and launch a webserver and watches for changes to documentation
	mkdocs serve

docs: build-docs  ## build docs

docs-serve: build-docs-serve ## builds docs and launch a webserver and watches for changes to documentation