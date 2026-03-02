# Output

Utilities for handling spatial and structured simulation output.

---

## SpatialOutput

```python
from idmtools_calibra.output.spatial_output import SpatialOutput
```

Helper class for reading and processing spatially-structured output files produced by simulations (e.g. spatial binary files from EMOD such as `SpatialReport_*.bin`).

### Class Methods

#### `from_file(filename)` *(classmethod)*

Load a spatial binary output file.

```python
spatial = SpatialOutput.from_file('output/SpatialReport_Prevalence.bin')
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `filename` | `str` | Path to the spatial binary output file |

Returns a `SpatialOutput` instance.

### Instance Methods

#### `to_dataframe()`

Convert the spatial output to a `pandas.DataFrame` indexed by node and time.

```python
df = spatial.to_dataframe()
# Returns DataFrame with columns: node_id, time, value
```

### Usage Example

```python
from idmtools_calibra.output.spatial_output import SpatialOutput

# Load EMOD spatial prevalence report
spatial = SpatialOutput.from_file('output/SpatialReport_Prevalence.bin')

# Convert to DataFrame for analysis
df = spatial.to_dataframe()
print(df.head())
# node_id  time  value
#       0     0  0.002
#       0     1  0.004
#       ...

# Use in an analyzer
class SpatialAnalyzer(BaseCalibrationAnalyzer):
    def map(self, data, item):
        spatial = SpatialOutput.from_file(data['output/SpatialReport_Prevalence.bin'])
        return spatial.to_dataframe()
```
