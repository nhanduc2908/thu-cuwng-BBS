# Quản lý thú cưng

Ứng dụng desktop Python cho cửa hàng thú cưng, xây dựng bằng PySide6 và SQLite.
Giao diện và dữ liệu chạy cục bộ trên Windows, không cần máy chủ riêng.

## Chức năng hiện có

- Dashboard thống kê tổng số, đang bán, đã bán và đang điều trị.
- Quản lý hồ sơ động vật: thêm, tìm kiếm, lọc trạng thái, sửa và xóa.
- Trạng thái động vật có tập giá trị cố định, tránh nhập trạng thái tùy ý.
- Hồ sơ sức khỏe: ghi nhận ngày khám, tình trạng, chẩn đoán, điều trị và bác sĩ.
- Chăm sóc: tạo lịch công việc, phân công và đánh dấu hoàn thành.
- Chuồng trại: quản lý mã/khu vực/loài/sức chứa, gán hoặc chuyển động vật, xem lịch sử vị trí; kiểm tra sức chứa và tính tương thích loài.
- Hồ sơ mỗi động vật có đúng 25 đặc điểm, gồm định danh, nguồn gốc, nhận dạng, sức khỏe và nhu cầu chăm sóc.
- Checklist chăm sóc/sức khỏe 25 mục theo cá thể và ngày; mỗi mục có kết quả, ghi chú và người kiểm tra. Có thể mở lại để cập nhật cùng ngày.
- Ràng buộc khóa ngoại để bảo vệ lịch sử sức khỏe/chăm sóc khi xóa hồ sơ.

## Các module và giao diện

Sơ đồ quy trình nghiệp vụ dạng HTML có thể mở trực tiếp bằng trình duyệt:
[workflow.html](./workflow.html). Trang gồm workflow tổng thể, tiếp nhận động vật,
chăm sóc, đặt chỗ/bán hàng, tồn kho và báo cáo/vận hành; hỗ trợ in hoặc lưu PDF.

- **Tổng quan:** thống kê tồn động vật theo trạng thái và danh sách hồ sơ mới.
- **Động vật:** bảng tra cứu, tìm kiếm/lọc và biểu mẫu 25 trường để thêm/sửa hồ sơ.
- **Sức khỏe:** bảng lịch sử khám và biểu mẫu ghi nhận khám.
- **Chăm sóc:** bảng lịch công việc, tạo/hoàn thành tác vụ và nút mở checklist 25 mục.
- **Chuồng trại:** danh sách chuồng và số chỗ, quản lý chuồng hoạt động/ngừng hoạt động, danh sách con vật đang ở và lịch sử phân chuồng.
- **Nhà cung cấp & nhập:** quản lý nhà cung cấp, lô nhập, hồ sơ cá thể trong lô, kết quả kiểm tra đầu vào và lịch sử kiểm tra.
- **Khách hàng & bán hàng:** quản lý hồ sơ khách, giữ chỗ và tiền cọc, lập đơn bán, ghi nhận thanh toán từng phần, theo dõi công nợ và hoàn cọc trước khi giải phóng chỗ.
- **Thức ăn & thuốc:** quản lý vật tư theo lô/hạn sử dụng, nhập kho, xuất dùng theo FEFO, gắn lần xuất với cá thể, theo dõi sổ giao dịch và cảnh báo tồn thấp/hết hạn.
- **Báo cáo:** tổng hợp tồn kho, đơn hàng/thanh toán và hồ sơ sức khỏe theo khoảng ngày, có thể xuất CSV.
- **Cảnh báo & sao lưu:** nhắc tồn thấp, hạn sử dụng, công việc chăm sóc đến hạn và giữ chỗ quá hạn; sao lưu SQLite vào thư mục cấu hình.
- **Tài khoản & phân quyền:** thiết lập quản trị viên lần đầu, đăng nhập, đổi mật khẩu, vai trò theo chức năng và khóa/mở khóa nhân viên.
- **Nhật ký thao tác:** ghi lại đăng nhập, thay đổi tài khoản và các thao tác ghi dữ liệu; nhật ký được bảo vệ khỏi sửa/xóa thông thường.

Checklist gồm khẩu phần/nước, thể trạng, da/lông, giác quan, vận động, bài tiết,
hành vi, môi trường sống, vệ sinh, an toàn, vaccine, ký sinh trùng và thuốc/tái khám.
Đây là danh sách theo dõi vận hành, không thay thế chẩn đoán hoặc hướng dẫn của bác sĩ thú y.

## Yêu cầu

- Python 3.10+
- PySide6

## Cài đặt và chạy

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

Luôn cài và chạy bằng cùng một Python. Nếu chạy bằng Python 3.12, thay `-3.13`
thành `-3.12`. Không chạy `main.py` bằng một bản Python khác chưa cài PySide6.

Trên Windows, cơ sở dữ liệu được lưu tại `%LOCALAPPDATA%\PetStoreManagement\pet_store.db`.
Ứng dụng tự tạo thư mục và các bảng ở lần chạy đầu tiên.
Ở lần mở đầu tiên, ứng dụng yêu cầu tạo tài khoản quản trị; từ lần sau cần đăng nhập.
Không có mật khẩu mặc định. Mật khẩu được dẫn xuất bằng PBKDF2-HMAC-SHA256 và salt ngẫu nhiên.

## Kiểm thử

```powershell
python -m pytest
```

## Cấu trúc

```text
app/
  database.py       # Schema, migration và facade tương thích
  main_window.py    # Import tương thích cho cửa sổ chính
  modules/          # Nghiệp vụ và truy cập dữ liệu theo chức năng
    animals/
      constants.py
      repository.py
    health/
      repository.py
    care/
      constants.py
      repository.py
    dashboard/
      repository.py
    store/
      repository.py  # Chuồng trại, sức chứa và lịch sử vị trí
    suppliers/
      repository.py  # Nhà cung cấp
    imports/
      constants.py
      repository.py  # Lô nhập, cá thể nhập và kiểm tra đầu vào
    inventory/
      repository.py  # Tồn kho theo lô, FEFO và sổ nhập/xuất
    reports/
      repository.py  # Truy vấn tồn kho, bán hàng và sức khỏe
    notifications/
      repository.py  # Cảnh báo vận hành
    auth/
      constants.py   # Vai trò và quyền theo chức năng
      security.py    # Băm/kiểm tra mật khẩu
      repository.py  # Đăng nhập, tài khoản, đổi mật khẩu
    audit/
      repository.py  # Nhật ký bất biến
  ui/
    common.py       # Thành phần giao diện, trạng thái và helper dùng chung
    main_window.py  # Điều hướng 15 trang và kiểm tra quyền hiển thị
    platform/
      page.py       # Phiên bản Python, SQLite, đường dẫn và dung lượng dữ liệu
    auth/
      access_page.py # Lối vào quản lý tài khoản/vai trò và nhật ký
      dialogs.py    # Thiết lập quản trị, đăng nhập, đổi mật khẩu, nhật ký
      manager.py    # Giao diện quản lý tài khoản và vai trò
    dashboard/
      page.py       # Tổng quan
    animals/
      dialogs.py    # Biểu mẫu hồ sơ 25 đặc điểm
      page.py       # Danh sách, tìm kiếm và quản lý động vật
    health/
      dialogs.py    # Biểu mẫu hồ sơ khám
      page.py       # Lịch sử sức khỏe
    care/
      dialogs.py    # Biểu mẫu lịch chăm sóc và checklist
      page.py       # Công việc chăm sóc
    store/
      dialogs.py    # Biểu mẫu chuồng, gán động vật và lịch sử
      page.py       # Sức chứa và phân chuồng
    imports/
      dialogs.py    # Nhà cung cấp, lô nhập, cá thể nhập và kiểm tra
      page.py       # Quy trình lô nhập và kiểm tra đầu vào
    suppliers/
      page.py       # Giao diện nhà cung cấp dùng chung nghiệp vụ nhập
    customers/
      page.py       # Giao diện khách hàng dùng chung nghiệp vụ bán hàng
    reservations/
      page.py       # Giao diện giữ chỗ, tiền cọc và hoàn cọc
    sales/
      dialogs.py    # Khách hàng, giữ chỗ, đơn hàng, thanh toán và hoàn cọc
      page.py       # Khách hàng, đặt trước, đơn bán và chi tiết đơn
    inventory/
      dialogs.py    # Vật tư, nhập lô và xuất dùng
      page.py       # Tồn kho, hạn sử dụng, cảnh báo và sổ giao dịch
    reports/
      page.py       # Báo cáo theo ngày và xuất CSV
    notifications/
      page.py       # Cảnh báo, cấu hình thư mục và sao lưu
main.py             # Điểm khởi chạy
tests/              # Kiểm thử nghiệp vụ, bán hàng, tồn kho và vận hành
```

Thanh điều hướng có đủ 15 trang tương ứng 15 phân hệ. Nhà cung cấp/lô nhập và
khách hàng/giữ chỗ/đơn hàng có trang riêng; các trang dùng lại component và nghiệp
vụ hiện có để tránh nhân đôi logic. Cảnh báo và sao lưu được chia thành tab riêng;
trang tài khoản là lối vào cho quản lý người dùng và nhật ký thao tác.

Mỗi module nghiệp vụ trong `app/modules/` sở hữu truy vấn dữ liệu của chức năng đó;
giao diện tương ứng nằm trong `app/ui/`. `Database` vẫn cung cấp các phương thức
facade cũ để giữ tương thích với điểm khởi chạy và các tích hợp hiện có.

## Danh mục mục tiêu 15 module

Đây là danh mục phát triển theo chức năng, không phải yêu cầu tạo sẵn hàng trăm file
rỗng. Mỗi module có file riêng khi có nghiệp vụ cần thiết; UI, repository và kiểm thử
được bổ sung cùng lúc để từng giai đoạn chạy được.

| # | Module | Trạng thái |
|---|---|---|
| 1 | Nền tảng ứng dụng, cấu hình và cơ sở dữ liệu | Đã có bản desktop SQLite |
| 2 | Tài khoản, vai trò và phân quyền | Đã triển khai bản desktop cơ bản |
| 3 | Dashboard và thống kê cơ bản | Đã triển khai |
| 4 | Hồ sơ và danh mục động vật | Đã triển khai |
| 5 | Cửa hàng, khu vực, chuồng và vị trí | Đã triển khai chuồng trại |
| 6 | Nhà cung cấp | Đã triển khai bản cơ bản |
| 7 | Lô nhập, kiểm tra đầu vào và cách ly | Đã triển khai bản cơ bản |
| 8 | Hồ sơ sức khỏe và khám | Đã có bản cơ bản |
| 9 | Chăm sóc, lịch và checklist | Đã có bản cơ bản |
| 10 | Khách hàng | Đã triển khai CRUD và thống kê giao dịch |
| 11 | Đặt trước và giữ chỗ | Đã triển khai trạng thái, tiền cọc và hoàn cọc |
| 12 | Bán hàng, đơn hàng và thanh toán | Đã triển khai đơn, thanh toán một phần/đủ và lịch sử |
| 13 | Vật tư, thức ăn và thuốc | Đã triển khai tồn kho theo lô, FEFO, nhật ký nhập/xuất và cảnh báo |
| 14 | Báo cáo và phân tích | Đã triển khai báo cáo tồn kho, bán hàng, sức khỏe và xuất CSV |
| 15 | Thông báo, thiết lập, nhật ký và sao lưu | Đã triển khai cảnh báo vận hành, thiết lập thư mục và sao lưu SQLite; nhật ký thao tác đã có |

Quy trình nhập tạo hồ sơ động vật ở trạng thái chờ kiểm tra. Kết quả đạt chuyển
sang đang bán, cần theo dõi chuyển sang cách ly, cần điều trị chuyển sang điều trị;
lô tự hoàn tất khi mọi cá thể đã có kiểm tra đầu vào. Dữ liệu lô và lịch sử kiểm tra
được giữ lại thay vì xóa khi nhà cung cấp ngừng hoạt động.
