import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.timeline import build_trajectory_text, get_patient_signals


def build_patient_trajectory_table(events_df):
    """
    Build one row per patient with a full trajectory text representation.

    The retrieval system compares patient-level trajectories instead of isolated notes.
    """
    patient_ids = sorted(events_df["patient_id"].unique())

    rows = []

    for patient_id in patient_ids:
        trajectory_text = build_trajectory_text(events_df, patient_id)
        signals = get_patient_signals(events_df, patient_id)

        rows.append(
            {
                "patient_id": patient_id,
                "trajectory_text": trajectory_text,
                "signals": signals,
            }
        )

    return pd.DataFrame(rows)


def retrieve_similar_patients(events_df, query_patient_id, top_k=3):
    """
    Retrieve similar historical patient trajectories.

    This is intentionally simple and explainable:
    - represent each full trajectory using TF-IDF
    - compare trajectories using cosine similarity
    - explain matches using overlapping normalized signals
    """
    trajectory_table = build_patient_trajectory_table(events_df)

    vectorizer = TfidfVectorizer(
        lowercase=True,
        ngram_range=(1, 2),
        min_df=1,
    )

    trajectory_vectors = vectorizer.fit_transform(trajectory_table["trajectory_text"])

    query_index = trajectory_table.index[
        trajectory_table["patient_id"] == query_patient_id
    ][0]

    similarities = cosine_similarity(
        trajectory_vectors[query_index],
        trajectory_vectors,
    )[0]

    query_signals = trajectory_table.loc[query_index, "signals"]

    results = []

    for idx, similarity in enumerate(similarities):
        candidate_patient_id = trajectory_table.loc[idx, "patient_id"]

        if candidate_patient_id == query_patient_id:
            continue

        candidate_signals = trajectory_table.loc[idx, "signals"]
        shared_signals = sorted(query_signals.intersection(candidate_signals))

        confidence_note = _make_confidence_note(similarity, shared_signals)

        results.append(
            {
                "patient_id": candidate_patient_id,
                "similarity_score": round(float(similarity), 3),
                "shared_signals": shared_signals,
                "confidence_note": confidence_note,
                "trajectory_text": trajectory_table.loc[idx, "trajectory_text"],
            }
        )

    results = sorted(
        results,
        key=lambda item: item["similarity_score"],
        reverse=True,
    )

    return results[:top_k]


def _make_confidence_note(similarity, shared_signals):
    """
    Convert a raw similarity score into a cautious interpretation.

    This is not a clinical confidence score. It is a retrieval confidence note.
    """
    if similarity >= 0.55 and len(shared_signals) >= 3:
        return "Higher retrieval confidence: multiple shared clinical and operational signals."
    if similarity >= 0.35 and len(shared_signals) >= 2:
        return "Moderate retrieval confidence: some shared trajectory signals."
    return "Low retrieval confidence: review manually before using this as an analog."