#!/usr/bin/python

import json
import os

def application( output_path ):
    # Calculate mean prevelance over final 60 days
    final_prev_a = 0
    final_prev_b = 0
    final_prev_c = 0
    final_prev_d = 0

    with open( os.path.join( output_path, "PropertyReport.json" ) ) as icj_fp:
        json_data = json.loads( icj_fp.read() )
        final_prev_a = json_data ["Channels"]["Infected:Geographic:Province_A"]["Data"][-1]/json_data ["Channels"]["Statistical Population:Geographic:Province_A"]["Data"][-1]
        final_prev_b = json_data ["Channels"]["Infected:Geographic:Province_B"]["Data"][-1]/json_data ["Channels"]["Statistical Population:Geographic:Province_B"]["Data"][-1]
        final_prev_c = json_data ["Channels"]["Infected:Geographic:Province_C"]["Data"][-1]/json_data ["Channels"]["Statistical Population:Geographic:Province_C"]["Data"][-1]
        final_prev_d = json_data ["Channels"]["Infected:Geographic:Province_D"]["Data"][-1]/json_data ["Channels"]["Statistical Population:Geographic:Province_D"]["Data"][-1]
    with open( os.path.join( output_path, "output.csv" ), "w" ) as calib_out_fp:
        calib_out_fp.write( "metric,value\n" )
        calib_out_fp.write( f"A,{final_prev_a}\n" )
        calib_out_fp.write( f"B,{final_prev_b}\n" )
        calib_out_fp.write( f"C,{final_prev_c}\n" )
        calib_out_fp.write( f"D,{final_prev_d}\n" )
