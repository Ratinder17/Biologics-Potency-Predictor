# services/report_service.py
from datetime import datetime
from config import openai_client, Config
from persistence.mongo import investigations, calculations, reports
import uuid


class ReportGenerationError(Exception):
    pass


def generate_investigation_report(investigation_id: str, user_sub: str = None) -> str:
    """
    Generates a Temperature Deviation Investigation Report and saves it to MongoDB.
    """
    # ---- Fetch authoritative data ----
    investigation = investigations.find_one({"investigation_id": investigation_id})
    if not investigation:
        raise ReportGenerationError("Investigation not found")

    calculation = calculations.find_one({"investigation_id": investigation_id})
    if not calculation:
        raise ReportGenerationError("Calculation not found")

    inputs = calculation["inputs"]
    results = calculation["results"]

    # ---- Prompt construction ----
    prompt = f"""
SYSTEM ROLE:
You are a Senior Quality Assurance (QA) Manager preparing a scientific, decision-support document.
You do NOT approve, reject, or release product.

DOCUMENT TYPE:
Temperature Deviation Investigation Report

REGULATORY CONTEXT (INFORMATIONAL ALIGNMENT ONLY):
- FDA 21 CFR Part 11 (Data Integrity)
- ICH Q1A(R2) (Stability)
- ICH Q9 (Quality Risk Management)
- GxP Documentation Principles

BOUNDARY CONDITIONS (STRICT):
- Use ONLY the data explicitly provided below.
- Do NOT invent, infer, or estimate missing values.
- Do NOT make release, rejection, or disposition decisions.
- Do NOT recommend discard, rework, or market action.
- Maintain neutral, evidence-based language.
- If data is unavailable, state exactly: "Data not available for assessment."

INVESTIGATION METADATA:
- Investigation ID: {investigation_id}
- Stability Profile Applied: {inputs['stability_profile']}
- Activation Energy (Ea): {inputs['Ea']} J/mol
- Frequency Factor (A): {inputs['A']}
- Kinetic Model: Arrhenius-based degradation
- Temperature Smoothing Method: Exponential
- Smoothing Parameter (α): {inputs['smoothing_alpha']}

ANALYTICAL RESULTS (SOURCE DATA):
- Worst-Case Air Temperature: {results['peak_sensor_temp_c']} °C
- Worst-Case Estimated Product Temperature: {results['peak_product_estimated_c']} °C
- Calculated Final Potency: {results['final_potency_percent']} %
- Calculated Total Potency Loss: {100 - results['final_potency_percent']:.4f} %

MANDATORY OUTPUT FORMAT:
The generated report MUST follow the exact structure below, including headings and order.
Do NOT add sections or conclusions beyond numerical interpretation.

TEMPERATURE DEVIATION INVESTIGATION REPORT  

Investigation ID: {investigation_id}  
Stability Profile: {inputs['stability_profile']}


1. PURPOSE AND SCOPE  
- State the purpose of this temperature deviation assessment  
- Define the scope as a quantitative evaluation of temperature-driven degradation  
- Explicitly state that kinetic modeling outputs are provided to support, but not replace, QA decision-making  
- State that labeled storage conditions are referenced for context only

---

2. DEVIATION OVERVIEW  
- Describe the observed temperature excursion using recorded sensor data  
- Identify the primary monitoring reference (air temperature vs estimated product temperature)  
- Report worst-case observed air and product temperatures  
- Define the temporal and analytical boundaries of the assessed event

---

3. SCIENTIFIC ANALYSIS AND RESULTS  
- Describe the Arrhenius-based degradation model applied  
- Explicitly list kinetic parameters used (Activation Energy and Frequency Factor)  
- Describe how temperature-time data was processed, including smoothing methodology  
- Compare observed air temperature to estimated product temperature profiles  
- Present calculated potency outcomes derived from modeled degradation kinetics  
- If applicable, compare observed temperatures to the labeled stability range for contextual reference only

---

4. DATA INTEGRITY AND METHODOLOGY  
- Describe source and handling of raw temperature time-series data  
- Confirm exponential smoothing methodology and parameter values  
- Confirm that calculations were performed using validated algorithms  
- Confirm alignment with 21 CFR Part 11 data integrity principles  
- State explicitly that no external data, assumptions, or stability extrapolations were introduced

---

5. INTERPRETIVE GUIDANCE (NON-BINDING)  
- Explain what the calculated potency and temperature data indicate in quantitative terms  
- Clarify that degradation estimates are driven by observed temperature exposure and kinetic parameters  
- Describe known limitations of model-based estimation, including sensitivity to parameter selection  
- Reiterate that final quality disposition decisions require authorized QA review and approved procedures

---

DISCLAIMER:
"This report provides quantitative scientific analysis to support quality review activities. Final disposition decisions must be made by authorized quality personnel in accordance with approved procedures."

"""



    # ---- OpenAI call ----
    try:
        response = openai_client.chat.completions.create(
            model=Config.AZURE_OPENAI_DEPLOYMENT,
            messages=[
                {"role": "system", "content": "You are a helpful scientific assistant."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=2000
        )
    except Exception as e:
        raise ReportGenerationError(f"OpenAI call failed: {str(e)}")

    report_content = response.choices[0].message.content

    # ---- Save to MongoDB ----
    if user_sub is None:
        raise ReportGenerationError("user_sub is required to save the report")

    save_report(
        investigation_id=investigation_id,
        report_content=report_content,
        user_sub=user_sub,
        calculation_id=calculation.get("calculation_id")
    )

    return report_content



def save_report(
    investigation_id: str,
    report_content: str,
    user_sub: str,
    calculation_id: str | None = None,
):
    """
    Stores the generated report in MongoDB.
    """
    report_id = f"REP-{uuid.uuid4().hex[:8]}"

    reports.insert_one({
        "report_id": report_id,
        "investigation_id": investigation_id,
        "calculation_id": calculation_id,
        "user_sub": user_sub,
        "content": report_content,
        "generation": {
            "model": Config.AZURE_OPENAI_DEPLOYMENT
        },
        "status": "GENERATED",
        "created_at": datetime.utcnow()
    })

    return report_id
