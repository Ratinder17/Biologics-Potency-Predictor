# ingestion/csv_loader.py

import pandas as pd
from config import azure_di_client
from fastapi import HTTPException
import difflib

class CSVSchemaError(Exception):
    """Raised when required columns are missing or malformed."""
    pass


class CSVIngestionError(Exception):
    """Raised when CSV cannot be parsed or contains invalid data."""
    pass


def load_temperature_csv(
    file_obj,
    time_column: str,
    temperature_column: str,
    temperature_unit: str = "C",
) -> pd.DataFrame:
    """
    Loads and validates a temperature time-series CSV.

    Returns a DataFrame with canonical columns:
      - timestamp (datetime, UTC-naive)
      - air_temp (float, Celsius)
    """

    try:
        df = pd.read_csv(file_obj)
    except Exception as e:
        raise CSVIngestionError(f"Failed to read CSV: {str(e)}")

    # ---- Validate required columns ----
    missing = {time_column, temperature_column} - set(df.columns)
    if missing:
        raise CSVSchemaError(f"Missing required columns: {missing}")

    # ---- Parse timestamps ----
    try:
        df["timestamp"] = pd.to_datetime(df[time_column], errors="raise")
    except Exception:
        raise CSVSchemaError(f"Invalid timestamp format in column '{time_column}'")

    # ---- Parse temperatures ----
    try:
        temps = pd.to_numeric(df[temperature_column], errors="raise")
    except Exception:
        raise CSVSchemaError(
            f"Non-numeric temperature values in column '{temperature_column}'"
        )

    # ---- Normalize temperature units ----
    unit = temperature_unit.upper()
    if unit == "C":
        df["air_temp"] = temps
    elif unit == "F":
        df["air_temp"] = (temps - 32.0) * (5.0 / 9.0)
    elif unit == "K":
        df["air_temp"] = temps - 273.15
    else:
        raise CSVSchemaError(f"Unsupported temperature unit: {temperature_unit}")

    # ---- Final validation ----
    if df["air_temp"].isna().any():
        raise CSVIngestionError("Temperature column contains NaN values")

    if df["timestamp"].isna().any():
        raise CSVIngestionError("Timestamp column contains NaT values")

    return df[["timestamp", "air_temp"]].copy()


