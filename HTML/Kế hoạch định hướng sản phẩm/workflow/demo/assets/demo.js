(() => {
  const systems = {
    "pet-care": {
      name: "Pet Care", product: "Hồ sơ & vận hành chăm sóc", status: "ĐANG CÓ · DEMO", current: true,
      description: "Màn hình điều hành minh họa dựa trên các phân hệ hiện có. Dữ liệu bên dưới là dữ liệu mẫu, không đọc từ cơ sở dữ liệu Pet Care.",
      nav: ["Tổng quan", "Khách hàng & thú cưng", "Động vật cửa hàng", "Chăm sóc", "Sức khỏe", "Dịch vụ", "Bán hàng", "Tồn kho", "Báo cáo"],
      metrics: [["Hồ sơ khách", "1.248", "Trong dữ liệu demo"], ["Việc chăm sóc", "18", "6 việc đến hạn hôm nay"], ["Lịch dịch vụ", "12", "Theo lịch mẫu hôm nay"], ["Tồn cần rà soát", "7", "Lô sắp hết hoặc cần kiểm kê"]],
      tableTitle: "Công việc đang theo dõi", tableHint: "Danh sách minh họa từ các phân hệ Pet Care", tableAction: "Mở phân hệ",
      columns: ["Mã", "Đối tượng", "Phân hệ", "Người phụ trách", "Trạng thái"],
      rows: [
        [["CARE-1042", "08:30 · lịch chăm sóc"], ["Milo · chó Poodle", "Hồ sơ cửa hàng"], ["Chăm sóc", null, "tag blue"], ["Linh Nguyễn"], ["Đến hạn", null, "tag gold"]],
        [["SVC-2081", "09:00 · cơ sở trung tâm"], ["Bông · mèo Anh lông ngắn", "Khách: Nguyễn An"], ["Dịch vụ", null, "tag blue"], ["Minh Trần"], ["Đã xác nhận", null, "tag"]],
        [["HLT-0634", "10:15 · hồ sơ sức khỏe"], ["Mít · chó ta", "Cần xem lại lần khám"], ["Sức khỏe", null, "tag blue"], ["BS. Hà"], ["Chờ rà soát", null, "tag gold"]],
        [["INV-3408", "Lô thức ăn · hạn 30 ngày"], ["Thức ăn mèo 2kg", "Kho cửa hàng"], ["Tồn kho", null, "tag blue"], ["Quang Lê"], ["Cần kiểm tra", null, "tag red"]],
        [["SAL-0917", "11:42 · thanh toán một phần"], ["Đơn sản phẩm #0917", "Khách: Trần Mai"], ["Bán hàng", null, "tag blue"], ["Huy Phạm"], ["Đang xử lý", null, "tag neutral"]]
      ],
      listTitle: "Nhắc việc trong ngày", listHint: "Thông tin mẫu · kiểm tra tại phân hệ nguồn",
      items: [["Đối chiếu task chăm sóc", "6 task chưa đánh dấu hoàn tất", "08:00", "gold"], ["Lịch hẹn sắp tới", "3 lịch trong 60 phút", "09:00", "blue"], ["Lô hàng cần rà soát", "Kiểm tra hạn dùng / lượng khả dụng", "Hôm nay", "red"]],
      chartTitle: "Hoạt động theo ngày", chartHint: "Số tác vụ mẫu đã ghi nhận", chart: [["T2", 45], ["T3", 61], ["T4", 52], ["T5", 78], ["T6", 66], ["T7", 88], ["CN", 56]],
      actions: [["Tạo nhiệm vụ chăm sóc", "Ghi task cho animal và chọn người phụ trách."], ["Mở hồ sơ khách", "Tra cứu khách hàng và thú cưng đã liên kết."], ["Ghi nhận khám", "Mở phân hệ sức khỏe; nội dung chuyên môn do người có thẩm quyền nhập."], ["Xem báo cáo", "Chọn loại báo cáo và khoảng ngày theo quyền hiện có."]],
      note: "Giao diện minh họa; vai trò, quyền và trạng thái thực tế phụ thuộc bản cài Pet Care. Không thể tạo đơn hoặc sửa dữ liệu thật từ demo."
    },
    "pet-service": {
      name: "Pet Service", product: "Lịch hẹn & điều phối dịch vụ", status: "ĐỀ XUẤT · DEMO", current: false,
      description: "Bàn điều phối lịch tắm, grooming, spa và lưu trú; hiển thị slot, nhân sự, tài nguyên, check-in và bàn giao.",
      nav: ["Bảng điều phối", "Lịch hẹn", "Lịch nhân sự", "Danh mục dịch vụ", "Khách & thú cưng", "Thanh toán", "Báo cáo"],
      metrics: [["Lịch hôm nay", "24", "17 đã xác nhận"], ["Chờ check-in", "5", "Trong 2 giờ tới"], ["Sức chứa", "82%", "Theo cơ sở demo"], ["Cần xác nhận", "3", "Đổi lịch / báo giá"]],
      tableTitle: "Lịch hẹn hôm nay", tableHint: "Lọc theo trạng thái · chọn lịch để xem chi tiết", tableAction: "Tạo lịch hẹn",
      columns: ["Giờ", "Khách · thú cưng", "Dịch vụ", "Nhân viên", "Trạng thái"],
      rows: [
        [["09:00", "45 phút"], ["Nguyễn An", "Bông · mèo · 4 tuổi"], ["Tắm & sấy", "Gói cơ bản"], ["Linh · Grooming"], ["Đã check-in", null, "tag"]],
        [["09:30", "90 phút"], ["Trần Mai", "Milo · Poodle · 3 tuổi"], ["Grooming", "Cắt tỉa tiêu chuẩn"], ["Quân · Grooming"], ["Đang thực hiện", null, "tag blue"]],
        [["10:00", "2 đêm"], ["Lê Minh", "Đậu · chó ta · 8kg"], ["Lưu trú", "Phòng nhỏ · 2 đêm"], ["Ca trực A"], ["Chờ check-in", null, "tag gold"]],
        [["10:30", "60 phút"], ["Phạm Vy", "Nâu · Corgi · 2 tuổi"], ["Spa da lông", "Cần xác nhận ghi chú"], ["Hà · Spa"], ["Chờ xác nhận", null, "tag red"]],
        [["11:00", "40 phút"], ["Võ Nam", "Miu · mèo · 2 tuổi"], ["Tắm vệ sinh", "Gói cơ bản"], ["Linh · Grooming"], ["Đã đặt", null, "tag"]]
      ],
      listTitle: "Tài nguyên ca sáng", listHint: "Khả dụng theo lịch mẫu",
      items: [["Bàn grooming 01", "Linh · 09:00–12:00", "Đang dùng", "blue"], ["Khu lưu trú A", "Sức chứa 8 · đang nhận 6", "Còn 2", "gold"], ["Phòng spa 02", "Hà · 10:30–13:00", "Đã xếp lịch", "neutral"]],
      chartTitle: "Công suất theo khung giờ", chartHint: "Phần trăm slot đã xếp · dữ liệu demo", chart: [["08", 32], ["09", 76], ["10", 90], ["11", 68], ["12", 40], ["13", 58], ["14", 72]],
      actions: [["Đặt lịch mới", "Mô phỏng nhập thú cưng, dịch vụ, chi nhánh và giờ mong muốn."], ["Check-in", "Mô phỏng xác nhận mã lịch, người giao và tình trạng ban đầu."], ["Điều phối nhân viên", "Mô phỏng xếp nhân sự và tài nguyên; không giữ chỗ thật."], ["Bàn giao dịch vụ", "Mô phỏng checklist hoàn tất và xác nhận người nhận."]],
      note: "Pet Service là đề xuất. Giữ chỗ, giá, sức chứa, lịch nhân viên và thông báo trong màn hình này đều là dữ liệu giả lập."
    },
    "pet-health": {
      name: "Pet Health", product: "Hồ sơ khám & điều phối chăm sóc sức khỏe", status: "ĐỀ XUẤT · DEMO", current: false,
      description: "Không gian làm việc cho phòng khám: lịch khám, hồ sơ encounter, chỉ định xét nghiệm, xác thực kết quả và tái khám có consent.",
      nav: ["Tổng quan y tế", "Lịch khám", "Hồ sơ bệnh án", "Tiêm chủng", "Xét nghiệm", "Phòng khám", "Consent & truy cập"],
      metrics: [["Lịch khám hôm nay", "16", "4 ca cần tiếp nhận"], ["Chờ bác sĩ duyệt", "7", "Hồ sơ / kết quả"], ["Mẫu đang xử lý", "9", "3 mẫu cần theo dõi"], ["Tái khám sắp đến", "21", "7 ngày tiếp theo"]],
      tableTitle: "Hàng đợi chuyên môn", tableHint: "Thông tin sức khỏe nhạy cảm · chỉ người được cấp quyền", tableAction: "Tạo encounter",
      columns: ["Thời gian", "Thú cưng · chủ nuôi", "Loại lượt", "Phụ trách", "Trạng thái"],
      rows: [
        [["08:45", "Hôm nay"], ["Bông · mèo", "Chủ nuôi: Nguyễn An"], ["Khám tổng quát"], ["BS. Phương"], ["Đang khám", null, "tag blue"]],
        [["09:30", "Hôm nay"], ["Milo · chó Poodle", "Chủ nuôi: Trần Mai"], ["Tái khám"], ["BS. Hà"], ["Chờ tiếp nhận", null, "tag gold"]],
        [["10:00", "Hôm nay"], ["Đậu · chó ta", "Consent: clinic A"], ["Xét nghiệm máu"], ["KTV. Nam"], ["Chờ kết quả", null, "tag"]],
        [["10:30", "Hôm nay"], ["Mít · mèo", "Kết quả cần xác thực"], ["Đọc kết quả"], ["BS. Phương"], ["Chờ duyệt", null, "tag red"]],
        [["11:15", "Hôm nay"], ["Nâu · Corgi", "Tiêm nhắc theo lịch"], ["Tiêm chủng"], ["BS. Hà"], ["Đã xác nhận", null, "tag"]]
      ],
      listTitle: "Cổng xác thực hồ sơ", listHint: "Hồ sơ chỉ phát hành sau người có chuyên môn duyệt",
      items: [["Kết quả xét nghiệm #LAB-0281", "Chờ bác sĩ xác thực", "Ưu tiên", "red"], ["Hồ sơ khám #ENC-1048", "Thiếu chữ ký phát hành", "Kiểm tra", "gold"], ["Consent chia sẻ #CNS-332", "Clinic A · hết hạn 16:00", "Theo dõi", "blue"]],
      chartTitle: "Lịch tái khám", chartHint: "Số lịch theo tuần · minh họa", chart: [["T2", 28], ["T3", 41], ["T4", 36], ["T5", 58], ["T6", 47], ["T7", 72], ["CN", 19]],
      actions: [["Tiếp nhận lượt khám", "Mô phỏng xác minh pet ID, đại diện và consent."], ["Ghi hồ sơ khám", "Mô phỏng encounter nháp; không phát hành chẩn đoán."], ["Theo dõi mẫu xét nghiệm", "Mô phỏng mã mẫu và các lần bàn giao."], ["Tạo lịch tái khám", "Mô phỏng lịch nhắc theo chỉ định đã xác nhận."]],
      note: "Pet Health là đề xuất, không thay thế cơ sở thú y. Dữ liệu bệnh án, kết quả và consent trên màn hình là giả lập; không chứa lời khuyên điều trị."
    },
    "pet-commerce": {
      name: "Pet Commerce", product: "Đơn hàng & fulfillment", status: "ĐỀ XUẤT · DEMO", current: false,
      description: "Bảng vận hành storefront từ catalog được duyệt đến đơn, xác minh thanh toán, phân bổ kho, giao nhận và đổi trả.",
      nav: ["Tổng quan", "Đơn hàng", "Catalog", "Thanh toán", "Fulfillment", "Đổi trả", "Khuyến mãi", "Đối soát"],
      metrics: [["Đơn mới hôm nay", "86", "12 chờ xác nhận"], ["Chờ đóng gói", "19", "Theo kho demo"], ["Thanh toán cần soát", "4", "Pending / không rõ"], ["Đổi trả mở", "6", "2 cần duyệt"]],
      tableTitle: "Đơn hàng gần đây", tableHint: "Trạng thái đơn, thanh toán và fulfillment tách biệt", tableAction: "Tạo đơn demo",
      columns: ["Mã đơn", "Khách hàng", "Sản phẩm", "Thanh toán", "Fulfillment"],
      rows: [
        [["WG-24081", "10:42"], ["Nguyễn An", "Hà Nội"], ["Thức ăn mèo 2kg × 2", "Kho HN-01"], ["Đã xác minh", null, "tag"], ["Chờ lấy hàng", null, "tag gold"]],
        [["WG-24080", "10:31"], ["Trần Mai", "TP.HCM"], ["Dây dắt size M × 1", "Kho HCM-02"], ["Đã xác minh", null, "tag"], ["Đang đóng gói", null, "tag blue"]],
        [["WG-24079", "10:12"], ["Lê Minh", "Đà Nẵng"], ["Combo chăm sóc × 1", "Kho DN-01"], ["Đang đối soát", null, "tag gold"], ["Chưa phân bổ", null, "tag neutral"]],
        [["WG-24078", "09:54"], ["Phạm Vy", "Hà Nội"], ["Cát vệ sinh 5L × 3", "Kho HN-01"], ["Đã xác minh", null, "tag"], ["Đang giao", null, "tag blue"]],
        [["WG-24077", "09:20"], ["Võ Nam", "Cần Thơ"], ["Pate gà × 12", "Kho CT-01"], ["Hoàn một phần", null, "tag red"], ["Case đổi trả", null, "tag gold"]]
      ],
      listTitle: "Cảnh báo đơn hàng", listHint: "Cần kiểm tra trước khi ghi nhận hoàn tất",
      items: [["Payment pending #24079", "Tra cứu provider trước khi retry", "Chờ", "gold"], ["SKU FOOD-220", "Tồn khả dụng thấp tại HN-01", "Cảnh báo", "red"], ["Đổi trả #RMA-018", "Chờ duyệt tình trạng hàng", "Mở", "blue"]],
      chartTitle: "Đơn theo trạng thái", chartHint: "Tỷ trọng đơn trong dữ liệu demo", chart: [["Mới", 66], ["Chờ thu", 31], ["Xử lý", 74], ["Giao", 89], ["Đổi", 24]],
      actions: [["Duyệt catalog", "Mô phỏng kiểm tra SKU, nguồn gốc, giá và cảnh báo."], ["Xem payment", "Mô phỏng đối chiếu mã đơn, số tiền và giao dịch."], ["Tạo lệnh lấy hàng", "Mô phỏng phân bổ kho và line items."], ["Mở case đổi trả", "Mô phỏng yêu cầu RMA gắn order line."]],
      note: "Commerce là đề xuất. Màn hình không kết nối payment provider, cửa hàng, tồn kho hay nhà vận chuyển; không tạo đơn hoặc thu tiền thật."
    },
    "pet-business": {
      name: "Pet Business", product: "Vận hành chuỗi & kiểm soát", status: "ĐỀ XUẤT · DEMO", current: false,
      description: "Bàn điều hành đa chi nhánh cho mua hàng, tồn, nhân sự, dịch vụ, doanh thu và các bước phê duyệt.",
      nav: ["Toàn cảnh", "Chi nhánh", "Mua hàng", "Tồn kho", "Nhân sự & ca", "Dịch vụ", "Tài chính", "Báo cáo"],
      metrics: [["Doanh thu mẫu", "₫128,4tr", "Kỳ demo hiện tại"], ["Đơn mua chờ duyệt", "8", "₫24,6tr dự kiến"], ["SKU dưới ngưỡng", "13", "Trên 3 chi nhánh"], ["Chênh lệch cần soát", "2", "Chưa khóa kỳ"]],
      tableTitle: "Hàng đợi vận hành", tableHint: "Tác vụ đa chi nhánh · quyền duyệt tách khỏi người lập", tableAction: "Tạo đề nghị mua",
      columns: ["Mã tác vụ", "Chi nhánh", "Nghiệp vụ", "Người lập", "Trạng thái"],
      rows: [
        [["PO-0084", "Mua hàng"], ["WAGGY Hà Nội", "Kho HN-01"], ["Nhập thức ăn · 32 SKU"], ["Ngọc Phạm"], ["Chờ duyệt", null, "tag gold"]],
        [["STK-0141", "Kiểm kê"], ["WAGGY Thủ Đức", "Kho TD-02"], ["Chênh lệch 4 dòng"], ["Tuấn Lê"], ["Cần xác minh", null, "tag red"]],
        [["TR-0212", "Điều chuyển"], ["HN-01 → HN-02", "Chi nhánh Hà Nội"], ["Chuyển phụ kiện"], ["Mai Võ"], ["Đang vận chuyển", null, "tag blue"]],
        [["CSH-0061", "Đóng ca"], ["WAGGY Đà Nẵng", "Ca sáng"], ["Lệch quỹ ₫120.000"], ["Huy Trần"], ["Chờ đối soát", null, "tag gold"]],
        [["EMP-0038", "Phân quyền"], ["WAGGY Cần Thơ", "Tài khoản nhân viên"], ["Yêu cầu quyền kho"], ["Admin cơ sở"], ["Chờ phê duyệt", null, "tag"]]
      ],
      listTitle: "Ngưỡng tồn theo chi nhánh", listHint: "Mức khả dụng theo bộ dữ liệu demo",
      items: [["Thức ăn chó 3kg", "HN-01 · còn 8 / ngưỡng 12", "Thấp", "red"], ["Cát vệ sinh 5L", "HCM-02 · còn 17 / ngưỡng 20", "Theo dõi", "gold"], ["Dây dắt size M", "DN-01 · còn 31 / ngưỡng 10", "Ổn định", "blue"]],
      chartTitle: "Hiệu suất các chi nhánh", chartHint: "Chỉ số thực hiện kế hoạch · mẫu", chart: [["HN", 82], ["HCM", 74], ["ĐN", 68], ["CT", 59], ["BD", 77]],
      actions: [["Lập đề nghị mua", "Mô phỏng chọn nhà cung cấp, SKU và ngân sách."], ["Duyệt giao dịch", "Mô phỏng luồng maker-checker, không thay sổ thật."], ["Điều chuyển kho", "Mô phỏng phiếu xuất và nhận hai đầu."], ["Đối soát ca", "Mô phỏng chênh lệch tiền, đơn và tồn."]],
      note: "Pet Business là đề xuất. Các chi nhánh, số tiền, nhân sự và tồn kho trên màn hình đều là dữ liệu giả lập; không tạo chứng từ kế toán."
    },
    "pet-community": {
      name: "Pet Community", product: "Cộng đồng & kiểm duyệt", status: "ĐỀ XUẤT · DEMO", current: false,
      description: "Không gian quản trị cộng đồng với feed nội dung, hàng đợi báo cáo, lịch sự kiện và các quyền riêng tư thành viên.",
      nav: ["Bảng tin", "Nhóm", "Sự kiện", "Hàng đợi kiểm duyệt", "Báo cáo", "Kháng nghị", "Quy tắc cộng đồng"],
      metrics: [["Bài chờ rà soát", "14", "5 mức ưu tiên cao"], ["Báo cáo mở", "9", "Theo SLA minh họa"], ["Sự kiện sắp tới", "6", "2 cần duyệt"], ["Kháng nghị", "3", "Chờ reviewer"]],
      tableTitle: "Hàng đợi an toàn", tableHint: "Quyết định phải có căn cứ và người xử lý", tableAction: "Mở báo cáo",
      columns: ["Case", "Nội dung", "Lý do báo cáo", "Mức ưu tiên", "Trạng thái"],
      rows: [
        [["MOD-0412", "Bài đăng · Nhóm mèo"], ["Ảnh có thể lộ thông tin liên hệ", "Người báo: ẩn danh"], ["Lộ dữ liệu", null, "tag red"], ["Cần rà soát", null, "tag gold"]],
        [["MOD-0411", "Bình luận"], ["Nội dung y tế chưa kiểm chứng"], ["Báo cáo cộng đồng"], ["Thông tin sức khỏe", null, "tag gold"], ["Đang xử lý", null, "tag blue"]],
        [["MOD-0408", "Tài khoản"], ["Hành vi spam lặp lại"], ["3 báo cáo"], ["Trung bình", null, "tag blue"], ["Chờ reviewer", null, "tag"]],
        [["EVT-0128", "Sự kiện · cuối tuần"], ["Ngày hội nhận nuôi"], ["Thiếu người chịu trách nhiệm"], ["Cần bổ sung", null, "tag gold"], ["Bản nháp", null, "tag neutral"]],
        [["APL-0032", "Kháng nghị"], ["Yêu cầu xem lại quyết định"], ["Ẩn bài MOD-0391"], ["Theo SLA", null, "tag blue"], ["Chờ độc lập", null, "tag"]]
      ],
      listTitle: "Lịch nội dung & sự kiện", listHint: "Chỉ hiển thị nội dung được phép công khai",
      items: [["Ngày hội thú cưng", "Chủ nhật · Công viên trung tâm", "Còn 4 ngày", "blue"], ["Buổi chia sẻ chăm sóc", "Nhóm người nuôi chó", "Chờ duyệt", "gold"], ["Bài ghim cộng đồng", "Quy tắc an toàn khi nhận nuôi", "Đang hiển thị", "neutral"]],
      chartTitle: "Báo cáo theo nhóm lý do", chartHint: "Số case mẫu trong 7 ngày", chart: [["Spam", 63], ["PII", 31], ["Y tế", 49], ["Quấy", 25], ["Khác", 38]],
      actions: [["Rà soát case", "Mô phỏng mở bằng chứng và quy tắc phiên bản."], ["Duyệt sự kiện", "Mô phỏng kiểm tra an toàn, sức chứa và người tổ chức."], ["Xử lý kháng nghị", "Mô phỏng chuyển reviewer độc lập."], ["Tạo bài thông báo", "Mô phỏng nội dung có giới hạn người xem."]],
      note: "Pet Community là đề xuất. Không có bài đăng, báo cáo vi phạm hay thông tin thành viên thật trong giao diện này."
    },
    "pet-connect": {
      name: "Pet Connect", product: "Case thất lạc & cứu hộ", status: "ĐỀ XUẤT · DEMO", current: false,
      description: "Bàn điều phối case mất/tìm thấy, yêu cầu cứu hộ và nhận nuôi; vị trí chi tiết, bằng chứng và liên hệ được giới hạn theo case.",
      nav: ["Bảng điều phối", "Case thất lạc", "Tin tìm thấy", "Cứu hộ", "Nhận nuôi", "Đối tác", "Kiểm duyệt"],
      metrics: [["Case đang mở", "38", "Theo khu vực demo"], ["Match cần xác minh", "7", "Không tự xác nhận"], ["Yêu cầu cứu hộ", "5", "2 ưu tiên cao"], ["Bàn giao hôm nay", "3", "Cần xác nhận hai phía"]],
      tableTitle: "Case cần điều phối", tableHint: "Địa điểm hiển thị ở mức khu vực gần đúng", tableAction: "Tạo case",
      columns: ["Case ID", "Loại & thú cưng", "Khu vực", "Điều phối", "Trạng thái"],
      rows: [
        [["PC-24061", "Mất · 09:12"], ["Mèo mướp · đeo vòng xanh", "Ảnh đã kiểm duyệt"], ["Cầu Giấy · Hà Nội"], ["H. Nguyễn"], ["Đang tìm", null, "tag blue"]],
        [["PC-24058", "Tìm thấy · hôm qua"], ["Chó nhỏ màu nâu", "Đặc điểm xác minh riêng"], ["Thủ Đức · TP.HCM"], ["M. Lê"], ["Match tiềm năng", null, "tag gold"]],
        [["PC-24052", "Cứu hộ · ưu tiên"], ["Mèo bị thương · cần hỗ trợ"], ["Hải Châu · Đà Nẵng"], ["Điều phối trực"], ["Đã chuyển đối tác", null, "tag red"]],
        [["PC-24047", "Nhận nuôi"], ["Chó trưởng thành · đã chăm sóc"], ["Ninh Kiều · Cần Thơ"], ["T. Phạm"], ["Đang thẩm định", null, "tag"]],
        [["PC-24042", "Đoàn tụ · hôm nay"], ["Bông · mèo tam thể"], ["Bình Thạnh · TP.HCM"], ["A. Võ"], ["Chờ xác nhận", null, "tag gold"]]
      ],
      listTitle: "Đối tác trực ca", listHint: "Năng lực và quyền nhận case minh họa",
      items: [["Nhóm cứu hộ miền Bắc", "Tiếp nhận mèo · 2 chỗ tạm", "Đang trực", "blue"], ["Phòng khám đối tác A", "Sơ cứu · theo lịch trực", "Đã xác minh", "neutral"], ["Nhà tạm lánh cộng đồng", "Chó nhỏ · cần đặt trước", "Còn 1 chỗ", "gold"]],
      chartTitle: "Case theo trạng thái", chartHint: "Số lượng mô phỏng theo tuần", chart: [["Mới", 49], ["Rà soát", 28], ["Đang tìm", 77], ["Match", 38], ["Đóng", 64]],
      actions: [["Tiếp nhận tin báo", "Mô phỏng tạo case với dữ liệu công khai và trường riêng tách biệt."], ["Xác minh match", "Mô phỏng đối chiếu đặc điểm bí mật; không quyết định chủ sở hữu."], ["Chuyển đối tác", "Mô phỏng cấp quyền truy cập theo case và thời hạn."], ["Ghi nhận bàn giao", "Mô phỏng xác nhận người giao/nhận và tình trạng."]],
      note: "Pet Connect là đề xuất. Vị trí, người báo tin, bằng chứng và đối tác đều là dữ liệu giả; không có bản đồ/vị trí chính xác hoặc liên hệ thật."
    },
    "pet-intelligence": {
      name: "Pet Intelligence", product: "Governance dữ liệu & insight", status: "ĐỀ XUẤT · DEMO", current: false,
      description: "Bảng quản trị use-case phân tích: nguồn dữ liệu được duyệt, kiểm định, phát hành có kiểm soát và giám sát/rollback.",
      nav: ["Tổng quan", "Use-case", "Dataset & lineage", "Đánh giá", "Khuyến nghị", "Giám sát", "Audit"],
      metrics: [["Use-case đang duyệt", "5", "2 cần data owner"], ["Dataset được duyệt", "12", "Theo mục đích sử dụng"], ["Model trong pilot", "3", "Shadow / nhóm giới hạn"], ["Cảnh báo monitoring", "2", "Chờ reviewer"]],
      tableTitle: "Danh mục use-case", tableHint: "Không phát hành nếu thiếu owner, căn cứ hoặc phương án rollback", tableAction: "Đăng ký use-case",
      columns: ["Mã", "Mục tiêu", "Nguồn dữ liệu", "Owner", "Cổng governance"],
      rows: [
        [["AI-0104", "Phân tích nhu cầu tồn"], ["Tổng hợp theo chi nhánh"], ["Business · aggregate"], ["Data owner: Retail"], ["Đang đánh giá", null, "tag gold"]],
        [["AI-0102", "Gợi ý nhắc lịch chăm sóc"], ["Chỉ số đã giảm định danh"], ["Care · consent scope"], ["Owner: Pet Care"], ["Pilot giới hạn", null, "tag blue"]],
        [["AI-0098", "Dự báo nhu cầu dịch vụ"], ["Booking aggregate"], ["Service · schema v2"], ["Owner: Operations"], ["Chờ review", null, "tag gold"]],
        [["AI-0092", "Chất lượng dữ liệu catalog"], ["SKU & taxonomy"], ["Commerce · read-only"], ["Owner: Catalog"], ["Đang giám sát", null, "tag"]],
        [["AI-0088", "Cohort sức khỏe"], ["Chưa có dataset được duyệt"], ["Health · blocked"], ["Data owner: Health"], ["Tạm dừng", null, "tag red"]]
      ],
      listTitle: "Giám sát & ngưỡng dừng", listHint: "Không tự động ghi nghiệp vụ",
      items: [["AI-0102 · Data freshness", "Nguồn cập nhật chậm hơn ngưỡng", "Cảnh báo", "gold"], ["AI-0098 · Sai số theo nhóm", "Reviewer cần xem cohort nhỏ", "Rà soát", "red"], ["Recommendation API", "Human approval bắt buộc", "Bật", "blue"]],
      chartTitle: "Chất lượng dữ liệu", chartHint: "Điểm kiểm tra minh họa theo nguồn", chart: [["Care", 86], ["Biz", 78], ["Svc", 69], ["Comm", 82], ["Health", 54]],
      actions: [["Tạo use-case", "Mô phỏng biểu mẫu mục đích, owner, dữ liệu và rủi ro."], ["Duyệt dataset", "Mô phỏng kiểm tra lineage, consent và tenant scope."], ["Mở đánh giá", "Mô phỏng kiểm định độc lập và quyết định go/no-go."], ["Kích hoạt rollback", "Mô phỏng dừng phát hành và chuyển quy trình thủ công."]],
      note: "Pet Intelligence là đề xuất. Điểm số và model là mẫu minh họa; màn hình không đọc dữ liệu cá nhân hay tự ra quyết định nghiệp vụ."
    }
  };

  const pageCatalog = {
    "pet-care": [
      ["overview", "Tổng quan", "Tình hình chăm sóc, lịch và cảnh báo trong ngày."],
      ["pets", "Hồ sơ thú cưng", "Tra cứu thú cưng, chủ nuôi và các liên kết nghiệp vụ."],
      ["customers", "Khách hàng", "Danh sách khách hàng, phương thức liên hệ và thú cưng liên kết."],
      ["care-tasks", "Nhiệm vụ chăm sóc", "Theo dõi checklist chăm sóc, người phụ trách và hạn xử lý."],
      ["health-records", "Hồ sơ sức khỏe", "Xem trạng thái hồ sơ và chuyển ca cần duyệt đến chuyên môn."],
      ["appointments", "Lịch hẹn", "Theo dõi lịch dịch vụ và lịch chăm sóc theo thời gian."],
      ["services", "Danh mục dịch vụ", "Quản lý dịch vụ mẫu, thời lượng và khả năng đặt lịch."],
      ["sales", "Đơn bán hàng", "Theo dõi đơn hàng, trạng thái xử lý và tham chiếu khách hàng."],
      ["inventory", "Tồn kho", "Rà soát SKU, lượng khả dụng và lô hàng cần chú ý."],
      ["suppliers", "Nhà cung cấp", "Tra cứu nhà cung cấp và thông tin phục vụ mua hàng."],
      ["reminders", "Nhắc việc", "Tổng hợp nhắc lịch, task đến hạn và các cảnh báo."],
      ["reports", "Báo cáo", "Tổng hợp chỉ số hoạt động theo dữ liệu demo."],
      ["audit", "Nhật ký thay đổi", "Lịch sử thao tác được ghi trên thiết bị hiện tại."],
      ["integrations", "Tích hợp", "Điểm kết nối, nguồn dữ liệu và phạm vi chia sẻ dự kiến."],
      ["settings", "Cấu hình", "Thiết lập hiển thị và phạm vi demo của Pet Care."]
    ],
    "pet-service": [
      ["overview", "Bảng điều phối", "Tổng quan lịch, năng lực phục vụ và việc cần xác nhận."],
      ["appointments", "Lịch hẹn", "Danh sách booking và trạng thái theo ngày."],
      ["booking-details", "Chi tiết lịch", "Thông tin khách, thú cưng, dịch vụ và ghi chú đặt chỗ."],
      ["check-in", "Tiếp nhận & check-in", "Checklist xác nhận lượt đến, tình trạng ban đầu và người giao."],
      ["staff-calendar", "Lịch nhân sự", "Phân ca nhân viên và theo dõi thời gian khả dụng."],
      ["service-catalog", "Danh mục dịch vụ", "Gói grooming, spa, tắm và lưu trú mẫu."],
      ["resources", "Tài nguyên cơ sở", "Theo dõi bàn, phòng, khu lưu trú và công suất."],
      ["handoff", "Bàn giao", "Checklist hoàn tất dịch vụ và xác nhận người nhận."],
      ["customers-pets", "Khách & thú cưng", "Tra cứu khách hàng, thú cưng và lịch sử dịch vụ."],
      ["pricing", "Bảng giá", "Giá mẫu, phụ phí và điều kiện cần xác nhận."],
      ["notifications", "Thông báo lịch", "Theo dõi nhắc lịch, đổi lịch và xác nhận gửi."],
      ["reports", "Báo cáo công suất", "Tổng hợp booking, thời gian chờ và sử dụng tài nguyên."],
      ["integrations", "Tích hợp", "Kết nối dự kiến với hồ sơ, thanh toán và cửa hàng."],
      ["audit", "Nhật ký thao tác", "Lịch sử thao tác demo trên thiết bị hiện tại."],
      ["settings", "Cấu hình cơ sở", "Thiết lập giờ hoạt động, ca và phạm vi demo."]
    ],
    "pet-health": [
      ["overview", "Tổng quan y tế", "Hàng đợi chuyên môn và các cổng an toàn cần theo dõi."],
      ["appointments", "Lịch khám", "Lịch tiếp nhận theo cơ sở và trạng thái khám."],
      ["patients", "Hồ sơ bệnh nhân", "Tra cứu thú cưng, chủ nuôi và tham chiếu clinic."],
      ["encounters", "Hồ sơ khám", "Theo dõi encounter, người phụ trách và trạng thái duyệt."],
      ["vaccinations", "Tiêm chủng", "Lịch tiêm mẫu, mũi tiếp theo và nhắc tái khám."],
      ["lab-orders", "Chỉ định xét nghiệm", "Theo dõi yêu cầu xét nghiệm và trạng thái mẫu."],
      ["results-review", "Duyệt kết quả", "Hàng đợi reviewer; kết quả không tự xác thực hoặc phát hành."],
      ["consent", "Consent & truy cập", "Phạm vi, mục đích và thời hạn chia sẻ dữ liệu."],
      ["clinic-capacity", "Năng lực phòng khám", "Theo dõi lịch bác sĩ, phòng và công suất mẫu."],
      ["staff", "Nhân sự chuyên môn", "Danh sách nhân sự và vai trò mô phỏng."],
      ["follow-ups", "Tái khám", "Theo dõi lịch nhắc và ca cần liên hệ lại."],
      ["reports", "Báo cáo vận hành", "Chỉ số tổng hợp, không đưa ra kết luận lâm sàng."],
      ["audit", "Nhật ký truy cập", "Theo dõi thao tác và các yêu cầu truy cập mẫu."],
      ["integrations", "Tích hợp y tế", "Điểm kết nối dự kiến; chia sẻ phải theo consent và quyền."],
      ["settings", "Cấu hình clinic", "Thiết lập cơ sở, vai trò và quy tắc demo."]
    ],
    "pet-commerce": [
      ["overview", "Bảng điều hành", "Tổng quan đơn hàng và các cổng xác minh."],
      ["catalog", "Danh mục sản phẩm", "Quản lý danh mục và trạng thái hiển thị mẫu."],
      ["products", "Sản phẩm & SKU", "Tra cứu sản phẩm, SKU và thông tin phân bổ."],
      ["orders", "Hàng đợi đơn hàng", "Theo dõi đơn theo trạng thái xử lý."],
      ["order-details", "Chi tiết đơn", "Thông tin dòng hàng và các cổng thực hiện."],
      ["payments", "Xác minh thanh toán", "Đối chiếu trạng thái mô phỏng; không lưu thông tin thanh toán."],
      ["inventory-allocation", "Phân bổ tồn", "Kiểm tra khả dụng trước khi xác nhận đơn."],
      ["fulfillment", "Đóng gói & giao", "Theo dõi đóng gói, bàn giao vận chuyển và giao hàng."],
      ["returns", "Đổi trả & hoàn tiền", "Tiếp nhận yêu cầu và luồng kiểm tra đổi trả."],
      ["customers", "Khách hàng", "Tra cứu hồ sơ khách và lịch sử đơn mẫu."],
      ["promotions", "Khuyến mãi", "Quản lý chương trình và điều kiện áp dụng demo."],
      ["analytics", "Phân tích bán hàng", "Tổng hợp hiệu suất catalog, đơn và kênh."],
      ["integrations", "Tích hợp kênh", "Kết nối dự kiến với cửa hàng, kho và thanh toán."],
      ["audit", "Nhật ký đơn hàng", "Lịch sử thao tác được ghi trong trình duyệt hiện tại."],
      ["settings", "Cấu hình cửa hàng", "Thiết lập kênh, ngưỡng và phạm vi demo."]
    ],
    "pet-business": [
      ["overview", "Control tower", "Tổng quan vận hành đa chi nhánh và các điểm cần kiểm soát."],
      ["branches", "Chi nhánh", "Theo dõi trạng thái, năng lực và chỉ số theo cơ sở."],
      ["inventory", "Tồn kho", "Tổng hợp tồn theo SKU, lô và chi nhánh."],
      ["procurement", "Đề nghị mua hàng", "Theo dõi yêu cầu mua và vòng phê duyệt."],
      ["suppliers", "Nhà cung cấp", "Hồ sơ nhà cung cấp và điều kiện giao dịch mẫu."],
      ["receiving", "Nhập hàng", "Checklist nhận hàng, đối chiếu chứng từ và số lượng."],
      ["transfers", "Điều chuyển", "Theo dõi yêu cầu chuyển hàng giữa các chi nhánh."],
      ["adjustments", "Điều chỉnh tồn", "Ghi nhận điều chỉnh giả lập với lý do và người duyệt."],
      ["approvals", "Phê duyệt", "Hàng đợi maker-checker và phân tách nhiệm vụ."],
      ["finance", "Tài chính", "Tổng hợp trạng thái kỳ và các hạng mục cần đối soát."],
      ["reconciliation", "Đối soát", "So sánh giao dịch, chứng từ và sai lệch mẫu."],
      ["reports", "Báo cáo chi nhánh", "Tổng hợp KPI theo kỳ và phạm vi cửa hàng."],
      ["audit", "Nhật ký kiểm soát", "Lịch sử thao tác demo theo thiết bị."],
      ["integrations", "Tích hợp", "Kết nối dự kiến với kho, bán hàng và kế toán."],
      ["settings", "Cấu hình tổ chức", "Thiết lập phạm vi chi nhánh và quy tắc demo."]
    ],
    "pet-community": [
      ["overview", "Trust & Safety", "Tổng quan nội dung, báo cáo và hàng đợi kiểm duyệt."],
      ["moderation", "Hàng đợi kiểm duyệt", "Danh sách nội dung chờ xử lý và người review."],
      ["posts", "Bài viết", "Tra cứu bài đăng, trạng thái và liên kết sự kiện."],
      ["reports", "Báo cáo vi phạm", "Tiếp nhận báo cáo và bằng chứng trong phạm vi demo."],
      ["member-safety", "An toàn thành viên", "Theo dõi biện pháp bảo vệ người báo cáo."],
      ["appeals", "Kháng nghị", "Luồng xét duyệt độc lập và kết quả kháng nghị."],
      ["policies", "Chính sách cộng đồng", "Danh mục quy tắc và phiên bản chính sách."],
      ["events", "Sự kiện", "Quản lý hoạt động cộng đồng và đăng ký mẫu."],
      ["announcements", "Thông báo", "Soạn, duyệt và theo dõi thông báo demo."],
      ["members", "Thành viên", "Quản lý trạng thái thành viên; dữ liệu định danh là giả."],
      ["signals", "Tín hiệu an toàn", "Tổng hợp dấu hiệu cần reviewer kiểm tra."],
      ["analytics", "Báo cáo cộng đồng", "Chỉ số tổng hợp về nội dung và thời gian xử lý."],
      ["integrations", "Tích hợp", "Kết nối dự kiến với case và danh tính tối thiểu."],
      ["audit", "Nhật ký kiểm duyệt", "Lịch sử thao tác và quyết định mẫu."],
      ["settings", "Cấu hình chính sách", "Thiết lập hàng đợi và phạm vi demo."]
    ],
    "pet-connect": [
      ["overview", "Bàn điều phối", "Tổng quan case hiện trường và ưu tiên an toàn."],
      ["cases", "Danh sách case", "Theo dõi case thất lạc, cứu hộ và trạng thái xác minh."],
      ["lost-pets", "Thú cưng thất lạc", "Quản lý thông tin nhận dạng và vùng tìm kiếm gần đúng."],
      ["rescue-tasks", "Nhiệm vụ cứu hộ", "Điều phối người phụ trách và checklist hiện trường."],
      ["partners", "Đối tác hiện trường", "Tra cứu tổ chức hỗ trợ và năng lực đã xác minh."],
      ["field-map", "Bản đồ khu vực", "Minh họa vùng hoạt động; không hiển thị vị trí chính xác."],
      ["evidence", "Bằng chứng", "Theo dõi tài liệu và trạng thái xác minh case."],
      ["safety-check", "Đánh giá an toàn", "Checklist an toàn trước khi điều phối hoặc bàn giao."],
      ["handoff", "Bàn giao", "Xác nhận người nhận, thời điểm và trạng thái case."],
      ["notifications", "Thông báo", "Theo dõi cập nhật case và trạng thái liên hệ demo."],
      ["resources", "Nguồn lực", "Theo dõi nhân sự, phương tiện và nguồn lực sẵn sàng."],
      ["analytics", "Báo cáo hiện trường", "Chỉ số tổng hợp về case và thời gian phản hồi."],
      ["audit", "Nhật ký case", "Lịch sử thay đổi trong trình duyệt hiện tại."],
      ["integrations", "Tích hợp", "Kết nối dự kiến với cộng đồng và hồ sơ tối thiểu."],
      ["settings", "Cấu hình khu vực", "Thiết lập phạm vi địa lý và chế độ riêng tư demo."]
    ],
    "pet-intelligence": [
      ["overview", "Data governance", "Tổng quan chất lượng nguồn, model gate và rủi ro."],
      ["datasets", "Danh mục dữ liệu", "Theo dõi owner, mục đích và trạng thái dataset."],
      ["lineage", "Data lineage", "Truy vết nguồn và biến đổi dữ liệu trong pipeline mẫu."],
      ["use-cases", "Use cases", "Quản lý mục tiêu, owner và rủi ro sử dụng."],
      ["model-registry", "Model registry", "Theo dõi phiên bản model và môi trường triển khai."],
      ["evaluations", "Đánh giá độc lập", "Kết quả kiểm định và tiêu chí go/no-go mẫu."],
      ["approvals", "Cổng phê duyệt", "Human approval, data owner và reviewer độc lập."],
      ["monitoring", "Giám sát", "Theo dõi freshness, chất lượng và ngưỡng cảnh báo."],
      ["drift", "Data & model drift", "Rà soát biến động theo cohort và nguồn."],
      ["incidents", "Sự cố", "Ghi nhận incident, tác động và quy trình phản ứng."],
      ["releases", "Phát hành", "Theo dõi phiên bản, phê duyệt và phạm vi rollout."],
      ["rollback", "Rollback", "Chuẩn bị phương án dừng và quay về quy trình thủ công."],
      ["audit", "Audit trail", "Lịch sử quyết định và dấu vết kiểm soát mẫu."],
      ["integrations", "Nguồn tích hợp", "Kết nối dữ liệu theo quyền, mục đích và lineage."],
      ["settings", "Cấu hình governance", "Thiết lập ngưỡng, vai trò và phạm vi demo."]
    ]
  };

  const playbook = (engine, workflow, algorithm, formula, inputs, guard) => ({
    engine, workflow, algorithm, formula, inputs, guard
  });
  const systemPlaybooks = {
    "pet-care": {
      owner: "Quản lý cơ sở điều phối; lễ tân cập nhật hồ sơ khách; nhân viên chăm sóc cập nhật task; hồ sơ sức khỏe chỉ chuyển bác sĩ/người được cấp quyền.",
      dataContract: "Mã khách và pet là khóa tham chiếu; tên hiển thị, species/breed, liên kết chủ nuôi, trạng thái, branchId, assignedTo, timestamps và provenance. Không dùng tên làm khóa.",
      integration: "Chủ sở hữu nguồn: Pet Care. Phát sự kiện tham chiếu sang Service (lịch), Health (chuyển ca theo consent), Commerce (order reference) và Business (số liệu tổng hợp). Mỗi consumer chỉ nhận trường tối thiểu; retry dùng eventId idempotent.",
      boundary: "Pet Care hiện có, nhưng bản demo không kết nối DB thật. Không ghi bệnh án/đơn hàng thật; quyền, consent, branch scope và audit phải được xác minh lại khi triển khai.",
      pages: {
        overview: playbook("priority", "Nạp snapshot → kiểm tra độ mới → gom việc theo thú cưng/chi nhánh → xếp hàng ưu tiên → giao owner → theo dõi SLA.", "Điểm ưu tiên điều hành tổng hợp mức khẩn cấp, tác động đến thú cưng và thời gian chờ; sắp giảm dần, không tự hoàn tất task.", "P = min(100, 35×urgency + 25×impact + 2×ageHours); tie-break theo hạn gần nhất rồi recordId.", "Mã việc, urgency 1–3, impact 1–3, thời gian chờ giờ, trạng thái và chi nhánh.", "Thiếu owner hoặc petId thì đưa vào hàng đợi lỗi; cảnh báo sức khỏe không thay cho đánh giá chuyên môn."),
        pets: playbook("quality", "Nhập mã định danh → chuẩn hóa thuộc tính → kiểm tra khóa chủ nuôi → đối chiếu trùng → áp dụng phạm vi truy cập → xuất hồ sơ tóm tắt.", "Chấm độ đầy đủ hồ sơ, không dùng fuzzy match để tự gộp thú cưng. Trùng nghi ngờ chỉ tạo case cho nhân viên xác minh.", "completeness = số trường bắt buộc hợp lệ / tổng trường bắt buộc × 100; duplicate candidate = exact normalized microchip OR exact ownerId + species + name.", "petId, species, displayName, ownerId, microchip (nếu có), branchId, consent và lastUpdatedAt.", "Không gộp bản ghi theo tên; microchip trùng hoặc chủ nuôi không khớp phải chặn sửa liên kết và ghi audit."),
        customers: playbook("quality", "Thu nhận thông tin liên hệ → chuẩn hóa → kiểm tra trùng theo khóa → xác nhận consent kênh → nối pet bằng relation ID → rà soát quyền xem.", "Đánh giá completeness và phát hiện trùng chính xác theo số/email đã chuẩn hóa; không tự hợp nhất khách khi thiếu bằng chứng.", "completion = validRequired / required × 100; duplicate = normalizedPhone match OR normalizedEmail match; name-only match chỉ là gợi ý.", "customerId, phone/email đã chuẩn hóa, contactConsent, petIds, branch scope và nguồn cập nhật.", "Ẩn liên hệ khi không có quyền; không đưa PII vào log analytics; mọi merge cần người duyệt và audit hai bản ghi."),
        "care-tasks": playbook("priority", "Tạo task từ checklist → gắn petId/owner/ca → tính hạn → xếp hàng → cập nhật trạng thái → nhắc/escalate nếu quá SLA.", "Tính priority score từ urgency, impact và age; trạng thái done chỉ đổi do người dùng xác nhận checklist.", "score = min(100, urgency×35 + impact×25 + min(ageHours, 12)×2); overdue = now > dueAt AND status != done.", "taskId, petId, checklistVersion, assignedTo, dueAt, urgency, impact và completion evidence.", "Không tự đánh dấu hoàn tất; task liên quan dấu hiệu lâm sàng chuyển bác sĩ, không hiển thị như chẩn đoán."),
        "health-records": playbook("consent", "Chọn pet → kiểm tra clinic/consent → xác minh mục đích → chỉ lấy trạng thái cần thiết → tạo yêu cầu chuyển ca → bác sĩ nhận và phản hồi.", "Quyết định cho xem theo tổ hợp purpose, tenant, scope và thời hạn; deny-by-default, chỉ chia sẻ trạng thái encounter tối thiểu.", "allow = activeConsent AND purposeAllowed AND tenantMatch AND requestedScope ⊆ grantedScope AND expiryAt > now.", "petId, clinicId, purposeCode, requestedScope, consentId/version, expiryAt và actorRole.", "Không render nội dung bệnh án ở Pet Care nếu thiếu consent; thu hồi quyền phải vô hiệu các token/cache theo thiết kế production."),
        appointments: playbook("schedule", "Nhập nhu cầu → tìm slot mở → kiểm tra thời lượng dịch vụ và buffer → xác nhận xung đột → giữ slot tạm → xác nhận bởi nhân viên.", "Tìm slot khả dụng theo khoảng nửa mở [start,end), chi nhánh, pet và tài nguyên; buffer tính vào chiếm chỗ.", "fit = start ≥ open AND end + buffer ≤ close AND overlap(existing, [start,end+buffer)) = false.", "branchId, serviceId, durationMin, bufferMin, preferredWindow, resourceId và booking status.", "Không tạo lịch nếu chưa xác nhận sức chứa hoặc dịch vụ cần ghi chú an toàn; hết slot gợi ý thời điểm khác."),
        services: playbook("quality", "Khai báo dịch vụ → kiểm tra thời lượng/giá → gắn tài nguyên yêu cầu → kiểm tra điều kiện pet → xuất bản phiên bản mới.", "Kiểm tra tính hợp lệ của catalog; giá áp dụng theo effectiveFrom đến effectiveTo, không sửa hồi tố lịch đã chốt.", "publishable = nameValid AND durationMin > 0 AND price ≥ 0 AND resourceRulesValid AND effectiveFrom < effectiveTo.", "serviceId, version, duration, price, resource requirements, species constraints và effective dates.", "Thay đổi dịch vụ đã đặt phải tạo version mới và yêu cầu báo/xác nhận lại; không âm thầm đổi giá booking."),
        sales: playbook("reconcile", "Đọc order reference → kiểm tra trạng thái nguồn → đối chiếu tổng tiền tham chiếu → gắn khách/pet đúng scope → cập nhật trạng thái read-only.", "So sánh số tiền/tổng số lượng hiển thị với snapshot đã ký; sai lệch ngoài tolerance thì cách ly, không phát lệnh thu.", "delta = localTotal − sourceTotal; matched = abs(delta) ≤ max(100 VND, sourceTotal×0.001) AND currencyMatch.", "orderId, sourceVersion, amount, currency, customerId, fulfillmentStatus và updatedAt.", "Không lưu PAN/token thanh toán; đơn refund/cancel không tự đổi về trạng thái bán thành công."),
        inventory: playbook("inventory", "Đọc SKU/lô → trừ giữ chỗ và hàng cách ly → tính available → kiểm tra hạn dùng → gắn cảnh báo → tạo đề xuất kiểm kê.", "Tính tồn khả dụng theo từng SKU-location-lot; FEFO chỉ đề xuất picking theo hạn, không ghi trừ kho.", "available = onHand − reserved − quarantined; reorderQty = max(0, minLevel − available); FEFO sort expiryAt ASC.", "skuId, locationId, lotId, onHand, reserved, quarantined, expiryAt và minLevel.", "Chặn số âm/đơn vị không tương thích; hàng hết hạn/cách ly không được tính available hoặc đề xuất bán."),
        suppliers: playbook("quality", "Nhập hồ sơ → xác minh mã số/đầu mối → kiểm tra trạng thái hợp tác → nối hợp đồng/điều khoản → cho phép tham chiếu mua hàng.", "Chấm completeness và trạng thái xác minh; không suy diễn nhà cung cấp an toàn chỉ từ hồ sơ đầy đủ.", "verified = requiredDocsValid AND status=active AND bankDetailsReviewedBy ≠ createdBy; completeness = validFields / requiredFields × 100.", "supplierId, taxRef, contacts, documents, termsVersion, status và reviewer identity.", "Thông tin ngân hàng chỉ vai trò finance được xem; thay đổi tài khoản cần xác minh ngoài kênh và maker-checker."),
        reminders: playbook("sla", "Sinh nhắc từ dueAt → loại trùng idempotency key → chọn kênh được consent → xếp lịch → ghi delivery attempt → retry có giới hạn.", "Phân loại due/overdue theo múi giờ cơ sở; retry theo backoff, nhưng chỉ kênh có consent và chưa opt-out.", "state = sent if acknowledged; else overdue if now > dueAt; retryDelay = min(2^attempt × 5min, 60min), maxAttempts=3.", "reminderId, entityId, dueAt/timezone, channel, consent, attemptCount và delivery receipt.", "Không gửi ngoài quiet hours; không retry khi opt-out/consent hết hạn; lỗi provider phải giữ trạng thái failed để xử lý."),
        reports: playbook("aggregate", "Chốt phạm vi ngày/chi nhánh → loại bản ghi test/trùng → chuẩn hóa timezone → tổng hợp KPI → kiểm tra mẫu số → xuất snapshot.", "Dùng distinct entity ID và denominator rõ ràng; phân biệt count theo event với count theo hồ sơ.", "completionRate = completedTasks / eligibleTasks × 100; overdueRate = overdueOpen / openTasks × 100; empty denominator => N/A.", "Date range, timezone, branch scope, event timestamps, status history và dedupe keys.", "Không hiển thị PII; số liệu thiếu nguồn gắn freshness label và không được cộng ngang các khoảng thời gian khác nhau."),
        audit: playbook("quality", "Ghi actor/action/subject/time → áp dụng retention → lọc theo quyền → đối chiếu requestId → xuất báo cáo đã che dữ liệu.", "Kiểm tra audit completeness; hash-chain chỉ minh họa tính liên tục, không tuyên bố là chữ ký/chống sửa production.", "validEvent = actor AND action AND subjectId AND timestamp AND requestId; chainHash = SHA-256(prevHash || canonicalEvent) (demo).", "ActorId, role, action, subjectId, timestamp, requestId, outcome và redacted diff.", "Không ghi secret/PII không cần thiết; lỗi ghi audit phải chặn thao tác nhạy cảm trong hệ thống thật."),
        integrations: playbook("lineage", "Đăng ký nguồn → khai báo owner/schema/purpose → kiểm tra field mapping → thử payload mẫu → duyệt quyền → bật consumer theo version.", "Đối chiếu required fields và schema version; sự kiện duplicate bỏ qua bằng eventId, version cũ đưa quarantine.", "accept = schemaSupported AND requiredFieldsPresent AND purposeAllowed AND eventVersion ≥ consumerVersion; idempotency key = eventId.", "Source/consumer IDs, schemaVersion, eventId, field mapping, purpose, consent, retry policy.", "Không đưa PII ngoài allowlist; lỗi schema không được chuyển thành success; retry phải có DLQ và owner."),
        settings: playbook("config", "Nhập cấu hình → validate type/range → chạy preview trên snapshot → yêu cầu owner duyệt → version hóa → áp dụng cho lượt mới.", "Dùng cấu hình bất biến theo version; tính khác biệt trước/sau và rollback về version trước nếu smoke check lỗi.", "valid = schemaValid AND rangesValid AND ownerApproved AND dryRunErrors=0; effectiveConfig = latest approved version.", "Timezone, business hours, thresholds, channels, role grants và configVersion.", "Không áp dụng cấu hình mới ngược cho booking đang thực hiện; secret phải quản lý ngoài trình duyệt.")
      }
    },
    "pet-service": {
      owner: "Lễ tân tiếp nhận booking; điều phối viên quản lý ca/tài nguyên; groomer cập nhật tiến độ; người giao/nhận xác nhận bàn giao.",
      dataContract: "Booking ID, pet/customer references, service/version, branch, interval, resource/staff assignments, checklist, consent, payment reference và status history; thời gian lưu UTC kèm timezone cơ sở.",
      integration: "Pet Service sở hữu booking và service execution. Đọc pet summary từ Care; phát booking/status reference về Care và Commerce; thanh toán chỉ qua provider token/reference, không lưu dữ liệu thẻ.",
      boundary: "Mọi slot, capacity, price và lịch nhân viên là giả lập. Không gửi SMS, không giữ chỗ thật, không dùng dữ liệu sức khỏe làm điều kiện tự động ngoài quy tắc được người có thẩm quyền duyệt.",
      pages: {
        overview: playbook("capacity", "Nạp booking theo cơ sở → loại canceled/no-show → cộng buffer → phân đoạn theo giờ/tài nguyên → hiển thị overload → điều phối thủ công.", "Tỷ lệ tải tính trên phút tài nguyên hữu dụng, không chia số booking cho số slot khi thời lượng khác nhau.", "utilization = bookedMinutesIncludingBuffer / availableMinutes × 100; >100% là xung đột, ≥90% cảnh báo.", "Branch, time window, resource minutes, duration, buffer, booking status.", "Không đề xuất nhận thêm lịch khi có xung đột; lưu trú dùng chỗ/đêm, không quy đổi thành phút grooming."),
        appointments: playbook("schedule", "Nhận yêu cầu → lọc dịch vụ/chi nhánh → tìm khoảng khả dụng → chặn overlap → tạo hold có TTL → xác nhận booking.", "Tìm slot sớm nhất đáp ứng duration+buffer trên đồng thời staff/resource; hold hết hạn tự giải phóng trong mô phỏng.", "candidate fits iff start≥open AND finish+buffer≤close AND no overlap(staff) AND no overlap(resource).", "Service version, pet size/species, branch, duration, buffer, staff/resource và preferred window.", "Xung đột cuối cùng luôn kiểm tra lại khi confirm; không coi slot đề xuất là đặt thành công."),
        "booking-details": playbook("quality", "Tải booking snapshot → kiểm tra đúng phiên bản service → xác minh owner/pet → so ghi chú/consent → tính trạng thái chuyển tiếp.", "Completeness gate ngăn check-in khi thiếu contact, pet identity, dịch vụ hoặc hướng dẫn bắt buộc.", "ready = customerVerified AND petLinked AND serviceVersionActive AND requiredNotesReviewed AND status in {held,confirmed}.", "Booking ID/version, customerId, petId, serviceId, notes, consent, assigned staff/resource.", "Ghi chú nhạy cảm chỉ nhóm phục vụ được xem; booking đã hoàn thành chỉ sửa bằng amendment có lý do."),
        "check-in": playbook("quality", "Quét booking → xác thực người giao → xác nhận pet/đặt dịch vụ → ghi tình trạng đầu vào → chụp checklist → chuyển in-service.", "Cổng check-in kiểm tra identity, booking window và checklist bắt buộc; không tự xác nhận đặc điểm sức khỏe.", "canCheckIn = bookingConfirmed AND identityMatched AND withinWindow(−30m,+15m) AND intakeChecklistComplete.", "Booking token, recipient relation, pet summary, timestamp, intake checklist, staff actor.", "Sai người nhận, pet không khớp hoặc ghi chú an toàn chưa đọc thì chuyển supervisor; không nhận bằng mã đơn đơn lẻ."),
        "staff-calendar": playbook("schedule", "Nạp ca và kỹ năng → trừ nghỉ/đào tạo → khóa lịch đã xác nhận → gán kỹ thuật viên theo năng lực → rà overlap.", "Ghép ca bằng earliest-fit có ràng buộc skill, giờ làm và max consecutive minutes; xếp tay vẫn cần validate.", "eligibleStaff = skillMatch AND shiftContains(interval) AND restSatisfied AND workload + duration ≤ maxLoad.", "Staff skills/certification, shift, breaks, service duration, leave và assigned bookings.", "Không phân việc chuyên môn ngoài chứng nhận; hủy/đổi ca phải tìm người thay và thông báo xác nhận."),
        "service-catalog": playbook("quality", "Soạn dịch vụ/version → khai báo thời lượng và tài nguyên → thêm điều kiện nhận → chạy kiểm tra giá → duyệt publish.", "Validate ràng buộc catalog và version; service đang gắn booking không bị mutate mà tạo version mới.", "valid = duration>0 AND price≥0 AND resourceDemandDefined AND speciesRuleDefined AND dateRangeNonOverlapping.", "Service/version, duration, resource type/count, price, species/size rules, cancellation terms.", "Thiếu resource demand hoặc thời gian lưu trú không có đơn vị đêm thì không publish; không áp giá hồi tố."),
        resources: playbook("capacity", "Khai báo tài nguyên → lịch mở/đóng → trừ maintenance → phân vùng theo loại → tính phút/chỗ còn lại → cảnh báo sắp đầy.", "Tính occupancy interval cho từng resource; lưu trú dùng capacity theo pet-night và không cho phép vượt sức chứa.", "remaining = capacity − activeAssignments; utilization = reservedUnits / capacity ×100; reject when remaining < demand.", "ResourceId, type, capacity, opening interval, maintenance, assignment, cleaning buffer.", "Giữ một khoảng vệ sinh giữa lượt; tài nguyên ngừng hoạt động không được tính available."),
        handoff: playbook("quality", "Hoàn tất checklist dịch vụ → ghi thời điểm/nhân viên → đối chiếu vật dụng và ghi chú → xác thực người nhận → đóng booking.", "Chỉ chuyển completed khi mọi checklist bắt buộc đã ký, charges đã xác nhận và người nhận hợp lệ.", "complete = requiredTasksDone AND finalConditionRecorded AND recipientVerified AND balanceStatus in {paid,approved-credit}.", "Booking/status version, task outcomes, final notes, add-ons, amount, recipient identity.", "Thiếu ảnh/đồng thuận nếu policy yêu cầu thì không đóng; không phát hành ghi chú y tế thay bác sĩ."),
        "customers-pets": playbook("consent", "Tìm customer/pet → xác minh quan hệ → lấy đúng field phục vụ → xác nhận consent liên hệ → hiển thị lịch sử dịch vụ giới hạn.", "Áp dụng least-privilege projection theo actor role và booking relation, không tải toàn bộ hồ sơ khách.", "visibleFields = requestedFields ∩ roleAllowlist ∩ purposeAllowlist; contactVisible requires activeContactConsent.", "Customer/pet IDs, relation, booking scope, contact consent, role và branch.", "Từ chối truy cập không có booking/purpose; không xuất địa chỉ/liên hệ ra bảng công khai."),
        pricing: playbook("reconcile", "Chọn service version → lấy base price → áp add-on đã đồng ý → áp thuế/discount theo thứ tự → hiển thị quote có hạn.", "Tính báo giá phiên bản hóa và làm tròn VND theo dòng; thay đổi sau check-in cần chấp thuận của khách.", "total = roundVND((base + approvedAddOns − eligibleDiscount) × (1 + taxRate)); discount không vượt base.", "Price version, quantity, add-on consent, discount eligibility, tax jurisdiction và quote expiry.", "Không tự thêm phụ phí; quote hết hạn phải tính lại; thuế/khuyến mãi giả lập cần đối chiếu chính sách thật."),
        notifications: playbook("sla", "Tạo event booking → kiểm tra consent/quiet hours → dedupe theo booking+template+event → enqueue → ghi receipt/retry.", "Gửi theo thời điểm cấu hình; retry exponential backoff tối đa 3 lần, hủy hàng đợi khi lịch đã đổi hoặc khách opt-out.", "send = consentActive AND notOptOut AND templateVersionApproved AND eventVersion=current; delay=min(5×2^attempt,60) minutes.", "Booking event/version, channel consent, timezone, template version, attempt and delivery receipt.", "Không gửi xác nhận lịch trước khi commit booking; event cũ bị bỏ qua bằng version check."),
        reports: playbook("aggregate", "Chọn ca/khoảng thời gian → quy đổi booking thành resource minutes → tính utilization/SLA/no-show → tách theo service và branch.", "Tỷ lệ công suất dùng tổng phút đã đặt / phút mở trừ bảo trì; báo cáo thiếu mẫu số là N/A.", "utilization = bookedMinutes / (openMinutes − maintenanceMinutes)×100; noShow = noShow / confirmed×100.", "Interval, resource schedule, service duration, booking terminal state, timezone, branch.", "Loại booking test/hold hết hạn; không cộng số chỗ lưu trú với phút bàn grooming."),
        integrations: playbook("lineage", "Đăng ký consumer → map booking event/schema → validate consent fields → gửi test event → kiểm tra idempotency → bật version.", "Event consumer dedupe eventId và reject phiên bản/schema sai; callback phải đối chiếu bookingVersion.", "apply iff validSchema AND sourceVersion > lastAppliedVersion AND eventId unseen AND purposeAllowed.", "Booking ID/reference, eventId, schema version, status, timestamps, pet reference scope.", "Không gửi health notes cho Commerce; lỗi downstream vào DLQ và hiển thị owner, không ack giả."),
        audit: playbook("quality", "Ghi before/after status, actor, resource assignment → lọc theo branch → dựng timeline → xuất dữ liệu đã che.", "Kiểm tra mọi status change có transition hợp lệ và actor; audit không phải nguồn để suy ra lịch đã hoàn tất nếu thiếu event.", "validTransition = target ∈ allowedTransitions[current] AND actorRole permits action AND requestId present.", "BookingId/version, actor, action, old/new state, reason, resource/staff and requestId.", "Không xóa lịch sử; sửa sai bằng event bù có tham chiếu bản gốc."),
        settings: playbook("config", "Thiết lập giờ mở/quiet hours/buffer → validate timezone → chạy fit test → owner duyệt → tạo config version.", "Config mới chỉ áp cho booking chưa xác nhận; chạy test kiểm tra lịch qua đêm và ngày đổi giờ.", "valid = open<close AND buffer≥0 AND timezoneValid AND simulatedConflicts=0 AND ownerApproved.", "Timezone, business hours, service buffers, capacity, cancellation window and notification settings.", "Không đổi timezone giữa booking; service lưu trú phải hỗ trợ interval qua ngày và ngày lễ.")
      }
    },
    "pet-health": {
      owner: "Bác sĩ thú y chịu trách nhiệm nội dung lâm sàng; lễ tân chỉ tiếp nhận; kỹ thuật viên nhập kết quả theo phân công; reviewer độc lập kiểm tra trước phát hành.",
      dataContract: "Patient/owner reference, clinic tenant, encounter ID/version, consent scope, authoredBy, signedAt, specimen/order/result references và audit; timezone và đơn vị đo phải có metadata.",
      integration: "Clinic là nguồn chuẩn của encounter/result. Chỉ phát trạng thái tối thiểu qua Care/Intelligence khi consent và mục đích hợp lệ; mọi kết quả cần human signature.",
      boundary: "Không đưa ra chẩn đoán, liều thuốc, khuyến nghị điều trị hay phát hành kết quả tự động. Dữ liệu demo không phải hồ sơ bệnh án và mọi cổng lâm sàng cần người có thẩm quyền.",
      pages: {
        overview: playbook("priority", "Kiểm tra clinic tenant → gom encounter/lab chờ → áp mức ưu tiên và SLA → phân bác sĩ/reviewer → chỉ hiện dữ liệu tối thiểu.", "Xếp hàng theo nguy cơ vận hành do người dùng gán và thời gian chờ; không suy luận bệnh từ triệu chứng.", "queueScore = urgencyLabel×40 + overdueHours×3 + waitingDependency×10; clinical decision remains human.", "Clinic, encounter status, assigned clinician, review SLA, consent state và timestamps.", "Thiếu consent/tenant hoặc có dấu hiệu khẩn do người dùng đánh dấu thì escalation; điểm số không phải triage y tế."),
        appointments: playbook("schedule", "Nhận yêu cầu → xác thực patient/clinic → chọn appointment type → ghép practitioner/room → kiểm tra slot → xác nhận.", "Tìm giao của lịch nhân sự và phòng theo duration, buffer vệ sinh và loại lượt; không ghép nếu practitioner không đủ thẩm quyền.", "fit = practitionerAvailable ∩ roomAvailable ∩ clinicOpen ∩ requiredCredential AND no overlap.", "PatientId, clinicId, visit type, duration, clinician credential, room, consent and timezone.", "Slot chỉ đề xuất; ca khẩn cần quy trình riêng do cơ sở xác định, không tự phân loại qua thuật toán."),
        patients: playbook("consent", "Tìm patient bằng ID → xác thực chủ/đại diện → xác định clinic tenant → kiểm tra consent → hiển thị projection được phép.", "Áp dụng scope theo clinic, purpose, field và hạn; không tự đồng nhất bệnh nhân bằng tên/giống loài.", "allow = tenantMatch AND verifiedRelation AND consentActive AND requestedScope⊆grantedScope AND purposeMatch.", "PatientId, owner relation, clinicId, consent ID/version, purpose, expiry and role.", "Không tiết lộ hồ sơ cross-clinic khi chưa có grant; yêu cầu sửa định danh chuyển data steward."),
        encounters: playbook("quality", "Mở encounter → xác thực người ghi → ghi structured fields → kiểm tra completeness → bác sĩ review/sign → khóa phiên bản.", "Tách draft/in-review/signed; chỉ sign khi mandatory sections đủ và signatory có credential đang hiệu lực.", "signable = requiredSectionsValid AND authorCredentialValid AND patientClinicMatch AND consent/purposeValid.", "EncounterId/version, patient, observations, assessment authored by clinician, plan, signature and timestamp.", "Không tự sinh assessment; sửa hồ sơ signed tạo amendment giữ bản cũ và lý do."),
        vaccinations: playbook("schedule", "Đọc lịch tiêm đã được bác sĩ xác nhận → xác thực sản phẩm/lô → lên nhắc → ghi nhận bởi người có quyền → tính ngày hẹn kế tiếp theo protocol.", "Tính dueAt từ protocol/version và mũi đã ký; algorithm chỉ nhắc, không tự xác định phù hợp tiêm.", "nextDue = clinicianApprovedProtocol(patient, product, doseDate); reminder only if consentActive AND status != administered.", "Patient, protocol version, vaccine product/lot, administeredAt, clinician signature, next due date.", "Không gợi ý liều/contraindication; ngày lịch phải được bác sĩ phê duyệt và đối chiếu nhãn sản phẩm."),
        "lab-orders": playbook("quality", "Bác sĩ tạo chỉ định → xác thực encounter/consent → kỹ thuật viên nhận mẫu → gắn specimen ID → cập nhật chain-of-custody.", "Cổng specimen yêu cầu ID duy nhất, loại mẫu, thời điểm, người lấy/nhận và trạng thái bảo quản theo cấu hình clinic.", "validOrder = signedByClinician AND patientMatch AND specimenIdUnique AND collectionMetadataComplete.", "OrderId, encounterId, test catalog version, specimen ID/type, collectedAt, collector and handling state.", "Không nhận mẫu thiếu định danh/metadata; demo không xác định xét nghiệm cần làm hoặc diễn giải kết quả."),
        "results-review": playbook("approval", "Nhận result draft → kiểm tra unit/reference metadata → đối chiếu mẫu/order/patient → reviewer xác thực → bác sĩ ký/phát hành.", "Maker-checker tách người nhập và người xác nhận; mọi kết quả ngoài reference range chỉ gắn cờ để con người đánh giá.", "release = resultComplete AND specimenMatched AND reviewerId ≠ authorId AND clinicianSignatureValid.", "Result version, units, reference range/version, specimen, author, reviewer, signature and timestamps.", "Không chuyển cờ máy thành chẩn đoán; thiếu đơn vị/phạm vi tham chiếu hoặc lệch mẫu thì giữ quarantine."),
        consent: playbook("consent", "Chọn chủ thể/clinic → ghi purpose/fields/recipient → xác nhận người đại diện → đặt expiry → cấp grant → thu hồi theo request.", "Grant chỉ cho scope nhỏ nhất, recipient cụ thể, purpose và thời hạn; mỗi lần truy cập kiểm tra lại trạng thái thu hồi.", "allow = grant.active AND recipientMatch AND purposeMatch AND field⊆scope AND now<expiryAt AND clinicMatch.", "Subject/representative ID, clinic, recipient, purpose, fields, validFrom/To, revocationAt.", "Không dùng consent chung không giới hạn; thu hồi ngay phải chặn cấp token mới và ghi audit có người thực hiện."),
        "clinic-capacity": playbook("capacity", "Nạp lịch clinic → loại đóng cửa/bảo trì → tính phút bác sĩ/phòng → dành buffer khử khuẩn → báo quá tải cho điều phối.", "Tính công suất riêng theo resource class; lượt có thời lượng khác nhau dùng phút, không đếm số appointment.", "utilization = reservedMinutes / (staffedMinutes−breaks−maintenance)×100; overbook if reserved > available.", "Clinic hours, clinician roster/credential, room, visit type duration, cleanup buffer and bookings.", "Không tự thêm slot; không giảm buffer an toàn nếu chưa có clinic owner phê duyệt."),
        staff: playbook("quality", "Quản lý credential/role → kiểm tra hạn/chứng chỉ → gắn clinic scope → phân quyền theo nhiệm vụ → rà soát định kỳ.", "Tính eligibility theo credential còn hạn, role, clinic assignment và separation of duties; không dựa chức danh nhập tay đơn độc.", "eligible = active AND credentialValidAt(now) AND clinicAssigned AND roleAllows(action) AND trainingCurrent.", "StaffId, role, credentials, expiry, clinic scope, training and reviewer.", "Credential hết hạn tự chặn thao tác nhạy cảm; thay đổi quyền cần phê duyệt và nhật ký."),
        "follow-ups": playbook("sla", "Tạo follow-up từ encounter đã ký → bác sĩ đặt due date → kiểm tra consent kênh → xếp nhắc → ghi kết quả liên hệ.", "Theo dõi due/overdue mà không suy luận kết quả sức khỏe; escalations theo policy clinic và consent.", "overdue = now>dueAt AND followUpStatus=open; remind = consentActive AND notOptOut AND dueAt within configuredWindow.", "Encounter reference, clinician-defined dueAt, channel consent, contact attempt and outcome.", "Không đặt lịch điều trị/nhắc liều tự động; nội dung nhạy cảm gửi qua kênh đã được clinic phê duyệt."),
        reports: playbook("aggregate", "Chọn clinic/time range → loại encounter draft/trùng → tính throughput/wait/review SLA → tách clinician → ẩn cohort nhỏ.", "Mỗi KPI có denominator và status inclusion rõ; cell nhỏ hơn ngưỡng k-anonymity bị ẩn.", "reviewSLA = signedWithinTarget / eligibleReviewed ×100; suppress if cohortSize<k; denominator=0 => N/A.", "Clinic scope, encounter timestamps/status, visit category, reviewer events and de-identified cohort.", "Không báo cáo chẩn đoán cá nhân cho quản trị; snapshot có freshness và suppression metadata."),
        audit: playbook("quality", "Ghi mọi read/write nhạy cảm → gắn purpose/clinic/request ID → phát hiện truy cập bất thường → reviewer xác minh → đóng case.", "Phát hiện truy cập ngoài phạm vi bằng policy check; audit bất thường tạo alert nhưng không tự kết luận sai phạm.", "flag = !roleAllows OR !purposeMatch OR !tenantMatch OR accessRate>configuredThreshold; reviewer decides disposition.", "Actor, patient/encounter reference, purpose, action, tenant, timestamp, outcome and requestId.", "Audit không chứa nội dung lâm sàng; log failure phải chặn thao tác release và báo clinic admin."),
        integrations: playbook("lineage", "Đăng ký clinic endpoint → xác minh tenant/cert → map FHIR-like resources → test consent filter → contract test → duyệt go-live.", "Chỉ nhận resource theo profile/version và consent; correlation ID nối order-result-encounter nhưng không ghép theo tên.", "accept = authenticatedTenant AND schemaProfileValid AND consentAllowed AND resourceVersion>cursor AND idempotencyPass.", "Tenant, resource ID/version, consent token, purpose, provenance, correlation and timestamps.", "Không gửi full medical record cho Care/analytics; lỗi signature/schema đưa quarantine."),
        settings: playbook("config", "Clinic owner cấu hình role/protocol/retention → kiểm tra xung đột → dry-run trên fixture → reviewer độc lập ký → version hiệu lực.", "Cấu hình lâm sàng không thể publish nếu thiếu owner, reviewer, version hoặc test case; rollback không xóa audit.", "publish = ownerApproved AND independentReviewer AND testPass AND effectiveVersionMonotonic.", "Clinic, roles, protocol/version references, retention, SLA and config effective range.", "Không dùng demo để cấu hình phác đồ hoặc liều; production cần clinical governance và kiểm định pháp lý.")
      }
    },
    "pet-commerce": {
      owner: "Commerce operations quản lý catalog/order; payment operations xác minh trạng thái; warehouse thực hiện picking/packing; finance duyệt refund và đối soát.",
      dataContract: "OrderId/version, lineId/SKU, quantity, price snapshot, currency, payment provider reference, stock reservation, shipment/RMA and state timestamps; không lưu thông tin thẻ.",
      integration: "Commerce sở hữu order lifecycle. Catalog/availability đọc Business inventory; payment và carrier dùng provider adapters; Care chỉ nhận order reference cần thiết, không nhận payment secrets.",
      boundary: "Giá, payment, stock, shipment và refund là dữ liệu giả. Không gọi cổng thanh toán/vận chuyển, không tạo giao dịch tài chính.",
      pages: {
        overview: playbook("priority", "Nạp order event → dedupe → phân nhóm payment/stock/fulfillment gate → tính tuổi hàng đợi → xếp owner và SLA.", "Ưu tiên đơn bị chặn ở cổng thanh toán/tồn trước đơn mới; tie-break theo createdAt và SLA gần nhất.", "score = gateSeverity×40 + min(ageHours,24)×2 + promisedDeadlineRisk×20; do not auto-capture or cancel.", "Order state/version, payment verification, stock reservation, promiseAt, exception code.", "Order version cũ bị bỏ qua; payment pending không đồng nghĩa thất bại hoặc được phép đóng gói."),
        catalog: playbook("quality", "Soạn category/product → khai báo thuộc tính bắt buộc → kiểm tra ảnh/giá/taxonomy → duyệt content → publish version.", "Catalog completeness và consistency validation trước publish; SKU không active thì không được nhận order.", "publishable = requiredAttributesValid AND price≥0 AND categoryActive AND contentApproved AND effectiveWindowValid.", "Category/product ID/version, SKU, attributes, price, tax class, media rights and active dates.", "Không hiển thị claim sức khỏe chưa được duyệt; thay đổi giá tạo version và không sửa order snapshot cũ."),
        products: playbook("quality", "Tạo SKU → xác minh barcode/unit/pack size → nối warehouse item → kiểm tra duplicate → kích hoạt bán theo channel.", "Chuẩn hóa barcode và unit; phát hiện xung đột SKU/barcode exact match, không tự gộp product.", "sellable = skuUnique AND barcodeUnique AND unitConversionValid AND priceVersionActive AND inventoryPolicyPresent.", "ProductId, SKU, GTIN/barcode, base unit, pack conversion, channel listing and stock policy.", "Không cho fulfillment nếu conversion thiếu; mỗi listing giữ source version để audit giá/thuế."),
        orders: playbook("priority", "Nhận order → schema/idempotency check → fraud/payment pending gate → reserve stock → tính SLA → vào queue fulfillment.", "State machine chỉ cho transition được phép; ưu tiên exception thay vì sắp xếp theo giá trị đơn.", "next = transition[current,event] if version=current AND guardsPass; else quarantine; priority by gate severity then SLA.", "Order ID/event ID/version, lines, payment state, stock state, risk review and delivery promise.", "Không double-reserve khi webhook lặp; đơn hủy phải release reservation idempotently."),
        "order-details": playbook("quality", "Tải immutable order snapshot → kiểm tra từng line/tax/discount → đối chiếu payment reference → hiển thị fulfillment/RMA timeline.", "Tổng line phải khớp snapshot; thay đổi sau submit là amendment riêng, không ghi đè đơn gốc.", "expectedTotal = Σ(qty×unitPrice−lineDiscount)+tax+shipping−orderDiscount; compare snapshotTotal within currency minor unit.", "Order/version, line snapshots, tax/discount, shipping, payment reference and event history.", "Thiếu currency hoặc mismatch vượt 1 minor unit thì chặn capture/fulfillment và mở reconciliation."),
        payments: playbook("reconcile", "Nhận provider event → verify signature ở backend (demo chỉ cờ mẫu) → dedupe transaction ID → đối chiếu amount/currency/order → review.", "Ba chiều match order reference, amount và currency; capture/refund không được tự suy ra từ redirect trình duyệt.", "matched = providerTxnIdUnique AND orderRefMatch AND abs(providerAmount−orderAmount)≤minorUnit AND currencyMatch.", "Provider transaction reference, order, amount, currency, event time and signature-verification result.", "Không thu thẻ/token; webhook không hợp lệ quarantine; refund cần approver khác maker."),
        "inventory-allocation": playbook("inventory", "Tính available theo location/lot → áp reservation atomic → chọn fulfillment node → chặn oversell → phát allocation version.", "Reserve bằng compare-and-set theo inventory version; pick theo FEFO nếu SKU/lô phù hợp và không cách ly.", "available=onHand−reserved−quarantined; allocate=min(requested, available); commit only if inventoryVersion unchanged.", "SKU, location, onHand, reserved, quarantine, lot expiry, requested quantity and inventory version.", "Không cho tồn âm; retry reservation idempotent; nếu hết hàng tạo backorder cần khách xác nhận."),
        fulfillment: playbook("schedule", "Đợi payment gate → chốt allocation → tạo pick wave → scan line/lot → pack verify → tạo carrier label → xác nhận handoff.", "Shipment chỉ tạo sau đầy đủ line allocation; scan pack phải khớp SKU/qty và cân nặng trong tolerance.", "readyToShip = paymentCleared AND allLinesAllocated AND packScanMatches AND addressValidated AND carrierAvailable.", "Order/version, pick location, SKU/lot/qty, package weight, address token and carrier reference.", "Thiếu một line thì partial shipment chỉ theo policy; không đánh dấu delivered từ trạng thái label-created."),
        returns: playbook("risk", "Tra order/line → kiểm tra return window/eligibility → ghi condition/evidence → tính refund ceiling → người duyệt quyết định → đối soát.", "Refund tối đa theo giá line còn lại sau discount; shipping/tax theo rule và trạng thái hàng được reviewer xác minh.", "eligible = delivered AND now≤returnDeadline AND qtyReturned≤qtyNet; refund≤lineNet+eligibleTax; no duplicate RMA.", "Order/line ID, deliveredAt, reason, condition, evidence reference, quantity and payment reference.", "Không tự duyệt hoàn tiền; hàng có nguy cơ an toàn được cách ly, không đưa lại tồn bán."),
        customers: playbook("consent", "Tìm theo customer key → xác thực session/role → lọc order scope → che thông tin giao hàng → kiểm tra yêu cầu xóa/opt-out.", "Projection chỉ trả field cần hỗ trợ đơn; phân tách account profile khỏi token thanh toán và giữ cờ privacy request.", "visible = roleAllows AND orderOwnershipVerified; export fields = allowlist − paymentSecrets − unnecessaryPII.", "CustomerId, order references, contact preferences, privacy flags and consent version.", "Không dùng lịch sử sức khỏe để target marketing; xóa/ẩn theo retention/legal hold policy."),
        promotions: playbook("reconcile", "Xác định eligibility → kiểm tra thời gian/kênh/SKU → áp discount order theo thứ tự priority → tính stacking → chốt snapshot.", "Áp promotion có deterministic precedence và chống cộng dồn vượt ceiling; kết quả gắn promotion version.", "discount = min(cap, eligibleBase×rate); stacking only if compatibleGroups disjoint AND totalDiscount≤maxDiscount.", "Promotion version/window, channel, customer segment consent, SKU exclusions, caps and order lines.", "Không đổi promotion đã chốt; race condition coupon dùng atomic redemption counter và idempotency key."),
        analytics: playbook("aggregate", "Chọn cửa sổ thời gian → dedupe order → chọn cohort theo createdAt/deliveredAt → loại test/refund theo định nghĩa → tính KPI.", "GMV/paid revenue tách rõ; refund trừ theo timestamp refund, không cộng đơn chưa capture vào doanh thu.", "conversion=paidOrders/eligibleSessions; netSales=settledSales−settledRefunds; denominator=0 => N/A.", "Session/order events, payment settlement, refund, channel, timestamps and attribution window.", "Không dùng attribution để khẳng định quan hệ nhân quả; freshness và definition version hiển thị cùng metric."),
        integrations: playbook("lineage", "Đăng ký channel/provider → quản lý secret phía server → map webhook → validate signature/idempotency → contract test → bật adapter.", "Webhook event phải có signature pass, event ID chưa xử lý và version hợp lệ; ack sau durable write.", "accept = signatureValid AND eventIdUnseen AND schemaValid AND orderRefExists; ack only after durable commit.", "Provider/channel ID, eventId, signature status, schema version, order ref and correlation ID.", "Secret không bao giờ ở localStorage/front-end; retry có backoff và DLQ."),
        audit: playbook("quality", "Ghi transition/payment/RMA changes → che dữ liệu thanh toán/địa chỉ → lọc theo order → dựng immutable timeline.", "Đảm bảo transition có actor/request/provider event và causal reference; phân biệt system event với human decision.", "valid = stateTransitionAllowed AND sourceEventUnique AND actorOrProviderPresent AND timestampMonotonic.", "Order/version, actor/service, old/new state, source event, decision reason and redacted values.", "Không ghi token/PAN; xóa sự kiện không cho phép, sửa sai bằng compensating event."),
        settings: playbook("config", "Cấu hình kênh/currency/tax/threshold → validate dependency → replay fixtures → finance/ops approve → version và activate.", "Config activation chỉ khi currency/tax/carrier dependencies có hiệu lực; rollback không làm thay đổi order snapshots.", "valid = currencySupported AND taxRuleVersion AND providerReady AND testsPass AND approversDistinct.", "Channel, currencies, tax rules, payment/fulfillment toggles, caps and config version.", "Không dùng feature flag để bỏ qua payment/stock gates; secrets lưu trong backend vault.")
      }
    },
    "pet-business": {
      owner: "Branch operator tạo yêu cầu; inventory/procurement xác minh; finance kiểm soát kỳ; approver độc lập duyệt; central operations quản lý phạm vi chuỗi.",
      dataContract: "Tenant/branch, SKU/location/lot, quantity/unit, cost/currency, document references, maker/checker, effective period, ledger event and reconciliation status.",
      integration: "Business là nguồn chuẩn cho branch inventory/procurement. Commerce nhận availability; Care đọc tồn tại cửa hàng; Finance/ERP nhận journal draft sau phê duyệt, không đẩy bút toán trực tiếp từ demo.",
      boundary: "Không cập nhật tồn, tiền, chứng từ hoặc kỳ kế toán thật. Maker-checker, branch scope, period lock và audit là cổng bắt buộc khi triển khai.",
      pages: {
        overview: playbook("priority", "Gom exception từng branch → chuẩn hóa kỳ/đơn vị → xếp lệch tiền, thiếu hàng, quá SLA → giao owner → theo dõi checker.", "Tổng điểm rủi ro theo độ lệch, giá trị phơi nhiễm và thời gian mở; tie-break theo kỳ gần khóa.", "risk = min(100, severity×30 + exposureBand×25 + ageDays×2 + periodCloseRisk×20).", "Branch, exception type, amount/qty delta, age, owner, period lock and approval state.", "Không cho ghi sổ từ bảng điều hành; period locked chỉ được correction entry kỳ kế tiếp."),
        branches: playbook("aggregate", "Chọn tenant/branch scope → kiểm tra quyền → ghép KPI theo kỳ → so với target đã version → đánh dấu outlier cần xác minh.", "Chuẩn hóa currency/timezone; so cùng kỳ/cùng cửa sổ hoạt động, không xếp hạng branch thiếu dữ liệu.", "variancePct=(actual−target)/max(abs(target),epsilon)×100; suppress comparison if coverage<configuredMinimum.", "Branch IDs, period, sales/stock/service aggregates, target version and data freshness.", "Người dùng chỉ xem branch được cấp quyền; KPI thiếu coverage gắn N/A thay vì zero."),
        inventory: playbook("inventory", "Nạp ledger movement → replay theo SKU/location/lot → đối chiếu snapshot → tính khả dụng và aging → tạo exception.", "Balance từ movement append-only; available trừ reservations/quarantine; kiểm tra unit conversion trước cộng.", "balance=opening+receipts+transfersIn−sales−transfersOut−adjustments; available=balance−reserved−quarantined.", "SKU, location, lot, movement ID/type/qty/unit, reservations and count snapshot.", "Không sửa balance trực tiếp; movement đảo phải tham chiếu movement gốc, lot hết hạn/cách ly loại khỏi bán."),
        procurement: playbook("approval", "Tính nhu cầu từ min/max/lead time → tạo requisition → kiểm tra ngân sách/vendor → tách maker → duyệt → phát PO draft.", "Reorder qty bù đến target stock và nhu cầu lead-time; phê duyệt theo ngưỡng giá trị/version, không tự gửi PO.", "suggestedQty=max(0,targetStock−available−onOrder); approvalRequired=amount≥threshold OR exceptionPresent.", "SKU, demand window, available/onOrder, MOQ, lead time, unit cost, budget and maker.", "Không cộng đơn đang mở hai lần; thiếu quote/budget hoặc approver trùng maker thì block."),
        suppliers: playbook("quality", "Xác thực vendor docs → kiểm tra terms/effective date → nối tax/bank info quyền hạn chế → đánh giá trạng thái → phê duyệt vendor.", "Tách completeness khỏi risk review; chi tiết tài khoản cần xác minh độc lập và version hóa.", "eligibleForPO = docsCurrent AND taxStatusVerified AND termsActive AND bankChangeApprovedBy≠maker.", "Supplier ID, tax reference, contract/terms version, contacts, bank-change request and reviewers.", "Không hiển thị bank info cho role kho; vendor bị suspended không xuất hiện trong requisition."),
        receiving: playbook("reconcile", "Mở PO → nhận scan chứng từ → nhập received/accepted/rejected → so PO và invoice → kiểm tra lô → tạo receipt draft.", "3-way match PO, receipt và invoice; tolerance theo từng unit/currency được cấu hình; variance cần checker.", "qtyDelta=received−ordered; priceDelta=invoiceUnit−POUnit; pass iff |delta|≤configuredTolerance on both.", "PO line, received qty/unit, rejected qty, invoice qty/price, lot/expiry and document refs.", "Không tự chấp nhận hàng sai lô/hết hạn; thiếu invoice hoặc unit mapping thì quarantine receipt."),
        transfers: playbook("schedule", "Tạo transfer request → kiểm tra nguồn available → chọn tuyến/ETA → giữ lượng tạm → duyệt → dispatch/receive hai bước.", "Chuyển hàng ghi hai movement liên kết; in-transit không tính available ở cả hai kho.", "dispatchQty≤sourceAvailable; destinationBalance changes only on receipt; inTransit=dispatched−received−lost.", "Transfer ID, source/destination, SKU/lot/qty, carrier, dispatch/receipt times and approvers.", "Không cho source=destination; partial receipt giữ phần chênh lệch ở transit exception."),
        adjustments: playbook("approval", "Nhập count và reason code → so ledger/cycle count → lượng hóa delta → yêu cầu chứng cứ → maker gửi → checker duyệt.", "Adjustment tạo movement bù, không sửa lịch sử; materiality threshold quyết định cấp duyệt cao hơn.", "delta=counted−book; postAllowed=reasonValid AND evidencePresent AND checker≠maker AND periodOpen.", "SKU/lot/location, book qty, counted qty, reason, evidence, period and actor identities.", "Không post nếu kỳ khóa/thiếu reason; chênh lệch lớn cần recount độc lập."),
        approvals: playbook("approval", "Lấy đề nghị → xác minh maker/request version → tính approval matrix → gán checker độc lập → approve/reject có lý do.", "Ma trận duyệt dựa amount, branch, category và risk; maker không thể checker; version đổi làm mất hiệu lực duyệt.", "approveAllowed = makerId≠checkerId AND checkerRole covers threshold AND requestVersion=current AND periodOpen.", "RequestId/version, amount, branch, category, maker, checker, policy version and decision reason.", "Bản ghi bị sửa sau phê duyệt phải re-approve; không giả lập quyền bằng tên nhập tự do."),
        finance: playbook("reconcile", "Đóng snapshot kỳ → nhập settlements → match reference/amount/date → phân loại unmatched → finance review → đề xuất journal.", "Reconcile theo khóa giao dịch exact trước, sau đó amount/date candidate chỉ gợi ý; journal chỉ tạo sau checker.", "matched if referenceExact AND currencySame AND abs(amountDelta)≤minorUnit; candidate by amount+date is not auto-match.", "Period, ledger account, settlement ref, amount/currency, bank ref, fee and lock state.", "Không ghi bút toán thật; period lock cấm backdate, unmatched giữ suspense và cần finance owner."),
        reconciliation: playbook("reconcile", "Import hai nguồn → chuẩn hóa timezone/currency → exact match transaction refs → đánh dấu one-to-many → tính residual → xử lý exception.", "Ghép exact ID ưu tiên; fuzzy amount/date chỉ vào review queue, đảm bảo không tái sử dụng cùng một giao dịch.", "residual=Σleft−Σright; pass if abs(residual)≤tolerance AND each source row matched at most once.", "Source row IDs, transaction refs, amount, currency, dates, fees and matching policy version.", "Không tự xóa residual/fee; duplicate source rows bị quarantine trước match."),
        reports: playbook("aggregate", "Chốt branch/period → lấy ledger snapshot và status → kiểm coverage → tính KPI có lineage → so kỳ trước → phát hành internal report.", "Tổng hợp từ posting/approved events, tách accrual vs cash và ghi rõ denominator/FX rate/version.", "variance=actual−budget; inventoryTurns=COGS/avgInventory; unavailable if avgInventory≤0 or coverage below threshold.", "Period, branch, approved ledger, budget version, inventory snapshot, FX source and freshness.", "Chỉ role được cấp quyền thấy finance values; export gắn timestamp/source/definition version."),
        audit: playbook("quality", "Ghi actor/branch/request/approval chain → tìm request cùng version → kiểm maker-checker → lọc theo retention → lập evidence package.", "Audit completeness kiểm quan hệ request→decision→movement; dấu thời gian không đơn điệu tạo exception, không tự sửa.", "traceable=allRequiredEventsPresent AND decisionVersion=requestVersion AND maker≠checker AND requestIdConnected.", "Actor, branch, request/version, decision, movement ID, period, source ref and outcome.", "Không xóa history; audit export che PII/financial account secrets theo role."),
        integrations: playbook("lineage", "Map event/account/branch → validate unit/currency/master data → replay fixture → kiểm duplicate → owner và finance ký contract.", "Outbox + idempotency event ID; account mapping không tồn tại thì fail closed, không đẩy số liệu vào tài khoản mặc định.", "accept=branchKnown AND accountMapped AND currencySupported AND eventVersionNew AND approverGatePassed.", "Branch, SKU/account references, event ID, ledger period, amount/unit and schema version.", "ERP interface dùng credential backend, retry có DLQ; demo chỉ hiển thị mapping và không post."),
        settings: playbook("config", "Cấu hình branch scope, tolerance, approval matrix, period calendar → validate segregation → simulate → dual approve → version.", "Ma trận phải không có khoảng ngưỡng mơ hồ và có fallback deny; cấu hình chỉ hiệu lực từ period future.", "valid=thresholdRangesNonOverlapping AND checkerRolesDistinct AND timezoneValid AND testFixturesPass.", "Thresholds, branch tree, tolerance, period close, role matrix and effective date.", "Không giảm ngưỡng audit/tách nhiệm vụ bằng config self-service; phải có independent approver.")
      }
    },
    "pet-community": {
      owner: "Trust & Safety moderator tiếp nhận; policy specialist phân loại; reviewer độc lập xử lý appeal; community manager quản lý sự kiện/thông báo.",
      dataContract: "Content/report/member IDs giả danh, policy version, evidence references, reporter safety flags, decision/reason, appeal linkage, consent and moderation timestamps.",
      integration: "Community sở hữu nội dung và moderation decision. Pet Connect chỉ nhận case opt-in đã tối thiểu hóa; Intelligence chỉ nhận aggregate đã loại định danh.",
      boundary: "Không công khai danh tính người báo cáo; không tự xóa/khóa tài khoản dựa điểm. Thuật toán chỉ xếp hàng và kiểm tra cổng chính sách; quyết định tác động con người do reviewer.",
      pages: {
        overview: playbook("priority", "Gom reports/appeals → áp policy version hiện hành → tách safeguarding → tính SLA/risk queue → giao moderator/reviewer.", "Xếp theo severity policy do người báo cáo/triager gán, nguy cơ tức thời và tuổi case; không dùng popularity làm mức độ đúng.", "queueScore=min(100, severity×35 + safetyRisk×30 + overdueHours×2 + appealSLA×15).", "Case status, policy category/version, reporter safety, SLA, evidence count and assigned reviewer.", "Không hiển thị nội dung nhạy cảm rộng; safety escalation ưu tiên bảo vệ, không thay quyết định điều tra."),
        moderation: playbook("priority", "Nạp case → kiểm duplicate report → phân policy category → che thông tin → moderator ghi rationale → reviewer kiểm quyết định.", "Queue score có thể xếp thứ tự nhưng không phán quyết; mọi action cần policy clause và evidence reference.", "priority=severity×40 + reportAgeHours×2 + exposureBand×20; action requires humanReason AND policyVersion.", "Content/report IDs, category, evidence refs, exposure, report timestamp and policy version.", "Tự động hóa không được remove/ban; evidence thiếu hoặc category không chắc chuyển specialist."),
        posts: playbook("quality", "Tạo draft → kiểm policy checklist/accessibility → duyệt nội dung → xuất bản version → quản lý edit/history.", "Validate required metadata và trạng thái moderation; edited post tạo revision mới và đưa lại review nếu policy yêu cầu.", "publishable=authorVerified AND requiredFieldsValid AND policyChecksPassed AND moderationState=approved.", "Post/version, author pseudonymous ID, media refs, visibility, event links and approval.", "Không đưa dữ liệu cá nhân/vị trí vào public post; xóa an toàn có thể thay bằng tombstone theo retention."),
        reports: playbook("risk", "Nhận report → xác nhận receipt → bảo vệ reporter → gắn evidence refs → triager phân loại → chuyển moderator phù hợp.", "Risk score dùng severity × exposure × vulnerability; chỉ ưu tiên, không dùng để kết luận vi phạm.", "risk=min(100, severity×20 + exposure×30 + vulnerability×30 + repeatSignal×10); unknown evidence => manual review.", "Report ID, alleged content, policy category, evidence provenance, reporter safety and submittedAt.", "Không tiết lộ reporter cho reported user; false/abusive report vẫn phải review, không xóa bằng điểm máy."),
        "member-safety": playbook("risk", "Xác nhận người có nguy cơ → lưu kênh liên lạc an toàn → hạn chế người xem → chuyển safeguarding reviewer → follow-up có consent.", "Cờ rủi ro chỉ kích hoạt bước review; phạm vi hiển thị reporter contact tách khỏi case content.", "safetyFlag=explicitHighRisk OR reviewerEscalation; access=needToKnow AND activeAssignment.", "Pseudonymous member ID, safety preference, safe contact window, access scope and reviewer.", "Không gửi notification có nội dung nhạy cảm ngoài kênh an toàn; không suy diễn nguy cơ từ sentiment score."),
        appeals: playbook("sla", "Nhận appeal → kiểm deadline/decision link → loại reviewer ban đầu khỏi assignment → cấp reviewer độc lập → ghi kết quả và căn cứ.", "SLA tính từ receivedAt; reviewer assignment phải conflict-free; kết quả appeal không xóa decision ban đầu.", "eligible=decisionAppealable AND withinWindow AND reviewerId≠originalModerator AND conflictCheck=clear.", "AppealId, original decision/version, policy version, receivedAt, independent reviewer and outcome.", "Appeal thiếu căn cứ vẫn được triage; trễ SLA chuyển manager, không auto-dismiss."),
        policies: playbook("quality", "Soạn policy version → map category/action/evidence → rà xung đột và appeal path → specialist review → publish ngày hiệu lực.", "Version compare phát hiện rule thiếu definition/owner/appeal route; decision cũ giữ policy version đã áp.", "publish=allCategoriesHaveOwner AND actionsHaveProportionality AND appealPathDefined AND reviewerApproved.", "PolicyId/version, category, examples, action ladder, effectiveAt, owner and approver.", "Không đổi policy hồi tố; mâu thuẫn quy tắc chuyển legal/policy review, không chọn tùy ý."),
        events: playbook("capacity", "Tạo sự kiện → giới hạn chỗ theo venue/host → xác nhận consent media → mở đăng ký → theo dõi waitlist/cancellation.", "Sức chứa còn lại tính theo confirmed registration và hold TTL; waitlist chỉ promote khi slot giải phóng hợp lệ.", "remaining=capacity−confirmed−activeHolds; promote next eligible waitlist if holdExpired or cancellationCommitted.", "Event version, capacity, venue, registrations, consent, waitlist order and event time.", "Không công khai danh sách người tham gia; hủy event phải thông báo và hoàn tác registration idempotent."),
        announcements: playbook("approval", "Soạn audience/message → chạy preview/PII scan → policy owner duyệt → xác nhận audience/consent → schedule/publish → audit delivery.", "Tách author khỏi approver; audience size và kênh được tính lại khi gửi để tránh gửi theo snapshot lỗi thời.", "publish=author≠approver AND templateApproved AND audienceConsentValid AND piiScanPass.", "Message version, audience definition, channel consent, schedule, author and approver.", "Không gửi mass notification nếu consent coverage thấp; hủy schedule trước enqueue phải được bảo đảm."),
        members: playbook("consent", "Tra member bằng pseudonymous ID → kiểm role/purpose → hiển thị trạng thái tối thiểu → thực hiện privacy request theo retention.", "Least privilege theo moderation assignment; marketing consent độc lập với community membership.", "visibleFields=roleAllowlist∩caseAssignment∩purpose; contactAllowed=explicitConsent AND !optOut.", "Member pseudonymous ID, roles, consent versions, safety flags and privacy requests.", "Không expose reporter/target link cho moderator không liên quan; xóa dữ liệu theo policy và giữ tombstone tối thiểu."),
        signals: playbook("risk", "Tổng hợp report patterns đã giảm định danh → lọc cohort nhỏ → đánh giá reviewer → tạo cảnh báo policy, không action tự động.", "Signal score chuẩn hóa theo exposure/time và confidence; cohort nhỏ hoặc drift cao chặn phát hành.", "signal=volumeZScore×confidence; show only if cohort≥k AND confidence≥threshold; never auto-enforce.", "Aggregated category counts, time window, cohort size, confidence and policy version.", "Không hiển thị member-level inference; drift hoặc sample nhỏ chỉ tạo review ticket."),
        analytics: playbook("aggregate", "Chọn cohort/window → dedupe report/content IDs → phân loại resolved/appealed → tính SLA/outcome → suppress small groups.", "Tách report volume khỏi violation-confirmed; phân tích outcome theo policy version và không suy luận nguyên nhân.", "SLA compliance=casesWithinSLA/eligibleClosed; appeal overturn=overturned/decidedAppeals; suppress cohort<k.", "Case events, policy versions, timestamps, outcome labels and de-identified cohort.", "Không xếp hạng moderator theo thô khi case mix khác nhau; freshness/definition hiển thị."),
        integrations: playbook("lineage", "Map minimal case ID/status → kiểm opt-in/purpose → loại reporter PII → gửi Connect/Intelligence aggregate → nhận delivery ack.", "Field allowlist theo consumer; eventId dedupe; Community không chia sẻ raw post/report evidence mặc định.", "share=purposeAllowed AND consentOrPolicyBasis AND fieldSet⊆consumerAllowlist AND eventVersionNew.", "Case reference, coarse status, region generalized, policy-safe category and provenance.", "Không gửi tên/report text/vị trí chính xác; revoke hoặc policy change phải dừng downstream feed."),
        audit: playbook("quality", "Ghi access/action/policy version → che reporter identity → nối decision và appeal → lọc theo assignment → export restricted.", "Kiểm decision có rationale, evidence ref, policy version và actor role; log access riêng khỏi content decision.", "traceable=decisionHasReason AND policyVersionPresent AND reviewerEligible AND accessPurposeRecorded.", "Moderator, case/policy/decision IDs, reason code, timestamps and redacted diff.", "Không log raw evidence; decision sửa tạo event mới; audit failure chặn action nghiêm trọng."),
        settings: playbook("config", "Cấu hình SLA/category/visibility/retention → policy owner review → preview theo fixture → independent approval → publish version.", "Kiểm rule không mở rộng quyền truy cập hơn policy; default-deny audience và moderation action.", "valid=retentionBounded AND appealSLA>0 AND visibilityLeastPrivilege AND testCasesPass AND approverDistinct.", "SLA, categories, access roles, retention, quiet hours and config version.", "Không cho một người tự tăng quyền ban/visibility; thay đổi policy phải có effective date.")
      }
    },
    "pet-connect": {
      owner: "Điều phối viên xác minh case; field responder tiếp nhận nhiệm vụ; đối tác chỉ thấy phần việc được giao; supervisor xác nhận an toàn và bàn giao.",
      dataContract: "Case ID, pet identity references, generalized geohash/zone, reporter contact vault reference, evidence provenance, assignment, safety checklist and handoff signatures.",
      integration: "Connect sở hữu case/assignment/handoff. Community chuyển case opt-in đã che danh tính; Care chỉ nhận confirmed match/status tối thiểu. Vị trí chính xác giữ trong access-controlled vault.",
      boundary: "Bản đồ và case giả lập không phải cứu hộ thật. Không phát vị trí chính xác, thông tin liên hệ hay chỉ dẫn tiếp cận; con người quyết định điều phối, xác minh và bàn giao.",
      pages: {
        overview: playbook("priority", "Gom case mới/đang mở → kiểm vùng và độ mới → đánh giá safety flags → xếp responder phù hợp → theo dõi ETA/handoff.", "Ưu tiên nguy cơ do reporter/responder khai báo, thời gian chờ và độ sẵn sàng; không dùng khoảng cách đơn lẻ để quyết định cứu hộ.", "priority=min(100, safetySeverity×35 + ageHours×2 + noResponder×20 + expiringEvidence×10).", "Case status, generalized zone, safety severity, responder availability, SLA and consent.", "Không hiển thị địa chỉ chính xác trên control tower; escalation khẩn theo protocol địa phương do người điều phối."),
        cases: playbook("priority", "Tạo case → xác thực contact an toàn → phân loại lost/rescue → kiểm trùng → gán zone/owner → cập nhật state có version.", "State machine phân biệt reported, verified, assigned, in-field, reunited/closed; mỗi transition cần actor và evidence.", "transitionAllowed = stateGraph[current].includes(target) AND actorRoleAllowed AND version=current AND reasonPresent.", "Case ID/version, type, generalized zone, owner, priority, consent, evidence refs and status history.", "Không đóng case chỉ vì reporter mất liên lạc; conflict identity/duplicate chuyển supervisor."),
        "lost-pets": playbook("quality", "Ghi đặc điểm nhận dạng tối thiểu → xác thực người báo → chuẩn hóa thời gian/khu vực → tạo vùng tìm kiếm mờ → review trùng.", "Match candidate chỉ gợi ý dựa đặc điểm có trọng số; không kết luận đoàn tụ tự động.", "candidateScore=0.35×visualTraits+0.25×species+0.20×timeProximity+0.20×zoneProximity; require human confirm.", "Species, distinctive traits, photo reference, last-seen time, generalized zone and owner consent.", "Ảnh/đặc điểm có thể sai; không công khai microchip, địa chỉ hoặc dữ liệu liên hệ."),
        "rescue-tasks": playbook("schedule", "Tạo task từ case đã triaged → kiểm responder/skill/shift → kiểm safety prerequisites → gán route coarse → dispatch ack.", "Chọn responder phù hợp kỹ năng và ca trực; ETA chỉ ước lượng, không route đến tọa độ private từ browser.", "eligible=skillMatch AND activeShift AND safetyBriefingAccepted AND zoneAuthorized AND workload<limit.", "Task/case ID, skill, shift, availability, coarse zone, safety briefing and acknowledgement.", "Không điều phối partner chưa xác minh; thiếu PPE/safety checklist giữ task ở pending."),
        partners: playbook("quality", "Thu hồ sơ tổ chức → xác minh liên hệ/chứng nhận → khai báo vùng/loại hỗ trợ → duyệt access scope → rà soát hết hạn.", "Eligibility phụ thuộc verification freshness, service capability và agreement; completeness không thay kiểm tra thực tế.", "eligible=verified AND credentialsCurrent AND agreementActive AND taskType∈capabilities AND accessApproved.", "Partner ID, capabilities, service zone, credentials/expiry, agreement and reviewer.", "Partner suspended mất quyền case ngay; chỉ chia sẻ case khi assignment active."),
        "field-map": playbook("consent", "Chọn case/zone → kiểm quyền assignment → làm tròn tọa độ theo privacy radius → render layer mẫu → hết hạn cache.", "Giảm độ chính xác theo sensitivity; chỉ responder được gán mới có thể yêu cầu vị trí chi tiết qua workflow kiểm soát.", "coarsePoint=geohash(center, precisionByRole); exactLocationAllowed=activeAssignment AND explicitPurpose AND tokenNotExpired.", "Coordinates in protected store, zone precision, role, assignment, purpose and expiry.", "Không lưu exact coordinates trong localStorage/URL/log; demo chỉ là minh họa khu vực, không có map thật."),
        evidence: playbook("quality", "Nhận evidence ref → ghi người cung cấp/thời điểm → kiểm hash/type → che metadata → reviewer xác thực liên quan case.", "Evidence chain yêu cầu provenance và immutable reference; hash chỉ kiểm toàn vẹn file, không xác nhận nội dung đúng.", "validEvidence=sourceRecorded AND timestampPresent AND fileHashMatches AND reviewerStatus∈{pending,verified,rejected}.", "Evidence ID, case ID, source, capturedAt, file type/hash, redaction status and reviewer.", "Không công khai evidence trước review; metadata GPS/EXIF bị loại khỏi bản chia sẻ."),
        "safety-check": playbook("risk", "Responder xem brief → tick hazard checklist → xác nhận liên lạc/đồng hành → đánh giá no-go conditions → supervisor clear.", "Tính safety gate theo các mục bắt buộc; bất kỳ critical hazard chưa mitigated đều block dispatch.", "dispatchAllowed=allCriticalControlsPassed AND briefingAccepted AND responderFit AND supervisorClearIfHighRisk.", "Task, hazard flags, PPE, buddy status, environment, contact plan and supervisor approval.", "Không gợi ý tiếp cận động vật nguy hiểm; no-go chuyển cơ quan/dịch vụ phù hợp."),
        handoff: playbook("quality", "Xác minh bên giao/nhận → khớp case và pet identifiers → ghi condition/time → xác nhận consent → hai bên ký nhận.", "Close chỉ khi hai vai trò độc lập xác nhận, custody event có thời gian và thông tin liên lạc được giữ riêng.", "handoffComplete=senderVerified AND receiverVerified AND identityChecks≥configuredMin AND custodyRecordSigned.", "Case ID, pet traits/ID, sender/receiver refs, timestamp, condition and signatures.", "Mismatch hoặc người nhận không xác minh giữ case mở; không công khai địa chỉ bàn giao."),
        notifications: playbook("sla", "Sinh event case → chọn người nhận có assignment → kiểm kênh an toàn/consent → dedupe → gửi payload tối thiểu → ack/retry.", "Retry theo backoff cho lỗi tạm; nếu assignment/status version đổi thì hủy payload cũ.", "send=assignmentActive AND consentChannel AND eventVersion=current; retry=min(2^attempt×5min,60min), max 3.", "Case/event IDs, role recipient, safe channel preference, consent, version and delivery receipt.", "Không chứa vị trí/liên hệ trong push preview; no-contact preference hủy queued messages."),
        resources: playbook("capacity", "Nạp responder/vehicle/kit availability → loại nghỉ/bảo trì → ghép skill-zone → giữ resource TTL → dispatch confirmation.", "Tính available theo overlap ca và trạng thái readiness; không gán một responder hai task trùng thời gian.", "available = onShift AND trained AND notAssignedOverlap AND resourcesReady AND zoneAuthorized.", "Responder shift, skill, vehicle/kit, task intervals, capacity and maintenance.", "Resource hết hạn/bảo trì không sẵn sàng; hold chưa confirm tự giải phóng."),
        analytics: playbook("aggregate", "Chọn khu vực/time range → generalized zones → tính response/handoff metrics → loại test/duplicate → suppress nhóm nhỏ.", "Response time đo từ reportedAt đến acknowledgedAt; không dùng metric để so sánh responder ngoài bối cảnh case mix.", "medianResponse=P50(ack−reported); resolutionRate=verifiedClosed/eligibleCases; suppress if cohort<k.", "Case lifecycle timestamps, generalized zone, task type, closure reason and cohort size.", "Không xuất tọa độ/identity; incomplete timestamps được báo coverage, không suy đoán."),
        audit: playbook("quality", "Ghi mọi location reveal/access/assignment/handoff → gắn purpose → kiểm người xem hợp lệ → phát hiện truy cập lệch → review.", "Đặc biệt kiểm location access token: assignment, purpose, expiry; bất kỳ lượt xem ngoài phạm vi tạo alert.", "locationAccessValid=assignmentActive AND purposeAllowed AND tokenTTL≤configuredMax AND actorAuthorized.", "Actor, case, action, generalized/exact location scope, purpose, token ID and outcome.", "Không lưu tọa độ trong audit; chỉ ghi access reference; audit failure chặn exact-location reveal."),
        integrations: playbook("lineage", "Nhận opt-in case referral → kiểm consent/source → map minimal schema → generalize location → ack/referral status → reconcile duplicates.", "Reference-only linkage; merge chỉ sau human verification, event ID chống lặp và source provenance được giữ.", "accept=consentValid AND sourceVerified AND requiredFieldsPresent AND locationGeneralized AND eventIdUnseen.", "Referral ID, source case, pet reference, coarse zone, consent, provenance and event version.", "Không gửi contact/evidence/raw coordinates; match không chắc tạo candidate relation thay vì merge."),
        settings: playbook("config", "Cấu hình privacy radius, responder zones, safety thresholds/TTL → test fixtures → privacy owner duyệt → version hóa.", "Kiểm precision không chi tiết hơn policy; TTL hữu hạn; config degrade về coarse visibility khi validation lỗi.", "valid=precision≤roleCeiling AND tokenTTL>0 AND criticalSafetyRulesPresent AND testsPass.", "Zone precision, access roles, token TTL, safety gates, quiet hours and config version.", "Không cho client cấu hình tăng precision; production cần threat model và review quyền vị trí.")
      }
    },
    "pet-intelligence": {
      owner: "Data owner duyệt mục đích và chất lượng; privacy/security đánh giá quyền; model owner quản lý version; independent reviewer quyết định release/rollback.",
      dataContract: "Dataset/model/use-case IDs, schema/lineage versions, purpose/legal basis, consent/tenant filters, cohort size, evaluation artifacts, approval identities, monitoring and rollback pointers.",
      integration: "Intelligence chỉ nhận curated/aggregate feeds với lineage và purpose. Không cung cấp quyết định tự động cho Health/Community; output dùng shadow mode cho tới khi owner/reviewer phê duyệt.",
      boundary: "Không huấn luyện model thật, không xử lý dữ liệu thật, không tự ra quyết định lâm sàng/moderation/giá. Điểm số demo là kiểm soát kỹ thuật, không chứng minh fairness/accuracy production.",
      pages: {
        overview: playbook("priority", "Thu health/lineage/release alerts → áp risk taxonomy → tính gate severity → xếp owner → giữ model ở shadow nếu có blocker.", "Ưu tiên blocker consent/tenant/security trước drift; score chỉ xếp công việc, không tự bật model.", "gatePriority=consentBlock×40 + securityBlock×30 + qualityBlock×20 + overdue×2; any criticalBlock => no release.", "Dataset freshness, lineage, approval gates, drift, incidents and model release state.", "Không hiển thị dữ liệu cá nhân; critical privacy/security blocker luôn chặn release bất kể score."),
        datasets: playbook("quality", "Đăng ký dataset → xác định owner/purpose/tenant → kiểm schema/quality/freshness → xác nhận retention/consent → approve access.", "Readiness là tích của các cổng độc lập; trường null không được xem như hợp lệ mặc định.", "ready=ownerPresent AND schemaValid AND freshness≤SLA AND consentCoverage≥threshold AND tenantFilterTestPass.", "Dataset/version, owner, schema, source, purpose, consent coverage, freshness, retention and row count.", "Cohort nhỏ/PII không được cấp quyền; thiếu owner hoặc retention block downstream."),
        lineage: playbook("lineage", "Nối source→transform→dataset→feature→model→output → kiểm version/hash → đánh dấu field classification → reviewer trace.", "Coverage theo cạnh lineage có provenance; source ngoài catalog hoặc transform không tái lập làm pipeline ineligible.", "coverage=verifiedEdges/expectedEdges×100; reproducible=allTransformVersionsPinned AND sourceSnapshotsAvailable.", "Node/edge IDs, versions, code hash, field lineage, timestamps and owner.", "Không suy lineage từ tên cột; untracked source chặn publish."),
        "use-cases": playbook("approval", "Khai báo mục tiêu/decision owner → xác định affected parties → data minimization → risk assessment → independent review → approve/reject.", "Use-case gate kiểm purpose, prohibited use, human override và measurable success metric trước dataset access.", "approved=purposeSpecific AND ownerNamed AND impactAssessmentComplete AND prohibitedUseCheckPass AND independentReviewer.", "UseCase ID, purpose, user population, data fields, impact, human review, success/stop criteria.", "Mục tiêu mơ hồ/secondary use chưa duyệt bị block; không tái dùng approval cho purpose khác."),
        "model-registry": playbook("quality", "Đăng ký artifact/version → pin code/data/feature schema → quét dependencies → xác định owner/stage → ký artifact → stage shadow.", "Model identity content-addressed; cùng version label nhưng artifact hash khác phải coi là artifact mới.", "registrable=artifactHashPresent AND dependenciesScanned AND datasetLineageComplete AND ownerAssigned AND signatureVerified.", "Model/version, artifact hash, training data refs, code/dependency versions, owner and stage.", "Không deploy artifact không xác minh; rollback pointer phải tồn tại trước staging."),
        evaluations: playbook("quality", "Chọn frozen test set → chạy baseline/candidate → tính metric và slice → so threshold/confidence interval → reviewer đọc → quyết định.", "Đánh giá gồm overall và cohort; small cohort suppressed; metric không đủ sample hoặc confidence thì inconclusive, không pass.", "pass=overallMetric≥min AND eachCriticalSlice≥sliceMin AND n≥minimumSample AND CIWidth≤maxWidth.", "Evaluation version, test set hash, metrics/slices, sample size, thresholds and reviewer.", "Không dùng test set bị leakage; kết quả inconclusive không được chuyển thành pass."),
        approvals: playbook("approval", "Tập hợp data owner/privacy/security/model approvals → kiểm xung đột → verify version/hash → ghi quyết định có hạn.", "Mỗi approval gắn chính xác artifact/config version và scope; bất kỳ input version đổi làm approval stale.", "releaseEligible=allRequiredApprovals AND approversDistinct AND artifactHashCurrent AND approvalNotExpired.", "Approver role/ID, artifact/config hashes, scope, purpose, expiry and decision reason.", "Thiếu approver độc lập hoặc approval version mismatch chặn rollout."),
        monitoring: playbook("sla", "Thu health metrics → kiểm freshness/completeness → so baseline/threshold → tạo incident ticket → owner acknowledge → close có căn cứ.", "Cảnh báo theo ngưỡng cấu hình và cửa sổ; debounce giảm noise nhưng không suppress critical privacy failures.", "alert if freshness>maxLag OR errorRate>limit OR quality<floor for consecutiveWindows; critical privacy => immediate.", "Timestamp lag, error rate, quality metrics, baseline version, alert window and owner.", "Missing telemetry không được coi là healthy; chuyển monitoring state=unknown và chặn promotion."),
        drift: playbook("risk", "So reference/current distributions → kiểm schema/cohort coverage → tính PSI/KS theo metric phù hợp → reviewer xác nhận → action plan.", "Drift statistic là trigger kiểm tra, không chứng minh model sai; cohort nhỏ hoặc schema change tạo inconclusive.", "PSI=Σ(current−reference)×ln(current/reference); flag at configured threshold with minimum sample.", "Reference/current window, feature distributions, cohort sizes, metric versions and thresholds.", "Không đưa demographic attribute ra action; mọi slice nhạy cảm cần privacy/legal approval."),
        incidents: playbook("risk", "Ghi incident/impact → severity classify → contain feature/model → preserve evidence → notify owner → root cause → corrective actions.", "Severity combines scope, duration and harm potential; containment may pause output but never auto-delete evidence.", "severity=max(policySeverity, impactBand×durationBand); criticalIncident => freeze promotion and invoke human response.", "Incident ID, model/use case, impact, time window, affected consumers, containment and owner.", "Không kết luận nguyên nhân bằng tương quan; bảo toàn audit và chuyển privacy/security khi liên quan dữ liệu."),
        releases: playbook("release", "Đóng băng artifact/config → kiểm đủ approvals/evals/monitoring → staged rollout shadow/canary → observe → owner promotes.", "Release gate fail-closed; canary tăng theo bước chỉ khi quality/error/guardrail pass liên tiếp.", "go=approvalsCurrent AND evaluationPass AND monitoringHealthy AND rollbackReady; canaryStep only after N healthy windows.", "Artifact/config hash, approvals, eval report, monitoring window, cohort and rollback pointer.", "Không gọi production deployment; mọi bước trong demo chỉ thay trạng thái mô phỏng."),
        rollback: playbook("rollback", "Phát hiện gate breach → pause promotion → pin last-known-good → route consumers về manual path → verify recovery → incident review.", "Rollback quyết định theo threshold hoặc human trigger; giữ data/event versions và không xóa artifact lỗi.", "rollbackTrigger=errorRate>limit OR privacyGateFail OR ownerCommand; execute only if priorVersionVerified AND manualFallbackReady.", "Current/previous artifact hashes, trigger, consumers, fallback owner and recovery checks.", "Không tự khôi phục nếu rollback target không xác minh; manual fallback phải được test."),
        audit: playbook("quality", "Ghi dataset/model/approval/access event → liên kết lineage/hash → kiểm completeness → tạo audit package có phạm vi.", "Traceability yêu cầu nối use-case→dataset→artifact→evaluation→approval→release; mọi link thiếu là finding.", "traceComplete=allRequiredLinksPresent AND versionsConsistent AND approverSeparationPass AND timestampsOrdered.", "Actor, object/version, purpose, event, hash, source and approval references.", "Không lưu raw training rows; audit export cần access review và redaction."),
        integrations: playbook("lineage", "Đăng ký producer/consumer → data classification → contract/schema/purpose review → test tenancy/consent → monitor lag → revoke on policy change.", "Contract version và access scope pin theo consumer; source quality failure dừng ingest thay vì lấp giá trị giả.", "ingest=contractApproved AND tenantFilterPass AND purposeValid AND schemaVersionSupported AND freshnessWithinSLA.", "Producer/consumer, contract, purpose, classification, tenant filter, event lineage and SLA.", "Không forward raw PII; consumer bị thu hồi phải dừng subscription và xác nhận xóa cache theo policy."),
        settings: playbook("config", "Đặt thresholds/sample minimum/retention/reviewer matrix → static validation → adversarial fixtures → governance approval → version publish.", "Ngưỡng phải có owner, rationale, range và test; thay đổi threshold tái đánh giá các release phụ thuộc.", "valid=thresholdsBounded AND minimumSample>0 AND approversDistinct AND regressionFixturesPass.", "Thresholds, cohort minimum, retention, roles, alert windows and config version.", "Không có default permissive khi field thiếu; config không được hạ ngưỡng chỉ để vượt gate.")
      }
    }
  };

  const businessScreen = (title, subtitle, columns, rows, stages, signals, action, actionDescription, control) => ({
    title, subtitle, columns, rows, stages, signals, action, actionDescription, control
  });
  const businessScreens = {
    branches: businessScreen("Portfolio chi nhánh", "So sánh hiệu suất theo cùng kỳ và độ phủ dữ liệu; chọn chi nhánh để khoanh vùng các nghiệp vụ cần xử lý.", ["Mã / cơ sở", "Quản lý", "Doanh thu thuần", "Tồn dưới ngưỡng", "Sức khỏe"], [
      ["HN-01 · Hà Nội", "Ngọc Phạm", "₫42,8tr · 18 đơn", "3 SKU", "Ổn định"],
      ["HCM-02 · Thủ Đức", "Tuấn Lê", "₫36,1tr · 14 đơn", "4 SKU", "Theo dõi"],
      ["DN-01 · Đà Nẵng", "Huy Trần", "₫21,4tr · 9 đơn", "5 SKU", "Cần xử lý"],
      ["CT-01 · Cần Thơ", "Mai Võ", "₫28,1tr · 11 đơn", "1 SKU", "Ổn định"]
    ], [["1", "Chọn tenant / cây chi nhánh"], ["2", "Đối chiếu cùng kỳ"], ["3", "Mở exception của cơ sở"], ["4", "Giao branch owner"]], [["Độ phủ dữ liệu", "4/4 chi nhánh có snapshot hợp lệ", "Đạt", "green"], ["Đóng ca chờ soát", "DN-01 · lệch quỹ ₫120.000", "1 case", "gold"], ["Quyền xem", "Branch scope lấy theo vai trò", "Giới hạn", "blue"]], "Mở hồ sơ chi nhánh", "Mở trang chi nhánh mẫu với KPI, owner, tồn và các hàng đợi; không thay đổi dữ liệu doanh nghiệp.", "So sánh không áp dụng khi kỳ/định nghĩa KPI khác nhau hoặc độ phủ dữ liệu dưới ngưỡng."),
    inventory: businessScreen("Sổ tồn theo SKU · location · lot", "Tồn khả dụng không đồng nghĩa tồn ghi nhận. Đối chiếu reservation, hàng cách ly, lô và hạn trước khi đề nghị mua.", ["SKU / sản phẩm", "Chi nhánh · lô", "On hand", "Đã giữ / cách ly", "Khả dụng / ngưỡng"], [
      ["FD-DOG-03 · Thức ăn chó 3kg", "HN-01 · LOT-HN-441", "14", "4 / 2", "8 / 12 · Bổ sung"],
      ["LT-CAT-05 · Cát vệ sinh 5L", "HCM-02 · LOT-HC-184", "24", "5 / 2", "17 / 20 · Theo dõi"],
      ["AC-LEASH-M · Dây dắt size M", "DN-01 · LOT-DN-091", "36", "4 / 1", "31 / 10 · Đủ"],
      ["FD-CAT-02 · Thức ăn mèo 2kg", "CT-01 · LOT-CT-021", "8", "3 / 1", "4 / 10 · Bổ sung"]
    ], [["1", "Đọc ledger movements"], ["2", "Trừ reservation / quarantine"], ["3", "Kiểm tra unit và hạn lô"], ["4", "Tạo đề nghị, không tự ghi tồn"]], [["Ngưỡng thấp", "2 SKU chạm reorder point", "Ưu tiên", "red"], ["Lô gần hạn", "LOT-HN-441 · cần xem FEFO", "30 ngày", "gold"], ["Bản snapshot", "INV-SNAP-2026-10-16 · v18", "Mới", "blue"]], "Tạo đề nghị bổ sung", "Tạo bản ghi đề nghị mua mẫu; hệ thống thật phải kiểm tồn lại theo version và phê duyệt trước khi phát PO.", "available = onHand − reserved − quarantined; đơn vị phải đồng nhất và balance không được âm."),
    procurement: businessScreen("Đề nghị mua & kiểm soát ngân sách", "Requisition chỉ là đề xuất nội bộ. Tách người lập/người duyệt, kiểm báo giá, ngưỡng ngân sách và kỳ kế toán.", ["Req / chi nhánh", "Nhà cung cấp · dòng SKU", "Giá trị dự kiến", "Maker → checker", "Cổng hiện tại"], [
      ["PR-0084 · HN-01", "Pet Supply VN · 32 SKU", "₫8.420.000", "Ngọc Phạm → Quản lý vùng", "Chờ duyệt"],
      ["PR-0082 · HCM-02", "Thức ăn & cát · 18 SKU", "₫6.180.000", "Tuấn Lê → Finance", "Thiếu báo giá"],
      ["PR-0079 · DN-01", "Bao bì / vật tư · 9 SKU", "₫2.040.000", "Huy Trần → Quản lý vùng", "Đã duyệt"],
      ["PR-0076 · CT-01", "Phụ kiện · 12 SKU", "₫3.620.000", "Mai Võ → Finance", "Đang đối chiếu"]
    ], [["1", "Tính nhu cầu từ tồn"], ["2", "Chọn vendor / quote"], ["3", "Kiểm ngân sách"], ["4", "Checker duyệt → PO draft"]], [["Ngân sách tháng", "₫24,6tr dự kiến · ₫18,2tr còn", "62% dùng", "blue"], ["Tách nhiệm vụ", "Maker không thể tự approve", "Bắt buộc", "gold"], ["Thiếu chứng từ", "PR-0082 chưa đủ báo giá", "Chặn", "red"]], "Tạo đề nghị mua", "Tạo requisition sandbox; không phát đơn mua hay cam kết thanh toán với nhà cung cấp.", "suggestedQty = max(0, targetStock − available − onOrder); approval theo amount/branch/category; makerId ≠ checkerId."),
    suppliers: businessScreen("Hồ sơ & hiệu lực nhà cung cấp", "Quản lý trạng thái xác minh, hợp đồng, điều kiện thanh toán và thay đổi thông tin nhạy cảm theo maker-checker.", ["Nhà cung cấp", "MST / hồ sơ", "Hợp đồng hiệu lực", "Điều khoản", "Trạng thái"], [
      ["SUP-001 · Pet Supply VN", "Đã đối chiếu · đủ hồ sơ", "01/01–31/12/2026", "Net 15 · giao HN/HCM", "Đang hoạt động"],
      ["SUP-004 · An Tâm Pet", "Thiếu chứng từ mới", "Hết hạn 30/09/2026", "Net 7 · giao toàn quốc", "Cần cập nhật"],
      ["SUP-008 · GreenPaws", "Đã xác minh · v3", "01/06/2026–31/05/2027", "COD · giới hạn ₫20tr", "Đang hoạt động"],
      ["SUP-012 · Kho Vận Miền Trung", "Đang review tài khoản", "01/08–31/12/2026", "Net 10 · DN/CT", "Tạm giữ"]
    ], [["1", "Thu hồ sơ / nguồn xác minh"], ["2", "Review độc lập điều khoản"], ["3", "Bật vendor scope"], ["4", "Rà soát trước hết hạn"]], [["Sắp hết hạn", "An Tâm Pet · hợp đồng đã hết", "1 hồ sơ", "red"], ["Tài khoản thay đổi", "SUP-012 · đang checker review", "Chưa duyệt", "gold"], ["PO đang mở", "3 PO tham chiếu SUP-001", "Đối chiếu", "blue"]], "Ghi nhận hồ sơ nhà cung cấp", "Ghi hồ sơ vendor giả lập; thay đổi tài khoản thanh toán ngoài hệ thống cần gọi xác minh và phê duyệt độc lập.", "PO eligibility = documentsCurrent AND termsActive AND status=active AND bankChangeApprovedBy ≠ maker."),
    receiving: businessScreen("Nhận hàng · 3-way match", "Đối chiếu PO, số nhận thực tế và hóa đơn. Sai lệch không được tự động cộng tồn hoặc ghi công nợ.", ["Receipt / PO", "SKU / lô", "PO qty", "Nhận / loại", "Match"], [
      ["GRN-0318 · PO-084", "FD-DOG-03 · LOT-HN-441", "24", "24 / 0", "Khớp"],
      ["GRN-0316 · PO-081", "LT-CAT-05 · LOT-HC-184", "40", "38 / 2", "Thiếu 2"],
      ["GRN-0312 · PO-079", "AC-LEASH-M · LOT-DN-091", "16", "16 / 0", "Chờ invoice"],
      ["GRN-0308 · PO-076", "FD-CAT-02 · LOT-CT-021", "20", "22 / 0", "Thừa 2"]
    ], [["1", "Xác nhận PO / dock"], ["2", "Scan qty, lot, expiry"], ["3", "So hóa đơn và PO"], ["4", "Checker nhận / cách ly"]], [["Chờ xác nhận", "GRN-0316 · thiếu 2 units", "Variance", "gold"], ["Chất lượng lô", "Expiry + điều kiện bảo quản", "Cần nhập", "blue"], ["Tồn sổ", "Chỉ tăng sau receipt được duyệt", "Chặn sớm", "red"]], "Mở phiếu nhận hàng", "Tạo receipt draft trong sandbox; chưa tăng tồn và không tạo khoản phải trả.", "qtyDelta = received − ordered; priceDelta = invoiceUnit − POUnit; pass khi cả hai trong tolerance cấu hình."),
    transfers: businessScreen("Điều chuyển kho liên chi nhánh", "Phiếu chuyển gồm yêu cầu, xuất, vận chuyển và nhận. Tồn đang vận chuyển không thuộc tồn khả dụng của hai kho.", ["Transfer", "Nguồn → đích", "SKU / số lượng", "Dispatch / ETA", "Trạng thái"], [
      ["TR-0212", "HN-01 → HN-02", "AC-LEASH-M · 12", "Xuất 08:20 · ETA 11:00", "Đang vận chuyển"],
      ["TR-0209", "HCM-02 → DN-01", "LT-CAT-05 · 8", "Nhận 09:12 · lệch 1", "Cần đối chiếu"],
      ["TR-0204", "CT-01 → HCM-02", "FD-CAT-02 · 16", "Dự kiến 17/10", "Chờ duyệt"],
      ["TR-0198", "DN-01 → HN-01", "AC-BOWL-S · 6", "Nhận đủ · GRN-302", "Hoàn tất"]
    ], [["1", "Kiểm nguồn khả dụng"], ["2", "Duyệt và giữ lượng"], ["3", "Dispatch + in-transit"], ["4", "Nhận đủ / ghi lệch"]], [["Đang vận chuyển", "1 transfer · tổng 12 units", "Theo dõi", "blue"], ["Sai lệch nhận", "TR-0209 · thiếu 1 unit", "Exception", "red"], ["ETA trễ", "Không tự đóng transfer", "Cảnh báo", "gold"]], "Tạo phiếu điều chuyển", "Tạo transfer request giả lập; nguồn và đích chỉ cập nhật ledger sau hai bước xuất và nhận xác nhận.", "DispatchQty ≤ sourceAvailable; inTransit = dispatched − received − lost; mọi movement phải liên kết cùng transferId."),
    adjustments: businessScreen("Kiểm kê & điều chỉnh có chứng cứ", "Điều chỉnh không sửa số tồn trực tiếp. Tạo movement bù có reason, chứng cứ, người kiểm đếm và checker riêng.", ["Count ID", "SKU / vị trí", "Sổ sách", "Đếm thực tế", "Sai lệch / duyệt"], [
      ["STK-0141 · HCM-02", "LT-CAT-05 · bin A-03", "24", "22", "−2 · Chờ recount"],
      ["STK-0138 · DN-01", "FD-DOG-03 · bin B-02", "18", "19", "+1 · Chờ checker"],
      ["STK-0133 · HN-01", "AC-LEASH-M · bin C-08", "31", "31", "0 · Khớp"],
      ["STK-0129 · CT-01", "FD-CAT-02 · lot CT-021", "8", "6", "−2 · Thiếu ảnh"]
    ], [["1", "Chốt snapshot sổ"], ["2", "Blind count độc lập"], ["3", "Ghi reason / evidence"], ["4", "Checker duyệt movement"]], [["Giá trị lệch", "2 dòng cần recount trước duyệt", "Mở", "gold"], ["Kỳ kế toán", "Tháng 10 · đang mở", "Cho phép draft", "blue"], ["Segregation", "Người đếm khác checker", "Bắt buộc", "red"]], "Tạo phiếu kiểm kê", "Tạo count draft mẫu; không sửa số lượng sổ và không phát movement cho tới khi checker duyệt.", "delta = counted − book; postAllowed = reasonValid AND evidencePresent AND checker ≠ maker AND periodOpen."),
    approvals: businessScreen("Hàng đợi phê duyệt độc lập", "Một quyết định, một phiên bản request. Maker không được duyệt request của mình; sửa request làm approval cũ mất hiệu lực.", ["Request / loại", "Chi nhánh", "Maker", "Giá trị / rủi ro", "Checker / SLA"], [
      ["PR-0084 · Mua hàng", "HN-01", "Ngọc Phạm", "₫8.420.000 · quote đủ", "Quản lý vùng · 42 phút"],
      ["STK-0141 · Điều chỉnh", "HCM-02", "Tuấn Lê", "−2 units · cần recount", "Kho vùng · 18 phút"],
      ["FIN-0061 · Đóng ca", "DN-01", "Huy Trần", "₫120.000 lệch quỹ", "Finance · quá SLA"],
      ["EMP-0038 · Quyền kho", "CT-01", "Admin cơ sở", "Quyền nhạy cảm", "Security · chưa nhận"]
    ], [["1", "Tải request version"], ["2", "Kiểm tra policy / scope"], ["3", "Checker độc lập quyết định"], ["4", "Commit hoặc trả bổ sung"]], [["Quá SLA", "FIN-0061 · chuyển Finance lead", "Escalate", "red"], ["Thiếu chứng cứ", "STK-0141 · không cho approve", "Block", "gold"], ["Tách nhiệm vụ", "0 request tự duyệt", "Đạt", "green"]], "Tạo yêu cầu phê duyệt", "Tạo yêu cầu approval minh họa; quyết định thật phải có role authorization và audit không thể xóa.", "approve = makerId ≠ checkerId AND checkerRole covers threshold AND requestVersion=current AND periodOpen."),
    finance: businessScreen("Finance close & settlement control", "Theo dõi kỳ, giao dịch treo, phí và đối soát. Bản demo chỉ lập danh sách kiểm tra, không tạo bút toán.", ["Batch / kỳ", "Chi nhánh · nguồn", "Gross / fee", "Khớp / treo", "Kỳ / trạng thái"], [
      ["SET-0621 · 16/10", "HN-01 · POS", "₫12.480.000 / ₫124.800", "18 / 0", "Đã đối chiếu"],
      ["SET-0619 · 16/10", "DN-01 · QR", "₫6.240.000 / ₫62.400", "8 / 1", "Lệch ₫120.000"],
      ["SET-0615 · 15/10", "HCM-02 · Online", "₫9.180.000 / ₫91.800", "12 / 0", "Chờ payout"],
      ["SET-0611 · 15/10", "CT-01 · POS", "₫4.840.000 / ₫48.400", "7 / 0", "Đã đối chiếu"]
    ], [["1", "Kỳ đang mở · 01–31/10"], ["2", "Import payout snapshot"], ["3", "Resolve unmatched items"], ["4", "Checker review → close"]], [["Kỳ đóng sổ", "Còn 15 ngày · chưa khóa", "Đang mở", "blue"], ["Suspense", "DN-01 · ₫120.000", "1 giao dịch", "red"], ["Posting", "Không có journal demo gửi ra ngoài", "Read-only", "gold"]], "Mở checklist đóng kỳ", "Mở checklist đối soát mô phỏng; không tạo journal entry, không gọi ngân hàng và không khóa kỳ thật.", "matched khi reference exact, currency giống nhau và |amountDelta| ≤ minor unit; fuzzy match chỉ đưa vào review."),
    reconciliation: businessScreen("Reconciliation workbench", "Ghép settlement, order/receipt và ledger theo khóa giao dịch. Ghép gần đúng chỉ gợi ý, không tự đánh dấu khớp.", ["Exception ID", "Nguồn A", "Nguồn B", "Delta", "Xử lý tiếp"], [
      ["REC-0218 · DN-01", "POS-8841 · ₫1.240.000", "SET-0619 · ₫1.120.000", "−₫120.000", "Chờ Finance"],
      ["REC-0212 · HCM-02", "PO-0081 · 38 units", "GRN-0316 · 40 units", "+2 units", "Chờ kiểm hàng"],
      ["REC-0208 · HN-01", "TR-0212 · 12 units", "Dispatch scan · 12", "0", "Khớp exact"],
      ["REC-0202 · CT-01", "POS-8820 · ₫480.000", "Payout ref thiếu", "Chưa tính", "Thiếu source"]
    ], [["1", "Nạp nguồn và giữ raw ref"], ["2", "Exact match trước"], ["3", "Tính residual / tolerance"], ["4", "Reviewer đóng exception"]], [["Auto-match exact", "18 dòng · reference trùng", "Đã đề xuất", "green"], ["Cần review", "3 dòng · amount/date candidate", "Không tự ghép", "gold"], ["Nguồn lỗi", "1 batch thiếu currency", "Quarantine", "red"]], "Chạy đối chiếu demo", "Chạy thuật toán với tolerance đã nhập; kết quả chỉ ghi audit mô phỏng, không sửa settlement hoặc ledger.", "Mỗi source row chỉ được match một lần; residual = Σleft − Σright; sai tolerance tạo exception."),
    reports: businessScreen("Branch performance & controls", "Dashboard quản trị có định nghĩa KPI, kỳ so sánh, nguồn và freshness; chọn branch để drill-down theo quyền.", ["Chỉ số", "Kỳ hiện tại", "Kỳ trước", "Thay đổi", "Coverage"], [
      ["Doanh thu thuần", "₫128,4tr", "₫116,2tr", "+10,5%", "4/4 branch"],
      ["Tỷ lệ đáp ứng tồn", "92,4%", "89,1%", "+3,3 điểm", "SKU active"],
      ["Thời gian nhận hàng TB", "1,8 ngày", "1,6 ngày", "+0,2 ngày", "21 receipt"],
      ["Exception quá SLA", "3", "2", "+1", "Tất cả branch"]
    ], [["1", "Chọn kỳ / branch"], ["2", "Kiểm định nghĩa + coverage"], ["3", "So cùng cohort"], ["4", "Drill-down exception"]], [["Freshness", "Snapshot 16/10 · 07:00", "Mới 26 phút", "green"], ["Kỳ so sánh", "01–16/10 vs 01–16/09", "Cùng độ dài", "blue"], ["Cảnh báo", "Không suy diễn nguyên nhân từ biến động", "Review", "gold"]], "Xuất báo cáo nội bộ", "Xuất bản xem trước trong trình duyệt; dữ liệu được ẩn/giới hạn theo quyền branch và không gồm PII.", "variancePct = (actual − target) / max(|target|, ε); KPI không có denominator/coverage thì hiển thị N/A."),
    audit: businessScreen("Audit trail · transaction lineage", "Truy vết yêu cầu từ actor và branch đến quyết định checker, movement và external reference; event gốc không bị ghi đè.", ["Thời điểm", "Actor · role", "Object / version", "Hành động", "Kết quả"], [
      ["07:42:28 · 16/10", "Ngọc Phạm · Buyer", "PR-0084 · v3", "Tạo requisition", "Chờ checker"],
      ["07:18:02 · 16/10", "Tuấn Lê · Branch ops", "STK-0141 · v2", "Gửi recount", "Thiếu ảnh"],
      ["06:59:44 · 16/10", "Finance adapter", "SET-0619 · v1", "Import payout ref", "Delta ₫120.000"],
      ["06:34:12 · 16/10", "System · Inventory", "TR-0212 · v4", "Dispatch committed", "Event ack"]
    ], [["1", "Tìm request / correlation ID"], ["2", "Mở chuỗi version"], ["3", "So actor và policy"], ["4", "Xuất evidence đã che"], ["5", "Ghi kết luận reviewer"]], [["Sự kiện hôm nay", "84 event · 100% có request ID", "Đủ dấu vết", "green"], ["Quyết định cần xem", "FIN-0061 · reason chưa ghi", "Thiếu căn cứ", "red"], ["Dữ liệu được che", "Tài khoản / liên hệ / secret", "Redacted", "blue"]], "Tạo audit evidence pack", "Tạo audit snapshot đã che thông tin nhạy cảm; không sửa hay xóa lịch sử gốc.", "Traceable khi requestId, actor, objectVersion, decisionReason và movement/sourceRef liên kết đầy đủ."),
    integrations: businessScreen("Connector health & data contracts", "Mỗi kết nối có owner, schema/version, scope chi nhánh, độ trễ, cursor, retry, DLQ và trạng thái ack.", ["Connector", "Contract / version", "Scope", "Độ trễ", "Health / DLQ"], [
      ["Commerce stock feed", "inventory.availability · v2", "4 branch · read", "42 giây", "Healthy · 0"],
      ["Service capacity", "branch.capacity · v1", "HN/HCM · read", "3 phút", "Chậm · 2 retry"],
      ["Finance payout", "settlement.import · v3", "Finance only", "Đợi file", "Degraded · 1 DLQ"],
      ["Intelligence metrics", "business.aggregate · v1", "Aggregate only", "1 giờ", "Healthy · 0"]
    ], [["1", "Xác thực connector identity"], ["2", "Validate schema / scope"], ["3", "Commit idempotently"], ["4", "Ack hoặc DLQ có owner"], ["5", "Reconcile sau replay"]], [["Outbox backlog", "6 event · oldest 4 phút", "Theo dõi", "gold"], ["Tenant mismatch", "0 event được accept sai scope", "Fail-closed", "green"], ["DLQ", "Settlement batch cần Finance owner", "Có owner", "red"]], "Chạy contract test", "Chạy kiểm tra schema/payload mẫu tại trình duyệt; không gọi endpoint hoặc gửi dữ liệu sang hệ thống khác.", "accept = schemaValid AND tenant/branchAllowed AND eventVersionNew AND idempotencyKeyUnseen; lỗi phải vào DLQ."),
    settings: businessScreen("Organization policy & configuration", "Cấu hình có phiên bản, phạm vi hiệu lực, owner và checker. Preview không áp dụng lên giao dịch đang chạy.", ["Tham số", "Giá trị hiện tại", "Phạm vi", "Version", "Kiểm soát"], [
      ["Reorder policy", "Min/max · lead time 7 ngày", "4 branches", "INV-POL-v4", "Đã duyệt"],
      ["Approval threshold", "≤₫5tr branch · >₫5tr region", "Procurement", "APR-MTX-v3", "Đã duyệt"],
      ["Reconcile tolerance", "1 minor unit / currency", "Finance", "REC-RULE-v2", "Cần review"],
      ["Period close", "Ngày 01–31 · soft close 28/10", "FY2026", "CAL-v6", "Đang hiệu lực"]
    ], [["1", "Tạo draft version"], ["2", "Validate range / role"], ["3", "Dry-run fixtures"], ["4", "Independent checker"], ["5", "Hiệu lực từ kỳ mới"]], [["Thay đổi chờ duyệt", "REC-RULE-v3 · Finance lead", "1 config", "gold"], ["Tách quyền", "Người tạo ≠ reviewer", "Đạt", "green"], ["Rollback", "Giữ version trước khả dụng", "Prepared", "blue"]], "Tạo bản cấu hình mới", "Tạo config draft sandbox; cấu hình chỉ có hiệu lực sau test pass và checker duyệt độc lập.", "valid = schema/range valid AND test fixtures pass AND ownerApproved AND reviewer ≠ author.")
  };
  const businessJourneys = {
    overview: {
      illustration: "control-tower", caption: "Phạm vi chi nhánh → công việc → kiểm soát → kết quả.",
      summary: "Control tower tập hợp tình trạng chi nhánh, tồn, mua hàng, phê duyệt và đóng kỳ. Chỉ số tổng hợp phải cho biết kỳ dữ liệu, thời điểm snapshot và độ phủ.",
      owner: "Quản lý vận hành vùng phối hợp với Supply Operations và Finance.",
      data: ["Nguồn: branch KPI, inventory snapshot, approval queue và finance close.", "Phạm vi tenant/branch áp dụng theo quyền người dùng.", "Chỉ đọc snapshot có version, source timestamp và quality state.", "Không ghi nghiệp vụ từ dashboard; drill-down mở hàng đợi chuyên trách."],
      guard: "Không cộng KPI khác kỳ/định nghĩa; snapshot stale hoặc thiếu coverage phải hiện cảnh báo.",
      path: ["overview", "branches", "inventory", "procurement", "approvals", "finance", "reports"],
      links: [["branches", "Portfolio, branch owner và độ phủ dữ liệu."], ["inventory", "SKU/lô thiếu, cách ly hoặc gần hạn."], ["approvals", "Request chờ checker và SLA."], ["finance", "Trạng thái kỳ đóng và khoản treo."], ["reports", "So sánh KPI giữa các cơ sở cùng kỳ."]]
    },
    branches: {
      illustration: "branches", caption: "Tenant → chi nhánh → owner → hàng đợi nghiệp vụ.",
      summary: "Hồ sơ chi nhánh là điểm gốc để lọc hoạt động. So sánh cùng kỳ/định nghĩa KPI, sau đó drill-down tới tồn, ngoại lệ và báo cáo trong cùng branch scope.",
      owner: "Regional Operations; branch manager chịu trách nhiệm dữ liệu tại cơ sở.",
      data: ["Nguồn: branch master, POS close, stock snapshot và lịch đồng bộ.", "Khóa dữ liệu: tenantId + branchId; mã hiển thị không dùng làm khóa.", "KPI: doanh thu thuần, đơn, tồn dưới ngưỡng và sai lệch ca.", "Drill-down mang theo branchId và period."],
      guard: "Ẩn chi nhánh ngoài quyền; không xếp hạng nếu coverage thấp hoặc kỳ không khớp.",
      path: ["overview", "branches", "inventory", "reports"],
      links: [["overview", "Tổng quan điều hành toàn mạng lưới."], ["inventory", "SKU/lô và đề nghị của chi nhánh."], ["reports", "Báo cáo theo đúng branch và period."], ["reconciliation", "Sai lệch ca và chứng từ đối soát."]]
    },
    inventory: {
      illustration: "inventory", caption: "Ledger + reservation + quarantine → khả dụng theo SKU/location/lot.",
      summary: "Sổ tồn tính lượng khả dụng theo từng lô; từ ngoại lệ người dùng có thể mở đề nghị mua, kiểm kê hoặc điều chuyển. Trang không tự ghi tăng/giảm tồn.",
      owner: "Inventory Control; branch warehouse xác nhận đếm và tình trạng lô.",
      data: ["Khóa: tenantId + branchId + locationId + skuId + lotId.", "available = onHand − reserved − quarantined.", "Đọc ledgerVersion, unitOfMeasure, expiryAt và snapshotAt.", "Giao dịch tiếp theo là requisition, count variance hoặc transfer."],
      guard: "Chặn số âm và khác đơn vị; snapshot cũ cần refresh trước khi phát sinh yêu cầu.",
      path: ["branches", "inventory", "procurement", "approvals", "receiving"],
      links: [["branches", "Đổi scope hoặc xem owner của cơ sở."], ["procurement", "Tạo requisition từ đề xuất bổ sung."], ["adjustments", "Kiểm kê, recount và variance."], ["transfers", "Xin chuyển từ cơ sở đang dư."], ["receiving", "Đối chiếu receipt trước khi tăng tồn."]]
    },
    procurement: {
      illustration: "procurement", caption: "Tồn → requisition → quote/vendor → checker → PO draft.",
      summary: "Requisition tổng hợp nhu cầu nhưng chưa phải đơn mua. Người lập đính kèm lý do và báo giá; hệ thống kiểm tồn/version, vendor, ngân sách và ma trận duyệt trước PO draft.",
      owner: "Supply Operations lập; checker theo hạn mức; Finance xác nhận ngân sách.",
      data: ["Nguồn: availability, reorder target, open PO và vendor catalog.", "Bản ghi: requisitionId, branchId, item lines, quoteRef, amount/currency.", "Duyệt theo amount + category + branch scope.", "Kết quả duyệt là PO draft liên kết vendor và giá có version."],
      guard: "Không tạo mua trùng open PO; quote hết hạn, vendor bị giữ hoặc maker tự duyệt thì chặn.",
      path: ["inventory", "procurement", "suppliers", "approvals", "receiving"],
      links: [["inventory", "Kiểm tra lại tồn và lượng đang đặt."], ["suppliers", "Xác minh hồ sơ, hợp đồng và điều khoản."], ["approvals", "Gửi checker độc lập theo hạn mức."], ["receiving", "Theo PO đã duyệt tới phiếu nhận."]]
    },
    suppliers: {
      illustration: "suppliers", caption: "Hồ sơ vendor → hiệu lực → điều kiện giao dịch → requisition/PO.",
      summary: "Supplier master cấp điều kiện giao hàng và thanh toán cho mua hàng. Hồ sơ hết hạn hoặc thay đổi tài khoản đi qua hàng đợi xác minh; dữ liệu demo không phải bằng chứng KYC.",
      owner: "Vendor Management; Finance xác minh điều khoản và tài khoản thanh toán.",
      data: ["Khóa supplierId; version hồ sơ, status, validFrom/validTo.", "Nguồn gồm hợp đồng, chứng từ, lead-time và quotation.", "Đầu ra là điều kiện giao dịch theo branch/category.", "Thay đổi nhạy cảm có actor, reviewer, reason và evidenceRef."],
      guard: "Hết hạn/thiếu chứng từ hoặc tài khoản chưa checker thì vendor không đủ điều kiện cho PO.",
      path: ["procurement", "suppliers", "approvals", "receiving"],
      links: [["procurement", "Requisition và báo giá tham chiếu vendor."], ["approvals", "Checker review hồ sơ hoặc tài khoản."], ["receiving", "Đối chiếu hàng giao theo PO."], ["audit", "Truy dấu thay đổi hồ sơ."]]
    },
    receiving: {
      illustration: "receiving", caption: "PO ↔ phiếu nhận ↔ invoice: three-way match trước khi post.",
      summary: "Phiếu nhận ghi số đếm, tình trạng, lô và bằng chứng; đối chiếu PO với hóa đơn theo từng dòng. Sai lệch được cách ly để checker xử lý trước khi cập nhật tồn/công nợ.",
      owner: "Nhân viên kho lập GRN; quản lý kho xác nhận; Finance xử lý invoice match.",
      data: ["Tham chiếu PO line, GRN line, invoice line, SKU, lot và expiry.", "So orderedQty, receivedQty, acceptedQty và invoiceQty.", "Phân loại matched, shortage, overage, damage hoặc invoice variance.", "Tồn tăng sau receipt duyệt và ledger event idempotent."],
      guard: "Không nhận vượt tolerance; thiếu evidence hoặc unit sai thì dừng; variance không tự tạo công nợ.",
      path: ["procurement", "receiving", "inventory", "finance", "reconciliation"],
      links: [["procurement", "Truy về requisition/PO và báo giá."], ["inventory", "Xem lot sau khi receipt được duyệt."], ["finance", "Theo dõi khoản phải trả liên quan."], ["reconciliation", "Xử lý lệch PO/GRN/invoice."]]
    },
    transfers: {
      illustration: "transfers", caption: "Kho nguồn → dispatch → in-transit → xác nhận kho đích.",
      summary: "Điều chuyển tạo chuỗi chứng từ giữa hai branch. Hàng xuất rời tồn khả dụng nguồn nhưng chỉ vào tồn đích sau xác nhận; trạng thái in-transit là một bucket riêng.",
      owner: "Quản lý kho nguồn và kho đích; vận hành vùng theo dõi ETA.",
      data: ["Khóa transferId + sourceBranch + destinationBranch + lineId.", "Lưu requested, reserved, dispatched, received và damaged quantities.", "Dispatch/receive có actor, timestamp, lot và evidenceRef.", "Nhận đủ ghi movement nối hai branch."],
      guard: "Không cho nguồn trùng đích, over-dispatch, nhận vượt số đang chuyển hoặc xử lý event hai lần.",
      path: ["inventory", "transfers", "adjustments", "inventory"],
      links: [["inventory", "Kiểm tra khả dụng tại nguồn và đích."], ["branches", "Xác nhận hai cơ sở cùng tenant/scope."], ["adjustments", "Ghi variance thiếu/hỏng sau checker."], ["audit", "Ai dispatch/nhận và bằng chứng nào."]]
    },
    adjustments: {
      illustration: "adjustments", caption: "Count → variance → recount → checker → ledger movement.",
      summary: "Kiểm kê chụp ledger version, ghi số đếm và evidence; variance phải có giải trình, recount khi vượt ngưỡng và checker độc lập trước khi post movement.",
      owner: "Inventory Control lập count; branch manager đếm; approver độc lập duyệt.",
      data: ["ExpectedQty và ledgerVersion tại thời điểm mở count.", "Ghi countedQty, unit, reasonCode, evidenceRef và counter.", "variance = countedQty − expectedQty; recount theo tolerance.", "Sau khi duyệt, ghi movement idempotent và giữ before/after."],
      guard: "Nếu ledger đổi giữa count và approve thì tính lại; maker không tự duyệt và count gửi đi không bị xóa.",
      path: ["inventory", "adjustments", "approvals", "audit"],
      links: [["inventory", "Sổ tồn và ledger version ban đầu."], ["approvals", "Gửi variance lớn cho checker."], ["audit", "Evidence, reason và actor của lần đếm."], ["transfers", "Kiểm tra hàng đang chuyển có giải thích chênh lệch."]]
    },
    approvals: {
      illustration: "approvals", caption: "Request version → quyền/hạn mức/evidence → checker decision → event.",
      summary: "Checker review request bất biến theo version rồi approve/reject/return kèm reason. Thay đổi sau khi gửi phải tạo revision mới và chạy lại các cổng duyệt.",
      owner: "Approver theo role/amount/branch matrix; data owner xử lý bổ sung.",
      data: ["requestId, resourceVersion, makerId, approverId và policyVersion.", "Sắp hàng theo SLA, rủi ro và deadline.", "Decision có reason, timestamp, evidenceRef và before/after.", "Approve phát event cho luồng tiếp theo, không bỏ qua downstream."],
      guard: "Deny khi maker = checker, quyền sai scope, request stale hoặc thiếu evidence.",
      path: ["procurement", "approvals", "receiving", "finance", "audit"],
      links: [["procurement", "Request mua cần quyết định."], ["suppliers", "Hồ sơ vendor nhạy cảm."], ["adjustments", "Variance kiểm kê chờ duyệt."], ["finance", "Close/variance sau phê duyệt."], ["audit", "Quyết định và lý do checker."]]
    },
    finance: {
      illustration: "finance", caption: "Branch/period close → kiểm chứng từ → resolve exception → lock.",
      summary: "Finance close tổng hợp receipt, invoice, settlement, credit note và ledger theo kỳ. Sai lệch giữ kỳ open; lock cần checklist hoàn tất và phê duyệt có audit.",
      owner: "Finance Controller; người lập kỳ khác người duyệt lock.",
      data: ["Khóa kỳ: tenantId + branchId + period + currency.", "Đọc GRN/PO/invoice, payout và journal reference; không lưu dữ liệu thẻ.", "Tổng hợp matched, pending, variance và freshness.", "Lock phát closeVersion; sửa sau lock qua adjustment kỳ tiếp theo."],
      guard: "Không đóng nếu source stale, exception chưa owner hoặc variance vượt tolerance.",
      path: ["receiving", "finance", "reconciliation", "reports"],
      links: [["receiving", "GRN/invoice chưa match."], ["reconciliation", "Sai lệch theo source và amount."], ["approvals", "Close/variance theo ma trận quyền."], ["reports", "Tổng hợp đã lock cùng kỳ."]]
    },
    reconciliation: {
      illustration: "reconciliation", caption: "Ghép reference → phân loại unmatched → owner/SLA → resolve.",
      summary: "Workbench khớp các source theo reference, amount, currency và thời gian. Mỗi ngoại lệ có owner/SLA; trang không sửa dữ liệu nguồn hoặc tự xác nhận settlement.",
      owner: "Reconciliation Analyst xử lý; Finance Controller xác nhận kết quả cuối.",
      data: ["Nguồn: PO/GRN/invoice, settlement/payout và ledger reference.", "Ghép exact key trước; tolerance chỉ theo policy.", "Case giữ sourceVersion, matched fields, variance và resolution evidence.", "Event đóng case idempotent, lưu mapping giữa hai source."],
      guard: "Thiếu source/freshness hoặc currency mismatch thì không tự match; duplicate reference cần điều tra.",
      path: ["receiving", "finance", "reconciliation", "reports", "audit"],
      links: [["finance", "Period close và số tổng hợp."], ["receiving", "Chứng từ PO/GRN/invoice liên quan."], ["integrations", "Lag/retry của nguồn còn thiếu."], ["audit", "Resolve event và evidence."]]
    },
    reports: {
      illustration: "reports", caption: "KPI có định nghĩa → snapshot/coverage → drill-down về nghiệp vụ nguồn.",
      summary: "Báo cáo so sánh chi nhánh và xu hướng với formula, đơn vị, timezone và kỳ rõ ràng. Drill-down giữ filter context; bản xuất trong prototype chỉ là mô phỏng.",
      owner: "Business Analyst và domain owner xác nhận định nghĩa/chất lượng KPI.",
      data: ["Dimensions: tenant, branch, period, channel/category theo quyền.", "Metric có formulaVersion, currency, aggregation và freshness.", "Drill-down giữ filter đến branches, inventory hoặc finance.", "Export kèm generatedAt, coverage và disclaimer."],
      guard: "Không so sánh snapshot stale/thiếu coverage hoặc metric khác timezone/công thức.",
      path: ["branches", "reports", "inventory", "finance"],
      links: [["branches", "Hồ sơ cơ sở được chọn."], ["inventory", "SKU ảnh hưởng KPI tồn."], ["finance", "KPI tài chính đối chiếu kỳ."], ["overview", "Trở về control tower."]]
    },
    audit: {
      illustration: "audit", caption: "Actor + entity/version + policy + reason + correlation/evidence.",
      summary: "Audit trail là append-only log cho thay đổi, quyết định và tích hợp. Tìm theo actor/entity/correlationId để truy từ request tới kết quả, không phơi bày PII.",
      owner: "Compliance/Audit; domain owner chỉ đọc theo quyền/scope.",
      data: ["eventId, actorId/role, action, entityId, before/after hash và reason.", "Gắn correlationId, requestVersion, policyVersion, timestamp và source.", "Evidence là reference có kiểm soát, không nhúng secret/PII.", "Retention/export theo policy; lần đọc audit cũng được ghi nhận."],
      guard: "Không sửa/xóa event gốc; thiếu actor hoặc reason cho hành động nhạy cảm là lỗi kiểm soát.",
      path: ["approvals", "audit", "settings", "integrations"],
      links: [["approvals", "Decision và checker chịu trách nhiệm."], ["settings", "Policy/version có hiệu lực lúc đó."], ["integrations", "Correlation qua outbox/retry."], ["adjustments", "Count và variance liên quan."]]
    },
    integrations: {
      illustration: "integrations", caption: "Producer → contract/schema → scope → outbox → retry/DLQ.",
      summary: "Connector health hiển thị producer/consumer, contract, freshness, retry và DLQ. Event chỉ được nhận khi tenant scope, schema version và idempotency key hợp lệ.",
      owner: "Integration Operations phối hợp data owner từng domain/source.",
      data: ["connectorId, producer/consumer, schemaVersion và contract owner.", "Theo dõi lastSuccessAt, lag, retryCount, DLQ và correlationId.", "Outbox pin event version; consumer ack idempotent.", "Thay đổi quyền/purpose có thể revoke consumer."],
      guard: "Schema lạ, tenant mismatch hoặc contract hết hiệu lực phải cách ly; retry có giới hạn.",
      path: ["settings", "integrations", "reconciliation", "audit"],
      links: [["settings", "Contract owner, scope và SLA."], ["reconciliation", "Case do source lag/missing."], ["audit", "Tra event theo correlationId/retry."], ["finance", "Feed settlement sau xác minh nguồn."]]
    },
    settings: {
      illustration: "settings", caption: "Change request → schema/bounds → dry-run → checker → hiệu lực.",
      summary: "Cấu hình tổ chức quản lý branch scope, reorder/variance, hạn mức duyệt, SLA và connector. Thay đổi được version hóa, kiểm tra bằng fixtures rồi checker duyệt trước khi có hiệu lực.",
      owner: "System Administrator đề xuất; domain/security owner review; approver độc lập publish.",
      data: ["configKey, scope, value, owner, rationale và validFrom/validTo.", "ConfigVersion được gắn với request và audit event.", "Dry-run so ảnh hưởng trên fixtures branch/category.", "Rollback trỏ tới last-known-good version."],
      guard: "Chặn giá trị ngoài schema, owner thiếu hoặc maker tự duyệt; không ghi đè version cũ.",
      path: ["audit", "settings", "integrations", "approvals"],
      links: [["audit", "Ai đổi policy/version và lý do."], ["integrations", "Contract, SLA và connector owner."], ["approvals", "Gửi config change cho checker."], ["overview", "Theo dõi tác động trên control tower."]]
    }
  };

  const field = (name, label, type, value, options = {}) => ({ name, label, type, value, ...options });
  const algorithmEngines = {
    priority: {
      name: "Xếp ưu tiên có giải thích",
      fields: [field("urgency", "Mức khẩn cấp (1–3)", "number", 2, { min: 1, max: 3, step: 1 }), field("impact", "Mức ảnh hưởng (1–3)", "number", 2, { min: 1, max: 3, step: 1 }), field("ageHours", "Thời gian chờ (giờ)", "number", 6, { min: 0, max: 720, step: 1 })],
      calculate: (v) => {
        const score = Math.min(100, v.urgency * 35 + v.impact * 25 + Math.min(v.ageHours, 12) * 2);
        return { status: score >= 75 ? "Ưu tiên cao" : score >= 45 ? "Theo dõi" : "Bình thường", tone: score >= 75 ? "red" : score >= 45 ? "gold" : "green", summary: `Điểm ưu tiên ${score}/100; sắp xếp theo điểm giảm dần, sau đó theo hạn gần nhất.`, calculation: `${v.urgency}×35 + ${v.impact}×25 + min(${v.ageHours},12)×2 = ${score}` };
      }
    },
    quality: {
      name: "Cổng chất lượng dữ liệu",
      fields: [field("required", "Trường bắt buộc", "number", 10, { min: 1, max: 500, step: 1 }), field("complete", "Trường hợp lệ", "number", 9, { min: 0, max: 500, step: 1 }), field("ageHours", "Độ trễ dữ liệu (giờ)", "number", 2, { min: 0, max: 8760, step: 1 }), field("maxAgeHours", "Độ trễ tối đa", "number", 24, { min: 1, max: 8760, step: 1 })],
      calculate: (v) => {
        if (v.complete > v.required) throw new Error("Số trường hợp lệ không thể lớn hơn tổng trường bắt buộc.");
        const score = Math.round(v.complete / v.required * 100);
        const fresh = v.ageHours <= v.maxAgeHours;
        const pass = score >= 80 && fresh;
        return { status: pass ? "Đạt cổng dữ liệu" : "Chặn để rà soát", tone: pass ? "green" : "red", summary: `Độ đầy đủ ${score}%; ${fresh ? "độ mới đạt" : "dữ liệu quá cũ"}.`, calculation: `${v.complete}/${v.required}×100 = ${score}%; freshness ${v.ageHours}h ≤ ${v.maxAgeHours}h: ${fresh ? "đạt" : "không đạt"}` };
      }
    },
    inventory: {
      name: "Tính khả dụng & đề xuất bổ sung",
      fields: [field("onHand", "Tồn ghi nhận", "number", 24, { min: 0, max: 1000000, step: 1 }), field("reserved", "Đã giữ chỗ", "number", 5, { min: 0, max: 1000000, step: 1 }), field("quarantined", "Cách ly / hỏng", "number", 1, { min: 0, max: 1000000, step: 1 }), field("reorderPoint", "Mức tồn mục tiêu", "number", 12, { min: 0, max: 1000000, step: 1 })],
      calculate: (v) => {
        if (v.reserved + v.quarantined > v.onHand) throw new Error("Tồn giữ chỗ và cách ly không thể vượt tồn ghi nhận.");
        const available = v.onHand - v.reserved - v.quarantined;
        const reorder = Math.max(0, v.reorderPoint - available);
        return { status: reorder ? "Cần đề xuất bổ sung" : "Tồn khả dụng đạt ngưỡng", tone: reorder ? "gold" : "green", summary: `Khả dụng ${available}; đề xuất bổ sung ${reorder} đơn vị để đạt ngưỡng.`, calculation: `${v.onHand} − ${v.reserved} − ${v.quarantined} = ${available}; max(0, ${v.reorderPoint} − ${available}) = ${reorder}` };
      }
    },
    capacity: {
      name: "Kiểm tra công suất",
      fields: [field("demand", "Nhu cầu đã đặt (phút/đơn vị)", "number", 420, { min: 0, max: 100000, step: 1 }), field("capacity", "Năng lực khả dụng", "number", 600, { min: 1, max: 100000, step: 1 }), field("buffer", "Buffer / bảo trì", "number", 30, { min: 0, max: 100000, step: 1 })],
      calculate: (v) => {
        if (v.buffer > v.capacity) throw new Error("Buffer không thể lớn hơn tổng năng lực khả dụng.");
        const available = v.capacity - v.buffer;
        const utilization = Math.round(v.demand / available * 100);
        return { status: utilization > 100 ? "Vượt công suất" : utilization >= 90 ? "Gần đầy" : "Còn năng lực", tone: utilization > 100 ? "red" : utilization >= 90 ? "gold" : "green", summary: `Mức sử dụng ${utilization}%; còn ${Math.max(0, available - v.demand)} đơn vị năng lực.`, calculation: `${v.demand}/(${v.capacity}−${v.buffer})×100 = ${utilization}%` };
      }
    },
    schedule: {
      name: "Kiểm tra khung lịch",
      fields: [field("start", "Bắt đầu (phút từ giờ mở cửa)", "number", 120, { min: 0, max: 1440, step: 5 }), field("duration", "Thời lượng", "number", 75, { min: 5, max: 1440, step: 5 }), field("buffer", "Buffer sau lượt", "number", 15, { min: 0, max: 480, step: 5 }), field("close", "Đóng cửa (phút từ giờ mở)", "number", 600, { min: 0, max: 1440, step: 5 })],
      calculate: (v) => {
        const finish = v.start + v.duration + v.buffer;
        const fits = finish <= v.close;
        return { status: fits ? "Khung giờ phù hợp" : "Vượt giờ hoạt động", tone: fits ? "green" : "red", summary: `Kết thúc có buffer ở phút ${finish}; giờ đóng cửa phút ${v.close}.`, calculation: `${v.start} + ${v.duration} + ${v.buffer} = ${finish}; ${fits ? "≤" : ">"} ${v.close}` };
      }
    },
    reconcile: {
      name: "Đối soát sai lệch",
      fields: [field("expected", "Giá trị nguồn A", "number", 100, { min: -1000000000, max: 1000000000, step: 0.01 }), field("actual", "Giá trị nguồn B", "number", 100.5, { min: -1000000000, max: 1000000000, step: 0.01 }), field("tolerance", "Ngưỡng sai lệch cho phép", "number", 1, { min: 0, max: 1000000, step: 0.01 })],
      calculate: (v) => {
        const delta = Math.round((v.actual - v.expected) * 100) / 100;
        const matched = Math.abs(delta) <= v.tolerance;
        return { status: matched ? "Khớp trong ngưỡng" : "Cần đối soát thủ công", tone: matched ? "green" : "red", summary: `Sai lệch ${delta}; ${matched ? "đạt tolerance" : "vượt tolerance"}, không tự ghi bút toán.`, calculation: `${v.actual} − ${v.expected} = ${delta}; |${delta}| ${matched ? "≤" : ">"} ${v.tolerance}` };
      }
    },
    consent: {
      name: "Kiểm tra consent và phạm vi",
      fields: [field("requestedScope", "Phạm vi được yêu cầu", "select", "profile-min", { options: [["profile-min", "Hồ sơ tối thiểu"], ["health-summary", "Tóm tắt sức khỏe"], ["coarse-location", "Vị trí gần đúng"], ["aggregate", "Dữ liệu tổng hợp"]] }), field("grantedScope", "Phạm vi đã cấp", "select", "profile-min", { options: [["profile-min", "Hồ sơ tối thiểu"], ["health-summary", "Tóm tắt sức khỏe"], ["coarse-location", "Vị trí gần đúng"], ["aggregate", "Dữ liệu tổng hợp"]] }), field("hoursRemaining", "Thời gian consent còn hiệu lực (giờ)", "number", 24, { min: 0, max: 8760, step: 1 }), field("minValidityHours", "Thời hạn tối thiểu cần có", "number", 1, { min: 0, max: 720, step: 1 })],
      calculate: (v) => {
        const scopeMatch = v.requestedScope === v.grantedScope;
        const active = v.hoursRemaining > 0 && v.hoursRemaining >= v.minValidityHours;
        const allowed = scopeMatch && active;
        return { status: allowed ? "Cho phép theo scope mẫu" : "Từ chối mặc định", tone: allowed ? "green" : "red", summary: `${scopeMatch ? "Scope khớp" : "Scope không khớp"}; consent ${active ? "còn hiệu lực" : "hết hạn/không đủ thời hạn"}.`, calculation: `requested=${v.requestedScope}; granted=${v.grantedScope}; ${v.hoursRemaining}h ${active ? "≥" : "<"} ${v.minValidityHours}h` };
      }
    },
    approval: {
      name: "Cổng maker–checker",
      fields: [field("maker", "Người lập", "select", "operator-a", { options: [["operator-a", "Nhân sự A"], ["operator-b", "Nhân sự B"]] }), field("checker", "Người duyệt", "select", "operator-b", { options: [["operator-a", "Nhân sự A"], ["operator-b", "Nhân sự B"]] }), field("amount", "Giá trị cần duyệt", "number", 500000, { min: 0, max: 1000000000, step: 1000 }), field("threshold", "Ngưỡng bắt buộc duyệt", "number", 100000, { min: 0, max: 1000000000, step: 1000 })],
      calculate: (v) => {
        const separated = v.maker !== v.checker;
        const approvalRequired = v.amount >= v.threshold;
        const allowed = separated && (!approvalRequired || v.checker !== v.maker);
        return { status: allowed ? approvalRequired ? "Đạt cổng duyệt độc lập" : "Dưới ngưỡng duyệt" : "Chặn: vi phạm phân tách", tone: allowed ? "green" : "red", summary: `Người lập ${v.maker}; checker ${v.checker}; ${approvalRequired ? "cần checker độc lập" : "dưới ngưỡng"}.`, calculation: `${v.amount} ${approvalRequired ? "≥" : "<"} ${v.threshold}; maker≠checker: ${separated ? "đúng" : "sai"}` };
      }
    },
    sla: {
      name: "Phân loại SLA",
      fields: [field("elapsed", "Thời gian đã trôi qua (giờ)", "number", 3, { min: 0, max: 87600, step: 0.25 }), field("limit", "SLA mục tiêu (giờ)", "number", 4, { min: 0.25, max: 87600, step: 0.25 }), field("openItems", "Số hạng mục còn mở", "number", 1, { min: 0, max: 100000, step: 1 })],
      calculate: (v) => {
        const overdue = v.openItems > 0 && v.elapsed > v.limit;
        const dueSoon = v.openItems > 0 && !overdue && v.elapsed >= v.limit * 0.8;
        return { status: overdue ? "Quá SLA · cần escalation" : dueSoon ? "Sắp đến hạn" : v.openItems ? "Trong SLA" : "Đã đóng", tone: overdue ? "red" : dueSoon ? "gold" : "green", summary: `${v.openItems} mục mở; đã dùng ${Math.round(v.elapsed / v.limit * 100)}% ngân sách SLA.`, calculation: `elapsed=${v.elapsed}h; limit=${v.limit}h; open=${v.openItems}` };
      }
    },
    aggregate: {
      name: "Tổng hợp KPI có mẫu số",
      fields: [field("eligible", "Số bản ghi đủ điều kiện", "number", 100, { min: 0, max: 10000000, step: 1 }), field("completed", "Số hoàn tất / đạt", "number", 78, { min: 0, max: 10000000, step: 1 }), field("cohort", "Quy mô cohort", "number", 100, { min: 0, max: 10000000, step: 1 }), field("minCohort", "Ngưỡng ẩn cohort nhỏ", "number", 10, { min: 1, max: 10000000, step: 1 })],
      calculate: (v) => {
        if (v.completed > v.eligible) throw new Error("Số hoàn tất không thể lớn hơn số bản ghi đủ điều kiện.");
        const rate = v.eligible ? Math.round(v.completed / v.eligible * 1000) / 10 : null;
        const suppressed = v.cohort < v.minCohort;
        return { status: suppressed ? "Ẩn cohort nhỏ" : rate === null ? "Không đủ mẫu số" : "KPI tổng hợp", tone: suppressed || rate === null ? "gold" : "green", summary: suppressed ? `Cohort ${v.cohort} thấp hơn ngưỡng ${v.minCohort}; không công bố tỷ lệ.` : `Tỷ lệ ${rate === null ? "N/A" : `${rate}%`} trên ${v.eligible} bản ghi đủ điều kiện.`, calculation: `${v.completed}/${v.eligible || "0"}×100 = ${rate === null ? "N/A" : `${rate}%`}; cohort=${v.cohort}, k=${v.minCohort}` };
      }
    },
    lineage: {
      name: "Kiểm tra schema và lineage",
      fields: [field("expected", "Số trường / nút dự kiến", "number", 12, { min: 1, max: 100000, step: 1 }), field("verified", "Đã ánh xạ/xác minh", "number", 11, { min: 0, max: 100000, step: 1 }), field("unmapped", "Trường chưa ánh xạ", "number", 1, { min: 0, max: 100000, step: 1 }), field("minimum", "Ngưỡng coverage (%)", "number", 95, { min: 0, max: 100, step: 1 })],
      calculate: (v) => {
        if (v.verified > v.expected || v.unmapped > v.expected) throw new Error("Giá trị đã xác minh/chưa ánh xạ không thể vượt tổng dự kiến.");
        const coverage = Math.round(v.verified / v.expected * 1000) / 10;
        const pass = coverage >= v.minimum && v.unmapped === 0;
        return { status: pass ? "Contract đạt kiểm tra" : "Chặn ingest / cần map", tone: pass ? "green" : "red", summary: `Coverage ${coverage}%; còn ${v.unmapped} trường chưa ánh xạ.`, calculation: `${v.verified}/${v.expected}×100 = ${coverage}%; ${coverage} ≥ ${v.minimum} AND unmapped=0` };
      }
    },
    risk: {
      name: "Sàng lọc rủi ro để reviewer",
      fields: [field("severity", "Mức độ (1–5)", "number", 3, { min: 1, max: 5, step: 1 }), field("exposure", "Mức phơi nhiễm (1–5)", "number", 3, { min: 1, max: 5, step: 1 }), field("evidence", "Bằng chứng hợp lệ (%)", "number", 80, { min: 0, max: 100, step: 1 }), field("threshold", "Ngưỡng chuyển review", "number", 60, { min: 0, max: 100, step: 1 })],
      calculate: (v) => {
        const score = Math.min(100, v.severity * 10 + v.exposure * 8 + (100 - v.evidence) * 0.2);
        const review = score >= v.threshold || v.evidence < 50;
        return { status: review ? "Chuyển reviewer" : "Theo dõi thường lệ", tone: review ? "gold" : "green", summary: `Điểm sàng lọc ${score}/100; ${v.evidence < 50 ? "bằng chứng còn yếu" : "đã xét mức bằng chứng"}. Không phải quyết định cuối.`, calculation: `${v.severity}×10 + ${v.exposure}×8 + (100−${v.evidence})×0.2 = ${score}; threshold=${v.threshold}` };
      }
    },
    release: {
      name: "Cổng phát hành nhiều điều kiện",
      fields: [field("consent", "Consent / purpose", "select", "pass", { options: [["pass", "Đạt"], ["fail", "Chưa đạt"]] }), field("evaluation", "Đánh giá độc lập", "select", "pass", { options: [["pass", "Đạt"], ["fail", "Chưa đạt"]] }), field("approval", "Owner / reviewer approval", "select", "pass", { options: [["pass", "Đạt"], ["fail", "Chưa đạt"]] }), field("monitoring", "Giám sát & rollback", "select", "pass", { options: [["pass", "Đạt"], ["fail", "Chưa đạt"]] })],
      calculate: (v) => {
        const gates = [v.consent, v.evaluation, v.approval, v.monitoring];
        const pass = gates.every((value) => value === "pass");
        return { status: pass ? "Đủ điều kiện shadow/canary" : "NO-GO · giữ trạng thái hiện tại", tone: pass ? "green" : "red", summary: `${gates.filter((value) => value === "pass").length}/4 cổng đạt; thuật toán chỉ tạo quyết định đề xuất.`, calculation: `consent ∧ evaluation ∧ approval ∧ monitoring = ${pass ? "true" : "false"}` };
      }
    },
    rollback: {
      name: "Ngưỡng rollback có fallback",
      fields: [field("errorRate", "Tỷ lệ lỗi hiện tại (%)", "number", 4, { min: 0, max: 100, step: 0.1 }), field("maxError", "Ngưỡng lỗi tối đa (%)", "number", 2, { min: 0, max: 100, step: 0.1 }), field("fallback", "Quy trình thủ công sẵn sàng", "select", "yes", { options: [["yes", "Có"], ["no", "Chưa có"]] }), field("lastKnownGood", "Bản ổn định trước đã xác minh", "select", "yes", { options: [["yes", "Có"], ["no", "Chưa có"]] })],
      calculate: (v) => {
        const trigger = v.errorRate > v.maxError;
        const ready = v.fallback === "yes" && v.lastKnownGood === "yes";
        return { status: trigger ? ready ? "Đề xuất rollback" : "Đóng băng · thiếu điều kiện an toàn" : "Tiếp tục giám sát", tone: trigger ? "red" : "green", summary: `${trigger ? "Vượt ngưỡng lỗi" : "Trong ngưỡng"}; fallback ${v.fallback === "yes" ? "sẵn sàng" : "chưa sẵn sàng"}. Thực thi cần người duyệt.`, calculation: `${v.errorRate}% ${trigger ? ">" : "≤"} ${v.maxError}%; rollback target verified=${v.lastKnownGood}` };
      }
    },
    config: {
      name: "Kiểm tra cấu hình trước áp dụng",
      fields: [field("owner", "Data/process owner", "select", "yes", { options: [["yes", "Đã xác nhận"], ["no", "Thiếu owner"]] }), field("reviewer", "Reviewer độc lập", "select", "yes", { options: [["yes", "Đã duyệt"], ["no", "Chưa duyệt"]] }), field("tests", "Bộ test cấu hình", "select", "yes", { options: [["yes", "Đạt"], ["no", "Lỗi"]] }), field("dryRunErrors", "Lỗi trong dry-run", "number", 0, { min: 0, max: 100000, step: 1 })],
      calculate: (v) => {
        const pass = v.owner === "yes" && v.reviewer === "yes" && v.tests === "yes" && v.dryRunErrors === 0;
        return { status: pass ? "Sẵn sàng tạo version" : "Không áp dụng cấu hình", tone: pass ? "green" : "red", summary: `${pass ? "Đủ owner, reviewer và test" : "Thiếu ít nhất một cổng"}; không tự áp dụng cấu hình.`, calculation: `owner ∧ reviewer ∧ tests ∧ (dryRunErrors=0) = ${pass}` };
      }
    }
  };

  const slug = document.body.dataset.demo;
  const data = systems[slug];
  const mount = document.getElementById("demoApp");
  if (!data || !mount) return;

  const icons = ["◫", "◷", "⌂", "♡", "▱", "▥", "◉", "⌖", "✳"];
  const esc = (value) => String(value).replace(/[&<>"']/g, (char) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  })[char]);
  const tag = (label, tone = "") => `<span class="tag ${tone}">${esc(label)}</span>`;
  const pageModules = pageCatalog[slug];
  const pageKey = document.body.dataset.demoPage || "overview";
  const pageModule = pageModules.find(([key]) => key === pageKey) || pageModules[0];
  if (slug === "pet-business" || slug === "pet-care" || slug === "pet-intelligence"
    || slug === "pet-service" || slug === "pet-health" || slug === "pet-connect"
    || slug === "pet-community" || slug === "pet-commerce") {
    document.title = `WAGGY ${data.name} · ${pageModule[1]}`;
    const description = document.querySelector('meta[name="description"]');
    if (description) description.content = `${pageModule[1]}: ${pageModule[2]} Dữ liệu minh họa trong sandbox ${data.name}.`;
  }
  const domainPlaybook = systemPlaybooks[slug];
  const pageSpec = domainPlaybook.pages[pageKey];
  const algorithm = slug === "pet-business" || slug === "pet-care"
    ? window[slug === "pet-business" ? "PetBusinessAlgorithms" : "PetCareAlgorithms"]?.get(pageKey)
    : pageSpec && algorithmEngines[pageSpec.engine];
  if (!pageSpec || !algorithm) {
    throw new Error(`Thiếu workflow/thuật toán cho màn hình ${slug}/${pageKey}.`);
  }
  const storageKey = `waggy-system-demo-${slug}-v1`;
  const seedRecords = data.rows.map((row, index) => {
    const cells = row.map((cell) => Array.isArray(cell) ? cell.filter(Boolean).join(" · ") : String(cell));
    return {
      id: cells[0] || `SAMPLE-${index + 1}`,
      name: cells[1] || "Bản ghi mẫu",
      details: cells.slice(2, -1).join(" · ") || data.name,
      status: cells[cells.length - 1] || "Mẫu",
      source: "seed"
    };
  });
  const isValidBusinessProcess = (process) =>
    process && typeof process.id === "string" && typeof process.title === "string" &&
    typeof process.sourcePage === "string" && typeof process.sourceLabel === "string" &&
    Array.isArray(process.steps) && process.steps.length >= 2 &&
    process.steps[0] === process.sourcePage &&
    process.steps.every((step) => pageModules.some(([route]) => route === step)) &&
    Number.isInteger(process.stageIndex) && process.stageIndex >= 0 && process.stageIndex <= process.steps.length &&
    typeof process.createdAt === "string" && Number.isFinite(Date.parse(process.createdAt));
  let systemState = { schemaVersion: 2, records: seedRecords, audit: [], simulations: [], businessProcesses: [] };
  let storageAvailable = true;
  let storageNotice = "";
  try {
    const storedState = localStorage.getItem(storageKey);
    if (storedState) {
      const parsedState = JSON.parse(storedState);
      if (![1, 2].includes(parsedState.schemaVersion) || !Array.isArray(parsedState.records) || !Array.isArray(parsedState.audit) ||
          (parsedState.schemaVersion === 2 && (!Array.isArray(parsedState.businessProcesses) || !parsedState.businessProcesses.every(isValidBusinessProcess)))) {
        throw new Error("Phiên bản dữ liệu của hệ thống không hợp lệ.");
      }
      systemState = {
        ...parsedState,
        schemaVersion: 2,
        simulations: Array.isArray(parsedState.simulations) ? parsedState.simulations : [],
        businessProcesses: Array.isArray(parsedState.businessProcesses) ? parsedState.businessProcesses : []
      };
      if (parsedState.schemaVersion === 1) localStorage.setItem(storageKey, JSON.stringify(systemState));
    } else {
      localStorage.setItem(storageKey, JSON.stringify(systemState));
    }
  } catch (error) {
    storageAvailable = false;
    storageNotice = `Không thể đọc hoặc khởi tạo dữ liệu lưu cục bộ (${error.message}). Dữ liệu hiện chỉ tồn tại trong tab này.`;
  }
  const saveSystemState = (auditMessage) => {
    systemState.audit.unshift({ id: `LOG-${Date.now()}`, message: auditMessage, at: new Date().toISOString() });
    systemState.audit = systemState.audit.slice(0, 50);
    if (!storageAvailable) return false;
    try {
      localStorage.setItem(storageKey, JSON.stringify(systemState));
      return true;
    } catch (error) {
      storageAvailable = false;
      storageNotice = `Không thể lưu dữ liệu demo (${error.message}). Thay đổi chỉ còn trong tab này.`;
      return false;
    }
  };
  const renderStoredRecords = () => systemState.records.map((record) => `
    <tr data-row data-search="${esc(`${record.id} ${record.name} ${record.details} ${record.status}`.toLocaleLowerCase("vi"))}">
      <td><strong>${esc(record.id)}</strong><small>${record.source === "seed" ? "Dữ liệu mẫu" : "Đã lưu trong hệ thống demo"}</small></td>
      <td>${esc(record.name)}</td><td>${esc(record.details)}</td><td>${tag(record.status, record.source === "seed" ? "blue" : "green")}</td>
    </tr>`).join("");
  const renderAuditRows = () => systemState.audit.map((entry) => `
    <div class="list-item"><div class="list-copy"><strong>${esc(entry.message)}</strong><span>${new Date(entry.at).toLocaleString("vi-VN")}</span></div><div class="list-meta">${tag("Đã ghi", "blue")}</div></div>`).join("");
  const renderSimulationHistory = () => systemState.simulations
    .filter((run) => run.system === slug && run.page === pageKey)
    .slice(0, 5)
    .map((run) => `<div class="list-item"><div class="list-copy"><strong>${esc(run.status)} · ${esc(run.summary)}</strong><span>${new Date(run.at).toLocaleString("vi-VN")} · ${esc(run.calculation)}</span></div><div class="list-meta">${tag("Mô phỏng", "blue")}</div></div>`).join("");
  const businessProcessFlows = slug === "pet-business" ? window.PetBusinessConfig?.workflows : null;
  if (slug === "pet-business" && (!businessProcessFlows || !businessProcessFlows[pageKey])) {
    throw new Error(`Thiếu pet-business-config.js hoặc workflow cho màn hình "${pageKey}".`);
  }
  const renderBusinessProcesses = () => {
    const pageLookup = new Map(pageModules.map(([key, label]) => [key, label]));
    return systemState.businessProcesses.slice(0, 10).map((process) => {
      const activePage = process.steps[process.stageIndex];
      const completed = process.stageIndex >= process.steps.length;
      const stageLabel = completed ? "Hoàn tất" : `${pageLookup.get(activePage) || activePage} · bước ${process.stageIndex + 1}/${process.steps.length}`;
      const action = completed
        ? `<span class="tag green">Đã hoàn tất</span>`
        : activePage === pageKey
          ? `<button class="business-process-advance" type="button" data-workflow-advance="${esc(process.id)}">Xác nhận bước này</button>`
          : `<a class="business-process-open" href="${activePage === "overview" ? "index.html" : esc(activePage) + ".html"}">Mở ${esc(pageLookup.get(activePage) || activePage)} ↗</a>`;
      return `<tr data-row data-workflow-row data-search="${esc(`${process.id} ${process.title} ${process.sourceLabel} ${stageLabel}`.toLocaleLowerCase("vi"))}"><td><strong>${esc(process.id)}</strong><small>${esc(process.sourceLabel)}</small></td><td><strong>${esc(process.title)}</strong><small>${new Date(process.createdAt).toLocaleString("vi-VN")}</small></td><td>${tag(stageLabel, completed ? "green" : "gold")}</td><td>${action}</td></tr>`;
    }).join("");
  };
  const businessProcessPanel = slug === "pet-business" ? `<section class="panel-card business-process-panel" aria-labelledby="business-process-title">
    <div class="panel-head"><div><span class="workspace-kicker">CROSS-SCREEN WORKFLOW · LOCAL DEMO</span><h2 id="business-process-title">Quy trình liên kết giữa các màn hình</h2><p>Tạo hồ sơ demo tại một trang, mở bước kế tiếp ở trang đích và xác nhận thủ công. Trạng thái được lưu riêng cho Pet Business trên trình duyệt này.</p></div><span class="tag blue" data-business-process-count>${systemState.businessProcesses.filter((process) => process.stageIndex < process.steps.length).length} đang mở</span></div>
    ${pageKey === "overview" ? `<div class="business-process-starts"><button type="button" class="business-process-start" data-business-process-start="inventory"><strong>Bổ sung hàng</strong><span>Tồn → mua → duyệt → nhận → Finance</span></button><button type="button" class="business-process-start" data-business-process-start="transfers"><strong>Điều chuyển</strong><span>Dispatch → xác minh → duyệt → ledger</span></button><button type="button" class="business-process-start" data-business-process-start="adjustments"><strong>Kiểm kê</strong><span>Count → checker → audit → tồn</span></button><button type="button" class="business-process-start" data-business-process-start="reconciliation"><strong>Đóng kỳ / đối soát</strong><span>Reconcile → Finance → báo cáo → audit</span></button></div>` : ""}
    <div class="table-wrap"><table class="data-table business-process-table"><thead><tr><th>Mã / nguồn</th><th>Hồ sơ demo</th><th>Bước hiện tại</th><th>Điều hướng / xác nhận</th></tr></thead><tbody data-business-process-rows>${renderBusinessProcesses()}</tbody></table></div>
    <p class="empty-state business-process-empty" ${systemState.businessProcesses.length ? 'style="display:none"' : ""}>Chưa có quy trình demo. Tạo một luồng ở Control tower hoặc dùng thao tác chính của trang để bắt đầu.</p>
  </section>` : "";
  const renderAlgorithmResult = (result, simulated = false) => `
    <div class="algorithm-result-heading"><div><span>KẾT QUẢ ${simulated ? "TÍNH THỬ" : "VỚI THAM SỐ MẪU"}</span><strong>${esc(result.status)}</strong></div>${tag(simulated ? "Không ghi nghiệp vụ" : "Mẫu minh họa", result.tone)}</div>
    <p>${esc(result.summary)}</p><code>${esc(result.calculation)}</code>`;
  const initialAlgorithmValues = Object.fromEntries(algorithm.fields.map((item) => [item.name, item.value]));
  const initialAlgorithmResult = algorithm.calculate(initialAlgorithmValues);
  const algorithmInputs = algorithm.fields.map((item) => {
    if (item.type === "select") {
      return `<label>${esc(item.label)}<select name="${esc(item.name)}" required>${item.options.map(([value, label]) => `<option value="${esc(value)}" ${value === item.value ? "selected" : ""}>${esc(label)}</option>`).join("")}</select></label>`;
    }
    return `<label>${esc(item.label)}<input type="number" name="${esc(item.name)}" value="${esc(item.value)}" min="${esc(item.min)}" max="${esc(item.max)}" step="${esc(item.step)}" required></label>`;
  }).join("");
  const workspace = {
    "pet-care": {
      kind: "care",
      eyebrow: "BẢNG ĐIỀU HÀNH CHĂM SÓC",
      title: "Hồ sơ liên kết & việc cần làm",
      lead: "Một góc nhìn theo thú cưng, nối nhiệm vụ chăm sóc với lịch và cảnh báo từ các phân hệ.",
      content: `<div class="care-profile"><div class="pet-avatar" aria-hidden="true">🐈</div><div class="care-profile-main"><span class="workspace-kicker">HỒ SƠ THÚ CƯNG · PET-1001</span><h3>Bông</h3><p>Mèo tam thể · 4 tuổi · Chủ nuôi Nguyễn An</p><div class="care-profile-tags"><span>Hồ sơ đang hoạt động</span><span>Đã liên kết chủ nuôi</span></div></div><div class="care-profile-side"><small>LẦN CẬP NHẬT GẦN NHẤT</small><strong>Hôm nay · 08:42</strong><span>Phạm vi xem theo vai trò</span><button class="workspace-action" type="button" data-action="Mở hồ sơ PET-1001" data-description="Hồ sơ chủ nuôi và thú cưng chỉ mở trong ứng dụng thật theo quyền được cấp. Đây là bản ghi demo.">Xem hồ sơ mẫu →</button></div></div>
        <div class="workspace-bottom-grid"><div class="workspace-inset"><div class="workspace-subhead"><strong>Việc chăm sóc trong ngày</strong><span>3 mục mẫu</span></div><div class="task-line"><i class="task-check done">✓</i><span><b>Kiểm tra hồ sơ &amp; lịch</b><small>08:30 · Nhân viên chăm sóc</small></span><em>Hoàn tất</em></div><div class="task-line"><i class="task-check">2</i><span><b>Nhắc lịch dịch vụ</b><small>09:00 · Xác nhận với chủ nuôi</small></span><em class="warn">Đến hạn</em></div><div class="task-line"><i class="task-check">3</i><span><b>Rà soát tồn sản phẩm</b><small>Kho cửa hàng · chỉ đọc</small></span><em class="warn">Cần xem</em></div></div><div class="workspace-inset care-domain"><div class="workspace-subhead"><strong>Phân hệ liên quan</strong><span>Điều hướng mẫu</span></div><div class="domain-grid"><span>♥ <b>Sức khỏe</b><small>Hồ sơ khám</small></span><span>◷ <b>Dịch vụ</b><small>Lịch hẹn</small></span><span>▱ <b>Bán hàng</b><small>Đơn &amp; hóa đơn</small></span><span>▥ <b>Tồn kho</b><small>Lô &amp; hạn dùng</small></span></div></div></div>`
    },
    "pet-service": {
      kind: "service",
      eyebrow: "SERVICE DESK · CA SÁNG",
      title: "Điều phối lịch & công suất",
      lead: "Theo dõi luồng tiếp nhận–thực hiện–bàn giao cùng năng lực nhân viên và tài nguyên theo giờ.",
      content: `<div class="service-summary"><div><span class="workspace-kicker">CƠ SỞ TRUNG TÂM</span><strong>Thứ Năm · 15 tháng 10</strong><small>24 lịch · 5 lượt chờ check-in</small></div><div class="capacity-ring"><span>82<small>%</small></span></div><div class="capacity-copy"><b>Công suất đã xếp</b><span>17 / 21 slot trong ca</span><i><u style="width:82%"></u></i><small>2 bàn grooming · 1 phòng spa · khu lưu trú còn 2 chỗ</small></div></div>
        <div class="service-timeline"><div class="timeline-head"><strong>Lịch theo thời gian</strong><button class="workspace-action" type="button" data-action="Mở lịch điều phối" data-description="Lịch minh họa hiển thị tài nguyên và nhân viên; thao tác không giữ slot hoặc thay đổi booking thật.">Mở lịch đầy đủ →</button></div><div class="timeline-track"><div class="timeline-now"><span>09:30</span><i></i></div><div class="timeline-row"><time>09:00</time><div class="timeline-slot checked"><b>Bông · Tắm &amp; sấy</b><span>Linh · Bàn grooming 01</span><small>Đã check-in · bàn giao đầu vào</small></div></div><div class="timeline-row"><time>09:30</time><div class="timeline-slot running"><b>Milo · Grooming tiêu chuẩn</b><span>Quân · Bàn grooming 02</span><small>Đang thực hiện · 45 / 90 phút</small></div></div><div class="timeline-row"><time>10:00</time><div class="timeline-slot waiting"><b>Đậu · Lưu trú 2 đêm</b><span>Ca trực A · Khu A</span><small>Chờ check-in · còn 2 chỗ</small></div></div><div class="timeline-row"><time>10:30</time><div class="timeline-slot confirm"><b>Nâu · Spa da lông</b><span>Hà · Phòng spa 02</span><small>Cần xác nhận ghi chú trước khi nhận</small></div></div></div></div>`
    },
    "pet-health": {
      kind: "health",
      eyebrow: "CLINICAL WORKSPACE · HUMAN REVIEW REQUIRED",
      title: "Hàng đợi chuyên môn & cổng an toàn",
      lead: "Tách trạng thái tiếp nhận, xét nghiệm và phê duyệt hồ sơ; nội dung lâm sàng chỉ do người đủ thẩm quyền xử lý.",
      content: `<div class="health-guard"><span class="guard-icon">+</span><div><strong>Kiểm soát phát hành hồ sơ</strong><p>Chưa có chẩn đoán/kết quả nào được xác nhận tự động. Cần xác thực danh tính, consent và chữ ký chuyên môn.</p></div><span class="guard-state">3 cổng bắt buộc</span></div>
        <div class="health-flow"><div class="health-stage done"><span>01</span><b>Tiếp nhận</b><small>5 lượt hôm nay</small></div><i></i><div class="health-stage active"><span>02</span><b>Khám / chỉ định</b><small>4 lượt đang mở</small></div><i></i><div class="health-stage review"><span>03</span><b>Kết quả &amp; duyệt</b><small>7 cần reviewer</small></div><i></i><div class="health-stage"><span>04</span><b>Phát hành</b><small>Chờ chữ ký</small></div></div>
        <div class="health-review-grid"><div class="workspace-inset"><div class="workspace-subhead"><strong>Ưu tiên rà soát</strong><span>Không phải kết luận y tế</span></div><div class="review-row"><span class="review-priority high">!</span><span><b>LAB-0281 · Kết quả xét nghiệm</b><small>Thiếu bước xác thực bác sĩ · Clinic A</small></span><span class="review-age">12 phút</span></div><div class="review-row"><span class="review-priority medium">↗</span><span><b>ENC-1048 · Hồ sơ encounter</b><small>Thiếu chữ ký phát hành</small></span><span class="review-age">34 phút</span></div><div class="review-row"><span class="review-priority consent">⌁</span><span><b>CNS-0332 · Consent chia sẻ</b><small>Quyền truy cập hết hạn lúc 16:00</small></span><span class="review-age">Theo dõi</span></div></div><div class="health-privacy"><small>PHẠM VI &amp; RIÊNG TƯ</small><strong>Clinic A · tenant riêng</strong><span>Consent còn hiệu lực: 8</span><span>Yêu cầu truy cập cần duyệt: 2</span><button class="workspace-action" type="button" data-action="Kiểm tra consent" data-description="Mở checklist mô phỏng về mục đích, phạm vi clinic và thời hạn truy cập.">Rà soát quyền truy cập →</button></div></div>`
    },
    "pet-commerce": {
      kind: "commerce",
      eyebrow: "COMMERCE OPERATIONS · ORDER TO DELIVERY",
      title: "Luồng đơn hàng & thực hiện",
      lead: "Theo dõi riêng vòng đời đơn, xác minh thanh toán, phân bổ tồn và vận chuyển để tránh đóng đơn sai trạng thái.",
      content: `<div class="commerce-funnel"><div class="funnel-head"><div><span class="workspace-kicker">ORDER PIPELINE</span><strong>86 đơn trong ngày</strong></div><span>So sánh trạng thái ở từng cổng</span></div><div class="commerce-stages"><div class="commerce-stage"><span>01</span><b>Đơn mới</b><strong>86</strong><small>12 chờ xác nhận</small><i style="--fill:100%"></i></div><div class="commerce-stage"><span>02</span><b>Payment verify</b><strong>82</strong><small>4 cần đối soát</small><i style="--fill:82%"></i></div><div class="commerce-stage alert"><span>03</span><b>Phân bổ kho</b><strong>67</strong><small>3 SKU thiếu khả dụng</small><i style="--fill:69%"></i></div><div class="commerce-stage"><span>04</span><b>Đóng gói / giao</b><strong>48</strong><small>11 đang vận chuyển</small><i style="--fill:52%"></i></div></div></div>
        <div class="commerce-lower"><div class="workspace-inset"><div class="workspace-subhead"><strong>Đơn cần thao tác tiếp theo</strong><span>Thứ tự theo cổng</span></div><div class="order-card"><span class="order-id">WG-24079</span><div><b>Combo chăm sóc × 1</b><small>Đà Nẵng · thanh toán đang đối soát</small></div><span class="order-badge wait">VERIFY</span></div><div class="order-card"><span class="order-id">WG-24081</span><div><b>Thức ăn mèo 2kg × 2</b><small>Hà Nội · đã xác minh · chờ lấy hàng</small></div><span class="order-badge pack">PICK</span></div></div><div class="commerce-return"><span class="workspace-kicker">REVERSE LOGISTICS</span><strong>06 <small>case đổi trả mở</small></strong><p>2 yêu cầu chờ duyệt tình trạng hàng; không tạo lệnh hoàn tiền tự động.</p><button class="workspace-action" type="button" data-action="Mở hàng đợi đổi trả" data-description="Xem luồng RMA mô phỏng, gồm kiểm tra order line, tình trạng hàng và phê duyệt hoàn tiền.">Mở hàng đợi RMA →</button></div></div>`
    },
    "pet-business": {
      kind: "business",
      eyebrow: "MULTI-BRANCH CONTROL TOWER",
      title: "Sức khỏe chi nhánh & hàng đợi phê duyệt",
      lead: "Một góc nhìn điều hành chuỗi; phân tách người lập, người duyệt và người đối soát theo chi nhánh.",
      content: `<div class="branch-grid"><article class="branch-card"><div><span class="branch-code">HN-01</span><span class="branch-health good">ỔN ĐỊNH</span></div><h3>WAGGY Hà Nội</h3><strong>₫42,8tr</strong><small>Doanh thu mẫu · 18 đơn</small><div class="branch-stock"><span>Hoàn thành kế hoạch</span><b>82%</b><i><u style="width:82%"></u></i></div></article><article class="branch-card"><div><span class="branch-code">HCM-02</span><span class="branch-health watch">THEO DÕI</span></div><h3>WAGGY Thủ Đức</h3><strong>₫36,1tr</strong><small>Doanh thu mẫu · 14 đơn</small><div class="branch-stock"><span>Hoàn thành kế hoạch</span><b>74%</b><i><u style="width:74%"></u></i></div></article><article class="branch-card"><div><span class="branch-code">DN-01</span><span class="branch-health risk">CẦN XỬ LÝ</span></div><h3>WAGGY Đà Nẵng</h3><strong>₫21,4tr</strong><small>₫120.000 lệch quỹ ca sáng</small><div class="branch-stock"><span>Đối soát ca</span><b>Chờ duyệt</b><i><u style="width:48%"></u></i></div></article></div>
        <div class="approval-rail"><div class="workspace-subhead"><strong>Maker–checker · Hàng đợi kiểm soát</strong><button class="workspace-action" type="button" data-action="Mở hàng đợi phê duyệt" data-description="Quy trình đề xuất tách người lập và người duyệt. Không có đề nghị mua hoặc số liệu kế toán thật.">Mở hàng đợi →</button></div><div class="approval-item"><span class="approval-step">01</span><div><b>PO-0084 · Đề nghị mua 32 SKU</b><small>Người lập: Ngọc Phạm · HN-01</small></div><span class="approval-status">Chờ quản lý</span></div><div class="approval-item"><span class="approval-step">02</span><div><b>STK-0141 · Lệch kiểm kê 4 dòng</b><small>Người xác minh: Tuấn Lê · HCM-02</small></div><span class="approval-status urgent">Cần xác minh</span></div><div class="approval-item"><span class="approval-step">03</span><div><b>CSH-0061 · Đóng ca / lệch quỹ</b><small>Ca sáng · chi nhánh Đà Nẵng</small></div><span class="approval-status">Chưa khóa kỳ</span></div></div>`
    },
    "pet-community": {
      kind: "community",
      eyebrow: "TRUST & SAFETY · MODERATION DESK",
      title: "Hàng đợi an toàn cộng đồng",
      lead: "Xếp loại báo cáo, bằng chứng và quyết định moderation; kháng nghị được chuyển reviewer độc lập.",
      content: `<div class="moderation-overview"><div class="moderation-total"><span class="workspace-kicker">OPEN REVIEW QUEUE</span><strong>14 <small>bài chờ</small></strong><p>5 ưu tiên cao · 9 báo cáo đang mở</p></div><div class="moderation-sla"><div><span>Trong SLA</span><b>78%</b></div><i><u style="width:78%"></u></i><small>Thời gian mục tiêu theo policy demo</small></div><div class="moderation-mix"><span>Spam <b>63</b></span><span>Riêng tư <b>31</b></span><span>Y tế <b>49</b></span><span>Quấy rối <b>25</b></span></div></div>
        <div class="moderation-board"><div class="workspace-subhead"><strong>Case cần quyết định</strong><span>Ưu tiên · thời hạn · reviewer</span></div><article class="mod-case urgent"><span class="mod-kind">RIÊNG TƯ</span><div><b>MOD-0412 · Bài đăng trong nhóm mèo</b><p>Ảnh có thể lộ thông tin liên hệ · bằng chứng đã che dữ liệu nhạy cảm</p><small>Ưu tiên cao · 12 phút trong hàng đợi</small></div><button class="workspace-action" type="button" data-action="Rà soát case MOD-0412" data-description="Mở quy trình mô phỏng xem policy hiện hành, bằng chứng đã lọc và lưu lý do quyết định.">Mở review →</button></article><article class="mod-case"><span class="mod-kind health-kind">Y TẾ</span><div><b>MOD-0411 · Bình luận tư vấn sức khỏe</b><p>Nội dung chưa kiểm chứng · cần reviewer có chuyên môn policy</p><small>Đang xử lý · chờ phản hồi</small></div><button class="workspace-action" type="button" data-action="Chuyển reviewer" data-description="Mô phỏng chuyển case sang reviewer độc lập; không ẩn/xóa nội dung thật.">Chuyển reviewer →</button></article><article class="mod-case appeal"><span class="mod-kind appeal-kind">KHÁNG NGHỊ</span><div><b>APL-0032 · Yêu cầu xem lại quyết định</b><p>Không giao lại cho moderator đưa ra quyết định ban đầu</p><small>Reviewer độc lập · SLA còn 3 giờ</small></div><button class="workspace-action" type="button" data-action="Mở kháng nghị APL-0032" data-description="Kiểm tra lịch sử quyết định và phân công reviewer độc lập theo quy tắc demo.">Xem kháng nghị →</button></article></div>`
    },
    "pet-connect": {
      kind: "connect",
      eyebrow: "FIELD RESPONSE · PRIVACY-SAFE CASE DESK",
      title: "Điều phối cứu hộ & xác minh đoàn tụ",
      lead: "Xem khu vực gần đúng và tiến độ hỗ trợ; địa chỉ, liên hệ và bằng chứng chi tiết không hiển thị trong bảng công khai.",
      content: `<div class="connect-command"><div class="safe-map" role="img" aria-label="Minh họa sơ đồ khu vực gần đúng, không phải bản đồ hoặc vị trí thực"><div class="map-grid"></div><span class="map-area area-one">CẦU GIẤY</span><span class="map-area area-two">BA ĐÌNH</span><span class="map-route"></span><span class="map-pin pin-one">⌖</span><span class="map-pin pin-two">+</span><span class="map-privacy">VỊ TRÍ ĐÃ LÀM MỜ · DEMO</span></div><div class="connect-case"><span class="workspace-kicker">CASE ƯU TIÊN · PC-24052</span><h3>Yêu cầu hỗ trợ động vật</h3><p>Mèo · khu vực Hải Châu, Đà Nẵng<br>Thông tin vị trí hiển thị gần đúng</p><div class="case-response"><span>01 · Tiếp nhận</span><b>Hoàn tất</b></div><div class="case-response"><span>02 · Điều phối</span><b>Đã nhận bởi đối tác</b></div><div class="case-response current"><span>03 · Bàn giao</span><b>Đang chờ xác nhận</b></div><button class="workspace-action" type="button" data-action="Xem hồ sơ case PC-24052" data-description="Màn hình case demo chỉ hiển thị dữ liệu được phép; vị trí chính xác và thông tin liên lạc được ẩn theo quyền.">Mở case an toàn →</button></div></div>
        <div class="responder-strip"><div><span class="responder-avatar">C</span><span><b>Nhóm cứu hộ miền Trung</b><small>Đã xác minh · 1/2 chỗ tạm</small></span><em>ĐANG TRỰC</em></div><div><span class="responder-avatar clinic">V</span><span><b>Phòng khám đối tác</b><small>Năng lực sơ cứu · lịch trực mẫu</small></span><em>ĐÃ DUYỆT</em></div><div><span class="responder-avatar foster">N</span><span><b>Nhà tạm lánh cộng đồng</b><small>Nhận chó nhỏ · cần đặt trước</small></span><em>CÒN 1 CHỖ</em></div></div>`
    },
    "pet-intelligence": {
      kind: "intelligence",
      eyebrow: "DATA GOVERNANCE · HUMAN-APPROVED INTELLIGENCE",
      title: "Lineage dữ liệu & cổng phát hành",
      lead: "Từ use-case đến monitoring có thể truy vết; không khuyến nghị nào được tự động ghi nghiệp vụ.",
      content: `<div class="governance-banner"><span>GATE 03 / 05</span><div><b>AI-0104 · Phân tích nhu cầu tồn kho</b><small>Owner: Retail · chế độ shadow · quyết định phát hành đang chờ</small></div><span class="governance-state">CHƯA PHÁT HÀNH</span></div>
        <div class="lineage-flow"><article><span class="lineage-icon source">DB</span><b>Nguồn được duyệt</b><small>Business · aggregate</small><em>Tenant scope: branch</em></article><i class="lineage-arrow">→</i><article><span class="lineage-icon quality">✓</span><b>Kiểm định dữ liệu</b><small>Schema v2 · freshness 94%</small><em>PII scan: passed</em></article><i class="lineage-arrow">→</i><article class="lineage-review"><span class="lineage-icon review">H</span><b>Human review</b><small>Data owner · 1 chữ ký còn thiếu</small><em>Go / no-go required</em></article><i class="lineage-arrow">→</i><article><span class="lineage-icon monitor">◎</span><b>Monitoring</b><small>Drift · bias · freshness</small><em>Rollback: ready</em></article></div>
        <div class="governance-foot"><div><span class="governance-meter"><i style="width:86%"></i></span><span>Chất lượng bộ dữ liệu <b>86 / 100</b></span></div><p>Điểm dưới ngưỡng, thiếu consent hoặc thiếu owner sẽ chặn phát hành và chuyển sang quy trình thủ công.</p><button class="workspace-action" type="button" data-action="Mở hồ sơ đánh giá AI-0104" data-description="Xem checklist dữ liệu, lineage, đánh giá độc lập, human approval và kế hoạch rollback ở trạng thái demo.">Mở checklist governance →</button></div>`
    }
  }[slug];
  const workflowPanel = `<section class="workflow-focus ${workspace.kind}" aria-labelledby="workflow-focus-title"><div class="workflow-focus-head"><div><span class="workspace-kicker">${workspace.eyebrow}</span><h2 id="workflow-focus-title">${workspace.title}</h2><p>${workspace.lead}</p></div><span class="focus-live"><i></i> DỮ LIỆU MẪU</span></div>${workspace.content}</section>`;
  const metrics = data.metrics.map(([label, value, foot], index) => `
    <article class="metric-card"><div class="metric-top"><span>${esc(label)}</span><span>${icons[index + 1]}</span></div>
      <div class="metric-value">${esc(value)}</div><div class="metric-foot">${esc(foot)}</div></article>`).join("");
  const rows = data.rows.map((row) => {
    const search = row.map((cell) => Array.isArray(cell) ? cell.join(" ") : cell).join(" ");
    return `<tr data-row data-search="${esc(search.toLowerCase())}">${row.map((cell) => {
      if (Array.isArray(cell) && cell.length > 2 && String(cell[2]).startsWith("tag")) {
        return `<td>${tag(cell[0], cell[2].replace("tag", "").trim())}</td>`;
      }
      if (Array.isArray(cell)) return `<td><span class="primary-cell">${esc(cell[0])}</span>${cell[1] ? `<span class="secondary-cell">${esc(cell[1])}</span>` : ""}</td>`;
      return `<td>${esc(cell)}</td>`;
    }).join("")}</tr>`;
  }).join("");
  const columns = data.columns.map((column) => `<th scope="col">${esc(column)}</th>`).join("");
  const items = data.items.map(([title, body, meta, tone]) => `
    <div class="list-item"><div class="list-copy"><strong>${esc(title)}</strong><span>${esc(body)}</span></div><div class="list-meta">${tag(meta, tone)}</div></div>`).join("");
  const bars = data.chart.map(([label, value]) => `
    <div class="chart-col"><i class="chart-bar" style="height:${Math.max(6, Math.min(100, Number(value)))}%"></i><span>${esc(label)}</span></div>`).join("");
  const actions = data.actions.map(([title, description]) => `
    <button class="quick-action" type="button" data-action="${esc(title)}" data-description="${esc(description)}"><strong>${esc(title)} <span aria-hidden="true">↗</span></strong><span>${esc(description)}</span></button>`).join("");
  const inSystemFolder = document.body.dataset.systemFolder === "true";
  const demoRoot = inSystemFolder ? "../" : "";
  const syncRoot = inSystemFolder ? "../../" : "";
  const workflowRoot = inSystemFolder ? "../../../" : "../";
  const productRoot = inSystemFolder ? "../../../../" : "../../";
  const routeHref = (key) => key === "overview" ? "index.html" : `${key}.html`;
  const allNavLinks = pageModules.map(([key, label], index) => `
    <a href="${routeHref(key)}" class="${pageKey === key ? "active" : ""}" data-nav><span class="nav-icon">${icons[index % icons.length]}</span>${esc(label)}</a>`).join("");
  const nav = `${pageModules.slice(0, 6).map(([key, label], index) => `
    <a href="${routeHref(key)}" class="${pageKey === key ? "active" : ""}" data-nav><span class="nav-icon">${icons[index % icons.length]}</span>${esc(label)}</a>`).join("")}
    <details class="system-more-nav"><summary>Thêm màn hình (${pageModules.length - 6})</summary><div>${pageModules.slice(6).map(([key, label], index) => `
      <a href="${routeHref(key)}" class="${pageKey === key ? "active" : ""}" data-nav><span class="nav-icon">${icons[(index + 6) % icons.length]}</span>${esc(label)}</a>`).join("")}</div></details>`;
  const workspaceLinks = `
    <a href="${workflowRoot}${slug}.html" target="_blank" rel="noopener">Workflow ↗</a>
    <a href="${productRoot}integration/${slug}.html" target="_blank" rel="noopener">Tích hợp ↗</a>
    <a href="${syncRoot}sync.html?system=${slug}" target="_blank" rel="noopener">Dữ liệu chung ↗</a>
    ${slug === "pet-business" ? `<a href="design.html">Thiết kế hệ thống ↗</a>` : ""}`;
  const pageHeading = `<section class="page-heading"><div><div class="crumb">WAGGY / ${esc(data.name.toUpperCase())} / ${esc(pageModule[1].toUpperCase())}</div><h1>${esc(pageModule[1])}</h1><p>${esc(pageModule[2])}</p></div><div class="heading-actions">${slug === "pet-business" ? `<a class="button" href="design.html">Bản thiết kế ↗</a>` : ""}<button class="button" type="button" data-action="Xuất dữ liệu" data-description="Chức năng xuất dữ liệu chỉ là minh họa và không tạo tệp.">Xuất báo cáo</button><a class="button primary" href="#system-record-form">＋ Ghi nhận demo</a></div></section>`;
  const demoBanner = `<div class="demo-banner"><span aria-hidden="true">ⓘ</span><div><strong>${esc(data.status)}</strong> · ${esc(data.description)}</div></div>`;
  const workflowSteps = pageSpec.workflow.split("→").map((step, index) => `
    <li><span>${String(index + 1).padStart(2, "0")}</span><div><strong>${esc(step.trim())}</strong><small>${index === 0 ? "Nhận dữ liệu theo đúng phạm vi" : index === pageSpec.workflow.split("→").length - 1 ? "Ghi kết quả, owner và dấu vết kiểm toán" : "Kiểm soát trước khi chuyển bước"}</small></div></li>`).join("");
  const pageDetailsPanel = `<section class="page-spec-grid" aria-label="Đặc tả nghiệp vụ ${esc(pageModule[1])}">
    <article class="panel-card page-workflow-spec"><div class="panel-head"><div><span class="workspace-kicker">WORKFLOW · ${esc(data.name.toUpperCase())}</span><h2>Luồng xử lý chi tiết</h2><p>Mỗi chuyển trạng thái phải có actor, thời điểm, phiên bản và lý do tương ứng.</p></div><span class="tag blue">${pageSpec.workflow.split("→").length} bước</span></div><ol class="workflow-step-list">${workflowSteps}</ol><div class="spec-note"><strong>Vai trò chịu trách nhiệm</strong><p>${esc(domainPlaybook.owner)}</p></div></article>
    <div class="page-spec-side"><article class="panel-card algorithm-spec-card"><div class="panel-head"><div><span class="workspace-kicker">LOGIC · EXPLAINABLE</span><h2>${esc(algorithm.name)}</h2></div><span class="tag gold">Quy tắc demo</span></div><p>${esc(pageSpec.algorithm)}</p><div class="formula-block"><small>CÔNG THỨC / ĐIỀU KIỆN</small><code>${esc(pageSpec.formula)}</code></div><dl class="spec-terms"><div><dt>Dữ liệu đầu vào</dt><dd>${esc(pageSpec.inputs)}</dd></div><div><dt>Điều kiện chặn / ngoại lệ</dt><dd>${esc(pageSpec.guard)}</dd></div></dl></article>
      <article class="panel-card data-contract-card"><div class="panel-head"><div><span class="workspace-kicker">DATA CONTRACT</span><h2>Phạm vi dữ liệu &amp; điểm kết nối</h2></div></div><dl class="spec-terms"><div><dt>Trường chuẩn của miền</dt><dd>${esc(domainPlaybook.dataContract)}</dd></div><div><dt>Luồng tích hợp</dt><dd>${esc(domainPlaybook.integration)}</dd></div></dl><div class="callout-card"><strong>Giới hạn:</strong> ${esc(domainPlaybook.boundary)}</div></article>
    </div>
  </section>`;
  const algorithmPanel = `<section class="panel-card algorithm-lab" aria-labelledby="algorithm-lab-title"><div class="panel-head"><div><span class="workspace-kicker">INTERACTIVE SANDBOX · ${esc(pageModule[0].toUpperCase())}</span><h2 id="algorithm-lab-title">Chạy thử thuật toán của màn hình</h2><p>Công thức bên trên là của riêng trang này. Thay tham số để kiểm tra nhánh đạt/chặn; mọi kết quả chỉ lưu trong sandbox của ${esc(data.name)}.</p></div><span class="tag">${esc(algorithm.name)}</span></div><form class="algorithm-inputs" data-algorithm-form>${algorithmInputs}<button class="button primary" type="submit">Tính toán &amp; ghi audit demo</button></form><div class="algorithm-result" id="algorithm-result" role="status" aria-live="polite">${renderAlgorithmResult(initialAlgorithmResult)}</div><div class="algorithm-history"><div class="workspace-subhead"><strong>Lần chạy gần đây của trang này</strong><span>Giữ tối đa 5 kết quả hiển thị</span></div><div class="list-stack" id="algorithm-history">${renderSimulationHistory() || `<p class="empty-state">Chưa có lần chạy nào được lưu cho màn hình này.</p>`}</div></div><p class="algorithm-disclaimer">Kết quả không tạo booking, chẩn đoán, giao dịch, quyết định moderation hay phát hành model. Ngưỡng mặc định chỉ minh họa và phải được domain owner xác nhận trước khi dùng thực tế.</p></section>`;
  const tablePanel = `<article class="panel-card data-workbench"><div class="panel-head"><div><h2>${esc(data.tableTitle)}</h2><p>${esc(data.tableHint)}</p></div><a class="text-link" href="#quick-actions">Thao tác nhanh ↓</a></div><div class="toolbar" aria-label="Lọc danh sách"><button class="filter-chip active" type="button" data-filter="all">Tất cả</button><button class="filter-chip" type="button" data-filter="open">Đang mở</button><button class="filter-chip" type="button" data-filter="attention">Cần xử lý</button><span class="text-link">Mẫu · ${data.rows.length} dòng</span></div><div class="table-wrap"><table class="data-table"><thead><tr>${columns}</tr></thead><tbody>${rows}</tbody></table></div><div class="empty-state">Không tìm thấy dòng phù hợp với bộ lọc.</div></article>`;
  const insightPanel = `<div class="insight-stack"><article class="panel-card"><div class="panel-head"><div><h2>${esc(data.listTitle)}</h2><p>${esc(data.listHint)}</p></div><a class="text-link" href="#quick-actions">Xem tất cả</a></div><div class="list-stack">${items}</div></article><article class="panel-card chart-card"><div class="panel-head"><div><h2>${esc(data.chartTitle)}</h2><p>${esc(data.chartHint)}</p></div></div><div class="chart" role="img" aria-label="${esc(data.chartTitle)}">${bars}</div></article></div>`;
  const systemRecordsPanel = `<section class="panel-card system-record-panel"><div class="panel-head"><div><h2>${esc(pageModule[1])} · dữ liệu dùng chung</h2><p>Các bản ghi và cập nhật này được dùng xuyên suốt 15 màn hình của riêng ${esc(data.name)}.</p></div><span class="tag blue">${systemState.records.length} bản ghi</span></div><form class="system-record-form" id="system-record-form" data-system-record-form><label>Tên bản ghi<input name="name" required maxlength="80" placeholder="Ví dụ: Hồ sơ Bông / yêu cầu dịch vụ"></label><label>Chi tiết<input name="details" maxlength="160" placeholder="Mô tả, mã liên kết hoặc ghi chú"></label><label>Trạng thái<select name="status"><option>Mới tạo</option><option>Đang xử lý</option><option>Chờ rà soát</option><option>Hoàn tất</option></select></label><button class="button primary" type="submit">Lưu vào dữ liệu demo</button></form></section>`;
  const sharedRecordsTable = `<article class="panel-card"><div class="panel-head"><div><h2>Bản ghi dùng chung trong hệ thống</h2><p>Khóa dữ liệu riêng: ${esc(data.name)} · không dùng chung với 7 bộ demo còn lại.</p></div><span class="tag blue">${systemState.records.length} bản ghi</span></div><div class="table-wrap"><table class="data-table"><thead><tr><th>Mã</th><th>Tên</th><th>Chi tiết liên kết</th><th>Trạng thái</th></tr></thead><tbody id="system-record-rows">${renderStoredRecords()}</tbody></table></div></article>`;
  const auditPanel = `<article class="panel-card system-audit-panel"><div class="panel-head"><div><h2>Nhật ký đồng bộ nội bộ</h2><p>Thay đổi trên bộ dữ liệu riêng của ${esc(data.name)}.</p></div><span class="tag">${systemState.audit.length} sự kiện</span></div><div class="list-stack" id="system-audit-rows">${renderAuditRows() || `<p class="empty-state">Chưa có thao tác mới trong phiên demo.</p>`}</div></article>`;
  const businessLayout = slug === "pet-business" ? businessScreens[pageKey] : null;
  const businessJourney = slug === "pet-business" ? businessJourneys[pageKey] : null;
  const businessJourneyPanel = businessJourney ? (() => {
    const flow = businessJourney.path.map((key) => {
      const module = pageModules.find(([route]) => route === key);
      if (!module) throw new Error(`Unknown Pet Business route in journey: ${key}`);
      return key === pageKey
        ? `<li class="business-journey-step current" aria-current="page"><span>${esc(module[1])}</span></li>`
        : `<li class="business-journey-step"><a href="${routeHref(key)}"><span>${esc(module[1])}</span><i aria-hidden="true">↗</i></a></li>`;
    }).join("");
    const related = businessJourney.links.map(([key, description]) => {
      const module = pageModules.find(([route]) => route === key);
      if (!module) throw new Error(`Unknown Pet Business related route: ${key}`);
      return `<a class="business-related-link" href="${routeHref(key)}"><span class="business-related-icon" aria-hidden="true">↗</span><span><strong>${esc(module[1])}</strong><small>${esc(description)}</small></span></a>`;
    }).join("");
    return `<section class="business-journey-panel" aria-labelledby="business-journey-title">
      <div class="business-journey-heading"><div><span class="workspace-kicker">BUSINESS JOURNEY · DATA FLOW</span><h2 id="business-journey-title">Nội dung nghiệp vụ &amp; liên kết quy trình</h2><p>${esc(businessJourney.summary)}</p></div><span class="tag blue">${esc(pageModule[1])} · workflow</span></div>
      <div class="business-journey-main"><figure class="business-journey-art"><svg viewBox="0 0 420 210" role="img" aria-labelledby="business-art-title business-art-description"><title id="business-art-title">${esc(pageModule[1])} · minh họa nghiệp vụ</title><desc id="business-art-description">${esc(businessJourney.caption)}</desc><use href="../../assets/pet-business-illustrations.svg#${esc(businessJourney.illustration)}"></use></svg><figcaption>${esc(businessJourney.caption)}</figcaption></figure>
        <div class="business-journey-facts"><div><small>PROCESS OWNER</small><strong>${esc(businessJourney.owner)}</strong></div><div><small>BUSINESS RULE / SAFE GUARD</small><p>${esc(businessJourney.guard)}</p></div></div></div>
      <div class="business-journey-data-grid">${businessJourney.data.map((item, index) => `<article><span>${String(index + 1).padStart(2, "0")}</span><p>${esc(item)}</p></article>`).join("")}</div>
      <div class="business-route-flow"><div class="workspace-subhead"><strong>Đường đi của bản ghi</strong><span>Chọn màn hình bất kỳ để đi sâu vào bước đó</span></div><ol>${flow}</ol></div>
      <nav class="business-related-routes" aria-label="Các màn hình Pet Business liên quan"><div class="workspace-subhead"><strong>Liên kết màn hình trong quy trình</strong><span>${businessJourney.links.length} điểm nối</span></div><div class="business-related-grid">${related}</div></nav>
    </section>`;
  })() : "";
  const businessStatusTone = (status) => /cần xử lý|cần cập nhật|cần review|cần đối chiếu|bổ sung|thiếu|lệch|delta|quá sla|chưa nhận|tạm giữ|thừa|degraded|chậm|dlq|block|treo|quá hạn/i.test(status) ? "red" : /chờ|theo dõi|recount|đang đối chiếu|retry|review|sắp/i.test(status) ? "gold" : /khớp|đủ|healthy|đã duyệt|ổn định|đang hoạt động|đang hiệu lực|hoàn tất|event ack|active|tất cả branch|4\/4 branch|21 receipt/i.test(status) ? "green" : "blue";
  const businessTableRows = businessLayout?.rows.map((row) => {
    const status = row[row.length - 1];
    const tone = businessStatusTone(status);
    const needsAttention = tone === "red" || tone === "gold";
    return `<tr data-row data-attention="${needsAttention}" data-search="${esc(row.join(" ").toLocaleLowerCase("vi"))}">${row.map((cell, index) =>
      index === row.length - 1 ? `<td>${tag(cell, tone)}</td>` : `<td>${index === 0 ? `<strong class="primary-cell">${esc(cell)}</strong>` : esc(cell)}</td>`
    ).join("")}</tr>`;
  }).join("");
  const businessScreenPanel = businessLayout ? `<section class="business-screen-page" aria-label="Màn hình ${esc(pageModule[1])}">
    <div class="business-screen-intro"><div><span class="business-screen-eyebrow">BUSINESS OPERATIONS · ${esc(pageModule[0].toUpperCase())}</span><h2>${esc(businessLayout.title)}</h2><p>${esc(businessLayout.subtitle)}</p></div><button class="button primary" type="button" data-action="${esc(businessLayout.action)}" data-description="${esc(businessLayout.actionDescription)}">＋ ${esc(businessLayout.action)}</button></div>
    <div class="business-stage-rail">${businessLayout.stages.map(([number, label], index) => `<article class="business-stage ${index === 0 ? "current" : ""}"><span>${esc(number)}</span><strong>${esc(label)}</strong>${index < businessLayout.stages.length - 1 ? `<i aria-hidden="true">→</i>` : ""}</article>`).join("")}</div>
    <div class="business-workspace-grid"><article class="panel-card business-queue"><div class="panel-head"><div><span class="workspace-kicker">QUEUE · VERSIONED RECORDS</span><h2>${esc(businessLayout.title)}</h2><p>${esc(businessLayout.subtitle)}</p></div><span class="tag blue">${businessLayout.rows.length} dòng mẫu</span></div><div class="toolbar" aria-label="Lọc hàng đợi Pet Business"><button class="filter-chip active" type="button" data-filter="all">Tất cả</button><button class="filter-chip" type="button" data-filter="open">Đang mở</button><button class="filter-chip" type="button" data-filter="attention">Cần xử lý</button><input class="business-local-search" type="search" placeholder="Tìm trong hàng đợi..." aria-label="Tìm trong hàng đợi Pet Business"></div><div class="table-wrap"><table class="data-table"><thead><tr>${businessLayout.columns.map((column) => `<th scope="col">${esc(column)}</th>`).join("")}</tr></thead><tbody>${businessTableRows}</tbody></table></div><div class="empty-state">Không có bản ghi phù hợp với bộ lọc.</div><div class="business-table-foot"><span>Snapshot: 16/10/2026 · 07:00 ICT</span><span>Tenant: WAGGY Retail Group · Demo</span><span>Sort: SLA / trạng thái</span></div></article>
      <aside class="business-side-stack"><article class="panel-card"><div class="panel-head"><div><span class="workspace-kicker">CONTROL SIGNALS</span><h2>Điểm cần chú ý</h2><p>Tín hiệu chỉ gợi ý bước xử lý tiếp theo.</p></div></div><div class="list-stack">${businessLayout.signals.map(([title, body, meta, tone]) => `<div class="list-item"><div class="list-copy"><strong>${esc(title)}</strong><span>${esc(body)}</span></div><div class="list-meta">${tag(meta, tone)}</div></div>`).join("")}</div></article>
      <article class="panel-card business-owner-card"><span class="workspace-kicker">SLA / OWNER</span><strong>Người xử lý theo branch scope</strong><p>${esc(domainPlaybook.owner)}</p><div class="business-owner-meta"><span>Queue owner</span><b>Business Operations</b></div><div class="business-owner-meta"><span>Maker ≠ Checker</span><b>Enforced in workflow</b></div><button class="workspace-action" type="button" data-action="Xem quy tắc kiểm soát" data-description="${esc(businessLayout.control)}">Xem cổng kiểm soát →</button></article></aside></div>
    <div class="business-lower-grid"><article class="panel-card"><div class="panel-head"><div><span class="workspace-kicker">RECORD LIFECYCLE</span><h2>Checklist triển khai</h2><p>Các cổng có thể audit trước khi trạng thái được chuyển.</p></div></div><ol class="business-checklist">${businessLayout.stages.map(([number, label], index) => `<li><span>${esc(number)}</span><div><strong>${esc(label)}</strong><small>${index === businessLayout.stages.length - 1 ? "Ghi kết quả, actor, reason và reference" : "Kiểm scope, dữ liệu nguồn và version trước khi tiếp tục"}</small></div><b>${index === 0 ? "MỞ" : "CỔNG"}</b></li>`).join("")}</ol></article><article class="panel-card business-data-card"><div class="panel-head"><div><span class="workspace-kicker">LOCAL SANDBOX</span><h2>Dữ liệu Pet Business</h2><p>Demo store chỉ chia sẻ giữa 15 màn hình Pet Business.</p></div><span class="tag blue">${systemState.records.length} records</span></div><div class="business-data-metrics"><div><small>Audit events</small><strong>${systemState.audit.length}</strong></div><div><small>Runs</small><strong>${systemState.simulations.filter((run) => run.system === slug).length}</strong></div><div><small>Scope</small><strong>Tenant</strong></div></div><a class="button" href="#system-record-form">Thêm dữ liệu sandbox</a></article></div>
    <div class="business-persistence-area">${systemRecordsPanel}${sharedRecordsTable}${auditPanel}</div><div class="callout-card business-control-note"><strong>Business control:</strong> ${esc(businessLayout.control)} Không có bút toán, giao dịch, thay đổi tồn hoặc lệnh tích hợp thật nào được gửi đi.</div></section>` : "";
  const modulePanel = slug === "pet-business" && businessLayout ? businessScreenPanel :
    pageKey === "audit" ? `<section class="system-module-grid">${auditPanel}${systemRecordsPanel}${sharedRecordsTable}</section>` :
    pageKey === "integrations" ? `<section class="system-module-grid"><article class="panel-card"><div class="panel-head"><div><h2>Điểm kết nối dự kiến</h2><p>${esc(pageModule[2])} Mọi liên kết dưới đây là tài liệu và sandbox, không gọi API thật.</p></div></div><div class="list-stack">${data.items.map(([title, body, meta, tone]) => `<div class="list-item"><div class="list-copy"><strong>${esc(title)}</strong><span>${esc(body)}</span></div><div class="list-meta">${tag(meta, tone)}</div></div>`).join("")}</div><nav class="integration-links">${workspaceLinks}</nav></article>${systemRecordsPanel}${sharedRecordsTable}</section>` :
    pageKey === "overview" ? `<section class="system-module-grid">${systemRecordsPanel}${sharedRecordsTable}${auditPanel}</section>` :
    `<section class="system-module-grid"><div><article class="panel-card"><div class="panel-head"><div><h2>${esc(pageModule[1])} · hàng đợi mẫu</h2><p>${esc(pageModule[2])} Bản ghi mới được thêm ở màn hình này sẽ hiển thị tại các màn hình khác của cùng hệ thống.</p></div><span class="tag blue">${data.rows.length} mẫu nguồn</span></div><div class="toolbar" aria-label="Lọc dữ liệu hệ thống"><button class="filter-chip active" type="button" data-filter="all">Tất cả</button><button class="filter-chip" type="button" data-filter="open">Đang mở</button><button class="filter-chip" type="button" data-filter="attention">Cần xử lý</button></div><div class="table-wrap"><table class="data-table"><thead><tr><th>Mã</th><th>Tên bản ghi</th><th>Thông tin liên quan</th><th>Trạng thái</th></tr></thead><tbody id="system-record-rows">${renderStoredRecords()}</tbody></table></div><div class="empty-state">Không tìm thấy dòng phù hợp với bộ lọc.</div></article>${auditPanel}</div><aside class="insight-stack"><article class="panel-card"><div class="panel-head"><div><h2>Luồng công việc liên quan</h2><p>${esc(pageModule[2])}</p></div></div><div class="list-stack">${data.items.slice(0, 3).map(([title, body, meta, tone]) => `<div class="list-item"><div class="list-copy"><strong>${esc(title)}</strong><span>${esc(body)}</span></div><div class="list-meta">${tag(meta, tone)}</div></div>`).join("")}</div></article><article class="panel-card"><div class="panel-head"><div><h2>Chỉ số mẫu</h2><p>Cập nhật từ dữ liệu minh họa của hệ thống</p></div></div><div class="list-stack">${data.metrics.map(([label, value, foot]) => `<div class="list-item"><div class="list-copy"><strong>${esc(label)} · ${esc(value)}</strong><span>${esc(foot)}</span></div></div>`).join("")}</div></aside></section>${systemRecordsPanel}`;
  const actionPanel = `<section class="panel-card action-workbench" id="quick-actions"><div class="panel-head"><div><h2>Thao tác theo quy trình</h2><p>Chọn thao tác để xem mục đích và giới hạn của bản demo</p></div><span class="tag ${data.current ? "" : "blue"}">${data.current ? "PHÂN HỆ HIỆN CÓ" : "CONCEPT"}</span></div><div class="quick-grid">${actions}</div><div class="callout-card"><strong>Ranh giới nghiệp vụ:</strong> ${esc(data.note)}</div></section>`;
  const footer = `<footer class="screen-footer"><a href="${workflowRoot}${slug}.html" target="_blank" rel="noopener">Workflow ${esc(data.name)} ↗</a><span>Giao diện demo · Không dùng cho giao dịch thật</span><a href="${syncRoot}sync.html?system=${slug}" target="_blank" rel="noopener">Mở sync lab ↗</a></footer>`;
  const topTools = `<div class="frame-tools"><input class="search-box" type="search" placeholder="Tìm trong danh sách..." aria-label="Tìm kiếm trong bảng"><button class="icon-action" type="button" data-action="Thông báo" data-description="Thông báo minh họa; không gửi thông báo thật." aria-label="Thông báo">♧</button><button class="icon-action theme-toggle" type="button" aria-label="Đổi giao diện" title="Đổi giao diện">◐</button></div>`;
  const dashboardContent = `<section class="metric-grid" aria-label="Chỉ số">${metrics}</section>${workflowPanel}<section class="dashboard-grid">${tablePanel}${insightPanel}</section>${actionPanel}`;
  const headingContent = slug === "pet-connect" ? `<div class="connect-page-heading">${pageHeading}<div class="connect-safety"><b>Chế độ bảo vệ vị trí</b><span>Địa chỉ và liên hệ chi tiết được ẩn</span></div></div>` : pageHeading;
  const applicationContent = `${demoBanner}${headingContent}${pageKey === "overview" ? `${dashboardContent}${modulePanel}` : modulePanel}${businessProcessPanel}${businessJourneyPanel}${pageDetailsPanel}${algorithmPanel}${footer}`;
  const appBrand = `<a class="app-brand" href="${demoRoot}index.html"><span class="brand-icon">W</span><span>WAGGY<small>${esc(data.name.toUpperCase())}</small></span></a>`;
  const headerTools = `<div class="demo-app-identity"><span><strong>WAGGY DEMO LAB</strong><i>INDEPENDENT SANDBOX · DỮ LIỆU GIẢ LẬP</i></span><a href="${demoRoot}index.html">Bộ demo độc lập <span aria-hidden="true">↗</span></a></div>${topTools}`;
  const systemNavigation = `<nav class="side-nav" aria-label="Phân hệ">${allNavLinks}</nav>`;
  const shell = {
    "pet-care": `<div class="app-shell care-shell" data-system="${slug}"><aside class="sidebar care-sidebar">${appBrand}<div class="sidebar-label">KHÔNG GIAN CHĂM SÓC</div>${systemNavigation}<div class="sidebar-label">LIÊN KẾT</div><nav class="side-nav ecosystem-nav" aria-label="Liên kết hệ thống">${workspaceLinks}<a href="${demoRoot}index.html">Chọn hệ thống demo</a></nav><div class="sidebar-foot"><strong>Pet Care hiện có · Bản xem trước</strong>Dữ liệu mẫu · Đọc/ghi nghiệp vụ bị tắt</div></aside><div class="app-main"><div class="demo-app-identity"><span><strong>WAGGY DEMO LAB</strong><i>INDEPENDENT SANDBOX · DỮ LIỆU GIẢ LẬP</i></span><a href="${demoRoot}index.html">Bộ demo độc lập <span aria-hidden="true">↗</span></a></div><header class="frame-header care-header"><span class="workspace-select">Cơ sở trung tâm⌄</span><span class="frame-context">Tổng quan vận hành <b>Hôm nay · 15/10</b></span>${topTools}</header><main class="app-content care-content">${applicationContent}</main></div></div>`,
    "pet-service": `<div class="app-shell service-shell" data-system="${slug}"><header class="service-masthead"><div class="service-brand">${appBrand}<span class="service-workspace">CƠ SỞ TRUNG TÂM <b>⌄</b></span></div><div class="service-masthead-tools"><span class="service-shift"><i></i> CA SÁNG · 4 NHÂN VIÊN</span>${topTools}</div></header><nav class="service-nav" aria-label="Điều hướng dịch vụ">${nav}<span class="service-nav-links">${workspaceLinks}</span></nav><main class="app-content service-content">${demoBanner}${pageHeading}<section class="metric-grid">${metrics}</section>${workflowPanel}<section class="dashboard-grid service-dashboard">${tablePanel}${insightPanel}</section>${actionPanel}${footer}</main></div>`,
    "pet-health": `<div class="app-shell health-shell" data-system="${slug}"><aside class="health-sidebar"><div class="health-brand">${appBrand}<span>CLINIC WORKSPACE</span></div><div class="clinic-switch"><small>CƠ SỞ ĐANG XEM</small><b>Phòng khám mẫu A⌄</b><em>Tenant riêng · sandbox</em></div><div class="sidebar-label">LÂM SÀNG</div>${systemNavigation}<div class="health-sidebar-bottom"><span>●</span> Human review required<br><small>Không phát hành tự động</small></div><nav class="health-links">${workspaceLinks}</nav></aside><div class="app-main health-main"><header class="health-topbar"><div><span class="health-crumb">CLINIC A / WORK QUEUE</span><strong>Clinical workspace</strong></div>${topTools}<span class="health-user"><i>BS</i> Reviewer mẫu</span></header><main class="app-content health-content">${demoBanner}${pageHeading}<section class="metric-grid">${metrics}</section>${workflowPanel}<section class="health-dashboard">${tablePanel}${insightPanel}</section>${actionPanel}${footer}</main></div></div>`,
    "pet-commerce": `<div class="app-shell commerce-shell" data-system="${slug}"><header class="commerce-masthead"><div>${appBrand}<span class="commerce-channel"><small>KÊNH BÁN</small><b>WAGGY Store · Online⌄</b></span></div><div class="commerce-tools">${topTools}<span class="commerce-user">OPS</span></div></header><nav class="commerce-nav" aria-label="Điều hướng commerce">${nav}<span class="commerce-nav-links">${workspaceLinks}</span></nav><main class="app-content commerce-content">${demoBanner}${pageHeading}<section class="metric-grid">${metrics}</section>${workflowPanel}<div class="commerce-dashboard">${tablePanel}${insightPanel}</div>${actionPanel}${footer}</main></div>`,
    "pet-business": `<div class="app-shell business-shell" data-system="${slug}"><aside class="business-sidebar">${appBrand}<div class="sidebar-label">TỔ CHỨC</div><button class="branch-switch" type="button" data-action="Chọn phạm vi chi nhánh" data-description="Bộ chọn chi nhánh là minh họa. Không có quyền truy cập hoặc dữ liệu doanh nghiệp thật."><span>W</span><span><b>WAGGY Retail Group</b><small>4 chi nhánh · Toàn hệ thống</small></span><i>⌄</i></button><div class="sidebar-label">VẬN HÀNH</div>${systemNavigation}<div class="business-branch-list"><small>CHI NHÁNH</small><span><i class="branch-dot good"></i>Hà Nội · HN-01</span><span><i class="branch-dot good"></i>Thủ Đức · HCM-02</span><span><i class="branch-dot warn"></i>Đà Nẵng · DN-01</span><span><i class="branch-dot"></i>Cần Thơ · CT-01</span></div><nav class="business-links">${workspaceLinks}</nav><div class="sidebar-foot"><strong>Finance controls enabled</strong>Maker ≠ checker · Kỳ chưa khóa</div></aside><div class="app-main"><header class="business-topbar"><div><span class="business-period">KỲ DEMO · 15/10/2026</span><strong>Control tower</strong></div>${topTools}</header><main class="app-content business-content">${demoBanner}${pageHeading}<section class="metric-grid">${metrics}</section>${workflowPanel}<div class="business-dashboard">${tablePanel}${insightPanel}</div>${actionPanel}${footer}</main></div></div>`,
    "pet-community": `<div class="app-shell community-shell" data-system="${slug}"><header class="community-masthead"><div>${appBrand}<span class="community-space"><small>MODERATION SPACE</small><b>WAGGY Community · Trust &amp; Safety</b></span></div>${topTools}</header><nav class="community-nav" aria-label="Moderation views">${nav}<span class="community-nav-links">${workspaceLinks}</span></nav><main class="app-content community-content">${demoBanner}${pageHeading}<section class="metric-grid">${metrics}</section>${workflowPanel}<div class="community-dashboard">${tablePanel}<aside>${insightPanel}<div class="community-policy"><b>Quy tắc xử lý</b><span>Quyết định có căn cứ · Kháng nghị reviewer độc lập · Bảo vệ người báo cáo</span></div></aside></div>${actionPanel}${footer}</main></div>`,
    "pet-connect": `<div class="app-shell connect-shell" data-system="${slug}"><header class="connect-masthead"><div>${appBrand}<span class="connect-operation"><i></i> FIELD RESPONSE DESK <b>·</b> KHU VỰC MẪU</span></div>${topTools}</header><nav class="connect-nav" aria-label="Điều phối case">${nav}<span class="connect-nav-links">${workspaceLinks}</span></nav><main class="app-content connect-content">${demoBanner}<div class="connect-page-heading">${pageHeading}<div class="connect-safety"><b>Chế độ bảo vệ vị trí</b><span>Địa chỉ và liên hệ chi tiết được ẩn</span></div></div><section class="metric-grid">${metrics}</section>${workflowPanel}<div class="connect-dashboard">${tablePanel}${insightPanel}</div>${actionPanel}${footer}</main></div>`,
    "pet-intelligence": `<div class="app-shell intelligence-shell" data-system="${slug}"><aside class="intelligence-sidebar"><div class="intelligence-brand">${appBrand}<span>DATA &amp; MODEL GOVERNANCE</span></div><div class="intelligence-env"><i></i> SANDBOX · SHADOW MODE</div><div class="sidebar-label">GOVERNANCE</div>${systemNavigation}<div class="intelligence-links">${workspaceLinks}</div><div class="intelligence-sidebar-foot"><span>MODEL GATE</span><b>Human approval required</b><small>Rollback plan · Ready</small></div></aside><div class="app-main intelligence-main"><header class="intelligence-topbar"><div><span class="intelligence-breadcrumb">WAGGY DATA PLATFORM / GOVERNANCE</span><strong>Decision intelligence console</strong></div>${topTools}</header><main class="app-content intelligence-content">${demoBanner}${pageHeading}<section class="metric-grid">${metrics}</section>${workflowPanel}<section class="intelligence-dashboard">${tablePanel}${insightPanel}</section>${actionPanel}${footer}</main></div></div>`
  }[slug];

  const pageShell = pageKey === "overview"
    ? (slug === "pet-care" ? shell : shell.replace(`${footer}</main>`, `${modulePanel}${businessProcessPanel}${businessJourneyPanel}${pageDetailsPanel}${algorithmPanel}${footer}</main>`))
    : shell.replace(/<main class="([^"]*)">[\s\S]*?<\/main>/, (_, classNames) =>
      `<main class="${classNames}">${demoBanner}${headingContent}${modulePanel}${businessProcessPanel}${businessJourneyPanel}${pageDetailsPanel}${algorithmPanel}${footer}</main>`);
  const sharedDataPanel = pageKey === "overview" ? `<section class="panel-card shared-data-panel" aria-labelledby="shared-data-title"><div class="panel-head"><div><span class="workspace-kicker">WAGGY ECOSYSTEM · COMMON DATASET</span><h2 id="shared-data-title">Dữ liệu liên thông 8 hệ thống</h2><p>Thực thể mẫu có mã tham chiếu thống nhất; mỗi miền chỉ nhận các trường được phép.</p></div><a class="text-link" href="${syncRoot}sync.html?system=${slug}" target="_blank" rel="noopener">Mở sổ dữ liệu ↗</a></div><div id="shared-data-snapshot" aria-live="polite"><p class="empty-state">Đang tải snapshot dữ liệu chung…</p></div></section>` : "";
  const dataFlow = window.WaggySharedDemoData?.workflows?.[slug];
  const dataFlowPanel = pageKey === "overview" && dataFlow ? `<section class="panel-card shared-workflow-panel" aria-labelledby="shared-workflow-title"><div class="panel-head"><div><span class="workspace-kicker">DATA FLOW · ${esc(data.name.toUpperCase())}</span><h2 id="shared-workflow-title">Workflow dữ liệu của hệ thống</h2><p>${esc(dataFlow.purpose)}</p></div><span class="tag blue">${dataFlow.dataSequence.length} bước</span></div><ol class="shared-workflow-steps">${dataFlow.dataSequence.map(({ step, action }) => `<li><span>${String(step).padStart(2, "0")}</span><strong>${esc(action)}</strong></li>`).join("")}</ol><div class="shared-workflow-grid"><div><h3>Dữ liệu nhận</h3><ul>${dataFlow.consumes.map((item) => `<li>${esc(item)}</li>`).join("")}</ul></div><div><h3>Dữ liệu phát</h3><ul>${dataFlow.produces.map((item) => `<li>${esc(item)}</li>`).join("")}</ul></div><div><h3>Cổng kiểm soát</h3><ul>${dataFlow.gates.map((item) => `<li>${esc(item)}</li>`).join("")}</ul></div></div><div class="shared-workflow-links"><strong>Miền liên kết</strong>${dataFlow.links.map((target) => `<a href="${syncRoot}sync.html?system=${encodeURIComponent(target.system)}" target="_blank" rel="noopener">${esc(window.WaggySharedDemoData.systems[target.system])} · ${esc(target.records.join(", "))} ↗</a>`).join("")}</div><p class="shared-data-footnote">Đặc tả đầy đủ: <code>data/workflows/${esc(slug)}.workflow.json</code>. Nguồn dữ liệu: <code>data/${esc(slug)}.js</code>.</p></section>` : "";
  const dashboardShell = pageKey === "overview"
    ? pageShell.replace(`${footer}</main>`, `${sharedDataPanel}${dataFlowPanel}${footer}</main>`)
    : pageShell;
  mount.innerHTML = `${dashboardShell}<div class="toast" role="status" aria-live="polite"></div><div class="modal-backdrop" role="presentation"><section class="demo-modal" role="dialog" aria-modal="true" aria-labelledby="demo-modal-title"><h2 id="demo-modal-title">Thao tác mô phỏng</h2><p class="modal-copy"></p><div class="modal-actions"><button class="button" type="button" data-close-modal>Đóng</button><button class="button primary" type="button" data-confirm-demo>Đã hiểu</button></div></section></div>`;
  mount.setAttribute("aria-busy", "false");

  const toast = mount.querySelector(".toast");
  const modal = mount.querySelector(".modal-backdrop");
  let toastTimer;
  const showToast = (message) => {
    toast.textContent = message;
    toast.classList.add("show");
    window.clearTimeout(toastTimer);
    toastTimer = window.setTimeout(() => toast.classList.remove("show"), 2800);
  };
  const sharedDataSnapshot = mount.querySelector("#shared-data-snapshot");
  const refreshSharedData = () => {
    if (!sharedDataSnapshot || !window.WaggyDemoSync) return;
    try {
      const snapshot = window.WaggyDemoSync.snapshotFor(slug);
      const rows = snapshot.records.slice(0, 5).map((record) => `
        <tr><td><strong>${esc(record.id)}</strong><small>${esc(record.type)}</small></td>
          <td>${esc(record.label)}</td><td>${esc(record.value || "Được chia sẻ")}</td>
          <td>${esc(record.sourceName)}${record.owner ? " · nguồn chuẩn" : " · bản chiếu"}</td></tr>`).join("");
      sharedDataSnapshot.innerHTML = `<div class="shared-data-summary"><strong>${snapshot.records.length} bản ghi liên quan</strong><span>Kho cục bộ · lược đồ v${snapshot.schemaVersion} · ${snapshot.storageAvailable ? "đồng bộ giữa các tab cùng nguồn" : "chỉ lưu tạm trong tab"}</span></div><div class="table-wrap"><table class="data-table shared-data-table"><thead><tr><th>Mã / loại</th><th>Thực thể</th><th>Trạng thái</th><th>Nguồn dữ liệu</th></tr></thead><tbody>${rows}</tbody></table></div><p class="shared-data-footnote">${snapshot.records.length > 5 ? `Hiển thị 5/${snapshot.records.length} bản ghi được cấp cho ${esc(data.name)}. ` : ""}Dữ liệu chỉ là mẫu giả lập, không chứa hồ sơ cá nhân thật.</p>`;
    } catch (error) {
      sharedDataSnapshot.innerHTML = `<p class="shared-data-error" role="alert">Không thể tải dữ liệu chung: ${esc(error.message)}</p>`;
    }
  };
  refreshSharedData();
  window.WaggyDemoSync?.subscribe(refreshSharedData);
  if (storageNotice) showToast(storageNotice);
  const closeModal = () => modal.classList.remove("open");

  const refreshSystemData = () => {
    const recordRows = mount.querySelector("#system-record-rows");
    const auditRows = mount.querySelector("#system-audit-rows");
    const algorithmHistory = mount.querySelector("#algorithm-history");
    if (recordRows) recordRows.innerHTML = renderStoredRecords();
    if (auditRows) auditRows.innerHTML = renderAuditRows() || `<p class="empty-state">Chưa có thao tác mới trong phiên demo.</p>`;
    if (algorithmHistory) algorithmHistory.innerHTML = renderSimulationHistory() || `<p class="empty-state">Chưa có lần chạy nào được lưu cho màn hình này.</p>`;
    mount.querySelectorAll(".system-record-panel .tag.blue, .system-module-grid .panel-head .tag.blue").forEach((badge) => {
      if (/^\d+ bản ghi$/.test(badge.textContent.trim())) badge.textContent = `${systemState.records.length} bản ghi`;
    });
    updateRows();
  };
  const refreshBusinessProcesses = () => {
    const rows = mount.querySelector("[data-business-process-rows]");
    const count = mount.querySelector("[data-business-process-count]");
    const empty = mount.querySelector(".business-process-empty");
    if (rows) rows.innerHTML = renderBusinessProcesses();
    if (count) count.textContent = `${systemState.businessProcesses.filter((process) => process.stageIndex < process.steps.length).length} đang mở`;
    if (empty) empty.style.display = systemState.businessProcesses.length ? "none" : "block";
  };
  const startBusinessProcess = (sourcePage, title) => {
    const module = pageModules.find(([key]) => key === sourcePage);
    const steps = businessProcessFlows[sourcePage];
    if (!module || !steps || steps.length < 2 || steps[0] !== sourcePage) {
      throw new Error(`Không tìm thấy luồng Pet Business hợp lệ cho màn hình "${sourcePage}".`);
    }
    const process = {
      id: `PB-${Date.now().toString(36).toUpperCase()}`,
      title: `${title} · ${module[1]}`,
      sourcePage,
      sourceLabel: module[1],
      steps,
      stageIndex: 0,
      createdAt: new Date().toISOString()
    };
    systemState.businessProcesses.unshift(process);
    systemState.businessProcesses = systemState.businessProcesses.slice(0, 100);
    const saved = saveSystemState(`Tạo workflow demo ${process.id} · ${process.title}`);
    refreshBusinessProcesses();
    showToast(saved ? `Đã tạo ${process.id}. Tiếp tục tại ${module[1]}.` : storageNotice);
  };
  const recordForm = mount.querySelector("[data-system-record-form]");
  if (recordForm) {
    recordForm.addEventListener("submit", (event) => {
      event.preventDefault();
      const formData = new FormData(recordForm);
      const name = String(formData.get("name") || "").trim();
      if (!name) {
        showToast("Vui lòng nhập tên bản ghi trước khi lưu.");
        recordForm.elements.name.focus();
        return;
      }
      const record = {
        id: `${slug.replace("pet-", "").toUpperCase()}-${Date.now().toString(36).toUpperCase()}`,
        name,
        details: String(formData.get("details") || "").trim() || "Không có ghi chú",
        status: String(formData.get("status") || "Mới tạo"),
        source: "user"
      };
      systemState.records.unshift(record);
      const saved = saveSystemState(`Đã thêm ${record.id} · ${record.name}`);
      refreshSystemData();
      recordForm.reset();
      showToast(saved ? "Đã lưu trong dữ liệu demo của hệ thống này; mở màn hình khác để xem bản ghi." : storageNotice);
    });
  }
  const algorithmForm = mount.querySelector("[data-algorithm-form]");
  if (algorithmForm) {
    algorithmForm.addEventListener("submit", (event) => {
      event.preventDefault();
      try {
        const formData = new FormData(algorithmForm);
        const values = Object.fromEntries(algorithm.fields.map((item) => {
          const rawValue = formData.get(item.name);
          if (item.type === "select") {
            const value = String(rawValue || "");
            if (!item.options.some(([option]) => option === value)) throw new Error(`Giá trị không hợp lệ cho trường "${item.label}".`);
            return [item.name, value];
          }
          const value = Number(rawValue);
          if (!Number.isFinite(value) || value < item.min || value > item.max) {
            throw new Error(`"${item.label}" phải nằm trong khoảng ${item.min}–${item.max}.`);
          }
          return [item.name, value];
        }));
        const result = algorithm.calculate(values);
        const simulation = {
          id: `SIM-${Date.now().toString(36)}`,
          system: slug,
          page: pageKey,
          status: result.status,
          summary: result.summary,
          calculation: result.calculation,
          at: new Date().toISOString()
        };
        systemState.simulations.unshift(simulation);
        systemState.simulations = systemState.simulations.slice(0, 100);
        const saved = saveSystemState(`${pageModule[1]} · ${result.status} · ${result.summary}`);
        const resultPanel = mount.querySelector("#algorithm-result");
        resultPanel.innerHTML = renderAlgorithmResult(result, true);
        refreshSystemData();
        showToast(saved ? "Đã chạy và lưu kết quả trong audit sandbox của hệ thống này." : storageNotice);
      } catch (error) {
        showToast(`Không thể chạy phép tính: ${error.message}`);
      }
    });
  }
  window.addEventListener("storage", (event) => {
    if (event.key !== storageKey || !event.newValue) return;
    try {
      const updated = JSON.parse(event.newValue);
      if (![1, 2].includes(updated.schemaVersion) || !Array.isArray(updated.records) || !Array.isArray(updated.audit) ||
          (updated.schemaVersion === 2 && (!Array.isArray(updated.businessProcesses) || !updated.businessProcesses.every(isValidBusinessProcess)))) {
        throw new Error("Dữ liệu đồng bộ từ tab khác không hợp lệ.");
      }
      systemState = {
        ...updated,
        schemaVersion: 2,
        businessProcesses: Array.isArray(updated.businessProcesses) ? updated.businessProcesses : []
      };
      refreshSystemData();
      refreshBusinessProcesses();
    } catch (error) {
      showToast(`Không thể đồng bộ thay đổi từ tab khác (${error.message}).`);
    }
  });
  mount.addEventListener("click", (event) => {
    const workflowStart = event.target.closest("[data-business-process-start]");
    if (workflowStart) {
      try {
        const sourcePage = workflowStart.dataset.businessProcessStart;
        const module = pageModules.find(([key]) => key === sourcePage);
        if (!module) throw new Error(`Không tìm thấy màn hình Pet Business "${sourcePage}".`);
        startBusinessProcess(sourcePage, module[1]);
      } catch (error) {
        showToast(`Không thể tạo workflow demo: ${error.message}`);
      }
      return;
    }
    const workflowAdvance = event.target.closest("[data-workflow-advance]");
    if (workflowAdvance) {
      const process = systemState.businessProcesses.find((item) => item.id === workflowAdvance.dataset.workflowAdvance);
      if (!process || process.steps[process.stageIndex] !== pageKey) {
        showToast("Không thể xác nhận: workflow đã thay đổi hoặc bước này không còn hiệu lực. Hãy làm mới danh sách.");
        return;
      }
      process.stageIndex += 1;
      const currentModule = pageModules.find(([key]) => key === pageKey);
      const nextModule = pageModules.find(([key]) => key === process.steps[process.stageIndex]);
      const result = nextModule ? `Chuyển tới ${nextModule[1]}` : "Đã hoàn tất quy trình demo";
      const saved = saveSystemState(`${process.id} · ${currentModule[1]} xác nhận · ${result}`);
      refreshBusinessProcesses();
      showToast(saved ? `${process.id}: ${result}.` : storageNotice);
      return;
    }
    const action = event.target.closest("[data-action]");
    if (action) {
      if (slug === "pet-business" && businessLayout && action.dataset.action === businessLayout.action) {
        try {
          startBusinessProcess(pageKey, action.dataset.action);
        } catch (error) {
          showToast(`Không thể tạo workflow demo: ${error.message}`);
        }
        return;
      }
      mount.querySelector(".modal-copy").textContent = `${action.dataset.description} Thao tác này không thay đổi dữ liệu; dùng biểu mẫu ghi nhận để lưu dữ liệu demo.`;
      modal.classList.add("open");
      return;
    }
    if (event.target.closest("[data-close-modal],[data-confirm-demo]")) closeModal();
    if (event.target === modal) closeModal();
    const filter = event.target.closest("[data-filter]");
    if (filter) {
      const filterBar = filter.closest(".toolbar");
      filterBar.querySelectorAll("[data-filter]").forEach((button) => button.classList.toggle("active", button === filter));
      updateRows(filter.closest(".business-queue,.data-workbench") || mount);
    }
  });

  const updateRows = (scope = mount, searchValue) => {
    const currentSearch = searchValue ?? scope.querySelector(".business-local-search")?.value ?? mount.querySelector(".search-box")?.value ?? "";
    const query = currentSearch.trim().toLocaleLowerCase("vi");
    const activeFilter = scope === mount ? "all" : scope.querySelector("[data-filter].active")?.dataset.filter || "all";
    let visible = 0;
    scope.querySelectorAll("[data-row]").forEach((row) => {
      const matchesText = row.dataset.search.includes(query);
      const text = row.textContent.toLocaleLowerCase("vi");
      const matchesFilter = activeFilter === "all" ||
        (activeFilter === "attention" && (row.dataset.attention === "true" || (row.dataset.attention === undefined && /cần|chờ|pending|thấp|lệch|mở|rà soát|xác minh|case đổi trả|đang đối soát/i.test(text)))) ||
        (activeFilter === "open" && !/hoàn tất|đã đóng|đã giao|đã phát hành/i.test(text));
      row.hidden = !(matchesText && matchesFilter);
      if (!row.hidden) visible += 1;
    });
    const emptyState = scope.querySelector(".empty-state");
    if (emptyState) emptyState.style.display = visible ? "none" : "block";
  };
  mount.querySelectorAll(".search-box,.business-local-search").forEach((search) => {
    search.addEventListener("input", () => updateRows(search.matches(".business-local-search") ? mount.querySelector(".business-queue") : mount, search.value));
  });
  mount.querySelectorAll(".theme-toggle").forEach((button) => button.addEventListener("click", () => {
    const dark = document.documentElement.dataset.theme !== "dark";
    document.documentElement.dataset.theme = dark ? "dark" : "light";
    try { localStorage.setItem("waggy-demo-theme", dark ? "dark" : "light"); }
    catch (error) { showToast("Không thể lưu tùy chọn giao diện trên trình duyệt này."); }
  }));
  try {
    const savedTheme = localStorage.getItem("waggy-demo-theme");
    if (savedTheme === "dark") document.documentElement.dataset.theme = "dark";
  } catch (error) {
    showToast("Không thể đọc tùy chọn giao diện đã lưu.");
  }
  const mobileNavToggle = mount.querySelector(".mobile-nav-toggle");
  if (mobileNavToggle) {
    mobileNavToggle.addEventListener("click", () => {
      mount.querySelector(".sidebar").scrollIntoView({ behavior: "smooth", block: "start" });
      showToast("Cuộn lên điều hướng hệ thống.");
    });
  }
})();
