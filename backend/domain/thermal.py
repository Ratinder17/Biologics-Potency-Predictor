# domain/thermal.py
# What does this sensor temperature mean for the product? from smoothing.py
# smoothing → thermal → degradation → forecasting → Flask
import math

def update_product_temperature(prev_product_temp,sensor_temp,delta_hours,k=0.25):
    if delta_hours < 0:
        raise ValueError("dt_hours must be non-negative")
    
    return sensor_temp + (prev_product_temp - sensor_temp) * math.exp(-k * delta_hours)

"""
k - thermal agility of the product— how easily it exchanges heat with its environment. 
Higher k -> higher sensitivity to external environment

Update product temperature using Newton’s law of cooling (exact discrete form).

Model (continuous):
    dT/dt = k * (T_sensor - T_product)

Exact discrete solution (assuming T_sensor is constant over dt):
    T_new = T_sensor + (T_prev - T_sensor) * exp(-k * dt)

Args:
    prev_product_temp (float): Product temperature at the previous time step (°C)
    sensor_temp (float): Ambient / sensor temperature during this interval (°C)
    delta_hours (float): Time step duration in hours
    k (float): Effective thermal response constant (1/hour),
               representing packaging, thermal mass, and insulation

Returns:
    float: Updated product temperature after delta_hours

Notes:
    - This is the exact solution of Newton’s law of cooling over a finite time step.
    - Temperature evolves smoothly toward the sensor temperature without overshoot.
    - Smaller k values indicate stronger insulation / higher thermal inertia.
    - Larger k values indicate faster thermal equilibration with the environment.

    """