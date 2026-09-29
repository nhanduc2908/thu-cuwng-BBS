from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QDialog, QLabel, QVBoxLayout, QWidget


def show_photo_preview(parent: QWidget, title: str, photo_data: bytes) -> None:
    pixmap = QPixmap()
    if not pixmap.loadFromData(photo_data):
        raise ValueError("Ảnh tiếp nhận trong cơ sở dữ liệu không đọc được.")

    dialog = QDialog(parent)
    dialog.setWindowTitle(title)
    dialog.setMinimumSize(520, 420)
    layout = QVBoxLayout(dialog)
    image = QLabel()
    image.setAlignment(Qt.AlignmentFlag.AlignCenter)
    image.setPixmap(
        pixmap.scaled(
            900,
            700,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
    )
    layout.addWidget(image)
    dialog.exec()
