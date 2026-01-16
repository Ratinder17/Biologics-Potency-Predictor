from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime



class InvestigationCreateRequest(BaseModel):
    gtin: str 
    time_column: str 
    temperature_column: str 
    temperature_unit: str

    


# ===============================
# Basic Investigation Response
# ===============================

class InvestigationResponse(BaseModel):
    investigation_id: str
    status: str


# ===============================
# Analysis Summary (QA-facing)
# ===============================

class AnalysisResponse(BaseModel):
    investigation_id: str
    final_potency: float # Estimated remaining potency percentage
    max_temperature: float # Maximum recorded temperature during excursion
    duration_minutes: float # Total duration above allowed range (minutes)

# ===============================
# Scientific Report Structures
# ===============================

class ScientificAssumption(BaseModel):
    assumption: str
    justification: str


class ExcursionSummary(BaseModel):
    start_time: datetime
    end_time: datetime
    max_temperature: float
    duration_minutes: float


class ModelDetails(BaseModel):
    thermal_model: str
    degradation_model: str
    constants_used: Dict[str, float]


class ReportResponse(BaseModel):
    investigation_id: str

    product_identification: Dict[str, str]

    excursion_summary: ExcursionSummary

    modeling_details: ModelDetails

    assumptions: List[ScientificAssumption]

    conclusion: str

    recommended_action: str


class TTSRequest(BaseModel):
    investigation_id: str
