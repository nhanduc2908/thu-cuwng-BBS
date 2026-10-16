# WAGGY · Định hướng thiết kế và nâng cấp giao diện

## 1. Mục tiêu

Nâng cấp trải nghiệm giao diện của hệ sinh thái WAGGY theo hai hướng:

1. **Một trải nghiệm nhất quán:** nhân viên có thể chuyển hệ thống, cơ sở, tìm kiếm và nhận biết trạng thái mà không phải học lại cách dùng ở mỗi nơi.
2. **Giao diện đúng nghiệp vụ từng miền:** mỗi hệ thống ưu tiên tác vụ, mức độ nhạy cảm, người dùng và tốc độ thao tác đặc thù; không ép cả tám sản phẩm vào cùng một dashboard hoặc một tập bảng biểu.

Đây là định hướng và yêu cầu nghiệm thu giao diện, không khẳng định mọi năng lực hiện đã hoạt động. Pet Care là sản phẩm hiện có; các hệ thống còn lại và luồng xuyên hệ thống là concept/demo cho tới khi được phát triển và nghiệm thu.

Xem [không gian chuyên đề UI/UX](./UI-UX/index.html) để mở bản đồ giao diện, liên kết giữa tám workspace và baseline demo; yêu cầu riêng từng hệ thống được tổng hợp tại [SYSTEM-UI-DIRECTION.md](./UI-UX/SYSTEM-UI-DIRECTION.md).

Trang trình bày HTML đầy đủ: [Kế hoạch nâng cấp UI/UX](./UI-UX-UPGRADE-PLAN.html).

## 2. Người dùng và tác vụ cần thiết kế quanh họ

| Nhóm người dùng | Nhu cầu chính | Định hướng giao diện |
|---|---|---|
| Nhân viên cửa hàng / chăm sóc | Tìm nhanh đúng khách/thú cưng, làm tác vụ, bàn giao ca | Ưu tiên mobile, tìm kiếm nhanh, tác vụ theo hàng đợi, ít nhập lặp |
| Quản lý cơ sở / chuỗi | So sánh cơ sở, xử lý ngoại lệ, điều phối người và nguồn lực | Bộ lọc cơ sở rõ ràng, KPI có định nghĩa, drill-down từ cảnh báo đến bản ghi |
| Bác sĩ / nhân viên chuyên môn | Xem đúng hồ sơ, ghi nhận chuyên môn, rà kết quả và consent | Trình tự đọc an toàn, nguồn/thời điểm rõ, bảo vệ dữ liệu nhạy cảm, không tạo cảm giác AI là chẩn đoán |
| Chủ nuôi / khách mua sắm | Tự phục vụ, đặt dịch vụ/sản phẩm, quản lý hồ sơ và đồng ý chia sẻ | Ngôn ngữ dễ hiểu, quy trình ngắn, giá/điều kiện minh bạch, consent tách theo mục đích |
| Điều phối viên cộng đồng / cứu hộ | Xử lý nội dung hoặc case an toàn, phối hợp đối tác | Hàng đợi có ngữ cảnh và mức độ ưu tiên; dữ liệu liên hệ/vị trí chỉ hiện khi được phép |
| Data owner / quản trị hệ thống | Theo dõi chất lượng, lineage, quyền, phát hành và sự cố | Bằng chứng, phiên bản, lịch sử thay đổi và trạng thái kiểm soát có thể kiểm tra |

Trước khi làm wireframe cho từng màn hình, cần xác nhận người dùng chính, tác vụ thường xuyên, tác vụ rủi ro cao, thiết bị/môi trường làm việc và chỉ số hoàn thành. Không suy ra nhu cầu chỉ từ một bản dashboard mẫu.

## 3. Quy chuẩn giao diện dùng chung

### 3.1 Design system và nhận diện

- Duy trì bộ token nền tảng dùng chung ở [waggy-product.css](./assets/waggy-product.css): màu thương hiệu xanh lá, nền/surface, màu chữ, đường viền, trạng thái, khoảng cách, bo góc, typography và elevation.
- Chuẩn hóa thành phần tái sử dụng: app shell, brand/system switcher, branch selector, breadcrumb, global search, page header, KPI, filter bar, data table, status badge, empty/error state, confirmation dialog, toast, audit entry và form field.
- Mỗi hệ thống có màu nhấn/biểu tượng phụ nếu cần, nhưng không thay đổi ý nghĩa màu trạng thái hoặc làm suy yếu độ tương phản.
- Dùng typography tiếng Việt dễ đọc, phân cấp heading và nhãn nhất quán. Tránh chữ siêu nhỏ cho thông tin cần hành động.
- Không dùng hình trang trí làm giảm mật độ thông tin, tương phản hoặc không gian cho tác vụ.

### 3.2 Khung ứng dụng và điều hướng

- Thanh đầu trang hiển thị tên hệ thống, khu vực nghiệp vụ hiện tại, cơ sở/phạm vi đang chọn và trạng thái dữ liệu.
- Điều hướng phân biệt rõ điều hướng cấp hệ thống với tab/phân hệ; trang đang xem có chỉ báo hiện hành.
- Mọi trang nghiệp vụ có tiêu đề chỉ rõ đối tượng và tác vụ, breadcrumb khi phân cấp sâu, và hành động chính đặt tại vị trí ổn định.
- Có tìm kiếm toàn cục theo quyền; kết quả hiển thị loại đối tượng, mã tham chiếu và nguồn hệ thống để tránh nhầm record trùng tên.
- Màn hình nhiều bước có thể quay lại mà không mất dữ liệu nhập; khi đổi hệ thống/cơ sở có cảnh báo nếu bộ lọc làm mất ngữ cảnh.

### 3.3 Quy tắc thiết kế dữ liệu và bảng biểu

- Mỗi KPI ghi rõ đơn vị, phạm vi cơ sở, mốc thời gian/cập nhật và cách mở danh sách chi tiết; không hiển thị số “đẹp” nhưng không giải thích nguồn.
- Bộ lọc đang áp dụng luôn hiển thị; hỗ trợ xóa nhanh, sắp xếp và tìm kiếm. Filter không được làm người dùng hiểu dữ liệu toàn chuỗi là dữ liệu của cơ sở hiện tại.
- Bảng desktop có tiêu đề cột dễ quét, hàng có khoảng cách phù hợp, cột thao tác rõ và không ẩn trạng thái quan trọng. Trên mobile, chuyển thành card theo thứ tự trường ưu tiên hoặc bảng cuộn ngang có nhãn cột cố định; không thu nhỏ chữ đến mức khó đọc.
- Bản ghi có mã định danh, trạng thái dạng chữ, thời gian cập nhật và liên kết đến nguồn chuẩn. Không coi bản projection ở hệ nhận là bản ghi có quyền sửa.
- Cảnh báo có mức độ, lý do, chủ sở hữu và bước tiếp theo; tránh dashboard dày đặc biểu đồ nhưng không chỉ ra hành động.
- Form nhóm trường theo tác vụ; kiểm tra ngay tại trường, nêu cách sửa, giữ dữ liệu hợp lệ khi có lỗi và yêu cầu xác nhận cho hành động không thể đảo ngược.

### 3.4 Responsive, khả năng tiếp cận và trạng thái hệ thống

- Thiết kế mobile-first cho luồng thao tác tại cửa hàng; xác nhận tối thiểu ở bề rộng 360 px, 390 px, tablet và desktop. Không tràn trang ngang ngoài các vùng dữ liệu bảng/sơ đồ được chủ ý cuộn.
- Hỗ trợ bàn phím đầy đủ, focus nhìn thấy được, thứ tự tab hợp lý, nhãn form và thông báo lỗi gắn với control; không biểu đạt trạng thái chỉ bằng màu.
- Mục tiêu nghiệm thu accessibility: WCAG 2.2 AA cho các luồng cốt lõi; tương phản, zoom/reflow, target cảm ứng tối thiểu 44×44 CSS px cho hành động chính và thông báo phù hợp với screen reader.
- Mọi màn hình dữ liệu phải có trạng thái loading, empty, error/retry, permission denied, offline/stale và success. Ghi rõ thời điểm cập nhật và không trình bày dữ liệu stale như dữ liệu mới.
- Hỗ trợ giảm chuyển động theo cài đặt của thiết bị; animation chỉ phản hồi thao tác hoặc làm rõ trạng thái, không làm chậm công việc.
- Hiệu năng giao diện phải được đo trên luồng pilot và thiết bị mục tiêu; tải danh sách có phân trang/lọc server-side khi chuyển sang backend, không tải vô hạn toàn bộ hồ sơ.

### 3.5 Nội dung, an toàn và quyền riêng tư

- Dùng tiếng Việt ngắn, rõ, nhất quán tên trạng thái. Thuật ngữ tiếng Anh chỉ giữ lại khi đội vận hành đã thống nhất và có giải thích.
- Mọi ghi chú về sức khỏe, vị trí cứu hộ, thông tin liên hệ hoặc tài chính phải ẩn/giảm thiểu theo role, mục đích và phạm vi; không đưa dữ liệu nhạy cảm vào toast, URL, tiêu đề hoặc preview không an toàn.
- Consent phải nêu dữ liệu, mục đích, nơi nhận, thời hạn/thu hồi; không gộp vào checkbox chung hoặc mặc định chọn sẵn.
- Không để giao diện ngụ ý rằng một hành động đã thành công nếu chỉ mới tạo yêu cầu/chờ duyệt/chờ đồng bộ.

## 4. Yêu cầu nâng cấp theo từng hệ thống

### 4.1 Pet Care · hồ sơ và chăm sóc

**Người dùng chính:** lễ tân, nhân viên chăm sóc, quản lý cơ sở, chủ nuôi.

- Dashboard mở đầu bằng việc cần làm hôm nay: lịch sắp tới, task quá hạn/chờ phân công và cảnh báo cần con người kiểm tra; cho xem nguồn, thời điểm cập nhật và bộ lọc cơ sở.
- Hồ sơ thú cưng là trang chi tiết thống nhất: danh tính và chủ nuôi tham chiếu, timeline chăm sóc/lịch hẹn, trạng thái, ghi chú được phân quyền và liên kết đến hồ sơ y tế theo consent; tách “tổng quan” khỏi lịch sử dài.
- Tìm kiếm theo mã/tên có phân biệt thú cưng trùng tên; trước khi tạo mới cho phép phát hiện trùng và đối chiếu.
- Luồng tạo/sửa task, lịch hẹn, nhắc việc tối ưu cho điện thoại: chọn thú cưng → công việc → người phụ trách → thời gian → rà soát → xác nhận.
- Đánh dấu rõ thông tin do Pet Care sở hữu và projection đến từ hệ khác; chỉ cho chỉnh sửa tại nguồn chuẩn.
- Trên mobile, có hành động nhanh gọi/đặt lịch/ghi nhận task nhưng không đưa thông tin liên hệ ra khu vực công cộng hoặc thông báo ngoài quyền.

**Màn hình ưu tiên:** tổng quan, thú cưng, khách hàng, nhiệm vụ chăm sóc, lịch hẹn, hồ sơ sức khỏe, nhắc việc.

### 4.2 Pet Business · vận hành cửa hàng và chuỗi

**Người dùng chính:** nhân viên kho/mua hàng, quản lý cửa hàng, kế toán, quản lý chuỗi.

- Control tower luôn ghim bộ lọc tổ chức/cơ sở/kỳ đang xem; dashboard tách chỉ số toàn chuỗi khỏi chỉ số cơ sở.
- Tồn kho dùng bảng có SKU, lô, vị trí, khả dụng, đã giữ, sắp hết hạn và trạng thái kiểm đếm; cho drill-down tới chứng từ nhập/xuất/điều chuyển, không cho sửa ledger trực tiếp.
- Mua hàng, nhận hàng và điều chuyển hiển thị tiến trình dạng timeline cùng người đang chịu trách nhiệm; maker-checker tách biệt trực quan.
- Đối soát/tài chính ưu tiên ngoại lệ và bằng chứng, có trạng thái kỳ, sai lệch, nguồn dữ liệu và liên kết audit; không nhồi báo cáo kế toán vào dashboard vận hành.
- Hỗ trợ thao tác quét mã và nhập nhanh trên thiết bị kho; mọi thay đổi số lượng cần đơn vị, lý do và xác nhận.
- Bảng nhiều cột có saved views/ẩn hiện cột trên desktop; mobile tập trung quét/tìm SKU và cập nhật tác vụ an toàn.

**Màn hình ưu tiên:** control tower, tồn kho, nhận hàng, mua hàng, điều chuyển, phê duyệt, đối soát, báo cáo, audit.

### 4.3 Pet Service · lịch và thực hiện dịch vụ

**Người dùng chính:** điều phối viên, lễ tân, nhân viên dịch vụ, quản lý cơ sở, chủ nuôi.

- Lịch hẹn hỗ trợ ngày/tuần, lọc theo cơ sở, nhân viên, loại dịch vụ và nguồn lực; chỉ rõ khung giờ kín, thời gian đệm và lý do không thể đặt.
- Luồng booking hướng dẫn chọn thú cưng/dịch vụ/cơ sở/giờ, kiểm tra năng lực, hiển thị giá/điều kiện và xác nhận consent cần thiết trước khi tạo.
- Chi tiết booking dùng timeline trạng thái: yêu cầu → xác nhận → check-in → đang làm → chờ bàn giao → hoàn tất/hủy/no-show; từng bước có actor và timestamp.
- Check-in/check-out ưu tiên một tay trên tablet/mobile, có checklist tình trạng tiếp nhận và đường xử lý khi khách đến trễ, thiếu thông tin hoặc dịch vụ cần xác nhận.
- Bàn giao hiển thị kết quả được phép, ghi chú vận hành và người nhận; không hiển thị dữ liệu y tế vượt phạm vi consent.

**Màn hình ưu tiên:** lịch điều phối, booking detail, check-in, lịch nhân viên, danh mục dịch vụ, tài nguyên, bàn giao.

### 4.4 Pet Health · hồ sơ y tế và an toàn chuyên môn

**Người dùng chính:** bác sĩ thú y, điều dưỡng, nhân viên tiếp nhận, chủ nuôi.

- Hàng đợi chuyên môn tách ca mới, cần rà soát, kết quả chờ duyệt và tái khám; mức ưu tiên không thay thế đánh giá lâm sàng.
- Màn hình bệnh nhân trình bày nhận diện và cảnh báo quan trọng trước; encounter theo timeline có người ghi, thời điểm, nguồn và trạng thái ký/đính chính.
- Consent và phạm vi chia sẻ phải hiện trước khi truy cập/trao đổi liên miền; cho biết mục đích và thời hạn, từ chối rõ ràng khi thiếu căn cứ.
- Kết quả xét nghiệm có đơn vị, khoảng tham chiếu, thời gian và trạng thái người có chuyên môn đã xem; không dựa riêng vào màu để báo bất thường.
- Ghi hồ sơ theo nhóm lâm sàng phù hợp, hỗ trợ lưu nháp/tiếp tục an toàn; hồ sơ đã ký không bị ghi đè âm thầm, đính chính tạo lịch sử.
- Không dùng AI/đồ họa để ngụ ý chẩn đoán tự động; luôn hiển thị giới hạn và người chịu trách nhiệm.

**Màn hình ưu tiên:** patient, encounter, lịch khám, lab orders/results review, vaccinations, follow-ups, consent, audit.

### 4.5 Pet Commerce · catalog, đơn hàng và hậu mãi

**Người dùng chính:** khách mua sắm, nhân viên xử lý đơn, chăm sóc khách hàng, quản lý catalog.

- Trải nghiệm khách hàng làm rõ danh mục, ảnh/thuộc tính, giá hiện hành, tình trạng hàng và cơ sở/kênh áp dụng; không hiển thị tồn ảo như cam kết giữ hàng.
- Checkout chia bước ngắn, nêu tổng tiền/phí/địa chỉ/giao nhận/chính sách đổi trả trước khi xác nhận; kiểm tra lỗi tại trường và không mất giỏ hàng khi lỗi.
- Màn hình vận hành phân biệt đơn mới, đang giữ tồn, chờ thanh toán xác minh, đóng gói, giao và hậu mãi; mỗi trạng thái có hành động tiếp theo hợp lệ.
- Chi tiết đơn có dòng thời gian từ tạo đến hoàn tất, tham chiếu thanh toán không chứa dữ liệu thẻ và liên kết SKU/chi nhánh/fulfillment.
- Đổi trả/hoàn tiền yêu cầu lý do, bằng chứng phù hợp, quyền duyệt và trạng thái hoàn tiền; tránh nút thao tác mơ hồ hoặc lặp.

**Màn hình ưu tiên:** catalog/products, giỏ/checkout, orders/order detail, fulfillment, payments, returns, promotions, analytics.

### 4.6 Pet Community · cộng đồng và Trust & Safety

**Người dùng chính:** thành viên, moderator, điều phối sự kiện, quản lý an toàn cộng đồng.

- Feed hỗ trợ đọc dễ, điều khiển media rõ, phân biệt nội dung quảng bá/thông báo và lọc theo chủ đề; hành động báo cáo luôn dễ tìm nhưng không lấn át nội dung.
- Hàng đợi moderation hiển thị lý do báo cáo, policy liên quan, mức độ, lịch sử xử lý và xung đột lợi ích; ưu tiên batch review có kiểm soát, không tự động kết luận từ một tín hiệu.
- Quyết định kiểm duyệt dùng lý do chuẩn hóa và thông điệp giải thích phù hợp; có đường kháng nghị, SLA và lịch sử thay đổi.
- Công cụ an toàn thành viên giới hạn thông tin cá nhân, hỗ trợ chặn/tắt thông báo/báo cáo và hướng dẫn trợ giúp.
- Dashboard sự kiện làm rõ thời gian, địa điểm, sức chứa, điều kiện tham gia và trạng thái đăng ký; không lộ thông tin người tham gia cho người không có quyền.

**Màn hình ưu tiên:** posts/feed, moderation queue, reports, appeals, policies, events, member safety, announcements.

### 4.7 Pet Connect · thất lạc, cứu hộ và bàn giao

**Người dùng chính:** chủ nuôi, điều phối viên cứu hộ, đối tác, nhân viên hiện trường.

- Tạo case theo bước: loại yêu cầu → nhận diện thú cưng → thời gian/khu vực → bằng chứng → cách liên hệ an toàn → xác nhận; chỉ thu dữ liệu tối thiểu cần thiết.
- Bản đồ dùng độ chính xác vị trí theo role/trạng thái case; vị trí chính xác chỉ mở cho người được giao nhiệm vụ. Cung cấp phương án danh sách/địa chỉ mô tả khi bản đồ không dùng được.
- Ghép kết quả tìm thấy hiển thị căn cứ/mức độ phù hợp và cho người xác minh; không tự kết luận đúng thú cưng hoặc công khai thông tin liên hệ.
- Case detail có timeline xác minh, phân công, cập nhật hiện trường, xác nhận bàn giao và đóng case; bằng chứng có trạng thái quyền truy cập và audit.
- Luồng bàn giao an toàn hiển thị checklist, danh tính hai bên theo quyền và xác nhận hoàn tất; có nút báo nguy cơ/escalate.

**Màn hình ưu tiên:** lost-pet case, map/field map, evidence, rescue tasks, partners, safety check, handoff, notifications.

### 4.8 Pet Intelligence · quản trị dữ liệu, insight và mô hình

**Người dùng chính:** data owner, analyst, ML engineer, reviewer nghiệp vụ và người phê duyệt.

- Landing page là governance overview: chất lượng nguồn, dataset mới thay đổi, lineage chưa duyệt, đánh giá/drift/sự cố cần xử lý; chỉ số có nguồn và thời điểm.
- Dataset/lineage cho phép lần ngược source → biến đổi → aggregate → consumer, xem quyền/mục đích, phiên bản schema và trường bị loại; không hiển thị PII nếu use-case không yêu cầu.
- Model registry/card nêu owner, version, phạm vi, giới hạn, tập đánh giá và trạng thái phê duyệt; phân biệt shadow, pilot và production.
- Monitoring/drift hiển thị baseline, ngưỡng, nhóm ảnh hưởng, bằng chứng và bước rollback; cảnh báo liên kết đến người chịu trách nhiệm.
- Gợi ý cho hệ nghiệp vụ có giải thích, độ tin cậy/độ bao phủ phù hợp và hạn dùng; người nhận có quyền chấp nhận/từ chối, không tự áp dụng thay đổi nghiệp vụ.

**Màn hình ưu tiên:** datasets, lineage, use-cases, evaluations, approvals, model registry, monitoring, drift, incidents, rollback.

## 5. Thành phần dùng chung và ranh giới tùy biến

| Dùng chung toàn hệ sinh thái | Phải tùy biến theo hệ thống |
|---|---|
| App shell, đăng nhập, hệ thống/cơ sở switcher, breadcrumbs, global search | Thuật ngữ nghiệp vụ, dashboard và chỉ số |
| Màu/typography/spacing tokens, form, table, badge, dialog, toast | Workflow, trạng thái, kiểm tra và hành động theo domain |
| Loading/empty/error/offline/permission/stale states | Trường dữ liệu, mức độ nhạy cảm, consent và retention |
| Audit metadata, thời gian, nguồn, mã tham chiếu và liên kết | Mật độ dữ liệu, bố cục desktop/mobile theo tác vụ |
| Tiêu chuẩn accessibility, localization và responsive behavior | Biểu đồ/map/timeline chuyên biệt khi tạo giá trị tác vụ |

Không tạo “một dashboard dùng chung” để thay các trang công việc. Dùng component thống nhất nhưng cho phép mỗi miền có workspace và mật độ thông tin riêng.

## 6. Quy trình nâng cấp giao diện

| Chặng | Việc làm | Đầu ra / điều kiện qua chặng |
|---|---|---|
| **A · Audit giao diện** | Kiểm kê màn hình hiện có theo 8 thư mục demo; ghi nhận người dùng, mục tiêu, hành động, trạng thái, vấn đề responsive/accessibility và mức hiện thực (đang có/demo/concept). | Screen inventory, mức ưu tiên theo rủi ro/tần suất, danh sách không được hiểu nhầm là production. |
| **B · Nghiên cứu tác vụ** | Phỏng vấn/quan sát đại diện nhân viên cửa hàng, quản lý và chuyên gia domain; đo tác vụ hiện tại và điều kiện thiết bị/mạng. | Persona/tác vụ có bằng chứng, journey map, baseline thời gian/lỗi; không tự giả định vai trò. |
| **C · Kiến trúc thông tin & wireframe** | Chuẩn hóa điều hướng, hierarchy, table/detail/form, permission states; thiết kế mobile và desktop cho luồng ưu tiên. | Wireframe được data owner và người vận hành duyệt; lỗi thao tác nghiêm trọng được giải quyết trước visual polish. |
| **D · UI kit & prototype** | Chốt token/component, tạo prototype tương tác, trạng thái rỗng/lỗi/quyền/đồng bộ và nội dung tiếng Việt. | Figma/HTML prototype có component inventory, annotation hành vi, responsive variants và accessibility review. |
| **E · Usability test & lặp** | Kiểm tra với người dùng đại diện trên thiết bị mục tiêu; quan sát hoàn thành tác vụ, lỗi, nhầm trạng thái và hiểu nhầm quyền. | Issue log ưu tiên, sửa các blocker/high severity, đo lại cùng kịch bản. |
| **F · Triển khai theo lát cắt** | Nâng cấp theo workflow end-to-end trong từng hệ thống; feature flag, analytics không chứa PII, support guide và release note. | Smoke/e2e, keyboard/responsive check, nội dung/accessibility sign-off, rollback path. |
| **G · Theo dõi & cải thiện** | Theo dõi tác vụ, lỗi form, tìm kiếm không có kết quả, usage của chức năng, phản hồi nhân viên và sự cố quyền. | Review định kỳ có owner; cải tiến dựa trên số liệu và phản hồi, không chỉ đánh giá thị giác. |

### Ưu tiên triển khai UI

1. **Nền chung:** app shell, token/component, navigation/search/scope selector, trạng thái hệ thống, accessibility baseline.
2. **Luồng tác nghiệp tại cửa hàng:** Pet Care → Pet Business/Service theo pilot đã phê duyệt; tập trung hồ sơ, task, lịch, tồn và bàn giao.
3. **Luồng chuyên môn/giao dịch:** Pet Health và Commerce với consent, quyền, payment/clinical review và trạng thái giao dịch.
4. **Luồng cộng đồng/hiện trường:** Community và Connect sau khi đã kiểm chứng cơ chế an toàn, vị trí và appeal.
5. **Công cụ quản trị/insight:** Intelligence sau khi lineage, chất lượng, quyền và giới hạn gợi ý đã rõ.

Thứ tự này là đề xuất phụ thuộc rủi ro và readiness, không phải cam kết lịch hoặc thứ tự phát hành bắt buộc.

## 7. Tiêu chí nghiệm thu giao diện cho mỗi màn hình

- Có mục tiêu người dùng, vai trò, phạm vi dữ liệu và hành động chính được duyệt.
- Mọi trạng thái loading/empty/error/retry/permission denied/offline/stale/success đều được thiết kế và có nội dung rõ.
- Màn hình desktop và mobile hoàn thành cùng tác vụ cốt lõi; không mất context, nhãn hoặc quyền thao tác khi reflow.
- Bàn phím, focus, screen reader label, tương phản và zoom/reflow được kiểm tra; không trạng thái nào phụ thuộc riêng vào màu.
- Giá trị, đơn vị, ngày giờ, cơ sở, nguồn chuẩn, người cập nhật và tính mới của dữ liệu rõ ở nơi cần quyết định.
- Hành động ghi/xóa/phê duyệt xác nhận đối tượng, tác động, quyền và khả năng hoàn tác; bản ghi nhạy cảm không lộ trong khu vực không được cấp.
- Prototype được usability test với người dùng đại diện. Mục tiêu định lượng được đặt sau baseline; đề xuất ban đầu là ≥80% hoàn thành luồng ưu tiên không cần trợ giúp và không có lỗi nghiêm trọng, sau đó đo lại trên cùng kịch bản.
- Có ánh xạ rõ giữa thiết kế, component hiện thực và ticket/release; thay đổi thiết kế không thể tự coi là backend/API đã tồn tại.

## 8. Bộ sản phẩm thiết kế cần duy trì

1. Design principles và token catalog.
2. Component library có trạng thái, responsive variants và accessibility notes.
3. Screen inventory cho 8 hệ thống, đánh dấu current/demo/proposed.
4. User flow, wireframe và prototype cho các tác vụ ưu tiên.
5. Ma trận role × screen × action × data scope, tham chiếu cùng data owner.
6. Nội dung tiếng Việt và glossary trạng thái nghiệp vụ.
7. Kịch bản usability, issue log, accessibility checklist và release checklist.
8. Decision log cho thay đổi ảnh hưởng xuyên hệ sinh thái.

## 9. Ranh giới và quyết định cần xác nhận

- Các trang HTML demo hiện tại là baseline để kiểm tra kiến trúc/nội dung, không tự động đại diện cho UI production đã được duyệt.
- Chưa thể chốt thời gian, ngân sách, nền tảng thiết kế, mức hỗ trợ thiết bị cũ hoặc chỉ số KPI nếu chưa biết nhóm người dùng thực tế, tần suất tác vụ, phạm vi triển khai và nguồn lực thiết kế/frontend.
- Trước khi sản xuất visual design, cần chỉ định product owner/designer và đại diện domain cho từng hệ thống; đặc biệt cần reviewer chuyên môn cho Health, Business finance và an toàn Community/Connect.
- Có thể dùng thư viện UI/framework hiện tại sau khi audit tương thích; không thêm framework hoặc thay toàn bộ UI chỉ để đổi diện mạo.
