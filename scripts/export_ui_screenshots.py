import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from app.database import Database
from app.ui.main_window import MainWindow

ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = ROOT / "report_assets"
ASSETS_DIR.mkdir(exist_ok=True)

TARGETS = {
    "dashboard": "dashboard",
    "inventory": "inventory",
    "sales": "sales",
    "customers": "customers",
    "services": "services",
    "reports": "reports",
}


def save_widget_screenshot(widget, output_path: Path) -> None:
    widget.show()
    widget.raise_()
    widget.activateWindow()
    app = QApplication.instance()
    app.processEvents()
    pixmap = widget.grab()
    if pixmap.isNull():
        raise RuntimeError(f"Không tạo được ảnh cho {output_path.name}")
    pixmap = pixmap.scaled(
        1920,
        1080,
        Qt.AspectRatioMode.IgnoreAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )
    pixmap.save(str(output_path), "PNG")
    print(f"Saved {output_path.name}")


def main() -> None:
    app = QApplication.instance() or QApplication(sys.argv)
    db_path = ROOT / "temp_report_database.db"
    if db_path.exists():
        db_path.unlink()
    database = Database(db_path)
    database.create_default_admin()

    user = {
        "id": 1,
        "username": "admin",
        "display_name": "Administrator",
        "role": "ADMIN",
    }
    window = MainWindow(database, user)
    window.resize(1920, 1080)
    window.show()
    app.processEvents()

    pages_by_name = {
        page_name: page
        for page_name, page in {
            "dashboard": window.dashboard,
            "inventory": window.inventory,
            "sales": window.sales,
            "customers": window.customers,
            "services": window.services,
            "reports": window.reports,
        }.items()
    }

    for page_name, file_name in TARGETS.items():
        page = pages_by_name[page_name]
        window.pages.setCurrentWidget(page)
        app.processEvents()
        save_widget_screenshot(page, ASSETS_DIR / f"{file_name}.png")

    database.close()
    db_path.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
