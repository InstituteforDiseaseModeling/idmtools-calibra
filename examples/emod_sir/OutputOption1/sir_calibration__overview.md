# Explain this calibration:
## You have 3 dynamic parameters that control disease dynamics:

* Base_Infectivity_Constant — how easily the disease spreads
* Infectious_Period_Exponential — how long someone is infectious
* Incubation_Period_Constant — how long before symptoms appear

Each simulation run produces an infected curve (number of infected people over time). You also have a reference curve 
(real-world or target data).

## The Connection
### Step 1: Each sample becomes a simulation
In one iteration, OptimTool generates ~100 parameter combinations (samples). Each sample is a specific set of values like:

| Sample | Base_Infectivity | Infectious_Period | Incubation_Period |
|--------|------------------|-------------------|-------------------|
| 0      |     0.3          |    5.0            |     3.0           |
|--------|------------------|-------------------|-------------------|
| 0      |     0.35         |    4.8            |     2.7           |

............

Each of these runs an EMOD-SIR simulation that produces an infected curve.

### Step 2: Each simulation gets a score
The simulated infected curve is compared to your reference data, producing a single fitness score (the Results value).
This is typically something like a negative sum of squared differences — the closer your simulation matches the reference, 
the higher the score.

### Step 3: OLS fits scores to parameters
Now the OLS regression fits:
```bash
score ≈ β₀ + β₁·Base_Infectivity + β₂·Infectious_Period + β₃·Incubation_Period
```
Using your ~100 samples and their scores, it finds the best-fit plane in this 3D parameter space.

### Step 4: Gradient tells you which way to move
Say the fitted coefficients are:

* β₁ = +50 (increasing infectivity improves the fit)
* β₂ = -20 (decreasing infectious period improves the fit)
* β₃ = +5 (increasing incubation period slightly improves the fit)

This tells the optimizer: "To better match the reference data, try higher infectivity, shorter infectious period, 
and slightly longer incubation." It then shifts the center in that direction and samples again.

### Step 5: Repeat
Each iteration the center moves closer to parameter values that produce an infected curve matching your reference. 
The "hill" being climbed is the fitness landscape — a surface where each point represents how well a particular 
parameter combination reproduces your reference data.
Visually
```
Iteration 0:  Samples scattered around initial guess
              → scores vary a lot, OLS fits a plane
             
Iteration 1:  Center moves along gradient
              → samples now around a better region 

Iteration 2:  Center moves again, getting closer
              → simulated curves start matching reference
             
...
              
Iteration N:  Center has converged
              → best parameter values found that reproduce
                your reference infected curve
```
When R² is low
If the relationship between your 3 parameters and the score is highly nonlinear in the sampled region (which is common 
in SIR models — small changes in infectivity can cause dramatic shifts in epidemic dynamics), the linear fit will be 
poor (low R²). In that case, the algorithm just jumps to whichever of the ~100 samples best matched the reference data, 
rather than trusting the gradient. So in essence: OLS is the algorithm's way of efficiently estimating "which direction 
in parameter space will make my simulated epidemic look more like the real data" without needing to run thousands of 
simulations.

### In the equation:
`score ≈ β₀ + β₁·Base_Infectivity + β₂·Infectious_Period + β₃·Incubation_Period`

Known: The 100 parameter values (x) AND their 100 scores (y) — these come from running the simulations
Unknown: β₀, β₁, β₂, β₃ — the coefficients that OLS needs to find

How the 100 samples apply
Each sample gives you one equation:

score_1  = β₀ + β₁·(0.30) + β₂·(5.0) + β₃·(3.0)

score_2  = β₀ + β₁·(0.35) + β₂·(4.8) + β₃·(2.7)

score_3  = β₀ + β₁·(0.28) + β₂·(5.2) + β₃·(3.1)

...

score_100 = β₀ + β₁·(0.32) + β₂·(4.9) + β₃·(2.9)

So you have 100 equations but only 4 unknowns (β₀, β₁, β₂, β₃). This is an overdetermined system — there's no perfect solution that satisfies all 100 equations exactly.
What OLS does
OLS finds the β values that minimize the total squared error across all 100 equations. In matrix form:
`Y = X · β + ε`

where:

Y = [score_1, score_2, ..., score_100]        → 100×1 vector

X = [[1, 0.30, 5.0, 3.0],

     [1, 0.35, 4.8, 2.7],

     ...

     [1, 0.32, 4.9, 2.9]]                     → 100×4 matrix (the "1" is from sm.add_constant)

β = [β₀, β₁, β₂, β₃]                         → 4×1 vector (UNKNOWN, to be solved)

ε = errors                                     → what OLS minimizes (sum of ε²)

The closed-form solution is:

β = (Xᵀ X)⁻¹ Xᵀ Y

That's exactly what mod.fit() computes. After solving, you get concrete β values like β₁ = +50, β₂ = -20, β₃ = +5, 
which tell the optimizer the gradient direction — how to shift the parameters to improve the score in the next iteration.