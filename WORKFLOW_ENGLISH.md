# System Workflow (English)

## Overview
The PetCare system workflow begins when the application is launched and ends when the user completes operational tasks such as pet management, inventory control, sales processing, services, membership updates, and reporting. The system is designed to maintain data integrity, enforce business rules, and record every significant action in an audit log.

## Workflow Description

1. Application startup
   - The system checks whether the SQLite database already exists.
   - If no database is present, it creates the required schema and tables.
   - It creates a default admin account with temporary credentials.
   - The admin is required to change the password during the first login.

2. Authentication
   - The user enters username and password.
   - The system validates the credentials against the stored salted hash.
   - If the credentials are invalid, the system displays an error and records a failed login in the audit log.
   - If the credentials are valid, the system checks whether the user must change the password.
   - A password change screen is shown when required.

3. Dashboard access
   - After a successful login, the system loads the main dashboard.
   - The dashboard centralizes access to all major modules: pet management, customer records, inventory, services, sales, memberships, and reports.

4. Pet management workflow
   - The user creates or updates a pet profile.
   - Information such as type, age, health status, housing, and owner details is recorded.
   - Medical and care records are attached to the pet profile.
   - The system stores the pet information and audit trail for future reference.

5. Customer management workflow
   - The user creates or updates customer information.
   - The customer is associated with one or more pets.
   - Financial records, service history, and deposits are tracked.
   - The system creates a linked history for customer transactions and relationship management.

6. Inventory workflow
   - The user adds or updates product records and SKUs.
   - Stock is imported, allocated, and tracked using quantity, batch, and expiry data.
   - The system checks low-stock and near-expiry conditions and triggers alerts.
   - Inventory updates are written to transaction history and audit logs.

7. Service workflow
   - The user creates an appointment for a pet and customer.
   - Staff are assigned and service fees are estimated.
   - The system updates status throughout the service lifecycle.
   - Completed or cancelled appointments are recorded and linked to billing and audit records.

8. Sales workflow
   - The user creates a sales order.
   - Membership discounts and pricing rules are applied automatically.
   - Payment or deposit is recorded.
   - Stock is reserved or deducted according to order status.
   - A bill is generated and saved in the database.

9. Membership workflow
   - The user creates a membership package.
   - A card is issued to the customer and linked with billing and rewards rules.
   - The system tracks activation, renewal, and payment status.
   - Membership benefits are applied when relevant sales or services occur.

10. Reporting and alert workflow
   - The system generates reports based on current inventory, sales, services, and membership records.
   - Alerts are triggered for stock shortages, upcoming expiries, pending invoices, and other operational risks.
   - Users may export reports to CSV or review the audit log for traceability.

11. Audit and continuity
   - Every significant action is stored in the audit log.
   - This allows the business to trace activity, manage accountability, and investigate unusual updates.
   - The process continues until the user logs out or closes the application.

## Flow Summary
The overall workflow of the system is: launch application → authenticate user → access dashboard → execute business function → validate business rules → update database → generate alerts/reports → save audit log → continue operations.
