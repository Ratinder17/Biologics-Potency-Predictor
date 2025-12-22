from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd
import math

# ===== Domain imports =====
from domain.smoothing import exponential_smoothing
from domain.thermal import update_product_temperature
from domain.degradation import degradation_rate
from domain.forecasting import forecast_future_temps

# ===== Config =====
DEBUG_PRINT = True          # Show output in terminal
PRINT_EVERY_N = 60          # Only print every N rows (minute data → hourly)
FORECAST_HOURS = 6          # How many hours ahead to forecast

# ===== Flask setup =====
app = Flask(__name__)
CORS(app)

@app.route("/api/forecast", methods=["GET"])
def get_forecast():
    # --------------------------------------------------
    # 1. Load & prepare data
    # --------------------------------------------------
    df = pd.read_csv("data/minute_weather.csv")
    df["timestamp"] = pd.to_datetime(df["time"])
    df = df.sort_values("timestamp")
    df = df[["timestamp", "air_temp"]].dropna() # removes rows where timestamp or air temp is  missing 

    timestamps = df["timestamp"].tolist()
    sensor_temps = df["air_temp"].tolist()

    # --------------------------------------------------
    # 2. Smooth sensor temperature
    # --------------------------------------------------
    smoothed_temps = exponential_smoothing(sensor_temps, alpha=0.1)
    """"
    smoothing factor, between 0 and 1
    It controls how much weight you give to the latest observation versus the historical smoothed values.
    High (closer to 1): more reactive to recent changes -> smooths less, follows data closely.
    -> potency decreases faster during brief heat excursions.

    Low (closer to 0): more stable -> reacts slowly to changes, smooths more.
    -> potency decreases more slowly, ignoring short-term fluctuations.

    because we want to filter out short term noise, it makes more sense to keep alpha closer to 0. 
    """

    # --------------------------------------------------
    # 3. Historical pipeline
    # --------------------------------------------------
    results = []

    product_temp = smoothed_temps[0]   # initial product temp
    cumulative_damage = 0.0 # running total of temperature-induced damage.

    for i in range(len(smoothed_temps)):
        if i == 0:
            delta_hours = 0.0
        else:
            delta_hours = (timestamps[i] - timestamps[i - 1]).total_seconds() / 3600.0

        # --- Thermal model ---
        product_temp = update_product_temperature(prev_product_temp=product_temp,sensor_temp=smoothed_temps[i],
                                                  delta_hours=delta_hours)

        # --- Degradation ---
        #first-order degradation kinetics model - k = temperature-dependent degradation rate
        k = degradation_rate(product_temp)
        cumulative_damage += k * delta_hours

        # --- Potency ---
        potency = 100.0 * math.exp(-cumulative_damage)

        # Sanity check
        if results:
            assert potency <= results[-1]["potency"] + 1e-9

        record = {
            "timestamp": timestamps[i].isoformat(),
            "sensor_temp": float(sensor_temps[i]),
            "smoothed_temp": float(smoothed_temps[i]),
            "product_temp": float(product_temp),
            "potency": float(potency),
            "type": "history"
        }
        results.append(record)

        # --- Terminal output ---
        if DEBUG_PRINT and i % PRINT_EVERY_N == 0:
            print(
                f"[HISTORY] {timestamps[i]} | "
                f"Air={sensor_temps[i]:.2f}°C | "
                f"Smooth={smoothed_temps[i]:.2f}°C | "
                f"Product={product_temp:.2f}°C | "
                f"Potency={potency:.4f}%"
            )

    # --------------------------------------------------
    # 4. Forecasting
    # --------------------------------------------------
    future_sensor_temps = forecast_future_temps(smoothed_temps, hours=FORECAST_HOURS)
    last_timestamp = timestamps[-1]

    for h, future_temp in enumerate(future_sensor_temps, start=1):
        delta_hours = 1.0  # 1-hour step

        product_temp = update_product_temperature(
            prev_product_temp=product_temp,
            sensor_temp=future_temp,
            delta_hours=delta_hours
        )

        k = degradation_rate(product_temp)
        cumulative_damage += k * delta_hours
        potency = 100.0 * math.exp(-cumulative_damage)

        record = {
            "timestamp": (last_timestamp + pd.Timedelta(hours=h)).isoformat(),
            "sensor_temp": float(future_temp),
            "product_temp": float(product_temp),
            "potency": float(potency),
            "type": "forecast"
        }

        results.append(record)

        if DEBUG_PRINT:
            print(
                f"[FORECAST +{h}h] {record['timestamp']} | "
                f"Air={future_temp:.2f}°C | "
                f"Product={product_temp:.2f}°C | "
                f"Potency={potency:.4f}%"
            )

    # --------------------------------------------------
    # 5. Return API response
    # --------------------------------------------------
    return jsonify(results)


if __name__ == "__main__":
    app.run(debug=True, port=5001)
