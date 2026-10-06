ROLE_PERMISSIONS = {
    "ADMIN": frozenset(
        {
            "dashboard.view",
            "animals.view",
            "animals.manage",
            "health.view",
            "health.manage",
            "care.view",
            "care.manage",
            "store.view",
            "store.manage",
            "imports.view",
            "imports.manage",
            "sales.view",
            "sales.manage",
            "membership.view",
            "membership.manage",
            "services.view",
            "services.manage",
            "services.catalog.manage",
            "inventory.view",
            "inventory.manage",
            "reports.view",
            "notifications.view",
            "settings.manage",
            "users.manage",
            "audit.view",
        }
    ),
    "MANAGER": frozenset(
        {
            "dashboard.view",
            "animals.view",
            "animals.manage",
            "health.view",
            "health.manage",
            "care.view",
            "care.manage",
            "store.view",
            "store.manage",
            "imports.view",
            "imports.manage",
            "sales.view",
            "sales.manage",
            "membership.view",
            "membership.manage",
            "services.view",
            "services.manage",
            "services.catalog.manage",
            "inventory.view",
            "inventory.manage",
            "reports.view",
            "notifications.view",
            "settings.manage",
            "audit.view",
        }
    ),
    "VETERINARIAN": frozenset(
        {
            "dashboard.view",
            "animals.view",
            "health.view",
            "health.manage",
            "care.view",
            "inventory.view",
            "inventory.manage",
            "reports.view",
            "notifications.view",
        }
    ),
    "CAREGIVER": frozenset(
        {
            "dashboard.view",
            "animals.view",
            "health.view",
            "care.view",
            "care.manage",
            "services.view",
            "services.manage",
            "inventory.view",
            "inventory.manage",
            "reports.view",
            "notifications.view",
        }
    ),
    "SALES": frozenset(
        {
            "dashboard.view",
            "animals.view",
            "store.view",
            "imports.view",
            "sales.view",
            "sales.manage",
            "membership.view",
            "membership.manage",
            "services.view",
            "services.manage",
            "reports.view",
            "notifications.view",
        }
    ),
    "INVENTORY_MANAGER": frozenset(
        {
            "dashboard.view",
            "imports.view",
            "imports.manage",
            "inventory.view",
            "inventory.manage",
            "reports.view",
            "notifications.view",
        }
    ),
    "SERVICE_COORDINATOR": frozenset(
        {
            "dashboard.view",
            "services.view",
            "services.manage",
            "membership.view",
            "reports.view",
            "notifications.view",
        }
    ),
    "CUSTOMER_SUPPORT": frozenset(
        {
            "dashboard.view",
            "animals.view",
            "sales.view",
            "membership.view",
            "services.view",
            "reports.view",
            "notifications.view",
        }
    ),
    "REPORT_ANALYST": frozenset(
        {
            "dashboard.view",
            "reports.view",
        }
    ),
    "AUDITOR": frozenset(
        {
            "dashboard.view",
            "reports.view",
            "audit.view",
        }
    ),
}

ROLE_LABELS = {
    "ADMIN": "Quản trị viên",
    "MANAGER": "Quản lý",
    "VETERINARIAN": "Bác sĩ thú y",
    "CAREGIVER": "Nhân viên chăm sóc",
    "SALES": "Nhân viên bán hàng",
    "INVENTORY_MANAGER": "Quản lý kho",
    "SERVICE_COORDINATOR": "Điều phối dịch vụ",
    "CUSTOMER_SUPPORT": "Chăm sóc khách hàng",
    "REPORT_ANALYST": "Chuyên viên báo cáo",
    "AUDITOR": "Kiểm toán viên",
}

ROLE_LABELS_EN = {
    "ADMIN": "Administrator",
    "MANAGER": "Store manager",
    "VETERINARIAN": "Veterinarian",
    "CAREGIVER": "Caregiver",
    "SALES": "Sales associate",
    "INVENTORY_MANAGER": "Inventory manager",
    "SERVICE_COORDINATOR": "Service coordinator",
    "CUSTOMER_SUPPORT": "Customer support",
    "REPORT_ANALYST": "Report analyst",
    "AUDITOR": "Auditor",
}
