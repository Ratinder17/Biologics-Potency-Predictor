import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

# ----------------------------
# CONFIGURATION
# ----------------------------
output_file = "data/minute_weather.csv"
num_minutes = 24 * 60  # 1 day of data, minute-level
start_time = datetime(2024, 1, 1, 0, 0)
np.random.seed(42)

# Base air temp (simulate storage room ~2-8°C for insulin)
base_temp = 5.0  # Celsius
temp_fluctuation = 0.5  # ±0.5°C short-term fluctuations
daily_variation = 1.0  # ±1°C daily drift

# Other weather parameters (random but plausible)
air_pressure_base = 1013.25  # hPa
humidity_base = 50.0  # %
wind_speed_base = 2.0  # m/s

# ----------------------------
# GENERATE DATA
# ----------------------------
timestamps = [start_time + timedelta(minutes=i) for i in range(num_minutes)]

# Sensor air temperature with daily pattern + random noise
air_temps = []
for i in range(num_minutes):
    # Simulate slow daily trend (e.g., room warms slightly during day)
    daily_cycle = daily_variation * np.sin(2 * np.pi * i / (24 * 60))
    noise = np.random.normal(0, temp_fluctuation)
    air_temp = base_temp + daily_cycle + noise
    air_temps.append(round(air_temp, 2))

# Other synthetic columns
air_pressure = [round(air_pressure_base + np.random.normal(0, 0.5), 2) for _ in range(num_minutes)]
humidity = [round(humidity_base + np.random.normal(0, 5), 2) for _ in range(num_minutes)]
avg_wind_speed = [round(wind_speed_base + np.random.normal(0, 0.5), 2) for _ in range(num_minutes)]
max_wind_speed = [round(s + np.random.uniform(0, 1), 2) for s in avg_wind_speed]
min_wind_speed = [round(s - np.random.uniform(0, 1), 2) for s in avg_wind_speed]
avg_wind_direction = np.random.randint(0, 360, size=num_minutes)
max_wind_direction = np.random.randint(0, 360, size=num_minutes)
min_wind_direction = np.random.randint(0, 360, size=num_minutes)
rain_accumulation = np.zeros(num_minutes)
rain_duration = np.zeros(num_minutes)

row_ids = list(range(1, num_minutes + 1))

# ----------------------------
# CREATE DATAFRAME
# ----------------------------
df = pd.DataFrame({
    "rowID": row_ids,
    "hpwren_timestamp": timestamps,
    "air_pressure": air_pressure,
    "air_temp": air_temps,
    "avg_wind_direction": avg_wind_direction,
    "avg_wind_speed": avg_wind_speed,
    "max_wind_direction": max_wind_direction,
    "max_wind_speed": max_wind_speed,
    "min_wind_direction": min_wind_direction,
    "min_wind_speed": min_wind_speed,
    "rain_accumulation": rain_accumulation,
    "rain_duration": rain_duration,
    "relative_humidity": humidity,
    "time": timestamps  # duplicate for your pipeline
})

# Ensure data directory exists
os.makedirs(os.path.dirname(output_file), exist_ok=True)

# ----------------------------
# SAVE CSV
# ----------------------------
df.to_csv(output_file, index=False)
print(f"Synthetic insulin CSV generated: {output_file}")
