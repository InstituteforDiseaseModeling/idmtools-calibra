HTML_TEST_REPORT ?= test_results.html
# Set comps to high because we mostly just wait on COMPS to finish
PARALLEL_TEST_COUNT ?= 12
.PHONY: help clean test test-all test-failed test-long test-no-long test-comps test-docer test-docker test-python test-smoke test-report coverage-report coverage coverage-smoke coverage-all coverage-report-view merge-reports
.EXPORT_ALL_VARIABLES:
PY?=python
# Platform Independent options for common commands
MV?=mv
RM?=rm
# Convience function for running dev scripts
PDS=$(PY) ../../.dev_scripts/
# Where should we store our reports
REPORT_DIR?= reports
TEST_REPORT ?= test_results.xml
# Test Configuration
SERIAL_TESTING?=
PARALLEL_TESTING?=
TEST_EXTRA_OPTS?=
DOCKER_REPO?=docker-staging
NO_SPINNER?=1
PARALLEL_TEST_COUNT?=8
TEST_COMMAND =  py.test --timeout=600 --junitxml=$(REPORT_DIR)/$(TEST_REPORT)



help:  ## This help
	$(PDS)get_help_from_makefile.py -f $(mkfile_path)

clean:
	-$(RM) -rf .pytest_cache .test_platform reports assets *.log *.log* *.buildlog __pycache__ *.html *.xml .coverage

test: ## Run default set of tests which exclude comps and docker tests
	-mkdir reports
	$(TEST_COMMAND)
