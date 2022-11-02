import numpy as np
from scipy.integrate import odeint
import matplotlib.pyplot as plt
from pathlib import Path
import json
import os

# settings
beta, gamma = 0.2, 1./10 
if os.path.exists( "config.json" ):
    with open( "config.json" ) as f:
        config = json.loads( f.read() )
    beta, gamma = config["a"], config["b"]
elif os.path.exists( "sir2/CalibManager.json" ):
    with open( "sir2/CalibManager.json" ) as f:
        config = json.loads( f.read() )
    beta, gamma = config["final_samples"]["beta"][-1], config["final_samples"]["gamma"][-1]
    
# Initial conditions
# Total population, N.
N = 1000
# Initial number of infected and recovered individuals, I0 and R0.
I0, R0 = 1, 0
# Everyone else, S0, is susceptible to infection initially.
S0 = N - I0 - R0
# Contact rate, beta, and mean recovery rate, gamma, (in 1/days).

# A grid of time points (in days)
t = np.linspace(0, 160, 160)

# The SIR model differential equations.
def deriv(y, t, N, beta, gamma):
    S, I, R = y
    dSdt = -beta * S * I / N
    dIdt = beta * S * I / N - gamma * I
    dRdt = gamma * I
    return dSdt, dIdt, dRdt

def visualize( S, I, R):
# Visualizations
# Plot the data on three separate curves for S(t), I(t) and R(t)
    fig = plt.figure(facecolor='w')
    ax = fig.add_subplot(111, facecolor='#dddddd', axisbelow=True)
    ax.plot(t, S/1000, 'b', alpha=0.5, lw=2, label='Susceptible')
    ax.plot(t, I/1000, 'r', alpha=0.5, lw=2, label='Infected')
    ax.plot(t, R/1000, 'g', alpha=0.5, lw=2, label='Recovered with immunity')
    ax.set_xlabel('Time /days')
    ax.set_ylabel('Number (1000s)')
    ax.set_ylim(0,1.2)
    ax.yaxis.set_tick_params(length=0)
    ax.xaxis.set_tick_params(length=0)
    ax.grid(b=True, which='major', c='w', lw=2, ls='-')
    legend = ax.legend()
    legend.get_frame().set_alpha(0.5)
    for spine in ('top', 'right', 'bottom', 'left'):
        ax.spines[spine].set_visible(False)
    plt.show()

def write_output( S, I, R ):
    # write results
    lines = ["timestep,prevalence"]
    #for i in range(len(model_results)):
    #    lines.append(f"{independent_values[i]},{model_results[i]}")
    #lines.append(f"S,{S[-1]/N}")
    #lines.append(f"I,{I[-1]/N}")
    #lines.append(f"R,{R[-1]/N}")
    for t in range(0,len(I),30):
        lines.append(f"{t},{I[t]/N}")

    lines_str = '\n'.join(lines)
    output_path = Path('output', 'output.csv')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(lines_str)

import argparse
parser = argparse.ArgumentParser()
parser.add_argument( "-v", "--visualize", action='store_true', default=False, help="Plot to screen instead of write to disk." )
args = parser.parse_args()

# Initial conditions vector
y0 = S0, I0, R0
# Integrate the SIR equations over the time grid, t.
ret = odeint(deriv, y0, t, args=(N, beta, gamma))
S, I, R = ret.T

print( S[-1]/N, I[-1]/N, R[-1]/N )
if args.visualize:
    visualize( S, I, R )
else:
    write_output( S, I, R )
