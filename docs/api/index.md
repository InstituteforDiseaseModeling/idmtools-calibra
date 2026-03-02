# API Reference

Complete reference for all public classes and functions in **idmtools_calibra**.

## Package Map

| Module | Description |
|--------|-------------|
| [Core](idmtools_calibra.md) | `CalibManager`, `CalibSite`, `RMSESiteSingleChannel`, `IterationState`, `ResampleManager` |
| [Algorithms](algorithms.md) | Sampling algorithms: `OptimTool`, `IMIS`, `GPC`, `SPSA`, `PSPO`, `PBNB` |
| [Analyzers](analyzers.md) | Simulation output analyzers: `BaseCalibrationAnalyzer`, `RMSEAnalyzer` |
| [Plotters](plotters.md) | Diagnostic visualization: `BasePlotter` and algorithm-specific subclasses |
| [Output](output.md) | Spatial output utilities |

## Typical Import Pattern

```python
from idmtools_calibra.calib_manager import CalibManager
from idmtools_calibra.calib_site import CalibSite
from idmtools_calibra.rmse_site import RMSESiteSingleChannel
from idmtools_calibra.algorithms.optim_tool import OptimTool
from idmtools_calibra.analyzers.rmse_analyzer import RMSEAnalyzer
from idmtools_calibra.plotters.likelihood_plotter import LikelihoodPlotter
```

## Calibration Flow

```
CalibManager.run_calibration()
  ├── NextPointAlgorithm.get_samples_for_iteration()   # sample parameter space
  ├── map_sample_to_model_input_fn()                   # configure simulation task
  ├── ExperimentManager (idmtools)                     # run simulations on platform
  ├── BaseCalibrationAnalyzer                          # score each simulation
  ├── NextPointAlgorithm.set_results_for_iteration()   # algorithm updates state
  └── BasePlotter.visualize()                          # diagnostic plots
```

Each iteration's state is saved to `Calibration.json` for [resume support](../overview.md#resume-support).
