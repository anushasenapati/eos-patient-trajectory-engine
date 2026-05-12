import pandas as pd


def load_all_data():
    """
    Load fragmented synthetic healthcare data from multiple simulated source systems.

    Each file intentionally has a different schema to mimic the real-world problem
    of fragmented clinic and hospital data.
    """
    labs = pd.read_csv("data/labs.csv")
    visits = pd.read_csv("data/visits.csv")
    referrals = pd.read_csv("data/referrals.csv")
    prior_auths = pd.read_csv("data/prior_auths.csv")
    claims = pd.read_csv("data/claims.csv")
    notes = pd.read_csv("data/notes.csv")

    return {
        "labs": labs,
        "visits": visits,
        "referrals": referrals,
        "prior_auths": prior_auths,
        "claims": claims,
        "notes": notes,
    }