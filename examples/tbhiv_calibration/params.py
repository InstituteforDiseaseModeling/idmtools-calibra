exp_name="sa_baseline_dynamic.py"
nSims = 1
base_infectivity=1.0
burn_initial = 1 * 365
burn_predots = 100 * 365

dots_start = burn_initial + burn_predots
hiv_epidemic_start = dots_start - 15 * 365
art_start = hiv_epidemic_start + 21 * 365
genexpert_introduction = dots_start + 9 * 365
length_gene_xpert_ramp = 3 * 365  # PLOS one
To_end_from_DOTS = 50 * 365
# passive seeking rates
high_seek = 1.0 / (3 * 30)
low_seek = 1.0 / (7 * 30)
b_offset = dots_start / 365.0 - 2000  # ie DOTS starting in 2000
# ART introduction in 2007
seek_200 = 1.0 / (30.0)
seek_350_500 = 1.0 / (60.0)

# sensitivities PreDOTS
sens_smear_neg_pre_GL = 0.4
sens_smear_pos_pre_GL = 0.7

sens_smear_neg_pre_GH = 0.4
sens_smear_pos_pre_GH = 0.7

sens_smear_neg_GXL = 0.7
sens_smear_pos_GXL = 0.7
sens_smear_pos_GXH = 0.99
sens_smear_neg_GXH = 0.9

sens_resistance_L = 0.5
sens_resistance_H = 0.7
specificity_resistance = 1.00
sens_resistance_L_clinical = 0.5
sens_resistance_H_clinical = 0.7
specificity_resistance_clinical = 1.00

CRP_Sensitivity = 0.91
CRP_Specificity = 0.59

intervention_day = dots_start + 18.0 * 365

dots_plus_15 = dots_start + 15.0 * 365.0

parameters = [
    {
        'Name': 'Base_Infectivity_Constant',
        'Dynamic': True,
        'MapTo': 'Base_Infectivity_Constant',
        'Guess': 0.028,
        'Min': 0.013,
        'Max': 0.035
    },
    {
        'Name': 'TB_Fast_Progressor_Fraction_Adult',
        'Dynamic': True,
        'MapTo': 'TB_Fast_Progressor_Fraction_Adult',
        'Guess': 0.10,
        'Min': 0.05,
        'Max': 0.15
    },
    {
        'Name': 'TB_Slow_Progressor_Rate',
        'Dynamic': True,
        'MapTo': 'TB_Slow_Progressor_Rate',
        'Guess': 0.005 / 365.0,
        'Min': 0.002 / 365.0,
        'Max': 0.0075 / 365.0
    },
    {
        'Name': 'TB Presymptomatic Duration Years',
        'Dynamic': True,
        # 'MapTo': 'M'
        'Guess': 100.0 / 365.0,
        'Min': 30.0 / 365.0,
        'Max': 365.0 / 365.0
    },
    {
        'Name': 'TB_Active_Presymptomatic_Infectivity_Multiplier',
        'Dynamic': True,
        'MapTo': 'TB_Active_Presymptomatic_Infectivity_Multiplier',
        # This is based on a relative smear-negative of 0.34604 fixed (ok sig figs not withstanding) so
        # ranging from no infectivity to equivalent to a smear negative case at best
        'Guess': 0.34604 * 0.3318,
        'Min': 0.0,
        'Max': 0.34604
    },
    {
        'Name': 'TBHIV Duration',
        'Dynamic': True,
        # constrain to less than duration without HIV
        'Guess': 1.8,
        'Min': 1.0,
        'Max': 4
    },
    {
        'Name': 'TB Duration',
        'Dynamic': True,
        # constrain to less than duration without HIV
        'Guess': 3.5,
        'Min': 2.5,
        'Max': 4.5
    },
    {
        'Name': 'Relative TB CD4 Infectiousness',
        'Dynamic': True,
        # for parsimony not CD4 or ART dependent
        'Guess': 0.5,
        'Min': 0.1,
        'Max': 0.9
    },

    {
        'Name': 'Post_Infection_Acquisition_Multiplier',
        'Dynamic': True,
        'MapTo': 'Post_Infection_Acquisition_Multiplier',
        'Guess': 0.5,
        'Min': 0.4,
        'Max': 0.8
    },
    {
        'Name': 'CD4_aq_below_200_rel',
        'Dynamic': True,
        # first two
        'Guess': 36.0,
        'Min': 4.0,
        'Max': 60.0
    },
    {
        'Name': 'CD4_aq_200_300_rel',
        'Dynamic': True,
        # third
        'Guess': 14.0,
        'Min': 3.0,
        'Max': 50.0
    },
    {
        'Name': 'CD4_aq_300_400_rel',
        'Dynamic': True,
        # fourth
        'Guess': 12.0,
        'Min': 2.0,
        'Max': 50.0
    },
    {
        'Name': 'CD4_aq_400_500_rel',
        'Dynamic': True,
        # fifth
        'Guess': 2.0,
        'Min': 1.0,
        'Max': 23.0
    },
    {
        'Name': 'CD4_aq_above_500',
        'Dynamic': True,
        # six and 7th (for now 7th is really superfluous in future, but for compatibility)
        'Guess': 1.1,
        'Min': 1.0,
        'Max': 4.0
    },
    {
        'Name': 'Primary HIV multiplier',
        'Dynamic': True,
        # for now
        'Guess': 2.0,
        'Min': 1.0,
        'Max': 4.0
    },
    {
        'Name': 'Death Fraction',
        'Dynamic': True,
        # for now
        'Guess': 0.6,
        'Min': 0.4,
        'Max': 0.7
    },
    {
        'Name': 'ART Factor',
        'Dynamic': True,
        # coinfection death scalar, 0 is like no HIV, 1 like HIV with no ART
        'Guess': 0.7,
        'Min': 0.0,
        'Max': 1.0
    },

    {
        'Name': 'Care Seeking Slow Duration Days',
        'Dynamic': True,
        # for now
        'Guess': 250.0,
        'Min': 90.0,
        'Max': 725.0
    },

    {
        'Name': 'Care Seeking Fast Duration Days',
        'Dynamic': True,
        # for now
        'Guess': 90.0,
        'Min': 30.0,
        'Max': 180.0
    },

]