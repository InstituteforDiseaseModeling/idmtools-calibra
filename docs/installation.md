<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

- [Install](#install)
  - [Prerequisites](#prerequisites)
  - [Installation instructions](#installation-instructions)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Install

Follow the steps below to install idmtools_calibra.

## Prerequisites

First, ensure the following prerequisites are met.

- Windows 10 Pro or Enterprise, Linux, or Mac
- Python >= 3.10 (https://www.python.org/downloads/release)
- A file that indicates the pip index-url:

    === "Windows"
        In `C:\Users\Username\pip\pip.ini` add the following:
        ```ini
        [global]
        index-url = https://pypi.org/simple
        ```

    === "Linux / Mac"
        In `$HOME/.config/pip/pip.conf` add the following:
        ```ini
        [global]
        index-url = https://pypi.org/simple
        ```

## Installation instructions

1. Open a command prompt and create a virtual environment in any directory you choose.
   The command below names the environment `v-calibra`, but you may use any desired name:

    ```bash
    python -m venv v-calibra
    ```

2. Activate the virtual environment:

    === "Windows"
        ```bat
        v-calibra\Scripts\activate
        ```

    === "Linux / Mac"
        ```bash
        source v-calibra/bin/activate
        ```

3. Install idmtools_calibra:

    ```bash
    pip install idmtools_calibra
    ```

    !!! note
        If you are on Linux, also run:
        ```bash
        pip install keyrings.alt
        ```

4. When you are finished, deactivate the virtual environment:

    ```bash
    deactivate
    ```
