![Staging: idmtools-calibra]

# idmtools-calibra

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

- [User Installation](#user-installation)
  - [Pre-requisites](#pre-requisites)
- [Development Environment Setup](#development-environment-setup)
  - [First Time Setup](#first-time-setup)
  - [Development Tips](#development-tips)
  - [Building docs](#building-docs)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->


# User Installation

```bash
pip install idmtools-calibra --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple
```

## Pre-requisites
- Python 3.6/3.7 x64


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
coverage    -   Run tests and generate coverage report that is shown in browser
```
On Windows, you can use `pymake` instead of `make`


## Building docs

From your virtualenv, install idmtools_calibra and all dependencies. Then from the docs folder, run ``pip install -r requirements.txt``. You can build the docs from that folder using ``make html``. 

To pick up docstring changes, you must re-run the setup script to include those changes in the itertool installation. Then run ``make clean`` and re-run ``make html``. 

Documentation on Read the Docs is available at https://docs.idmod.org/projects/idmtools_calibra/en/latest/.


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
