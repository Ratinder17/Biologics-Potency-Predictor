# domain/degradation.py
# smoothing → thermal → degradation → forecasting → Flask

import math

def degradation_rate(product_temp, A=1e13, Ea=90000):
    """
    Calculate the reaction rate using the Arrhenius equation.

    Args:
        product_temp (float): Product temperature in °C
        A (float): Pre-exponential factor (frequency factor)
        Ea (float): Activation energy (J/mol)

    Constants:
        R (float): Gas constant (8.314 J/(mol*K))

    Returns:
        float: Degradation rate (1/hour)
    """
    R = 8.314
    T_kelvin = product_temp + 273.15

    k = A * math.exp(-Ea / (R * T_kelvin))
    return k
