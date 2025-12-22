# domain/degradation.py
# smoothing → thermal → degradation → forecasting → Flask

import math

def degradation_rate(product_temp, A=1e13, Ea=90000, R=8.314):
    """
    Calculate the reaction rate using the Arrhenius equation.

    Args:
        product_temp (float): product temperature in °C
        A (float): pre-exponential factor (frequency factor)
        Ea (float): activation energy (J/mol)
        R (float): gas constant (8.314 J/(mol*K))

    Returns:
        float: degradation rate (1/hour)
    """
    T_kelvin = product_temp + 273.15
    k = A * math.exp(-Ea / (R * T_kelvin))
    return k
