#!/usr/bin/python

import json
import os

def application( output_path ):
    # Create output.csv file with sparse Prevalence channel
    with open( os.path.join( output_path, "InsetChart.json" ) ) as icj_fp:
        prev = json.loads( icj_fp.read() )["Channels"]["Infected"]["Data"]
    with open( os.path.join( output_path, "output.csv" ), "w" ) as calib_out_fp:
        calib_out_fp.write( "timestep,prevalence\n" )
        for t in range( 0, len(prev), 30 ):
            calib_out_fp.write( f"{t},{prev[t]}\n" )
