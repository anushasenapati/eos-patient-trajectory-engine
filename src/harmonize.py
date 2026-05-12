import pandas as pd


def _base_event(
    patient_id,
    timestamp,
    event_type,
    source_system,
    clinical_signal,
    operational_signal,
    severity,
    summary,
    metadata,
):
    """
    Standard event representation used across all source systems.

    This is the core abstraction of the prototype:
    fragmented records become comparable patient events.
    """
    return {
        "patient_id": patient_id,
        "timestamp": timestamp,
        "event_type": event_type,
        "source_system": source_system,
        "clinical_signal": clinical_signal,
        "operational_signal": operational_signal,
        "severity": severity,
        "summary": summary,
        "metadata": metadata,
    }


def harmonize_labs(labs):
    events = []

    for _, row in labs.iterrows():
        value = float(row["value"])

        if row["test"] == "A1C" and value >= 8.5:
            clinical_signal = "worsening A1C"
            severity = 3
        elif row["test"] == "A1C" and value >= 7.5:
            clinical_signal = "elevated A1C"
            severity = 2
        else:
            clinical_signal = "stable lab"
            severity = 1

        events.append(
            _base_event(
                patient_id=row["patient_id"],
                timestamp=row["timestamp"],
                event_type="lab_result",
                source_system=row["source_system"],
                clinical_signal=clinical_signal,
                operational_signal="none",
                severity=severity,
                summary=f"{row['test']} result was {row['value']}{row['unit']}",
                metadata={
                    "test": row["test"],
                    "value": value,
                    "unit": row["unit"],
                },
            )
        )

    return events


def harmonize_visits(visits):
    events = []

    for _, row in visits.iterrows():
        reason = str(row["reason"]).lower()
        visit_type = str(row["visit_type"]).lower()

        if "emergency" in visit_type or "severe" in reason:
            clinical_signal = "emergency escalation"
            severity = 4
        elif "worsening" in reason or "fatigue" in reason:
            clinical_signal = "clinical deterioration"
            severity = 3
        elif "diabetes" in reason:
            clinical_signal = "chronic disease management"
            severity = 2
        else:
            clinical_signal = "routine care"
            severity = 1

        events.append(
            _base_event(
                patient_id=row["patient_id"],
                timestamp=row["timestamp"],
                event_type="visit",
                source_system=row["source_system"],
                clinical_signal=clinical_signal,
                operational_signal="none",
                severity=severity,
                summary=f"{row['visit_type']} with {row['provider']} for {row['reason']}",
                metadata={
                    "visit_type": row["visit_type"],
                    "provider": row["provider"],
                    "reason": row["reason"],
                },
            )
        )

    return events


def harmonize_referrals(referrals):
    events = []

    for _, row in referrals.iterrows():
        status = str(row["status"]).lower()

        if status == "pending":
            operational_signal = "pending referral"
            severity = 3
        elif status == "urgent":
            operational_signal = "urgent referral"
            severity = 4
        elif status == "completed":
            operational_signal = "completed referral"
            severity = 1
        else:
            operational_signal = "no referral action needed"
            severity = 1

        events.append(
            _base_event(
                patient_id=row["patient_id"],
                timestamp=row["timestamp"],
                event_type="referral",
                source_system=row["source_system"],
                clinical_signal=row["referral_type"],
                operational_signal=operational_signal,
                severity=severity,
                summary=f"{row['referral_type']} referral status: {row['status']}",
                metadata={
                    "referral_type": row["referral_type"],
                    "status": row["status"],
                    "last_action_date": row["last_action_date"],
                },
            )
        )

    return events


def harmonize_prior_auths(prior_auths):
    events = []

    for _, row in prior_auths.iterrows():
        status = str(row["status"]).lower()
        days_pending = int(row["days_pending"])

        if status == "delayed" or days_pending >= 14:
            operational_signal = "prior authorization delay"
            severity = 4 if days_pending >= 30 else 3
        elif status == "approved":
            operational_signal = "authorization approved"
            severity = 1
        else:
            operational_signal = "authorization not required"
            severity = 1

        events.append(
            _base_event(
                patient_id=row["patient_id"],
                timestamp=row["timestamp"],
                event_type="prior_authorization",
                source_system=row["source_system"],
                clinical_signal=row["authorization_type"],
                operational_signal=operational_signal,
                severity=severity,
                summary=(
                    f"{row['authorization_type']} prior authorization is {row['status']} "
                    f"with {row['payer']} after {row['days_pending']} days pending"
                ),
                metadata={
                    "authorization_type": row["authorization_type"],
                    "status": row["status"],
                    "payer": row["payer"],
                    "days_pending": days_pending,
                },
            )
        )

    return events


def harmonize_claims(claims):
    events = []

    for _, row in claims.iterrows():
        status = str(row["status"]).lower()

        if status == "denied":
            operational_signal = "denied claim"
            severity = 3
            summary = (
                f"{row['claim_type']} claim denied for ${row['amount_usd']}: "
                f"{row['denial_reason']}"
            )
        else:
            operational_signal = "claim paid"
            severity = 1
            summary = f"{row['claim_type']} claim paid for ${row['amount_usd']}"

        events.append(
            _base_event(
                patient_id=row["patient_id"],
                timestamp=row["timestamp"],
                event_type="claim",
                source_system=row["source_system"],
                clinical_signal=row["claim_type"],
                operational_signal=operational_signal,
                severity=severity,
                summary=summary,
                metadata={
                    "claim_type": row["claim_type"],
                    "status": row["status"],
                    "amount_usd": float(row["amount_usd"]),
                    "denial_reason": row["denial_reason"],
                },
            )
        )

    return events


def harmonize_notes(notes):
    events = []

    concerning_terms = [
        "worsening",
        "difficulty",
        "not completed",
        "not heard back",
        "waiting",
        "delayed",
        "emergency",
        "inconsistent",
    ]

    for _, row in notes.iterrows():
        note = str(row["note"]).lower()

        if any(term in note for term in concerning_terms):
            clinical_signal = "concerning clinical note"
            operational_signal = "possible care gap"
            severity = 3
        else:
            clinical_signal = "stable note"
            operational_signal = "none"
            severity = 1

        events.append(
            _base_event(
                patient_id=row["patient_id"],
                timestamp=row["timestamp"],
                event_type="clinical_note",
                source_system=row["source_system"],
                clinical_signal=clinical_signal,
                operational_signal=operational_signal,
                severity=severity,
                summary=row["note"],
                metadata={
                    "note": row["note"],
                },
            )
        )

    return events


def build_unified_events(data):
    """
    Convert all fragmented source tables into one event table.
    """
    events = []

    events.extend(harmonize_labs(data["labs"]))
    events.extend(harmonize_visits(data["visits"]))
    events.extend(harmonize_referrals(data["referrals"]))
    events.extend(harmonize_prior_auths(data["prior_auths"]))
    events.extend(harmonize_claims(data["claims"]))
    events.extend(harmonize_notes(data["notes"]))

    events_df = pd.DataFrame(events)
    events_df["timestamp"] = pd.to_datetime(events_df["timestamp"])
    events_df = events_df.sort_values(["patient_id", "timestamp"]).reset_index(drop=True)

    return events_df