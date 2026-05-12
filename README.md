# Patient Trajectory Retrieval Engine

a small synthetic prototype exploring how fragmented healthcare records can be harmonized into longitudinal patient trajectories, retrieved against similar historical journeys, and also used to surface operational intervention points.

this project was inspired by the infrastructure problem of turning disconnected hospital data into actionable intelligence (creds: Eos AI). it is not a clinical prediction tool.

## What This Prototype Demonstrates

the prototype takes fragmented synthetic data from multiple simulated source systems:

- lab results
- visits
- referrals
- prior authorizations
- claims
- clinical notes

it then converts those records into a shared event representation, builds patient timelines, retrieves similar historical trajectories, and generates a simple operational forecast.

## Why Trajectories Matter

a single lab result, claim denial, referral, or clinical note is useful, but incomplete.

The more interesting signal appears when those events are placed in sequence:

```text
elevated A1C → primary care visit → pending endocrinology referral → delayed prior authorization → denied claim → worsening A1C → note describing difficulty scheduling follow-up
