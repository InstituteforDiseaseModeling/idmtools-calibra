.PHONY: clean clean-all lint coverage release dist bump-minor bump-major bump-patch bump-release
# Python from command line
IPY=python -c
# If user did not define python, set our default to python
PY?=python
# Shortcut for running scripts from the dev_scripts folder
PDS=$(PY) ../.dev_scripts/
# Shortcut for the cleandir command
CLDIR=$(PDS)clean_dir.py
# Shortcut for the run command
PDR=$(PDS)run.py
# Shortcut for commnad to run tests with
TEST_COMMAND=py.test --durations=3 -v --junitxml=test_results.xml
# Test command options
TEST_RUN_OPTS=?
# Builds full test command
FULL_TEST_CMD=$(PDR) -w 'tests' $(TEST_RUN_OPTS) -ex '$(TEST_COMMAND)
# Command to run coverage
COVERAGE_CMD=$(PDR) -w 'tests' $(TEST_RUN_OPTS) -p . ../ -ex 'coverage run --omit="*/test*,*/setup.py"
REPO_URL=?https://packages.idmod.org/api/pypi/idm-pypi-staging/
PACKAGE_NAME=itertool

# Makefile rules

help:
	$(PDS)get_help_from_makefile.py

setup-dev: ## Install all dependencies needed for development
    $(PDS)bootstrap.py

clean: ## Clean most of the temp-data from the project
	$(CLDIR) --file-patterns "*.py[co],*.done,*.log,**/.coverage" \
		--dir-patterns "**/__pycache__,**/htmlcov,**/.pytest_cache" --directories "dist,build"

# WARNING: You will need to re-install after running this
clean-all:  ## Deleting package info hides plugins so we only want to do that for packaging
	@make clean
	$(CLDIR) --dir-patterns "**/*.egg-info/"lint: ## check style with flake8
	flake8 --ignore=E501,W291 $(PACKAGE_NAME) tests


test: ## Run our tests
	$(FULL_TEST_CMD)

test-failed: ## Run only previously failed tests
	$(FULL_TEST_CMD) --lf'

# If you want to label tests and then exclude those from a rule, you can use the following
#test-unit-only: ## Run only unit tests
#	$(FULL_TEST_CMD) -m "not comps and not docker"'

coverage: ## Generate a code-coverage report
	@make clean
	# We have to run in our tests folder to use the proper config
	$(COVERAGE_CMD)
	@+$(IPY) "import shutil as s; s.move('tests/.coverage','.coverage')"
	coverage report -m
	coverage html -i
	$(PDS)/launch_dir_in_browser.py htmlcov/index.html

# Release
dist: ## build our package
	@make clean
	python setup.py sdist bdist_wheel

release: ## perform a release to staging
	@make dist
	twine upload --verbose --repository-url $(REPO_URL) dist/*

bump-release: ## bump the release version.
	bump2version release --commit

bump-release-dry-run: ## bump the release version. (dry run)
	bump2version release --dry-run --allow-dirty --verbose

bump-major: ## bump the major version
	bump2version major --commit

bump-major-dry-run: ## bump the major version(dry run)
	bump2version major --dry-run --allow-dirty --verbose

bump-minor: ## bump the minor version
	bump2version minor --commit

bump-minor-dry-run: ## bump the minor version(dry run)
	bump2version minor --dry-run --allow-dirty --verbose

bump-patch: ## bump the patch version
	bump2version patch --commit

bump-patch-dry-run: ## bump the patch version(dry run)
	bump2version patch --dry-run --allow-dirty --verbose# Docs
build-docs: ## build docs(only works on linux at moment due to make.bat not running by default)
	$(PDR) -wd 'docs' -ex 'make html'

build-docs-server: ## builds docs and launch a webserver
	@make build-docs
	@+$(IPY) "print('Serving documentation @ server at http://localhost:8000 . Ctrl + C Will Stop Server')"
	$(PDR) -wd 'docs/_build/html' -ex 'python -m http.server'
