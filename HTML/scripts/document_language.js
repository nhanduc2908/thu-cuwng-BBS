(() => {
  const translations = {
    'Local-first desktop system': 'Hệ thống desktop cục bộ',
    'Browse the project': 'Duyệt tài liệu dự án',
    'Project library': 'Thư viện dự án',
    'Reports & presentations': 'Báo cáo & thuyết trình',
    'Review and present': 'Xem báo cáo và thuyết trình',
    'Decision brief': 'Tóm tắt điều hành',
    'Daily operations': 'Vận hành hằng ngày',
    'Presenter guide': 'Hướng dẫn thuyết trình',
    'A record through its lifecycle': 'Vòng đời một hồ sơ',
    'Problem / response / assumptions': 'Vấn đề / giải pháp / giả định',
    'Illustrative dashboard / sample only': 'Dashboard minh họa / chỉ là dữ liệu mẫu',
    'Template / no live data': 'Mẫu báo cáo / không có dữ liệu trực tiếp',
    'Planning / subject to validation': 'Đề xuất / cần được xác nhận',
    'Problem / solution / boundaries': 'Vấn đề / giải pháp / giới hạn',
    'Evidence-aware review': 'Đánh giá theo bằng chứng',
    'Design / functions / security': 'Thiết kế / chức năng / bảo mật',
    'Record lifecycle': 'Vòng đời hồ sơ',
    'Project library': 'Thư viện dự án',
    'Reports & analytics': 'Báo cáo & phân tích',
    'Demo & pitch': 'Demo & giới thiệu',
    'Strategic and presentation pages': 'Tài liệu chiến lược & thuyết trình',
    'Core project structure': 'Cấu trúc dự án',
    'Master hub': 'Trang điều hướng chính',
    'Module catalog': 'Danh mục phân hệ',
    'Project overview': 'Tổng quan dự án',
    'KPI board': 'Bảng chỉ số KPI',
    'Business case': 'Cơ sở kinh doanh',
    'Executive': 'Điều hành',
    'Reports & analytics': 'Báo cáo & phân tích',
    'Demo & pitch': 'Demo & giới thiệu',
    'Business review': 'Đánh giá nghiệp vụ',
    'Final report': 'Báo cáo cuối',
    'Operations snapshot': 'Ảnh chụp vận hành',
    'Pitch brief': 'Tóm tắt thuyết trình',
    'Demo slides': 'Slide demo',
    'UI preview': 'Xem trước giao diện',
    'UI wireframe': 'Khung dây giao diện',
    'Interactive app demo': 'Demo ứng dụng tương tác',
    'Workflow story': 'Câu chuyện quy trình',
    'Interface preview': 'Xem trước giao diện',
    'Sample metrics, clearly marked': 'Số liệu mẫu, đã ghi nhãn',
    'Value, risks and assumptions': 'Giá trị, rủi ro và giả định',
    'Presentation deck': 'Bộ slide thuyết trình',
    'Problem, solution, impact': 'Vấn đề, giải pháp, tác động kỳ vọng',
    'Product flow and functions': 'Luồng và chức năng sản phẩm',
    'Business lifecycle narrative': 'Hành trình nghiệp vụ',
    'Low-fidelity layout study': 'Bản nghiên cứu bố cục sơ bộ',
    'Static sample records and panels': 'Bản ghi và màn hình mẫu tĩnh',
    'Home / Trang chủ': 'Trang chủ',
    'Workflow': 'Quy trình',
    'Report': 'Báo cáo',
    'Overview': 'Tổng quan',
    'Modules': 'Phân hệ',
    'Primary navigation': 'Điều hướng chính',
    'PetCare / Project files': 'PetCare / Tài liệu dự án',
    'PetCare presentation suite': 'Bộ tài liệu PetCare',
    'Project documentation': 'Tài liệu dự án',
    'Python · PySide6 · SQLite': 'Python · PySide6 · SQLite',
    'PetCare / Project presentation': 'PetCare / Thuyết trình dự án',
    'Project briefing / 8 slides': 'Giới thiệu dự án / 8 slide',
    'Presentation': 'Thuyết trình',
    'Local SQLite': 'SQLite cục bộ',
    'Interface concept': 'Mô phỏng giao diện',
    'Demo screens': 'Màn hình demo',
    'Primary navigation': 'Điều hướng chính',
    'Application modules': 'Các phân hệ ứng dụng',
    'Search displayed records': 'Tìm bản ghi đang hiển thị',
    'Previous slide': 'Slide trước',
    'Next slide': 'Slide tiếp theo',
    'Operations / implemented flow': 'Vận hành / luồng đã triển khai',
    '01 / Shared application flow': '01 / Luồng ứng dụng dùng chung',
    '02 / Business branches': '02 / Các nhánh nghiệp vụ',
    'A / Intake': 'A / Tiếp nhận',
    'B / Daily care & health': 'B / Chăm sóc & sức khỏe hằng ngày',
    'C / Reservation & animal sale': 'C / Giữ chỗ & bán vật nuôi',
    'D / Product orders': 'D / Đơn hàng sản phẩm',
    'E / Customer-owned pet & service': 'E / Thú cưng khách hàng & dịch vụ',
    'F / Membership': 'F / Hội viên',
    '03 / State transitions': '03 / Chuyển trạng thái',
    '04 / Role boundaries': '04 / Ranh giới quyền hạn',
    '05 / Exceptions & close': '05 / Ngoại lệ & kết thúc',
    'SQLite on one Windows machine': 'SQLite trên một máy Windows',
    'Presenter story / sample journey': 'Câu chuyện thuyết trình / hành trình mẫu',
    'Walkthrough / 10 steps': 'Hướng dẫn / 10 bước',
    'Story steps': 'Các bước câu chuyện',
    'Customer-owned pet': 'Thú cưng khách hàng',
    'Service workflow': 'Quy trình dịch vụ',
    'Not live data': 'Không phải dữ liệu trực tiếp',
    'Do not merge these paths': 'Không gộp hai nhánh',
    'Store branch': 'Nhánh cửa hàng',
    'Customer service branch': 'Nhánh dịch vụ khách hàng',
    'Boundary': 'Giới hạn',
    'Decision brief / evidence-led': 'Tóm lược quyết định / dựa trên bằng chứng',
    '01 / Business need': '01 / Nhu cầu nghiệp vụ',
    '01 / Records': '01 / Hồ sơ',
    '02 / Operations': '02 / Vận hành',
    '03 / Oversight': '03 / Giám sát',
    '02 / Product response': '02 / Giải pháp PetCare',
    '03 / Editable scenario': '03 / Kịch bản có thể điều chỉnh',
    '04 / Cost, risk & readiness': '04 / Chi phí, rủi ro & mức sẵn sàng',
    '05 / Pilot plan': '05 / Kế hoạch pilot',
    '06 / Success measures': '06 / Chỉ số đánh giá',
    'VND / hour': 'VND / giờ',
    'No assumed ROI': 'Không giả định ROI',
    'Value to validate': 'Giá trị cần kiểm chứng',
    'Executive brief': 'Tóm tắt điều hành',
    'Executive summary': 'Tóm tắt điều hành',
    'Report contents': 'Mục lục báo cáo',
    '03 / System design': '03 / Kiến trúc hệ thống',
    '04 / Operational workflows': '04 / Quy trình vận hành',
    '05 / Security & governance': '05 / Bảo mật & quản trị',
    '06 / Data, reporting & operations': '06 / Dữ liệu, báo cáo & vận hành',
    '07 / Boundaries & readiness': '07 / Giới hạn & mức sẵn sàng',
    '08 / Pilot decision gate': '08 / Cổng quyết định pilot',
    '09 / Measures to validate': '09 / Chỉ số cần kiểm chứng',
    '10 / Conclusion & references': '10 / Kết luận & tài liệu tham chiếu',
    'At a glance': 'Tóm lược nhanh',
    '01 / At a glance': '01 / Tóm lược nhanh',
    '02 / Current product': '02 / Sản phẩm hiện có',
    '03 / Boundaries & readiness': '03 / Giới hạn & mức sẵn sàng',
    '04 / Pilot decision gate': '04 / Cổng quyết định pilot',
    '05 / Measures to validate': '05 / Chỉ số cần kiểm chứng',
    '01 · NEED': '01 · NHU CẦU',
    '02 · PRODUCT': '02 · SẢN PHẨM',
    '03 · EVIDENCE': '03 · BẰNG CHỨNG',
    'Gate 01': 'Cổng 01',
    'Gate 02': 'Cổng 02',
    'Gate 03': 'Cổng 03',
    'Gate 04': 'Cổng 04',
    'Decision brief / pilot proposal': 'Tóm tắt điều hành / đề xuất pilot',
    'Decision requested / Quyết định cần có': 'Quyết định cần có',
    '01 · NEED': '01 · NHU CẦU',
    '02 · PRODUCT': '02 · SẢN PHẨM',
    '03 · EVIDENCE': '03 · BẰNG CHỨNG'
  };
  const reverseTranslations = Object.fromEntries(Object.entries(translations).map(([english, vietnamese]) => [vietnamese, english]));
  const pairedLabelValues = [
    ['Scope / Phạm vi.', 'Phạm vi.', 'Scope.'],
    ['Back to project hub / Về trang dự án', 'Về trang dự án', 'Back to project hub'],
    ['Bộ slide song ngữ / bilingual deck', 'Bộ slide song ngữ', 'Bilingual presentation deck'],
    ['PetCare / Project documentation', 'PetCare / Tài liệu dự án', 'PetCare / Project documentation'],
    ['Recommendation / Khuyến nghị', 'Khuyến nghị', 'Recommendation'],
    ['Decision requested / Quyết định cần có', 'Quyết định cần có', 'Decision requested'],
    ['Step 01', 'Bước 01', 'Step 01'],
    ['Step 02', 'Bước 02', 'Step 02'],
    ['Step 03', 'Bước 03', 'Step 03'],
    ['Step 04', 'Bước 04', 'Step 04']
  ];
  const pairedLabels = new Map();
  for (const [source, vietnamese, english] of pairedLabelValues) {
    for (const label of [source, vietnamese, english]) pairedLabels.set(label, [vietnamese, english]);
  }
  const formLabelValues = [
    ['Tên hoặc chức năng / Name or function', 'Tên hoặc chức năng', 'Name or function'],
    ['Tất cả nhóm / All groups', 'Tất cả nhóm', 'All groups'],
    ['Nền tảng / Platform', 'Nền tảng', 'Platform'],
    ['Chăm sóc động vật / Animal care', 'Chăm sóc động vật', 'Animal care'],
    ['Bán hàng & kho / Sales & inventory', 'Bán hàng & kho', 'Sales & inventory'],
    ['Dịch vụ / Services', 'Dịch vụ', 'Services']
  ];
  const formLabels = new Map();
  for (const [source, vietnamese, english] of formLabelValues) {
    for (const label of [source, vietnamese, english]) formLabels.set(label, [vietnamese, english]);
  }
  const fileLabels = {
    'index.html': ['Trang chủ', 'Home'],
    'workflow.html': ['Quy trình', 'Workflow'],
    'report_final.html': ['Báo cáo', 'Report'],
    'project_overview.html': ['Tổng quan', 'Overview'],
    'report_kpi_board.html': ['Bảng KPI', 'KPI board'],
    'business_case.html': ['Cơ sở kinh doanh', 'Business case'],
    'executive_summary.html': ['Tóm tắt điều hành', 'Executive summary'],
    'roadmap.html': ['Lộ trình', 'Roadmap'],
    'slides_pitch.html': ['Thuyết trình', 'Pitch'],
    'slides_demo.html': ['Demo', 'Demo walkthrough'],
    'app_interface_preview.html': ['Giao diện', 'Interface preview'],
    'demo_ui_preview.html': ['Khung giao diện', 'UI preview']
  };

  const setLanguage = () => {
    const english = document.body.classList.contains('show-en');
    document.documentElement.lang = english ? 'en' : 'vi';
    const localizedTitle = document.documentElement.dataset[english ? 'titleEn' : 'titleVi'];
    if (localizedTitle) document.title = `PetCare | ${localizedTitle}`;
    document.title = document.title.replace(/^PetCare \| PetCare (?:\/ )?/, 'PetCare | ');

    const brand = document.querySelector('.brand');
    if (brand) {
      for (const node of brand.childNodes) {
        if (node.nodeType === Node.TEXT_NODE) node.textContent = node.textContent.replace('PetCare / PetCare /', 'PetCare /');
      }
    }

    for (const element of document.querySelectorAll('[data-lang="vi"], [data-lang="en"]')) {
      element.lang = element.dataset.lang;
      const current = element.textContent.trim();
      const spanDictionary = element.dataset.lang === 'vi' ? translations : reverseTranslations;
      const translated = spanDictionary[current];
      if (translated) element.textContent = translated;
    }

    const toggle = document.querySelector('[data-document-language-toggle], button[aria-label="Switch language"], #language-toggle');
    if (toggle) {
      toggle.dataset.documentLanguageToggle = 'true';
      toggle.setAttribute('aria-label', english ? 'Switch to Vietnamese' : 'Switch to English');
      toggle.setAttribute('aria-pressed', String(english));
      toggle.title = english ? 'Switch to Vietnamese' : 'Switch to English';
    }

    for (const link of document.querySelectorAll('.header-nav a, .nav a, .site-actions a')) {
      if (link.querySelector('[data-lang]')) continue;
      const target = link.getAttribute('href')?.split(/[?#]/, 1)[0].split('/').pop();
      const labels = fileLabels[target];
      if (labels) link.textContent = labels[english ? 1 : 0];
    }

    const dictionary = english ? reverseTranslations : translations;
    for (const input of document.querySelectorAll('[placeholder]')) {
      const pair = formLabels.get(input.placeholder);
      if (pair) input.placeholder = pair[english ? 1 : 0];
    }
    for (const option of document.querySelectorAll('option')) {
      const pair = formLabels.get(option.textContent.trim());
      if (pair) option.textContent = pair[english ? 1 : 0];
    }
    for (const element of document.querySelectorAll('[aria-label]')) {
      if (element === toggle) continue;
      const label = element.getAttribute('aria-label');
      const pair = pairedLabels.get(label);
      if (pair) element.setAttribute('aria-label', pair[english ? 1 : 0]);
      else if (dictionary[label]) element.setAttribute('aria-label', dictionary[label]);
    }
    const candidates = document.querySelectorAll('.eyebrow, .tile-kicker, .tag, .summary-number, .gate b, .link-box h3, .section-title h2, .section-head h2, .footer span, .footer, .site-footer span, .site-footer a, .tablist button, .demo-table th, .note strong');
    for (const element of candidates) {
      if (element.closest('[data-lang]') || element.querySelector('[data-lang]')) continue;
      const current = element.textContent.trim();
      const pair = pairedLabels.get(current);
      const translated = pair ? pair[english ? 1 : 0] : dictionary[current];
      if (translated) element.textContent = translated;
    }
  };

  setLanguage();
  new MutationObserver(setLanguage).observe(document.body, { attributes: true, attributeFilter: ['class'] });
})();