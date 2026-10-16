(() => {
  "use strict";

  const field = (name, label, value, min, max, step = 1) => ({
    name, label, type: "number", value, min, max, step
  });
  const choice = (name, label, value, options) => ({
    name, label, type: "select", value, options
  });
  const options = (...values) => values.map((value) => [value, value]);
  const result = (status, tone, summary, calculation) => ({ status, tone, summary, calculation });
  const round = (value, digits = 2) => Number(value.toFixed(digits));
  const money = (value) => new Intl.NumberFormat("vi-VN", {
    style: "currency", currency: "VND", maximumFractionDigits: 0
  }).format(value);

  const define = (name, fields, calculate) => Object.freeze({
    name,
    fields: Object.freeze(fields.map((item) => Object.freeze(item))),
    calculate(values) {
      for (const item of fields) {
        const value = values[item.name];
        if (item.type === "select") {
          if (!item.options.some(([option]) => option === value)) {
            throw new Error(`Giá trị không hợp lệ cho trường "${item.label}".`);
          }
          continue;
        }
        if (!Number.isFinite(value) || value < item.min || value > item.max) {
          throw new Error(`"${item.label}" phải nằm trong khoảng ${item.min}–${item.max}.`);
        }
        if (item.step === 1 && !Number.isInteger(value)) {
          throw new Error(`"${item.label}" phải là số nguyên.`);
        }
      }
      const output = calculate(values);
      if (!output || !["green", "gold", "red", "blue", ""].includes(output.tone) ||
          typeof output.status !== "string" || typeof output.summary !== "string" ||
          typeof output.calculation !== "string") {
        throw new Error(`Thuật toán "${name}" trả về kết quả không hợp lệ.`);
      }
      return output;
    }
  });

  const algorithms = {
    overview: define("Xếp hạng ngoại lệ điều hành", [
      field("severity", "Mức nghiêm trọng (1–5)", 3, 1, 5),
      field("impact", "Phạm vi ảnh hưởng (1–5)", 3, 1, 5),
      field("ageHours", "Thời gian đang mở (giờ)", 8, 0, 8760),
      field("periodCloseHours", "Thời gian đến khi khóa kỳ (giờ)", 48, 0, 8760),
      choice("periodLocked", "Kỳ kế toán", "open", options("open", "locked"))
    ], (v) => {
      const urgency = Math.min(v.ageHours, 24) * 1.5;
      const closeRisk = v.periodLocked === "locked" ? 30 : Math.max(0, 20 - v.periodCloseHours / 6);
      const score = Math.min(100, Math.round(v.severity * 12 + v.impact * 8 + urgency + closeRisk));
      const blocked = v.periodLocked === "locked";
      return result(blocked ? "Chặn ghi sổ · kỳ đã khóa" : score >= 75 ? "Ưu tiên xử lý cao" : score >= 45 ? "Theo dõi sát" : "Xử lý thường lệ",
        blocked || score >= 75 ? "red" : score >= 45 ? "gold" : "green",
        `Điểm ngoại lệ ${score}/100${blocked ? "; mọi điều chỉnh phải chuyển kỳ sau." : "; xếp hàng theo điểm rồi đến hạn gần nhất."}`,
        `min(100, ${v.severity}×12 + ${v.impact}×8 + min(${v.ageHours},24)×1.5 + ${round(closeRisk)}) = ${score}; period=${v.periodLocked}`);
    }),

    branches: define("So sánh KPI chi nhánh có cổng dữ liệu", [
      field("actual", "Kết quả thực tế", 42800000, 0, 100000000000),
      field("target", "Mục tiêu cùng kỳ", 40000000, 0, 100000000000),
      field("coverage", "Độ phủ dữ liệu (%)", 96, 0, 100),
      field("minimumCoverage", "Độ phủ tối thiểu (%)", 90, 0, 100),
      field("ageHours", "Tuổi snapshot (giờ)", 2, 0, 87600),
      field("maxAgeHours", "Tuổi snapshot tối đa (giờ)", 24, 0, 87600)
    ], (v) => {
      if (v.target === 0) throw new Error("Mục tiêu bằng 0; không thể tính phần trăm biến động.");
      const variance = round((v.actual - v.target) / Math.abs(v.target) * 100);
      const usable = v.coverage >= v.minimumCoverage && v.ageHours <= v.maxAgeHours;
      return result(!usable ? "Không đủ điều kiện so sánh" : variance >= 0 ? "Đạt / vượt mục tiêu" : "Thấp hơn mục tiêu",
        !usable ? "gold" : variance >= 0 ? "green" : "red",
        usable ? `Biến động ${variance}% so với cùng kỳ; chỉ so sánh khi kỳ, tiền tệ và định nghĩa KPI đồng nhất.` : `Độ phủ ${v.coverage}% hoặc freshness không đạt; báo cáo phải hiển thị N/A.`,
        `(${v.actual} − ${v.target}) / |${v.target}| × 100 = ${variance}%; coverage ${v.coverage} ≥ ${v.minimumCoverage}; freshness ${v.ageHours}h ≤ ${v.maxAgeHours}h`);
    }),

    inventory: define("Tái dựng khả dụng và đề xuất bổ sung", [
      field("onHand", "Tồn ghi sổ", 24, 0, 100000000),
      field("reserved", "Đã giữ chỗ", 5, 0, 100000000),
      field("quarantined", "Cách ly / hỏng", 1, 0, 100000000),
      field("reorderPoint", "Mức tồn mục tiêu", 12, 0, 100000000),
      field("onOrder", "Số lượng đang đặt", 2, 0, 100000000)
    ], (v) => {
      if (v.reserved + v.quarantined > v.onHand) throw new Error("Giữ chỗ và cách ly không thể vượt tồn ghi sổ.");
      const available = v.onHand - v.reserved - v.quarantined;
      const suggested = Math.max(0, v.reorderPoint - available - v.onOrder);
      return result(suggested ? "Cần tạo đề nghị bổ sung" : "Tồn đạt ngưỡng",
        suggested ? "gold" : "green",
        `Khả dụng ${available}; đề xuất mua thêm ${suggested} sau khi trừ hàng đã đặt. Đây chưa phải lệnh mua.`,
        `${v.onHand} − ${v.reserved} − ${v.quarantined} = ${available}; max(0, ${v.reorderPoint} − ${available} − ${v.onOrder}) = ${suggested}`);
    }),

    procurement: define("Nhu cầu mua theo lead time và ngân sách", [
      field("dailyDemand", "Nhu cầu trung bình / ngày", 4, 0, 1000000),
      field("leadDays", "Thời gian cung ứng (ngày)", 7, 0, 3650),
      field("safetyStock", "Tồn an toàn", 8, 0, 10000000),
      field("available", "Tồn khả dụng", 12, 0, 10000000),
      field("onOrder", "Đang đặt chưa nhận", 4, 0, 10000000),
      field("minimumOrder", "Số lượng tối thiểu (MOQ)", 10, 1, 10000000),
      field("packSize", "Quy cách đóng gói", 2, 1, 10000000),
      field("unitCost", "Giá dự kiến / đơn vị (₫)", 125000, 0, 1000000000, 0.01),
      field("budgetRemaining", "Ngân sách còn lại (₫)", 5000000, 0, 100000000000, 0.01)
    ], (v) => {
      const leadDemand = Math.ceil(v.dailyDemand * v.leadDays);
      const rawNeed = Math.max(0, leadDemand + v.safetyStock - v.available - v.onOrder);
      const quantity = rawNeed === 0 ? 0 : Math.ceil(Math.max(rawNeed, v.minimumOrder) / v.packSize) * v.packSize;
      const estimated = quantity * v.unitCost;
      const overBudget = estimated > v.budgetRemaining;
      return result(overBudget ? "Chặn · vượt ngân sách" : quantity ? "Đề xuất requisition" : "Chưa cần mua",
        overBudget ? "red" : quantity ? "gold" : "green",
        `Nhu cầu lead time ${leadDemand}; đề xuất ${quantity} đơn vị, dự kiến ${money(estimated)}${overBudget ? ` (vượt ${money(estimated - v.budgetRemaining)}).` : "."} Chưa phát hành PO.`,
        `max(0, ceil(${v.dailyDemand}×${v.leadDays}) + ${v.safetyStock} − ${v.available} − ${v.onOrder}) = ${rawNeed}; MOQ/pack => ${quantity}; ${quantity}×${v.unitCost} = ${estimated}`);
    }),

    suppliers: define("Cổng đủ điều kiện nhà cung cấp", [
      field("requiredDocs", "Tài liệu bắt buộc", 5, 1, 100),
      field("validDocs", "Tài liệu còn hiệu lực", 5, 0, 100),
      choice("active", "Trạng thái hợp tác", "active", options("active", "suspended")),
      field("contractDays", "Ngày còn hiệu lực hợp đồng", 90, -3650, 3650),
      choice("bankChange", "Có thay đổi tài khoản thanh toán", "no", options("no", "yes")),
      choice("maker", "Người đề xuất", "operator-a", options("operator-a", "operator-b")),
      choice("checker", "Người xác minh độc lập", "operator-b", options("operator-a", "operator-b"))
    ], (v) => {
      if (v.validDocs > v.requiredDocs) throw new Error("Số tài liệu hợp lệ không thể vượt tổng tài liệu bắt buộc.");
      const complete = v.validDocs === v.requiredDocs;
      const bankReview = v.bankChange === "no" || v.maker !== v.checker;
      const eligible = complete && v.active === "active" && v.contractDays >= 0 && bankReview;
      const completeness = Math.round(v.validDocs / v.requiredDocs * 100);
      return result(eligible ? "Đủ điều kiện tham chiếu mua hàng" : "Tạm giữ · cần rà soát",
        eligible ? "green" : "red",
        `Hồ sơ đạt ${completeness}%; ${eligible ? "hợp đồng và trạng thái hợp lệ." : "thiếu hồ sơ, hợp đồng hoặc xác minh độc lập."} Không thẩm định rủi ro pháp lý tự động.`,
        `docs ${v.validDocs}/${v.requiredDocs} (${completeness}%); active=${v.active}; contractDays=${v.contractDays}; bankChangeApproved=${bankReview}`);
    }),

    receiving: define("Đối chiếu PO · hàng nhận · hóa đơn", [
      field("ordered", "Số lượng PO", 24, 0, 10000000),
      field("received", "Số lượng giao đến", 24, 0, 10000000),
      field("rejected", "Số lượng bị từ chối / cách ly", 0, 0, 10000000),
      field("invoiceQty", "Số lượng trên hóa đơn", 24, 0, 10000000),
      field("poUnitPrice", "Đơn giá PO (₫)", 125000, 0, 1000000000, 0.01),
      field("invoiceUnitPrice", "Đơn giá hóa đơn (₫)", 125000, 0, 1000000000, 0.01),
      field("quantityTolerance", "Sai lệch số lượng cho phép", 0, 0, 100000),
      field("priceTolerancePct", "Sai lệch giá cho phép (%)", 1, 0, 100),
      field("expiryDays", "Số ngày đến hạn dùng", 365, 0, 36500),
      field("minimumExpiryDays", "Hạn dùng tối thiểu cần có (ngày)", 90, 0, 36500),
      choice("invoicePresent", "Có hóa đơn đối chiếu", "yes", options("yes", "no"))
    ], (v) => {
      if (v.rejected > v.received) throw new Error("Số lượng từ chối không thể lớn hơn số lượng giao đến.");
      const accepted = v.received - v.rejected;
      const qtyDelta = v.invoiceQty - accepted;
      const priceDeltaPct = v.poUnitPrice === 0
        ? v.invoiceUnitPrice === 0 ? 0 : 100
        : Math.abs(v.invoiceUnitPrice - v.poUnitPrice) / v.poUnitPrice * 100;
      const checks = [
        Math.abs(qtyDelta) <= v.quantityTolerance,
        priceDeltaPct <= v.priceTolerancePct,
        v.expiryDays >= v.minimumExpiryDays,
        v.invoicePresent === "yes"
      ];
      const pass = checks.every(Boolean);
      return result(pass ? "Khớp · chờ checker xác nhận" : "Sai lệch · cách ly / rà soát",
        pass ? "green" : "red",
        `Đạt ${checks.filter(Boolean).length}/4 điều kiện; nhận đạt ${accepted} đơn vị, lệch hóa đơn ${qtyDelta}, lệch giá ${round(priceDeltaPct)}%. Không tự tăng tồn.`,
        `accepted=${v.received}−${v.rejected}=${accepted}; qtyDelta=${qtyDelta}; priceVariance=${round(priceDeltaPct)}% (limit ${v.priceTolerancePct}%); expiry ${v.expiryDays}d ≥ ${v.minimumExpiryDays}d; invoice=${v.invoicePresent}`);
    }),

    transfers: define("Kiểm soát điều chuyển hai đầu", [
      choice("sourceBranch", "Chi nhánh nguồn", "HN-01", options("HN-01", "HCM-02", "DN-01", "CT-01")),
      choice("destinationBranch", "Chi nhánh đích", "HCM-02", options("HN-01", "HCM-02", "DN-01", "CT-01")),
      field("sourceAvailable", "Khả dụng tại nguồn", 30, 0, 10000000),
      field("requested", "Số lượng yêu cầu", 12, 1, 10000000),
      field("dispatched", "Đã dispatch", 12, 0, 10000000),
      field("received", "Đã nhận tại đích", 0, 0, 10000000),
      field("lost", "Thiếu / hỏng có xác nhận", 0, 0, 10000000)
    ], (v) => {
      if (v.received + v.lost > v.dispatched) throw new Error("Nhận cộng thiếu/hỏng không thể vượt số đã dispatch.");
      const inTransit = v.dispatched - v.received - v.lost;
      const validRoute = v.sourceBranch !== v.destinationBranch;
      const withinSource = v.requested <= v.sourceAvailable;
      const validDispatch = v.dispatched <= v.requested;
      const pass = validRoute && withinSource && validDispatch;
      const status = !validRoute ? "Chặn · nguồn và đích trùng" :
        !withinSource ? "Chặn · vượt khả dụng nguồn" :
          !validDispatch ? "Chặn · dispatch vượt yêu cầu" :
            inTransit ? "Đang vận chuyển" : v.lost ? "Cần điều tra thiếu/hỏng" : v.received === v.dispatched ? "Đã nhận đủ" : "Chờ dispatch";
      const tone = !pass || v.lost ? "red" : inTransit || v.dispatched < v.requested ? "gold" : "green";
      return result(status, tone,
        `Còn ${inTransit} đơn vị trên đường; chỉ cộng tồn đích khi xác nhận nhận. ${pass ? "Không ghi chuyển động tồn trong sandbox." : "Yêu cầu bị chặn."}`,
        `inTransit=${v.dispatched}−${v.received}−${v.lost}=${inTransit}; route ${v.sourceBranch}≠${v.destinationBranch}; dispatch ${v.dispatched}≤${v.requested}≤${v.sourceAvailable}`);
    }),

    adjustments: define("Kiểm kê và cổng điều chỉnh tồn", [
      field("bookQty", "Số lượng theo sổ", 24, 0, 10000000),
      field("countedQty", "Số lượng kiểm đếm", 22, 0, 10000000),
      field("materiality", "Ngưỡng yêu cầu recount", 2, 0, 1000000),
      choice("reason", "Mã lý do", "damage", options("damage", "count-error", "expiry", "loss", "other")),
      choice("evidence", "Có bằng chứng", "yes", options("yes", "no")),
      choice("period", "Trạng thái kỳ", "open", options("open", "locked")),
      choice("maker", "Người lập", "operator-a", options("operator-a", "operator-b")),
      choice("checker", "Checker độc lập", "operator-b", options("operator-a", "operator-b"))
    ], (v) => {
      const delta = v.countedQty - v.bookQty;
      const recount = Math.abs(delta) >= v.materiality && Math.abs(delta) > 0;
      const valid = v.reason !== "other" && v.evidence === "yes" && v.period === "open" && v.maker !== v.checker;
      const pass = valid && !recount;
      const blockers = [
        v.reason === "other" ? "cần reason cụ thể" : "",
        v.evidence !== "yes" ? "thiếu bằng chứng" : "",
        v.period !== "open" ? "kỳ đã khóa" : "",
        v.maker === v.checker ? "maker trùng checker" : "",
        recount ? "cần recount độc lập" : ""
      ].filter(Boolean);
      return result(pass ? "Đủ điều kiện gửi duyệt" : recount ? "Chặn · yêu cầu recount" : "Chặn · thiếu kiểm soát",
        pass ? "green" : "red",
        `Chênh lệch ${delta > 0 ? "+" : ""}${delta}; ${blockers.length ? blockers.join(", ") : "đủ kiểm soát"}. Chưa post movement.`,
        `delta=${v.countedQty}−${v.bookQty}=${delta}; |delta| ${Math.abs(delta)} ${recount ? "≥" : "<"} ${v.materiality}; reason=${v.reason}; evidence=${v.evidence}; period=${v.period}; maker≠checker=${v.maker !== v.checker}`);
    }),

    approvals: define("Ma trận maker–checker và hạn mức", [
      choice("maker", "Người lập", "operator-a", options("operator-a", "operator-b")),
      choice("checker", "Người duyệt", "operator-b", options("operator-a", "operator-b")),
      field("amount", "Giá trị yêu cầu (₫)", 8400000, 0, 100000000000, 0.01),
      field("checkerLimit", "Hạn mức checker (₫)", 10000000, 0, 100000000000, 0.01),
      field("approvalThreshold", "Ngưỡng cần phê duyệt (₫)", 100000, 0, 100000000000, 0.01),
      choice("versionCurrent", "Phiên bản yêu cầu", "yes", options("yes", "no")),
      choice("period", "Trạng thái kỳ", "open", options("open", "locked"))
    ], (v) => {
      const required = v.amount >= v.approvalThreshold;
      const independent = v.maker !== v.checker;
      const limitOk = v.amount <= v.checkerLimit;
      const versionOk = v.versionCurrent === "yes";
      const periodOpen = v.period === "open";
      const pass = (!required || independent) && limitOk && versionOk && periodOpen;
      const gates = [independent || !required, limitOk, versionOk, periodOpen];
      return result(pass ? required ? "Đạt cổng duyệt độc lập" : "Dưới ngưỡng phê duyệt" : "Chặn · không đủ điều kiện duyệt",
        pass ? "green" : "red",
        `Đạt ${gates.filter(Boolean).length}/4 cổng; amount=${money(v.amount)}, hạn mức=${money(v.checkerLimit)}. Kết quả chỉ là khuyến nghị sandbox.`,
        `maker≠checker=${independent}; amount ${v.amount} ${required ? "≥" : "<"} threshold ${v.approvalThreshold}; amount≤limit=${limitOk}; version=${versionOk}; periodOpen=${periodOpen}`);
    }),

    finance: define("Đối chiếu settlement và kỳ kế toán", [
      field("expected", "Số tiền kỳ vọng (₫)", 8420000, -100000000000, 100000000000, 0.01),
      field("settled", "Số tiền settlement (₫)", 8378000, -100000000000, 100000000000, 0.01),
      field("fees", "Phí được chứng từ (₫)", 42000, 0, 100000000000, 0.01),
      field("tolerance", "Sai lệch cho phép (₫)", 1000, 0, 1000000000, 0.01),
      choice("currencyMatch", "Đồng tiền khớp", "yes", options("yes", "no")),
      choice("referenceMatch", "Tham chiếu giao dịch exact", "yes", options("yes", "no")),
      choice("period", "Trạng thái kỳ", "open", options("open", "locked"))
    ], (v) => {
      const residual = round(v.expected - v.settled - v.fees);
      const pass = Math.abs(residual) <= v.tolerance && v.currencyMatch === "yes" &&
        v.referenceMatch === "yes" && v.period === "open";
      return result(pass ? "Khớp · chờ finance checker" : v.period === "locked" ? "Chặn · kỳ đã khóa" : "Có ngoại lệ settlement",
        pass ? "green" : "red",
        `Residual ${money(residual)}; ${pass ? "có thể đưa vào hàng đợi checker." : "giữ suspense và không tự tạo bút toán."}`,
        `${v.expected} − ${v.settled} − ${v.fees} = ${residual}; |residual|≤${v.tolerance}; currency=${v.currencyMatch}; reference=${v.referenceMatch}; period=${v.period}`);
    }),

    reconciliation: define("Ghép đối soát exact và residual", [
      field("sourceA", "Tổng nguồn A (₫)", 1000000, -100000000000, 100000000000, 0.01),
      field("sourceB", "Tổng nguồn B (₫)", 999500, -100000000000, 100000000000, 0.01),
      field("tolerance", "Tolerance (₫)", 1000, 0, 1000000000, 0.01),
      field("duplicateRows", "Số dòng trùng", 0, 0, 10000000),
      field("unmatchedRows", "Số dòng chưa ghép", 0, 0, 10000000),
      choice("currencyMatch", "Đồng tiền đồng nhất", "yes", options("yes", "no")),
      choice("referenceMatch", "Khóa tham chiếu exact", "yes", options("yes", "no"))
    ], (v) => {
      const residual = round(v.sourceA - v.sourceB);
      const pass = Math.abs(residual) <= v.tolerance && v.duplicateRows === 0 &&
        v.unmatchedRows === 0 && v.currencyMatch === "yes" && v.referenceMatch === "yes";
      return result(pass ? "Khớp trong tolerance" : "Cần xử lý exception",
        pass ? "green" : "red",
        `Residual ${money(residual)}; duplicate ${v.duplicateRows}, unmatched ${v.unmatchedRows}. Không dùng fuzzy match để tự ghi sổ.`,
        `${v.sourceA} − ${v.sourceB} = ${residual}; |residual|≤${v.tolerance}; duplicate=0; unmatched=0; currency=${v.currencyMatch}; reference=${v.referenceMatch}`);
    }),

    reports: define("Tổng hợp KPI có denominator và freshness", [
      field("eligible", "Bản ghi đủ điều kiện", 100, 0, 100000000),
      field("completed", "Bản ghi hoàn tất", 78, 0, 100000000),
      field("coverage", "Độ phủ chi nhánh (%)", 96, 0, 100),
      field("minimumCoverage", "Độ phủ tối thiểu (%)", 90, 0, 100),
      field("snapshotAgeHours", "Tuổi snapshot (giờ)", 2, 0, 87600),
      field("maxAgeHours", "Tuổi snapshot tối đa (giờ)", 24, 0, 87600)
    ], (v) => {
      if (v.completed > v.eligible) throw new Error("Số hoàn tất không thể vượt số bản ghi đủ điều kiện.");
      const rate = v.eligible ? round(v.completed / v.eligible * 100, 1) : null;
      const valid = v.eligible > 0 && v.coverage >= v.minimumCoverage && v.snapshotAgeHours <= v.maxAgeHours;
      return result(!valid ? "Không phát hành KPI · dữ liệu thiếu/stale" : "Snapshot KPI hợp lệ",
        !valid ? "gold" : "green",
        valid ? `Tỷ lệ hoàn tất ${rate}%; mẫu số ${v.eligible}, coverage ${v.coverage}%.` : `Tỷ lệ ${rate === null ? "N/A" : `${rate}%`}; thiếu mẫu số, độ phủ hoặc freshness.`,
        `${v.completed}/${v.eligible || "0"}×100 = ${rate === null ? "N/A" : `${rate}%`}; coverage ${v.coverage}≥${v.minimumCoverage}; age ${v.snapshotAgeHours}h≤${v.maxAgeHours}h`);
    }),

    audit: define("Cổng đầy đủ audit event", [
      choice("actorPresent", "Có actor / role", "yes", options("yes", "no")),
      choice("actionPresent", "Có action", "yes", options("yes", "no")),
      choice("entityPresent", "Có entity/version", "yes", options("yes", "no")),
      choice("reasonPresent", "Có lý do", "yes", options("yes", "no")),
      choice("correlationPresent", "Có request/correlation ID", "yes", options("yes", "no")),
      choice("timestampValid", "Timestamp hợp lệ", "yes", options("yes", "no")),
      choice("containsSensitiveData", "Có secret/PII không cần thiết", "no", options("no", "yes"))
    ], (v) => {
      const required = [v.actorPresent, v.actionPresent, v.entityPresent, v.reasonPresent, v.correlationPresent, v.timestampValid];
      const pass = required.every((value) => value === "yes") && v.containsSensitiveData === "no";
      const missing = required.filter((value) => value !== "yes").length;
      return result(pass ? "Event đủ điều kiện ghi audit" : "Chặn thao tác nhạy cảm",
        pass ? "green" : "red",
        `Thiếu ${missing} trường bắt buộc; ${v.containsSensitiveData === "yes" ? "phải loại secret/PII trước khi ghi." : "không sửa/xóa event đã ghi."}`,
        `actor/action/entity/reason/correlation/timestamp=${required.join("/")}; sensitiveData=${v.containsSensitiveData}`);
    }),

    integrations: define("Cổng contract và sức khỏe connector", [
      field("requiredFields", "Trường contract bắt buộc", 12, 1, 100000),
      field("mappedFields", "Trường đã ánh xạ", 12, 0, 100000),
      field("lagMinutes", "Độ trễ hiện tại (phút)", 5, 0, 525600),
      field("maxLagMinutes", "Độ trễ tối đa (phút)", 30, 0, 525600),
      field("retryCount", "Số lần retry", 0, 0, 100000),
      field("maxRetries", "Retry tối đa", 5, 0, 100000),
      field("deadLetterCount", "Số event DLQ", 0, 0, 10000000),
      choice("schemaSupported", "Schema version được hỗ trợ", "yes", options("yes", "no")),
      choice("tenantMatch", "Tenant scope khớp", "yes", options("yes", "no")),
      choice("purposeAllowed", "Purpose được phép", "yes", options("yes", "no"))
    ], (v) => {
      if (v.mappedFields > v.requiredFields) throw new Error("Số trường đã ánh xạ không thể vượt số trường bắt buộc.");
      const coverage = round(v.mappedFields / v.requiredFields * 100, 1);
      const gates = [
        coverage === 100,
        v.lagMinutes <= v.maxLagMinutes,
        v.retryCount <= v.maxRetries,
        v.deadLetterCount === 0,
        v.schemaSupported === "yes",
        v.tenantMatch === "yes",
        v.purposeAllowed === "yes"
      ];
      const pass = gates.every(Boolean);
      return result(pass ? "Connector đạt contract" : "Cách ly / cần xử lý",
        pass ? "green" : "red",
        `Đạt ${gates.filter(Boolean).length}/7 cổng; coverage ${coverage}%, lag ${v.lagMinutes} phút, DLQ ${v.deadLetterCount}.`,
        `coverage=${v.mappedFields}/${v.requiredFields}=${coverage}%; lag≤${v.maxLagMinutes}; retries≤${v.maxRetries}; DLQ=0; schema/tenant/purpose=${v.schemaSupported}/${v.tenantMatch}/${v.purposeAllowed}`);
    }),

    settings: define("Dry-run và kiểm tra thay đổi policy", [
      choice("ownerApproved", "Owner đã xác nhận", "yes", options("yes", "no")),
      choice("reviewerApproved", "Reviewer độc lập", "yes", options("yes", "no")),
      field("dryRunErrors", "Lỗi trong dry-run", 0, 0, 100000),
      field("proposedMinimum", "Ngưỡng nhỏ nhất đề xuất", 5, 0, 1000000),
      field("proposedMaximum", "Ngưỡng lớn nhất đề xuất", 50, 0, 1000000),
      field("allowedMinimum", "Giới hạn nhỏ nhất theo schema", 0, 0, 1000000),
      field("allowedMaximum", "Giới hạn lớn nhất theo schema", 100, 0, 1000000),
      choice("backwardCompatible", "Tương thích dữ liệu hiện có", "yes", options("yes", "no")),
      choice("rollbackReady", "Có version rollback đã xác minh", "yes", options("yes", "no"))
    ], (v) => {
      const rangeValid = v.proposedMinimum <= v.proposedMaximum &&
        v.proposedMinimum >= v.allowedMinimum && v.proposedMaximum <= v.allowedMaximum;
      const gates = [
        v.ownerApproved === "yes",
        v.reviewerApproved === "yes",
        v.dryRunErrors === 0,
        rangeValid,
        v.backwardCompatible === "yes",
        v.rollbackReady === "yes"
      ];
      const pass = gates.every(Boolean);
      return result(pass ? "Đủ điều kiện tạo version đề xuất" : "NO-GO · không áp dụng",
        pass ? "green" : "red",
        `Đạt ${gates.filter(Boolean).length}/6 cổng; cấu hình chỉ đủ điều kiện gửi publish, không tự áp dụng.`,
        `owner=${v.ownerApproved}; reviewer=${v.reviewerApproved}; dryRunErrors=${v.dryRunErrors}; range=${v.proposedMinimum}..${v.proposedMaximum} within ${v.allowedMinimum}..${v.allowedMaximum} (${rangeValid}); compatible=${v.backwardCompatible}; rollback=${v.rollbackReady}`);
    })
  };

  const routes = Object.freeze(Object.fromEntries(
    Object.entries(algorithms).map(([route, engine]) => [route, engine])
  ));

  window.PetBusinessAlgorithms = Object.freeze({
    routes,
    get(route) {
      const engine = routes[route];
      if (!engine) throw new Error(`Chưa có thuật toán Pet Business cho route "${route}".`);
      return engine;
    }
  });
})();
