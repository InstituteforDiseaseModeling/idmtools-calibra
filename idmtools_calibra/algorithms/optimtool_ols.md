# OLS OptimTool — Gradient Ascent via Linear Regression

OptimTool is a gradient-ascent-based optimization algorithm used for **calibration** of simulation models. It is part of the `idmtools_calibra` package (from the Institute for Disease Modeling).

## What It Does (High Level)

OptimTool iteratively searches for the best parameter values that maximize a fitness/likelihood function. Each iteration it:

1. **Samples** parameter combinations around a "center" point
2. **Evaluates** those samples (via simulation)
3. **Fits a linear regression** (OLS) on the results
4. **Moves the center** in the direction of the gradient (steepest improvement)
5. Repeats

## Key Components

### Initialization

Takes a list of parameter definitions (each with `Name`, `Min`, `Max`, `Guess`, and `Dynamic` flag), plus tuning parameters:

- `mu_r` (default 0.1) — step size, as a fraction of the parameter range
- `sigma_r` (default 0.02) — step size variance
- `center_repeats` — how many times to sample the center point
- `samples_per_iteration` — total number of samples per iteration

### `choose_initial_samples`

For iteration 0, it places the center at each parameter's `Guess` value and draws samples on a hypersphere around it.

### `sample_hypersphere`

Generates samples distributed on a **fuzzy shell** (hypersphere with random radius) around the current center:

- Only `Dynamic=True` parameters are varied; static parameters stay fixed
- The radius is drawn from a normal distribution with mean `mu_r` and std `sigma_r`
- Direction is uniformly random on the unit sphere

```python
standard_normal = norm(loc=0, scale=1)
radius_normal = norm(loc=self.mu_r, scale=self.sigma_r)
for i in range(N - self.center_repeats):
    sn_rvs = standard_normal.rvs(size=len(dynamic_state))  # random direction
    sn_nrm = np.linalg.norm(sn_rvs)                        # normalize
    radius = radius_normal.rvs()                            # random distance
    deviations.append([radius / sn_nrm * sn for sn in sn_rvs])
```

With default settings, most samples land about **8–12% of the parameter range** away from the center (0.1 ± 0.02).

### `choose_samples_via_gradient_ascent`

The core logic for iterations ≥ 1:

1. Fits an OLS linear regression of results vs. dynamic parameter values
2. If R² > threshold: moves the center along the normalized gradient direction
3. If R² < threshold: falls back to jumping to the best-performing sample (argmax)
4. Generates new hypersphere samples around the new center

### `clamp`

Ensures all samples stay within `[Min, Max]` bounds.

### `constrain_sample_fn`

A user-provided function for additional constraints (e.g., enforcing relationships between parameters).

### State Management (`get_state` / `set_state`)

Serializes and deserializes the optimizer's state for pause/resume support.

## OLS Linear Regression Explained

### The Model

The relationship between parameter values and simulation results is approximated as a linear function:

**score ≈ β₀ + β₁·x₁ + β₂·x₂ + β₃·x₃**

Where:

- **Known**: The ~100 parameter values (x) AND their ~100 scores (y) — from running simulations
- **Unknown**: β₀, β₁, β₂, β₃ — the coefficients that OLS solves for

### How Samples Apply

Each sample gives one equation:

```
score_1   = β₀ + β₁·(0.30) + β₂·(5.0) + β₃·(3.0)
score_2   = β₀ + β₁·(0.35) + β₂·(4.8) + β₃·(2.7)
score_3   = β₀ + β₁·(0.28) + β₂·(5.2) + β₃·(3.1)
...
score_100 = β₀ + β₁·(0.32) + β₂·(4.9) + β₃·(2.9)
```

100 equations, 4 unknowns — an overdetermined system. OLS finds the β values that **minimize the total squared error**.

### In Matrix Form

```
Y = X · β + ε

Y = [score_1, score_2, ..., score_100]        → 100×1 vector
X = [[1, 0.30, 5.0, 3.0],
     [1, 0.35, 4.8, 2.7],
     ...
     [1, 0.32, 4.9, 2.9]]                     → 100×4 matrix
β = [β₀, β₁, β₂, β₃]                         → 4×1 vector (SOLVED BY OLS)
ε = errors                                     → minimized (sum of ε²)
```

The closed-form solution is: **β = (Xᵀ X)⁻¹ Xᵀ Y**

### Using the Gradient

The fitted coefficients tell the optimizer which direction to move:

- Positive β₁ → increasing that parameter improves the score
- Negative β₂ → decreasing that parameter improves the score

The center is shifted in that direction, scaled by each parameter's range and normalized by `mu_r`.

## R² (R-squared)

R² measures how well the linear model fits the data (0 to 1):

- **R² = 1** — model perfectly explains all variation
- **R² = 0** — model explains nothing

```python
if mod_fit.rsquared > self.rsquared_thresh:
    # Good fit — trust the gradient and step along it
else:
    # Poor fit — jump to the best-performing sample instead
    max_idx = np.argmax(latest_results)
    new_dynamic_center = latest_dynamic_samples[max_idx].tolist()
```

With the default threshold of 0.5, if the linear model explains more than 50% of the variance, the algorithm trusts the gradient. Otherwise, the landscape is too nonlinear or noisy, so it falls back to the simpler heuristic.

## Connecting to an EMOD-SIR Problem

For a 3-parameter SIR calibration (`Base_Infectivity_Constant`, `Infectious_Period_Exponential`, `Incubation_Period_Constant`):

1. **Each sample becomes a simulation** — OptimTool generates ~100 parameter combinations, each run through EMOD-SIR to produce an infected curve
2. **Each simulation gets a score** — the simulated infected curve is compared to reference data, producing a single fitness score
3. **OLS fits scores to parameters** — finds the linear relationship between parameters and scores
4. **Gradient tells you which way to move** — the coefficients indicate how to adjust each parameter to better match the reference data
5. **Repeat** — each iteration the center moves closer to parameter values that reproduce the reference infected curve

### Visually

```
Iteration 0:  Samples scattered around initial guess
              → scores vary, OLS fits a plane

Iteration 1:  Center moves along gradient
              → samples now around a better region

Iteration 2:  Center moves again, getting closer
              → simulated curves start matching reference

   ...

Iteration N:  Center has converged
              → best parameter values found
```

### Analogy

Imagine you're on a foggy hillside trying to reach the peak. You can't see far, so you probe a few nearby points, fit a tilted plane to what you find, and walk uphill along that plane's steepest direction. That's essentially what each iteration does — the linear regression is how the algorithm "feels out" the local slope.
