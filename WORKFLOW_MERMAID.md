# Workflow Diagram (Mermaid)

```mermaid
flowchart TD
    A[Start: Launch Application] --> B[Initialize SQLite Database]
    B --> C{Database exists?}
    C -- No --> D[Create database schema]
    D --> E[Create default admin account]
    E --> F[Set temporary password: admin]
    F --> G[Require password change on first login]
    C -- Yes --> H[Open Login Screen]
    G --> H

    H --> I[Enter username and password]
    I --> J{Credentials valid?}
    J -- No --> K[Display login error]
    K --> L[Save audit log: LOGIN_FAILED]
    L --> H

    J -- Yes --> M{Must change password?}
    M -- Yes --> N[Open Password Change Dialog]
    N --> O[Validate new password]
    O --> P[Hash password with salt]
    P --> Q[Save new credentials]
    Q --> R[Login success]
    R --> S[Save audit log: LOGIN_SUCCESS]
    M -- No --> S
    S --> T[Display Main Dashboard]

    T --> U[Select business module]
    U --> U1[Pet Management]
    U --> U2[Customer Management]
    U --> U3[Inventory Management]
    U --> U4[Service Scheduling]
    U --> U5[Sales and Billing]
    U --> U6[Membership Management]
    U --> U7[Reports and Alerts]

    U1 --> U1A[Add/Edit pet profile]
    U1A --> U1B[Attach care history]
    U1B --> U1C[Track health and intake records]
    U1C --> U1D[Save pet data and audit log]

    U2 --> U2A[Add/Edit customer]
    U2A --> U2B[Link customer to pet]
    U2B --> U2C[Track deposits and payments]
    U2C --> U2D[Save customer data and audit log]

    U3 --> U3A[Add product / SKU]
    U3A --> U3B[Import stock]
    U3B --> U3C[Track batch, expiry, and quantity]
    U3C --> U3D[Generate low-stock / near-expiry alerts]
    U3D --> U3E[Save inventory update and audit log]

    U4 --> U4A[Create appointment]
    U4A --> U4B[Assign staff]
    U4B --> U4C[Calculate service fee]
    U4C --> U4D[Track status: pending / in progress / completed / canceled / no-show]
    U4D --> U4E[Save appointment and audit log]

    U5 --> U5A[Create sales order]
    U5A --> U5B[Apply membership and discount rules]
    U5B --> U5C[Accept payment or deposit]
    U5C --> U5D[Update stock and payment status]
    U5D --> U5E[Generate bill and save audit log]

    U6 --> U6A[Create membership package]
    U6A --> U6B[Issue card and assign customer]
    U6B --> U6C[Track billing and renewal]
    U6C --> U6D[Activate or extend membership]
    U6D --> U6E[Save membership and audit log]

    U7 --> U7A[Generate inventory / sales / service reports]
    U7A --> U7B[Check operational alerts]
    U7B --> U7C[Export CSV and review audit log]
    U7C --> U7D[Decision / management action]

    U1D --> Z[End or continue next operation]
    U2D --> Z
    U3E --> Z
    U4E --> Z
    U5E --> Z
    U6E --> Z
    U7D --> Z
```

## Workflow Summary

The application starts by creating the database and default admin account if needed. The user then logs in and is authenticated through secure password validation. After passing authentication, the user can access the dashboard and operate across main business modules such as pet management, customer records, inventory, services, sales, membership, and reporting. Every business action triggers data updates and audit logging to protect operational integrity and traceability.
