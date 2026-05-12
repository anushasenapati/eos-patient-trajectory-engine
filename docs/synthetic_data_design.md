# Synthetic Data Design

This project uses fully synthetic patient records. The goal is not to make clinically valid predictions or simulate real patients. The goal is to test the representation problem of whether fragmented healthcare records can be normalized into comparable patient trajectories?

## Design Principle

The synthetic dataset is scenario-based rather than random. Each patient represents a specific care or operational trajectory archetype.

## Patient Archetypes

| Patient | Archetype | Expected System Behavior |
|---|---|---|
| P001 | Worsening diabetes + pending endocrinology referral + delayed prior authorization + denied claim | Should be flagged for care gap and revenue leakage risk |
| P002 | Stable routine care + completed nutrition referral | Should be low risk |
| P003 | Worsening diabetes + delayed specialist authorization + incomplete referral documentation | Should retrieve as similar to P001/P005 |
| P004 | Preventive routine visit with no major care gap | Should be low risk |
| P005 | Worsening diabetes + patient has not heard back about specialist approval + denied claim | Should retrieve as highly similar to P001 |
| P006 | Elevated diabetes risk but completed endocrinology referral and improved A1C | Should show improved trajectory after intervention |
| P007 | Severe hyperglycemia requiring emergency escalation | Should show late escalation/high severity |
| P008 | Delayed imaging review + authorization pending + denied imaging claim | Should show non-diabetes operational bottleneck |

## Source Systems

The dataset is fragmented across simulated systems:

- lab results
- EHR visits
- referral management
- payer prior authorizations
- billing/claims
- clinical notes

Each source has a different schema, requiring harmonization into a shared event model.

## Evaluation Intent

The retrieval engine should compare full patient trajectories, not isolated notes or visits.

For example, P001 should retrieve P005 and P003 because they share worsening chronic disease, specialist workflow delay, and reimbursement risk.

## Limitations

This dataset is synthetic and intentionally small. It is not clinically validated, not statistically representative, and not suitable for care decisions. It exists only to demonstrate event harmonization, trajectory retrieval, and operational intervention logic.