# Output

Utilities for handling spatial and structured simulation output.

---

## SpatialOutput

```python
from idmtools_calibra.output.spatial_output import SpatialOutput
```

Helper class for reading and processing spatially-structured output files produced by simulations (e.g. spatial binary files from EMOD).

### Usage

```python
from idmtools_calibra.output.spatial_output import SpatialOutput

spatial = SpatialOutput.from_file('output/SpatialReport_Prevalence.bin')
df = spatial.to_dataframe()   # returns a DataFrame indexed by node and time
```
