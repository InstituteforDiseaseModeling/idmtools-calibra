import pandas as pd

from idmtools_calibra.analyzers.base_calibration_analyzer import BaseCalibrationAnalyzer


class RMSEAnalyzer(BaseCalibrationAnalyzer):

    # Setting up the reference data for use in the analyzer and identifying the model output file to compare against
    def __init__(self, site, dependent_column, independent_column, output_filename="output.csv"):
        #self.model_output_filename = '/'.join(['output', f'{dependent_column}.csv'])
        self.model_output_filename = '/'.join(['output', f'{output_filename}'])

        self.independent_column = independent_column  # 'date'
        self.dependent_column = dependent_column  # 'production'
        self.reference = site.get_reference_data(reference_type='production') # TBD, let's not hardcode this

        # rename reference data column to NOT conflict with model data column; it happens to have the same column
        # name in this example
        self.reference_column = f"{self.dependent_column}_reference"
        self.reference.rename(columns={self.dependent_column: self.reference_column}, inplace=True)
        super().__init__(filenames=[str(self.model_output_filename)])

    # Here we do what needs to be done once per simulation. Often, as below, the main goal is to line up comparable
    # reference and model data.
    def map(self, data, item):
        sim_df = data[str(self.model_output_filename)]

        # merge reference and model data
        merged = self.reference.merge(sim_df, on=self.independent_column)
        merged.index.name = 'Index'

        # each thing returned by 'map' will be available for use in 'reduce'
        result = {
            'df': merged,
            'reference_column': self.reference_column,
            'data_column': self.dependent_column
        }
        return result

    @staticmethod
    def _rmse(series1, series2):
        return ((series1 - series2) ** 2).mean() ** 0.5

    @classmethod
    def rmse(cls, df, data_column, reference_column):
        return cls._rmse(series1=df[data_column], series2=df[reference_column])

    def compare(self, sample, data_column, reference_column):
        # we need to now group by Sim_Id within sample, which lets us compute scores on a per-replicate basis
        replicate_groups = sample.groupby(['Sim_Id'])
        # One rmse per replicate
        rmses = replicate_groups.apply(self.rmse, data_column=data_column, reference_column=reference_column)

        # low rmse is good, so we invert rmse to get 'likelihood score' (where higher is better). This is what calibra
        # assumes: higher scores are better.
        scores = (1 / rmses)
        # computing replicate-averaged score, which is our score for the parameterization sample provided
        score = scores.mean()

        return score

    def reduce(self, all_data):
        """
        Combine the simulation data into a single table for all analyzed simulations.
        """
        data = {}
        reference_column = None
        data_column = None

        # Obtain and set the sample index on each mapped result so that we can properly identify which result
        # belongs to which sample and to support replicate handling.
        # Also identify which data columns are to be used in the scoring calculation, as reported by
        # the mapped results.
        for simulation, mapping_dict in all_data.items():
            sample_index = int(simulation.tags.get("__sample_index__"))
            key = (sample_index, simulation.id)
            data[key] = mapping_dict['df']
            reference_column = reference_column or mapping_dict['reference_column']
            data_column = data_column or mapping_dict['data_column']

        # a bit of name manipulation for calibra's sake
        data = pd.concat(list(data.values()), axis=0, keys=list(data.keys()), names=['Sample', 'Sim_Id'])
        data.reset_index(level='Index', drop=True, inplace=True)

        # compare sim data to reference data and determine a match likelihood/score. Higher is better in calibra.
        results = data.reset_index().groupby(['Sample']).apply(self.compare,
                                                               reference_column=reference_column,
                                                               data_column=data_column)

        # the return of 'reduce' is a Series of N items, where N is the number of samples run with
        return results
