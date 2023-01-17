<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

- [Welcome to the EMOD SIS Demo of idmtools-calibra.](#welcome-to-the-emod-sis-demo-of-idmtools-calibra)
      - [Explanation](#explanation)
        - [Reference Data](#reference-data)
        - [Model](#model)
        - [Settings](#settings)
        - [To Run](#to-run)
        - [Output](#output)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Welcome to the EMOD SIS Demo of idmtools-calibra.
#### Explanation
This is the fourth example/demo. Here, we have a very simple SIS model (in EMOD). It has 6 parameters:
```
* Base_Infectivity_Constant (how infectious?)
* Infectious_Period_Exponential (how long infectious?)
* Incubation_Period_Constant (how long latent?)
* Acquisition_Blocking_Immunity_Decay_Rate (how fast immunity decays)
* Acquisition_Blocking_Immunity_Duration_Before_Decay (how long before immunity decays)
* Vaccine Efficacy
```
This is the same as EMOD-Generic SIS Output Option 1 except we've added a campaign component for the first time. Our campaign consists of an acquisition-blocking vaccine given to everyone at the 1 year mark. Our sim now lasts for 2 years. (The efficacy lasts 10 years -- beyond the reach of our sim.)

 
##### Reference Data
The reference data is two scalars:
1) The mean prevalence over the last 60 days of the first year.
2) The mean prevalence over the last month of the second year.
```
metric,value
mean_prev_y1,0.2
mean_prev_y2,0.05
```

##### Model
The model is EMOD-generic. This should get installed by doing:
```
pip3 install -r requirements.txt
```
or
```
pip3 install emod-generic
```

##### Settings
* N_SAMPLES = 125 (5 samples, 3 'axes')
* N_REPLICATES = 1 (with so many samples we hopefully don't need to worry about replicates for now)
* N_ITERATIONS = 10 (let's stop before too long and see how we're doing)

##### To Run
calibrate.py is the main run script of this example. Please refer to it for example information

calibrate.py is run via:
```
python3.9 calibrate.py

```
Replace 'python3.9' as appropriate for your machine.

##### Output
Option 2) In this second SIS dem, we let calibra run for 10 iterations again.

test_and_plot.py runs a sweep over 10 Run_Number values using the best values found for the 6 parameters. It should look something like this:
![](results_sweep.png)
