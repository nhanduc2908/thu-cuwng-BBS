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
            "reports.view",
            "notifications.view",
        }
    ),
}

ROLE_LABELS = {
    "ADMIN": "Quản trị viên",
    "MANAGER": "Quản lý",
    "VETERINARIAN": "Bác sĩ thú y",
    "CAREGIVER": "Nhân viên chăm sóc",
    "SALES": "Nhân viên bán hàng",
}
