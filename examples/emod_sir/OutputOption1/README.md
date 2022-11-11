<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

- [Welcome to the EMOD SIR Demo of idmtools-calibra.](#welcome-to-the-emod-sir-demo-of-idmtools-calibra)
      - [Explanation](#explanation)
        - [Reference Data](#reference-data)
        - [Model](#model)
        - [Settings](#settings)
        - [To Run](#to-run)
        - [Output](#output)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Welcome to the EMOD SIR Demo of idmtools-calibra.
#### Explanation
This is the third example/demo. Here, we have a very simple SIR model (in EMOD). It also has 3 parameters:
```
* Base_Infectivity_Constant (how infectious?)
* Infectious_Period_Exponential (how long infectious?)
* Incubation_Period_Constant (how long latent?)
```
These 3 params ought to be able to get us to almost any regular SIR set of curves.

 
##### Reference Data
The reference data is a single scalar: The timestep of peak prevalence.
```
metric,value
t_max,59.999
```

So we have the epidemic peeking at t=60. (We use 59.999 to avoid a divide by zero error which occurs with 60.0.)

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
python3.9 calibrate.py && python3.9 test_and_plot.py

```
Replace 'python3.9' as appropriate for your machine.

##### Output
Option 1) In the first case, we let calibra run for 10 iterations.

test_and_plot.py runs a sweep over 10 Run_Number values using the best values found for the 3 parameters.
