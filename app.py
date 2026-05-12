import streamlit as st

from src.load_data import load_all_data
from src.harmonize import build_unified_events
from src.timeline import get_patient_timeline
from src.retrieval import retrieve_similar_patients
from src.forecast import forecast_patient_breakdown, estimate_illustrative_admin_impact


st.set_page_config(
    page_title="Patient Trajectory Retrieval Engine",
    layout="wide",
)


@st.cache_data
def load_events():
    data = load_all_data()
    events = build_unified_events(data)
    return data, events


def render_event_card(row):
    severity = int(row["severity"])

    if severity >= 4:
        severity_label = "High severity"
    elif severity >= 3:
        severity_label = "Medium severity"
    else:
        severity_label = "Low severity"

    st.markdown(
        f"""
        **{row['timestamp'].date()} — {row['event_type']}**  
        Source system: `{row['source_system']}`  
        Clinical signal: `{row['clinical_signal']}`  
        Operational signal: `{row['operational_signal']}`  
        Severity: `{severity}` — {severity_label}  
        {row['summary']}
        """
    )


data, events = load_events()

st.title("Patient Trajectory Retrieval Engine")
st.caption(
    "A synthetic prototype exploring event harmonization, longitudinal patient timelines, "
    "trajectory retrieval, and operational intervention logic."
)

st.warning(
    "This demo uses fully synthetic data. It is not clinically validated and should not be used "
    "for care decisions. The goal is to explore the representation and retrieval problem."
)

st.markdown(
    """
    ### Core idea

    Hospitals often store labs, visits, referrals, prior authorizations, claims, and notes in different systems.
    This prototype normalizes those fragments into a shared patient event model, then compares full patient
    trajectories rather than isolated documents.
    """
)

tab_source, tab_timeline, tab_retrieval, tab_eval, tab_design = st.tabs(
    [
        "1. Fragmented Data",
        "2. Unified Timeline",
        "3. Similar Trajectories",
        "4. Evaluation",
        "5. Design Tension",
    ]
)

with tab_source:
    st.header("Fragmented source systems")

    st.markdown(
        """
        Each table below represents a simulated source system with its own schema.
        The point is not the data volume; it is the normalization problem.
        """
    )

    source_name = st.selectbox(
        "Choose source system",
        ["labs", "visits", "referrals", "prior_auths", "claims", "notes"],
    )

    st.dataframe(data[source_name], use_container_width=True)

    st.subheader("Unified PatientEvent schema")

    st.code(
        """
PatientEvent = {
    patient_id: str,
    timestamp: datetime,
    event_type: str,
    source_system: str,
    clinical_signal: str,
    operational_signal: str,
    severity: int,
    summary: str,
    metadata: dict
}
        """,
        language="python",
    )

    st.subheader("Unified event table")
    st.dataframe(
        events[
            [
                "patient_id",
                "timestamp",
                "event_type",
                "source_system",
                "clinical_signal",
                "operational_signal",
                "severity",
                "summary",
            ]
        ],
        use_container_width=True,
    )

with tab_timeline:
    st.header("Patient timeline")

    patient_ids = sorted(events["patient_id"].unique())
    selected_patient = st.selectbox("Select patient", patient_ids, index=0)

    timeline = get_patient_timeline(events, selected_patient)
    forecast = forecast_patient_breakdown(events, selected_patient)
    impact = estimate_illustrative_admin_impact(forecast)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Priority", forecast["priority"])

    with col2:
        st.metric("Total severity", forecast["total_severity"])

    with col3:
        st.metric(
            "Illustrative revenue at risk",
            f"${impact['illustrative_revenue_at_risk']}",
        )

    st.subheader(f"Chronological story for {selected_patient}")

    for _, row in timeline.iterrows():
        render_event_card(row)
        st.divider()

    st.subheader("Forecasted operational breakdowns")

    for risk in forecast["risks"]:
        st.write(f"- {risk}")

    st.subheader("Recommended workflow actions")

    for intervention in forecast["recommended_interventions"]:
        st.write(f"- {intervention}")

    st.caption(impact["note"])

with tab_retrieval:
    st.header("Similar patient trajectory retrieval")

    st.markdown(
        """
        This section compares entire patient trajectories using TF-IDF + cosine similarity.
        It intentionally uses a simple explainable retrieval method rather than an opaque model.
        """
    )

    query_patient = st.selectbox(
        "Select patient to retrieve analog trajectories for",
        sorted(events["patient_id"].unique()),
        index=0,
        key="retrieval_patient",
    )

    matches = retrieve_similar_patients(events, query_patient, top_k=3)

    st.subheader(f"Top similar trajectories for {query_patient}")

    for match in matches:
        st.markdown(f"### {match['patient_id']}")
        st.metric("Trajectory similarity", match["similarity_score"])
        st.write(match["confidence_note"])

        if match["shared_signals"]:
            st.write("Shared signals:")
            for signal in match["shared_signals"]:
                st.write(f"- {signal}")
        else:
            st.write("No normalized signals overlapped. This match should be treated cautiously.")

        candidate_forecast = forecast_patient_breakdown(events, match["patient_id"])
        st.write("Candidate forecast:")
        st.write(", ".join(candidate_forecast["risks"]))

        if match["patient_id"] == "P006":
            st.info(
                "Important nuance: P006 is clinically similar but operationally different. "
                "Its referral was completed and claim was paid, so it may represent a successful "
                "intervention trajectory rather than a breakdown trajectory."
            )

        st.divider()

with tab_eval:
    st.header("Mini evaluation: keyword search vs trajectory retrieval")

    st.markdown(
        """
        A keyword search can find exact terms, but it may miss the broader patient journey.
        Trajectory retrieval compares the sequence of normalized clinical and operational signals.
        """
    )

    st.subheader("Example task")
    st.write(
        "Find patients similar to P001: worsening diabetes + specialist workflow delay + reimbursement risk."
    )

    st.subheader("Keyword-style search")
    st.code("search: 'denied claim'", language="text")
    st.write(
        "This would find patients with denied claims, but it does not necessarily distinguish between "
        "a diabetes referral breakdown, an imaging authorization delay, or an isolated billing issue."
    )

    st.subheader("Trajectory retrieval")
    st.write(
        "The retrieval engine correctly surfaces P005 and P003 as close analogs because they share multiple "
        "clinical and operational signals over time."
    )

    eval_rows = []
    for match in retrieve_similar_patients(events, "P001", top_k=3):
        eval_rows.append(
            {
                "query_patient": "P001",
                "retrieved_patient": match["patient_id"],
                "similarity_score": match["similarity_score"],
                "shared_signal_count": len(match["shared_signals"]),
                "shared_signals": ", ".join(match["shared_signals"]),
            }
        )

    st.dataframe(eval_rows, use_container_width=True)

with tab_design:
    st.header("Design tension / flaw in the naive version")

    st.markdown(
        """
        The tempting version of this system is: normalize records, embed trajectories, retrieve similar patients,
        and trigger actions automatically.

        The flaw is that trajectory retrieval is only useful if the representation layer is standardized enough
        to compare patients fairly.

        If two clinics encode referrals, claims, prior authorizations, or follow-ups differently, a model can
        confidently retrieve the wrong analogs. In a hospital setting, that false confidence is dangerous.
        """
    )

    st.subheader("Mitigations a real system would need")

    st.write("- Strong normalization across source systems")
    st.write("- Uncertainty scores around retrieved analogs")
    st.write("- Human-in-the-loop review before high-impact workflow automation")
    st.write("- Auditing for missingness, payer-specific artifacts, and site-specific documentation patterns")
    st.write("- Separation between clinical similarity and operational similarity")

    st.subheader("Why this prototype keeps the model simple")

    st.markdown(
        """
        I used TF-IDF + cosine similarity intentionally. For a founder-facing prototype, this makes the retrieval
        mechanism inspectable. The goal is not to claim clinical sophistication; it is to show how fragmented records
        can become comparable longitudinal trajectories.
        """
    )