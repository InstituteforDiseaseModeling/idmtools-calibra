import json
from pathlib import Path
import random


def linear_model(a, b, x, noisy=True):
    # generate the config-specified linear line, for a selection of independent-axis values
    if noisy:
        noise = (random.random() - 0.5) * 2  # -1 to 1
        noise = noise * 0.1  # scaled to -0.1 to 0.1
    else:
        noise = 1

    return (a * x + b) * (1 + noise)


def parse_args():
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument('-c', '--config', dest='config_filename', type=str, required=True,
                        help='Path of configuration file to load (Required).')
    args = parser.parse_args()

    return args


def run_from_values( a, b ):
    independent_values = [x+1 for x in range(200)]
    model_results = [linear_model(a, b, x+1) for x in independent_values]

    # write results
    lines = ["date,production"]
    for i in range(len(model_results)):
        lines.append(f"{independent_values[i]},{model_results[i]}")
    lines_str = '\n'.join(lines)

    output_path = Path('output', 'output.csv')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(lines_str) 

def main(args):
    # load the config file
    with open(args.config_filename, 'r') as f:
        config = json.load(f)

    # set the random seed
    run_number = int(config['Run_Number'])
    random.seed(run_number)

    # generate results for x = 1 through 200
    a = config['a']
    b = config['b']
    run_from_values( a, b )

if __name__ == '__main__':
    args = parse_args()
    main(args)
