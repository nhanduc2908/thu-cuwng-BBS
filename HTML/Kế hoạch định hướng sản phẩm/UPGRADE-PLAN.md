# WAGGY · Phương án nâng cấp hệ thống

## 1. Mục tiêu và hiện trạng

Đưa bộ prototype trong thư mục này từ tài liệu/giao diện demo thành nền tảng có thể vận hành an toàn theo từng giai đoạn, không coi các màn hình đề xuất là chức năng production.

Hiện trạng trong repository:

- 8 miền dữ liệu tĩnh, 14 bảng logic và 14 bản ghi giả; mỗi miền có workflow JSON.
- Có bản đồ kết nối bảng, mini-map luồng, trang mô phỏng quyền CRUD và sandbox đồng bộ.
- CRUD và trạng thái đồng bộ hiện lưu ở `localStorage`; quyền vai trò được chọn ở trình duyệt, chưa xác thực danh tính.
- Chưa có API, cơ sở dữ liệu máy chủ, kiểm soát giao dịch, đồng bộ giữa người dùng/thiết bị hoặc bảo đảm sao lưu.
- Pet Care là hệ thống hiện có; các hệ thống còn lại là concept/đề xuất cho đến khi được xây dựng và nghiệm thu.

Trang quản trị hiện tại:

- [Định hướng thiết kế và nâng cấp giao diện 8 hệ thống](./UI-UX-UPGRADE-PLAN.md)
- [Sơ đồ kết nối bảng](./data/connection-map.html)
- [Kiểm tra quyền CRUD demo](./data/record-access.html)
- [Mini-map kiểm soát luồng](./data/flow-control.html)
- [Bản đồ dữ liệu và giá trị mẫu](./data/data-map.html)
- [Trung tâm đồng bộ demo](./workflow/demo/sync.html)
- [Tài liệu mô hình dữ liệu](./data/DATA-FLOW.md)

## 2. Nguyên tắc kiến trúc đề xuất

1. **Một chủ sở hữu cho mỗi miền:** hệ nguồn là nơi tạo/cập nhật dữ liệu chuẩn; consumer tham chiếu ID hoặc nhận projection được duyệt, không tạo bản chuẩn thứ hai.
2. **Quyền được kiểm tra ở server:** RBAC kết hợp phạm vi tenant/cơ sở và quyền theo hành động; ẩn nút trên giao diện chỉ là UX, không phải cơ chế bảo vệ.
3. **Hợp đồng dữ liệu có phiên bản:** schema, chủ sở hữu, trường bắt buộc, khóa tham chiếu, projection, consent/mục đích và chính sách lưu giữ cần được kiểm tra tự động.
4. **Đồng bộ có thể phục hồi:** transactional outbox, idempotency key, retry có giới hạn, dead-letter queue, phát hiện version conflict và audit xuyên suốt.
5. **Tách dữ liệu nhạy cảm:** hồ sơ y tế/liên hệ riêng tư được phân loại, giới hạn truy cập, mã hóa và chỉ chia sẻ khi có mục đích/consent hợp lệ.
6. **Đo lường trước khi mở rộng:** có chất lượng dữ liệu, độ trễ đồng bộ, lỗi, quyền bị từ chối và khả năng khôi phục được kiểm tra bằng chỉ số.

### Kiến trúc đích tham khảo

```text
Web/mobile clients
        │ HTTPS + OIDC session/token
API gateway / backend-for-frontend
        │ authentication → RBAC + branch/tenant scope → validation
Domain services ── transactional write ── relational database
        │                                      │
        └──── transactional outbox ────────────┘
                         │
                 message broker / queue
                         │ schema + consent + projection + idempotency
                 consumer services
                         │
             audit / metrics / tracing / alerts
```

PostgreSQL là lựa chọn mặc định phù hợp cho dữ liệu nghiệp vụ có quan hệ và giao dịch; cần xác nhận cùng đội vận hành về hosting, backup, chi phí và năng lực trước khi chốt. Hàng đợi sự kiện chỉ nên thêm khi có nhu cầu/độ tải thực tế; giai đoạn đầu có thể dùng outbox worker trong cùng nền tảng backend.

## 3. Lộ trình theo giai đoạn

| Giai đoạn | Phạm vi và đầu ra | Cổng nghiệm thu |
|---|---|---|
| **0 · Chốt nghiệp vụ, UX và dữ liệu** | Xác nhận actor/role, tenant-cơ sở, tác vụ ưu tiên, screen inventory, journey, nguồn sở hữu bảng, trạng thái, dữ liệu nhạy cảm, retention, SLA và hệ thống ưu tiên. Chuẩn hóa data dictionary/schema cho 14 bảng và baseline usability/accessibility. | Product/data owner và người dùng đại diện ký xác nhận RACI, luồng cốt lõi, ma trận quyền, design requirements, nguồn chuẩn và hợp đồng dữ liệu; không còn khóa tham chiếu mơ hồ. |
| **1 · Design system và nền tảng an toàn** | Chuẩn hóa token/component/app shell/responsive/accessibility; tạo OIDC, API có kiểm tra RBAC + branch scope, database, migrations, secrets, backup/restore và audit actor. UI hiển thị trạng thái scope, nguồn và tính mới của dữ liệu. | Component dùng chung được kiểm thử; API từ chối mặc định khi thiếu quyền; test chéo cơ sở không truy cập được dữ liệu; restore thử nghiệm đạt RPO/RTO đã thống nhất. |
| **2 · Nâng cấp tác vụ cốt lõi và CRUD miền** | Ưu tiên Pet Care và pilot Business/Service: tìm kiếm, hồ sơ, lịch/task/tồn, bảng responsive, form validation, empty/error/stale states; thay CRUD demo bằng API miền, constraints, soft-delete, optimistic locking và audit. | Người dùng hoàn thành luồng ưu tiên theo tiêu chí usability đã đặt; CRUD lưu trên server; schema/khóa/quyền sai bị từ chối; không có lỗi accessibility nghiêm trọng chưa xử lý. |
| **3 · Đồng bộ và tích hợp có kiểm soát** | Chọn một luồng pilot Care ↔ Service hoặc Business ↔ Commerce; áp dụng outbox, event envelope/version, idempotency, retry/backoff, DLQ, replay có quyền và dashboard độ trễ/lỗi. | Duplicate event không tạo duplicate write; consumer lỗi phục hồi được; mọi event truy được correlation ID và audit. |
| **4 · Pilot một cơ sở** | Chạy song song quy trình hiện tại; đào tạo nhân viên bằng prototype/guide; theo dõi hoàn thành tác vụ, lỗi giao diện, CRUD, phân quyền, xung đột, reconcile tồn và hỗ trợ sự cố. Có feature flags, quy trình rollback và người trực vận hành. | Không còn lỗi truy cập vượt quyền mức nghiêm trọng; KPI UX/vận hành và checklist đạt ngưỡng do chủ sản phẩm đặt; quản lý cơ sở ký go/no-go. |
| **5 · Mở rộng theo giá trị và rủi ro** | Mở rộng Service, Health, Commerce rồi Community/Connect theo phê duyệt. Health cần consent/clinical governance trước khi trao đổi dữ liệu; Intelligence chỉ nhận dữ liệu tối thiểu/đã tổng hợp và không tự ghi quyết định nghiệp vụ. | Mỗi miền có owner, threat/privacy review, SLO, runbook, quality gates và kế hoạch hỗ trợ trước khi bật production. |

Yêu cầu giao diện theo từng miền, component dùng chung, quy trình thiết kế và tiêu chí nghiệm thu chi tiết được quản lý riêng trong [UI-UX-UPGRADE-PLAN.md](./UI-UX-UPGRADE-PLAN.md).

Thứ tự hệ thống là khuyến nghị có phụ thuộc: củng cố Pet Care hiện có và dữ liệu nền; ưu tiên Business/Service cho vận hành một cơ sở; thêm Health/Commerce khi quyền và giao dịch đã rõ; mở Community/Connect sau khi có quy trình an toàn; cuối cùng mở Intelligence sau khi lineage, consent và chất lượng dữ liệu được chứng minh.

## 4. Quyền thao tác đề xuất

| Vai trò | Đọc | Thêm | Sửa | Xóa |
|---|---|---|---|---|
| Nhân viên | Theo phân hệ và cơ sở được cấp | Trong hệ sở hữu, cơ sở được phân công | Bản ghi trong phạm vi; trường nhạy cảm cần quyền riêng | Không xóa cứng; gửi yêu cầu hủy/đính chính |
| Quản lý cơ sở | Dữ liệu vận hành cơ sở | Trong phạm vi cơ sở | Phê duyệt các thay đổi nghiệp vụ được ủy quyền | Xóa mềm/hủy theo chính sách; lý do và audit bắt buộc |
| Chuyên gia y tế | Hồ sơ y tế theo ca/mục đích và consent | Hồ sơ chuyên môn được giao | Hồ sơ chuyên môn của ca được phép; đính chính có dấu vết | Không xóa hồ sơ y tế đã ký; tạo bản đính chính |
| Quản trị dữ liệu | Metadata/schema; dữ liệu cá nhân chỉ khi được cấp rõ | Không tự động có quyền sửa mọi hồ sơ nghiệp vụ | Quản trị schema/cấu hình qua change approval | Không xóa nghiệp vụ trực tiếp; thao tác khẩn cấp có break-glass audit |
| Dịch vụ tích hợp | Projection theo service account và audience | Chỉ endpoint/event được cấp | Không sở hữu dữ liệu miền khác | Không xóa |

Quyền cuối cùng phải được quyết định theo nghiệp vụ, luật áp dụng và phân tách nhiệm vụ (maker-checker). Vai trò “admin” không nên mặc định có quyền đọc mọi nội dung y tế/PII.

## 5. Chỉ số và kiểm thử bắt buộc

- **Bảo mật:** kiểm thử ma trận role × action × system × branch; kiểm tra IDOR, escalation, token expiry, rate limit và log không chứa secrets/PII không cần thiết.
- **Tính toàn vẹn:** tỷ lệ khóa tham chiếu hợp lệ; bản ghi trùng; trường thiếu; sai lệch snapshot/source; migration tương thích dữ liệu cũ.
- **Đồng bộ:** event lag p95, tỉ lệ thành công, retry, dead-letter, duplicate, conflict age và thời gian phục hồi.
- **Vận hành:** API availability/latency, lỗi theo endpoint, backup success, restore drill, RPO/RTO và thời gian xử lý sự cố.
- **Trải nghiệm:** tác vụ hoàn thành tại cơ sở, lỗi nhập liệu, thời gian đào tạo và khả năng dùng trên mobile/mạng yếu.
- **Chất lượng phát hành:** unit/integration/e2e, accessibility cơ bản, kiểm tra migration và smoke test staging trước release.

Ngưỡng cụ thể cần được thống nhất sau khi biết số cơ sở, người dùng đồng thời, dữ liệu/tháng, thiết bị, ngân sách và cam kết dịch vụ; không gán SLO giả khi chưa có baseline.

## 6. Rủi ro và quyết định cần chốt

| Rủi ro | Giảm thiểu |
|---|---|
| Nhầm prototype với hệ thống đã triển khai | Gắn nhãn demo/đề xuất; chỉ công bố trạng thái production sau nghiệm thu. |
| Chọn role ở trình duyệt bị giả mạo | Xác thực và authorize ở API/database; kiểm thử negative-path. |
| Sai ID hoặc schema làm lệch dữ liệu | Migration có kiểm soát, FK/unique constraints, data quality checks và replay idempotent. |
| Lộ dữ liệu sức khỏe/liên hệ | Phân loại, consent theo mục đích, field-level minimization, encryption, audit access và retention. |
| Queue lỗi hoặc gửi lặp | Outbox, idempotency, retry/backoff, DLQ, reconcile và runbook replay. |
| Mở rộng quá sớm sang 8 miền | Pilot một cơ sở và một luồng tích hợp; dùng go/no-go có KPI. |
| Quy mô/chi phí vượt giả định | Load test theo baseline; xác nhận hosting, RPO/RTO, ngân sách và on-call trước production. |

Trước khi lập estimates cam kết, cần xác nhận: đội backend/ops hiện có, nền tảng triển khai được phép, IdP/SSO, số cơ sở và người dùng, yêu cầu lưu trữ/riêng tư, tích hợp ngoài hệ thống, ngân sách và người chịu trách nhiệm vận hành.

## 7. Việc làm tiếp theo

1. Chốt phạm vi pilot (khuyến nghị: Pet Care + một quy trình Business/Service tại một cơ sở).
2. Chỉ định product owner, data owner và security/operations reviewer cho từng miền.
3. Phê duyệt data dictionary, ma trận quyền và hợp đồng đầu tiên từ 14 bảng logic.
4. Chọn stack backend/hosting sau khi xác nhận năng lực vận hành; không nối trang demo thẳng vào production database.
5. Tạo backlog có estimates và tiêu chí go/no-go sau khi các quyết định trên được chốt.
