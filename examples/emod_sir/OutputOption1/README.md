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
Base_Infectivity_Constant (how infectious?)
Infectious_Period_Exponential (how long infectious?)
Incubation_Period_Constant (how long latent?)
```
These 3 params ought to be able to get us to almost any regular SIR set of curves.

 
##### Reference Data
The reference data is sparse prevalence values, every 30 days. For example:
```
0,  0.001
30, 0.019
60, 0.141
90, 0.084
120,0.017
150,0.003
180,0
```

So we have the epidemic peeking at around day 70, below 20%. The plot is TBD.

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
* N_ITERATIONS = 20 (let's stop before too long and see how we're doing)

##### To Run
calibrate.py is the main run script of this example. Please refer to it for example information

calibrate.py is run via:
```
python calibrate.py
```

##### Output
Option 1) In the first case, we let calibra run for 20 iterations using the same sparse prevalence values we used in py-sir/OutputOption2.

Option 2) In the second case, eveyrything is similar except our reference output is actually taken from an EMOD run, just in case that matters. 

We are expecting to have the tool 'rediscover' input values of ~: 
* Base_Infectivity_Constant: ~1.0
* Infectious_Period_Exponential: ~4.0
* Incubation_Period_Constant: ~7.8
