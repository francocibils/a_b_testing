import statsmodels.stats.api as sms

def get_required_size(control_rate, desired_effect_size = 0.01, power = 0.8, alpha = 0.05):

    # Compute proportion effect size
    effect_size = sms.proportion_effectsize(control_rate, control_rate + desired_effect_size)

    # Obtain required size
    required_size = sms.NormalIndPower().solve_power(effect_size, power = power, alpha = alpha, ratio = 1)

    return round(required_size)

def get_file_type(file):
    
    if file.name.endswith(".csv"):
        return "csv"
    elif file.name.endswith(".xlsx"):
        return "xlsx"