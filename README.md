# PetCare — Pet Store Management System

PetCare is a Windows desktop application for managing a pet store business using Python, PySide6, and SQLite. The solution runs locally on a single machine without requiring a separate backend, web login service, or external AI provider. It is designed to support daily store operations such as animal intake, care tracking, customer management, inventory, sales, memberships, service scheduling, recommendations, and operational reporting.

## Overview

This project is a local-first business management system for a pet store and service center. It consolidates core operational workflows into one desktop application while keeping data in an embedded SQLite database. The design favors simplicity, local privacy, and independence from cloud infrastructure, making it suitable for small to medium-sized stores that need a reliable operational tool without a full SaaS installation.

The application includes:

- A local authentication system with admin setup and password rotation
- Role-aware access and audit logs
- Pet profile and intake records
- Housing, care, and health management
- Supplier and stock tracking
- Retail catalog and sales orders
- Memberships, cards, and bill management
- Service booking and appointment workflows
- Offline recommendation logic for product suggestions
- CSV export and operational reporting

## Key Features

### 1. Animal and care management

- Individual pet profiles with more than 25 recorded attributes
- Intake and check-in workflow before the animal is used in business operations
- Housing and capacity tracking
- Species suitability and enclosure history
- Health observations and care timeline
- 25-point operational checklist for care tasks

### 2. Inventory and supply management

- Batch and expiry tracking
- FEFO-style inventory selection
- Stock inflow/outflow logging
- Low-stock and soon-to-expire warnings
- Retail catalog with demo groups, SKUs, and combinations
- Product composition and membership pricing support

### 3. Sales and orders

- Sales order management with partial payment handling
- Reservation and deposit tracking
- Customer-specific membership pricing logic
- Inventory reservation for pending or partially paid orders
- Combo stock deduction rules and release of reserved inventory on cancellation

### 4. Membership and billing

- Membership packages and card issuance
- Payment scheduling and installment tracking
- Activation and extension rules based on invoice settlement
- Internal bill and status management
- Membership-based service discounts and allowances

### 5. Service scheduling and appointments

- Customer-to-pet appointment booking
- Staff assignment and service configuration
- Price estimation before saving a booking
- Appointment states including received, in progress, completed, canceled, and no-show
- Prepaid service usage tracking and release of unused slots

### 6. Recommendations and offline advisor

- Offline recommendation engine based on pet profile and inventory
- Budget-aware combo optimization
- Feedback for liked/disliked SKUs
- Explanation tags configured in the application
- Ranking evaluation based on recorded interaction data

### 7. Security and auditability

- Password hashing with PBKDF2-HMAC-SHA256 and random salt
- Mandatory password change on first login for the default admin account
- Audit log for write operations and authentication events
- Role-based area access for operational controls

## Technology Stack

- Python 3.10+
- PySide6 for the desktop UI
- SQLite for local data persistence
- Pytest for automated testing
- GitHub sync script for repository synchronization tasks

## Requirements

- Windows 10/11
- Python 3.10 or newer (Python 3.13 is recommended)
- Internet access only for installing Python dependencies

## Installation

Open PowerShell in the project folder and run:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

If Python 3.13 is not available on the system, replace `-3.13` with the installed version such as `-3.12` or `-3.11`.

You can also activate the virtual environment manually and run the app from there:

```powershell
.\.venv\Scripts\Activate.ps1
python main.py
```

## Running the Application

From the project root:

```powershell
.\.venv\Scripts\python.exe main.py
```

On the first launch, the application creates a default admin account:

- Username: `admin`
- Temporary password: `admin`

The user is required to change the password immediately after the first successful login. Passwords are stored using PBKDF2-HMAC-SHA256 hashing with a unique salt.

## Resetting the Default Admin Account

If you need to restore the default admin login on a machine that already contains data, run:

```powershell
.\.venv\Scripts\python.exe main.py --reset-admin
```

This resets the admin password to `admin`, unlocks the admin account, and forces a password change on the next sign-in. Use this only on a trusted Windows account and do not leave the temporary default password in production use.

## Data Storage and Backup

By default, SQLite is stored under the user's local application data folder:

```text
%LOCALAPPDATA%\PetStoreManagement\pet_store.db
```

The application creates the directory, schema, and tables automatically on startup. Pet intake documents and associated record data are stored in SQLite. A backup directory can be configured inside the application, and regular backups are strongly recommended because the database contains customer, operational, and health-related information.

## Application Modules

The UI includes multiple operational areas:

1. Platform and data
2. Accounts, roles, and logs
3. Dashboard
4. Pet profiles
5. Housing and enclosure management
6. Suppliers
7. Imports, handover photos, and intake checks
8. Health
9. Care and checklists
10. Customers
11. Reservations, deposits, and refunds
12. Orders and payments
13. Memberships, cards, and bills
14. Services and scheduling
15. Inventory for food, medicine, and supplies
16. Reports
17. Alerts and backup

## Business Scope and Operational Notes

The project includes a broad set of workflows that are useful for a real pet business, but it also has intentional limitations:

- Membership functions are designed as internal administration tools for existing customer data; they are not a public online signup or customer portal.
- Seed catalog data is demo and documentation-based rather than verified local pricing. It is intended as a starting dataset that a store can review and adjust.
- Inventory quantities are not auto-generated from supplier data. Actual stock must be entered manually before sales.
- Feed and nutrition profiles are catalog classification tools rather than medical instructions. They do not replace veterinary advice.
- Service package pricing and fees are reference data and should be validated before use in live operations.
- Payment collection is handled by staff confirmation within the application; there is no payment gateway, QR payment integration, or automatic renewal workflow.
- Membership bills are internal records and are not designed as legal tax invoices or PDF exports.
- The recommendation advisor is a local rules-based system rather than a generative AI or external ML service.

## Project Structure

```text
main.py
requirements.txt
workflow.html
app/
  database.py
  modules/
    animals/
    audit/
    auth/
    care/
    customers/
    dashboard/
    health/
    imports/
    inventory/
    memberships/
    notifications/
    nutrition/
    recommendations/
    sales/
    services/
    store/
    suppliers/
  ui/
    auth/
    animals/
    care/
    customers/
    dashboard/
    health/
    imports/
    inventory/
    memberships/
    notifications/
    platform/
    reservations/
    sales/
    services/
    store/
    suppliers/
    main_window.py
scripts/
  github_sync.py
tests/
```

- `main.py` is the entry point and initializes the application
- `app/database.py` centralizes the SQLite schema, access control, and auditing layer
- `app/modules/` contains business logic and repository access patterns
- `app/ui/` contains the PySide6 user interface
- `tests/` contains end-to-end and functional test coverage

## Workflow Diagram

Open [workflow.html](./workflow.html) in a modern browser to view the application flow for login, animal intake, care, sales, services, membership, recommendations, inventory, and reporting operations. The diagram can be printed or saved as a PDF for internal documentation.

## Testing

Run the full automated suite with:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

If Qt-based tests are running without showing a visible window, use offscreen rendering:

```powershell
$env:QT_QPA_PLATFORM = "offscreen"
.\.venv\Scripts\python.exe -m pytest -q
```

## GitHub Sync

After configuring a Git remote and authenticating through Git Credential Manager, you can synchronize the project with:

```powershell
.\.venv\Scripts\python.exe scripts\github_sync.py --message "Describe your change"
```

This script only uploads approved files to GitHub. It does not sync the SQLite database, intake images, virtual environments, bytecode, or secret files. Always review the file list and remote configuration before running a sync.

## Demo Catalog Notes

The application includes demo seed data for a retail pet catalog, including:

- Dog food, cat food, wet food, and snacks
- Grooming and hygiene products
- Litter and pet accessories
- Toys, collars, bowls, and furniture
- Travel accessories, clothing, and enrichment items
- Nutrition and vitamin products
- Small animal, fish, bird, and reptile catalog entries

Sample data includes roughly 20 product groups and about 600 demo SKUs, along with eight example combos. The seed catalog is designed to help the store review and tune the product structure before live deployment. Brand names, barcodes, product photos, and detailed composition metadata are not inferred automatically and may need to be completed manually inside the application.

## Operational Security Guidance

- Keep the local machine secured and restrict access to the SQLite data folder
- Use a strong password for the admin account after first login
- Regularly back up the database and intake file store
- Restrict user permissions according to staff responsibilities
- Treat the software as an internal operations system, not a public-facing commerce platform

## License and Usage

This project is intended for internal business management and operational use. It is best suited for locally managed pet stores, grooming services, animal care operations, and small retail environments that need a practical desktop tool without external infrastructure.

## Summary

PetCare is a desktop-first management platform for pet stores and service businesses. It combines transactional operations, customer records, inventory tracking, service scheduling, and operational reporting into a single local application. It is especially useful for stores that want a privacy-friendly, offline-capable, and self-contained business system without requiring a cloud-hosted backend.
