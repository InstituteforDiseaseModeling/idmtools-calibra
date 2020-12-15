import numpy as np
import pandas as pd
import logging

from .TBCalibSite import TBCalibSite
from .TBCalibAnalyzer import TBCalibAnalyzer

logger = logging.getLogger(__name__)


class SouthAfricaCalibSite(TBCalibSite):
    mort_remap = {'name': 'DiseaseDeaths',
                  'map_variables': ['DiseaseDeaths', 'HIVDeaths_ActiveTB'],
                  'func': np.sum}

    rd_format = {'Incidence': {'Year': list(np.arange(2000, 2019)),
                               'AgeBin': ['All']},
                 'DiseaseDeaths': {'Year': list(np.arange(2000, 2019)),
                                   'AgeBin': ['All']}
                 }

    def __init__(self):
        super(SouthAfricaCalibSite, self).__init__('South Africa')

    def get_analyzers_orig(self):
        return [TBCalibAnalyzer(site=None, siteTB=self, input_vars=[],
                                local_dir='South Africa', start_year=1900, year_range=[1990, 2050],
                                columns=['Incidence', 'DiseaseDeaths'], remap=[SouthAfricaCalibSite.mort_remap],
                                weights=[0.5, 1.0])]

    def get_analyzers(self):
        return [TBCalibAnalyzer(site=None, siteTB=self, input_vars=[],
                                local_dir='South Africa', start_year=1900, year_range=[1990, 2050],
                                columns='All', remap=[SouthAfricaCalibSite.mort_remap],
                                weights=[0.5, 1.0])]


if __name__ == '__main__':

    agemap_dictionary = {
        'Under 5': '0_4',
        '5 to 9': '5_14',
        '10 to 14': '5_14',
        '15 to 19': '15_24',
        '20 to 24': '15_24',
        '25 to 29': '25_34',
        '30 to 34': '25_34',
        '35 to 39': '35_44',
        '40 to 44': '35_44',
        '45 to 49': '45_54',
        '50 to 54': '45_54',
        '55 to 59': '55_64',
        '60 to 64': '55_64',
        '65 to 69': '65_999',
        '70 to 74': '65_999',
        '75 to 79': '65_999',
        '80 plus': '65_999'
    }


    def agemap(agebin):
        return agemap_dictionary.get(agebin)


    def uncertaintymap(upper, lower, val, denominator):
        sigma = (((upper - lower) / (2.0 * 1.95)))
        scalefactor = (np.sqrt(val) / sigma) ** 2
        return scalefactor


    def computeN(average, low, high, scale=1.0e5):
        pop_sigma = (high - low) / (2.0 * 1.96 * scale)
        average /= scale
        bernouilli_sigma = np.sqrt(average * (1.0 - average))
        Trial_N = (bernouilli_sigma / pop_sigma) ** 2.0
        return Trial_N


    d = SouthAfricaCalibSite()
    writer = pd.ExcelWriter('MasterDataforCalibration.xlsx')

    for name in d.rd_format.keys():
        a = (d.rd_format.get('Incidence').get('Year'))
        b = d.rd_format.get('Incidence').get('AgeBin')
        idx = pd.MultiIndex.from_product([a, b], names=['Year', 'AgeBin'])
        col = ['Observations', 'Trials']
        df = pd.DataFrame('-', idx, col)

        df.to_excel(writer, sheet_name=name)
    writer.save()
    print('Created template calibration data file')

    WHO_data = True
    if WHO_data:
        cols_to_use = ['e_inc_100k', 'e_inc_100k_lo', 'e_inc_100k_hi', 'e_mort_100k', 'e_mort_100k_lo',
                       'e_mort_100k_hi']
        data_loc = pd.read_csv('TBburden.csv', usecols=cols_to_use + ['country', 'year'])
        data_loc = data_loc[data_loc['country'] == 'South Africa']
        data_loc['Trial_Mort'] = data_loc[['e_mort_100k', 'e_mort_100k_lo', 'e_mort_100k_hi']].apply(
            lambda x: computeN(*x), axis=1)
        data_loc['Observations_Mort'] = data_loc[['e_mort_100k', 'Trial_Mort']].apply(lambda x: np.multiply(*x) / 1.0e5,
                                                                                      axis=1)
        data_loc['Trial_Inc'] = data_loc[['e_inc_100k', 'e_inc_100k_lo', 'e_inc_100k_hi']].apply(lambda x: computeN(*x),
                                                                                                 axis=1)
        data_loc['Observations_Inc'] = data_loc[['e_inc_100k', 'Trial_Inc']].apply(lambda x: np.multiply(*x) / 1.0e5,
                                                                                   axis=1)
        data_loc.drop(columns=cols_to_use, inplace=True)
        data_loc.set_index(['country', 'year'], inplace=True)
        data_loc.to_csv('SAWHO_for_calib.csv')

    add_causes = ['measure', 'age', 'cause', 'metric', 'year']
    reduced = ['measure', 'year', 'age', 'metric']
    data_loc = pd.read_csv('IHME_India_from1995.csv', index_col=reduced, usecols=add_causes + ['val', 'upper', 'lower'])

    # aggregate over the subcategories (note rates are per 100k in IHME)
    data_loc = data_loc.groupby(reduced).sum()
    data_loc = data_loc.unstack(-1)
    data_loc.columns = data_loc.columns.swaplevel(0, 1)
    # compute denominator from the rate
    data_loc['Number', 'Denominator'] = data_loc.Number.val / (data_loc.Rate.val) * 1.0e5
    print(data_loc['Number', 'Denominator'])
    # resubdivide the age-bins
    data_loc.reset_index(inplace=True)
    data_loc['age'] = data_loc['age'].apply(lambda x: agemap(x))
    data_loc = data_loc.drop(columns=['Rate'])  # rates are not additive so drop
    data_loc = data_loc.groupby(['measure', 'year', 'age']).sum()

    # compute what the Trial number c
    data_loc.columns = data_loc.columns.droplevel(0)
    data_loc['Scale_factor'] = data_loc[['upper', 'lower', 'val', 'Denominator']].apply(lambda x: uncertaintymap(*x),
                                                                                        axis=1)
    data_loc['Observations'] = data_loc['Scale_factor'] * data_loc['val']
    data_loc['Trials'] = data_loc['Scale_factor'] * data_loc['Denominator']
    data_loc = data_loc[['Observations', 'Trials']]

    IHME_writer = pd.ExcelWriter('IHME_output.xlsx')
    # rename some columns
    data_loc.rename(index={'Deaths': 'DiseaseDeaths'}, inplace=True)
    data_loc.reset_index(inplace=True)
    data_loc.rename(columns={'age': 'AgeBin', 'year': 'Year'}, inplace=True)
    data_loc.set_index(['measure', 'Year', 'AgeBin'], inplace=True)
    for name in data_loc.index.get_level_values(0).unique():
        data_tmp = data_loc.loc[(name, slice(None), slice(None)),]
        data_tmp.reset_index(inplace=True)
        data_tmp = data_tmp.set_index(['Year', 'AgeBin']).drop(columns='measure')
        data_tmp.to_excel(IHME_writer, sheet_name=name)
    IHME_writer.save()
