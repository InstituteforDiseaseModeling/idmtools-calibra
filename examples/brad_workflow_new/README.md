<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

- [How to run optim_tool example](#how-to-run-optim_tool-example)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# How to run optim_tool example 
1. Activate your virtual environment

2. Install idmtools-calibra
    ```bash
    pip install idmtools-calibra --index-url=https://email:password@packages.idmod.org/api/pypi/pypi-staging/simple
    OR
    pip install idmtools-calibra --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple
    ```
3. First time run examples, install all emodpy and emodpy-tbhiv dependency

    `pip install -r requirements_b_example.txt`

4. install dataclasses if you are using python 3.6.x

    `pip install dataclasses`

5. login to bamboo and cache your credential for download Eradication.exe, schema. etc.(need turn on IDM VPN)

    `python .dev_scripts/bamboo_login.py -u youremail@idmod.org -p password`
 
6. run examples, ie
   
    `python sa_base_or_calib_dynamic.py`

7. switch platform between Windows BELEGOST and Linux CALCULON in code. for example

    `platform = Platform('CALCULON')`