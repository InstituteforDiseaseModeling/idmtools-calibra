#!/usr/bin/env python

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import json
import os
import sys
from sklearn.linear_model import LinearRegression

def plot( calibname="solar_optimtool_linear_model" ):
    df = pd.read_csv( "reference/production.csv" )
    df.plot( kind="scatter", x="date", y="production" )

    x = np.linspace(start=0,stop=200,num=101)
    with open( os.path.join( calibname, "CalibManager.json" ) ) as output:
        json_output = json.loads( output.read() )
        grad = json_output["final_samples"]["linear-coefficient"]
        inter = json_output["final_samples"]["constant"]
    y = grad*x+inter
    plt.plot(x, y, '-r', label=f'y={grad}x+{inter}')

    x_data = np.array( df["date"] )
    y_data = np.array( df["production"] )
    model = LinearRegression() 
    model.fit( x_data.reshape(-1,1), y_data.reshape(-1,1) )
    x_new = np.linspace(1,200,201)
    y_new = model.predict(x_new[:, np.newaxis])
    plt.plot(x_new,y_new,'-g')

    plt.title(f'Graph of y={grad}x+{inter}')
    plt.xlabel('days', color='#1C2833')
    plt.ylabel('mw-hours', color='#1C2833')
    plt.legend(loc='upper left')
    plt.grid()
    plt.show()


