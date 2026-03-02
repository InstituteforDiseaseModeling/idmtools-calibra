# Troubleshooting

Common mistakes and how to fix them.

---

## Common Mistakes

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| `TypeError` on `map_sample_to_model_input_fn` | Wrong function signature | Must be `(simulation, sample_row)` — `sample_row` is a `pandas.Series` |
| `reduce()` fails or returns wrong scores | `reduce()` returns wrong shape | Must return a `DataFrame` with a score column, **indexed by simulation ID** |
| Fixed parameters never move | `Dynamic: False` on those params | Set `Dynamic: True` for parameters you want the algorithm to adapt |
| Resume fails with missing file error | `Calibration.json` not found | Ensure `name` matches the existing calibration directory; use `backup=True` for safety |
| Low R² warning every iteration | Nonlinear fitness landscape | Expected; `OptimTool` falls back to best sample. Consider increasing `samples_per_iteration` |
| Scores are all identical | `map_sample_to_model_input_fn` not applying the sample | Verify the callback is actually modifying simulation parameters |
| Calibration hangs at commissioning | Platform connection issue | Check your COMPS credentials or Container platform configuration |
| `KeyError` on sample column | Parameter name mismatch | `Name` in `params` must match exactly what `sample_row[...]` accesses |

---

## `map_sample_to_model_input_fn` Signature

This is the most common source of errors. The function **must** accept exactly two positional arguments:

```python
# CORRECT
def my_map(simulation, sample):
    simulation.task.set_parameter('beta', sample['beta'])

# WRONG — missing simulation argument
def my_map(sample):
    ...

# WRONG — wrong argument order
def my_map(sample, simulation):
    ...
```

The `sample` argument is a `pandas.Series`, so access parameters by name: `sample['beta']`, not `sample[0]`.

---

## `reduce()` Return Shape

The `reduce()` method must return a `pandas.DataFrame` indexed by **simulation ID** with at least one score column:

```python
# CORRECT — indexed by sim_id
def reduce(self, all_data):
    scores = {
        sim_id: -np.sqrt(((d['model'] - d['ref'])**2).mean())
        for sim_id, d in all_data.items()
    }
    return pd.DataFrame({'score': scores})

# WRONG — integer index, not sim_id
def reduce(self, all_data):
    return pd.DataFrame({'score': [1.0, 2.0, 3.0]})
```

Note: **higher scores = better fit**. If you compute an error metric (RMSE, MAE), negate it: `-rmse`.

---

## Resume Fails

If `run_calibration(resume=True)` fails:

1. Confirm `Calibration.json` exists in the calibration directory (`<name>/Calibration.json`)
2. Use `dry_run=True` first to preview what the resume will do without executing:
   ```python
   calib.run_calibration(resume=True, iteration=2, iter_step='analyze', dry_run=True)
   ```
3. Use `backup=True` to protect state before any resume operation:
   ```python
   calib.run_calibration(resume=True, iteration=2, iter_step='analyze', backup=True)
   ```

---

## Low R² Every Iteration

If `OptimTool` logs low R² values every iteration, the fitness landscape is highly nonlinear in the sampled region. This is common in SIR/SIS epidemic models near threshold parameters.

`OptimTool` handles this gracefully — when R² falls below `rsquared_thresh` (default 0.5), it falls back to sampling around the best-scoring point rather than following the regression gradient. You do not need to intervene.

If convergence is slow, try:

- Increasing `samples_per_iteration` to get a better regression fit per iteration
- Narrowing the `Min`/`Max` bounds if you have prior knowledge about the parameter range
- Reducing `mu_r` (step size mean) to take smaller steps

---

## Analyzing Results Without Re-Running

To load a completed calibration for analysis without executing anything:

```python
from idmtools_calibra.calib_manager import CalibManager

cm = CalibManager.open_for_reading('my_calibration')
```

---

## Getting Help

- Check the [examples](https://github.com/InstituteforDiseaseModeling/idmtools-calibra/tree/main/examples) — `examples/solar/` is the simplest end-to-end reference
- File an issue on [GitHub](https://github.com/InstituteforDiseaseModeling/idmtools-calibra/issues)
