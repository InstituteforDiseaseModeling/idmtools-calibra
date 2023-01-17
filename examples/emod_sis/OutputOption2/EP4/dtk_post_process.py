#!/usr/bin/python

import json
import os

def application( output_path ):
    # Calculate mean prevelance over final 60 days
    with open( os.path.join( output_path, "InsetChart.json" ) ) as icj_fp:
        prev = json.loads( icj_fp.read() )["Channels"]["Infected"]["Data"]
    result1 = 0
    cum1 = 0 
    for idx in range( 305,365,1 ):
        cum1 += prev[idx]
    result1 = cum1 / 60
    result2 = 0
    cum2 = 0 
    for idx in range( 700,730,1 ):
        cum2 += prev[idx]
    result2 = cum2 / 30
    with open( os.path.join( output_path, "output.csv" ), "w" ) as calib_out_fp:
        calib_out_fp.write( "metric,value\n" )
        calib_out_fp.write( f"mean_prev_y1,{result1}\n" )
        calib_out_fp.write( f"mean_prev_y2,{result2}\n" )
