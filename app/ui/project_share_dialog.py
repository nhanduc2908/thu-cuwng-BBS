from collections.abc import Callable

from PySide6.QtGui import QDesktopServices
from PySide6.QtCore import QUrl
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from app.project_share import ProjectShareServer


class ProjectShareDialog(QDialog):
    def __init__(
        self,
        parent,
        server: ProjectShareServer,
        manage_users: Callable[[], None],
    ) -> None:
        super().__init__(parent)
        self.server = server
        self.setWindowTitle("Chia sẻ dự án · Chế độ quan sát")
        self.setMinimumWidth(590)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Máy chủ chia sẻ chỉ đọc"))
        layout.addWidget(
            QLabel(
                "Chỉ phục vụ SC.HTML và website HTML cùng JSON tham khảo. "
                "Máy chủ này không cung cấp API SQLite, portal khách hàng hay thao tác sửa/xóa."
            )
        )

        self.status = QLabel()
        self.status.setWordWrap(True)
        layout.addWidget(self.status)

        self.address = QLineEdit()
        self.address.setReadOnly(True)
        self.address.setPlaceholderText("Khởi động máy chủ để tạo địa chỉ localhost")
        layout.addWidget(self.address)

        address_buttons = QHBoxLayout()
        self.start_button = QPushButton("Tạo địa chỉ / Bắt đầu chia sẻ")
        self.start_button.clicked.connect(self.start_server)
        self.stop_button = QPushButton("Dừng chia sẻ")
        self.stop_button.clicked.connect(self.stop_server)
        self.copy_button = QPushButton("Sao chép địa chỉ")
        self.copy_button.clicked.connect(self.copy_address)
        self.open_button = QPushButton("Mở trang báo cáo")
        self.open_button.clicked.connect(self.open_report)
        for button in (
            self.start_button,
            self.stop_button,
            self.copy_button,
            self.open_button,
        ):
            address_buttons.addWidget(button)
        layout.addLayout(address_buttons)

        layout.addWidget(
            QLabel(
                "Tài khoản người xem: tạo tài khoản nhân viên riêng với vai trò "
                "“Chuyên viên báo cáo” hoặc “Kiểm toán viên”, đặt mật khẩu mạnh "
                "(tối thiểu 10 ký tự) và đổi mật khẩu tạm trước khi chia sẻ. "
                "Quyền trên máy chủ này chỉ đọc website tĩnh."
            )
        )
        user_button = QPushButton("Mở quản lý tài khoản")
        user_button.clicked.connect(manage_users)
        layout.addWidget(user_button)

        layout.addWidget(
            QLabel(
                "Truy cập từ xa: máy chủ chỉ bind 127.0.0.1. Trên VPN riêng, cấu hình "
                "reverse proxy/serve của VPN trỏ về địa chỉ localhost bên trên. "
                "Với tunnel Internet, bắt buộc bật HTTPS, xác thực và allowlist người "
                "được mời tại nhà cung cấp tunnel; sau đó trỏ origin về localhost. "
                "Không mở cổng router/firewall trực tiếp và không chia sẻ link tunnel "
                "công khai. Tunnel/VPN phải được bạn cấu hình riêng; ứng dụng không tự "
                "tạo tài khoản nhà cung cấp hay tên miền Internet."
            )
        )
        layout.addWidget(
            QLabel(
                "Người xem phải đăng nhập bằng tài khoản REPORT_ANALYST hoặc AUDITOR. "
                "Phiên hết hạn sau 30 phút không hoạt động; đăng nhập/đăng xuất có ghi "
                "nhật ký. Dừng ở đây hoặc thoát ứng dụng sẽ tắt địa chỉ localhost."
            )
        )
        self.refresh_state()

    def refresh_state(self) -> None:
        base_url = self.server.base_url
        if self.server.is_running and base_url:
            self.address.setText(f"{base_url}/SC.HTML")
            self.status.setText("Đang chạy cục bộ · chỉ đọc · cần đăng nhập viewer.")
        else:
            self.address.clear()
            self.status.setText("Đã dừng. Nhấn “Tạo địa chỉ” để bắt đầu chia sẻ.")
        running = self.server.is_running
        self.start_button.setEnabled(not running)
        self.stop_button.setEnabled(running)
        self.copy_button.setEnabled(running)
        self.open_button.setEnabled(running)

    def start_server(self) -> None:
        try:
            self.server.start()
        except (OSError, TimeoutError, ValueError, FileNotFoundError) as error:
            QMessageBox.warning(self, "Không thể chia sẻ", str(error))
        self.refresh_state()

    def stop_server(self) -> None:
        self.server.stop()
        self.refresh_state()

    def copy_address(self) -> None:
        if not self.server.base_url:
            return
        QApplication.clipboard().setText(self.address.text())
        self.status.setText("Đã sao chép địa chỉ localhost. Địa chỉ này chỉ truy cập được trên máy chủ.")

    def open_report(self) -> None:
        if self.server.base_url:
            QDesktopServices.openUrl(QUrl(f"{self.server.base_url}/SC.HTML"))
