
from os import path
import json

def application(output_folder="output"):
    config_path = 'config.json'
    with open(config_path, 'r') as config_file:
        params = json.load(config_file)['parameters']

    start_time = params['Start_Time']
    num_timesteps = params['Simulation_Duration']
    ts_size = params['Simulation_Timestep']

    vsp_json = None
    vsp_path = path.join(output_folder, 'VectorSpeciesReport.json')
    with open(vsp_path, 'r') as infile:
        vsp_json = json.load(infile)

    ts_count = vsp_json['Header']['Timesteps']

    ts_channel = {'Units': ''}
    timesteps = list(range(start_time, (num_timesteps * ts_size) + start_time, ts_size))
    ts_channel['Data'] = [timesteps]
    vsp_json['Channels']['timestep'] = ts_channel
    with open('VectorSpeciesReport_ts.json','w') as outfile:
        json.dump(vsp_json, outfile, indent=4, sort_keys=True)
    return

if __name__ == '__main__':
    application('output')



