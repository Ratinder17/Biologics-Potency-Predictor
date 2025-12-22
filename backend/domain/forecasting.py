# domain/forecasting.py
# smoothing → thermal → degradation → forecasting → Flask


# domain/forecasting.py

import numpy as np

def forecast_future_temps(recent_temps, hours):
    """
    Predict future product temperatures using a linear trend.

    Args:
        recent_temps (list of float): last few smoothed or product temps
        hours_ahead (int): number of hours to predict

    Returns:
        list of float: predicted temperatures
    """
    x = np.arange(len(recent_temps))
    y = recent_temps
    if len(x) > 1:
        slope = np.polyfit(x, y, 1)[0]
    else:
        slope = 0.0
    last_temp = recent_temps[-1]
    return [last_temp + slope * (i + 1) for i in range(hours)]
