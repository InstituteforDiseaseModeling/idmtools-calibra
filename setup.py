#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script for the itertool"""
import os

from setuptools import setup, find_packages
import sys
CURRENT_DIRECTORY = os.path.dirname(__file__)
version_file = os.path.join(CURRENT_DIRECTORY, "version.py")
version = {}
with open(version_file) as f:
    exec(f.read(), version)  # This will define __version__

with open('requirements.txt') as requirements_file:
    lines = requirements_file.read().strip().split("\n")
requirements = []
arguments = []
develop_install = 'develop' in sys.argv
for line in lines:
    if line[0] == '-':
        # we have a flag to handle on the command line
        arguments.extend(line.split(' '))
    else:
        # we have an actual package requirement
        requirements.append(line)
if develop_install:
    sys.argv.extend(arguments)

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('history_matching_requirements.txt') as requirements_file:
    history_matching_requirements = requirements_file.read().split("\n")

dev_requirements = ['flake8', 'coverage', 'bump2version', 'twine']
setup_requirements = []
test_requirements = ['pytest', 'pytest-runner', 'pytest-timeout', 'pytest-cache'] + dev_requirements

extras = dict(test=test_requirements, dev=dev_requirements)
extras['history-matching'] = history_matching_requirements

authors = [
    ("Ross Carter", "rcarter@idmod.org"),
    ("Sharon Chen", "shchen@idmod.org"),
    ("Clinton Collins", "ccollins@idmod.org"),
    ("Zhaowei Du", "zdu@idmod.org"),
    ("Mary Fisher", "mafisher@idmod.org"),
    ("Mandy Izzo", "mizzo@idmod.org"),
    ("Clark Kirkman IV", "ckirkman@idmod.org"),
    ("Benoit Raybaud", "braybaud@idmod.org"),
    ("Jen Schripsema", "jschripsema@idmod.org")
]

setup(
    author=[author[0] for author in authors],
    author_email=[author[1] for author in authors],
    classifiers=[
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12'
    ],
    description="Calibration tool for IDM-Tools",
    install_requires=requirements,
    long_description=readme,
    include_package_data=True,
    keywords='modeling, IDM',
    name='idmtools-calibra',
    entry_points={"idmtools_cli.cli_plugins": ["calibra=idmtools_calibra.cli.commands:calibra"]},
    packages=find_packages(),
    setup_requires=setup_requirements,
    python_requires='>3.7',
    test_suite='tests',
    extras_require=extras,
    version=version['__version__']
)
