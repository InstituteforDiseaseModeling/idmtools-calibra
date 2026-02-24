<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

- [idmtools_calibra](#idmtools_calibra)
  - [Features](#features)
  - [Package Structure](#package-structure)
  - [Examples](#examples)
  - [Contents](#contents)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# idmtools_calibra

**idmtools_calibra** (v3.0.0) is an iterative parameter calibration framework for epidemic and scientific models. It repeatedly samples the parameter space, runs simulations/experiments via idmtools on [comps](https://comps.idmod.org/), compares output to reference data, and updates the sampling strategy until convergence.

For a detailed explanation and step-by-step calibration of an EMOD SIR model, see the  [Overview](overview.md)

---

## Features

- **Multiple sampling algorithms** — `OptimTool` (OLS model), `IMIS` (Bayesian posterior), `GPC` (Gaussian process), `SPSA`, `PSPO`, `PBNB`
- **Platform-agnostic** — runs simulations on local machines or COMPS HPC clusters via idmtools
- **Resume from any point** — full iteration state is serialized to `Calibration.json`; resume from any iteration and phase
- **Pluggable analyzers** — implement `BaseCalibrationAnalyzer` to score any model output format
- **Diagnostic plotting** — per-iteration likelihood, data overlay, and algorithm-specific plots
- **Post-calibration resampling** — `ResampleManager` with Cramér-Rao and random-perturbation strategies

---

## Package Structure

| Package | Description |
|---------|-------------|
| `idmtools_calibra` | Core: `CalibManager`, `CalibSite`, `RMSESiteSingleChannel`, `IterationState`, `ResampleManager` |
| `idmtools_calibra.algorithms` | Sampling algorithms: `OptimTool`, `IMIS`, `GPC`, `SPSA`, `PSPO`, `PBNB` |
| `idmtools_calibra.analyzers` | Output analyzers: `BaseCalibrationAnalyzer`, `RMSEAnalyzer` |
| `idmtools_calibra.plotters` | Diagnostic plots: likelihood, site data, algorithm-specific |
| `idmtools_calibra.resamplers` | Post-calibration resampling: Cramér-Rao, random perturbation |
| `idmtools_calibra.utilities` | Helpers: priors, likelihood calculators, parsers, encoders |
| `idmtools_calibra.output` | Spatial output utilities |

---

## Examples

| Example | Location | Description |
|---------|----------|-------------|
| Solar linear model | `examples/solar/` | Simplest: fits `y = ax + b` to solar production data |
| SIR model | `examples/sir/` | Epidemiological SIR model, multiple output options |
| EMOD SIR | `examples/emod_sir/` | Full EMOD disease model calibration on COMPS |
| EMOD SIS | `examples/emod_sis/` | EMOD SIS model variant |

---

## Contents

- [Installation](installation.md)
- [Overview](overview.md)
- [API Reference](api/index.md)
