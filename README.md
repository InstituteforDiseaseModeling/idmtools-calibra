# emodpy

[![Build docs and deploy to GH Pages](https://github.com/InstituteforDiseaseModeling/idmtools-calibra/actions/workflows/deploy_docs_api.yml/badge.svg)](https://github.com/InstituteforDiseaseModeling/idmtools-calibra/actions/workflows/deploy_docs_api.yml)
[![Lint](https://github.com/InstituteforDiseaseModeling/idmtools-calibra/actions/workflows/lint.yml/badge.svg)](https://github.com/InstituteforDiseaseModeling/idmtools-calibra/actions/workflows/lint.yml)
[![Build and publish package to Pypi](https://github.com/InstituteforDiseaseModeling/idmtools-calibra/actions/workflows/publish-pypi.yml/badge.svg)](https://github.com/InstituteforDiseaseModeling/idmtools-calibra/actions/workflows/publish-pypi.yml)
[![Tests](https://github.com/InstituteforDiseaseModeling/idmtools-calibra/actions/workflows/tests.yml/badge.svg)](https://github.com/InstituteforDiseaseModeling/idmtools-calibra/actions/workflows/tests.yml)


# idmtools-calibra

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

- [User Installation](#user-installation)
  - [Pre-requisites](#pre-requisites)
- [Development Environment Setup](#development-environment-setup)
  - [First Time Setup](#first-time-setup)
  - [Development Tips](#development-tips)
  - [Documentation](#documentation)
    - [Build mkdocs locally](#build-mkdocs-locally)
    - [Build and publish document from Github Actions](#build-and-publish-document-from-github-actions)
  - [Resume Supports Parameters](#resume-supports-parameters)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->


# User Installation 

```bash
pip install idmtools-calibra 
```

## Pre-requisites
- Python 3.10, 3.11, 3.12, 3.13, 31.4 x64


# Development Environment Setup

When setting up your environment for the first time, you can use the following instructions

## First Time Setup
1) Clone the repository:
   ```bash
   > git clone https://github.com/InstituteforDiseaseModeling/idmtools_calibra.git
   ```
2) Create a virtualenv. On Windows, please use venv to create the environment
   `python -m venv idmtools_calibra`
   On Unix(Mac/Linux) you can use venv or virtualenv
3) Activate the virtualenv
4) Then run `python ./.dev_scripts/bootstrap.py`. This will install all the tools. 

## Development Tips

There is a Makefile file available for most common development tasks. Here is a list of commands
```bash
clean       -   Clean up temproary files
lint        -   Lint package and tests
test        -   Run All tests
docs        -   Build mkdocs documentation
bump-patch  -   Bump patch version
bump-minor  -   Bump minor version
bump-major  -   Bump major version
```

## Documentation
Documentation available at https://institutefordiseasemodeling.github.io/idmtools-calibra/.

### Build mkdocs locally

Create and activate a venv.
Navigate to the root directory of the repo.
```bash
cd docs
pip install -r requirments.txt
mkdocs build  # build docs
mkdocs serve  # view docs from  http://127.0.0.1:8000/idmtools_calibra/
mkdocs gh-deploy # deploy to github (need to be on the specific branch)
```
### Build and publish document from Github Actions
Go to Github Actions -> Run GHA job: **Deploy MkDocs via GitHub Pages API**

## Resume Supports Parameters
CalibManager's run_calibration method supports the following parameters for resume action, for example:
 
  run_calibration(resume=True, iteration=2, iter_step='analyze')

- resume: bool, default=False, required for resume
  Note: resume=True is required for resume, otherwise all the parameters will be ignored
- iteration: int, default=None, from which iteration to resume
  Note: in None case, calibra will detect and take the last iteration from last run
- iter_step: str, default=None, from which calibration step to resume
  Note: in None case, calibra will detect and take the valid step of the iteration
- loop: bool, default=True, if like to continue to next iteration
  Note: by default, resume will continue to run next iteration
- max_iterations, int, default=None, user can override the max_iterations defined in calib_manager
  Note: in None case, calibra will take max_iterations defined in calib_manager
- backup: bool, default=False, if like to backup Calibration.json
  Note: by default, resume will not make a backup of Calibration.json
- dry_run: bool, default=False, if like to really execute resume action
  Note: by default (dry_run= False), resume will go ahead to execute resume action
  
iter_step supports the following options:
- commission: will start to run a new iteration
- analyze: analyze the output data from given iteration
- plot: just plot for given iteration
- next_point: go directly to next iteration

## Examples as Reference

The `examples/` directory contains canonical usage patterns:
- `examples/solar/` — Simplest: fits a linear model (y = mx + c) to data using OptimTool + RMSE
- `examples/sir/` — SIR epidemiological model with multiple output configuration options
- `examples/emod_sir/` — EMOD sir disease model calibrations using COMPS platform
When implementing new features or debugging, the solar example (`solar_optimtool_linear_model.py`) is the clearest end-to-end reference.