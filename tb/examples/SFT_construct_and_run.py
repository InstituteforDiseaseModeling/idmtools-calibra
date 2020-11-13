from dtk.utils.core.DTKConfigBuilder import DTKConfigBuilder
from simtools.ExperimentManager.ExperimentManagerFactory import ExperimentManagerFactory
from simtools.ModBuilder import ModBuilder, ModFn
from dtk.utils.builders.sweep import GenericSweepBuilder
from simtools.SetupParser import SetupParser
from tb.TBCustomReports import *
from tb.add_tbhiv_treat import add_tbhiv_treat
from tb.add_ActiveDiagnostic import add_ActiveDiagnostic
from tb.add_HIVIncidence import add_HIVIncidence
from tb.add_DiagnosticTreatNeg import add_DiagnosticTreatNeg
from tb.add_SimpleHealthSeeking import add_SimpleHealthSeeking
from tb.add_Ramp_DiagnosticTreatNeg import add_Ramp_DiagnosticTreatNeg
from tb.add_cd4diagnostic import add_cd4diagnostic
from tb.add_art import add_art
from tb.add_ResistanceDiagnostic import add_ResistanceDiagnostic
from tb.add_tb_drug_type import add_tb_drug_type
from tb.add_tbhiv_outbreak import add_tbhiv_outbreak
from tb.add_simplehivdiagnostic import add_simplehivdiagnostic
from tb.utils.TB_LL_calculators import *
from tb.utils.TBCustomReports import add_tb_report
from tb.add_SubClinicalTBTest import add_SubClinicalTBTest
from tb.add_BCG import add_BCG
from tb.add_SimpleVaccine import add_SimpleVaccine
from tb.add_import_tb_outbreak import add_tb_import_outbreak
import os


def SFT_write_file(name, content):
    filename = os.path.join(os.getcwd(),exp_name, name,'%s' % content)
    with open(filename, 'w') as f:
        f.write(content)

def write_file(name, content):
    file_dir = os.path.join(os.getcwd(), exp_name)
    if not os.path.exists(file_dir):
        os.mkdir(file_dir)
    filename = os.path.join(file_dir, '%s' % name)
    with open(filename, 'w') as f:
        f.write(content)

write_local = True
# Set the default configuration block to HPC (we will run on COMPS)
SetupParser.default_block = 'HPC'

case_bases = {'Diagnostics': ['MDR','Active_Smear_Pos','Active_Smear_Neg','All_Active'],
              'Immunity': ['BCG','Natural_Immunity','Natural_Immunity_Decay'],
              'MDR': ['Outbreak', 'Transmit_No_MDR'],
              'SEIR': ['Cure','Death','PreSymptomatic','Latent_Slow','Fast_Progress_HIV','PreSymptomatic_Cure', 'Latent_Cure']}

def setRunNumber(cb, run):
    cb.set_param('Run_Number',run)
    return {'Run_Number': run}



        # Create a default ConfigBuilder
cb = DTKConfigBuilder.from_defaults('TBHIV_SIM')


def CreateSFT(cb,case_base, case_sub):

        cb.set_param('Listed_Events', ['Blackout', 'TBTestPreDOTSLow','TBTestPreDOTSHigh','TBDS_Positive',
                                       'TBTestDOTSHigh', 'TBTestDOTSLow'],)
        # set underlying parameters
        cb.set_param('Base_Population_Scale_Factor', 10000)
        cb.set_param('Simulation_Timestep', 1)
        cb.set_param('CoInfection_Mortality_Rate_Off_ART', 0)
        cb.set_param('CoInfection_Mortality_Rate_On_ART', 0)

        #Mofidy base params a bit
        cb.update_params({'Base_Infectivity': 0.026570,'TB_Smear_Negative_Infectivity_Multiplier': 0.34604, 'TB_Presymptomatic_Rate': 0.01165,'TB_Active_Presymptomatic_Infectivity_Multiplier':0.34604*0.3318}, validate=True)


        cb.set_param('x_Other_Mortality', 0)  #turn off birth via scaling for now
        cb.set_param('x_Birth', 0)

        if case_base == 'MDR':
            if case_sub == 'Outbreak':
                add_tbhiv_outbreak(cb, 1.0, 'TB',start_day= 1, genome= 1)  #check we actually oubreak MDR

            if case_sub == 'Transmit_No_MDR':   # Tests fitness cost should be no transmission after outbreak
                add_tbhiv_outbreak(cb, 0.1, 'TB', start_day=1, genome=1)  # check we actually oubreak MDR

                cb.update_params({'Base_Infectivity': 0.0274, 'TB_Smear_Negative_Infectivity_Multiplier': 1.0,
                                  'TB_Presymptomatic_Rate': 1.0,
                                  'TB_Active_Presymptomatic_Infectivity_Multiplier': 1, 'TB_Fast_Progressor_Fraction_Adult': 1.0,
                'TB_Fast_Progressor_Fraction_Child': 1.0,
                "TB_Fast_Progressor_Rate": 1.0, 'TB_MDR_Fitness_Multiplier': 0}, validate=True)

        if case_base == 'Diagnostics':
            if case_sub == 'Active_Smear_Neg':   #should be 25%% TBTestPositive 25% TBTestNegative 0 dropout
                add_tbhiv_outbreak(cb, 1.0, 'TB', start_day=1, genome=0)
                cb.update_params({'Base_Infectivity': 0, 'TB_Smear_Negative_Infectivity_Multiplier': 1.0,
                                  'TB_Presymptomatic_Rate': 1.0,
                                  'TB_Active_Presymptomatic_Infectivity_Multiplier': 1,
                                  'TB_Fast_Progressor_Fraction_Adult': 1.0,
                                  'TB_Fast_Progressor_Fraction_Child': 1.0,
                                  "TB_Fast_Progressor_Rate": 1.0,
                                  'TB_Extrapulmonary_Fraction_Adult': 0.5,
                                  'TB_Extrapulmonary_Fraction_Child': 0.5,
                                  'TB_Smear_Positive_Fraction_Adult': 0,
                                  'TB_Smear_Positive_Fraction_Child': 0,
                                  },validate=True)
                add_DiagnosticTreatNeg(cb, ['TBActivation'],0 , 0.5,
                                       treatment_fraction=1.0, start_day=0, duration=-1 )
            if case_sub == 'Active_Smear_Pos':  # should be 25%% TBTestPositive 25% TBTestNegative 0 dropout
                add_tbhiv_outbreak(cb, 1.0, 'TB', start_day=1, genome=0)
                cb.update_params({'Base_Infectivity': 0, 'TB_Smear_Negative_Infectivity_Multiplier': 1.0,
                                  'TB_Presymptomatic_Rate': 1.0,
                                  'TB_Active_Presymptomatic_Infectivity_Multiplier': 1,
                                  'TB_Fast_Progressor_Fraction_Adult': 1.0,
                                  'TB_Fast_Progressor_Fraction_Child': 1.0,
                                  "TB_Fast_Progressor_Rate": 1.0,
                                  'TB_Extrapulmonary_Fraction_Adult': 0,
                                  'TB_Extrapulmonary_Fraction_Child': 0,
                                  'TB_Smear_Positive_Fraction_Adult': 1.0,
                                  'TB_Smear_Positive_Fraction_Child': 1.0,
                                  }, validate=True)
                add_DiagnosticTreatNeg(cb, ['TBActivation'], 0.5, 1.0,
                                       treatment_fraction=0.8, start_day=0, duration=-1)

            if case_sub == 'All_Active':
                add_tbhiv_outbreak(cb, 1.0, 'TB', start_day=0, genome=0)
                cb.update_params({'Base_Infectivity': 0, 'TB_Smear_Negative_Infectivity_Multiplier': 1.0,
                                  'TB_Presymptomatic_Rate': 1.0,
                                  'TB_Active_Presymptomatic_Infectivity_Multiplier': 1,
                                  'TB_Fast_Progressor_Fraction_Adult': 1.0,
                                  'TB_Fast_Progressor_Fraction_Child': 1.0,
                                  "TB_Fast_Progressor_Rate": 1.0,
                                  'TB_Extrapulmonary_Fraction_Adult': 0,
                                  'TB_Extrapulmonary_Fraction_Child': 0,
                                  'TB_Smear_Positive_Fraction_Adult': 1.0,
                                  'TB_Smear_Positive_Fraction_Child': 1.0,
                                  }, validate=True)
                add_ActiveDiagnostic(cb,['TBActivation'], 0.5, 1.0, treatment_fraction= 0.8, start_day= 0)

            if case_sub == 'MDR' :
                add_tbhiv_outbreak(cb, 1.0, 'TB', start_day=0, genome=1, antigen=0)
                cb.update_params({'Base_Infectivity': 0, 'TB_Smear_Negative_Infectivity_Multiplier': 1.0,
                                  'TB_Presymptomatic_Rate': 1.0,
                                  'TB_Active_Presymptomatic_Infectivity_Multiplier': 1,
                                  'TB_Fast_Progressor_Fraction_Adult': 1.0,
                                  'TB_Fast_Progressor_Fraction_Child': 1.0,
                                  "TB_Fast_Progressor_Rate": 1.0,
                                  'TB_Extrapulmonary_Fraction_Adult': 0,
                                  'TB_Extrapulmonary_Fraction_Child': 0,
                                  'TB_Smear_Positive_Fraction_Adult': 1.0,
                                  'TB_Smear_Positive_Fraction_Child': 1.0,
                                  }, validate=True)
                add_ResistanceDiagnostic(cb,['TBActivation'],0.7,1.0, treatment_fraction= 0.7, treatment_fraction_negative_test= 0.9, start_day= 0)


        if case_base == 'Immunity':
            if case_sub == 'BCG':
                add_SimpleVaccine(cb,['HappyBirthday'],1.0,vtype= 'TransmissionBlocking',box_duration= 1000, start_day= 0)
                add_BCG(cb,['HappyBirthday'], 0.5,age_take_decay= 0, box_duration= 1000, start_day= 0, duration = 365)
                add_tb_import_outbreak(cb, numcases= 1, start_day= 366)
                base_tmp = 10.0/365.0
                cb.update_params({'Base_Infectivity': base_tmp, 'TB_Smear_Negative_Infectivity_Multiplier': 1.0,
                                  'TB_Presymptomatic_Rate': 1.0,
                                  'TB_Active_Presymptomatic_Infectivity_Multiplier': 1,
                                  'TB_Fast_Progressor_Fraction_Adult': 1.0,
                                  'TB_Fast_Progressor_Fraction_Child': 1.0,
                                  "TB_Fast_Progressor_Rate": 1.0,
                                  'TB_Extrapulmonary_Fraction_Adult': 0,
                                  'TB_Extrapulmonary_Fraction_Child': 0,
                                  'TB_Smear_Positive_Fraction_Adult': 1.0,
                                  'TB_Smear_Positive_Fraction_Child': 1.0,
                                  'TB_Immune_Loss_Fraction': 1.0,
                                  'Immunity_Acquisition_Factor': 1.0,
                                  'Enable_Immunity': 1,
                                  'Enable_Immune_Decay': 0,
                                  'TB_Active_Mortality_Rate': 0
                                  }, validate=True)


            if case_sub == 'Natural_Immunity':
                     add_SimpleVaccine(cb, ['HappyBirthday'], 1.0, vtype='TransmissionBlocking', box_duration=1000,
                                          start_day=0, duration=365)
                     add_tbhiv_outbreak(cb,1.0,'TB', start_day=365)
                     add_tb_drug_type(cb, 'Full_Clear', 10, 0.99, 0, 0, 0, 0)
                     add_tbhiv_treat(cb,'Full_Clear',['TBActivation'], start_day=365, duration=10)

                     add_tb_import_outbreak(cb, numcases=1, start_day=375)
                     base_tmp = 10.0 / 365.0
                     cb.update_params({'Base_Infectivity': base_tmp, 'TB_Smear_Negative_Infectivity_Multiplier': 1.0,
                                          'TB_Presymptomatic_Rate': 1.0,
                                          'TB_Active_Presymptomatic_Infectivity_Multiplier': 1,
                                          'TB_Fast_Progressor_Fraction_Adult': 1.0,
                                          'TB_Fast_Progressor_Fraction_Child': 1.0,
                                          "TB_Fast_Progressor_Rate": 1.0,
                                          'TB_Extrapulmonary_Fraction_Adult': 0,
                                          'TB_Extrapulmonary_Fraction_Child': 0,
                                          'TB_Smear_Positive_Fraction_Adult': 1.0,
                                          'TB_Smear_Positive_Fraction_Child': 1.0,
                                          'TB_Immune_Loss_Fraction': 1.0,
                                          'Immunity_Acquisition_Factor': 0.5,
                                          'Enable_Immunity': 1,
                                          'Enable_Immune_Decay': 0,
                                          'TB_Active_Mortality_Rate': 0
                                           }, validate=True)

            if case_sub == 'Natural_Immunity_Decay':
                    add_SimpleVaccine(cb, ['HappyBirthday'], 1.0, vtype='TransmissionBlocking', box_duration=1000,
                                      start_day=0, duration=365)
                    add_tbhiv_outbreak(cb, 1.0, 'TB', start_day=365)
                    add_tb_drug_type(cb, 'Full_Clear', 10, 0.99, 0, 0, 0, 0)
                    add_tbhiv_treat(cb, 'Full_Clear', ['TBActivation'], start_day=365, duration=10)

                    add_tb_import_outbreak(cb, numcases=1, start_day=375)
                    base_tmp = 10.0 / 365.0
                    cb.update_params({'Base_Infectivity': base_tmp, 'TB_Smear_Negative_Infectivity_Multiplier': 1.0,
                                      'TB_Presymptomatic_Rate': 1.0,
                                      'TB_Active_Presymptomatic_Infectivity_Multiplier': 1,
                                      'TB_Fast_Progressor_Fraction_Adult': 1.0,
                                      'TB_Fast_Progressor_Fraction_Child': 1.0,
                                      "TB_Fast_Progressor_Rate": 1.0,
                                      'TB_Extrapulmonary_Fraction_Adult': 0,
                                      'TB_Extrapulmonary_Fraction_Child': 0,
                                      'TB_Smear_Positive_Fraction_Adult': 1.0,
                                      'TB_Smear_Positive_Fraction_Child': 1.0,
                                      'TB_Immune_Loss_Fraction': 1.0,
                                      'Immunity_Acquisition_Factor': 0.5,
                                      'Enable_Immunity': 1,
                                      'Enable_Immune_Decay': 1,
                                      'TB_Active_Mortality_Rate': 0,
                                      'Acquisition_Blocking_Immunity_Decay_Rate': 100
                                      }, validate=True)

        if case_base == 'SEIR':
            if case_sub == 'Cure':
                        base_tmp = 0.0
                        cure_rate = 1.0/365.0
                        add_tbhiv_outbreak(cb, 1.0, 'TB', start_day=1, genome=0)
                        cb.update_params({'Base_Infectivity': base_tmp, 'TB_Smear_Negative_Infectivity_Multiplier': 1.0,
                                          'TB_Presymptomatic_Rate': 1.0,
                                          'TB_Active_Presymptomatic_Infectivity_Multiplier': 1,
                                          'TB_Fast_Progressor_Fraction_Adult': 1.0,
                                          'TB_Fast_Progressor_Fraction_Child': 1.0,
                                          "TB_Fast_Progressor_Rate": 1.0,
                                          'TB_Extrapulmonary_Fraction_Adult': 0,
                                          'TB_Extrapulmonary_Fraction_Child': 0,
                                          'TB_Smear_Positive_Fraction_Adult': 1.0,
                                          'TB_Smear_Positive_Fraction_Child': 1.0,
                                          'TB_Immune_Loss_Fraction': 1.0,
                                          'Immunity_Acquisition_Factor': 1.0,
                                          'Enable_Immunity': 1,
                                          'Enable_Immune_Decay': 0,
                                          'TB_Active_Mortality_Rate': 0,
                                          'TB_Active_Cure_Rate': cure_rate
                                          }, validate=True)
            if case_sub == 'Death':
                        base_tmp = 0.0
                        death_rate = 1.0
                        add_tbhiv_outbreak(cb, 1.0, 'TB', start_day=1, genome=0)
                        cb.update_params({'Base_Infectivity': base_tmp, 'TB_Smear_Negative_Infectivity_Multiplier': 1.0,
                                          'TB_Presymptomatic_Rate': 1.0,
                                          'TB_Active_Presymptomatic_Infectivity_Multiplier': 1,
                                          'TB_Fast_Progressor_Fraction_Adult': 1.0,
                                          'TB_Fast_Progressor_Fraction_Child': 1.0,
                                          "TB_Fast_Progressor_Rate": 1.0,
                                          'TB_Extrapulmonary_Fraction_Adult': 0,
                                          'TB_Extrapulmonary_Fraction_Child': 0,
                                          'TB_Smear_Positive_Fraction_Adult': 1.0,
                                          'TB_Smear_Positive_Fraction_Child': 1.0,
                                          'TB_Immune_Loss_Fraction': 1.0,
                                          'Immunity_Acquisition_Factor': 1.0,
                                          'Enable_Immunity': 1,
                                          'Enable_Immune_Decay': 0,
                                          'TB_Active_Mortality_Rate': death_rate,
                                          'TB_Active_Cure_Rate': 0
                                          }, validate=True)

            if case_sub == 'PreSymptomatic':
                        base_tmp = 0.0
                        presymp_rate = 1.0/365.0
                        add_tbhiv_outbreak(cb, 1.0, 'TB', start_day=1, genome=0)
                        cb.update_params({'Base_Infectivity': base_tmp, 'TB_Smear_Negative_Infectivity_Multiplier': 1.0,
                                          'TB_Presymptomatic_Rate': presymp_rate,
                                          'TB_Active_Presymptomatic_Infectivity_Multiplier': 1,
                                          'TB_Fast_Progressor_Fraction_Adult': 1.0,
                                          'TB_Fast_Progressor_Fraction_Child': 1.0,
                                          "TB_Fast_Progressor_Rate": 1.0,
                                          'TB_Extrapulmonary_Fraction_Adult': 0,
                                          'TB_Extrapulmonary_Fraction_Child': 0,
                                          'TB_Smear_Positive_Fraction_Adult': 1.0,
                                          'TB_Smear_Positive_Fraction_Child': 1.0,
                                          'TB_Immune_Loss_Fraction': 1.0,
                                          'Immunity_Acquisition_Factor': 1.0,
                                          'Enable_Immunity': 1,
                                          'Enable_Immune_Decay': 0,
                                          'TB_Active_Mortality_Rate': 1e-6,                # lets not draw infinity on time til next event
                                          'TB_Active_Cure_Rate': 0
                                          }, validate=True)

            if case_sub == 'Latent_Slow':
                        base_tmp = 0.0
                        test_rate = 1.0 / 365.0
                        add_tbhiv_outbreak(cb, 1.0, 'TB', start_day=1, genome=0)
                        cb.update_params({'Base_Infectivity': base_tmp, 'TB_Smear_Negative_Infectivity_Multiplier': 1.0,
                                          'TB_Presymptomatic_Rate': 1.0,
                                          'TB_Active_Presymptomatic_Infectivity_Multiplier': 1,
                                          'TB_Fast_Progressor_Fraction_Adult': 0,
                                          'TB_Fast_Progressor_Fraction_Child': 0,
                                          "TB_Fast_Progressor_Rate": 1.0,
                                          'TB_Extrapulmonary_Fraction_Adult': 0,
                                          'TB_Extrapulmonary_Fraction_Child': 0,
                                          'TB_Smear_Positive_Fraction_Adult': 1.0,
                                          'TB_Smear_Positive_Fraction_Child': 1.0,
                                          'TB_Immune_Loss_Fraction': 1.0,
                                          'Immunity_Acquisition_Factor': 1.0,
                                          'Enable_Immunity': 1,
                                          'Enable_Immune_Decay': 0,
                                          'TB_Active_Mortality_Rate': 1e-6,  # lets not draw infinity on time til next event
                                          'TB_Active_Cure_Rate': 0,
                                          "TB_Slow_Progressor_Rate": test_rate
                                          }, validate=True)

            if case_sub == 'Fast_Progress_HIV':
                        base_tmp = 0.0
                        test_rate= 1e-9
                        add_tbhiv_outbreak(cb, 1.0, 'TB', start_day=2, genome=0)
                        add_tbhiv_outbreak(cb,1.0, 'HIV', start_day =0, genome=0 )
                        cb.update_params({'Base_Infectivity': base_tmp, 'TB_Smear_Negative_Infectivity_Multiplier': 1.0,
                                          'TB_Presymptomatic_Rate': 1.0,
                                          'TB_Active_Presymptomatic_Infectivity_Multiplier': 1,
                                          'TB_Fast_Progressor_Fraction_Adult': 0.25,
                                          'TB_Fast_Progressor_Fraction_Child': 0.25,
                                          "TB_Fast_Progressor_Rate": 1.0,
                                          'TB_Extrapulmonary_Fraction_Adult': 0,
                                          'TB_Extrapulmonary_Fraction_Child': 0,
                                          'TB_Smear_Positive_Fraction_Adult': 1.0,
                                          'TB_Smear_Positive_Fraction_Child': 1.0,
                                          'TB_Immune_Loss_Fraction': 1.0,
                                          'Immunity_Acquisition_Factor': 1.0,
                                          'Enable_Immunity': 1,
                                          'Enable_Immune_Decay': 0,
                                          'TB_Active_Mortality_Rate': 1e-6,  # lets not draw infinity on time til next event
                                          'TB_Active_Cure_Rate': 0,
                                          "TB_CD4_Activation_Vector": [5e-7, 5e-7, 2.6e-7, 1.7e-7, 1.4e-7, 2.8e-7, 2.8e-7],
                                          'TB_CD4_Primary_Progression': [2,2,2,2,2,2,2],
                                          'TB_Slow_Progressor_Rate': test_rate
                                          }, validate=True)

            if case_sub == 'PreSymptomatic_Cure':
                        base_tmp = 0.0
                        test_rate = 1.0/365.0
                        add_tbhiv_outbreak(cb, 1.0, 'TB', start_day=2, genome=0)
                        add_tbhiv_outbreak(cb, 1.0, 'HIV', start_day=0, genome=0)
                        cb.update_params({'Base_Infectivity': base_tmp, 'TB_Smear_Negative_Infectivity_Multiplier': 1.0,
                                          'TB_Presymptomatic_Rate': 1e-9,
                                          'TB_Active_Presymptomatic_Infectivity_Multiplier': 1,
                                          'TB_Fast_Progressor_Fraction_Adult': 1.0,
                                          'TB_Fast_Progressor_Fraction_Child': 1.0,
                                          "TB_Fast_Progressor_Rate": 1.0,
                                          'TB_Extrapulmonary_Fraction_Adult': 0,
                                          'TB_Extrapulmonary_Fraction_Child': 0,
                                          'TB_Smear_Positive_Fraction_Adult': 1.0,
                                          'TB_Smear_Positive_Fraction_Child': 1.0,
                                          'TB_Immune_Loss_Fraction': 1.0,
                                          'Immunity_Acquisition_Factor': 1.0,
                                          'Enable_Immunity': 1,
                                          'Enable_Immune_Decay': 0,
                                          'TB_Active_Mortality_Rate': 1e-6,  # lets not draw infinity on time til next event
                                          'TB_Active_Cure_Rate': 0,
                                          "TB_Presymptomatic_Cure_Rate": test_rate
                                          }, validate=True)

            if case_sub == 'Latent_Cure':
                        base_tmp = 0.0
                        test_rate = 1.0 / 365.0
                        add_tbhiv_outbreak(cb, 1.0, 'TB', start_day=2, genome=0)
                        add_tbhiv_outbreak(cb, 1.0, 'HIV', start_day=0, genome=0)
                        cb.update_params({'Base_Infectivity': base_tmp, 'TB_Smear_Negative_Infectivity_Multiplier': 1.0,
                                          'TB_Presymptomatic_Rate': 1e-9,
                                          'TB_Active_Presymptomatic_Infectivity_Multiplier': 1,
                                          'TB_Fast_Progressor_Fraction_Adult': 1.0,
                                          'TB_Fast_Progressor_Fraction_Child': 1.0,
                                          "TB_Fast_Progressor_Rate": 1e-9,
                                          'TB_Extrapulmonary_Fraction_Adult': 0,
                                          'TB_Extrapulmonary_Fraction_Child': 0,
                                          'TB_Smear_Positive_Fraction_Adult': 1.0,
                                          'TB_Smear_Positive_Fraction_Child': 1.0,
                                          'TB_Immune_Loss_Fraction': 1.0,
                                          'Immunity_Acquisition_Factor': 1.0,
                                          'Enable_Immunity': 1,
                                          'Enable_Immune_Decay': 0,
                                          'TB_Active_Mortality_Rate': 1e-6,  # lets not draw infinity on time til next event
                                          'TB_Active_Cure_Rate': 0,
                                          "TB_Latent_Cure_Rate": test_rate
                                          }, validate=True)


        builder.tags.update({'Simulation_Duration': cb.get_param('Simulation_Duration')})
        builder.tags.update({'Base_Infectivity': cb.get_param('Base_Infectivity')})
        builder.tags.update({'Simulation_Timestep': cb.get_param('Simulation_Timestep')})


        cb.update_params({'Simulation_Duration': 730}, validate= True)
        add_tb_report(cb,type='Report_TBHIV_ByAge', stop_year= 200)
        return {'SFT': (case_base, case_sub)}




builder = ModBuilder.from_combos([ModFn(setRunNumber, g) for g in range(0, 1)],
                                         [ModFn(CreateSFT, v, k) for v in case_bases.keys() for k in case_bases.get(v)]
                                        )

exp_name = 'SFTS_TB(HIV)_All'
run_sim_args = {
'exp_name': exp_name,
'config_builder': cb,
'exp_builder': builder
        }

if __name__ == "__main__":
        SetupParser.init()
        exp_manager = ExperimentManagerFactory.from_cb(cb)
        exp_manager.run_simulations(**run_sim_args)

