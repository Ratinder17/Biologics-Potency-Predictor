# utils/ids.py

import uuid
from datetime import datetime


def generate_investigation_id() -> str:
    """
    Example:
      INV-20251229-a3f91c
    """
    date_part = datetime.utcnow().strftime("%Y%m%d")
    rand_part = uuid.uuid4().hex[:6]
    return f"INV-{date_part}-{rand_part}"


def generate_calculation_id() -> str:
    """
    Example:
      CALC-4b92fd
    """
    return f"CALC-{uuid.uuid4().hex[:6]}"