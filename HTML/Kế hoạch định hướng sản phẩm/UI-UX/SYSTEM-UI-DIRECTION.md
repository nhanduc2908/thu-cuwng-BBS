# WAGGY · Định hướng giao diện và kết nối 8 hệ thống

## Mục tiêu

Xây dựng trải nghiệm WAGGY có chung cách điều hướng, nhận diện và tương tác, nhưng giữ workspace riêng cho đúng nghiệp vụ của từng hệ thống. Nhân viên có thể hiểu mình đang ở đâu, đang xem dữ liệu nào, ai sở hữu dữ liệu và bước tiếp theo là gì; chủ nuôi không phải nhập lại thông tin không cần thiết; dữ liệu nhạy cảm chỉ đi qua điểm bàn giao có quyền và mục đích rõ ràng.

Tài liệu này là định hướng thiết kế, không phải đặc tả API hay xác nhận hệ thống đã tích hợp. Pet Care là hệ thống hiện có; các hệ thống còn lại và luồng liên kết là đề xuất/demo.

## 1. Ngôn ngữ giao diện dùng chungq

- **Một app shell:** thương hiệu WAGGY, bộ chuyển hệ thống, breadcrumb, tìm kiếm theo quyền, thông báo, tài khoản và trợ giúp.
- **Một ngữ cảnh nhìn thấy được:** luôn hiển thị hệ thống hiện tại, cơ sở/phạm vi, vai trò nếu phù hợp, bộ lọc đang áp dụng và thời điểm/cập nhật dữ liệu.
- **Một bộ thành phần nhất quán:** design tokens, nút, trường nhập, bảng/card, trạng thái, xác nhận, thông báo, timeline và metadata nguồn/audit.
- **Một chuẩn thao tác:** trạng thái loading, empty, error/retry, permission denied, offline/stale và success có nội dung rõ; hành động ghi/xóa/phê duyệt nêu đối tượng và hệ quả.
- **Trải nghiệm riêng theo miền:** mỗi hệ thống có dashboard, thuật ngữ, biểu mẫu, mật độ thông tin và workflow phù hợp; không ép mọi nghiệp vụ vào cùng một màn hình.
- **Responsive và accessibility:** ưu tiên mobile cho tác vụ hiện trường/cửa hàng; kiểm tra bàn phím, focus, tương phản, reflow và vùng chạm.

## 2. Bản đồ kết nối giao diện và điểm bàn giao

```text
                         ┌─────────────────────────┐
                         │  WAGGY App Shell chung  │
                         │ hệ thống · tìm kiếm     │
                         │ cơ sở · thông báo       │
                         └────────────┬────────────┘
                                      │ chuyển hệ thống có quyền
       ┌───────────────┬──────────────┼───────────────┬────────────────┐
       ▼               ▼              ▼               ▼                ▼
   Pet Care       Pet Business   Pet Service      Pet Health      Pet Commerce
 hồ sơ nền      cơ sở/kho/nhân sự lịch/check-in   hồ sơ chuyên môn catalog/đơn hàng
       │               │              │               │                │
       ├──── hồ sơ ───►│◄─ năng lực ──┤               │                │
       ├────────────────────────────►│               │                │
       ├────────────────────────────────────────────►│                │
       └─────────────────────────────────────────────────────────────►│
                                                                       │ tồn/đơn
                                                                       ▼
                                                                 Pet Business

        Pet Community ── báo cáo/sự kiện/đăng ký ──► Pet Connect
        Pet Care ─────── yêu cầu tìm kiếm/hỗ trợ ──► Pet Connect

   Các nguồn được duyệt, giảm thiểu dữ liệu và có lineage
       Pet Care · Business · Service · Health · Commerce
       Community · Connect ──────────────────────────────► Pet Intelligence
                                                             │
                                          insight/cảnh báo có giải thích
                                          và quyền xem; không ghi ngược
                                          hoặc tự quyết định nghiệp vụ
```

Sơ đồ mô tả **đích đến trải nghiệm**, không khẳng định các mũi tên đang hoạt động. Mỗi mũi tên cần có chủ sở hữu dữ liệu, hợp đồng tích hợp, mục đích, quyền, consent khi cần, trạng thái đồng bộ và audit.

### Các quy tắc điều hướng xuyên hệ thống

1. Người dùng chuyển qua system switcher hoặc một liên kết bàn giao có ngữ cảnh; giao diện đích mở đúng loại bản ghi bằng mã tham chiếu, không dựa vào tên hiển thị.
2. Trước khi mở bản ghi nhạy cảm, hệ thống đích kiểm tra đăng nhập, quyền, phạm vi cơ sở và consent/mục đích. Thiếu điều kiện thì chặn và giải thích; không tự mở dữ liệu thay thế.
3. Giao diện đích phân biệt dữ liệu **do hệ thống sở hữu** với dữ liệu **tham chiếu/chiếu từ hệ thống khác**. Chỉ sửa tại nguồn chuẩn; liên kết đưa người dùng có quyền về nguồn nếu cần chỉnh.
4. Điểm bàn giao hiển thị nguồn, trạng thái, thời điểm cập nhật và bước tiếp theo. Tạo yêu cầu, gửi đi, chờ xác nhận và hoàn tất là các trạng thái khác nhau.
5. Lỗi/mất kết nối không tạo thông báo thành công giả. Bản cũ phải được đánh dấu stale; thao tác ghi chỉ thành công khi nguồn có thẩm quyền xác nhận.
6. Mọi thông tin qua liên kết chỉ ở mức tối thiểu cần dùng; không đưa PII, thông tin sức khỏe, vị trí chính xác hoặc dữ liệu thanh toán vào URL/thông báo không an toàn.

### Các hành trình cần thiết kế đầu-cuối

| Hành trình | Màn hình bắt đầu → nơi bàn giao | Ngữ cảnh cần giữ | Điều kiện kiểm soát |
|---|---|---|---|
| Chăm sóc tại cửa hàng | Pet Care → Pet Service / Pet Business | Mã thú cưng, lịch/task, cơ sở, trạng thái bàn giao | Nhân viên có quyền; Service xác nhận năng lực; ghi nhận kết quả về đúng hồ sơ |
| Nhu cầu sức khỏe | Pet Care → Pet Health | Mã thú cưng, lý do giới thiệu tối thiểu, lịch sử được phép | Consent theo mục đích; hồ sơ chuyên môn do người đủ thẩm quyền ghi |
| Mua và xử lý đơn | Pet Commerce → Pet Business | Mã đơn/SKU, chi nhánh, fulfillment và trạng thái tồn | Business là nguồn vận hành kho; Commerce không hiển thị tồn như cam kết nếu chưa giữ hàng |
| Cộng đồng và cứu hộ | Pet Community → Pet Connect | Mã nội dung/case, lý do báo cáo hoặc nhiệm vụ | Bảo vệ danh tính/vị trí; kiểm duyệt và phân công theo quyền |
| Theo dõi và ra quyết định | Hệ nghiệp vụ → Pet Intelligence → hệ nghiệp vụ | Link tới insight, nguồn, phiên bản và giải thích | Chỉ dataset/use-case được duyệt; insight không tự ghi hoặc thay quyết định con người |

## 3. Định hướng nâng cấp theo hệ thống

### 01 · Pet Care — hồ sơ và chăm sóc

- **Trọng tâm giao diện:** trang hồ sơ thú cưng theo timeline; tìm kiếm/phát hiện hồ sơ trùng; lịch, task và việc đến hạn.
- **Nâng cấp:** đưa việc cần làm hôm nay lên trước; làm gọn tạo/cập nhật công việc trên mobile; phân tách tổng quan và lịch sử dài; thể hiện rõ nguồn chuẩn so với dữ liệu tham chiếu.
- **Liên kết:** điểm xuất phát cho hồ sơ nền và bàn giao có chọn lọc đến Service, Health, Business, Commerce hoặc Connect; không dùng Care làm nơi sửa dữ liệu nghiệp vụ thuộc hệ khác.
- **Màn hình ưu tiên:** tổng quan, khách hàng, thú cưng, lịch, chăm sóc, nhắc việc và hồ sơ sức khỏe được phép.
- **Baseline:** [WAGGY Pet Care demo](../workflow/demo/Giao%20di%E1%BB%87n%20c%E1%BA%A7n%20t%E1%BA%A1o/Pet%20Care/index.html).

### 02 · Pet Business — vận hành cửa hàng và chuỗi

- **Trọng tâm giao diện:** control tower theo chuỗi/cơ sở; kho, mua/nhận hàng, điều chuyển, phê duyệt và đối soát.
- **Nâng cấp:** ghim phạm vi cơ sở/kỳ; KPI có drill-down; tồn theo SKU/lô/vị trí và trạng thái; timeline người chịu trách nhiệm; maker-checker; chế độ quét mã cho kho.
- **Liên kết:** cung cấp thông tin tổ chức, cơ sở, nhân sự, năng lực và trạng thái tồn cho các workflow được phép; nhận tham chiếu giao dịch từ Commerce và Service.
- **Màn hình ưu tiên:** control tower, inventory, receiving, procurement, transfers, approvals, reconciliation, audit.
- **Baseline:** [WAGGY Pet Business demo](../workflow/demo/Giao%20di%E1%BB%87n%20c%E1%BA%A7n%20t%E1%BA%A1o/Pet%20Business/index.html).

### 03 · Pet Service — lịch và thực hiện dịch vụ

- **Trọng tâm giao diện:** lịch năng lực, booking, check-in, checklist, bàn giao và lịch sử dịch vụ.
- **Nâng cấp:** xem lịch ngày/tuần theo nhân viên/cơ sở/nguồn lực; đặt lịch từng bước; công khai giá và điều kiện; timeline trạng thái cùng người thực hiện; thao tác một tay trên mobile.
- **Liên kết:** nhận hồ sơ thú cưng tối thiểu từ Care và lịch/năng lực từ Business; trả trạng thái, kết quả bàn giao và tham chiếu giao dịch theo quyền.
- **Màn hình ưu tiên:** lịch điều phối, booking detail, check-in/out, lịch nhân viên, danh mục dịch vụ và handoff.
- **Baseline:** [WAGGY Pet Service demo](../workflow/demo/Giao%20di%E1%BB%87n%20c%E1%BA%A7n%20t%E1%BA%A1o/Pet%20Service/index.html).

### 04 · Pet Health — hồ sơ sức khỏe và chuyên môn

- **Trọng tâm giao diện:** hàng đợi khám, hồ sơ bệnh nhân, encounter, xét nghiệm, consent và tái khám.
- **Nâng cấp:** ưu tiên nhận diện/cảnh báo quan trọng; timeline có nguồn, thời gian, người ghi và trạng thái ký; kết quả kèm đơn vị/phạm vi tham chiếu; đính chính có lịch sử.
- **Liên kết:** tiếp nhận referral từ Care/Service với consent và dữ liệu tối thiểu; trả lịch/trạng thái hoặc phần tóm tắt được phép, không làm lộ hồ sơ chuyên môn.
- **Màn hình ưu tiên:** patient, encounter, lịch khám, lab review, vaccinations, follow-ups, consent và audit.
- **Baseline:** [WAGGY Pet Health demo](../workflow/demo/Giao%20di%E1%BB%87n%20c%E1%BA%A7n%20t%E1%BA%A1o/Pet%20Health/index.html).

### 05 · Pet Commerce — catalog, đơn hàng và hậu mãi

- **Trọng tâm giao diện:** danh mục, sản phẩm, giỏ/checkout, đơn, fulfillment, thanh toán và đổi trả.
- **Nâng cấp:** minh bạch giá/điều kiện/khả dụng; checkout ngắn nhưng rà soát được; giữ giỏ khi lỗi; timeline đơn và trạng thái chờ xác minh; thao tác hoàn tiền có lý do và quyền duyệt.
- **Liên kết:** tra cứu catalog và trạng thái tồn từ Business; chuyển đơn/fulfillment sang vận hành; chỉ liên kết tới hồ sơ Care khi có mục đích và quyền phù hợp.
- **Màn hình ưu tiên:** catalog, cart/checkout, orders, fulfillment, payments, returns và promotions.
- **Baseline:** [WAGGY Pet Commerce demo](../workflow/demo/Giao%20di%E1%BB%87n%20c%E1%BA%A7n%20t%E1%BA%A1o/Pet%20Commerce/index.html).

### 06 · Pet Community — cộng đồng và Trust & Safety

- **Trọng tâm giao diện:** feed, sự kiện, báo cáo, moderation queue, quyết định và kháng nghị.
- **Nâng cấp:** tách nội dung quảng bá; làm rõ lý do/ưu tiên/chính sách khi duyệt; cung cấp giải thích và appeal; công cụ chặn/báo cáo dễ thấy; giới hạn dữ liệu thành viên.
- **Liên kết:** gửi báo cáo, sự kiện hoặc nhiệm vụ cần phối hợp đến Connect bằng mã tham chiếu; chỉ trao đổi trạng thái và dữ liệu tối thiểu cần thiết.
- **Màn hình ưu tiên:** feed/posts, moderation queue, reports, appeals, events, member safety và announcements.
- **Baseline:** [WAGGY Pet Community demo](../workflow/demo/Giao%20di%E1%BB%87n%20c%E1%BA%A7n%20t%E1%BA%A1o/Pet%20Community/index.html).

### 07 · Pet Connect — thất lạc, cứu hộ và bàn giao

- **Trọng tâm giao diện:** case, bản đồ/tác vụ hiện trường, bằng chứng, đối tác, kiểm tra an toàn và bàn giao.
- **Nâng cấp:** tạo case theo bước; bản đồ có chế độ danh sách; giảm chính xác vị trí theo vai trò/trạng thái; timeline phân công/xác minh; checklist bàn giao và escalation.
- **Liên kết:** nhận yêu cầu có kiểm soát từ Care/Community; trả trạng thái cho người gửi; không công khai thông tin liên hệ, bằng chứng hoặc vị trí chính xác.
- **Màn hình ưu tiên:** lost-pet case, field map, evidence, rescue tasks, partners, safety check và handoff.
- **Baseline:** [WAGGY Pet Connect demo](../workflow/demo/Giao%20di%E1%BB%87n%20c%E1%BA%A7n%20t%E1%BA%A1o/Pet%20Connect/index.html).

### 08 · Pet Intelligence — governance và insight

- **Trọng tâm giao diện:** chất lượng dữ liệu, lineage, dataset/use-case, model registry, đánh giá, drift, sự cố và rollback.
- **Nâng cấp:** truy vết nguồn → biến đổi → consumer; hiển thị quyền/mục đích/schema; giải thích giới hạn của insight; phân biệt shadow/pilot/production; có người phê duyệt.
- **Liên kết:** nhận dữ liệu đã duyệt, giảm thiểu và có lineage từ các hệ; cung cấp insight có giải thích quay về màn hình nghiệp vụ bằng liên kết chỉ đọc.
- **Màn hình ưu tiên:** datasets, lineage, evaluations, approvals, model registry, monitoring, incidents và rollback.
- **Baseline:** [WAGGY Pet Intelligence demo](../workflow/demo/Giao%20di%E1%BB%87n%20c%E1%BA%A7n%20t%E1%BA%A1o/Pet%20Intelligence/index.html).

## 4. Lộ trình nâng cấp giao diện đề xuất

| Chặng | Phạm vi | Điều kiện hoàn tất |
|---|---|---|
| 0 · Nền dùng chung | Audit 8 demo, design tokens, app shell, system switcher, search/scope, trạng thái và accessibility baseline | Component/state inventory; xác nhận vai trò, quyền và trạng thái; không làm sai lệch mức độ production |
| 1 · Tác nghiệp cửa hàng | Pet Care + Pet Business + Pet Service | Một luồng hồ sơ → đặt lịch → tiếp nhận/bàn giao được kiểm thử; Mobile và desktop; nguồn chuẩn rõ |
| 2 · Chuyên môn và giao dịch | Pet Health + Pet Commerce | Consent, quyền, trạng thái chuyên môn/thanh toán, ngoại lệ và audit được duyệt |
| 3 · Cộng đồng/hiện trường | Pet Community + Pet Connect | Moderation/appeal, bảo vệ vị trí và danh tính, bàn giao có kiểm soát được usability test |
| 4 · Insight có quản trị | Pet Intelligence và điểm đọc insight ở các workspace | Lineage/use-case được duyệt; insight có giải thích, owner, quyền xem và không tự ghi nghiệp vụ |
| 5 · Theo dõi, cải tiến | Tất cả luồng đã phát hành | Đo baseline và usability, lỗi tác vụ, accessibility, phản hồi, sự cố quyền; có owner và kế hoạch sửa |

Thứ tự là đề xuất phụ thuộc mức sẵn sàng nghiệp vụ, chủ dữ liệu, nguồn lực và kết quả pilot; không phải cam kết ngày phát hành.

## 5. Tiêu chí nghiệm thu xuyên hệ thống

- Người dùng xác định được hệ thống, cơ sở/phạm vi, nguồn dữ liệu và trạng thái cập nhật.
- Luồng cốt lõi hoàn thành được trên mobile và desktop; link bàn giao giữ đúng mã tham chiếu và đích đến, không mất ngữ cảnh quan trọng.
- Hệ đích kiểm tra quyền/consent độc lập; không dựa vào việc người dùng đã nhìn thấy liên kết từ hệ nguồn.
- Dữ liệu nguồn và projection phân biệt rõ; thao tác sửa chỉ thực hiện tại nơi sở hữu dữ liệu.
- Loading, empty, lỗi, retry, từ chối quyền, offline/stale và success được kiểm thử; không có success giả.
- Thông tin nhạy cảm không rò rỉ qua URL, notification, preview hoặc workspace không được phép.
- Kiểm tra responsive, bàn phím, focus, tương phản, zoom/reflow và screen-reader labels cho các luồng cốt lõi.
- Nghiệm thu bởi đại diện người dùng và chủ nghiệp vụ từng hệ thống; xác nhận các liên kết xuyên hệ thống là demo hay production.
