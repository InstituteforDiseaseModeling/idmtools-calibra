=============================
|calibra| installation
=============================

Follow the steps below to install |calibra|.

Prerequisites
=============

First, ensure the following prerequisites are met.

* Windows 10 Pro or Enterprise, Linux, or Mac

* |Python_supp| (https://www.python.org/downloads/release)

* A file that indicates the pip index-url:

    .. container:: os-code-block

        .. container:: choices

            * Windows
            * Linux

        .. container:: windows

            In C:\\Users\\Username\\pip\\pip.ini, containing the following::

                [global]
                index-url = https://packages.idmod.org/api/pypi/pypi-production/simple

        .. container:: linux

            In $HOME/.config/pip/pip.conf, containing the following::

                [global]
                index-url = https://packages.idmod.org/api/pypi/pypi-production/simple

Installation instructions
=========================

#.  Open a command prompt and create a virtual environment in any directory you choose. The
    command below names the environment "v-calibra", but you may use any desired name::

        python -m venv v-calibra

#.  Activate the virtual environment:

    .. container:: os-code-block

        .. container:: choices

            * Windows
            * Linux

        .. container:: windows

            Enter the following::

                v-calibra\Scripts\activate

        .. container:: linux

            Enter the following::

                source v-calibra/bin/activate

#.  Install |calibra| packages::

        pip install idmtools_calibra

    If you are on Python 3.6, also run::

        pip install dataclasses

    If you are on Linux, also run::

        pip install keyrings.alt

#.  When you are finished, deactivate the virtual environment by entering the following at a command prompt::

        deactivate
