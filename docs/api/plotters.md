<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

- [Plotters](#plotters)
  - [Available Plotters](#available-plotters)
  - [BasePlotter](#baseplotter)
    - [Constructor](#constructor)
    - [Abstract Method](#abstract-method)
      - [`visualize(iteration_state)`](#visualizeiteration_state)
    - [Helper Methods](#helper-methods)
      - [`combine_by_site(site_name, analyzer_names, results)` *(staticmethod)*](#combine_by_sitesite_name-analyzer_names-results-staticmethod)
    - [Custom Plotter Example](#custom-plotter-example)
  - [LikelihoodPlotter](#likelihoodplotter)
  - [SiteDataPlotter](#sitedataplotter)
  - [OptimToolPlotter](#optimtoolplotter)
  - [OptimToolPBNBPlotter](#optimtoolpbnbplotter)
  - [OptimToolSPSAPlotter](#optimtoolspsaplotter)
  - [SeparatrixBHMPlotter](#separatrixbhmplotter)
  - [Using Multiple Plotters](#using-multiple-plotters)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Plotters

Plotters generate diagnostic visualizations after each calibration iteration. They are passed to `CalibManager` and called automatically.

## Available Plotters

| Class | Module | Description |
|-------|--------|-------------|
| [BasePlotter](#baseplotter) | `plotters.base_plotter` | Abstract base — subclass to create custom plots |
| [LikelihoodPlotter](#likelihoodplotter) | `plotters.likelihood_plotter` | Likelihood scores across iterations |
| [SiteDataPlotter](#sitedataplotter) | `plotters.site_data_plotter` | Model vs. reference data overlays per site |
| [OptimToolPlotter](#optimtoolplotter) | `plotters.optim_tool_plotter` | Parameter space and regression diagnostics for `OptimTool` |
| [OptimToolPBNBPlotter](#optimtoolpbnbplotter) | `plotters.optim_tool_pbnb_plotter` | Branch-and-bound region diagnostics |
| [OptimToolSPSAPlotter](#optimtoolspsaplotter) | `plotters.optim_tool_spsa_plotter` | SPSA step-size and gradient diagnostics |
| [SeparatrixBHMPlotter](#separatrixbhmplotter) | `plotters.separatrix_bhm_plotter` | Separatrix boundary plots |

---

## BasePlotter

```python
from idmtools_calibra.plotters.base_plotter import BasePlotter
```

Abstract base class. Subclass this to write a custom plotter.

### Constructor

```python
BasePlotter(combine_sites=True)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `combine_sites` | `bool` | `True` | Whether to aggregate results across all sites into a single plot |

### Abstract Method

#### `visualize(iteration_state)`

Called by `CalibManager` at the end of each iteration.

| Parameter | Type | Description |
|-----------|------|-------------|
| `iteration_state` | `IterationState` | Full state of the current iteration, including samples, results, and paths |

### Helper Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `get_iteration_directory()` | `str` | Path to the current iteration's output folder |
| `get_plot_directory()` | `str` | Path to the shared `_plots/` folder (created if absent) |
| `all_results` *(property)* | `DataFrame` | All results from `iteration_state.all_results` |

#### `combine_by_site(site_name, analyzer_names, results)` *(staticmethod)*

Sum analyzer scores for a given site into a `<site>_total` column in `results`.

```python
BasePlotter.combine_by_site('my_site', ['analyzer1', 'analyzer2'], results_df)
```

### Custom Plotter Example

```python
from idmtools_calibra.plotters.base_plotter import BasePlotter
import matplotlib.pyplot as plt

class MyPlotter(BasePlotter):
    def visualize(self, iteration_state):
        results = iteration_state.all_results
        fig, ax = plt.subplots()
        ax.plot(results['__sample_index__'], results['total'], 'o')
        ax.set_xlabel('Sample index')
        ax.set_ylabel('Total likelihood')
        fig.savefig(f'{self.get_plot_directory()}/scores_iter{iteration_state.iteration}.png')
        plt.close(fig)
```

---

## LikelihoodPlotter

```python
from idmtools_calibra.plotters.likelihood_plotter import LikelihoodPlotter
```

Plots the distribution of likelihood scores across samples for each iteration, showing how the algorithm converges.

```python
LikelihoodPlotter(combine_sites=True)
```

---

## SiteDataPlotter

```python
from idmtools_calibra.plotters.site_data_plotter import SiteDataPlotter
```

Overlays the best-fit model output against the reference data for each calibration site.

```python
SiteDataPlotter(combine_sites=True)
```

---

## OptimToolPlotter

```python
from idmtools_calibra.plotters.optim_tool_plotter import OptimToolPlotter
```

Generates diagnostics specific to `OptimTool`: parameter scatter plots, regression R² values, and the evolution of the search center and radius over iterations.

```python
OptimToolPlotter(combine_sites=True)
```

---

## OptimToolPBNBPlotter

```python
from idmtools_calibra.plotters.optim_tool_pbnb_plotter import OptimToolPBNBPlotter
```

Visualizes the branch-and-bound region partition for `OptimToolPBNB` calibrations.

```python
OptimToolPBNBPlotter(combine_sites=True)
```

---

## OptimToolSPSAPlotter

```python
from idmtools_calibra.plotters.optim_tool_spsa_plotter import OptimToolSPSAPlotter
```

Plots SPSA-specific diagnostics including step size decay and estimated gradient direction.

```python
OptimToolSPSAPlotter(combine_sites=True)
```

---

## SeparatrixBHMPlotter

```python
from idmtools_calibra.plotters.separatrix_bhm_plotter import SeparatrixBHMPlotter
```

Visualizes the separatrix (decision boundary) estimated by the BHM algorithm.

```python
SeparatrixBHMPlotter(combine_sites=True)
```

---

## Using Multiple Plotters

Pass a list of plotters to `CalibManager`:

```python
from idmtools_calibra.plotters.likelihood_plotter import LikelihoodPlotter
from idmtools_calibra.plotters.site_data_plotter import SiteDataPlotter
from idmtools_calibra.plotters.optim_tool_plotter import OptimToolPlotter

calib = CalibManager(
    ...,
    plotters=[
        LikelihoodPlotter(),
        SiteDataPlotter(),
        OptimToolPlotter(),
    ],
)
```
