# idmtools_calibra

**idmtools_calibra** is an iterative parameter calibration framework for epidemic and scientific models. It repeatedly samples the parameter space, runs simulations via [idmtools](https://github.com/InstituteforDiseaseModeling/idmtools) on COMPS, Slurm and Container platforms, compares output to reference data, and updates the sampling strategy until convergence.

For a detailed explanation and step-by-step calibration of an EMOD SIR model, see the  [Overview](overview.md)


---

## Quick Start

```python
from idmtools_calibra.calib_manager import CalibManager
from idmtools_calibra.algorithms.optim_tool import OptimTool
from idmtools_calibra.rmse_site import RMSESiteSingleChannel
from idmtools_calibra.plotters.likelihood_plotter import LikelihoodPlotter

site = RMSESiteSingleChannel(
    name='my_site',
    reference_sources={'data': 'reference/output.csv'}
)

calib = CalibManager(
    task=task,                              # ITask (PythonTask, EMODTask, etc.)
    map_sample_to_model_input_fn=my_map_fn, # (simulation, sample_row) -> None
    sites=[site],
    next_point=OptimTool(params=[
        {'Name': 'beta',  'Min': 0.01, 'Max': 1.0, 'Center': 0.3, 'Dynamic': True},
        {'Name': 'gamma', 'Min': 0.01, 'Max': 1.0, 'Center': 0.1, 'Dynamic': True},
    ], samples_per_iteration=25),
    name='my_calibration',
    max_iterations=10,
    plotters=[LikelihoodPlotter()],
)

calib.run_calibration()
```

See the [Quick Start guide](quickstart.md) for a complete end-to-end walkthrough.

---

## How It Works

Each calibration iteration follows six steps:

1. **Sample** — The algorithm proposes a set of parameter combinations
2. **Configure** — Each sample is mapped to a simulation task
3. **Execute** — Simulations run on the idmtools platform (COMPS HPC, Slurm cluster, local docker container)
4. **Analyze** — Model output is compared to reference data; each simulation gets a score
5. **Update** — The algorithm updates its internal state using the scores
6. **Plot** — Diagnostic plots are generated for the iteration

State is persisted to `Calibration.json` after every iteration, enabling [resume from any point](overview.md#resume-support).

---

## Features

- **Multiple sampling algorithms** — `OptimTool` (OLS regression), `IMIS` (Bayesian posterior), `GPC` (Gaussian process), `SPSA`, `PSPO`, `PBNB`
- **Platform-agnostic** — runs on local container, COMPS HPC, Slurm clusters via idmtools
- **Resume from any point** — full iteration state serialized to `Calibration.json`; resume from any iteration and phase
- **Pluggable analyzers** — implement `BaseCalibrationAnalyzer` to score any model output format
- **Diagnostic plotting** — per-iteration likelihood, data overlay, and algorithm-specific plots
- **Post-calibration resampling** — `ResampleManager` with Cramér-Rao and random-perturbation strategies

---

## Package Structure

| Package | Description                                                                                                    |
|---------|----------------------------------------------------------------------------------------------------------------|
| `idmtools_calibra` | Core: `CalibManager`, `CalibSite`, `RMSESiteSingleChannel`, `IterationState`, `ResumeManger` |
| `idmtools_calibra.algorithms` | Sampling algorithms: `OptimTool`, `IMIS`, `GPC`, `SPSA`, `PSPO`, `PBNB`                                        |
| `idmtools_calibra.analyzers` | Output analyzers: `BaseCalibrationAnalyzer`, `RMSEAnalyzer`                                                    |
| `idmtools_calibra.plotters` | Diagnostic plots: likelihood, site data, algorithm-specific                                                    |
| `idmtools_calibra.resamplers` | Post-calibration resampling: Cramér-Rao, random perturbation                                                   |
| `idmtools_calibra.utilities` | Helpers: priors, likelihood calculators, resume manager, parsers, encoders                                     |
| `idmtools_calibra.output` | Spatial output utilities                                                                                       |

---

## Examples

| Example | Location | Description |
|---------|----------|-------------|
| Solar linear model | `examples/solar/` | Simplest: fits `y = ax + b` to solar production data |
| SIR model | `examples/sir/` | Epidemiological SIR model, multiple output options |
| EMOD SIR | `examples/emod_sir/` | Full EMOD disease model calibration on COMPS |
| EMOD SIS | `examples/emod_sis/` | EMOD SIS model variant |

---

## Documentation

- [Installation](installation.md) — install and verify the package
- [Quick Start](quickstart.md) — end-to-end tutorial using the solar example
- [Overview](overview.md) — how the calibration loop works, algorithm details, resume support
- [Troubleshooting](troubleshooting.md) — common mistakes and how to fix them
- [API Reference](api/index.md) — complete reference for all public classes
