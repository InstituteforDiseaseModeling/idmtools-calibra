# Welcome to the Hello World of idmtools-calibra.
#### Explanation
We start with some real-world data from a solar panel. We have measured mw-hours of energy produced each day for 200 days. Plot is TBD. Our goal is to create a simple linear model of the principal component of this dataset. We use calibra to solve this. To be specific, we are trying to discover a line, and since lines are described as 
```
y = mx + c
```
where m is the gradient and c is the intercept, we need to solve for m and c.

In addition to our reference dataset (reference/production.csv), we also have a very simple "model", written in Python, and takes two input parameters -- gradient and intercept -- and produces "y=mx+c" + some noise. For an example plot, TBD. The code for this is found in bin/linear_model.py.

In order to throw calibra at this problem, we need to hook the code up to our reference data and our model. And then make a few quantitative decisions. 

##### Reference Data
In order to connect up our reference data, we need something called a "site", which is captured in a class. In this case the class is called SolarSite and the file is called solar_site.py. You can see it's very short and makes some assumptions: it assumes the reference data is in a csv, and it assumes that the model output data that it will comparing this to is in the same format. You may also notice that it hands the quantitive "error measurement" work off to an Analyzer. In this case, it's a Root Mean Square Error calculator, in a class called from RMSEAnalyzer in a file rmse_analyzer.py. You do not need to code up your own analyzer if you're willing to use one of the stock or library ones.

##### Model
This example uses as As-Simple-As-Possible toy model to get things started. From a system point of view, it takes a configuration which holds parameters, it runs when invoked, and produces an output data file. If that output data file is already in the format of our reference dateset -- in this case a set of 200 csv value pairs -- we can pass it as-is to calibra. We actually execute the model, as simple as it is, on COMPS. Someone will have to connect up other models, like EMOD, as a one-time activity. That should then be stored as the EMOD-Calibra Template.

##### Settings
The various settings -- like how many iterations to run, how many samples to include in each iteration, etc. -- are held in the Settings class. (This 'class' is essentially just a variable bucket.)

##### To Run
calibrate.py is the main run script of this example. Please refer to it for example information

calibrate.py is run via:
```
python calibrate.py
```

