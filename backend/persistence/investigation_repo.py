# persistence/investigation_repo.py
from datetime import datetime
import uuid
from .mongo import investigations, temperature_readings, calculations


def create_investigation(investigation_id, user_sub):
    investigations.insert_one({
        "investigation_id": investigation_id,
        "user_sub": user_sub,            # Add the user reference
        "created_at": datetime.utcnow(),
        "status": "COMPUTED",
        "source": "csv_upload",
        "schema_version": "1.0"
    })

def save_temperature_readings(investigation_id, timestamps, temps, user_sub):
    temperature_readings.insert_many([
        {
            "investigation_id": investigation_id,
            "time": t.to_pydatetime(),
            "temperature_c": float(temp),
            "sensor_type": "air",
            "ingested_at": datetime.utcnow(),
            "user_sub": user_sub
        }
        for t, temp in zip(timestamps, temps)
    ])

def save_calculation(investigation_id, profile_key, Ea, A, alpha, metrics, user_sub):
    calculations.insert_one({
        "calculation_id": f"CALC-{uuid.uuid4().hex[:6]}",
        "investigation_id": investigation_id,
        "schema_version": "1.0",
        "model": {
            "thermal": "first_order_lag_v1",
            "chemistry": "arrhenius_v1"
        },
        "inputs": {
            "stability_profile": profile_key,
            "Ea": Ea,
            "A": A,
            "smoothing_alpha": alpha
        },
        "results": metrics,
        "computed_at": datetime.utcnow(),
        "supersedes": None,
        "user_sub": user_sub
    })

