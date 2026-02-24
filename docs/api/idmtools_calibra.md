# Core Package

The top-level `idmtools_calibra` package contains the central orchestration classes for running calibrations.

---

## CalibManager

```python
from idmtools_calibra.calib_manager import CalibManager
```

The top-level entry point. Manages the multi-iteration calibration loop: sampling parameters, commissioning simulations, analyzing results, and updating the algorithm state.

### Constructor

```python
CalibManager(
    task,
    map_sample_to_model_input_fn,
    sites,
    next_point,
    platform=None,
    name='calib_test',
    sim_runs_per_param_set=1,
    max_iterations=5,
    plotters=None,
    map_replicates_callback=None,
    directory='.'
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `task` | `ITask` | — | An idmtools task (e.g. `PythonTask`, `EMODTask`) |
| `map_sample_to_model_input_fn` | `callable` | — | Callback `(simulation, sample_row) -> dict` that applies one parameter sample to the task |
| `sites` | `List[CalibSite]` | — | One or more calibration sites providing reference data and analyzers |
| `next_point` | `NextPointAlgorithm` | — | Sampling algorithm instance (e.g. `OptimTool`, `IMIS`) |
| `platform` | `IPlatform` | `None` | idmtools platform; defaults to the current platform context |
| `name` | `str` | `'calib_test'` | Calibration name; also used as the output directory name |
| `sim_runs_per_param_set` | `int` | `1` | Number of replicate simulations per parameter sample |
| `max_iterations` | `int` | `5` | Maximum number of calibration iterations |
| `plotters` | `List[BasePlotter]` | `None` | Diagnostic plotters run after each iteration |
| `map_replicates_callback` | `callable` | `None` | Callback for sweeping the replicate seed (defaults to `Run_Number`) |
| `directory` | `str` | `'.'` | Root directory under which the calibration folder is created |

### Key Methods

#### `run_calibration(**kwargs)`

Start or resume a calibration. All parameters are passed as keyword arguments.

| Keyword | Type | Default | Description |
|---------|------|---------|-------------|
| `resume` | `bool` | `False` | Resume an existing calibration |
| `iteration` | `int` | `None` | Iteration number to resume from |
| `iter_step` | `str` | `None` | Phase to resume from: `'commission'`, `'analyze'`, `'plot'`, `'next_point'` |
| `loop` | `bool` | `True` | Continue to subsequent iterations after resuming |
| `max_iterations` | `int` | `None` | Override the max iterations set in the constructor |
| `backup` | `bool` | `False` | Back up `Calibration.json` before resuming |
| `dry_run` | `bool` | `False` | Preview resume action without executing |
| `directory` | `str` | `None` | Override the calibration directory |

#### `open_for_reading(calibration_directory)` *(classmethod)*

Open an existing calibration directory for reading results without executing anything.

```python
cm = CalibManager.open_for_reading('my_calibration')
```

### Example

```python
from idmtools_calibra.calib_manager import CalibManager
from idmtools_calibra.algorithms.optim_tool import OptimTool
from idmtools.entities.command_task import CommandTask

task = CommandTask(command='python model.py')

calib = CalibManager(
    task=task,
    map_sample_to_model_input_fn=my_map_fn,
    sites=[my_site],
    next_point=OptimTool(params=[...]),
    name='my_calibration',
    max_iterations=10,
)

calib.run_calibration()

# Resume from iteration 3, analyze phase:
calib.run_calibration(resume=True, iteration=3, iter_step='analyze')
```

---

## CalibSite

```python
from idmtools_calibra.calib_site import CalibSite
```

Abstract base class for calibration sites. A site pairs reference (observed) data with the analyzers that compare model output against it.

### Constructor

```python
CalibSite(name)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Unique name for this calibration site |

### Abstract Methods to Implement

| Method | Returns | Description |
|--------|---------|-------------|
| `get_analyzers()` | `List[IAnalyzer]` | Return analyzer instances for this site |
| `get_setup_functions()` | `List[callable]` | Return functions that configure the task for this site |
| `get_reference_data(reference_type=None)` | `DataFrame` | Return the reference/observed data |

### Example

```python
from idmtools_calibra.calib_site import CalibSite
from my_analyzers import MyAnalyzer

class MySite(CalibSite):
    def __init__(self):
        super().__init__(name='my_site')

    def get_analyzers(self):
        return [MyAnalyzer(site=self)]

    def get_setup_functions(self):
        return []

    def get_reference_data(self, reference_type=None):
        return pd.read_csv('reference/data.csv')
```

---

## RMSESiteSingleChannel

```python
from idmtools_calibra.rmse_site import RMSESiteSingleChannel
```

A ready-to-use `CalibSite` subclass for RMSE-based calibration of a single output channel. Reads reference data from a CSV and wires up an `RMSEAnalyzer` automatically.

### Constructor

```python
RMSESiteSingleChannel(
    name,
    reference_sources={'just_one': 'reference/output.csv'}
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `str` | — | Site name |
| `reference_sources` | `dict` | `{'just_one': 'reference/output.csv'}` | Dict mapping a key to the path of the reference CSV file. The CSV must have an independent column (first) and a dependent column (second). |

### Example

```python
from idmtools_calibra.rmse_site import RMSESiteSingleChannel

site = RMSESiteSingleChannel(
    name='solar_site',
    reference_sources={'data': 'reference/output.csv'}
)
```

---

## IterationState

```python
from idmtools_calibra.iteration_state import IterationState
```

Holds all state for a single calibration iteration: parameter samples, simulation IDs, analyzer results, and timestamps. Serialized to and deserialized from `Calibration.json` to support resuming.

### Key Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `iteration` | `int` | Current iteration number |
| `calibration_name` | `str` | Name of the calibration |
| `calibration_directory` | `str` | Path to the calibration output directory |
| `samples_for_this_iteration` | `dict` | Parameter samples drawn for this iteration |
| `experiment_id` | `str` | ID of the commissioned experiment |
| `results` | `dict` | Per-site analyzer results |
| `all_results` | `DataFrame` | Combined results across all sites |
| `summary_table` | `DataFrame` | Summary statistics |

---

## ResampleManager

```python
from idmtools_calibra.resample_manager import ResampleManager
```

Orchestrates post-calibration resampling across one or more `BaseResampler` steps.

### Constructor

```python
ResampleManager(steps, calibration_manager, restart_at_step=None)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `steps` | `List[BaseResampler]` | — | Ordered list of resampling steps |
| `calibration_manager` | `CalibManager` | — | The completed calibration to resample from |
| `restart_at_step` | `int` | `None` | Resume resampling from a specific step index |

### Key Method

#### `resample_and_run()`

Execute all resampling steps in sequence, persisting restart state between steps.

---

## Utility Functions

### `set_parameter_sweep_callback`

```python
from idmtools_calibra.calib_manager import set_parameter_sweep_callback
```

Convenience callback compatible with `CalibManager.map_replicates_callback`. Sets a named parameter on the simulation task, supporting both `task.config.parameters` (EMOD-style) and `task.parameters` (JSON-configured tasks).

```python
set_parameter_sweep_callback(simulation, param='Run_Number', value=42)
```
