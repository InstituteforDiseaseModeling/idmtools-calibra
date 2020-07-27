params = {
    "Anemia_Mortality_Inverse_Width": 1,
    "Anemia_Mortality_Threshold": 0.654726662830038,
    "Anemia_Severe_Inverse_Width": 10,
    "Anemia_Severe_Threshold": 4.50775824973078,

    "Fever_Mortality_Inverse_Width": 1895.51971624351,
    "Fever_Mortality_Threshold": 3.4005008555391,
    "Fever_Severe_Inverse_Width": 27.5653580403806,
    "Fever_Severe_Threshold": 3.98354299722192,

    "Parasite_Mortality_Inverse_Width": 327.51594505874,
    "Parasite_Mortality_Threshold": 10**5.93,
    "Parasite_Severe_Inverse_Width": 56.5754896048744,
    "Parasite_Severe_Threshold": 10**5.929945527,

    "Clinical_Fever_Threshold_High": 1.5,
    "Clinical_Fever_Threshold_Low": 0.5,
    "Min_Days_Between_Clinical_Incidents": 14,

    # updated from mambrose Oct 11 2019, personal communication with M Plucinski
    "PfHRP2_Boost_Rate": 0.018,  # original value: 0.07
    "PfHRP2_Decay_Rate": 0.167,  # original value: 0.172

    "Report_Detection_Threshold_Blood_Smear_Gametocytes": 20,
    "Report_Detection_Threshold_Blood_Smear_Parasites": 20,
    "Report_Detection_Threshold_Fever": 1.0,
    "Report_Detection_Threshold_PCR_Gametocytes": 0.05,
    "Report_Detection_Threshold_PCR_Parasites": 0.05,
    "Report_Detection_Threshold_PfHRP2": 5.0,
    "Report_Detection_Threshold_True_Parasite_Density": 0.0,

    "Gametocyte_Smear_Sensitivity": 0.1,
    "Parasite_Smear_Sensitivity": 0.1,  # 10/uL

    # params obsolete in Jan 2018 DTK update of MalariaDiagnostic
    "Fever_Detection_Threshold": 1,
    "PCR_Sensitivity": 20,  # 0.05/uL
    "RDT_Sensitivity": 0.01,  # 100/uL
    "New_Diagnostic_Sensitivity": 0.025,  # 40/uL
}
