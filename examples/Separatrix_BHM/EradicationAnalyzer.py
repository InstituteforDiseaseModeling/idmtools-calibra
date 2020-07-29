import os
import pandas as pd
from simtools.Analysis.BaseAnalyzers import BaseAnalyzer
import matplotlib.pyplot as plt

class EradicationAnalyzer(BaseAnalyzer):
    def __init__(self):
        super().__init__(filenames=['output\\InsetChart.json'])

        self.ch_vec = ['Susceptible Population', 'Infected', 'Recovered Population', 'New Infections']

    def select_simulation_data(self, data, simulation):
        # Apply is called for every simulations included into the experiment
        # We are simply storing the population data in the pop_data dictionary
        header = data[self.filenames[0]]["Header"]
        time = [header["Start_Time"] + dt * header["Simulation_Timestep"] for dt in range(header["Timesteps"])]

        ret = {
            'sample_index': simulation.tags.get('__sample_index__'),
            'Time': time
        }

        for ch in self.ch_vec:
            ret[ch] = data[self.filenames[0]]["Channels"][ch]["Data"]

        return ret


    def finalize(self, all_data):
        fig, ax_vec = plt.subplots(nrows=2, ncols=2, sharex=True, figsize=(16,10))

        for key, data in all_data.items():
            d = pd.DataFrame(data)
            for ch, ax in zip(self.ch_vec, ax_vec.flatten()):
                ax.plot(d['Time'], d[ch])
                ax.set_xlabel('Time')
                ax.set_ylabel(ch)

        #ax.legend([s.id for s in all_data.keys()])
        fig.savefig(os.path.join(self.working_dir, "EradicationAnalyzer.png"))

        any_infected = []
        # Sort our data by sample_index
        # We need to preserve the order by sample_index
        for d in sorted(all_data.values(), key=lambda k: k['sample_index']):
            any_infected.append(2*(d['Infected'][-1] == 0.0)-1) # At final time

        return pd.Series(any_infected)

    def cache(self):
        # Somehow required function for calibtool?
        return None
