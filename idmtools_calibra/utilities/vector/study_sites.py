from .species import set_larval_habitat, set_species_param, scale_all_habitats
from ..generic.climate import set_climate_constant
from ..generic.geography import set_geography


class StudySite(object):
    site = ''
    static = False

    @classmethod
    def setup(cls, geography):
        geo_parts = geography.split('.')
        if len(geo_parts) == 2 and geo_parts[1] == 'static':
            cls.site = geo_parts[0]
            cls.static = True
        else:
            cls.site = geography
            cls.static = False

    @classmethod
    def set_geography(cls, simulation, site, pop_scale=1):
        set_geography(simulation, site, cls.static, pop_scale)


def configure_site(cb, site, pop_scale=1):
    StudySite.setup(site)
    cb.set_param("Config_Name", StudySite.site)
    cfg_fn = globals().get('configure_' + StudySite.site.lower(), None)
    if cfg_fn:
        # logging.debug('StudySite.site = %s' % StudySite.site)
        StudySite.set_geography(cb, geography_from_site(StudySite.site), pop_scale)
        cfg_fn(cb)
        if pop_scale != 1:
            scale_all_habitats(cb, pop_scale)
    else:
        raise Exception('%s study site not yet implemented.' % StudySite.site)
    return {'_site_': site, 'population_scale': pop_scale}


def geography_from_site(site):
    site_splits = site.split('.')  # e.g. to accommodate site='Chipepo.static'
    site_to_geography = {
        'Sugungum': 'Garki_Single',
        'Matsari': 'Garki_Single',
        'Rafin_Marke': 'Garki_Single',

        'Chipepo': 'Sinazongwe',
        'SinazongweConstant': 'Sinazongwe'
    }

    geo = site_to_geography.get(site_splits[0], '')
    return '.'.join([geo] + site_splits[1:]) if geo else site


def set_habitat_scale(simulation, scale):
    simulation.task.set_parameter('x_Temporary_Larval_Habitat', scale)


def configure_magude(simulation):
    set_larval_habitat(simulation, {
        "gambiae": {
            'TEMPORARY_RAINFALL': 2.2e9,
            "LINEAR_SPLINE": {
                "Capacity_Distribution_Per_Year": {
                    "Times": [0.0, 30.417, 60.833, 91.25, 121.667, 152.083, 182.5, 212.917, 243.333, 273.75, 304.167, 334.583],
                    "Values": [3, 0.8, 1.25, 0.1, 2.7, 8, 4, 35, 6.8, 6.5, 2.6, 2.1]
                },
                "Max_Larval_Capacity": 1e8}
        },
        "funestus": {
            'WATER_VEGETATION': 4e8,
            "LINEAR_SPLINE": {
                "Capacity_Distribution_Per_Year": {
                    "Times": [0.0, 30.417, 60.833, 91.25, 121.667, 152.083, 182.5, 212.917, 243.333, 273.75, 304.167, 334.583],
                    "Values": [3, 0.8, 1.25, 0.1, 2.7, 8, 4, 35, 6.8, 6.5, 2.6, 2.1]
                }, "Max_Larval_Capacity": 1e8
            }
        }
    })


def configure_garki_gridded_net(simulation):
    set_larval_habitat(simulation, {"gambiae": {'TEMPORARY_RAINFALL': 2.2e9, "LINEAR_SPLINE": {
        "Capacity_Distribution_Per_Year": {
            "Times": [0.0, 30.417, 60.833, 91.25, 121.667, 152.083,
                      182.5, 212.917, 243.333, 273.75, 304.167, 334.583],
            "Values": [3, 0.8, 1.25, 0.1, 2.7, 8, 4, 35, 6.8, 6.5, 2.6, 2.1]},
        "Max_Larval_Capacity": 1e8
    }}})


# Namawala, Tanzania: EIR = 400
def configure_namawala(simulation):
    set_larval_habitat(simulation, {"arabiensis": {'TEMPORARY_RAINFALL': 7.5e9, 'CONSTANT': 1e7},
                                    "funestus": {'WATER_VEGETATION': 4e8},
                                    "gambiae": {'TEMPORARY_RAINFALL': 8.3e8, 'CONSTANT': 1e7}
                                    })


# "Puerto_Rico": Tanzania: EIR = 400
def configure_puerto_rico(simulation):
    set_larval_habitat(simulation, {"aegypti": {'TEMPORARY_RAINFALL': 1.125e10}})


# Sugungum, Garki, Jigawa, Nigeria: EIR = 132 (56 from funestus)
def configure_sugungum(simulation):
    set_larval_habitat(simulation, {"arabiensis": {'TEMPORARY_RAINFALL': 2.3e9, 'CONSTANT': 1.25e7},
                                    "funestus": {'WATER_VEGETATION': 6e8},
                                    "gambiae": {'TEMPORARY_RAINFALL': 2.3e9, 'CONSTANT': 1.25e7}})


# Matsari, Garki, Jigawa, Nigeria: EIR = 68 (2 from funestus)
def configure_matsari(simulation):
    set_larval_habitat(simulation, {"arabiensis": {'TEMPORARY_RAINFALL': 2.2e9, 'CONSTANT': 1.25e7},
                                    "funestus": {'WATER_VEGETATION': 2.5e7},
                                    "gambiae": {'TEMPORARY_RAINFALL': 2.2e9, 'CONSTANT': 1.25e7}
                                    })


# Rafin Marke, Garki, Jigawa, Nigeria: EIR = 18
def configure_rafin_marke(simulation):
    set_larval_habitat(simulation, {"arabiensis": {'TEMPORARY_RAINFALL': 5e8, 'CONSTANT': 8e6},
                                    "gambiae": {'TEMPORARY_RAINFALL': 5e8, 'CONSTANT': 8e6}
                                    })


# Dielmo, Senegal: EIR = 200
def configure_dielmo(simulation):
    set_larval_habitat(simulation, {"arabiensis": {'TEMPORARY_RAINFALL': 4e9, 'CONSTANT': 1e7},
                                    "funestus": {'WATER_VEGETATION': 5e8},
                                    "gambiae": {'TEMPORARY_RAINFALL': 4e9, 'CONSTANT': 1e7}})


# Ndiop, Senegal: EIR = 20
def configure_ndiop(simulation):
    set_larval_habitat(simulation, {"arabiensis": {'TEMPORARY_RAINFALL': 4e8, 'CONSTANT': 5e6},
                                    "gambiae": {'TEMPORARY_RAINFALL': 4e8, 'CONSTANT': 5e6}})


# Thies, Senegal
def configure_thies(simulation):
    set_larval_habitat(simulation, {"arabiensis": {'TEMPORARY_RAINFALL': 4e7, 'CONSTANT': 1.5e6},
                                    "gambiae": {'TEMPORARY_RAINFALL': 4e7, 'CONSTANT': 1.5e6}})


# Burkina sites from A L Ouedraogo
def configure_dapelogo(simulation):
    set_larval_habitat(simulation, {"funestus": {'WATER_VEGETATION': 5e8},
                                    "gambiae": {'TEMPORARY_RAINFALL': 3e10, 'CONSTANT': 1e8}})


def configure_laye(simulation):
    set_larval_habitat(simulation, {"funestus": {'WATER_VEGETATION': 5e7},
                                    "gambiae": {'TEMPORARY_RAINFALL': 3e9, 'CONSTANT': 1e7}})


# Sinazongwe, Southern, Zambia: EIR ~= 20
def configure_sinazongwe(simulation):
    set_larval_habitat(simulation, {"arabiensis": {'TEMPORARY_RAINFALL': 2e9, 'CONSTANT': 2e8}})
    set_species_param(simulation, "arabiensis", "Indoor_Feeding_Fraction", 0.5)


def configure_chipepo(simulation):
    set_larval_habitat(simulation, {"arabiensis": {'TEMPORARY_RAINFALL': 1e9, 'CONSTANT': 1e9}})
    set_species_param(simulation, "arabiensis", "Indoor_Feeding_Fraction", 0.5)


# [TODO]: Fix simulation enable call here
def configure_sinazongweconstant(simulation):
    set_larval_habitat(simulation, {"arabiensis": {'CONSTANT': 1.5e9}})
    set_species_param(simulation, "arabiensis", "Indoor_Feeding_Fraction", 0.5)
    set_climate_constant(simulation, Base_Air_Temperature=22, Base_Rainfall=10)
    simulation.enable('Climate_Stochasticity')


# Gwembe, Southern, Zambia: EIR ~= 0.1-20
def configure_gwembe2node(simulation):
    set_larval_habitat(simulation, {"arabiensis": {'TEMPORARY_RAINFALL': 2e9, 'CONSTANT': 8e7}})
    set_species_param(simulation, "arabiensis", "Indoor_Feeding_Fraction", 0.8)


# Gwembe + Sinazongwe, Southern, Zambia: EIR ~= 0.1-20
def configure_gwembesinazongwehealthfacility(simulation):
    set_larval_habitat(simulation, {"arabiensis": {'TEMPORARY_RAINFALL': 2e9, 'CONSTANT': 8e7}})
    set_species_param(simulation, "arabiensis", "Indoor_Feeding_Fraction", 0.8)


def configure_gwembesinazongwepopcluster(simulation):
    # set_larval_habitat(cb, {"arabiensis":[2e9, 8e7]})
    # set_species_param(cb,"arabiensis","Indoor_Feeding_Fraction",0.8)
    set_larval_habitat(simulation, {"arabiensis": {'TEMPORARY_RAINFALL': 2e9, 'CONSTANT': 2e8}})
    set_species_param(simulation, "arabiensis", "Indoor_Feeding_Fraction", 0.5)


def configure_sinamalima_1_node(simulation):
    set_geography(simulation, "Sinamalima_1_node")
    set_larval_habitat(simulation, {"arabiensis": {'TEMPORARY_RAINFALL': 2e9, 'CONSTANT': 2e8}})
    set_species_param(simulation, "arabiensis", "Indoor_Feeding_Fraction", 0.5)


def configure_gwembe_1_node(simulation):
    set_geography(simulation, "Gwembe_1_node")
    set_larval_habitat(simulation, {"arabiensis": {'TEMPORARY_RAINFALL': 2e9, 'CONSTANT': 2e8}})
    set_species_param(simulation, "arabiensis", "Indoor_Feeding_Fraction", 0.5)


def configure_lukonde_1_node(simulation):
    set_geography(simulation, "Lukonde_1_node")
    set_larval_habitat(simulation, {"arabiensis": {'TEMPORARY_RAINFALL': 2e9, 'CONSTANT': 2e8}})
    set_species_param(simulation, "arabiensis", "Indoor_Feeding_Fraction", 0.5)


def configure_munumbwe_1_node(simulation):
    set_geography(simulation, "Munumbwe_1_node")
    set_larval_habitat(simulation, {"arabiensis": {'TEMPORARY_RAINFALL': 2e9, 'CONSTANT': 2e8}})
    set_species_param(simulation, "arabiensis", "Indoor_Feeding_Fraction", 0.5)


# Mocuba, Zambezia, Mozambique: EIR = 70
def configure_mocuba(simulation):
    set_larval_habitat(simulation, {"arabiensis": {'TEMPORARY_RAINFALL': 1e8, 'CONSTANT': 5e6},
                                    "funestus": {'WATER_VEGETATION': 8e8}})


# West Kenya: EIR ~ 100
def configure_west_kenya(simulation):
    set_larval_habitat(simulation, {"arabiensis": {'TEMPORARY_RAINFALL': 2.2e9, 'CONSTANT': 1e7},
                                    "funestus": {'WATER_VEGETATION': 7e8},
                                    "gambiae": {'TEMPORARY_RAINFALL': 5.5e9, 'CONSTANT': 1e7}})


# Solomon_Islands
def configure_solomon_islands(simulation):
    set_larval_habitat(simulation, {"farauti": {"BRACKISH_SWAMP", 6e9}})


def configure_solomon_islands_2node(simulation):
    set_larval_habitat(simulation, {"farauti": {"BRACKISH_SWAMP", 6e9}})


# Nabang on Chinese-Burmese border
def configure_nabang(simulation):
    set_larval_habitat(simulation, {"maculatus": {"WATER_VEGETATION": 1e8},
                                    "minimus": {"WATER_VEGETATION": 1e8}})


def configure_gwembe_sinazongwe_115_nodes(simulation):
    set_geography(simulation, "Gwembe_Sinazongwe_115_nodes")

    '''
    once PIECEWISE_MONTHLY habitat is introduced we can configure it;
    set_larval_habitat(cb, {"arabiensis":{'TEMPORARY_RAINFALL': 1e8, 'CONSTANT': 2e6},
                            "funestus":[ 1e8, 2e7 ]})
    '''

    '''
    for now we only configure water vegetation
    '''
    set_larval_habitat(simulation, {"arabiensis": {'TEMPORARY_RAINFALL': 1e8, 'CONSTANT': 2e6},
                                    "funestus": {"WATER_VEGETATION": 2e7}})

    set_species_param(simulation, "arabiensis", "Indoor_Feeding_Fraction", 0.5)


# Thailand: same habitat for two species,
# but maculatus more zoophilic --> fewer human bites
def configure_tha_song_yang(simulation):
    set_larval_habitat(simulation, {"minimus": {"WATER_VEGETATION": 1e8},
                                    "maculatus": {"WATER_VEGETATION": 1e8}})
