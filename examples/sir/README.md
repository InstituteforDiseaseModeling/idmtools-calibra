<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

- [Welcome to the Super-Simple SIR Demo of idmtools-calibra.](#welcome-to-the-super-simple-sir-demo-of-idmtools-calibra)
      - [Explanation](#explanation)
        - [Reference Data](#reference-data)
        - [Model](#model)
        - [Settings](#settings)
        - [To Run](#to-run)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Welcome to the Super-Simple SIR Demo of idmtools-calibra.
#### Explanation
This is the second example/demo after the Hello World which tries to find a straight line which goes through some real-world data. In this example, we have a very simple SIR model (in Python). It also has two parameters:
```
beta
gamma
```
where beta is the infection rate and gamma is the recovery rate.

 
##### Reference Data
Our reference data is actually just 3 numbers: the final values of S, I, and R. We don't use any intermediate values for now.

##### Model
See the model in bin/sir.py

##### Settings
Our setting sare the same as the Solar hello world, except our two parameters are different. They both have a range 0-1 and the initial guess is 0.5.

##### To Run
calibrate.py is the main run script of this example. Please refer to it for example information

calibrate.py is run via:
```
python calibrate.py
```

