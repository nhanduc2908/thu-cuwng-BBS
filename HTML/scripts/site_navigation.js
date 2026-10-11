(() => {
  "use strict";

  const script = document.currentScript;
  if (!script || document.querySelector(".petcare-wayfinder")) return;

  const scriptUrl = new URL(script.src, document.baseURI);
  const siteRoot = new URL("../", scriptUrl);
  const mainPage = new URL("TRrang chính/index.html", siteRoot);
  const systemHub = new URL("index.html", siteRoot);
  const historyKey = `petcare-wayfinder:${siteRoot.href}`;
  const returningKey = `${historyKey}:returning`;
  const pageGroups = [
    {
      title: "Cổng & trang chính",
      pages: [
        ["Cổng hệ thống PetCare", "index.html"],
        ["Menu danh sách trang", "menu.html"],
        ["Trang chủ Bông Bông Pet Care", "TRrang chính/index.html"],
        ["PetCare System", "TRrang chính/petcare_system.html"],
        ["Cổng khách hàng", "TRrang chính/index_customer.html"],
        ["Khách hàng & nhân viên", "TRrang chính/user_portal.html"],
        ["Trưng bày sản phẩm", "TRrang chính/product_showcase.html"],
        ["Danh mục dinh dưỡng", "TRrang chính/nutrition_products.html"],
        ["Dinh dưỡng cho chó", "TRrang chính/nutrition_products_dog.html"],
        ["Dinh dưỡng cho mèo", "TRrang chính/nutrition_products_cat.html"],
        ["Thông số sản phẩm chó mèo · 70 trường", "Trang thông số của các sản phẩm/index.html"],
        ["Thương hiệu thức ăn chó mèo toàn cầu", "Trang thông số của các sản phẩm/thuong-hieu.html"],
        ["Quy trình chăm sóc", "TRrang chính/workflow.html"]
      ]
    },
    {
      title: "Điều hành & dữ liệu",
      pages: [
        ["Bảng điều hành PetCare", "TRrang chính/petcare_management.html"],
        ["Quản trị cửa hàng", "Trang hỗ trợ/admin_store_management.html"],
        ["Trung tâm dữ liệu JSON", "Trang hỗ trợ/data_explorer.html"],
        ["Hỗ trợ tra cứu bệnh lý", "Trang hỗ trợ/disease_support.html"],
        ["Báo cáo sức khỏe thú cưng", "Trang hỗ trợ/pet_health_report.html"],
        ["Tổng quan vận hành", "Trang hỗ trợ/operations_snapshot.html"],
        ["Thư viện 17 phân hệ", "Trang hỗ trợ/Module/index.html"],
        ["Xem trước giao diện ứng dụng", "Trang hỗ trợ/app_interface_preview.html"],
        ["Demo PetCare đầy đủ", "Trang hỗ trợ/petcare_demo_full.html"],
        ["Câu chuyện quy trình", "Trang hỗ trợ/workflow_story.html"]
      ]
    },
    {
      title: "17 phân hệ nghiệp vụ",
      pages: [
        ["01 · Nền tảng & dữ liệu", "Trang hỗ trợ/Module/module_01_platform.html"],
        ["02 · Tài khoản & vai trò", "Trang hỗ trợ/Module/module_02_accounts.html"],
        ["03 · Bảng điều khiển", "Trang hỗ trợ/Module/module_03_dashboard.html"],
        ["04 · Hồ sơ thú cưng", "Trang hỗ trợ/Module/module_04_pets.html"],
        ["05 · Chuồng trại", "Trang hỗ trợ/Module/module_05_housing.html"],
        ["06 · Nhà cung cấp", "Trang hỗ trợ/Module/module_06_suppliers.html"],
        ["07 · Nhập hàng", "Trang hỗ trợ/Module/module_07_imports.html"],
        ["08 · Sức khỏe", "Trang hỗ trợ/Module/module_08_health.html"],
        ["09 · Chăm sóc", "Trang hỗ trợ/Module/module_09_care.html"],
        ["10 · Khách hàng", "Trang hỗ trợ/Module/module_10_customers.html"],
        ["11 · Đặt trước", "Trang hỗ trợ/Module/module_11_reservations.html"],
        ["12 · Đơn hàng", "Trang hỗ trợ/Module/module_12_orders.html"],
        ["13 · Hội viên", "Trang hỗ trợ/Module/module_13_memberships.html"],
        ["14 · Dịch vụ & lịch hẹn", "Trang hỗ trợ/Module/module_14_services.html"],
        ["15 · Kho & sản phẩm", "Trang hỗ trợ/Module/module_15_inventory.html"],
        ["16 · Báo cáo", "Trang hỗ trợ/Module/module_16_reports.html"],
        ["17 · Cảnh báo", "Trang hỗ trợ/Module/module_17_alerts.html"]
      ]
    },
    {
      title: "Hồ sơ dự án & báo cáo",
      pages: [
        ["Hồ sơ tổng hợp dự án", "Trang hỗ trợ/project_master_summary.html"],
        ["Tổng quan dự án", "Trang hỗ trợ/project_overview.html"],
        ["Báo giá dự án", "Trang hỗ trợ/project_quote.html"],
        ["Hóa đơn & lịch thanh toán", "Trang hỗ trợ/project_invoice.html"],
        ["Business case", "Trang hỗ trợ/business_case.html"],
        ["Tóm tắt điều hành", "Trang hỗ trợ/executive_summary.html"],
        ["Bảo mật & dữ liệu", "Trang hỗ trợ/project_security.html"],
        ["Quy trình dự án chi tiết", "Trang hỗ trợ/project_workflow_full.html"],
        ["Proposal trình bày đầy đủ", "Trang hỗ trợ/project_slides_final.html"],
        ["Slide dự án", "Trang hỗ trợ/project_slides.html"],
        ["Pitch deck", "Trang hỗ trợ/slides_pitch.html"],
        ["Slide trình diễn", "Trang hỗ trợ/slides_demo.html"],
        ["Trang trình bày tổng quan", "Trang hỗ trợ/index_presentation.html"],
        ["Bảng chỉ số KPI", "Trang hỗ trợ/report_kpi_board.html"],
        ["Đánh giá kinh doanh", "Trang hỗ trợ/report_business_review.html"],
        ["Báo cáo tổng kết", "Trang hỗ trợ/report_final.html"],
        ["Tài liệu dự án đầy đủ", "Trang hỗ trợ/projext _Full.html"]
      ]
    }
  ];

  const readLocalHistory = () => {
    try {
      const history = JSON.parse(sessionStorage.getItem(historyKey) || "[]");
      return Array.isArray(history)
        ? history.filter((url) => typeof url === "string" && url.startsWith(siteRoot.href))
        : [];
    } catch {
      return [];
    }
  };

  const saveLocalHistory = (history) => {
    try {
      sessionStorage.setItem(historyKey, JSON.stringify(history.slice(-50)));
    } catch {
      return;
    }
  };

  let localHistory = readLocalHistory();
  try {
    const returningTo = sessionStorage.getItem(returningKey);
    if (returningTo === location.href) {
      sessionStorage.removeItem(returningKey);
    } else {
      sessionStorage.removeItem(returningKey);
      if (localHistory.at(-1) !== location.href) {
        localHistory.push(location.href);
        saveLocalHistory(localHistory);
      }
    }
  } catch {
    localHistory = [];
  }

  const stylesheet = document.createElement("link");
  stylesheet.rel = "stylesheet";
  stylesheet.href = new URL("../styles/site_navigation.css", scriptUrl).href;
  document.head.append(stylesheet);

  const header = document.createElement("header");
  header.className = "petcare-global-header";
  header.setAttribute("aria-label", "PetCare global navigation");

  const brand = document.createElement("a");
  brand.className = "petcare-global-brand";
  brand.href = mainPage.href;
  brand.innerHTML = "<span class=\"petcare-global-mark\" aria-hidden=\"true\">P</span><span>PetCare<small>Bông Bông · Hệ thống quản lý</small></span>";

  const quickLinks = document.createElement("nav");
  quickLinks.className = "petcare-global-links";
  quickLinks.setAttribute("aria-label", "Liên kết nhanh");
  for (const [label, url] of [["Trang chính", mainPage], ["Cổng hệ thống", systemHub]]) {
    const link = document.createElement("a");
    link.href = url.href;
    link.textContent = label;
    quickLinks.append(link);
  }

  const directory = document.createElement("details");
  directory.className = "petcare-directory";
  const toggle = document.createElement("summary");
  toggle.className = "petcare-directory-toggle";
  const pageCount = pageGroups.reduce((total, group) => total + group.pages.length, 0);
  toggle.innerHTML = `<span aria-hidden="true">☷</span> Danh mục trang <span class="petcare-directory-count">${pageCount}</span>`;
  directory.append(toggle);

  const panel = document.createElement("div");
  panel.className = "petcare-directory-panel";
  const panelHeader = document.createElement("div");
  panelHeader.className = "petcare-directory-heading";
  const heading = document.createElement("strong");
  heading.textContent = "Điều hướng PetCare";
  const fullMenu = document.createElement("a");
  fullMenu.href = new URL("menu.html", siteRoot).href;
  fullMenu.textContent = "Mở menu đầy đủ ↗";
  panelHeader.append(heading, fullMenu);

  const search = document.createElement("input");
  search.className = "petcare-directory-search";
  search.type = "search";
  search.placeholder = "Tìm trang theo tên hoặc URL…";
  search.setAttribute("aria-label", "Tìm trong danh mục PetCare");

  const groupsContainer = document.createElement("div");
  groupsContainer.className = "petcare-directory-groups";
  const entries = [];
  const groups = [];
  for (const [index, groupData] of pageGroups.entries()) {
    const group = document.createElement("details");
    group.className = "petcare-directory-group";
    if (index === 0) group.open = true;
    const summary = document.createElement("summary");
    summary.textContent = groupData.title;
    const list = document.createElement("div");
    list.className = "petcare-directory-list";
    for (const [label, path] of groupData.pages) {
      const link = document.createElement("a");
      link.href = new URL(path, siteRoot).href;
      link.className = "petcare-directory-link";
      const name = document.createElement("span");
      name.textContent = label;
      const url = document.createElement("code");
      url.textContent = path;
      link.append(name, url);
      list.append(link);
      entries.push({ link, group, searchText: `${label} ${path}`.toLocaleLowerCase("vi") });
    }
    group.append(summary, list);
    groupsContainer.append(group);
    groups.push(group);
  }

  const noResults = document.createElement("p");
  noResults.className = "petcare-directory-empty";
  noResults.textContent = "Không tìm thấy trang phù hợp.";
  noResults.hidden = true;
  search.addEventListener("input", () => {
    const query = search.value.trim().toLocaleLowerCase("vi");
    let visible = 0;
    for (const entry of entries) {
      const matches = !query || entry.searchText.includes(query);
      entry.link.hidden = !matches;
      if (matches) visible += 1;
    }
    for (const group of groups) {
      const hasResults = Boolean(group.querySelector(".petcare-directory-link:not([hidden])"));
      group.hidden = !hasResults;
      if (query && hasResults) group.open = true;
    }
    noResults.hidden = visible > 0;
  });
  panel.append(panelHeader, search, groupsContainer, noResults);
  directory.append(panel);

  const headerInner = document.createElement("div");
  headerInner.className = "petcare-global-inner";
  headerInner.append(brand, quickLinks, directory);
  header.append(headerInner);
  document.body.prepend(header);

  const pageLocation = new URL(location.href);
  const pageGroup = pageGroups.find((group) =>
    group.pages.some(([, path]) => new URL(path, siteRoot).pathname === pageLocation.pathname)
  );
  const pageEntry = pageGroup?.pages.find(([, path]) =>
    new URL(path, siteRoot).pathname === pageLocation.pathname
  );
  if (pageGroup && pageEntry) {
    const guideContent = {
      "Cổng & trang chính": {
        intro: "Khu vực này trình bày trải nghiệm thương hiệu, thông tin dịch vụ và các điểm chạm dành cho khách hàng.",
        steps: [
          "Bắt đầu từ nội dung giới thiệu và xác định nhu cầu của người xem.",
          "Đi theo các liên kết sản phẩm, dinh dưỡng hoặc quy trình có liên quan.",
          "Dùng cổng khách hàng hoặc trang hệ thống để tiếp tục tới đúng hành trình."
        ],
        checks: [
          "Thông tin sản phẩm và khuyến nghị cần được đối chiếu với danh mục thực tế trước khi áp dụng.",
          "Nội dung giới thiệu không thay thế tư vấn thú y hoặc cam kết giao dịch.",
          "Các trang tĩnh không tự tạo hồ sơ khách hàng hay đơn hàng trong cơ sở dữ liệu."
        ]
      },
      "Điều hành & dữ liệu": {
        intro: "Khu vực này dành cho tra cứu dữ liệu, giám sát vận hành và các công cụ quản trị nội bộ.",
        steps: [
          "Xác định phạm vi dữ liệu và khoảng thời gian trước khi đọc chỉ số.",
          "Mở bảng hoặc bộ lọc liên quan để đối chiếu bản ghi nguồn.",
          "Lưu lại kết quả hoặc chuyển tới phân hệ nghiệp vụ để xử lý tiếp."
        ],
        checks: [
          "Phân biệt dữ liệu demo trong JSON với hồ sơ vận hành trong SQLite.",
          "Một số trang báo cáo chỉ đọc; quyền thao tác phụ thuộc tài khoản và phân hệ.",
          "Kiểm tra thời điểm cập nhật, bộ lọc và đơn vị tính trước khi dùng số liệu."
        ]
      },
      "17 phân hệ nghiệp vụ": {
        intro: "Phân hệ mô tả một miền nghiệp vụ riêng trong PetCare và các thông tin cần phối hợp để hoàn tất công việc.",
        steps: [
          "Xác nhận đối tượng và mã hồ sơ trước khi bắt đầu thao tác.",
          "Đọc trạng thái hiện tại, lịch sử liên quan và các điều kiện nghiệp vụ.",
          "Hoàn tất thay đổi trong ứng dụng có quyền; kiểm tra kết quả sau khi lưu."
        ],
        checks: [
          "Workspace web hiện chỉ cho xem SQLite nghiệp vụ; không sửa trực tiếp hồ sơ vận hành.",
          "CRUD trên JSON và SQLite workspace là dữ liệu chuẩn bị riêng, không phải hồ sơ thật.",
          "Các thao tác thay đổi cần tài khoản có quyền phù hợp và được ghi nhận theo cơ chế ứng dụng."
        ]
      },
      "Hồ sơ dự án & báo cáo": {
        intro: "Khu vực này tập hợp tài liệu thuyết minh, quy trình, dự toán và báo cáo để rà soát hoặc trình bày dự án.",
        steps: [
          "Đọc phần mục tiêu và phạm vi để hiểu bối cảnh của tài liệu.",
          "Đối chiếu giả định, hạng mục, con số và mốc thời gian với nguồn được duyệt.",
          "Dùng các liên kết liên quan để xem quy trình, bảo mật, chi phí và kết quả."
        ],
        checks: [
          "Tài liệu tham khảo không tự xác nhận tính pháp lý, giá bán hoặc kết quả triển khai.",
          "Thông tin tài chính và doanh nghiệp cần được chủ dự án xác nhận trước khi gửi ra ngoài.",
          "Báo cáo phản ánh dữ liệu tại thời điểm lập và không thay thế kiểm tra nghiệp vụ."
        ]
      }
    }[pageGroup.title];

    if (guideContent) {
      const guide = document.createElement("details");
      guide.className = "petcare-page-guide";
      const guideSummary = document.createElement("summary");
      guideSummary.innerHTML = "<span>▤ Hướng dẫn chi tiết trang</span><span class=\"petcare-page-guide-hint\">Phạm vi · quy trình · điểm kiểm tra</span>";
      const guideBody = document.createElement("div");
      guideBody.className = "petcare-page-guide-body";
      const intro = document.createElement("p");
      intro.className = "petcare-page-guide-intro";
      intro.textContent = `${pageEntry[0]} — ${guideContent.intro}`;

      const guideColumns = document.createElement("div");
      guideColumns.className = "petcare-page-guide-columns";
      for (const [title, items] of [
        ["Cách khai thác", guideContent.steps],
        ["Điểm cần kiểm tra", guideContent.checks]
      ]) {
        const section = document.createElement("section");
        const heading = document.createElement("h2");
        heading.textContent = title;
        const list = document.createElement("ol");
        for (const item of items) {
          const entry = document.createElement("li");
          entry.textContent = item;
          list.append(entry);
        }
        section.append(heading, list);
        guideColumns.append(section);
      }

      const related = document.createElement("nav");
      related.className = "petcare-page-guide-related";
      related.setAttribute("aria-label", "Trang liên quan");
      const relatedTitle = document.createElement("strong");
      relatedTitle.textContent = "Trang liên quan";
      related.append(relatedTitle);
      const pageIndex = pageGroup.pages.indexOf(pageEntry);
      const relatedPages = pageGroup.pages.slice(
        Math.max(0, pageIndex - 2),
        Math.min(pageGroup.pages.length, pageIndex + 3)
      );
      for (const [label, path] of relatedPages) {
        if (path === pageEntry[1] || path === "menu.html") continue;
        const link = document.createElement("a");
        link.href = new URL(path, siteRoot).href;
        link.textContent = label;
        related.append(link);
        if (related.childElementCount >= 5) break;
      }
      guideBody.append(intro, guideColumns, related);
      guide.append(guideSummary, guideBody);
      header.after(guide);
    }
  }

  directory.addEventListener("click", (event) => event.stopPropagation());
  document.addEventListener("click", (event) => {
    if (!directory.contains(event.target)) directory.open = false;
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") directory.open = false;
  });

  const currentPath = decodeURIComponent(location.pathname);
  const moduleMatch = currentPath.match(/(?:^|\/)module_(\d{2}_[a-z]+)\.html$/i);
  const moduleId = moduleMatch
    ? `module_${moduleMatch[1].toLowerCase()}`
    : /(?:^|\/)petcare_management\.html$/i.test(currentPath)
      ? "module_04_pets"
      : null;
  if (moduleId) {
    const permissionByModule = {
      module_02_accounts: "users.manage",
      module_04_pets: "animals.manage",
      module_05_housing: "store.manage",
      module_06_suppliers: "imports.manage",
      module_07_imports: "imports.manage",
      module_08_health: "health.manage",
      module_09_care: "care.manage",
      module_10_customers: "sales.manage",
      module_11_reservations: "sales.manage",
      module_12_orders: "sales.manage",
      module_13_memberships: "membership.manage",
      module_14_services: "services.manage",
      module_15_inventory: "inventory.manage"
    };
    const bridgePage = () => {
      const match = decodeURIComponent(location.pathname).match(/\/HTML\/(.+)$/i);
      if (!match) return "http://127.0.0.1:8767/";
      const encodedPath = match[1].split("/").map(encodeURIComponent).join("/");
      return `http://127.0.0.1:8767/${encodedPath}`;
    };
    const workspace = document.createElement("details");
    workspace.className = "petcare-data-workspace";
    const workspaceSummary = document.createElement("summary");
    workspaceSummary.className = "petcare-data-workspace-summary";
    workspaceSummary.innerHTML = `<span>▤ Dữ liệu phân hệ <small>${moduleId}</small></span><span class="petcare-data-workspace-hint">Mở bảng dữ liệu & thao tác ↴</span>`;
    const workspaceBody = document.createElement("div");
    workspaceBody.className = "petcare-data-workspace-body";
    const status = document.createElement("p");
    status.className = "petcare-data-status";
    status.setAttribute("role", "status");
    const actions = document.createElement("div");
    actions.className = "petcare-data-actions";
    const source = document.createElement("select");
    source.className = "petcare-data-source";
    source.setAttribute("aria-label", "Nguồn dữ liệu");
    source.innerHTML = "<option value=\"live\">SQLite nghiệp vụ · chỉ xem</option><option value=\"file\">JSON đã chuẩn bị · CRUD có backup</option><option value=\"sqlite\">SQLite workspace · JSON đã nhập</option>";
    source.autocomplete = "off";
    source.value = "live";
    const searchInput = document.createElement("input");
    searchInput.className = "petcare-data-search";
    searchInput.type = "search";
    searchInput.placeholder = "Tìm trong bản ghi…";
    searchInput.setAttribute("aria-label", "Tìm bản ghi");
    const loadButton = document.createElement("button");
    loadButton.type = "button";
    loadButton.className = "petcare-data-button";
    loadButton.textContent = "Tải dữ liệu";
    const importButton = document.createElement("button");
    importButton.type = "button";
    importButton.className = "petcare-data-button";
    importButton.textContent = "Nhập JSON → SQLite";
    importButton.hidden = true;
    const addButton = document.createElement("button");
    addButton.type = "button";
    addButton.className = "petcare-data-button petcare-data-primary";
    addButton.textContent = "＋ Thêm bản ghi";
    addButton.hidden = true;
    const accountForm = document.createElement("form");
    accountForm.className = "petcare-data-login";
    accountForm.innerHTML = "<label>Tài khoản <input name=\"username\" autocomplete=\"username\" required></label><label>Mật khẩu <input name=\"password\" type=\"password\" autocomplete=\"current-password\" required></label><button class=\"petcare-data-button petcare-data-primary\" type=\"submit\">Đăng nhập để mở dữ liệu</button>";
    const bridgeLink = document.createElement("a");
    bridgeLink.className = "petcare-data-button";
    bridgeLink.href = bridgePage();
    bridgeLink.textContent = "Mở trang qua ứng dụng PetCare để đăng nhập";
    bridgeLink.hidden = location.protocol !== "file:";
    if (location.protocol === "file:") {
      bridgeLink.addEventListener("click", (event) => {
        event.preventDefault();
        location.assign(bridgePage());
      });
    }
    const tableWrap = document.createElement("div");
    tableWrap.className = "petcare-data-table-wrap";
    const table = document.createElement("table");
    table.className = "petcare-data-table";
    const tableHead = document.createElement("thead");
    const tableBody = document.createElement("tbody");
    table.append(tableHead, tableBody);
    tableWrap.append(table);
    const pagination = document.createElement("div");
    pagination.className = "petcare-data-pagination";
    const pageLabel = document.createElement("span");
    const previousPage = document.createElement("button");
    previousPage.type = "button";
    previousPage.className = "petcare-data-button";
    previousPage.textContent = "← Trước";
    const nextPage = document.createElement("button");
    nextPage.type = "button";
    nextPage.className = "petcare-data-button";
    nextPage.textContent = "Tiếp →";
    pagination.append(pageLabel, previousPage, nextPage);
    const editor = document.createElement("dialog");
    editor.className = "petcare-data-editor";
    editor.innerHTML = "<form method=\"dialog\"><h3>Chỉnh sửa bản ghi JSON</h3><label>Nội dung bản ghi<textarea spellcheck=\"false\" required></textarea></label><p class=\"petcare-data-editor-error\" role=\"alert\"></p><div><button class=\"petcare-data-button\" value=\"cancel\">Hủy</button><button class=\"petcare-data-button petcare-data-primary\" type=\"submit\" value=\"save\">Lưu</button></div></form>";
    const editorForm = editor.querySelector("form");
    const editorTextarea = editor.querySelector("textarea");
    const editorError = editor.querySelector(".petcare-data-editor-error");
    const editorSave = editor.querySelector("button[value=\"save\"]");
    workspaceBody.append(status, actions, accountForm, bridgeLink, tableWrap, pagination, editor);
    actions.append(source, searchInput, loadButton, importButton, addButton);
    workspace.append(workspaceSummary, workspaceBody);
    header.after(workspace);

    const pageSize = 20;
    let page = 0;
    let records = [];
    let loggedIn = false;
    let canManage = false;
    let editingRecordId = null;
    const apiRoot = `${location.origin}/api`;
    const apiFetch = (path, options = {}) => fetch(`${apiRoot}${path}`, {
      credentials: "include",
      cache: "no-store",
      ...options,
      headers: {
        ...(options.headers || {}),
        ...(options.method && options.method !== "GET" ? { "X-PetCare-Request": "1" } : {})
      }
    });
    const showStatus = (message, isError = false) => {
      status.textContent = message;
      status.classList.toggle("is-error", isError);
    };
    const notifyError = (error) => showStatus(error.message || "Không thể hoàn tất thao tác.", true);
    const parseResponse = async (response) => {
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.error || `Yêu cầu thất bại (${response.status}).`);
      return payload;
    };
    const visibleRecord = (record) => Object.fromEntries(
      Object.entries(record || {}).filter(([key]) => !key.startsWith("_"))
    );
    const filteredRecords = () => {
      const query = searchInput.value.trim().toLocaleLowerCase("vi");
      return records.filter((item) => !item.archived &&
        JSON.stringify(visibleRecord(item.record)).toLocaleLowerCase("vi").includes(query));
    };
    function renderDataset() {
      const visible = filteredRecords();
      const fields = [...new Set(visible.flatMap((item) => Object.keys(visibleRecord(item.record))))].slice(0, 6);
      const headerRow = document.createElement("tr");
      for (const field of fields) {
        const cell = document.createElement("th");
        cell.textContent = field;
        headerRow.append(cell);
      }
      const actionsHeader = document.createElement("th");
      actionsHeader.textContent = "Thao tác";
      headerRow.append(actionsHeader);
      tableHead.replaceChildren(headerRow);
      tableBody.replaceChildren();
      const pageCount = Math.ceil(visible.length / pageSize);
      const start = page * pageSize;
      for (const item of visible.slice(start, start + pageSize)) {
        const row = document.createElement("tr");
        for (const field of fields) {
          const cell = document.createElement("td");
          const value = visibleRecord(item.record)[field];
          cell.textContent = value === null || value === undefined
            ? "—"
            : typeof value === "object" ? JSON.stringify(value) : String(value);
          row.append(cell);
        }
        const controls = document.createElement("td");
        controls.className = "petcare-data-row-actions";
        if (canManage) {
          const edit = document.createElement("button");
          edit.type = "button";
          edit.textContent = "Sửa";
          edit.addEventListener("click", () => editRecord(item));
          const archive = document.createElement("button");
          archive.type = "button";
          archive.textContent = "Lưu trữ";
          archive.addEventListener("click", () => archiveRecord(item));
          controls.append(edit, archive);
        } else {
          controls.textContent = "Chỉ xem";
        }
        row.append(controls);
        tableBody.append(row);
      }
      if (!visible.length) {
        const emptyRow = document.createElement("tr");
        const cell = document.createElement("td");
        cell.colSpan = Math.max(fields.length + 1, 1);
        cell.textContent = records.length ? "Không có bản ghi khớp bộ lọc." : "Nguồn hiện chưa có bản ghi.";
        emptyRow.append(cell);
        tableBody.append(emptyRow);
      }
      pageLabel.textContent = `${visible.length.toLocaleString("vi-VN")} bản ghi · trang ${visible.length ? page + 1 : 0}/${pageCount}`;
      previousPage.disabled = page <= 0;
      nextPage.disabled = pageCount === 0 || page >= pageCount - 1;
    }
    async function loadDataset() {
      if (location.protocol === "file:") {
        showStatus("Trang đang mở bằng file:// nên không có kết nối CRUD an toàn. Hãy mở trang qua ứng dụng PetCare.", true);
        return;
      }
      showStatus("Đang tải nguồn dữ liệu…");
      try {
        const payload = await parseResponse(await apiFetch(
          `/datasets/${moduleId}/records?source=${encodeURIComponent(source.value)}`
        ));
        records = payload.records || [];
        canManage = Boolean(payload.canManage);
        const permission = permissionByModule[moduleId];
        addButton.hidden = !canManage;
        importButton.hidden = !canManage || source.value !== "sqlite";
        searchInput.disabled = false;
        page = 0;
        renderDataset();
        showStatus(
          `${payload.total.toLocaleString("vi-VN")} bản ghi · ${
            source.value === "file" ? "JSON đã chuẩn bị" :
            source.value === "sqlite" ? "SQLite workspace nhập từ JSON" :
            "SQLite nghiệp vụ của ứng dụng"
          } · ` +
          (canManage ? "Có quyền thêm, sửa, lưu trữ." : `Chỉ xem${permission && source.value !== "live" ? ` · thiếu quyền ${permission}` : " · nguồn chỉ đọc"}.`)
        );
        accountForm.hidden = true;
      } catch (error) {
        if (error.message.includes("Sign-in required")) {
          loggedIn = false;
          accountForm.hidden = false;
          showStatus("Đăng nhập bằng tài khoản ứng dụng để đọc và quản lý dữ liệu.");
        } else {
          notifyError(error);
        }
      }
    }
    async function checkSession() {
      if (location.protocol === "file:") {
        accountForm.hidden = true;
        loadButton.disabled = true;
        source.disabled = true;
        showStatus("Mở trang từ ứng dụng PetCare để dùng SQLite và thao tác có xác thực.");
        return;
      }
      try {
        const response = await apiFetch("/session");
        if (response.ok) {
          const session = await response.json();
          loggedIn = Boolean(session.authenticated);
          accountForm.hidden = loggedIn;
          if (session.must_change_password) {
            showStatus("Tài khoản yêu cầu đổi mật khẩu trong ứng dụng trước khi dùng workspace.", true);
            return;
          }
          await loadDataset();
        } else {
          accountForm.hidden = false;
          showStatus("Đăng nhập để mở dữ liệu nghiệp vụ đã phân quyền.");
        }
      } catch (error) {
        accountForm.hidden = false;
        showStatus(`Không kết nối được API của ứng dụng: ${error.message}`, true);
      }
    }
    function openEditor(recordId, record) {
      editingRecordId = recordId;
      const editableRecord = visibleRecord(record);
      editor.querySelector("h3").textContent = recordId === null ? "Thêm bản ghi" : "Sửa bản ghi";
      editorTextarea.value = JSON.stringify(editableRecord, null, 2);
      editorError.textContent = "";
      editor.showModal();
    }
    function editRecord(item) {
      openEditor(item.id, item.record);
    }
    async function archiveRecord(item) {
      if (!window.confirm("Lưu trữ bản ghi này? Dữ liệu không bị xóa vĩnh viễn.")) return;
      try {
        await parseResponse(await apiFetch(
          `/datasets/${moduleId}/records/${item.id}?source=${encodeURIComponent(source.value)}`,
          { method: "DELETE" }
        ));
        showStatus("Đã lưu trữ bản ghi; không xóa vĩnh viễn.");
        await loadDataset();
      } catch (error) {
        notifyError(error);
      }
    }
    source.addEventListener("change", () => {
      importButton.hidden = source.value !== "sqlite" || !canManage;
      loadDataset();
    });
    loadButton.addEventListener("click", loadDataset);
    searchInput.addEventListener("input", () => { page = 0; renderDataset(); });
    previousPage.addEventListener("click", () => { if (page > 0) { page -= 1; renderDataset(); } });
    nextPage.addEventListener("click", () => {
      if ((page + 1) * pageSize < filteredRecords().length) { page += 1; renderDataset(); }
    });
    addButton.addEventListener("click", () => {
      const template = records.find((item) => !item.archived)?.record || {};
      openEditor(null, template);
    });
    importButton.addEventListener("click", async () => {
      if (!window.confirm("Nhập các bản ghi JSON chưa lưu trữ vào SQLite workspace? Bản ghi trùng nguồn sẽ được bỏ qua.")) return;
      try {
        const payload = await parseResponse(await apiFetch(
          `/datasets/${moduleId}/import?source=sqlite`,
          { method: "POST", headers: { "Content-Type": "application/json" }, body: "{}" }
        ));
        showStatus(`Đã nhập ${payload.inserted} bản ghi; bỏ qua ${payload.skipped} bản ghi đã nhập trước đó.`);
        await loadDataset();
      } catch (error) {
        notifyError(error);
      }
    });
    accountForm.addEventListener("submit", async (event) => {
      event.preventDefault();
      const form = new FormData(accountForm);
      const submit = accountForm.querySelector("button[type=submit]");
      submit.disabled = true;
      try {
        await parseResponse(await apiFetch("/login", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            username: form.get("username"),
            password: form.get("password")
          })
        }));
        loggedIn = true;
        accountForm.reset();
        await loadDataset();
      } catch (error) {
        notifyError(error);
      } finally {
        submit.disabled = false;
      }
    });
    editorForm.addEventListener("submit", async (event) => {
      if (event.submitter?.value !== "save") return;
      event.preventDefault();
      let record;
      try {
        record = JSON.parse(editorTextarea.value);
        if (!record || Array.isArray(record) || typeof record !== "object") {
          throw new Error("Bản ghi phải là một đối tượng JSON.");
        }
      } catch (error) {
        editorError.textContent = error.message;
        return;
      }
      editorSave.disabled = true;
      try {
        const method = editingRecordId === null ? "POST" : "PUT";
        const route = editingRecordId === null
          ? `/datasets/${moduleId}/records?source=${encodeURIComponent(source.value)}`
          : `/datasets/${moduleId}/records/${editingRecordId}?source=${encodeURIComponent(source.value)}`;
        await parseResponse(await apiFetch(route, {
          method,
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ record })
        }));
        editor.close();
        showStatus(editingRecordId === null ? "Đã thêm bản ghi." : "Đã lưu thay đổi.");
        await loadDataset();
      } catch (error) {
        editorError.textContent = error.message;
      } finally {
        editorSave.disabled = false;
      }
    });
    workspace.addEventListener("toggle", () => {
      if (workspace.open && !loggedIn && location.protocol !== "file:") checkSession();
    });
    checkSession();
  }

  const navigation = document.createElement("nav");
  navigation.className = "petcare-wayfinder";
  navigation.setAttribute("aria-label", "Điều hướng nhanh PetCare");

  const backLink = document.createElement("a");
  backLink.href = mainPage.href;
  backLink.setAttribute("aria-label", "Quay lại trang trước hoặc về trang chính");
  backLink.innerHTML = "<span aria-hidden=\"true\">←</span><span>Quay lại</span>";
  backLink.addEventListener("click", (event) => {
    const history = readLocalHistory();
    if (history.at(-1) === location.href) history.pop();
    const trackedPreviousPage = history.pop();
    if (trackedPreviousPage) {
      event.preventDefault();
      saveLocalHistory(history);
      try {
        sessionStorage.setItem(returningKey, trackedPreviousPage);
      } catch {
        location.assign(mainPage.href);
        return;
      }
      location.assign(trackedPreviousPage);
      return;
    }

    const referrer = document.referrer;
    if (!referrer) return;

    let previousPage;
    try {
      previousPage = new URL(referrer);
    } catch {
      return;
    }

    if (previousPage.href.startsWith(siteRoot.href) && history.length > 1) {
      event.preventDefault();
      history.back();
    }
  });

  const homeLink = document.createElement("a");
  homeLink.className = "petcare-wayfinder-home";
  homeLink.href = mainPage.href;
  homeLink.setAttribute("aria-label", "Về website chính PetCare");
  homeLink.innerHTML = "<span aria-hidden=\"true\">⌂</span><span>Trang chính</span>";

  const hubLink = document.createElement("a");
  hubLink.href = systemHub.href;
  hubLink.setAttribute("aria-label", "Về cổng hệ thống PetCare");
  hubLink.innerHTML = "<span aria-hidden=\"true\">◈</span><span>Cổng hệ thống</span>";

  navigation.append(backLink, homeLink, hubLink);
  document.body.append(navigation);
})();
