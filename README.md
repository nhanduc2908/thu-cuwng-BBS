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

## HTML Website Integration

The desktop application serves the complete `HTML` folder through its local web bridge. After signing in, use **Mở website** in the top bar to open the central project hub, or **Quản trị web** to open the HTML admin workspace. The project hub links to the branded website, the new PetCare Enterprise Console, supporting project materials, and the full module library. The pages are organized into two folders:

- `HTML/TRrang chính/` contains the public-facing homepage, customer portal, product and nutrition pages, workflow, and `petcare_management.html` operations console.
- `HTML/Trang hỗ trợ/` contains project proposals, reports, admin and demo screens, and the 17-module library under `Module/`.
- `HTML/Trang hỗ trợ/data_explorer.html` provides on-demand browsing, search, pagination, JSON downloads, and CSV export for the prepared module, disease, and nutrition catalogs in `HTML/data/`. Catalogs are not fetched until selected.
- `HTML/TRrang chính/petcare_management.html` reads the prepared `module_*.json` demo datasets for its dashboard metrics, pet list, care chart, and alerts. These JSON records are synthetic demo data; real operational records remain in the local SQLite database.

`HTML/index.html` is the central project hub. Relative CSS, JavaScript, image, data, preview, and page links are served from the same local site.
`HTML/menu.html` is a standalone, searchable list menu containing direct links to the hub, every main-site and support page, and all 17 module pages. Each entry shows its actual relative URL within the served `HTML` site.
Every HTML page loads `HTML/scripts/site_navigation.js`, which supplies the same responsive PetCare header, grouped searchable directory with direct links to the HTML pages, a collapsible page guide with usage steps and checks, and the back/home shortcuts.

The Python sidebar's **Bản đồ trang HTML & Python** scans the HTML tree, labels navigation, reference, demo and interactive module pages, and opens eligible HTML or Python pages directly. All 17 module reference pages have corresponding Python operational screens; the HTML module pages describe workflows and are not CRUD replacements. The HTML data explorer has a Python catalog counterpart. Nutrition pages remain product/reference guides rather than full replacements for inventory operations. The HTML admin workspace is a partial browser alternative; use the typed Python screens for complete operational workflows.

### Shared staff login accounts

On the first normal application startup after this update, the desktop app provisions the ten supplied staff usernames and roles in the same SQLite `users` table used by desktop authentication and the HTML bridge. Passwords are stored as salted PBKDF2-HMAC-SHA256 hashes. The seeding runs once; existing same-name accounts are never reset or re-enabled, and a username already assigned to another role is reported instead of overwritten.

The `admin / admin` account is a temporary bootstrap login and must have its password changed in the desktop app before it can sign in to the HTML workspace. The other supplied role accounts can sign in to both the desktop app and HTML bridge. These are shared default credentials: change them in **Tài khoản & nhật ký** before sharing the system or allowing anyone else to access the machine. The HTML workspace continues to enforce each account's SQLite role permissions.

`HTML/TRrang chính/user_portal.html` is the customer portal entry point. Customer accounts are separate from staff accounts: self-registration remains pending until staff links it to an existing customer profile, or staff can issue a one-time invite valid for 24 hours. Customers can view only records attached to their linked customer profile. The Python sidebar provides **Tài khoản portal khách hàng** for staff with `sales.manage` to review registrations, create invitations, and expire active invitations. Invitation codes are shown only once and must be sent to the intended customer securely.

Customer portal routes are enabled only when the bridge binds to a loopback address. The customer session uses a separate HttpOnly, SameSite cookie from staff login. This is a local workflow, not a public hosting backend; public Internet access requires a separately deployed and security-reviewed service.

### Shared HTML/Python JSON catalog and SQLite transfer

`HTML/data/` currently contains 26 dataset JSON files and the shared `catalog_manifest.json`: 17 module reference/demo datasets, generated disease catalogs, generated nutrition catalogs, a 70-field product specification, four partial source-backed product references, and a global brand-directory reference. The module `demoData` and disease records identify themselves as synthetic; nutrition entries are generated catalog combinations. These files are not verified store inventory, medical records, customers, pets, prices, or operational transactions. The combined disease and all-species nutrition files overlap their per-species source catalogs and are marked as derived. For backwards compatibility, `nutrition_catalog_4000.json` keeps its existing name even though it contains 8,000 generated product rows plus breed and feeding-profile rows.

`HTML/Trang thông số của các sản phẩm/index.html` provides a 70-field product reference schema and currently four Royal Canin Vietnam product-page references. These are partial source-backed records, not a complete market catalog: label values not found on the cited source remain unfilled, product packaging must be checked, and one Medium Adult page has a URL slug mismatch noted in its record. The schema covers identity, suitability, directions and safety, nutrition analysis, active ingredients, and source verification. No nutrition values are estimated; veterinary medicines must be used only according to their current label and veterinary advice. The older generated nutrition catalogs are explicitly illustrative and must not be used for purchase or health decisions.

`HTML/Trang thông số của các sản phẩm/thuong-hieu.html` is a searchable global brand and product-line directory organized by the countries/market sections in the user-provided list. Every entry is marked unverified: section placement is not proof of origin, manufacturing location, ownership, current distribution, market share, product quality, or nutrition suitability. Corporate ownership and promotional/market-share claims from the supplied list are intentionally not presented as confirmed facts. Each brand links into the in-system product catalog with a brand filter; directly verified product-source links are shown only for SKU records already present. The current SKU coverage is limited to four partial Royal Canin references. The agreed expansion order is all verifiable Vietnam-market SKUs first, then a separately identifiable international catalog; do not treat a brand link as proof that all of its SKUs are listed.

`HTML/data/catalog_manifest.json` is the shared source index used by the HTML Data Explorer and the Python desktop data-catalog screen. It lists the JSON file, display label, record array, provenance class, and whether a catalog is derived/overlapping. Unknown JSON files remain discoverable in Python but are marked unverified; the manifest is not treated as an importable record dataset.

The Python desktop sidebar adds **Danh mục JSON & nhập SQLite**. Users with `reports.view` can inspect sources; importing requires `settings.manage`. Use `scripts/import_html_data_to_sqlite.py` to validate and transfer the same JSON documents into separate `html_data_sources` and `html_data_records` SQLite staging tables. By default it performs validation and a count/hash preview only:

```powershell
.\.venv\Scripts\python.exe scripts\import_html_data_to_sqlite.py --database HTML\data\petcare_reference.sqlite
```

To apply the import:

```powershell
.\.venv\Scripts\python.exe scripts\import_html_data_to_sqlite.py --database HTML\data\petcare_reference.sqlite --apply
```

The desktop screen and CLI default to the local `HTML/data/petcare_reference.sqlite` file (ignored by Git to avoid publishing large generated catalogs). Re-importing a source replaces only that source's staged records, while preserving other datasets and unrelated application tables. Original JSON documents, SHA-256 hashes, classification, overlap flags, and searchable object-array rows are retained. This is a data-preserving transfer layer, not a loader into operational customer, pet, inventory, health, booking, or order tables. Replace generated/demo content with verified business and veterinary sources before making it available as live customer-facing data.

### Operational dataset workspace

The 17 module detail pages and the Enterprise Console include a permission-checked data workspace when served by the local Python bridge. Sign in with an application account; module permissions control view and edit access. The workspace provides:

- **SQLite nghiệp vụ · chỉ xem** for the live operational records already managed by the desktop application. Selecting this source explicitly refreshes actual database records; it is not a write path.
- **JSON đã chuẩn bị · CRUD có backup** for the `demoData` records in the selected `HTML/data/module_*.json` file. Add/edit operations write atomically and keep a backup beside the application database; archive marks a record instead of deleting it.
- **SQLite workspace · JSON đã nhập** for a separate, persistent snapshot of prepared JSON records. Import skips keys already imported; the copied workspace supports add, edit, and archive without silently changing live operational tables.

Use the **Mở website** button in the desktop application or the displayed local-bridge link; `file://` pages cannot authenticate or perform writes. Informational pages, aggregate modules, audit history, and system reports remain read-only. Dataset JSON is synthetic/demo content, not real customer or animal records.

This workspace provides generic prepared-dataset record management, not domain-specific CRUD for live animals, customers, health records, care tasks, or inventory. Live application SQLite data is read-only here; real operational changes must use the desktop application until typed web operations are provided.

The bridge listens only on `127.0.0.1`; its SQLite APIs require web authentication and enforce the same role permissions as the desktop application. If the bridge cannot start, the desktop modules remain available, while the web buttons are disabled.

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
