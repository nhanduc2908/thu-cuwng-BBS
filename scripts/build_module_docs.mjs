import { writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const outputDir = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../HTML/Module');
const modules = [
  {
    file: 'module_01_platform.html', title: ['Nền tảng & dữ liệu', 'Platform & Data'], group: ['Nền tảng', 'Platform'],
    purpose: ['Quản lý môi trường chạy cục bộ, cơ sở dữ liệu SQLite và thông tin nền tảng của PetCare.', 'Covers the local runtime, SQLite database and platform information for PetCare.'],
    responsibilities: [['Thông tin môi trường', 'Environment information'], ['Vị trí và kích thước cơ sở dữ liệu', 'Database path and size'], ['Phiên bản SQLite', 'SQLite version'], ['Số lượng vật nuôi và tài khoản được đọc từ dữ liệu', 'Animal and user counts read from data']],
    workflow: [['Mở ứng dụng desktop', 'Launch the desktop application'], ['Khởi tạo hoặc mở cơ sở dữ liệu SQLite', 'Initialize or open the SQLite database'], ['Đọc thông tin môi trường và dữ liệu nền', 'Read environment and baseline data'], ['Rà soát sao lưu theo quy trình vận hành', 'Review backups as part of operations']],
    operations: [['Đọc thông tin môi trường', 'Read environment information'], ['Kiểm tra đường dẫn SQLite', 'Check the SQLite path'], ['Xem kích thước cơ sở dữ liệu', 'View database size'], ['Xem phiên bản SQLite', 'View SQLite version'], ['Đếm hồ sơ vật nuôi', 'Count animal records'], ['Đếm tài khoản nội bộ', 'Count internal accounts'], ['Khởi tạo cấu trúc dữ liệu khi chạy lần đầu', 'Initialize data structures on first run'], ['Mở lại dữ liệu đã lưu', 'Reopen persisted data'], ['Rà soát tính toàn vẹn trước khi thao tác', 'Review integrity before operations'], ['Lập kế hoạch sao lưu ngoài ứng dụng', 'Plan backups outside the application']],
    limits: [['Không có dịch vụ backend, cloud hoặc SaaS nhiều chi nhánh.', 'There is no backend, cloud service or multi-branch SaaS.'], ['Màn hình không phải bảng giám sát uptime hay chính sách lưu trữ tự động.', 'The screen is not an uptime monitor or automated retention policy.'], ['Sao lưu thường xuyên và bảo vệ máy là trách nhiệm vận hành.', 'Regular backups and machine security are operational responsibilities.']]
  },
  {
    file: 'module_02_accounts.html', title: ['Tài khoản & phân quyền', 'Accounts & Roles'], group: ['Nền tảng', 'Platform'],
    purpose: ['Quản trị tài khoản nội bộ, xác thực, vai trò, quyền khu vực và dấu vết kiểm toán.', 'Administrates internal accounts, authentication, roles, area access and audit traceability.'],
    responsibilities: [['Tài khoản nhân viên nội bộ', 'Internal staff accounts'], ['Vai trò và quyền truy cập', 'Roles and access permissions'], ['Đăng nhập và đổi mật khẩu', 'Sign-in and password change'], ['Audit cho sự kiện quan trọng', 'Audit records for important events']],
    workflow: [['Tạo tài khoản hoặc mở danh sách tài khoản', 'Create an account or open the account list'], ['Gán vai trò theo trách nhiệm công việc', 'Assign a role based on job responsibility'], ['Xác thực khi đăng nhập', 'Authenticate at sign-in'], ['Ghi nhận thao tác được kiểm toán', 'Record auditable operations']],
    operations: [['Tạo tài khoản nhân viên', 'Create a staff account'], ['Cập nhật trạng thái tài khoản', 'Update account status'], ['Gán vai trò', 'Assign a role'], ['Kiểm tra quyền khu vực', 'Check area permissions'], ['Đăng nhập bằng thông tin hợp lệ', 'Sign in with valid credentials'], ['Từ chối thông tin xác thực không hợp lệ', 'Reject invalid credentials'], ['Đổi mật khẩu quản trị mặc định lần đầu', 'Change the default admin password on first use'], ['Xem sự kiện đăng nhập đã ghi', 'Review recorded sign-in events'], ['Ghi dấu thao tác ghi quan trọng', 'Audit an important write operation'], ['Bàn giao quyền khi thay đổi nhân sự', 'Review access after staff changes']],
    limits: [['Mật khẩu được băm bằng PBKDF2-HMAC-SHA256 với salt ngẫu nhiên.', 'Passwords use PBKDF2-HMAC-SHA256 with a random salt.'], ['Tài khoản là tài khoản nội bộ cục bộ, không phải danh tính trực tuyến.', 'Accounts are local internal accounts, not online identities.'], ['Bảo vệ tài khoản Windows và đổi mật khẩu tạm là cần thiết.', 'Secure the Windows account and rotate the temporary password.']]
  },
  {
    file: 'module_03_dashboard.html', title: ['Bảng điều khiển', 'Dashboard'], group: ['Nền tảng', 'Platform'],
    purpose: ['Tổng hợp các chỉ báo vận hành được truy vấn từ dữ liệu hiện có để giúp nhân viên bắt đầu công việc.', 'Summarizes operational indicators queried from existing records so staff can orient their work.'],
    responsibilities: [['Tóm tắt hoạt động', 'Activity summaries'], ['Liên kết sang khu vực nghiệp vụ', 'Links to operational areas'], ['Cảnh báo dựa trên dữ liệu đã ghi', 'Alerts based on recorded data'], ['Điểm bắt đầu rà soát', 'Starting point for review']],
    workflow: [['Khởi chạy sau khi người dùng đăng nhập', 'Open after the user signs in'], ['Truy vấn số liệu hiện có', 'Query available records'], ['Rà soát mục cần chú ý', 'Review items needing attention'], ['Mở phân hệ để xử lý chi tiết', 'Open a module for detailed handling']],
    operations: [['Mở bảng điều khiển', 'Open the dashboard'], ['Tải số liệu hiện có', 'Load available figures'], ['Điều hướng tới hồ sơ vật nuôi', 'Navigate to animal records'], ['Điều hướng tới kho', 'Navigate to inventory'], ['Điều hướng tới lịch dịch vụ', 'Navigate to the service schedule'], ['Rà soát mục cảnh báo', 'Review alert items'], ['Mở nguồn của chỉ báo', 'Open an indicator source'], ['Làm mới dữ liệu sau cập nhật', 'Refresh after a change'], ['Phân biệt trạng thái trống với số không', 'Distinguish empty state from zero'], ['Diễn giải trong đúng khoảng dữ liệu', 'Interpret within the available data period']],
    limits: [['Không dùng số liệu minh họa trong tài liệu làm KPI thực tế.', 'Do not treat illustrative documentation figures as real KPIs.'], ['Số liệu phụ thuộc độ đầy đủ và chính xác của dữ liệu đã nhập.', 'Figures depend on the completeness and accuracy of entered data.'], ['Dashboard không tự chứng minh hiệu quả kinh doanh hoặc uptime.', 'The dashboard does not prove business outcomes or uptime.']]
  },
  {
    file: 'module_04_pets.html', title: ['Hồ sơ vật nuôi', 'Pet Profiles'], group: ['Chăm sóc động vật', 'Animal care'],
    purpose: ['Quản lý hồ sơ định danh vật nuôi, trạng thái, liên kết chủ nuôi và lịch sử vận hành.', 'Manages animal identity records, status, owner links and operational history.'],
    responsibilities: [['Thông tin định danh và thuộc tính', 'Identity and profile attributes'], ['Liên kết khách hàng', 'Customer association'], ['Trạng thái hồ sơ', 'Record status'], ['Lịch sử chăm sóc và sức khỏe liên quan', 'Related care and health history']],
    workflow: [['Tiếp nhận và xác nhận dữ liệu đầu vào', 'Receive and confirm intake information'], ['Tạo hồ sơ vật nuôi', 'Create the animal profile'], ['Liên kết chủ nuôi khi phù hợp', 'Link an owner when applicable'], ['Theo dõi trạng thái và hoạt động tiếp theo', 'Track status and subsequent activity']],
    operations: [['Tạo hồ sơ vật nuôi', 'Create an animal profile'], ['Cập nhật thuộc tính hồ sơ', 'Update profile attributes'], ['Tìm kiếm hồ sơ hiện có', 'Find an existing profile'], ['Liên kết khách hàng', 'Link a customer'], ['Thay đổi trạng thái hồ sơ', 'Change record status'], ['Rà soát thông tin tiếp nhận', 'Review intake information'], ['Mở lịch sử chăm sóc', 'Open care history'], ['Mở hồ sơ sức khỏe liên quan', 'Open related health records'], ['Kiểm tra ảnh bàn giao khi có', 'Check a handover photo when present'], ['Đóng hoặc lưu thay đổi hồ sơ', 'Save profile changes']],
    limits: [['Quy trình tiếp nhận/check-in cần hoàn tất trước khi dùng hồ sơ trong nghiệp vụ phù hợp.', 'Intake/check-in should be completed before the profile is used in relevant operations.'], ['Thông tin demo không phải số vật nuôi hoặc tình trạng sức khỏe hiện tại.', 'Demo content is not a current animal count or health status.'], ['Hồ sơ sức khỏe không tương đương chẩn đoán thú y.', 'Health records are not veterinary diagnoses.']]
  },
  {
    file: 'module_05_housing.html', title: ['Chuồng nuôi & sức chứa', 'Housing & Enclosures'], group: ['Chăm sóc động vật', 'Animal care'],
    purpose: ['Quản lý khu vực/chuồng nuôi, sức chứa, loài phù hợp, phân công và lịch sử vị trí.', 'Manages housing areas, capacity, species suitability, assignments and location history.'],
    responsibilities: [['Danh mục enclosure', 'Enclosure catalog'], ['Sức chứa và loài được phép', 'Capacity and accepted species'], ['Gán vật nuôi vào vị trí', 'Assign animals to locations'], ['Lịch sử thay đổi vị trí', 'Location change history']],
    workflow: [['Rà soát khu vực và sức chứa khai báo', 'Review declared areas and capacity'], ['Xác nhận loài phù hợp', 'Confirm species suitability'], ['Gán vật nuôi vào vị trí còn khả dụng', 'Assign an animal to an available location'], ['Lưu lịch sử khi chuyển vị trí', 'Record history when moving locations']],
    operations: [['Tạo hồ sơ khu vực nuôi', 'Create a housing area'], ['Cập nhật sức chứa', 'Update capacity'], ['Rà soát loài được chấp nhận', 'Review accepted species'], ['Đặt trạng thái enclosure hoạt động', 'Set enclosure active status'], ['Gán vật nuôi', 'Assign an animal'], ['Từ chối gán vượt sức chứa', 'Reject assignment beyond capacity'], ['Từ chối loài không phù hợp', 'Reject an unsuitable species'], ['Chuyển vị trí vật nuôi', 'Move an animal'], ['Xem lịch sử phân công', 'Review assignment history'], ['Ngừng sử dụng vị trí không hoạt động', 'Stop using an inactive location']],
    limits: [['Sức chứa và trạng thái hoạt động phải được duy trì chính xác bởi người dùng.', 'Users must maintain accurate capacity and active status.'], ['Không suy ra điều kiện thú y chỉ từ phân loại loài.', 'Do not infer veterinary suitability from species classification alone.'], ['Số lượng trên trang mẫu không đại diện tình trạng thực tế.', 'Sample page counts do not represent actual occupancy.']]
  },
  {
    file: 'module_06_suppliers.html', title: ['Nhà cung cấp', 'Suppliers'], group: ['Bán hàng & kho', 'Sales & inventory'],
    purpose: ['Lưu hồ sơ liên hệ nhà cung cấp và liên kết với các đợt nhập hàng được ghi nhận.', 'Stores supplier contact records and links them to recorded stock intake batches.'],
    responsibilities: [['Thông tin nhà cung cấp', 'Supplier information'], ['Trạng thái hồ sơ', 'Record status'], ['Liên kết tới phiếu/đợt nhập', 'Links to imports/batches'], ['Tra cứu lịch sử giao dịch nhập đã lưu', 'Review saved intake history']],
    workflow: [['Tạo hoặc tìm nhà cung cấp', 'Create or find a supplier'], ['Cập nhật thông tin liên hệ', 'Update contact information'], ['Chọn nhà cung cấp khi ghi nhận đợt nhập', 'Select a supplier when recording an intake'], ['Rà soát các đợt nhập liên quan', 'Review related intake batches']],
    operations: [['Tạo hồ sơ nhà cung cấp', 'Create a supplier record'], ['Sửa thông tin liên hệ', 'Edit contact information'], ['Tìm nhà cung cấp', 'Find a supplier'], ['Cập nhật trạng thái hồ sơ', 'Update record status'], ['Liên kết đợt nhập', 'Link an intake batch'], ['Mở lịch sử nhập hàng', 'Open intake history'], ['Kiểm tra dữ liệu liên hệ trước khi lưu', 'Validate contact data before saving'], ['Tránh tạo hồ sơ trùng', 'Avoid duplicate records'], ['Rà soát nhà cung cấp không còn hoạt động', 'Review inactive suppliers'], ['Đối chiếu thông tin nhập đã ghi', 'Reconcile recorded intake information']],
    limits: [['Không tự động đặt hàng hoặc dự đoán thời gian giao hàng.', 'Does not automate purchasing or predict lead times.'], ['Dữ liệu nhà cung cấp không tự tạo số lượng tồn kho.', 'Supplier data does not automatically create stock quantities.'], ['Điều kiện mua và giá cần được cửa hàng xác nhận.', 'Stores must validate purchase terms and prices.']]
  },
  {
    file: 'module_07_imports.html', title: ['Nhập hàng & tiếp nhận', 'Imports & Intake'], group: ['Bán hàng & kho', 'Sales & inventory'],
    purpose: ['Ghi nhận đợt nhập, nguồn cung, tiếp nhận vật nuôi và kết quả kiểm tra ban đầu.', 'Records intake batches, source, animal receipt and initial inspection outcomes.'],
    responsibilities: [['Đợt nhập và nhà cung cấp liên quan', 'Intake batches and related suppliers'], ['Thông tin tiếp nhận vật nuôi', 'Animal receipt information'], ['Ảnh bàn giao bắt buộc theo quy trình', 'Handover photo required by the workflow'], ['Kết quả kiểm tra', 'Inspection outcome']],
    workflow: [['Mở phiếu/đợt nhập', 'Open an intake batch'], ['Ghi thông tin lô và nguồn', 'Record batch and source'], ['Tiếp nhận và đính kèm ảnh bàn giao', 'Receive and attach a handover photo'], ['Nhân viên xác nhận và chọn kết quả kiểm tra', 'Staff confirm and select inspection outcome']],
    operations: [['Tạo đợt nhập', 'Create an intake batch'], ['Chọn nhà cung cấp liên quan', 'Select a related supplier'], ['Ghi thông tin lô hàng', 'Record batch information'], ['Tiếp nhận vật nuôi', 'Receive an animal'], ['Đính kèm ảnh bàn giao', 'Attach a handover photo'], ['Xác nhận tiếp nhận bởi nhân viên', 'Confirm receipt by staff'], ['Đánh dấu đã kiểm tra', 'Mark as inspected'], ['Chọn passed', 'Select passed'], ['Chọn quarantine', 'Select quarantine'], ['Chọn needs treatment', 'Select needs treatment']],
    limits: [['Ảnh bàn giao và xác nhận của nhân viên là một phần quy trình tiếp nhận.', 'Handover photos and staff confirmation are part of the intake workflow.'], ['Trạng thái needs treatment ghi nhận kết quả vận hành, không tạo chẩn đoán.', 'Needs treatment records an operational outcome, not a diagnosis.'], ['Nhập dữ liệu nhà cung cấp không thay thế kiểm đếm kho thực tế.', 'Supplier intake does not replace a physical stock count.']]
  },
  {
    file: 'module_08_health.html', title: ['Theo dõi sức khỏe', 'Health Monitoring'], group: ['Chăm sóc động vật', 'Animal care'],
    purpose: ['Lưu quan sát sức khỏe, danh mục bệnh và lịch/bản ghi tiêm chủng để hỗ trợ theo dõi nội bộ.', 'Stores health observations, disease catalog entries and vaccination schedules/records for internal tracking.'],
    responsibilities: [['Bản ghi quan sát sức khỏe', 'Health observation records'], ['Danh mục phân loại', 'Classification catalog'], ['Lịch tiêm và lịch sử tiêm', 'Vaccination schedule and history'], ['Liên kết hồ sơ vật nuôi', 'Animal profile association']],
    workflow: [['Chọn hồ sơ vật nuôi', 'Select an animal profile'], ['Ghi quan sát có nguồn và ngày', 'Record an observation with source and date'], ['Lập hoặc rà soát lịch tiêm', 'Create or review a vaccination schedule'], ['Theo dõi lịch sử và nhắc việc', 'Track history and reminders']],
    operations: [['Tạo quan sát sức khỏe', 'Create a health observation'], ['Liên kết vật nuôi', 'Link an animal'], ['Chọn danh mục phù hợp', 'Select a suitable catalog entry'], ['Ghi ngày quan sát', 'Record observation date'], ['Cập nhật bản ghi sức khỏe', 'Update a health record'], ['Tạo lịch tiêm', 'Create a vaccination schedule'], ['Ghi tiêm đã thực hiện', 'Record a completed vaccination'], ['Rà soát lịch đến hạn', 'Review due schedules'], ['Mở lịch sử sức khỏe', 'Open health history'], ['Chuyển trường hợp cần chuyên gia cho bác sĩ thú y', 'Refer cases needing expertise to a veterinarian']],
    limits: [['Ứng dụng lưu trữ theo dõi; không chẩn đoán bệnh hoặc kê phác đồ điều trị.', 'The app records observations; it does not diagnose disease or prescribe treatment.'], ['Thông tin dinh dưỡng là phân loại danh mục, không phải chỉ dẫn y tế.', 'Nutrition information is catalog classification, not medical guidance.'], ['Ngày và trạng thái nhắc việc cần được người dùng xác minh.', 'Users must verify dates and reminder status.']]
  },
  {
    file: 'module_09_care.html', title: ['Chăm sóc hằng ngày', 'Daily Care'], group: ['Chăm sóc động vật', 'Animal care'],
    purpose: ['Theo dõi công việc chăm sóc thường nhật và checklist vận hành 25 điểm cho vật nuôi.', 'Tracks routine care tasks and the 25-point operational checklist for animals.'],
    responsibilities: [['Tác vụ chăm sóc', 'Care tasks'], ['Checklist 25 điểm', '25-point checklist'], ['Người thực hiện và trạng thái', 'Assigned staff and status'], ['Lịch sử hoàn thành', 'Completion history']],
    workflow: [['Mở danh sách tác vụ theo vật nuôi', 'Open tasks by animal'], ['Thực hiện kiểm tra chăm sóc', 'Perform care checks'], ['Đánh dấu hoàn thành hoặc ghi chú cần theo dõi', 'Mark complete or note follow-up'], ['Rà soát các mục chưa hoàn tất', 'Review incomplete items']],
    operations: [['Tạo tác vụ chăm sóc', 'Create a care task'], ['Chọn vật nuôi', 'Select an animal'], ['Mở checklist 25 điểm', 'Open the 25-point checklist'], ['Ghi nhận mục đã kiểm tra', 'Record checked items'], ['Ghi người thực hiện', 'Record the staff member'], ['Cập nhật trạng thái tác vụ', 'Update task status'], ['Lưu ghi chú vận hành', 'Save an operational note'], ['Rà soát mục quá hạn theo dữ liệu', 'Review overdue items from records'], ['Mở lịch sử chăm sóc', 'Open care history'], ['Chuyển vấn đề sức khỏe sang phân hệ health', 'Route health concerns to the health module']],
    limits: [['Module tập trung checklist và tác vụ chăm sóc, không phải lịch đặt dịch vụ.', 'This module focuses on care checklists and tasks, not service bookings.'], ['Không đưa ra điều trị hoặc lời khuyên thú y.', 'It does not provide treatment or veterinary advice.'], ['Tác vụ chưa ghi nhận không thể được coi là đã hoàn tất.', 'Unrecorded tasks cannot be assumed complete.']]
  },
  {
    file: 'module_10_customers.html', title: ['Khách hàng', 'Customers'], group: ['Bán hàng & kho', 'Sales & inventory'],
    purpose: ['Quản lý hồ sơ khách hàng nội bộ, liên kết vật nuôi và tra cứu quan hệ giao dịch/dịch vụ.', 'Manages internal customer records, animal links and related sales/service history.'],
    responsibilities: [['Thông tin khách hàng', 'Customer information'], ['Liên kết khách hàng-vật nuôi', 'Customer-animal links'], ['Lịch sử nghiệp vụ liên quan', 'Related operational history'], ['Tra cứu trong luồng bán hàng', 'Lookup in sales workflows']],
    workflow: [['Tạo hoặc tra cứu khách hàng', 'Create or find a customer'], ['Xác minh thông tin nhập', 'Verify entered information'], ['Liên kết vật nuôi thuộc khách hàng', 'Link customer animals'], ['Mở giao dịch hoặc lịch sử liên quan', 'Open related transactions or history']],
    operations: [['Tạo hồ sơ khách hàng', 'Create a customer record'], ['Tìm hồ sơ hiện có', 'Find an existing record'], ['Cập nhật thông tin liên hệ', 'Update contact information'], ['Liên kết vật nuôi', 'Link an animal'], ['Rà soát vật nuôi đã liên kết', 'Review linked animals'], ['Mở lịch sử bán hàng liên quan', 'Open related sales history'], ['Mở lịch sử dịch vụ liên quan', 'Open related service history'], ['Kiểm tra dữ liệu trùng trước khi tạo', 'Check for duplicates before creating'], ['Giới hạn quyền truy cập dữ liệu cá nhân', 'Restrict access to personal data'], ['Cập nhật hoặc ngừng sử dụng hồ sơ theo chính sách', 'Update or retire a record under policy']],
    limits: [['Đây là dữ liệu khách hàng nội bộ, không có cổng đăng ký công khai.', 'These are internal customer records; there is no public signup portal.'], ['Trang khách hàng là góc nhìn tập trung của dữ liệu dùng chung với bán hàng.', 'The customer view focuses shared data also used by sales.'], ['Chỉ thu thập và hiển thị dữ liệu cần thiết cho vận hành.', 'Collect and display only information needed for operations.']]
  },
  {
    file: 'module_11_reservations.html', title: ['Đặt giữ & tiền cọc', 'Reservations & Deposits'], group: ['Bán hàng & kho', 'Sales & inventory'],
    purpose: ['Theo dõi giữ chỗ vật nuôi, tiền cọc và hoàn cọc theo trạng thái giao dịch.', 'Tracks animal reservations, deposits and refunds through transaction states.'],
    responsibilities: [['Liên kết vật nuôi và giao dịch', 'Animal and transaction links'], ['Số tiền đặt cọc', 'Deposit amount'], ['Tình trạng giữ chỗ', 'Reservation state'], ['Lịch sử hoàn tiền', 'Refund history']],
    workflow: [['Tạo yêu cầu giữ chỗ', 'Create a reservation'], ['Ghi tiền cọc trong giới hạn giá bán', 'Record a deposit within the sale-price limit'], ['Theo dõi trạng thái giữ', 'Track reservation status'], ['Hoàn đủ tiền cọc trước khi giải phóng giữ chỗ', 'Refund the deposit in full before releasing the reservation']],
    operations: [['Tạo giữ chỗ cho vật nuôi', 'Reserve an animal'], ['Liên kết khách hàng và giao dịch', 'Link customer and transaction'], ['Ghi tiền cọc', 'Record a deposit'], ['Từ chối tiền cọc vượt giá bán', 'Reject a deposit above the sale price'], ['Cập nhật trạng thái giữ chỗ', 'Update reservation status'], ['Ghi một phần hoàn cọc', 'Record a partial deposit refund'], ['Ghi hoàn cọc đủ', 'Record a full deposit refund'], ['Chỉ giải phóng sau khi hoàn đủ', 'Release only after a full refund'], ['Hủy giữ chỗ theo quy tắc', 'Cancel according to rules'], ['Đối chiếu lịch sử cọc và hoàn', 'Reconcile deposit and refund history']],
    limits: [['Tiền cọc không được vượt giá bán.', 'A deposit cannot exceed the sale price.'], ['Không thể giải phóng reservation cho tới khi tiền cọc được hoàn đủ.', 'A reservation cannot be released until its deposit is fully refunded.'], ['Không có đặt chỗ trực tuyến hoặc hoàn tiền tự động.', 'There is no online booking or automatic refund processing.']]
  },
  {
    file: 'module_12_orders.html', title: ['Đơn hàng & thanh toán', 'Orders & Payments'], group: ['Bán hàng & kho', 'Sales & inventory'],
    purpose: ['Quản lý đơn bán vật nuôi/sản phẩm, thanh toán một phần, tiền giữ và quy tắc tồn kho liên quan.', 'Manages animal/product sales, partial payments, deposits and related inventory rules.'],
    responsibilities: [['Đơn hàng và dòng hàng', 'Orders and line items'], ['Trạng thái thanh toán', 'Payment status'], ['Đặt cọc và số dư', 'Deposits and balances'], ['Giữ/trả tồn kho theo trạng thái đơn', 'Reserve/release stock by order state']],
    workflow: [['Chọn khách hàng và mặt hàng', 'Select a customer and items'], ['Tính giá và quy tắc thành viên', 'Apply pricing and membership rules'], ['Ghi thanh toán hoặc tiền cọc', 'Record payment or deposit'], ['Cập nhật tồn kho theo vòng đời đơn', 'Update stock through the order lifecycle']],
    operations: [['Tạo đơn hàng', 'Create an order'], ['Thêm sản phẩm hoặc vật nuôi', 'Add products or an animal'], ['Áp dụng giá thành viên khi đủ điều kiện', 'Apply member pricing when eligible'], ['Ghi thanh toán một phần', 'Record a partial payment'], ['Giữ tồn cho đơn đang chờ phù hợp', 'Reserve stock for eligible pending orders'], ['Trừ tồn theo quy tắc combo', 'Deduct stock according to combo rules'], ['Hủy đơn và giải phóng tồn giữ', 'Cancel an order and release reserved stock'], ['Đối chiếu số dư còn lại', 'Reconcile the remaining balance'], ['Xác nhận thanh toán do nhân viên ghi', 'Confirm staff-recorded payment'], ['Xem lịch sử trạng thái đơn', 'Review order-state history']],
    limits: [['Nhân viên xác nhận thanh toán trong ứng dụng; không có cổng thanh toán/QR.', 'Staff confirm payment in the app; there is no payment gateway or QR integration.'], ['Bill nội bộ không đồng nghĩa hóa đơn thuế pháp lý.', 'An internal bill is not a legal tax invoice.'], ['Quy tắc giữ/trả tồn cần được kiểm thử cùng trường hợp hủy đơn.', 'Stock reservation/release rules should be tested with cancellations.']]
  },
  {
    file: 'module_13_memberships.html', title: ['Hội viên & thanh toán nội bộ', 'Memberships & Internal Billing'], group: ['Bán hàng & kho', 'Sales & inventory'],
    purpose: ['Quản lý gói hội viên, thẻ, hóa đơn nội bộ, lịch thanh toán và quyền lợi áp dụng.', 'Manages membership plans, cards, internal bills, payment schedules and eligible benefits.'],
    responsibilities: [['Gói và điều kiện hội viên', 'Plans and membership terms'], ['Hồ sơ hội viên và thẻ', 'Membership records and cards'], ['Bill nội bộ và đợt thanh toán', 'Internal bills and installments'], ['Giảm giá/quyền lợi trong nghiệp vụ', 'Discounts/benefits in operations']],
    workflow: [['Cấu hình gói tham chiếu', 'Configure a reference plan'], ['Tạo membership và thẻ', 'Create a membership and card'], ['Ghi nhận các khoản thanh toán', 'Record payments'], ['Kích hoạt/gia hạn theo điều kiện thanh toán', 'Activate/extend under settlement rules']],
    operations: [['Tạo gói hội viên', 'Create a membership plan'], ['Tạo membership cho khách hàng', 'Create a customer membership'], ['Phát hành thẻ nội bộ', 'Issue an internal card'], ['Tạo bill nội bộ', 'Create an internal bill'], ['Lập lịch đợt thanh toán', 'Schedule installments'], ['Ghi nhận thanh toán từng đợt', 'Record installment payments'], ['Kích hoạt khi đáp ứng điều kiện', 'Activate when conditions are met'], ['Gia hạn theo quy tắc', 'Extend under rules'], ['Áp dụng giảm giá khi đủ điều kiện', 'Apply eligible discounts'], ['Rà soát trạng thái membership', 'Review membership status']],
    limits: [['Công cụ dành cho quản trị khách hàng hiện có, không có đăng ký công khai.', 'This administers existing customers; there is no public signup.'], ['Không tự gia hạn hoặc thu tiền qua payment gateway.', 'There is no automatic renewal or gateway collection.'], ['Bill nội bộ không phải hóa đơn thuế hoặc PDF invoice pháp lý.', 'Internal bills are not legal tax invoices or PDF invoices.']]
  },
  {
    file: 'module_14_services.html', title: ['Dịch vụ & lịch hẹn', 'Services & Scheduling'], group: ['Dịch vụ', 'Services'],
    purpose: ['Quản lý cấu hình dịch vụ, ước tính giá, lịch hẹn, phân công nhân viên và trạng thái thực hiện.', 'Manages service configuration, price estimates, appointments, staff assignment and execution states.'],
    responsibilities: [['Danh mục dịch vụ và gói giá tham chiếu', 'Service catalog and reference pricing'], ['Thông tin khách hàng và tên/loài vật nuôi ghi trên lịch', 'Customer details and pet name/species recorded on a booking'], ['Lịch hẹn, nhân viên phụ trách và trạng thái', 'Appointments, assigned staff and status'], ['Ước tính giá và quyền lợi hội viên áp dụng', 'Price estimates and eligible membership benefits']],
    workflow: [['Chọn khách hàng, nhập tên/loài vật nuôi và chọn dịch vụ', 'Select a customer, enter pet name/species and choose a service'], ['Ước tính giá trước khi lưu lịch', 'Estimate price before saving a booking'], ['Phân công nhân viên và xác nhận giờ hẹn', 'Assign staff and confirm the appointment time'], ['Theo dõi đến hoàn tất/hủy/không đến', 'Track through completion/cancellation/no-show']],
    operations: [['Tạo dịch vụ tham chiếu', 'Create a reference service'], ['Cập nhật cấu hình và giá', 'Update configuration and price'], ['Chọn khách hàng; nhập tên và loài vật nuôi', 'Select customer; enter pet name and species'], ['Ước tính giá trước khi lưu', 'Estimate price before saving'], ['Tạo lịch hẹn có mã duy nhất', 'Create an appointment with a unique code'], ['Phân công nhân viên', 'Assign staff'], ['Đánh dấu received', 'Mark received'], ['Đánh dấu in progress', 'Mark in progress'], ['Đánh dấu completed/canceled/no-show', 'Mark completed/canceled/no-show'], ['Rà soát quyền lợi dịch vụ trả trước', 'Review prepaid service allowances']],
    limits: [['Lịch hẹn lưu customer_id cùng tên và loài vật nuôi; hiện không lưu pet-profile ID.', 'Appointments store customer_id with pet name and species; the current schema does not store a pet-profile ID.'], ['Giá dịch vụ là dữ liệu tham chiếu cần xác minh trước khi vận hành thật.', 'Service prices are reference data and must be validated before live use.'], ['Không tự động sắp lịch hoặc thu tiền; trạng thái do nhân viên cập nhật.', 'Scheduling and payment collection are not automated; staff update appointment status.']]
  },
  {
    file: 'module_15_inventory.html', title: ['Sản phẩm & tồn kho', 'Products & Inventory'], group: ['Bán hàng & kho', 'Sales & inventory'],
    purpose: ['Quản lý danh mục sản phẩm, biến động số lượng, lô, hạn dùng, cảnh báo và phân loại dinh dưỡng.', 'Manages product catalog, quantity movements, batches, expiry, alerts and nutrition classification.'],
    responsibilities: [['Sản phẩm, nhóm và SKU', 'Products, groups and SKUs'], ['Nhập/xuất và số lượng tồn', 'Inbound/outbound movements and stock'], ['Lô hàng và hạn dùng', 'Batches and expiry dates'], ['Cảnh báo và quy tắc phân loại', 'Alerts and classification rules']],
    workflow: [['Tạo hoặc rà soát danh mục', 'Create or review the catalog'], ['Nhập số lượng và lô thực tế', 'Enter actual quantities and batches'], ['Ghi biến động kho', 'Record stock movements'], ['Rà soát cảnh báo thấp/gần hết hạn', 'Review low/near-expiry alerts']],
    operations: [['Tạo SKU sản phẩm', 'Create a product SKU'], ['Cập nhật nhóm và thuộc tính', 'Update group and attributes'], ['Nhập số lượng tồn thủ công', 'Enter stock manually'], ['Ghi lô và hạn dùng', 'Record batch and expiry'], ['Ghi nhập/xuất kho', 'Record stock movement'], ['Áp dụng FEFO khi phân bổ phù hợp', 'Apply FEFO where allocation applies'], ['Rà soát cảnh báo tồn thấp', 'Review low-stock alerts'], ['Rà soát lô gần hết hạn', 'Review near-expiry batches'], ['Kiểm tra giữ tồn từ đơn hàng', 'Check order reservations'], ['Cập nhật hồ sơ phân loại dinh dưỡng', 'Update nutrition classification']],
    limits: [['Số lượng không tự tạo từ dữ liệu nhà cung cấp; phải nhập/xác nhận thực tế.', 'Quantities are not generated from supplier data; enter/verify actual stock.'], ['Catalog seed và giá là dữ liệu demo cần cửa hàng rà soát.', 'Seed catalog and prices are demo data for store review.'], ['Thông tin dinh dưỡng không phải hướng dẫn y tế thú y.', 'Nutrition data is not veterinary medical guidance.']]
  },
  {
    file: 'module_16_reports.html', title: ['Báo cáo vận hành', 'Operational Reports'], group: ['Nền tảng', 'Platform'],
    purpose: ['Tổng hợp dữ liệu đã lưu về kho, bán hàng, sức khỏe và khách hàng để phục vụ rà soát nội bộ.', 'Summarizes saved inventory, sales, health and customer data for internal review.'],
    responsibilities: [['Báo cáo tồn kho', 'Inventory reports'], ['Báo cáo bán hàng', 'Sales reports'], ['Báo cáo sức khỏe', 'Health reports'], ['Tóm tắt khách hàng và xuất CSV/PDF theo hỗ trợ hiện có', 'Customer summaries and CSV/PDF export where supported']],
    workflow: [['Chọn loại báo cáo', 'Select report type'], ['Chọn bộ lọc/khoảng ngày', 'Choose filters/date range'], ['Đọc kết quả theo định nghĩa chỉ số', 'Read results using metric definitions'], ['Xuất tệp nếu chức năng hỗ trợ', 'Export if the feature supports it']],
    operations: [['Chọn báo cáo tồn kho', 'Select an inventory report'], ['Chọn báo cáo bán hàng', 'Select a sales report'], ['Chọn báo cáo sức khỏe', 'Select a health report'], ['Chọn tóm tắt khách hàng', 'Select a customer summary'], ['Đặt khoảng ngày', 'Set a date range'], ['Áp dụng bộ lọc', 'Apply filters'], ['Kiểm tra trạng thái không có dữ liệu', 'Check the no-data state'], ['Đối chiếu tổng với bản ghi nguồn', 'Reconcile totals with source records'], ['Xuất CSV khi có hỗ trợ', 'Export CSV where supported'], ['Xuất PDF khi có hỗ trợ', 'Export PDF where supported']],
    limits: [['Kết quả phản ánh dữ liệu đã lưu và khoảng thời gian chọn.', 'Results reflect stored data and the selected date range.'], ['Không phải báo cáo kiểm toán tài chính hoặc hóa đơn thuế.', 'Reports are not audited accounts or tax invoices.'], ['Chỉ số cần định nghĩa kỳ, đơn vị và xử lý hủy/hoàn trước khi so sánh.', 'Define periods, units and cancellation/refund handling before comparison.']]
  },
  {
    file: 'module_17_alerts.html', title: ['Cảnh báo & sao lưu', 'Alerts & Backup'], group: ['Nền tảng', 'Platform'],
    purpose: ['Hiển thị cảnh báo kho/chăm sóc/tiêm chủng và hỗ trợ tạo bản sao lưu SQLite theo yêu cầu.', 'Surfaces stock/care/vaccination alerts and supports on-demand SQLite backup creation.'],
    responsibilities: [['Cảnh báo tồn thấp và gần hết hạn', 'Low-stock and near-expiry alerts'], ['Nhắc chăm sóc và lịch tiêm', 'Care and vaccination reminders'], ['Tạo bản sao lưu theo yêu cầu', 'On-demand backup creation'], ['Rà soát trạng thái thông báo', 'Review notification status']],
    workflow: [['Đọc cảnh báo phát sinh từ dữ liệu', 'Review alerts generated from records'], ['Mở bản ghi nguồn để xử lý', 'Open the source record to act'], ['Tạo backup khi cần', 'Create a backup when needed'], ['Xác minh tệp và lập lịch sao lưu bên ngoài', 'Verify the file and schedule backups externally']],
    operations: [['Rà soát cảnh báo tồn thấp', 'Review low-stock alerts'], ['Rà soát lô gần hết hạn', 'Review near-expiry batches'], ['Rà soát nhắc chăm sóc', 'Review care reminders'], ['Rà soát lịch tiêm', 'Review vaccination schedules'], ['Mở bản ghi nguồn của cảnh báo', 'Open the alert source record'], ['Đánh dấu/đóng cảnh báo theo chức năng', 'Acknowledge/close an alert where supported'], ['Chọn vị trí backup', 'Select a backup location'], ['Tạo bản sao SQLite theo yêu cầu', 'Create an on-demand SQLite copy'], ['Kiểm tra tệp backup được tạo', 'Verify the backup file'], ['Lập lịch và kiểm thử khôi phục bên ngoài', 'Schedule and test restoration externally']],
    limits: [['Backup là thao tác thủ công/theo yêu cầu; UI không lập lịch tự động.', 'Backup is manual/on demand; the UI does not schedule it automatically.'], ['Ứng dụng không cung cấp quy trình restore trong UI hiện tại.', 'The current UI does not provide a restore workflow.'], ['Tệp backup cần lưu ở nơi an toàn và kiểm thử phục hồi theo quy trình riêng.', 'Store backups securely and test recovery using a separate procedure.']]
  }
];

const documents = [
  { file: '../index.html', title: ['Trang chủ PetCare', 'PetCare project hub'], group: ['Tổng quan', 'Overview'], summary: ['Cổng vào bộ tài liệu và giới thiệu phạm vi hệ thống.', 'Entry point to the document set and system scope.'] },
  { file: '../project_overview.html', title: ['Tổng quan dự án', 'Project overview'], group: ['Tổng quan', 'Overview'], summary: ['Mục tiêu, đối tượng sử dụng, phạm vi và kiến trúc.', 'Goals, users, scope and architecture.'] },
  { file: '../executive_summary.html', title: ['Báo cáo dự án & tóm tắt điều hành', 'Executive summary & project report'], group: ['Báo cáo', 'Reports'], summary: ['Quyết định pilot, kiến trúc, nghiệp vụ, kiểm soát và giới hạn.', 'Pilot decision, architecture, workflows, controls and limits.'] },
  { file: '../business_case.html', title: ['Cơ sở kinh doanh', 'Business case'], group: ['Chiến lược', 'Strategy'], summary: ['Nhu cầu, mô hình giả định, chi phí, rủi ro và tiêu chí pilot.', 'Needs, scenario model, costs, risks and pilot criteria.'] },
  { file: '../report_business_review.html', title: ['Đánh giá nghiệp vụ', 'Business review'], group: ['Chiến lược', 'Strategy'], summary: ['Giá trị kỳ vọng, rủi ro và cách đánh giá bằng bằng chứng.', 'Expected value, risks and evidence-based evaluation.'] },
  { file: '../roadmap.html', title: ['Lộ trình đề xuất', 'Proposed roadmap'], group: ['Chiến lược', 'Strategy'], summary: ['Các hướng phát triển cần ưu tiên và xác nhận.', 'Proposed directions to prioritize and validate.'] },
  { file: '../workflow.html', title: ['Bản đồ quy trình PetCare', 'PetCare workflow map'], group: ['Quy trình', 'Workflows'], summary: ['Luồng dùng chung, nhánh nghiệp vụ, trạng thái, quyền và ngoại lệ.', 'Shared flow, branches, states, roles and exceptions.'] },
  { file: '../project_workflow_full.html', title: ['Luồng hệ thống đầy đủ', 'Full system workflow'], group: ['Quy trình', 'Workflows'], summary: ['Ranh giới giao diện, nghiệp vụ, SQLite và kiểm soát.', 'Boundaries between UI, business logic, SQLite and controls.'] },
  { file: '../workflow_story.html', title: ['Câu chuyện quy trình', 'Workflow story'], group: ['Quy trình', 'Workflows'], summary: ['Deck demo 10 bước về lịch dịch vụ của thú cưng khách hàng.', 'A 10-step demo story for a customer-owned pet appointment.'] },
  { file: '../report_final.html', title: ['Báo cáo dự án PetCare', 'PetCare project report'], group: ['Báo cáo', 'Reports'], summary: ['Thiết kế, chức năng, bảo mật và giới hạn hiện tại.', 'Current design, functions, security and limitations.'] },
  { file: '../report_kpi_board.html', title: ['Bảng chỉ số vận hành', 'Operational KPI board'], group: ['Báo cáo', 'Reports'], summary: ['Mẫu định nghĩa KPI; không có dữ liệu trực tiếp.', 'KPI-definition template; no live data.'] },
  { file: '../operations_snapshot.html', title: ['Ảnh chụp vận hành', 'Operations snapshot'], group: ['Báo cáo', 'Reports'], summary: ['Bố cục báo cáo minh họa, không phải kết quả đo.', 'Illustrative report layout, not measured results.'] },
  { file: '../project_slides_final.html', title: ['Thuyết trình dự án · 12 slide', 'Project presentation · 12 slides'], group: ['Thuyết trình', 'Presentations'], summary: ['Bộ slide song ngữ về dự án PetCare.', 'Bilingual PetCare project deck.'] },
  { file: '../project_slides.html', title: ['Thuyết trình dự án · 8 slide', 'Project presentation · 8 slides'], group: ['Thuyết trình', 'Presentations'], summary: ['Bộ slide song ngữ có điều khiển bàn phím.', 'Bilingual deck with keyboard controls.'] },
  { file: '../slides_demo.html', title: ['Hướng dẫn demo', 'Demo walkthrough'], group: ['Thuyết trình', 'Presentations'], summary: ['Kịch bản trình bày các điểm chạm hệ thống.', 'Presenter guide to system touchpoints.'] },
  { file: '../slides_pitch.html', title: ['Tóm tắt thuyết trình', 'Project pitch'], group: ['Thuyết trình', 'Presentations'], summary: ['Vấn đề, giải pháp, ranh giới và bước tiếp theo.', 'Problem, response, boundaries and next steps.'] },
  { file: '../product_showcase.html', title: ['Giới thiệu sản phẩm', 'Product showcase'], group: ['Sản phẩm', 'Product'], summary: ['Năng lực và hành trình sử dụng PetCare.', 'PetCare capabilities and user journey.'] },
  { file: '../app_interface_preview.html', title: ['Preview giao diện tương tác', 'Interactive interface preview'], group: ['Demo & giao diện', 'Demos & interface'], summary: ['Mô phỏng 19 route, bảng mẫu, lọc và chi tiết.', 'Prototype of 19 routes, sample tables, filters and details.'] },
  { file: '../petcare_demo_full.html', title: ['Demo giao diện theo tab', 'Tabbed interface demo'], group: ['Demo & giao diện', 'Demos & interface'], summary: ['Các panel tổng quan, vật nuôi, kho và dịch vụ.', 'Overview, animal, inventory and service panels.'] },
  { file: '../projext _Full.html', title: ['Danh mục tài liệu cũ', 'Legacy document directory'], group: ['Tài liệu khác', 'Other documents'], summary: ['Trang điều hướng cũ; giữ lại để tương thích liên kết.', 'Legacy directory retained for link compatibility.'] }
];

const catalogEntries = [
  ...documents.map((document) => ({ ...document, kind: 'document' })),
  ...modules.map((module) => ({ file: module.file, title: module.title, group: module.group, summary: module.purpose, kind: 'module' }))
];

const hub = {
  file: 'index.html',
  catalogEntries,
  html: `<!doctype html>
<html lang="vi">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Duyệt và xem trực tiếp toàn bộ báo cáo, slide, workflow và tài liệu 17 phân hệ PetCare.">
  <title>PetCare | Document Workbench</title>
  <link rel="stylesheet" href="../styles/petcare_pages.css">
  <style>
    .page-shell { width: min(1760px, calc(100% - 32px)); padding: 18px 0 18px; }
    .page-hero, .section-head, .note, .site-footer { display: none; }
    .section { margin-top: 0; }
    .module-browser { display: grid; grid-template-columns: minmax(270px, 330px) minmax(0, 1fr); gap: 12px; height: calc(100vh - 112px); min-height: 620px; align-items: stretch; }
    .module-list { display: grid; grid-template-rows: auto auto minmax(0, 1fr); min-width: 0; min-height: 0; overflow: hidden; border: 1px solid var(--line); border-radius: 6px; background: var(--surface); }
    .module-tools { display: grid; grid-template-columns: 1fr 1fr; align-items: end; gap: 7px; margin: 0; padding: 10px; border-bottom: 1px solid var(--line); }
    .module-tools label { display: grid; gap: 5px; color: var(--muted); font-size: 11px; }
    .module-tools input, .module-tools select { width: 100%; min-width: 0; height: 40px; padding: 8px 10px; border: 1px solid var(--line); border-radius: 5px; color: var(--ink); background: var(--surface); font: inherit; font-size: 13px; }
    .module-tools input:focus, .module-tools select:focus, .clear-filters:focus-visible, .preview-button:focus-visible, .open-link:focus-visible { outline: 2px solid var(--green); outline-offset: 2px; }
    .clear-filters { min-height: 40px; padding: 7px 10px; border: 1px solid var(--line); border-radius: 5px; color: var(--green); background: var(--surface); font: inherit; font-size: 12px; cursor: pointer; }
    .module-count { min-height: 18px; margin: 0; padding: 5px 10px; color: var(--muted); font-size: 10px; }
    .module-tile[hidden], .no-results[hidden] { display: none; }
    .no-results { padding: 22px; border: 1px dashed var(--line); border-radius: 5px; color: var(--muted); background: var(--surface); }
    .module-grid { grid-template-columns: 1fr; grid-auto-rows: max-content; align-content: start; gap: 0; min-height: 0; overflow: auto; padding: 0; }
    .module-tile { display: grid; grid-template-columns: minmax(0,1fr) auto; align-items: center; gap: 0 8px; min-width: 0; min-height: 0; padding: 0; border: 0; border-bottom: 1px solid var(--line); border-radius: 0; background: transparent; }
    .module-tile:hover { transform: none; box-shadow: none; background: var(--paper); }
    .file-select { grid-column: 1; display: flex; min-width: 0; flex-direction: column; gap: 2px; padding: 9px 10px; border: 0; border-left: 3px solid transparent; color: var(--ink); background: transparent; font: inherit; text-align: left; cursor: pointer; }
    .file-select:hover { color: var(--green); }
    .file-select:focus-visible, .file-select[aria-pressed="true"] { border-left-color: var(--green); outline: 0; background: #edf5ef; }
    .module-tile .tile-kicker { margin: 0; color: var(--muted); font-size: 9px; }
    .module-tile .tile-filename { color: var(--green); font-family: ui-monospace, Consolas, monospace; font-size: 10px; overflow-wrap: anywhere; }
    .module-tile .file-title { font-family: 'Newsreader', Georgia, serif; font-size: 14px; line-height: 1.25; }
    .module-tile p { display: none; }
    .module-actions { grid-column: 2; display: flex; align-items: center; padding-right: 8px; }
    .open-link { min-height: 30px; display: inline-flex; align-items: center; justify-content: center; padding: 4px 7px; border: 1px solid var(--line); border-radius: 4px; color: var(--muted); background: var(--surface); font: inherit; font-size: 10px; cursor: pointer; white-space: nowrap; }
    .open-link:hover { border-color: var(--green); color: var(--green); }
    .preview-panel { display: flex; min-width: 0; min-height: 0; flex-direction: column; overflow: hidden; border: 1px solid var(--line); border-radius: 6px; background: var(--surface); box-shadow: var(--shadow); }
    .preview-heading { display: grid; grid-template-columns: minmax(0,1fr) auto; align-items: center; gap: 8px 16px; padding: 12px 16px; border-bottom: 1px solid var(--line); }
    .preview-heading h3 { margin: 3px 0 0; font-size: 20px; }
    .presentation-tools { display: flex; flex: 0 0 auto; align-items: center; gap: 6px; }
    .presentation-tools button { min-height: 36px; padding: 6px 10px; border: 1px solid var(--line); border-radius: 5px; color: var(--ink); background: var(--surface); font: inherit; font-size: 12px; cursor: pointer; }
    .presentation-tools button:hover, .presentation-tools button:focus-visible { border-color: var(--green); color: var(--green); outline-color: var(--green); }
    .slide-position { min-width: 54px; color: var(--muted); font-size: 11px; text-align: center; font-variant-numeric: tabular-nums; }
    .preview-status { grid-column: 1 / -1; color: var(--muted); font-size: 10px; }
    .preview-status[data-state="ready"] { color: var(--green); }
    .preview-status[data-state="error"] { color: var(--coral); }
    #module-preview { display: block; width: 100%; flex: 1; min-height: 0; border: 0; background: var(--paper); }
    .preview-panel:fullscreen { display: flex; flex-direction: column; padding: 12px; border: 0; border-radius: 0; background: var(--paper); }
    .preview-panel:fullscreen #module-preview { flex: 1; height: auto; min-height: 0; }
    .preview-panel:fullscreen .preview-heading, .preview-panel:fullscreen .preview-footer { background: var(--surface); }
    .preview-footer { display: flex; flex-wrap: wrap; justify-content: space-between; gap: 8px 14px; padding: 12px 15px; border-top: 1px solid var(--line); color: var(--muted); font-size: 11px; }
    .preview-footer a { color: var(--green); font-weight: 700; }
    @media (max-width: 900px) { .module-browser { grid-template-columns: minmax(230px, .38fr) minmax(0, .62fr); } }
    @media (max-width: 680px) { .page-shell { width: calc(100% - 20px); padding: 10px 0; } .module-browser { grid-template-columns: 1fr; grid-template-rows: minmax(180px, 30vh) minmax(0, 1fr); height: calc(100dvh - 96px); min-height: 620px; gap: 8px; } .module-tools { grid-template-columns: 1fr 1fr; } .module-tools label:first-child { grid-column: 1 / -1; } .clear-filters { grid-column: 1 / -1; } .preview-heading { grid-template-columns: 1fr; padding: 9px 12px; } .presentation-tools { width: 100%; } .preview-status { grid-column: 1; } .preview-footer { padding: 7px 10px; } }
  </style>
</head>
<body>
  <header class="site-header"><div class="header-inner">
    <a class="brand" href="../index.html"><span class="brand-mark">P</span> PetCare / Library</a>
    <div class="header-actions"><nav class="header-nav" aria-label="Primary navigation"><a href="../index.html">Project hub</a><a href="../workflow.html">Workflow</a></nav>
    <button class="lang-button" type="button" onclick="document.body.classList.toggle('show-en');this.textContent=document.body.classList.contains('show-en')?'VI':'EN'">EN</button></div>
  </div></header>
  <main class="page-shell">
    <section class="page-hero"><span class="eyebrow">37 previewable HTML documents</span>
      <h1><span data-lang="vi">Trung tâm báo cáo & tài liệu PetCare</span><span data-lang="en">PetCare Reports & Documents</span></h1>
      <p class="lede"><span data-lang="vi">Danh mục báo cáo, quy trình, slide, demo và 17 tài liệu phân hệ. Chọn một mục để xem nội dung thật ngay bên cạnh.</span><span class="en" data-lang="en">Browse reports, workflows, slides, demos and all 17 module documents. Select an item to preview the actual page alongside the catalog.</span></p>
      <div class="hero-foot"><span class="tag">20 project pages</span><span class="tag">17 module references</span><span class="tag">Live HTML preview</span><span class="tag">Local-first PetCare</span></div>
    </section>
    <section class="section" id="modules"><div class="section-head"><div><span class="eyebrow">Document workbench</span><h2><span data-lang="vi">Duyệt tài liệu</span><span data-lang="en">Document library</span></h2></div><p><span data-lang="vi">Chọn Xem để nạp tài liệu trong khung; Mở riêng để xem toàn trang. Danh mục liệt kê 37 trang nội dung, không nhúng chính trang danh mục.</span><span data-lang="en">Select Preview to load a page here; Open separately for a full page. The catalog lists 37 content pages and does not embed itself.</span></p></div>
      <div class="module-browser">
        <div class="module-list">
          <div class="module-tools">
            <label><span><span data-lang="vi">Tìm tài liệu</span><span data-lang="en">Search documents</span></span><input id="module-search" type="search" autocomplete="off" placeholder="Tên hoặc nội dung / Name or content"></label>
            <label><span><span data-lang="vi">Loại</span><span data-lang="en">Type</span></span><select id="document-kind"><option value="all">Tất cả / All</option><option value="document">Báo cáo & tài liệu / Reports & docs</option><option value="module">Phân hệ / Modules</option></select></label>
            <label><span><span data-lang="vi">Nhóm</span><span data-lang="en">Group</span></span><select id="module-group"><option value="all">Tất cả nhóm / All groups</option><option value="overview">Tổng quan / Overview</option><option value="strategy">Chiến lược / Strategy</option><option value="workflows">Quy trình / Workflows</option><option value="reports">Báo cáo / Reports</option><option value="presentations">Thuyết trình / Presentations</option><option value="product">Sản phẩm / Product</option><option value="demos-interface">Demo & giao diện / Demos & interface</option><option value="other-documents">Tài liệu khác / Other documents</option><option value="platform">Nền tảng / Platform</option><option value="animal-care">Chăm sóc động vật / Animal care</option><option value="sales-inventory">Bán hàng & kho / Sales & inventory</option><option value="services">Dịch vụ / Services</option></select></label>
            <button class="clear-filters" id="clear-filters" type="button"><span data-lang="vi">Xóa lọc</span><span data-lang="en">Clear</span></button>
          </div>
          <p class="module-count" id="module-count" aria-live="polite"><span data-lang="vi"></span><span data-lang="en"></span></p>
          <div class="grid module-grid">
${catalogEntries.map((entry, index) => { const href = encodeURI(entry.file); const filename = entry.file.split('/').pop(); const groupName = entry.group[1]; const groupKey = groupName.toLocaleLowerCase().replaceAll(' & ', '-').replaceAll(' ', '-'); return `            <article class="tile module-tile" data-kind="${entry.kind}" data-group="${groupKey}" data-search="${entry.title.join(' ')} ${entry.summary.join(' ')} ${filename}"><button class="file-select" type="button" data-preview="${href}" data-title-vi="${entry.title[0]}" data-title-en="${entry.title[1]}" aria-pressed="${entry.file === '../executive_summary.html'}"><span class="tile-kicker">${String(index + 1).padStart(2, '0')} / ${entry.kind === 'module' ? 'Module' : groupName}</span><code class="tile-filename">${filename}</code><span class="file-title"><span data-lang="vi">${entry.title[0]}</span><span data-lang="en">${entry.title[1]}</span></span></button><p><span data-lang="vi">${entry.summary[0]}</span><span class="en" data-lang="en">${entry.summary[1]}</span></p><div class="module-actions"><a class="open-link" href="${href}" target="_blank" rel="noopener" aria-label="Open ${filename} separately" title="Open separately">↗</a></div></article>`; }).join('\n')}
        </div>
          <p class="no-results" id="no-results" hidden><span data-lang="vi">Không tìm thấy tài liệu phù hợp. Hãy thử từ khóa hoặc bộ lọc khác.</span><span data-lang="en">No matching documents. Try another search or filter.</span></p>
        </div>
        <aside class="preview-panel" aria-label="Document preview">
          <div class="preview-heading"><div><span class="eyebrow"><span data-lang="vi">Màn hình trình chiếu</span><span data-lang="en">Presentation screen</span></span><h3 id="preview-title"><span data-lang="vi">${documents[2].title[0]}</span><span data-lang="en">${documents[2].title[1]}</span></h3></div><div class="presentation-tools"><button id="previous-document" type="button" aria-label="Previous document" title="Previous document (Left arrow)">←</button><span id="slide-position" class="slide-position" aria-live="polite">03 / 37</span><button id="next-document" type="button" aria-label="Next document" title="Next document (Right arrow)">→</button><button id="present-document" type="button" aria-pressed="false"><span data-lang="vi">Toàn màn hình</span><span data-lang="en">Present</span></button></div><span id="preview-status" class="preview-status" aria-live="polite"><span data-lang="vi">Đang tải tài liệu</span><span data-lang="en">Loading document</span></span></div>
          <iframe id="module-preview" src="${encodeURI(documents[2].file)}" title="${documents[2].title[1]}" loading="eager" allow="fullscreen"></iframe>
          <div class="preview-footer"><span data-lang="vi">Hiển thị HTML trong thư mục dự án ở chế độ xem trước.</span><span data-lang="en">Displays project HTML in a preview-only frame.</span><a id="preview-open" href="${encodeURI(documents[2].file)}" target="_blank" rel="noopener"><span data-lang="vi">Mở tài liệu ↗</span><span data-lang="en">Open document ↗</span></a></div>
        </aside>
      </div>
    </section>
    <div class="note"><strong>Scope / Phạm vi.</strong> <span data-lang="vi">Các chỉ số trong ví dụ cần được xem là mẫu trừ khi truy vấn từ dữ liệu thật. Danh sách kiểm tra là hướng dẫn rà soát, không thay thế kiểm chứng mã nguồn.</span><span data-lang="en">Example metrics are sample values unless queried from real data. Checklists are review guidance, not a substitute for source verification.</span></div>
    <footer class="site-footer"><span>PetCare / Document library</span><a href="../index.html">Back to project hub</a></footer>
  </main>
  <script>
    const previewFrame = document.getElementById('module-preview');
    const previewOpen = document.getElementById('preview-open');
    const previewStatus = document.getElementById('preview-status');
    const previewButtons = [...document.querySelectorAll('[data-preview]')];
    const presentationPanel = document.querySelector('.preview-panel');
    const slidePosition = document.getElementById('slide-position');
    const presentButton = document.getElementById('present-document');
    const moduleTiles = [...document.querySelectorAll('.module-tile')];
    const moduleSearch = document.getElementById('module-search');
    const documentKind = document.getElementById('document-kind');
    const moduleGroup = document.getElementById('module-group');
    const moduleCount = document.getElementById('module-count');
    const noResults = document.getElementById('no-results');
    let activePreviewButton = previewButtons.findIndex((button) => button.getAttribute('aria-pressed') === 'true');
    const visiblePreviewButtons = () => previewButtons.filter((button) => !button.closest('.module-tile').hidden);
    const updateSlidePosition = () => {
      const visible = visiblePreviewButtons();
      const currentIndex = visible.indexOf(previewButtons[activePreviewButton]);
      const total = visible.length;
      const position = currentIndex >= 0 ? currentIndex + 1 : 0;
      slidePosition.textContent = String(position).padStart(2, '0') + ' / ' + String(total).padStart(2, '0');
      document.getElementById('previous-document').disabled = total === 0;
      document.getElementById('next-document').disabled = total === 0;
    };
    const selectPreview = (button) => {
      if (!button) return;
      activePreviewButton = previewButtons.indexOf(button);
      previewButtons.forEach((item) => item.setAttribute('aria-pressed', String(item === button)));
      previewFrame.title = button.dataset.titleEn;
      previewOpen.href = button.dataset.preview;
      document.querySelector('#preview-title [data-lang="vi"]').textContent = button.dataset.titleVi;
      document.querySelector('#preview-title [data-lang="en"]').textContent = button.dataset.titleEn;
      updateSlidePosition();
      setPreviewStatus('loading');
      previewFrame.src = button.dataset.preview;
    };
    const updateModuleList = () => {
      const query = moduleSearch.value.trim().toLocaleLowerCase();
      const kind = documentKind.value;
      const group = moduleGroup.value;
      let visibleCount = 0;
      for (const tile of moduleTiles) {
        const matches = tile.textContent.toLocaleLowerCase().includes(query)
          && (kind === 'all' || tile.dataset.kind === kind)
          && (group === 'all' || tile.dataset.group === group);
        tile.hidden = !matches;
        if (matches) visibleCount += 1;
      }
      noResults.hidden = visibleCount !== 0;
      moduleCount.querySelector('[data-lang="vi"]').textContent = visibleCount + ' / ' + moduleTiles.length + ' tài liệu';
      moduleCount.querySelector('[data-lang="en"]').textContent = visibleCount + ' / ' + moduleTiles.length + ' documents';
      const visible = visiblePreviewButtons();
      if (visible.length && !visible.includes(previewButtons[activePreviewButton])) selectPreview(visible[0]);
      updateSlidePosition();
    };
    const setPreviewStatus = (state) => {
      previewStatus.dataset.state = state;
      previewStatus.querySelector('[data-lang="vi"]').textContent = state === 'ready' ? 'Đã tải' : state === 'error' ? 'Không tải được' : 'Đang tải tài liệu';
      previewStatus.querySelector('[data-lang="en"]').textContent = state === 'ready' ? 'Loaded' : state === 'error' ? 'Could not load' : 'Loading document';
    };
    previewFrame.addEventListener('load', () => setPreviewStatus('ready'));
    moduleSearch.addEventListener('input', updateModuleList);
    documentKind.addEventListener('change', updateModuleList);
    moduleGroup.addEventListener('change', updateModuleList);
    document.getElementById('clear-filters').addEventListener('click', () => {
      moduleSearch.value = '';
      documentKind.value = 'all';
      moduleGroup.value = 'all';
      updateModuleList();
      moduleSearch.focus();
    });
    const movePresentation = (direction) => {
      const visible = visiblePreviewButtons();
      const current = visible.indexOf(previewButtons[activePreviewButton]);
      const start = current < 0 ? 0 : current;
      const next = (start + direction + visible.length) % visible.length;
      selectPreview(visible[next]);
    };
    document.getElementById('previous-document').addEventListener('click', () => movePresentation(-1));
    document.getElementById('next-document').addEventListener('click', () => movePresentation(1));
    presentButton.addEventListener('click', async () => {
      try {
        if (document.fullscreenElement === presentationPanel) {
          await document.exitFullscreen();
        } else if (presentationPanel.requestFullscreen) {
          await presentationPanel.requestFullscreen();
        }
      } catch {
        presentButton.setAttribute('aria-pressed', 'false');
      }
    });
    document.addEventListener('fullscreenchange', () => {
      const isPresenting = document.fullscreenElement === presentationPanel;
      presentButton.setAttribute('aria-pressed', String(isPresenting));
      presentButton.querySelector('[data-lang="vi"]').textContent = isPresenting ? 'Thoát trình chiếu' : 'Toàn màn hình';
      presentButton.querySelector('[data-lang="en"]').textContent = isPresenting ? 'Exit presentation' : 'Present';
    });
    const handlePresentationKey = (event) => {
      if (document.fullscreenElement !== presentationPanel || event.target.closest('input, select, textarea, [contenteditable="true"]')) return;
      if (event.key === 'Escape') {
        event.preventDefault();
        document.exitFullscreen();
      } else if (event.key === 'ArrowRight' || event.key === 'PageDown') {
        event.preventDefault();
        movePresentation(1);
      } else if (event.key === 'ArrowLeft' || event.key === 'PageUp') {
        event.preventDefault();
        movePresentation(-1);
      }
    };
    document.addEventListener('keydown', handlePresentationKey, true);
    previewFrame.addEventListener('load', () => {
      previewFrame.contentWindow.addEventListener('keydown', handlePresentationKey, true);
    });
    for (const button of previewButtons) {
      button.addEventListener('click', () => {
        selectPreview(button);
      });
    }
    updateModuleList();
  </script>
</body>
</html>`
};

const controls = [
  ['Required information', 'Thông tin bắt buộc', 'Verify required values are present before save.', 'Xác minh trường bắt buộc trước khi lưu.'],
  ['Input validity', 'Tính hợp lệ đầu vào', 'Check accepted format, range and normalization.', 'Kiểm tra định dạng, miền giá trị và chuẩn hóa.'],
  ['Related records', 'Bản ghi liên quan', 'Confirm linked records exist and belong to the intended workflow.', 'Xác nhận bản ghi liên kết tồn tại và thuộc đúng quy trình.'],
  ['Role access', 'Quyền vai trò', 'Verify the action is available only to an authorized role.', 'Xác minh thao tác chỉ dành cho vai trò được phép.'],
  ['State transition', 'Chuyển trạng thái', 'Check that the transition is allowed from the current state.', 'Kiểm tra chuyển trạng thái hợp lệ từ trạng thái hiện tại.'],
  ['Boundary condition', 'Điều kiện biên', 'Test empty, minimum, maximum and just-outside-boundary values where applicable.', 'Thử dữ liệu rỗng, biên dưới, biên trên và vượt biên nếu áp dụng.'],
  ['Duplicate handling', 'Xử lý trùng lặp', 'Check how repeated submissions or matching records are handled.', 'Kiểm tra cách xử lý gửi lặp hoặc bản ghi có dữ liệu khớp.'],
  ['Failure feedback', 'Phản hồi lỗi', 'Confirm validation failures explain what needs correction.', 'Xác nhận lỗi kiểm tra nêu rõ dữ liệu cần sửa.'],
  ['Persistence', 'Lưu bền vững', 'Reopen the record and verify the saved result is still present.', 'Mở lại bản ghi và xác minh kết quả đã lưu còn tồn tại.'],
  ['Traceability', 'Khả năng truy vết', 'Check audit/history records for actions that should be traceable.', 'Kiểm tra audit/lịch sử với thao tác cần truy vết.'],
  ['Privacy', 'Quyền riêng tư', 'Limit displayed and exported data to the operational need.', 'Giới hạn dữ liệu hiển thị/xuất theo nhu cầu vận hành.'],
  ['No-data behavior', 'Trạng thái không dữ liệu', 'Distinguish missing data from a true zero or completed state.', 'Phân biệt thiếu dữ liệu với số 0 hoặc trạng thái hoàn tất thật.']
];

const moduleTestSuites = {
  'module_01_platform.html': ['test_database.py', 'test_main.py'],
  'module_02_accounts.html': ['test_database.py', 'test_main.py'],
  'module_03_dashboard.html': ['test_main.py', 'test_operations.py'],
  'module_04_pets.html': ['test_database.py', 'test_operations.py'],
  'module_05_housing.html': ['test_database.py', 'test_operations.py'],
  'module_06_suppliers.html': ['test_inventory.py', 'test_database.py'],
  'module_07_imports.html': ['test_inventory.py', 'test_operations.py'],
  'module_08_health.html': ['test_operations.py'],
  'module_09_care.html': ['test_operations.py'],
  'module_10_customers.html': ['test_sales.py', 'test_database.py'],
  'module_11_reservations.html': ['test_sales.py'],
  'module_12_orders.html': ['test_sales.py', 'test_inventory.py'],
  'module_13_memberships.html': ['test_memberships.py'],
  'module_14_services.html': ['test_services.py'],
  'module_15_inventory.html': ['test_inventory.py', 'test_product_catalog.py'],
  'module_16_reports.html': ['test_operations.py'],
  'module_17_alerts.html': ['test_operations.py', 'test_database.py']
};

const esc = (value) => value.replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;');
const bilingual = (values, className = '') => `<span class="${className}" data-lang="vi">${esc(values[0])}</span><span class="en ${className}" data-lang="en">${esc(values[1])}</span>`;

function renderPage(module, index) {
  const filename = module.file;
  const prev = modules[index - 1];
  const next = modules[index + 1];
  const responsibilities = module.responsibilities.map((item, itemIndex) => `          <li><span class="tile-kicker">${String(itemIndex + 1).padStart(2, '0')}</span>${bilingual(item)}</li>`).join('\n');
  const workflow = module.workflow.map((item, itemIndex) => `          <li><span class="tile-kicker">${String(itemIndex + 1).padStart(2, '0')}</span>${bilingual(item)}</li>`).join('\n');
  const limits = module.limits.map((item) => `          <li>${bilingual(item)}</li>`).join('\n');
  const testSuites = moduleTestSuites[filename] ?? [];
  const testSuiteList = testSuites.map((suite) => `          <li><code>${esc(suite)}</code></li>`).join('\n');
  const operationLinks = module.operations.map((operation, operationIndex) => `          <li><a href="#check-${String(operationIndex + 1).padStart(2, '0')}">${bilingual(operation)}</a></li>`).join('\n');
  const operationSections = module.operations.map((operation, operationIndex) => {
    const start = operationIndex * controls.length + 1;
    const end = start + controls.length - 1;
    return `        <section class="section" id="check-${String(operationIndex + 1).padStart(2, '0')}">
          <div class="section-head">
            <div><span class="eyebrow">Operation ${String(operationIndex + 1).padStart(2, '0')} / ${module.group[1]}</span>
            <h2>${bilingual(operation)}</h2></div>
            <p>${bilingual(['Mở rộng thao tác thành tiêu chí xác minh đầu vào, quyền, trạng thái, lưu trữ và lỗi.', 'Decompose the operation into input, access, state, persistence and failure checks.'])}</p>
          </div>
          <ol class="checklist" start="${start}">
${renderChecksForOperation(module, operationIndex)}
          </ol>
          <p class="check-range">${bilingual([`Mã kiểm tra ${start}–${end}; đây là tiêu chí rà soát, không phải tuyên bố tự động đã kiểm thử.`, `Check IDs ${start}–${end}; these are review criteria, not a claim of automated test execution.`])}</p>
        </section>`;
  }).join('\n');
  const related = [prev, next].filter(Boolean).map((item) => `        <a class="tile" href="${item.file}"><span class="tile-kicker">${item === prev ? 'Previous module' : 'Next module'}</span><h3>${bilingual(item.title)}</h3><p>${bilingual(item.purpose)}</p></a>`).join('\n');
  return `<!doctype html>
<html lang="vi">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="${esc(module.purpose[0])}">
  <title>PetCare | ${esc(module.title[1])}</title>
  <link rel="stylesheet" href="../styles/petcare_pages.css">
  <style>
    .module-nav { display: flex; gap: 8px; flex-wrap: wrap; margin: 18px 0; }
    .module-nav a { border: 1px solid var(--line); padding: 8px 10px; border-radius: 5px; font-size: 13px; background: var(--surface); }
    .module-nav a:hover { border-color: var(--green); }
    .detail-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }
    .detail-panel { padding: 20px; border: 1px solid var(--line); border-radius: 6px; background: var(--surface); }
    .detail-panel h3 { margin-bottom: 12px; }
    .detail-panel li { margin: 8px 0; }
    .checklist { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; margin: 0; padding: 0; list-style: none; counter-reset: list-item calc(var(--start, 1) - 1); }
    .check-row { min-width: 0; padding: 14px; border: 1px solid var(--line); border-radius: 5px; background: var(--surface); }
    .check-row code { display: inline-block; margin-bottom: 8px; color: var(--green); font-size: 11px; }
    .check-row strong, .check-row > span { display: block; }
    .check-row strong [data-lang="en"], .check-row > span [data-lang="en"] { color: var(--muted); font-weight: 500; }
    .check-row p { margin: 9px 0; font-size: 13px; }
    .check-row p [data-lang="en"] { color: var(--muted); }
    .check-row small { color: var(--muted); font-size: 11px; }
    .check-range { color: var(--muted); font-size: 12px; }
    .scope-list { columns: 2; }
    @media (max-width: 720px) { .checklist, .detail-grid { grid-template-columns: 1fr; } .scope-list { columns: 1; } }
  </style>
</head>
<body>
  <header class="site-header"><div class="header-inner">
    <a class="brand" href="index.html"><span class="brand-mark">P</span> PetCare / ${esc(module.title[0])}</a>
    <div class="header-actions"><nav class="header-nav" aria-label="Primary navigation"><a href="../index.html">Project hub</a><a href="index.html">Modules</a><a href="../workflow.html">Workflow</a></nav>
    <button class="lang-button" type="button" aria-label="Switch language" onclick="document.body.classList.toggle('show-en');this.textContent=document.body.classList.contains('show-en')?'VI':'EN'">EN</button></div>
  </div></header>
  <main class="page-shell">
    <section class="page-hero">
      <span class="eyebrow">Module ${String(index + 1).padStart(2, '0')} / ${esc(module.group[1])}</span>
      <h1>${bilingual(module.title)}</h1>
      <p class="lede">${bilingual(module.purpose)}</p>
      <div class="hero-foot"><span class="tag">${esc(module.group[0])} / ${esc(module.group[1])}</span><span class="tag">Python + PySide6</span><span class="tag">SQLite local</span><span class="tag">Detailed reference</span></div>
    </section>
    <nav class="module-nav" aria-label="Module sections"><a href="#overview">Overview / Tổng quan</a><a href="#workflow">Workflow / Quy trình</a><a href="#operations">Checks / Kiểm tra</a><a href="#evidence">Evidence / Bằng chứng</a><a href="#boundaries">Limits / Giới hạn</a></nav>
    <section class="section" id="overview">
      <div class="section-head"><div><span class="eyebrow">Purpose & ownership</span><h2><span data-lang="vi">Trách nhiệm phân hệ</span><span data-lang="en">Module responsibilities</span></h2></div>
      <p>${bilingual(['Mô tả theo phạm vi ứng dụng hiện có; số liệu ví dụ không được xem là trạng thái trực tiếp.', 'Describes current application scope; example values are not live status.'])}</p></div>
      <div class="detail-grid"><article class="detail-panel"><h3><span data-lang="vi">Phạm vi phụ trách</span><span data-lang="en">Responsibilities</span></h3><ul>
${responsibilities}
      </ul></article><article class="detail-panel"><h3><span data-lang="vi">Luồng công việc chính</span><span data-lang="en">Primary workflow</span></h3><ol>
${workflow}
      </ol></article></div>
    </section>
    <section class="section" id="workflow">
      <div class="section-head"><div><span class="eyebrow">Operational map</span><h2><span data-lang="vi">Danh sách thao tác cần rà soát</span><span data-lang="en">Operations to review</span></h2></div>
      <p>${bilingual(['Đi tới từng thao tác để xem các trường hợp kiểm tra chi tiết.', 'Jump to an operation to review its detailed checks.'])}</p></div>
      <div class="detail-panel"><ol class="scope-list">
${operationLinks}
      </ol></div>
    </section>
    <section class="section" id="operations">
      <div class="section-head"><div><span class="eyebrow">Detailed review matrix</span><h2><span data-lang="vi">Ma trận kiểm tra chi tiết</span><span data-lang="en">Detailed verification matrix</span></h2></div>
      <p>${bilingual(['Mỗi thao tác được xem xét theo 12 chiều: dữ liệu, quyền, trạng thái, lỗi, lưu trữ và truy vết. Đây là danh sách kiểm thử đề xuất, không phải bằng chứng đã chạy tự động.', 'Each operation is reviewed across 12 dimensions: data, access, state, failures, persistence and traceability. This is a proposed test checklist, not evidence of automated execution.'])}</p></div>
${operationSections}
    </section>
    <section class="section" id="evidence">
      <div class="section-head"><div><span class="eyebrow">Evidence & verification</span><h2><span data-lang="vi">Cơ sở kiểm chứng</span><span data-lang="en">Verification basis</span></h2></div></div>
      <div class="detail-grid">
        <article class="detail-panel"><h3><span data-lang="vi">Test suite có thể liên quan</span><span data-lang="en">Potentially related test suites</span></h3><ul>
${testSuiteList}
        </ul><p>${bilingual(['Danh sách này là điểm bắt đầu tra cứu; cần đọc assertion trong từng test để xác định đúng phạm vi module.', 'These files are starting points for review; inspect individual assertions to establish actual module coverage.'])}</p></article>
        <article class="detail-panel"><h3><span data-lang="vi">Trạng thái bằng chứng</span><span data-lang="en">Evidence status</span></h3><p>${bilingual(['Ma trận phía trên là tiêu chí rà soát đề xuất. Generator không chạy test và không xác nhận pass/fail. Khi nộp dự án, ghi revision, môi trường, lệnh chạy và kết quả thực tế.', 'The matrix above is a proposed review checklist. The generator does not run tests or assert pass/fail. For submission, record the revision, environment, command and actual results.'])}</p><p>${bilingual(['Demo HTML và số liệu mẫu không thay thế test chức năng, kiểm thử người dùng hoặc đánh giá pilot.', 'HTML demos and sample metrics do not replace functional tests, user testing or pilot evaluation.'])}</p></article>
      </div>
    </section>
    <section class="section" id="boundaries">
      <div class="section-head"><div><span class="eyebrow">Constraints</span><h2><span data-lang="vi">Giới hạn & diễn giải</span><span data-lang="en">Boundaries & interpretation</span></h2></div></div>
      <div class="note"><ul>
${limits}
      </ul></div>
    </section>
    <section class="section"><div class="section-head"><div><span class="eyebrow">Continue</span><h2><span data-lang="vi">Phân hệ lân cận</span><span data-lang="en">Related modules</span></h2></div></div><div class="grid">
${related}
        <a class="tile" href="index.html"><span class="tile-kicker">Module library</span><h3><span data-lang="vi">Quay lại danh mục</span><span data-lang="en">Back to module library</span></h3><p><span data-lang="vi">Mở danh sách 17 phân hệ.</span><span data-lang="en">Browse all 17 modules.</span></p></a>
    </div></section>
    <footer class="site-footer"><span>PetCare / ${esc(module.title[0])}</span><a href="index.html">Module hub / Danh mục</a></footer>
  </main>
</body>
</html>
`;
}

function renderChecksForOperation(module, operationIndex) {
  return controls.map((control, controlIndex) => {
    const id = `M${String(modules.indexOf(module) + 1).padStart(2, '0')}-${String(operationIndex + 1).padStart(2, '0')}-${String(controlIndex + 1).padStart(2, '0')}`;
    const operation = module.operations[operationIndex];
    const vi = `${operation[0]}: ${control[1]} — ${control[3]}`;
    const en = `${operation[1]}: ${control[0]} — ${control[2]}`;
    return `            <li class="check-row" data-check="${id}">
              <code>${id}</code>
              <strong>${bilingual(operation)}</strong>
              <span>${bilingual([control[1], control[0]])}</span>
              <p>${bilingual([vi, en])}</p>
              <small>${bilingual(['Tiêu chí rà soát; xác minh với giao diện/mã nguồn hiện hành.', 'Review criterion; verify against the current UI/source.'])}</small>
            </li>`;
  }).join('\n');
}

await writeFile(path.join(outputDir, hub.file), hub.html, 'utf8');
if (!process.argv.includes('--hub-only')) {
  for (const [index, module] of modules.entries()) {
    await writeFile(path.join(outputDir, module.file), renderPage(module, index), 'utf8');
  }
}
console.log(process.argv.includes('--hub-only') ? 'Generated the document hub.' : `Generated ${modules.length} bilingual module pages plus the module hub.`);