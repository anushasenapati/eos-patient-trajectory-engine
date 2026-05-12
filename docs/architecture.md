# Architecture

this prototype is intentionally small, but it mirrors a real healthcare data infrastructure pattern:

1. fragmented source systems
2. event harmonization
3. longitudinal patient timelines
4. trajectory retrieval
5. operational forecast and workflow trigger

## System Flow

```mermaid
flowchart TD
    A[Fragmented Source Systems] --> B[Data Loader]

    A1[Labs] --> A
    A2[Visits] --> A
    A3[Referrals] --> A
    A4[Prior Authorizations] --> A
    A5[Claims] --> A
    A6[Clinical Notes] --> A

    B --> C[Harmonization Layer]

    C --> D[Unified PatientEvent Table]

    D --> E[Patient Timeline Builder]
    D --> F[Trajectory Text Builder]
    D --> G[Forecast Engine]

    F --> H[TF-IDF Vectorizer]
    H --> I[Cosine Similarity Retrieval]

    I --> J[Similar Historical Trajectories]
    G --> K[Operational Risks + Workflow Actions]

    J --> L[Streamlit Prototype UI]
    K --> L
    E --> L