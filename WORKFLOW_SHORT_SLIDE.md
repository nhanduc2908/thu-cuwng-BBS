# Short Workflow for One Slide

```mermaid
flowchart LR
    A[Login] --> B{Valid user?}
    B -- No --> C[Error + Audit Log]
    B -- Yes --> D[Dashboard]
    D --> E[Select Module]
    E --> F[Pet / Customer / Inventory / Service / Sales / Membership]
    F --> G[Validate Data + Business Rules]
    G --> H[Update Database]
    H --> I[Generate Alert / Bill / Report]
    I --> J[Save Audit Log]
    J --> K[Continue Operations]
```

## Presentation note
This one-slide workflow summarizes the operational cycle of the system: authentication → main dashboard → business module → validation → database update → alerts/reporting → audit trail.
