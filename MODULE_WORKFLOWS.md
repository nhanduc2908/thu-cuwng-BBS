# Module-Specific Workflows

## 1. Authentication Workflow

```mermaid
flowchart TD
    A[Open App] --> B[Check user session]
    B --> C{Session exists?}
    C -- Yes --> D[Open dashboard]
    C -- No --> E[Open login screen]
    E --> F[Enter username/password]
    F --> G{Credentials valid?}
    G -- No --> H[Display error]
    H --> I[Audit: LOGIN_FAILED]
    I --> E
    G -- Yes --> J{Password change required?}
    J -- Yes --> K[Open password update dialog]
    K --> L[Validate and save new password]
    L --> M[Audit: LOGIN_SUCCESS]
    J -- No --> M
    M --> D
```

## 2. Pet Management Workflow

```mermaid
flowchart TD
    A[Open Pet Module] --> B[Create or select pet]
    B --> C[Enter profile details]
    C --> D[Attach care and health data]
    D --> E[Upload photo / intake documents]
    E --> F[Link to owner and location]
    F --> G[Save pet record]
    G --> H[Audit log: PET_CREATED or PET_UPDATED]
    H --> I[Display updated pet profile]
```

## 3. Inventory Workflow

```mermaid
flowchart TD
    A[Open Inventory Module] --> B[Add or edit product]
    B --> C[Define SKU, price, expiry, stock]
    C --> D[Receive stock]
    D --> E[Update quantity and batch records]
    E --> F{Low stock or expiry risk?}
    F -- Yes --> G[Generate alert]
    F -- No --> H[Continue]
    G --> I[Save inventory transaction]
    H --> I
    I --> J[Audit log: INVENTORY_UPDATED]
```

## 4. Sales Workflow

```mermaid
flowchart TD
    A[Open Sales Module] --> B[Create order]
    B --> C[Select customer and items]
    C --> D[Apply discounts and membership rules]
    D --> E[Record payment or deposit]
    E --> F{Full payment?}
    F -- No --> G[Reserve stock and keep pending order]
    G --> H[Save bill and audit log]
    F -- Yes --> I[Deduct stock and finalize order]
    I --> H
    H --> J[Display receipt / order status]
```

## 5. Service Workflow

```mermaid
flowchart TD
    A[Open Service Module] --> B[Create appointment]
    B --> C[Select pet, customer, and service]
    C --> D[Assign staff and calculate fee]
    D --> E[Save appointment]
    E --> F[Track status updates]
    F --> G{Completed or canceled?}
    G -- Completed --> H[Finalize service and create bill]
    G -- Canceled --> I[Release reserved slot / refund if applicable]
    H --> J[Audit log: SERVICE_UPDATED]
    I --> J
    J --> K[Display updated service status]
```

## 6. Membership Workflow

```mermaid
flowchart TD
    A[Open Membership Module] --> B[Create membership package]
    B --> C[Assign package to customer]
    C --> D[Issue membership card]
    D --> E[Track billing and payment]
    E --> F{Membership fully paid?}
    F -- No --> G[Keep inactive / pending state]
    F -- Yes --> H[Activate or extend membership]
    G --> I[Save billing status and audit log]
    H --> I
    I --> J[Apply benefits in future purchases]
```

## 7. Reporting Workflow

```mermaid
flowchart TD
    A[Open Reports Module] --> B[Select report type]
    B --> C[Inventory / Sales / Services / Membership]
    C --> D[Query current database records]
    D --> E[Generate summary and alert data]
    E --> F[Export CSV or view dashboard]
    F --> G[Save management review log]
```
