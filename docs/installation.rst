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

    * For Windows, in C:\\Users\\Username\\pip\\pip.ini add the following::

        [global]
        index-url = https://packages.idmod.org/api/pypi/pypi-production/simple

    * For Linux, in $HOME/.config/pip/pip.conf add the following::

        [global]
        index-url = https://packages.idmod.org/api/pypi/pypi-production/simple

Installation instructions
=========================

#.  Open a command prompt and create a virtual environment in any directory you choose. The
    command below names the environment "v-calibra", but you may use any desired name::

        python -m venv v-calibra

#.  Activate the virtual environment:

    * For Windows, enter the following::

        v-calibra\Scripts\activate

    * For Linux, enter the following::

        source v-calibra/bin/activate


#.  Install |calibra| packages::

        pip install idmtools_calibra

    * If you are on Python 3.6, also run::

        pip install dataclasses

    * If you are on Linux, also run::

        pip install keyrings.alt

#.  When you are finished, deactivate the virtual environment by entering the following at a command prompt::

        deactivate
