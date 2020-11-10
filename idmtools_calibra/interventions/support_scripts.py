
def validate_distribution_dictionary(parameter: str = None, distribution_dictionary: dict = None):

    """
        Validates that the distribution dictionary passed in contains all the parameters needed to define a valid
        distribution
    Args:
        parameter: Parameter for which we are looking at a valid distribution
            Examples: "Duration_At_Node", "Expiration_Period", "Duration_Before_Leaving"
        distribution_dictionary: a dictionary that defines a distribution
            Examples: {"Expiration_Period_Distribution": "EXPONENTIAL_DISTRIBUTION",
                    "Expiration_Period_Exponential": 14}
    Returns:
        Raises ValueError if not all parameters needed are found

    """
    if not parameter or not distribution_dictionary:
        raise ValueError("Both parameter and distribution dictionary need to be present for validation.\n")

    validated = False
    constant_dist = [f"{parameter}_Distribution", f"{parameter}_Constant"]
    uniform_dist = [f"{parameter}_Distribution", f"{parameter}_Max ", f"{parameter}_Min"]
    gaussian_dist = [f"{parameter}_Distribution", f"{parameter}_Gaussian_Mean", f"{parameter}_Gaussian_Std_Dev"]
    exponential_dist = [f"{parameter}_Distribution", f"{parameter}_Exponential"]
    weibull_dist = [f"{parameter}_Distribution", f"{parameter}_Kappa", f"{parameter}_Lambda"]
    log_normal_dist = [f"{parameter}_Distribution", f"{parameter}_Log_Normal_Mu",
                       f"{parameter}_Log_Normal_Sigma"]
    poisson_dist = [f"{parameter}_Distribution", f"{parameter}_Poisson_Mean"]
    dual_constant_dist = [f"{parameter}_Distribution", f"{parameter}_0", "Peak_2_Value"]
    dual_exponential_dist = [f"{parameter}_Distribution", f"{parameter}_Mean_1", f"{parameter}_Mean_2",
                             f"{parameter}_Proportion_1"]
    distributions = [constant_dist, uniform_dist, gaussian_dist, exponential_dist, weibull_dist,
                     log_normal_dist, poisson_dist, dual_constant_dist, dual_exponential_dist]

    for distribution in distributions:
        if all([k in distribution_dictionary for k in distribution]):
            validated = True

    if not validated:
        error = f"Please verify that the distribution dictionary for {parameter} has all parameters " \
            f"present needed to define a distribution.\n"
        raise ValueError(error)

