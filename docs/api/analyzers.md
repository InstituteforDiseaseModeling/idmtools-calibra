# Analyzers

Analyzers compare simulation output against reference data and return a scalar score (likelihood or error) per simulation. They extend idmtools' `IAnalyzer` interface.

---

## BaseCalibrationAnalyzer

```python
from idmtools_calibra.analyzers.base_calibration_analyzer import BaseCalibrationAnalyzer
```

Abstract base class for all calibration analyzers. Extends idmtools `IAnalyzer` with calibration-specific fields.

### Constructor

```python
BaseCalibrationAnalyzer(
    uid=None,
    working_dir=None,
    parse=True,
    need_dir_map=False,
    filenames=None,
    reference_data=None,
    weight=1
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `uid` | `str` | `None` | Unique identifier for this analyzer instance |
| `working_dir` | `str` | `None` | Working directory for output files |
| `parse` | `bool` | `True` | Whether to parse simulation output files |
| `need_dir_map` | `bool` | `False` | Whether to use a directory map |
| `filenames` | `List[str]` | `None` | Output filenames to retrieve from each simulation |
| `reference_data` | any | `None` | Reference/observed data to compare against |
| `weight` | `float` | `1` | Relative weight of this analyzer when combining scores across multiple analyzers |

### Methods to Implement

Subclasses must implement the standard `IAnalyzer` interface:

| Method | Signature | Description |
|--------|-----------|-------------|
| `map` | `(data, item) -> any` | Extract and align data for a single simulation |
| `reduce` | `(all_data) -> DataFrame` | Aggregate map results across all simulations into a score per sample |

### Inherited Method

#### `cache()`

Serialize the analyzer to a JSON string (using `GeneralEncoder`). Called by the calibration framework to persist analyzer state.

### Example

```python
from idmtools_calibra.analyzers.base_calibration_analyzer import BaseCalibrationAnalyzer
import pandas as pd
import numpy as np

class MyAnalyzer(BaseCalibrationAnalyzer):
    def __init__(self, site, weight=1):
        self.reference = site.get_reference_data()
        super().__init__(filenames=['output/results.csv'], weight=weight)

    def map(self, data, item):
        sim_df = data['output/results.csv']
        return sim_df.merge(self.reference, on='time')

    def reduce(self, all_data):
        scores = {}
        for sim_id, merged in all_data.items():
            rmse = np.sqrt(((merged['model'] - merged['reference']) ** 2).mean())
            scores[sim_id] = -rmse   # negative because higher = better
        return pd.DataFrame({'score': scores})
```

---

## RMSEAnalyzer

```python
from idmtools_calibra.analyzers.rmse_analyzer import RMSEAnalyzer
```

A ready-to-use analyzer that computes Root Mean Squared Error (RMSE) between a simulation output CSV and reference data. Automatically wired up by `RMSESiteSingleChannel`.

### Constructor

```python
RMSEAnalyzer(
    site,
    dependent_column,
    independent_column,
    output_filename='output.csv'
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `site` | `CalibSite` | — | The calibration site providing reference data (via `site.get_reference_data()`) |
| `dependent_column` | `str` | — | Name of the column to compare (the quantity being calibrated) |
| `independent_column` | `str` | — | Name of the column used to align reference and model data (e.g. `'time'`) |
| `output_filename` | `str` | `'output.csv'` | Model output filename inside the `output/` directory |

### Custom Cost Function

By default RMSE uses scikit-learn's `root_mean_squared_error`. Override the cost function for the entire class:

```python
RMSEAnalyzer.set_custom_cost_fn(my_cost_fn)
# my_cost_fn(series_model, series_reference, series_weights) -> float
```

### Example

```python
from idmtools_calibra.analyzers.rmse_analyzer import RMSEAnalyzer
from idmtools_calibra.rmse_site import RMSESiteSingleChannel

site = RMSESiteSingleChannel(
    name='my_site',
    reference_sources={'data': 'reference/output.csv'}
)

# RMSEAnalyzer is created automatically by RMSESiteSingleChannel.
# To use it directly:
analyzer = RMSEAnalyzer(
    site=site,
    dependent_column='prevalence',
    independent_column='year',
    output_filename='output.csv',
)
```
