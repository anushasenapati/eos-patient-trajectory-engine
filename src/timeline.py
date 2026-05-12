def get_patient_timeline(events_df, patient_id):
    """
    Return all events for one patient in chronological order.
    """
    timeline = events_df[events_df["patient_id"] == patient_id]
    return timeline.sort_values("timestamp")


def build_trajectory_text(events_df, patient_id):
    """
    Convert a full patient timeline into a text representation.

    This is what lets us compare patient journeys rather than isolated records.
    """
    timeline = get_patient_timeline(events_df, patient_id)

    parts = []

    for _, row in timeline.iterrows():
        parts.append(
            f"{row['event_type']} | "
            f"clinical: {row['clinical_signal']} | "
            f"operational: {row['operational_signal']} | "
            f"severity: {row['severity']} | "
            f"{row['summary']}"
        )

    return " ".join(parts)


def get_patient_signals(events_df, patient_id):
    """
    Extract normalized clinical and operational signals for explanation.
    """
    timeline = get_patient_timeline(events_df, patient_id)

    signals = set()

    for _, row in timeline.iterrows():
        clinical_signal = row["clinical_signal"]
        operational_signal = row["operational_signal"]

        if clinical_signal and clinical_signal != "none":
            signals.add(clinical_signal)

        if operational_signal and operational_signal != "none":
            signals.add(operational_signal)

    return signals