# CMS examples

In this folder you will find some example illustrating the use of dtk-tools with the CMS model.

### simple_model.py

This example shows how to run a simple CMS simulation.
It uses previously created model and configuration files.
It also demonstrates the use of the `CMSAnalyzer` which allows to quickly visualize CMS outputs.

### simple_model_default.py

This example creates a CMS simulation from scratch using the EMODL language helpers.
It demonstrates how to create the model and configuration directly from Python and then proceed to run and chart the results.

### age_groups_demo.py

This file shows how to create age groups using the CMSGroup and CMSGroupManager allowing to easily duplicate species and reaction
across user-defined groups. It only display the generated model and does not run it.

### CMSCalibration folder

This folder contains a fully-functioning calibration of the CMS model.
The calibration uses:
- CMSSite.py: defining the calibration "site" and containing the reference data
- CMSAnalyzer.py: defining the analyzer allowing to compare the model outputs to the reference data
- calibration_script.py: the calibration script putting it all together

#### Reference data

The reference data is contained in the CMSSite and define what is the calibration target.
Here, the reference data is a simple dictionary:
``` python
    def get_reference_data(self, reference_type=None):
        return {
            "ratio_SI_10": 1,
            "ratio_SI_100": 5
        }
```
It defines that at timestep 10, the ratio between S and I should be 1 and at timestep 100, this ration should be 5.
This is arbitrary data and one should feel free to structure and name the data as desired. 

#### Calibration script

In the calibration script, we can find some important part of the calibration:

**The parameters to calibrate**
This is represented by the following list:
```python
params = [
    {
        'Name': 'initial_S_A04',
        'Dynamic': True,
        'Guess': 4879554,
        'Min': 4800000,
        'Max': 4900000
    },
    {
        'Name': 'initial_I_A04',
        'Dynamic': True,
        'Guess': 7608,
        'Min': 2000,
        'Max': 10000
    }
]
```

Here we see that the calibration will be varying the `Initial_S_A04` (which represents the initial number of susceptible for age group 0 to 4) from 4.8M to 4.9M.
The calibration will also be able to vary the `Initial_I_A04` from 2000 to 10000.

Once again, the naming is left at the user discretion.

**The function allowing to set parameters in the model**
The next point algorithm will vary the parameters defined earlier in the `params` list. The user needs to provide a function that will take those values
and make the actual change in the model configuration. It is done with the following:

```python
def map_sample_to_model_input(cb, sample):
    tags = {}
    # Make a copy of samples so we can alter it safely
    sample = copy.deepcopy(sample)

    # Go through the parameters
    for p in params:
        value = sample.pop(p['Name'])
        # Replace the (species S 100) with the correct number coming from our sample
        if p["Name"] == "initial_S_A04":
            cb.set_species("S-A04", int(value))

        # Replaces the (species I 100) with the correct number coming from our sample
        elif p["Name"] == "initial_I_A04":
            cb.set_species("I-A04", int(value))

        # Add this change to our tags
        tags[p["Name"]] = value

    return tags
```

As we see here, the `Initial_S_A04` parameter will actually change the value of the `S-A04` species. 
This function is expected to return tags allowing to identify the generated simulation. 


#### Analyzer script

The analyzer job is to compare the model outputs to the reference data and return a likelihood.
All the likelihoods will then be used by the next point algorithm to define what is the best set of new parameters to try.

In our particular example, we are calculating the S/I ratio at different timesteps for each of the simulations:
```python
    def select_simulation_data(self, sim_data, simulation):
        # Transform the data into a normal data frame
        data = pd.read_csv(io.BytesIO(sim_data[self.filenames[0]]), skiprows=1, header=None).transpose()
        data.columns = data.iloc[0]
        data = data.reindex(data.index.drop(0))

        # Calculate the ratios needed for comparison with the reference data
        ratio_SI_10 = 0 if data["smear-positive{0}"][10] == 0 else data["susceptible{0}"][10]/data["smear-positive{0}"][10]
        ratio_SI_100 = 0 if data["smear-positive{0}"][100] == 0 else data["susceptible{0}"][100]/data["smear-positive{0}"][100]

        # Returns the data needed for this simulation
        return {
            "sample_index": simulation.tags.get('__sample_index__'),
            "ratio_SI_10": ratio_SI_10,
            "ratio_SI_100": ratio_SI_100
        }
```

Then comparing those ratios to the reference data and returning the likelihoods.
In out example we are doing a simple `euclidean_distance`.
Please note that the likelihoods need to be indexed per sample_index and returned in this exact format (pandas series with index being the sample index and value being the likelihood for this sample).

```python
    def finalize(self, all_data):
        lls = []
        # Sort our data by sample_index
        # We need to preserve the order by sample_index
        # Calculate the Log Likelihood by comparing the simulated data with the reference data and computing the
        # euclidean distance
        for d in sorted(all_data.values(), key=lambda k: k['sample_index']):
            lls.append(euclidean_distance(list(self.reference_data.values()), [d[k] for k in self.reference_data.keys()]))

        return pd.Series(lls)
```