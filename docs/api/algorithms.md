<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

- [Algorithms](#algorithms)
  - [Comparison](#comparison)
  - [NextPointAlgorithm *(abstract base)*](#nextpointalgorithm-abstract-base)
    - [Methods to Implement](#methods-to-implement)
    - [Inherited Utility Methods](#inherited-utility-methods)
  - [OptimTool](#optimtool)
    - [Constructor](#constructor)
    - [Parameter Dictionary Format](#parameter-dictionary-format)
    - [Example](#example)
  - [IMIS](#imis)
    - [Constructor](#constructor-1)
    - [Example](#example-1)
  - [GPC](#gpc)
    - [Constructor](#constructor-2)
  - [SPSA](#spsa)
    - [Constructor](#constructor-3)
  - [PSPO](#pspo)
    - [Constructor](#constructor-4)
  - [PBNB](#pbnb)
    - [Constructor](#constructor-5)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Algorithms

Sampling algorithms that propose and refine parameter sets across calibration iterations.

## Comparison

| Algorithm | Class | Strategy | Best For |
|-----------|-------|----------|----------|
| [OptimTool](#optimtool) | `OptimTool` | Adaptive regression-based | General-purpose; most commonly used |
| [IMIS](#imis) | `IMIS` | Bayesian importance sampling | Posterior distribution estimation |
| [GPC](#gpc) | `GPC` | Gaussian process surrogate | Smooth, low-dimensional parameter spaces |
| [SPSA](#spsa) | `SPSA` | Stochastic gradient approximation | Noisy objectives |
| [PSPO](#pspo) | `PSPO` | Particle swarm / perturbation | Population-based optimization |
| [PBNB](#pbnb) | `OptimToolPBNB` | Progressive branch-and-bound | High-dimensional bounded spaces |

---

## NextPointAlgorithm *(abstract base)*

```python
from idmtools_calibra.algorithms.next_point_algorithm import NextPointAlgorithm
```

Abstract base class for all sampling algorithms. Subclass this to implement a custom algorithm.

### Methods to Implement

| Method | Signature | Description |
|--------|-----------|-------------|
| `get_samples_for_iteration` | `(iteration) -> DataFrame` | Return a DataFrame of parameter samples for the given iteration |
| `set_results_for_iteration` | `(iteration, results)` | Receive analyzer results and update algorithm state |
| `end_condition` | `() -> bool` | Return `True` to stop the calibration loop |
| `get_final_samples` | `() -> DataFrame` | Return the best samples after calibration completes |
| `get_param_names` | `() -> List[str]` | Return the list of parameter names |
| `get_state` | `() -> dict` | Serialize algorithm state for persistence |
| `set_state` | `(state, iteration)` | Restore algorithm state from a persisted dict |
| `cleanup` | `()` | Release any resources held by the algorithm |

### Inherited Utility Methods

| Method | Description |
|--------|-------------|
| `update_iteration(iteration)` | Set the current iteration counter |
| `prep_for_dict(df)` | Convert a DataFrame to a JSON-serializable dict (nulls → `None`) |
| `sample_from_function(function, N)` | Draw `N` samples from a callable prior function |

---

## OptimTool

```python
from idmtools_calibra.algorithms.optim_tool import OptimTool
```

The default and most commonly used algorithm. Each iteration fits a regression model to the likelihood surface and adaptively narrows the sampling region around the best-scoring area.

### Constructor

```python
OptimTool(
    params,
    constrain_sample_fn=lambda s: s,
    mu_r=0.1,
    sigma_r=0.02,
    center_repeats=2,
    samples_per_iteration=100,
    rsquared_thresh=0.5
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `params` | `List[dict]` | — | Parameter definitions (see format below) |
| `constrain_sample_fn` | `callable` | identity | Optional function to enforce constraints between parameters |
| `mu_r` | `float` | `0.1` | Mean fractional step size for exploration |
| `sigma_r` | `float` | `0.02` | Std dev of step size |
| `center_repeats` | `int` | `2` | Number of replicates at the current best center point |
| `samples_per_iteration` | `int` | `100` | Total samples drawn per iteration (must be > `center_repeats`) |
| `rsquared_thresh` | `float` | `0.5` | R² threshold; if regression fit is below this, the search radius is not contracted |

### Parameter Dictionary Format

Each entry in `params` must be a dict with these keys:

| Key | Type | Description |
|-----|------|-------------|
| `Name` | `str` | Parameter name (must match what `map_sample_to_model_input_fn` expects) |
| `Min` | `float` | Minimum allowed value |
| `Max` | `float` | Maximum allowed value |
| `Center` | `float` | Starting center point |
| `Dynamic` | `bool` | If `True`, the algorithm adapts the search region; if `False`, the parameter is held fixed |

### Example

```python
from idmtools_calibra.algorithms.optim_tool import OptimTool

params = [
    {'Name': 'beta',  'Min': 0.01, 'Max': 1.0, 'Center': 0.3, 'Dynamic': True},
    {'Name': 'gamma', 'Min': 0.01, 'Max': 1.0, 'Center': 0.1, 'Dynamic': True},
]

algo = OptimTool(
    params=params,
    samples_per_iteration=50,
    mu_r=0.15,
)
```

---

## IMIS

```python
from idmtools_calibra.algorithms.imis import IMIS
```

Incremental Mixture Importance Sampling — a Bayesian algorithm that builds an iteratively refined mixture distribution over the posterior. Ported from the [R IMIS package](http://cran.r-project.org/web/packages/IMIS) by Raftery & Bao (2009).

At each iteration IMIS centers a new multivariate-normal component on the highest-weight sample, progressively filling in underrepresented regions of the posterior.

### Constructor

```python
IMIS(
    prior_fn,
    initial_samples=10000,
    samples_per_iteration=1000,
    n_resamples=3000,
    current_state=None
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `prior_fn` | `callable` | — | Function that draws `N` samples from the prior distribution; signature: `(N) -> DataFrame` |
| `initial_samples` | `int` | `10000` | Samples drawn from the prior in iteration 0 |
| `samples_per_iteration` | `int` | `1000` | New samples added per subsequent iteration |
| `n_resamples` | `int` | `3000` | Posterior resamples drawn for `get_final_samples()` |
| `current_state` | `dict` | `None` | Restore from a previously serialized state |

### Example

```python
from idmtools_calibra.algorithms.imis import IMIS
import numpy as np

def prior(N):
    return pd.DataFrame({
        'beta':  np.random.uniform(0, 1, N),
        'gamma': np.random.uniform(0, 1, N),
    })

algo = IMIS(prior_fn=prior, initial_samples=5000, samples_per_iteration=500)
```

---

## GPC

```python
from idmtools_calibra.algorithms.gpc import GPC
```

Gaussian Process Calibration. Uses a Gaussian process surrogate model trained on previous iteration results to guide sampling toward high-likelihood regions.

### Constructor

```python
GPC(params, samples_per_iteration=100)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `params` | `List[dict]` | — | Parameter definitions (same format as `OptimTool`) |
| `samples_per_iteration` | `int` | `100` | Samples per iteration |

---

## SPSA

```python
from idmtools_calibra.algorithms.optim_tools_spsa import SPSA
```

Simultaneous Perturbation Stochastic Approximation. A gradient-free stochastic optimizer suited for noisy objective functions. Uses random simultaneous perturbations to estimate the gradient direction.

### Constructor

```python
SPSA(params, samples_per_iteration=100)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `params` | `List[dict]` | — | Parameter definitions (same format as `OptimTool`) |
| `samples_per_iteration` | `int` | `100` | Samples per iteration |

---

## PSPO

```python
from idmtools_calibra.algorithms.optim_tools_pspo import PSPO
```

A particle swarm / perturbation variant of OptimTool. Maintains a population of candidate solutions and uses perturbation-based updates.

### Constructor

```python
PSPO(params, samples_per_iteration=100)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `params` | `List[dict]` | — | Parameter definitions (same format as `OptimTool`) |
| `samples_per_iteration` | `int` | `100` | Samples per iteration |

---

## PBNB

```python
from idmtools_calibra.algorithms.pbnb.optim_tool_pbnb import OptimToolPBNB
```

Progressive Branch and Bound. Partitions the parameter space into sub-regions and progressively refines promising regions using a branch-and-bound strategy. Best suited for high-dimensional bounded parameter spaces.

### Constructor

```python
OptimToolPBNB(params, samples_per_iteration=100)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `params` | `List[dict]` | — | Parameter definitions (same format as `OptimTool`) |
| `samples_per_iteration` | `int` | `100` | Samples per iteration |
