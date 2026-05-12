def forecast_patient_breakdown(events_df, patient_id):
    """
    Produce a simple operational forecast from normalized trajectory signals.

    This is not a clinical prediction model. It is a rule-based prototype meant to
    demonstrate how harmonized events can trigger workflow review.
    """
    patient_events = events_df[events_df["patient_id"] == patient_id]

    clinical_signals = set(patient_events["clinical_signal"].tolist())
    operational_signals = set(patient_events["operational_signal"].tolist())
    total_severity = int(patient_events["severity"].sum())

    risks = []
    interventions = []

    if "worsening A1C" in clinical_signals or "clinical deterioration" in clinical_signals:
        risks.append("care drop-off risk")
        interventions.append("Route to care coordinator for follow-up outreach.")

    if "pending referral" in operational_signals:
        risks.append("specialist referral delay")
        interventions.append("Check referral queue and schedule next action.")

    if "prior authorization delay" in operational_signals:
        risks.append("delayed approval risk")
        interventions.append("Escalate prior authorization with payer documentation.")

    if "denied claim" in operational_signals:
        risks.append("revenue leakage risk")
        interventions.append("Review denial reason and resubmit corrected claim.")

    if "emergency escalation" in clinical_signals or "urgent referral" in operational_signals:
        risks.append("high-acuity escalation risk")
        interventions.append("Prioritize manual clinical/administrative review.")

    if not risks:
        risks.append("low immediate operational risk")
        interventions.append("Continue routine monitoring.")

    if total_severity >= 16:
        priority = "High"
    elif total_severity >= 9:
        priority = "Medium"
    else:
        priority = "Low"

    return {
        "patient_id": patient_id,
        "priority": priority,
        "total_severity": total_severity,
        "risks": sorted(set(risks)),
        "recommended_interventions": sorted(set(interventions)),
    }


def estimate_illustrative_admin_impact(forecast):
    """
    Create a deliberately simple illustrative ROI estimate.

    This is not a real financial model. It only connects operational triggers
    to the staff-time/revenue-recovery logic Eos talks about.
    """
    risks = forecast["risks"]

    minutes_saved = 0
    revenue_at_risk = 0

    if "specialist referral delay" in risks:
        minutes_saved += 20

    if "delayed approval risk" in risks:
        minutes_saved += 25

    if "revenue leakage risk" in risks:
        minutes_saved += 15
        revenue_at_risk += 400

    if "care drop-off risk" in risks:
        minutes_saved += 15

    return {
        "illustrative_minutes_saved": minutes_saved,
        "illustrative_revenue_at_risk": revenue_at_risk,
        "note": "Illustrative only; not based on real hospital financial data.",
    }