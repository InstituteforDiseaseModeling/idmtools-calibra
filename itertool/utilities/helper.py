max_exp_name_len = 255

def validate_exp_name(exp_name):
    if len(exp_name) > max_exp_name_len:
        print(
            "The experiment name '%s' exceeds the max length %d (%d), please adjust your experiment name. Exiting..." %
            (exp_name, max_exp_name_len, len(exp_name)))
        return False
    else:
        return True