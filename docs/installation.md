# Installation

## Quick install

```bash
pip install idmtools_calibra
```

---

## Prerequisites

- Windows 10+ Pro/Enterprise, Linux, or macOS
- Python: Versions 3.10, 3.11, 3.12, 3.13, or 3.14 are supported.

---

## Detailed installation

### 1. Create a virtual environment

```bash
python -m venv v-calibra
```

### 2. Activate it

=== "Windows"
    ```bat
    v-calibra\Scripts\activate
    ```

=== "Linux / macOS"
    ```bash
    source v-calibra/bin/activate
    ```

### 3. Install idmtools_calibra

```bash
pip install idmtools_calibra
```

!!! note "Linux additional dependency"
    On Linux, also install the keyring backend:
    ```bash
    pip install keyrings.alt
    ```

### 4. Verify the installation

```python
import idmtools_calibra
print(idmtools_calibra.__version__)
```

## Corporate or offline environments

If you are behind a corporate proxy or need to point pip at a custom index, create a pip configuration file:

=== "Windows"
    `C:\Users\<Username>\pip\pip.ini`:
    ```ini
    [global]
    index-url = https://pypi.org/simple
    ```

=== "Linux / macOS"
    `$HOME/.config/pip/pip.conf`:
    ```ini
    [global]
    index-url = https://pypi.org/simple
    ```

---

## Development install

For contributing to idmtools_calibra or running tests:

### 1. Clone the repository

```bash
git clone https://github.com/InstituteforDiseaseModeling/idmtools_calibra.git
cd idmtools_calibra
```

### 2. Create and activate a virtual environment

```bash
python -m venv v-calibra
# Windows:
v-calibra\Scripts\activate
# Linux/macOS:
source v-calibra/bin/activate
```

### 3. Bootstrap the dev environment

```bash
python .dev_scripts/bootstrap.py
```

This installs all package dependencies and development tools.

Alternatively, install manually with test extras:

```bash
pip install -e ".[test]"
```

### 4. Run the tests

```bash
cd tests
make test-all          # run all tests
make test-unittests    # fast unit tests only
```

### 5. Build documentation locally

```bash
make docs        # build
make docs-serve  # build and serve at http://127.0.0.1:8000
```

