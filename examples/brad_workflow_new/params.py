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