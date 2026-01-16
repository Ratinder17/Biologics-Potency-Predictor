# services/forecast_service.py

import math
from typing import List, Tuple, Dict
from datetime import datetime

from domain.smoothing import exponential_smoothing
from domain.thermal import update_product_temperature
from domain.degradation import degradation_rate
from domain.stability_profiles import STABILITY_PROFILES


class ForecastModelViolation(Exception):
    """Raised when scientific model constraints are violated."""
    pass


def run_forecast(
    timestamps: List[datetime],
    sensor_temps: List[float],
    stability_profile_key: str,
    smoothing_alpha: float = 0.1,
    debug: bool = False,
    print_every_n: int = 60,
) -> Tuple[List[Dict], Dict]:
    """
    Executes the temperature → product → potency model.

    Returns:
      results: full time-series (history)
      metrics: aggregate summary statistics
    """

    if stability_profile_key not in STABILITY_PROFILES:
        raise ValueError(f"Unknown stability profile: {stability_profile_key}")

    if len(sensor_temps) < 2:
        raise ValueError("At least two temperature points are required")

    # ---- Stability parameters ----
    profile = STABILITY_PROFILES[stability_profile_key]
    Ea = profile["Ea"]
    A = profile["A"]

    # ---- Smoothing ----
    smoothed = exponential_smoothing(sensor_temps, alpha=smoothing_alpha)

    # ---- Core simulation ----
    results = []
    product_temp = smoothed[0]
    cumulative_damage = 0.0
    prev_potency = 100.0

    for i in range(len(smoothed)):

        if i == 0:
            delta_hours = 0.0
        else:
            delta_hours = (
                (timestamps[i] - timestamps[i - 1]).total_seconds() / 3600.0
            )

        product_temp = update_product_temperature(
            prev_product_temp=product_temp,
            sensor_temp=smoothed[i],
            delta_hours=delta_hours,
        )

        k = degradation_rate(product_temp, A=A, Ea=Ea)
        cumulative_damage += k * delta_hours
        potency = 100.0 * math.exp(-cumulative_damage)

        # ---- Scientific invariant ----
        if potency > prev_potency + 1e-9:
            raise ForecastModelViolation(
                "Potency increased over time — model violation"
            )

        prev_potency = potency

        results.append({
            "timestamp": timestamps[i].isoformat(),
            "sensor_temp": float(sensor_temps[i]),
            "smoothed_temp": float(smoothed[i]),
            "product_temp": float(product_temp),
            "potency": float(potency),
            "type": "history",
        })

        if debug and i % print_every_n == 0:
            print(
                f"[HISTORY] {timestamps[i]} | "
                f"Air={sensor_temps[i]:.2f}°C | "
                f"Product={product_temp:.2f}°C | "
                f"Potency={potency:.4f}%"
            )

    # ---- Aggregate metrics ----
    metrics = {
        "peak_sensor_temp_c": max(sensor_temps),
        "peak_product_estimated_c": max(r["product_temp"] for r in results),
        "min_sensor_estimated_c": min(sensor_temps),
        "min_product_estimated_c": min(r["product_temp"] for r in results),
        "final_potency_percent": results[-1]["potency"],
    }

    return results, metrics
