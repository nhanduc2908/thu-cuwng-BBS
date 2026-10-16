(() => {
  "use strict";

  const routes = [
    { key: "overview", label: "Control tower", group: "Điều hành", hint: "Tổng quan vận hành, ngoại lệ và quy trình đang mở." },
    { key: "branches", label: "Chi nhánh", group: "Điều hành", hint: "Owner, tình trạng cơ sở, độ phủ dữ liệu và KPI." },
    { key: "inventory", label: "Tồn kho", group: "Kho & cung ứng", hint: "SKU, location, lot, tồn khả dụng và ngưỡng bổ sung." },
    { key: "procurement", label: "Đề nghị mua hàng", group: "Kho & cung ứng", hint: "Requisition, báo giá, hạn mức và PO draft." },
    { key: "suppliers", label: "Nhà cung cấp", group: "Kho & cung ứng", hint: "Hồ sơ, hợp đồng và điều kiện giao dịch." },
    { key: "receiving", label: "Nhập hàng", group: "Kho & cung ứng", hint: "PO, phiếu nhận, lô và đối chiếu hóa đơn." },
    { key: "transfers", label: "Điều chuyển", group: "Kho & cung ứng", hint: "Dispatch, hàng đang chuyển, ETA và xác nhận nhận." },
    { key: "adjustments", label: "Điều chỉnh tồn", group: "Kho & cung ứng", hint: "Kiểm kê, recount, variance và chứng từ." },
    { key: "approvals", label: "Phê duyệt", group: "Kiểm soát", hint: "Maker-checker, quyền, hạn mức và SLA." },
    { key: "finance", label: "Tài chính", group: "Tài chính", hint: "Đóng kỳ, chứng từ, settlement và ngoại lệ." },
    { key: "reconciliation", label: "Đối soát", group: "Tài chính", hint: "Ghép source, phân loại sai lệch và xử lý case." },
    { key: "reports", label: "Báo cáo chi nhánh", group: "Điều hành", hint: "KPI, coverage, freshness và drill-down." },
    { key: "audit", label: "Nhật ký kiểm soát", group: "Kiểm soát", hint: "Actor, entity/version, decision và evidence." },
    { key: "integrations", label: "Tích hợp", group: "Nền tảng", hint: "Contract, connector, retry, lag và DLQ." },
    { key: "settings", label: "Cấu hình tổ chức", group: "Nền tảng", hint: "Policy, scope, version và dry-run." }
  ];

  const workflows = {
    overview: ["overview", "branches", "reports"],
    branches: ["branches", "inventory", "reports"],
    inventory: ["inventory", "procurement", "approvals", "receiving", "finance"],
    procurement: ["procurement", "suppliers", "approvals", "receiving", "finance"],
    suppliers: ["suppliers", "procurement", "approvals", "receiving"],
    receiving: ["receiving", "inventory", "finance", "reconciliation", "reports"],
    transfers: ["transfers", "adjustments", "approvals", "inventory", "audit"],
    adjustments: ["adjustments", "approvals", "audit", "inventory"],
    approvals: ["approvals", "finance", "audit"],
    finance: ["finance", "reconciliation", "reports", "audit"],
    reconciliation: ["reconciliation", "finance", "reports", "audit"],
    reports: ["reports", "overview"],
    audit: ["audit", "settings", "integrations"],
    integrations: ["integrations", "reconciliation", "audit"],
    settings: ["settings", "approvals", "integrations", "audit"]
  };

  const routeKeys = new Set(routes.map(({ key }) => key));
  for (const [source, steps] of Object.entries(workflows)) {
    if (!routeKeys.has(source) || steps.length < 2 || steps[0] !== source || steps.some((step) => !routeKeys.has(step))) {
      throw new Error(`Pet Business có workflow không hợp lệ tại route "${source}".`);
    }
  }

  window.PetBusinessConfig = Object.freeze({
    routes: Object.freeze(routes.map((route) => Object.freeze(route))),
    workflows: Object.freeze(Object.fromEntries(
      Object.entries(workflows).map(([key, steps]) => [key, Object.freeze(steps)])
    ))
  });
})();
