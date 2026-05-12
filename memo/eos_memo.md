# Notes from Building a Tiny Patient Trajectory Retrieval Engine

i built this prototype to better understand the infrastructure problem behind longitudinal patient intelligence: how fragmented hospital records can become standardized trajectories that support earlier operational and care intervention.

this is not a clinical prediction tool. it uses fully synthetic data and is meant to explore representation, retrieval, and workflow logic.

## Starting Question

the question I wanted to explore was:

> what changes when a hospital stops treating each lab, note, claim, referral, or prior authorization as an isolated record and instead treats them as part of a patient trajectory?

## What I Built

the prototype ingests synthetic data from six fragmented source systems:

- labs
- visits
- referrals
- prior authorizations
- claims
- clinical notes

each source has its own schema. i normalize them into a shared `PatientEvent` representation with:

- patient ID
- timestamp
- event type
- source system
- clinical signal
- operational signal
- severity
- summary
- metadata

from there, the app builds chronological patient timelines, retrieves similar historical trajectories, forecasts likely operational breakdowns, and recommends workflow actions.

## Why I Used Synthetic Data

i used synthetic data because the goal was to explore architecture, not make clinical claims.
the synthetic patients are scenario-based rather than random. each represents a trajectory archetype:

- stable routine care
- worsening chronic disease with pending referral
- delayed prior authorization
- denied claim from missing documentation
- completed referral followed by improvement
- emergency escalation after worsening disease
- delayed imaging review

this made it possible to test whether the retrieval system would surface the expected analogs.

for example, patient `P001` should retrieve `P005` and `P003` because they share worsening diabetes signals, specialist workflow delay, prior authorization friction, and reimbursement risk.

## Retrieval Design

the retrieval layer intentionally uses TF-IDF and cosine similarity over full patient trajectory text.

i chose this because it is inspectable. for a prototype, i wanted to avoid hiding the main idea behind a black-box model.

the retrieval process is:

1. convert each patient timeline into a full trajectory text representation.
2. vectorize trajectories with TF-IDF.
3. compare patients using cosine similarity.
4. explain matches using overlapping normalized clinical and operational signals.

## What Worked

the prototype surfaced the expected high-similarity patients.

for example, `P001` retrieved:

- `P005`, which shares worsening diabetes, pending specialist workflow, prior authorization delay, and denied claim
- `P003`, which shares a similar specialist workflow breakdown with incomplete documentation
- `P006`, which is clinically similar but operationally different because its referral was completed and the claim was paid

that third result is useful because it reveals a real design issue: clinical similarity and operational similarity should not always be collapsed into one score.

## Design Tension

the biggest flaw in a naive trajectory retrieval system is false confidence.

a system can retrieve patients that look similar in a compressed representation but are meaningfully different in the action they require.

for example, two patients may both have elevated A1C and endocrinology referrals. But one may have:

- completed referral
- approved authorization
- paid claim
- improving labs

while another may have:

- pending referral
- delayed authorization
- denied claim
- worsening labs

they are clinically related, but operationally very different.

this suggests a production system would need to separate:

- clinical similarity
- operational similarity
- payer/workflow similarity
- missing-data confidence
- site-specific documentation artifacts

## What a Real System Would Need

a production-grade version would need:

1. stronger ontology mapping across source systems  
2. explicit uncertainty scores around retrieved analogs  
3. human-in-the-loop review before high-impact workflow automation  
4. payer-aware workflow logic  
5. auditing for missingness and site-specific documentation patterns  
6. separate scoring for clinical similarity vs operational similarity  

## Why This Matters

the hardest part of healthcare AI may not be the model interface. it may be the representation layer underneath it.

if fragmented records can be transformed into reliable patient trajectories, then hospitals can reason across time: which patients are likely to fall through the cracks, which workflows are delayed, which approvals need escalation, and where revenue leakage may occur.

that is the core idea this prototype tries to explore in a very small way.