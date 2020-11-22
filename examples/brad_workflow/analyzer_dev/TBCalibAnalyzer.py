import logging
import os
import matplotlib.pyplot as plt
import seaborn as sns

import pandas as pd
import numpy as np

# from dtk.utils.analyzers import default_select_fn, default_group_fn, default_filter_fn
# from dtk.utils.analyzers.plot import plot_by_channel
from scipy.special import gammaln
from functools import reduce

# from calibtool.LL_calculators import gamma_poisson_pandas, beta_binomial_pandas
# from simtools.Analysis.BaseAnalyzers import BaseAnalyzer
# from simtools.Analysis.BaseAnalyzers.BaseCalibrationAnalyzer import BaseAnalyzer, BaseCalibrationAnalyzer
from itertool.analyzers.base_calibration_analyzer import BaseCalibrationAnalyzer

logger = logging.getLogger(__name__)

ordered_age_levels = ['LESS_1', 'LESS_5', 'LESS_10', 'LESS_15', 'LESS_20', 'LESS_25', 'LESS_30', 'LESS_35',
                      'LESS_40', 'LESS_45', 'LESS_50', 'LESS_55', 'LESS_60', 'LESS_65',
                      'LESS_70', 'LESS_75', 'LESS_80', 'LESS_85', 'LESS_90', 'LESS_95', 'GREAT_95']
ordered_age_levels_minus_max = ['LESS_1', 'LESS_5', 'LESS_10', 'LESS_15', 'LESS_20', 'LESS_25', 'LESS_30', 'LESS_35',
                                'LESS_40', 'LESS_45', 'LESS_50', 'LESS_55', 'LESS_60', 'LESS_65',
                                'LESS_70', 'LESS_75', 'LESS_80', 'LESS_85', 'LESS_90', 'LESS_95']


def gamma_poisson_pandas(df, mean=False):
    LL = gammaln(df.ref.Observations + df.sim.Observations + 1) \
         - gammaln(df.ref.Observations + 1) \
         - gammaln(df.sim.Observations + 1)

    ix = df.ref.Trials > 0
    LL.loc[ix] += (df.loc[ix].ref.Observations + 1) * np.log(df.loc[ix].ref.Trials)

    ix = df.sim.Trials > 0
    LL.loc[ix] += (df.loc[ix].sim.Observations + 1) * np.log(df.loc[ix].sim.Trials)

    ix = (df.ref.Trials > 0) & (df.sim.Trials > 0)
    LL.loc[ix] -= (df.loc[ix].ref.Observations + df.loc[ix].sim.Observations + 1) \
                  * np.log(df.loc[ix].ref.Trials + df.loc[ix].sim.Trials)

    if mean == True:
        return LL.mean
    else:
        return LL


def beta_binomial_pandas(df, mean=False):
    LL = gammaln(df.ref.Trials + 1) \
         + gammaln(df.sim.Trials + 2) \
         - gammaln(df.ref.Trials + df.sim.Trials + 2) \
         + gammaln(df.ref.Observations + df.sim.Observations + 1) \
         + gammaln(df.ref.Trials - df.ref.Observations + df.sim.Trials - df.sim.Observations + 1) \
         - gammaln(df.ref.Observations + 1) \
         - gammaln(df.ref.Trials - df.ref.Observations + 1) \
         - gammaln(df.sim.Observations + 1) \
         - gammaln(df.sim.Trials - df.sim.Observations + 1)

    if mean == True:
        return LL.mean
    else:
        return LL


def map_age_level(age_level, new_age_levels):
    if 'All' in new_age_levels:
        return 'All'

    # now do cases where we split up age levels.
    stripped_tuple = [a.split('_') for a in new_age_levels]

    for i, name in enumerate(new_age_levels):
        suffix, maxval = age_level.split('_')
        maxval = int(maxval) - 1
        if suffix == 'LESS':
            if maxval >= int(stripped_tuple[i][0]) and maxval <= int(stripped_tuple[i][1]):
                return name
        elif suffix == 'GREAT':
            if maxval >= int(stripped_tuple[i][0]) and maxval + 120 <= int(stripped_tuple[i][1]):
                # note 120 chosen to exceed max human age in years
                return name

    raise ValueError  # we should never get through the loop without returning something


class TBCalibAnalyzer(BaseCalibrationAnalyzer):
    data_group_names = ['sample', 'sim_id', 'channels']

    def __init__(self, site=None, siteTB=None, filename=[os.path.join('output', 'Report_TBHIV_ByAge.csv')],
                 remap=None, outputs=None, local_dir=None, input_vars=None,
                 year_range=None, name='TBPlotAnalyzer', like_dimensions=['Incidence', 'DiseaseDeaths'],
                 start_year=1900, columns='All', outfile='Outfile', infile='Data.xlsx', sum_LL_axes=['AgeBin'],
                 avg_LL_axes=['Year'], weights=[1.0]):
        super().__init__(site)
        self.name = name
        self.filenames = filename
        self.outfile = outfile + '.csv'
        self.columns = columns
        self.prevalence_columns = ['Population', 'Active']
        self.setup = {}
        self.start_year = start_year
        self.variables = input_vars
        self.years = year_range
        self.local_dir = local_dir
        self.need_dir_map = True
        self.likdimensions = like_dimensions
        self.input_file = infile
        self.sum_LL_axes = sum_LL_axes
        self.avg_LL_axes = avg_LL_axes
        self.weights = weights
        self.remap = remap
        if outputs:
            self.labels = outputs
        else:
            self.labels = []
        self.set_site(siteTB)

        #
        # Note remap has form of dictionary ie  remap = {'name': 'DiseaseDeaths','map_variables': ['DiseaseDeaths', 'HIVDeaths_ActiveTB',  'func' : np.sum}

    def initialize(self):
        # if self.local_dir and not os.path.exists(self.local_dir):
        #     os.mkdir(self.local_dir)
        # save local analysis outputs to this directory
        # [TODO] zdu: comment out above two line and will use iteration state working directory
        if not os.path.exists(self.working_dir):
            os.mkdir(self.working_dir)

    def per_experiment(self, experiment):
        pass

    def filter(self, simulation):
        pass

    def map(self, data, simulation):
        """
        simulation :type simulation: object
        """
        csv_data = data[self.filenames[0]]
        if self.columns != 'All':
            csv_data = csv_data[['Year', 'NodeID', 'AgeBin', 'Population'] + self.columns]
        csv_data_copy = csv_data.copy()
        csv_data_copy['Year'] = csv_data['Year'].apply(lambda x: x + self.start_year)
        csv_data = csv_data_copy
        if self.years:
            csv_data = csv_data[csv_data['Year'].between(self.years[0], self.years[1])]  # cut down to needed years
        if self.remap:
            for entry in self.remap:
                try:
                    csv_data_copy = csv_data.copy()
                    csv_data_copy[entry.get('name')] = csv_data[entry.get('map_variables')].apply(
                        entry.get('func'), axis=1)
                    csv_data = csv_data_copy

                except ValueError as e:
                    print('make iterable')
                    csv_data_copy = csv_data.copy()
                    csv_data_copy[entry.get('name')] = csv_data[entry.get('map_variables')].apply(
                        entry.get('func'), axis=1)
                    csv_data = csv_data_copy
                    print(e)

                if bool(set(self.prevalence_columns).intersection(set(entry.get('map_variables')))) \
                        and entry.get('name') not in self.prevalence_columns:
                    self.prevalence_columns += [entry.get('name')]

        csv_data.set_index(['Year', 'NodeID', 'AgeBin'], inplace=True)
        d = csv_data.unstack(level=[-1, -2])

        # Set the proper years for interpolation
        year_index = np.arange(self.years[0] + 0.5, self.years[1] + 0.5, 0.5)
        super_index = d.index.union(year_index)
        e = d.reindex(super_index, axis=0)
        second_order_adjust_incidence = 1.0 / np.diff(d.index).mean()
        e.interpolate(inplace=True)
        e = e.loc[(year_index),]
        e = e.stack(level=[-1, -2])
        e.reset_index(inplace=True)
        e['Year'] = e['level_0'].apply(lambda x: int(np.floor(x)))
        e.set_index(['NodeID', 'AgeBin', 'Year'], inplace=True)
        e.drop(labels=['level_0'], axis=1, inplace=True)
        for col in e.columns:
            if col not in self.prevalence_columns:
                e[col] = e[col].apply(lambda x: x * second_order_adjust_incidence)
        e = e.groupby(['NodeID', 'AgeBin', 'Year']).mean()

        if self.variables:
            for var in self.variables:
                variable = simulation.tags.get(var)
                e[var] = variable

        e['sim_id'] = simulation.id
        sample_val = simulation.tags.get('__sample_index__')
        if int(sample_val) >= 0:
            e['sample_id'] = sample_val

        return e

    def set_site(self, site):
        '''
        Get data
        '''
        self.site = site

    def filter(self, sim_metadata):
        '''
        This analyzer only needs to analyze simulations for the site it is linked to.
        N.B. another instance of the same analyzer may exist with a different site
             and correspondingly different reference data.
        '''

        return True

    def compare(self, df, col, lik_type='gamma_poisson'):
        '''
        return dataframe with likelihood functions
        '''
        df_sample = df.copy()
        df_sample.reset_index(inplace=True)
        years_to_compare = self.site.rd_format.get(col).get('Year')
        ix = df_sample.Year.isin(years_to_compare)
        df_sample = df_sample[ix]  # reducing only to years in which we calculate a likelihood
        ad_fields = []
        if 'sample_id' in df_sample.columns:
            ad_fields += ['sample_id']

        # rename to fit with structure of likelihood functions
        df_sample.rename(columns={'Population': 'Trials', col: 'Observations'}, inplace=True)
        df_data = pd.read_excel(self.input_file, col, index_col=[0, 1])

        df_sample['Source'] = 'sim'
        df_data['Source'] = 'ref'
        df_sample['AgeBin'] = df_sample['AgeBin'].apply(
            lambda x: map_age_level(x, self.site.rd_format.get(col).get('AgeBin')))

        df_data.reset_index(inplace=True)
        df_data.set_index(['AgeBin', 'Year', 'Source'], inplace=True)
        df_sample.set_index(ad_fields + ['NodeID', 'sim_id', 'AgeBin', 'Year', 'Source'], inplace=True)
        df_sample = df_sample.groupby(ad_fields + ['NodeID', 'sim_id', 'AgeBin', 'Year', 'Source']).sum()

        df_data = df_data.unstack(-1)
        df_data.columns = df_data.columns.swaplevel(0, 1)
        df_sample = df_sample.unstack(-1)
        df_sample.columns = df_sample.columns.swaplevel(0, 1)
        df_sample = df_sample.join(df_data, how='left', on=['AgeBin', 'Year'])

        if lik_type == 'gamma_poisson':
            out = gamma_poisson_pandas(df_sample)
        elif lik_type == 'beta_binomial':
            out = beta_binomial_pandas(df_sample)
        else:
            raise ValueError

        return out

    def reduce(self, all_data):
        return [1] * len(all_data)    # [TODO] zdu: test to avoid error. Note: it will cause error later if we return None

        data_frame_list = [all_data[sim_key] for sim_key in list(all_data.keys())]
        selected_data = pd.concat(data_frame_list, axis=0)
        # selected_data.to_csv(os.path.join(self.local_dir, self.outfile))
        selected_data.to_csv(os.path.join(self.working_dir, self.outfile))
        print(all_data.keys())

        LL_list = []
        for i, col in enumerate(self.likdimensions):
            LL_list += [self.compare(selected_data, col).multiply(self.weights[i])]
        if 'sample_id' in LL_list[0].index.names:
            group_val_loc = ['sample_id']
        else:
            group_val_loc = ['sim_id']
        # note as written below this is summing over Nodes and age-groups, averaging years, first mean averages over replicates fore each Node
        # and AgeBin and sample (degenerate if sim_id used and or one replicate)
        combined_LL_list = [df.groupby(group_val_loc + ['Year', 'AgeBin', 'NodeID']).mean().groupby(
            group_val_loc + ['Year']).sum().groupby(group_val_loc).mean() for df in LL_list]
        combined_LL = pd.concat(combined_LL_list).groupby(group_val_loc).sum()

        if group_val_loc == ['sample_id']:
            combined_LL.sort_index(inplace=True,
                                   ascending=True)  # double check we are ordered correctly for calib routines

        print(combined_LL_list)
        return pd.Series(combined_LL)

    def cache(self):
        '''
        Return a cache of the minimal data required for plotting sample comparisons
        to reference comparisons.
        '''
        # cache = self.data.copy()

        # sample_dicts = []
        # for idx, df in cache.groupby(level='sample', sort=True) :
        #    d = { 'region' : self.regions,
        #           self.y : [sdf[self.y].values.tolist() for jdx, sdf in df.groupby(level='region') ] }
        #    sample_dicts.append(d)

        # logger.debug(sample_dicts)

        # return {'sims': sample_dicts, 'reference': self.reference, 'axis_names': ['region', self.y]}
        return []

    def uid(self):
        ''' A unique identifier of site-name and analyzer-name. '''
        return '_'.join([self.site.name, self.name])

    def plot_comparison(cls, fig, data, **kwargs):
        """
        Plot data onto figure according to logic in derived classes
        """
        a = 1
        pass
