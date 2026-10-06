# Workflow Flowchart and Process Explanation

This document is intended to provide a solid process diagram and detailed explanation of the PetCare system flow. The flowchart is designed to show how the application behaves from startup to end-user operation and how the system connects login, business operations, rules validation, database updates, report generation, and audit tracking.

## 1. Application Startup Flow

```text
START
  |
  v
Check whether a database file exists
  |
  +--> No -> Initialize SQLite database
  |            -> Create necessary tables
  |            -> Create default admin account
  |            -> Assign temporary admin password
  |            -> Force first-login password change
  |
  +--> Yes -> Open login screen
  |
  v
Login screen
```

This is the first step in the system lifecycle. On first run, the application creates the SQLite database and default account because the project is designed to be usable immediately in a local environment. It also introduces a security requirement: the first admin login must change the default password. This is a strong design move because it reduces the risk of the default credentials being left in use.

## 2. Authentication Flow

```text
User enters username and password
  |
  v
Validate credentials against stored hash
  |
  +--> Invalid -> Display message -> Save failed login to audit log -> Return to login
  |
  +--> Valid -> Check whether password change is required
                      |
                      +--> Yes -> Open password change dialog -> Save new hash -> Continue
                      |
                      +--> No -> Continue to dashboard
```

Authentication is central because every system action depends on a trusted user identity. The system does not trust the UI alone. It verifies the user through the database and validates the password using secure hashing and salt. The workflow also logs both failures and successful login events. This approach is essential because it supports accountability and makes operational behavior traceable.

## 3. Main Dashboard Flow

```text
Successful login
  |
  v
Load dashboard
  |
  v
Display business overview and navigation
  |
  v
User chooses a module
```

The dashboard is the central navigation layer. It is the first screen that helps the user orient to the operational state of the business. It presents a broad view of the system and provides access to pet operations, customer data, inventory, sales, membership, reports, and alerts. The dashboard should be conceptualized as the operational nerve center of the project.

## 4. Business Module Flow

```text
Select module
  |
  +--> Pet Management
  |         -> Add/edit pet profile
  |         -> Link customers and care records
  |         -> Update health and intake information
  |
  +--> Customer Management
  |         -> Add/edit customer profile
  |         -> Link to pets and services
  |         -> Record transactions and membership history
  |
  +--> Inventory Management
  |         -> Add products and stock batches
  |         -> Track quantity and expiry
  |         -> Trigger low stock and near-expiry alerts
  |
  +--> Sales Management
  |         -> Create sales order
  |         -> Apply discounts and pricing rules
  |         -> Save payment/deposit records
  |         -> Update stock and customer records
  |
  +--> Service Management
  |         -> Create appointment
  |         -> Assign staff and service type
  |         -> Track status until completion
  |         -> Connect service history to customer and pet profile
  |
  +--> Membership Management
  |         -> Create membership package
  |         -> Assign card and benefits
  |         -> Track renewal and billing status
  |
  +--> Reporting and Alerts
            -> Generate reports
            -> Display stock, sales, and service summaries
            -> Save CSV export or operational alert data
```

This flow shows the system’s core business logic. Each module is interconnected and depends on the same underlying data model. This integration is one of the main strengths of the system because it mirrors real business operations rather than treating each area as isolated.

## 5. Record Validation and Business Rule Enforcement

After the user selects a module and enters data, the system validates the operation. This may include required data checks, rule checks, pricing checks, or status validation. The system applies business logic based on real operational rules rather than allowing random or invalid data to be written.

Examples:

- A sales order cannot be processed without valid product and customer data.
- A service may require a pet and customer record to exist.
- Inventory records must have valid stock and quantity values.
- Membership and billing logic must remain consistent with business requirements.

This validation step is important because it reduces data corruption and helps the software behave more like a real business system than a simple data-entry app.

## 6. Database Update Flow

```text
User completes action
  |
  v
Validate data and check business rules
  |
  v
Write transaction to database
  |
  v
Update dependent records and relationships
  |
  v
Generate alerts or notifications if relevant
  |
  v
Save record in audit log
```

Once the user completes a valid action, the database is updated. This may involve one or more tables depending on the operation. For example, a sales order may update sales records, customer history, and inventory counts. A membership update may affect customer billing and benefit state. A service update may affect appointment status and associated customer activity.

The database update flow is central because it keeps the application consistent and allows management to make decisions based on current operational data.

## 7. Reporting and Alert Generation Flow

```text
Business action is completed
  |
  v
System updates operational state
  |
  v
Reporting module reads current database state
  |
  v
Aggregates selected data by category
  |
  v
Produces dashboard metrics, tables, or CSV output
  |
  v
Displays alert if item quantity, price, expiry, or service state exceeds rule threshold
```

The system’s reporting and alerting flows are essential because they close the loop between operational events and managerial insight. They turn transaction data into decision support. Without this layer, the system would simply store records but no longer deliver business value.

## 8. Audit Log Flow

```text
Action is executed
  |
  v
System identifies whether the action is significant
  |
  +--> Significant -> Save audit record with timestamp, actor, and action type
  |
  +--> Non-significant -> No audit record or minimal record
```

Auditability is a major design feature. Every important business action registers in the system. Examples include login, password updates, deletion or modification of records, order creation, service status changes, inventory change logs, and membership change events. This makes the system more reliable and gives administrators confidence that actions are traceable.

## 9. End-of-Session Flow

```text
User chooses to logout or close app
  |
  v
System finalizes session state
  |
  v
Close active data transactions
  |
  v
Return to application shutdown or next startup
```

The end-of-session flow is intentionally simple. It ensures that the application closes cleanly and ensures data remains consistent. It is also important because the system is designed for a local desktop environment with persistent local state.

## 10. Full End-to-End Flowchart

```text
START
  |
  v
Initialize app and database
  |
  v
Check if first run
  |
  +--> Yes -> Create database -> Create default admin -> Force password change
  |
  +--> No -> Continue
  |
  v
Open login screen
  |
  v
Validate username/password
  |
  +--> Invalid -> Show error -> Save failed login -> Return to login
  |
  +--> Valid -> Check password change requirement
                       |
                       +--> Yes -> Prompt for password update -> Save new hash
                       |
                       +--> No -> Proceed
  |
  v
Load main dashboard
  |
  v
User selects module
  |
  v
Validate data and business rules
  |
  v
Update database tables and related records
  |
  v
Generate alert / bill / report if needed
  |
  v
Save audit log
  |
  v
Continue operations or logout
  |
  v
END
```

## 11. Interpretation of the Workflow

The workflow illustrates a complete business cycle rather than a technical process alone. It begins with secure access, then moves into operations, then into validation, then into persistence, and finally into reporting and accountability. This is essential because a functioning business system is not only about the database; it is about how users interact with the information throughout the day.

This workflow also highlights a fundamental principle: operational design should follow business reality. The application is modeled after a retail and service environment, not a generic database-driven demo. This is why PetCare feels more like an operational management product and less like an abstract student project.

## 12. Conclusion

The flowchart and narrative explain why PetCare is a strong project in functional systems design. The process is not fragmented or unrealistic. It is a consistent cycle from initialization to user login, to business operation, to data persistence, to report generation, and finally to audit-based accountability. This makes the system both technically coherent and practically useful for a real pet business scenario.
