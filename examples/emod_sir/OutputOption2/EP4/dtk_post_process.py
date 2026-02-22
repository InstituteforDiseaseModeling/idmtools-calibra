#!/usr/bin/python

import json
import os

def application( output_path ):
    # Create output.csv file with sparse Prevalence channel
    with open( os.path.join( output_path, "InsetChart.json" ) ) as icj_fp:
        prev = json.loads( icj_fp.read() )["Channels"]["Infected"]["Data"]
    t_max = 0
    max_i = 0
    for idx in range( len( prev ) ):
        if prev[idx]>max_i:
            t_max=idx
            max_i=prev[idx]
    with open( os.path.join( output_path, "output.csv" ), "w" ) as calib_out_fp:
        calib_out_fp.write( "metric,value\n" )
        calib_out_fp.write( f"t_max,{t_max}\n" )
