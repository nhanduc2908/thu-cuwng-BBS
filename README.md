# PetCare — Quản lý cửa hàng thú cưng

Ứng dụng quản lý cửa hàng thú cưng dạng desktop, viết bằng Python, PySide6 và
SQLite. Chương trình hoạt động cục bộ trên máy tính Windows, không cần backend,
tài khoản web hoặc dịch vụ AI bên ngoài.

## Yêu cầu

- Windows 10/11
- Python 3.10 trở lên (khuyến nghị Python 3.13)
- Kết nối Internet chỉ cần khi cài các gói Python

## Cài đặt và chạy

Mở PowerShell tại thư mục dự án:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

Dùng cùng một Python để cài thư viện và chạy ứng dụng. Nếu máy không có Python
3.13, thay `-3.13` bằng phiên bản đã cài (ví dụ `-3.12`). Có thể kích hoạt môi
trường trước rồi chạy ngắn gọn:

```powershell
.\.venv\Scripts\Activate.ps1
python main.py
```

Ở lần khởi chạy đầu, ứng dụng tạo tài khoản `admin` với mật khẩu tạm `admin`;
đăng nhập lần đầu sẽ bắt buộc đặt mật khẩu mới (ít nhất 10 ký tự) trước khi vào
hệ thống. Thông tin tài khoản được lưu dưới dạng hash PBKDF2-HMAC-SHA256 kèm salt
ngẫu nhiên.

Nếu cần khôi phục tài khoản `admin` trên máy đã có dữ liệu, chạy tại thư mục dự án:

```powershell
.\.venv\Scripts\python.exe main.py --reset-admin
```

Lệnh này đặt mật khẩu tạm thành `admin`, mở khóa tài khoản quản trị `admin` và
bắt buộc thay mật khẩu khi đăng nhập kế tiếp. Chỉ dùng trên máy/Windows account
được phép quản trị dữ liệu cửa hàng; không giữ mật khẩu tạm sau khi đăng nhập.

## Dữ liệu và sao lưu

Trên Windows, SQLite mặc định nằm tại:

```text
%LOCALAPPDATA%\PetStoreManagement\pet_store.db
```

Ứng dụng tự tạo thư mục, schema và các bảng khi khởi động. Ảnh chứng từ tiếp nhận
động vật được lưu trong SQLite. Có thể cấu hình thư mục sao lưu trong ứng dụng;
nên sao lưu định kỳ và hạn chế quyền truy cập vào thư mục dữ liệu vì có thông tin
khách hàng và hồ sơ vận hành.

## Các phân hệ

Điều hướng ứng dụng có 17 trang:

1. Nền tảng và dữ liệu
2. Tài khoản, vai trò và nhật ký
3. Tổng quan
4. Hồ sơ động vật
5. Chuồng trại và vị trí
6. Nhà cung cấp
7. Nhập lô, ảnh bàn giao và kiểm tra đầu vào
8. Sức khỏe
9. Chăm sóc và checklist
10. Khách hàng
11. Đặt chỗ, tiền cọc và hoàn cọc
12. Đơn hàng và thanh toán
13. Hội viên, thẻ và bill
14. Dịch vụ và lịch hẹn
15. Tồn kho thức ăn, thuốc và vật tư
16. Báo cáo
17. Cảnh báo và sao lưu

Các chức năng chính gồm:

- Quản lý hồ sơ cá thể với 25 đặc điểm; lưu ảnh, người xác nhận và thời điểm
  tiếp nhận. Hồ sơ nhập mới phải qua kiểm tra đầu vào trước khi đưa vào kinh doanh.
- Theo dõi chuồng, sức chứa, loài phù hợp, lịch sử phân chuồng, sức khỏe và lịch
  chăm sóc; checklist 25 mục là công cụ vận hành, không thay thế bác sĩ thú y.
- Quản lý khách hàng, giữ chỗ, đơn bán, cọc, thanh toán từng phần và công nợ.
- Quản lý tồn kho theo lô/hạn sử dụng, xuất theo FEFO, lịch sử nhập/xuất và cảnh
  báo tồn thấp/hàng sắp hết hạn.
- Catalog bán lẻ có 20 nhóm hàng demo, khoảng 600 SKU và 8 combo mẫu; SKU lưu mã/barcode, thương
  hiệu, loài/độ tuổi, quy cách, giá bán, giá thành viên, khuyến mãi, thành phần và
  đường dẫn ảnh. Có thể sửa sản phẩm và cấu hình SKU/định lượng trong từng combo.
- Bán sản phẩm/combo từ trang **Đơn hàng & thanh toán**. Giá membership được áp
  dụng theo khách hàng và kỳ hội viên còn hiệu lực; tồn sản phẩm được giữ khi đơn
  chờ/thanh toán một phần, chỉ trừ kho theo FEFO khi đơn thanh toán đủ. Combo trừ
  tồn của từng sản phẩm thành phần; hủy đơn chưa thanh toán sẽ giải phóng tồn giữ.
- Gợi ý sản phẩm theo hồ sơ và tồn kho; Advisor tiếng Việt chạy ngoại tuyến, tối
  ưu combo trong ngân sách, ghi nhớ SKU thích/tránh sau khi nhân viên xác nhận,
  giải thích bằng tag đã cấu hình và đánh giá ranking ngoại tuyến khi có đủ dữ liệu.
- Hồ sơ thức ăn mở rộng theo loài/phân loài, tháng tuổi, giai đoạn sống, loại
  thức ăn, kích thước giống, khoảng cân nặng phù hợp, protein, mục đích, vitamin C
  (theo nhãn), tầng nước và kiểu ăn. Quy tắc tuổi được lưu thành dữ liệu có thể
  quản lý; bộ lọc thức ăn dùng tuổi hồ sơ, giống, cân nặng và hàng còn sử dụng được.
  Tần suất/khẩu phần để theo nhãn nếu cửa hàng chưa nhập dữ liệu sản phẩm cụ thể.
- Tạo gói hội viên, cấp thẻ, lập bill và gia hạn. Thanh toán từng phần được lưu
  thành sổ; thẻ chỉ kích hoạt/gia hạn khi bill đủ tiền. Gia hạn sớm nối kỳ mới
  sau thời hạn hiện có.
- Catalog dịch vụ tách khỏi kho hàng: 240 gói mẫu thuộc sáu nhóm (tắm, tắm +
  vệ sinh, grooming, vệ sinh, chăm sóc và premium/spa/VIP), cùng 40 gói hội viên
  mẫu. Gói cấu hình loài, cân nặng, thời lượng, giá hội viên và phụ phí cân nặng/
  loại lông; ưu đãi hội viên áp dụng trên giá gốc, phụ phí được cộng riêng theo
  quy tắc cửa hàng cấu hình. Nhân viên có thể sửa quy tắc và trạng thái.
- Đặt lịch gắn khách hàng với hồ sơ thú cưng tại cửa hàng, phân công nhân viên,
  xem bảng tính giá/phụ phí/ưu đãi trước khi lưu và theo dõi trạng thái tiếp nhận,
  thực hiện, hoàn thành, hủy hoặc không đến. Hủy/không đến giải phóng lượt trả
  trước; lượt chỉ được trừ khi hoàn thành. Dịch vụ tính tiền tạo bill OTHER để
  nhân viên ghi thanh toán tại trang hội viên & bill.
- Gói dịch vụ hội viên chọn một trong ba kiểu: trả trước theo lượt, giảm giá hội
  viên hoặc định kỳ. Bill định kỳ/gia hạn do nhân viên tạo thủ công; ứng dụng
  không tự thu tiền hoặc tự gia hạn.
- Báo cáo tồn kho, bán hàng và sức khỏe; xuất CSV. Cảnh báo vận hành, phân quyền
  theo vai trò và audit log cho các thao tác ghi dữ liệu.

### Giới hạn nghiệp vụ hiện tại

- Phân hệ hội viên là công cụ quản trị nội bộ gắn với hồ sơ khách hàng hiện có;
  chưa có đăng ký trực tuyến, OTP hoặc cổng tài khoản khách hàng.
- Catalog và giá sản phẩm khởi tạo là dữ liệu demo/giá đề xuất theo tài liệu, không
  phải báo giá đã xác minh. Catalog không tự tạo lô tồn; cần nhập hàng thực tế
  trước khi bán. Thương hiệu, barcode, ảnh và thành phần chi tiết không được suy
  diễn nếu chưa có dữ liệu. Gói combo demo đã có thành phần SKU mẫu để cửa hàng
  rà soát/chỉnh lại. Vitamin/dinh dưỡng không được hiểu là thuốc hay chỉ định điều trị.
- Quy tắc tuổi và hồ sơ thức ăn demo chỉ để phân loại catalog, không quy định
  khẩu phần, liều dùng hoặc lịch cho ăn bắt buộc. Các mốc chó/mèo/động vật nhỏ
  thay đổi theo giống và nhãn; chim, cá, rùa và loài ngoại lai cần xác định phân
  loài. Luôn kiểm tra nhãn sản phẩm; vấn đề sức khỏe cần bác sĩ thú y.
- 280 gói dịch vụ/hội viên và giá trong catalog cũng là dữ liệu tham khảo từ đề
  xuất, chưa được xác minh theo bảng giá địa phương. Phụ phí chỉ phát sinh theo
  quy tắc cửa hàng cấu hình; cửa hàng cần kiểm tra giá và phạm vi áp dụng trước
  khi dùng với khách thật. Hồ sơ thú cưng trong lịch hẹn là dữ liệu nhập tại chỗ,
  độc lập với động vật thuộc tồn kho/bán của cửa hàng.
- Nhân viên chỉ ghi thanh toán sau khi tự xác minh tiền đã nhận. Chưa tích hợp
  ngân hàng, payment gateway/webhook, QR thanh toán, hoàn tiền membership hoặc
  tự động gia hạn/notification theo lịch.
- Thẻ hiện có token ngẫu nhiên để tra cứu trạng thái trong ứng dụng. Chưa tạo ảnh
  QR/thẻ in hoặc trang xác minh công khai.
- Bill membership là chứng từ nội bộ; chưa có xuất PDF/DOCX hoặc tích hợp hóa đơn
  điện tử. Không dùng làm hóa đơn thuế.
- Advisor là bộ luật cục bộ, không phải mô hình AI tạo sinh/ML, không gửi dữ liệu
  ra ngoài, không chẩn đoán và không tự tạo bill, ghi thanh toán hay trừ kho.
- Các chỉ số đánh giá recommendation là offline trên tương tác đã được ghi nhận;
  không chứng minh CTR, doanh thu tăng thêm hay hiệu quả y tế.

## Workflow

Mở [workflow.html](./workflow.html) trực tiếp bằng trình duyệt hiện đại để xem
workflow khởi chạy/đăng nhập, tiếp nhận động vật, chăm sóc, bán hàng, dịch vụ/lịch
hẹn, hội viên, gợi ý ngoại tuyến, tồn kho và báo cáo/vận hành. Có thể in hoặc lưu
sơ đồ thành PDF.

## Kiểm thử

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Các kiểm thử giao diện Qt không hiển thị cửa sổ có thể chạy với:

```powershell
$env:QT_QPA_PLATFORM = "offscreen"
.\.venv\Scripts\python.exe -m pytest -q
```

## Đồng bộ mã nguồn lên GitHub

Sau khi cấu hình Git remote và xác thực Git Credential Manager, có thể chạy:

```powershell
.\.venv\Scripts\python.exe scripts\github_sync.py --message "Mô tả thay đổi"
```

Script chỉ đưa các file được cho phép lên GitHub; không đồng bộ cơ sở dữ liệu,
ảnh tiếp nhận, môi trường ảo, bytecode hoặc file bí mật. Cần kiểm tra danh sách
file và remote trước khi đồng bộ.

## Cấu trúc dự án

```text
main.py
requirements.txt
workflow.html
app/
  database.py
  modules/
    animals/ care/ customers/ dashboard/ health/ imports/
    inventory/ memberships/ notifications/ recommendations/
    reports/ sales/ services/ store/ suppliers/ auth/ audit/
  ui/
    main_window.py
    animals/ care/ customers/ dashboard/ health/ imports/
    inventory/ memberships/ notifications/ platform/ reports/ services/
    reservations/ sales/ store/ suppliers/ auth/
tests/
```

`main.py` là điểm khởi chạy, thiết lập SQLite, tạo quản trị viên lần đầu và đăng
nhập. `app/database.py` quản lý schema/facade; repository trong `app/modules/`
chứa nghiệp vụ và truy vấn; `app/ui/` chứa giao diện PySide6. Dữ liệu được kiểm
tra quyền và ghi audit thông qua facade `Database`.

Catalog mẫu nằm trong `app/modules/inventory/catalog_seed.py`; ứng dụng thêm SKU
và combo demo một lần theo mã, không ghi đè các SKU đó khi nhân viên sửa lại sau
khi khởi tạo. Dữ liệu seed không nhập số lượng tồn.

20 nhóm hàng mẫu gồm thức ăn chó, thức ăn mèo, pate/thức ăn ướt, snack/bánh
thưởng, sữa tắm/chăm sóc, vệ sinh, cát mèo, đồ chơi, dây dắt/vòng cổ, bát/dụng
cụ ăn, ổ nằm/nhà, balo/túi vận chuyển, quần áo, grooming, vitamin/dinh dưỡng,
hamster/thỏ, cá cảnh, chim cảnh, chuột cảnh và bò sát cảnh. Mỗi nhóm có khoảng
25–35 SKU demo. 8 combo có SKU thành phần mẫu để nhân viên rà soát.
Catalog demo chưa gán thương hiệu thật, barcode hay ảnh không được cung cấp trong
dữ liệu đầu vào; các trường này có thể được cửa hàng cập nhật trong biểu mẫu SKU.
