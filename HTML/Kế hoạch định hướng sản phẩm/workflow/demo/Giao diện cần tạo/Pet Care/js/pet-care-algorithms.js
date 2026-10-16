(() => {
  "use strict";

  const number = (name, label, value, min, max, step = 1) =>
    ({ name, label, type: "number", value, min, max, step });
  const select = (name, label, value, ...values) =>
    ({ name, label, type: "select", value, options: values.map((item) => [item, item]) });
  const round = (value, digits = 1) => Number(value.toFixed(digits));
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
      if (!output || typeof output.status !== "string" || typeof output.tone !== "string" ||
          typeof output.summary !== "string" || typeof output.calculation !== "string") {
        throw new Error(`Thuật toán "${name}" trả về kết quả không hợp lệ.`);
      }
      return output;
    }
  });
  const result = (status, tone, summary, calculation) => ({ status, tone, summary, calculation });

  const routes = {
    overview: define("Ưu tiên hàng đợi chăm sóc", [
      number("urgency", "Mức khẩn cấp do nhân viên đánh dấu (1–3)", 2, 1, 3),
      number("impact", "Ảnh hưởng vận hành (1–3)", 2, 1, 3),
      number("ageHours", "Thời gian đang chờ (giờ)", 4, 0, 720),
      select("ownerAssigned", "Đã phân công người phụ trách", "yes", "yes", "no"),
      select("healthEscalation", "Đã đánh dấu cần bác sĩ đánh giá", "no", "yes", "no")
    ], (v) => {
      const score = Math.min(100, v.urgency * 35 + v.impact * 25 + Math.min(v.ageHours, 12) * 2);
      const status = v.healthEscalation === "yes" ? "Chuyển nhân viên chuyên môn" :
        v.ownerAssigned === "no" ? "Chưa có người phụ trách" :
          score >= 75 ? "Ưu tiên cao" : score >= 45 ? "Theo dõi" : "Thông thường";
      const tone = v.healthEscalation === "yes" || v.ownerAssigned === "no" || score >= 75
        ? "red" : score >= 45 ? "gold" : "green";
      return result(status, tone,
        `Điểm ưu tiên ${score}/100. Điểm số chỉ sắp thứ tự công việc, không đánh giá tình trạng y tế.`,
        `min(100, ${v.urgency}×35 + ${v.impact}×25 + min(${v.ageHours},12)×2) = ${score}; owner=${v.ownerAssigned}; clinicalEscalation=${v.healthEscalation}`);
    }),

    pets: define("Kiểm tra hồ sơ thú cưng và trùng khóa chính xác", [
      number("requiredFields", "Trường bắt buộc", 6, 1, 100),
      number("validFields", "Trường hợp lệ", 5, 0, 100),
      select("petIdPresent", "Có pet ID", "yes", "yes", "no"),
      select("ownerIdPresent", "Có owner ID", "yes", "yes", "no"),
      select("microchipDuplicate", "Microchip trùng chính xác", "no", "yes", "no"),
      select("ownerSpeciesNameDuplicate", "Trùng owner + loài + tên đã chuẩn hóa", "no", "yes", "no")
    ], (v) => {
      if (v.validFields > v.requiredFields) throw new Error("Trường hợp lệ không thể vượt tổng trường bắt buộc.");
      const completeness = Math.round(v.validFields / v.requiredFields * 100);
      const duplicate = v.microchipDuplicate === "yes" || v.ownerSpeciesNameDuplicate === "yes";
      const ready = v.petIdPresent === "yes" && v.ownerIdPresent === "yes" && completeness >= 80 && !duplicate;
      return result(duplicate ? "Có khả năng trùng · xác minh thủ công" : ready ? "Hồ sơ đủ điều kiện rà soát" : "Thiếu trường bắt buộc",
        duplicate ? "gold" : ready ? "green" : "red",
        `Độ đầy đủ ${completeness}%. Không tự gộp hồ sơ; trùng tên đơn lẻ không đủ căn cứ.`,
        `completeness=${v.validFields}/${v.requiredFields}×100=${completeness}%; duplicate=exactMicrochip(${v.microchipDuplicate}) OR exactOwnerSpeciesName(${v.ownerSpeciesNameDuplicate})`);
    }),

    customers: define("Kiểm tra hồ sơ khách hàng và consent liên hệ", [
      number("requiredFields", "Trường bắt buộc", 5, 1, 100),
      number("validFields", "Trường hợp lệ", 5, 0, 100),
      select("customerIdPresent", "Có customer ID", "yes", "yes", "no"),
      select("normalizedContactUnique", "Liên hệ chuẩn hóa không trùng", "yes", "yes", "no"),
      select("contactConsent", "Consent cho kênh liên hệ", "yes", "yes", "no"),
      select("nameOnlyMatch", "Chỉ trùng tên với hồ sơ khác", "no", "yes", "no")
    ], (v) => {
      if (v.validFields > v.requiredFields) throw new Error("Trường hợp lệ không thể vượt tổng trường bắt buộc.");
      const completeness = Math.round(v.validFields / v.requiredFields * 100);
      const ready = completeness >= 80 && v.customerIdPresent === "yes" &&
        v.normalizedContactUnique === "yes" && v.contactConsent === "yes";
      return result(ready ? v.nameOnlyMatch === "yes" ? "Hồ sơ đạt · tên trùng cần xem xét" : "Hồ sơ đạt kiểm tra" : "Chặn liên hệ / cần bổ sung",
        ready ? v.nameOnlyMatch === "yes" ? "gold" : "green" : "red",
        `Độ đầy đủ ${completeness}%; chỉ dùng kênh có consent. Không tự hợp nhất khách theo tên.`,
        `completeness=${completeness}%; customerId=${v.customerIdPresent}; uniqueContact=${v.normalizedContactUnique}; contactConsent=${v.contactConsent}; nameOnlyMatch is not an auto-merge key`);
    }),

    "care-tasks": define("Ưu tiên task và SLA chăm sóc", [
      number("urgency", "Mức khẩn cấp (1–3)", 2, 1, 3),
      number("impact", "Mức ảnh hưởng (1–3)", 2, 1, 3),
      number("ageHours", "Thời gian chờ (giờ)", 6, 0, 720),
      number("slaHours", "SLA mục tiêu (giờ)", 8, 0.25, 720, 0.25),
      select("ownerAssigned", "Đã phân công người phụ trách", "yes", "yes", "no"),
      select("checklistComplete", "Checklist đã xác nhận hoàn tất", "no", "yes", "no"),
      select("clinicalFlag", "Có dấu hiệu cần chuyển chuyên môn", "no", "yes", "no")
    ], (v) => {
      const score = Math.min(100, v.urgency * 35 + v.impact * 25 + Math.min(v.ageHours, 12) * 2);
      const overdue = v.ageHours > v.slaHours && v.checklistComplete !== "yes";
      const status = v.clinicalFlag === "yes" ? "Escalate theo quy trình chuyên môn" :
        v.ownerAssigned === "no" ? "Cần gán người phụ trách" :
          overdue ? "Quá SLA · cần theo dõi" : v.checklistComplete === "yes" ? "Hoàn tất do nhân viên xác nhận" : `Đang mở · điểm ${score}/100`;
      return result(status, v.clinicalFlag === "yes" || overdue || v.ownerAssigned === "no" ? "red" :
        score >= 60 ? "gold" : "green",
      "Task không tự hoàn tất; xác nhận checklist và mọi escalations do nhân viên có trách nhiệm thực hiện.",
      `score=min(100, ${v.urgency}×35 + ${v.impact}×25 + min(${v.ageHours},12)×2)=${score}; overdue=${v.ageHours}>${v.slaHours} AND incomplete; owner=${v.ownerAssigned}; clinicalFlag=${v.clinicalFlag}`);
    }),

    "health-records": define("Consent và quyền truy cập hồ sơ sức khỏe", [
      select("tenantMatch", "Clinic/tenant khớp", "yes", "yes", "no"),
      select("purposeAllowed", "Mục đích sử dụng được phép", "yes", "yes", "no"),
      select("requestedScope", "Scope yêu cầu", "summary", "minimum", "summary", "full-record"),
      select("grantedScope", "Scope đã cấp", "summary", "minimum", "summary", "full-record"),
      number("consentHoursRemaining", "Consent còn hiệu lực (giờ)", 24, 0, 87600),
      number("minimumValidityHours", "Thời hạn tối thiểu cần có (giờ)", 1, 0, 87600),
      select("actorAuthorized", "Actor có vai trò được cấp", "yes", "yes", "no")
    ], (v) => {
      const rank = { minimum: 1, summary: 2, "full-record": 3 };
      const scopeAllowed = rank[v.requestedScope] <= rank[v.grantedScope];
      const active = v.consentHoursRemaining > 0 && v.consentHoursRemaining >= v.minimumValidityHours;
      const allowed = v.tenantMatch === "yes" && v.purposeAllowed === "yes" &&
        scopeAllowed && active && v.actorAuthorized === "yes";
      return result(allowed ? "Cho phép scope tối thiểu theo demo" : "Từ chối mặc định · thiếu quyền/consent",
        allowed ? "green" : "red",
        `${allowed ? "Đủ" : "Không đủ"} điều kiện scope, purpose, tenant, actor và thời hạn. Không hiển thị hoặc diễn giải nội dung y khoa.`,
        `allow=${v.tenantMatch} AND ${v.purposeAllowed} AND scope(${v.requestedScope})⊆${v.grantedScope}(${scopeAllowed}) AND ${v.consentHoursRemaining}h≥${v.minimumValidityHours}h AND actor=${v.actorAuthorized}`);
    }),

    appointments: define("Kiểm tra slot lịch hẹn và xung đột", [
      number("openMinute", "Giờ mở cửa (phút trong ngày)", 480, 0, 1439),
      number("closeMinute", "Giờ đóng cửa (phút trong ngày)", 1080, 1, 1440),
      number("startMinute", "Bắt đầu lịch (phút trong ngày)", 600, 0, 1439),
      number("durationMinute", "Thời lượng (phút)", 60, 1, 1440),
      number("bufferMinute", "Buffer sau lượt (phút)", 15, 0, 480),
      number("existingStart", "Lịch hiện có bắt đầu (phút)", 0, 0, 1439),
      number("existingEnd", "Lịch hiện có kết thúc (phút)", 0, 0, 1440),
      select("staffAvailable", "Nhân viên phù hợp và rảnh", "yes", "yes", "no"),
      select("resourceAvailable", "Tài nguyên phù hợp và rảnh", "yes", "yes", "no"),
      select("bookingConfirmed", "Booking đã được người dùng xác nhận", "no", "yes", "no")
    ], (v) => {
      if (v.closeMinute <= v.openMinute) throw new Error("Giờ đóng cửa phải sau giờ mở cửa trong cùng ngày.");
      if ((v.existingStart === 0) !== (v.existingEnd === 0) || v.existingEnd < v.existingStart) {
        throw new Error("Khoảng lịch hiện có không hợp lệ; dùng 0/0 nếu không có lịch xung đột.");
      }
      const end = v.startMinute + v.durationMinute + v.bufferMinute;
      const overlap = v.existingEnd > v.existingStart &&
        v.startMinute < v.existingEnd && v.existingStart < end;
      const withinHours = v.startMinute >= v.openMinute && end <= v.closeMinute;
      const available = v.staffAvailable === "yes" && v.resourceAvailable === "yes";
      const fits = withinHours && !overlap && available;
      return result(!fits ? "Không khả dụng · chọn slot khác" :
        v.bookingConfirmed === "yes" ? "Đã xác nhận bởi người dùng" : "Slot phù hợp · chưa giữ chỗ",
        !fits ? "red" : v.bookingConfirmed === "yes" ? "green" : "gold",
        `${fits ? "Không phát hiện" : "Có"} xung đột; thuật toán không tự giữ slot hoặc xác nhận booking.`,
        `end=${v.startMinute}+${v.durationMinute}+${v.bufferMinute}=${end}; hours=${withinHours}; overlap([${v.startMinute},${end}),[${v.existingStart},${v.existingEnd}))=${overlap}; staff/resource=${available}`);
    }),

    services: define("Kiểm tra catalog dịch vụ và hiệu lực", [
      number("durationMinutes", "Thời lượng (phút)", 60, 1, 1440),
      number("price", "Giá dịch vụ (₫)", 350000, 0, 1000000000, 0.01),
      number("resourceDemand", "Số tài nguyên yêu cầu", 1, 1, 100),
      select("speciesRule", "Quy tắc loài đã khai báo", "yes", "yes", "no"),
      select("effectiveDatesValid", "Khoảng ngày hiệu lực hợp lệ", "yes", "yes", "no"),
      select("versionUnique", "Version mới, không sửa hồi tố", "yes", "yes", "no"),
      select("safetyNotesReviewed", "Ghi chú tiếp nhận đã rà soát", "yes", "yes", "no")
    ], (v) => {
      const gates = [v.durationMinutes > 0, v.price >= 0, v.resourceDemand > 0,
        v.speciesRule === "yes", v.effectiveDatesValid === "yes",
        v.versionUnique === "yes", v.safetyNotesReviewed === "yes"];
      const ready = gates.every(Boolean);
      return result(ready ? "Đủ điều kiện gửi duyệt catalog" : "Chặn xuất bản dịch vụ",
        ready ? "green" : "red",
        `Đạt ${gates.filter(Boolean).length}/7 điều kiện; giá/version chỉ có hiệu lực sau owner review.`,
        `duration>0 AND price≥0 AND resourceDemand>0 AND speciesRule AND validDates AND newVersion AND safetyNotesReviewed = ${ready}`);
    }),

    sales: define("Đối chiếu đơn hàng read-only", [
      number("localTotal", "Tổng tham chiếu cục bộ (₫)", 850000, 0, 100000000000, 0.01),
      number("sourceTotal", "Tổng từ nguồn đơn (₫)", 850000, 0, 100000000000, 0.01),
      number("tolerance", "Sai lệch cho phép (₫)", 1000, 0, 1000000000, 0.01),
      select("currencyMatch", "Đồng tiền khớp", "yes", "yes", "no"),
      select("sourceVersionCurrent", "Version snapshot hiện hành", "yes", "yes", "no"),
      select("paymentVerified", "Thanh toán đã xác minh từ nguồn", "yes", "yes", "no"),
      select("orderCanceled", "Đơn đã hủy", "no", "yes", "no")
    ], (v) => {
      const delta = round(v.localTotal - v.sourceTotal, 2);
      const matched = Math.abs(delta) <= v.tolerance && v.currencyMatch === "yes" &&
        v.sourceVersionCurrent === "yes";
      const fulfillmentReady = matched && v.paymentVerified === "yes" && v.orderCanceled === "no";
      return result(!matched ? "Cách ly · cần đối soát" :
        v.orderCanceled === "yes" ? "Đơn đã hủy · không thực hiện" :
          v.paymentVerified !== "yes" ? "Chờ xác minh thanh toán" : "Khớp tham chiếu · chờ nhân viên",
        !matched || v.orderCanceled === "yes" ? "red" : fulfillmentReady ? "green" : "gold",
        `Sai lệch ${delta} ₫. Không capture tiền, phân bổ hàng hoặc đổi trạng thái đơn tự động.`,
        `${v.localTotal}−${v.sourceTotal}=${delta}; |delta|≤${v.tolerance}; currency=${v.currencyMatch}; version=${v.sourceVersionCurrent}; payment=${v.paymentVerified}; canceled=${v.orderCanceled}`);
    }),

    inventory: define("Tính tồn khả dụng và gợi ý bổ sung", [
      number("onHand", "Tồn ghi nhận", 24, 0, 10000000),
      number("reserved", "Đã giữ chỗ", 5, 0, 10000000),
      number("quarantined", "Cách ly / hỏng", 1, 0, 10000000),
      number("minimumLevel", "Mức tồn tối thiểu", 12, 0, 10000000),
      number("onOrder", "Đang đặt chưa nhận", 2, 0, 10000000),
      number("daysToExpiry", "Số ngày đến hạn dùng", 365, 0, 36500),
      select("lotQuarantined", "Lô đang cách ly", "no", "yes", "no")
    ], (v) => {
      if (v.reserved + v.quarantined > v.onHand) throw new Error("Giữ chỗ và cách ly không thể vượt tồn ghi nhận.");
      const available = v.onHand - v.reserved - v.quarantined;
      const sellable = v.lotQuarantined === "no" && v.daysToExpiry > 0 ? available : 0;
      const reorder = Math.max(0, v.minimumLevel - sellable - v.onOrder);
      return result(v.lotQuarantined === "yes" || v.daysToExpiry === 0 ? "Lô không khả dụng · kiểm tra" :
        reorder ? "Cần xem xét bổ sung" : "Đủ ngưỡng demo",
        v.lotQuarantined === "yes" || v.daysToExpiry === 0 ? "red" : reorder ? "gold" : "green",
        `Tồn khả dụng ${available}; bán được ${sellable}; đề xuất xem xét ${reorder}. Không tạo movement/PO.`,
        `available=${v.onHand}−${v.reserved}−${v.quarantined}=${available}; sellable=${sellable}; reorder=max(0,${v.minimumLevel}−${sellable}−${v.onOrder})=${reorder}`);
    }),

    suppliers: define("Kiểm tra hồ sơ nhà cung cấp", [
      number("requiredDocs", "Tài liệu bắt buộc", 5, 1, 100),
      number("validDocs", "Tài liệu còn hiệu lực", 5, 0, 100),
      select("status", "Trạng thái nhà cung cấp", "active", "active", "suspended"),
      number("contractDaysRemaining", "Ngày hợp đồng còn hiệu lực", 90, -3650, 36500),
      select("bankChange", "Có đổi tài khoản thanh toán", "no", "yes", "no"),
      select("maker", "Người đề xuất", "operator-a", "operator-a", "operator-b"),
      select("checker", "Checker độc lập", "operator-b", "operator-a", "operator-b")
    ], (v) => {
      if (v.validDocs > v.requiredDocs) throw new Error("Tài liệu hợp lệ không thể vượt số tài liệu bắt buộc.");
      const verified = v.validDocs === v.requiredDocs && v.status === "active" &&
        v.contractDaysRemaining >= 0 && (v.bankChange === "no" || v.maker !== v.checker);
      return result(verified ? "Đủ điều kiện tham chiếu mua hàng" : "Tạm giữ · cần xác minh",
        verified ? "green" : "red",
        `Không hiển thị thông tin ngân hàng; đổi thông tin nhạy cảm cần checker độc lập.`,
        `docs=${v.validDocs}/${v.requiredDocs}; status=${v.status}; contractDays=${v.contractDaysRemaining}; bankChangeIndependent=${v.bankChange === "no" || v.maker !== v.checker}`);
    }),

    reminders: define("Lập nhắc việc có consent và chống gửi trùng", [
      number("hoursUntilDue", "Số giờ đến lịch/task", 24, -87600, 87600, 0.25),
      number("sendWindowHours", "Cửa sổ gửi trước hạn (giờ)", 48, 0, 87600, 0.25),
      select("contactConsent", "Consent kênh gửi còn hiệu lực", "yes", "yes", "no"),
      select("contactVerified", "Kênh liên hệ đã xác minh", "yes", "yes", "no"),
      select("duplicateExists", "Đã có nhắc cùng event/kênh", "no", "yes", "no"),
      select("eventCanceled", "Lịch/task đã hủy", "no", "yes", "no")
    ], (v) => {
      const inWindow = v.hoursUntilDue >= 0 && v.hoursUntilDue <= v.sendWindowHours;
      const allowed = inWindow && v.contactConsent === "yes" && v.contactVerified === "yes" &&
        v.duplicateExists === "no" && v.eventCanceled === "no";
      const status = v.eventCanceled === "yes" ? "Không gửi · sự kiện đã hủy" :
        v.duplicateExists === "yes" ? "Không gửi trùng" :
          v.contactConsent !== "yes" ? "Chặn · thiếu consent" :
            allowed ? "Đủ điều kiện đưa vào hàng đợi gửi" : "Chưa đến cửa sổ nhắc";
      return result(status, allowed ? "green" : "gold",
        "Chỉ lập đề xuất nhắc; gửi thật cần dịch vụ notification và kiểm tra consent tại thời điểm gửi.",
        `window=${v.hoursUntilDue}h∈[0,${v.sendWindowHours}h](${inWindow}); consent=${v.contactConsent}; verified=${v.contactVerified}; duplicate=${v.duplicateExists}; canceled=${v.eventCanceled}`);
    }),

    reports: define("Tổng hợp KPI có mẫu số và độ mới", [
      number("eligible", "Bản ghi đủ điều kiện", 100, 0, 100000000),
      number("completed", "Bản ghi hoàn tất", 78, 0, 100000000),
      number("coveragePct", "Độ phủ dữ liệu (%)", 96, 0, 100),
      number("minimumCoveragePct", "Độ phủ tối thiểu (%)", 90, 0, 100),
      number("snapshotAgeHours", "Tuổi snapshot (giờ)", 2, 0, 87600),
      number("maxAgeHours", "Tuổi tối đa cho phép (giờ)", 24, 0, 87600),
      number("cohortSize", "Quy mô cohort", 100, 0, 100000000),
      number("minimumCohort", "Ngưỡng ẩn cohort nhỏ", 10, 1, 100000000)
    ], (v) => {
      if (v.completed > v.eligible) throw new Error("Bản ghi hoàn tất không thể vượt mẫu số đủ điều kiện.");
      const rate = v.eligible ? round(v.completed / v.eligible * 100) : null;
      const valid = rate !== null && v.coveragePct >= v.minimumCoveragePct &&
        v.snapshotAgeHours <= v.maxAgeHours && v.cohortSize >= v.minimumCohort;
      return result(valid ? "Snapshot đủ điều kiện báo cáo" : "Ẩn / đánh dấu N/A",
        valid ? "green" : "gold",
        valid ? `Tỷ lệ hoàn tất ${rate}% trên ${v.eligible} bản ghi.` :
          `Không công bố KPI: thiếu mẫu số, coverage/freshness hoặc cohort nhỏ.`,
        `${v.completed}/${v.eligible || 0}×100=${rate === null ? "N/A" : `${rate}%`}; coverage=${v.coveragePct}≥${v.minimumCoveragePct}; age=${v.snapshotAgeHours}h≤${v.maxAgeHours}h; cohort=${v.cohortSize}≥${v.minimumCohort}`);
    }),

    audit: define("Kiểm tra sự kiện audit tối thiểu", [
      select("actorPresent", "Có actor và vai trò", "yes", "yes", "no"),
      select("actionPresent", "Có hành động", "yes", "yes", "no"),
      select("subjectPresent", "Có đối tượng/ID", "yes", "yes", "no"),
      select("timestampValid", "Timestamp hợp lệ", "yes", "yes", "no"),
      select("reasonPresent", "Có lý do cho thay đổi nhạy cảm", "yes", "yes", "no"),
      select("requestIdPresent", "Có request/correlation ID", "yes", "yes", "no"),
      select("containsUnnecessaryPii", "Có PII không cần thiết", "no", "yes", "no")
    ], (v) => {
      const required = [v.actorPresent, v.actionPresent, v.subjectPresent, v.timestampValid,
        v.reasonPresent, v.requestIdPresent];
      const complete = required.every((value) => value === "yes") && v.containsUnnecessaryPii === "no";
      const missing = required.filter((value) => value !== "yes").length;
      return result(complete ? "Event đủ trường kiểm tra" : "Chặn thao tác nhạy cảm",
        complete ? "green" : "red",
        `${missing} trường bắt buộc thiếu; ${v.containsUnnecessaryPii === "yes" ? "loại PII không cần thiết trước khi ghi." : "không sửa event gốc."}`,
        `actor/action/subject/time/reason/request=${required.join("/")}; unnecessaryPII=${v.containsUnnecessaryPii}`);
    }),

    integrations: define("Cổng contract cho trao đổi dữ liệu", [
      number("requiredFields", "Trường contract bắt buộc", 10, 1, 100000),
      number("mappedFields", "Trường đã ánh xạ", 10, 0, 100000),
      select("schemaSupported", "Schema được hỗ trợ", "yes", "yes", "no"),
      select("tenantMatch", "Tenant/scope khớp", "yes", "yes", "no"),
      select("purposeAllowed", "Mục đích chia sẻ được phép", "yes", "yes", "no"),
      select("consentActive", "Consent đang hiệu lực nếu cần", "yes", "yes", "no"),
      number("lagMinutes", "Độ trễ hiện tại (phút)", 5, 0, 525600),
      number("maxLagMinutes", "Độ trễ tối đa (phút)", 30, 0, 525600),
      number("retryCount", "Số lần retry", 0, 0, 100000),
      number("retryLimit", "Giới hạn retry", 5, 0, 100000),
      number("deadLetterCount", "Event trong DLQ", 0, 0, 10000000)
    ], (v) => {
      if (v.mappedFields > v.requiredFields) throw new Error("Số trường đã ánh xạ không thể vượt tổng trường bắt buộc.");
      const coverage = round(v.mappedFields / v.requiredFields * 100);
      const gates = [coverage === 100, v.schemaSupported === "yes", v.tenantMatch === "yes",
        v.purposeAllowed === "yes", v.consentActive === "yes", v.lagMinutes <= v.maxLagMinutes,
        v.retryCount <= v.retryLimit, v.deadLetterCount === 0];
      const pass = gates.every(Boolean);
      return result(pass ? "Đủ điều kiện nhận event" : "Cách ly · cần xử lý",
        pass ? "green" : "red",
        `Đạt ${gates.filter(Boolean).length}/8 cổng; coverage ${coverage}%, DLQ ${v.deadLetterCount}. Không chuyển lỗi thành thành công.`,
        `coverage=${coverage}%; schema=${v.schemaSupported}; tenant=${v.tenantMatch}; purpose=${v.purposeAllowed}; consent=${v.consentActive}; lag≤${v.maxLagMinutes}; retry≤${v.retryLimit}; DLQ=0`);
    }),

    settings: define("Dry-run cấu hình Pet Care", [
      select("ownerApproved", "Domain owner đã xác nhận", "yes", "yes", "no"),
      select("reviewerApproved", "Reviewer độc lập", "yes", "yes", "no"),
      select("schemaValid", "Cấu hình đúng schema", "yes", "yes", "no"),
      select("scopeValid", "Tenant/clinic scope hợp lệ", "yes", "yes", "no"),
      number("dryRunErrors", "Lỗi dry-run", 0, 0, 100000),
      select("backwardCompatible", "Tương thích dữ liệu hiện có", "yes", "yes", "no"),
      select("rollbackReady", "Có version rollback đã kiểm chứng", "yes", "yes", "no")
    ], (v) => {
      const gates = [v.ownerApproved === "yes", v.reviewerApproved === "yes",
        v.schemaValid === "yes", v.scopeValid === "yes", v.dryRunErrors === 0,
        v.backwardCompatible === "yes", v.rollbackReady === "yes"];
      const pass = gates.every(Boolean);
      return result(pass ? "Đủ điều kiện gửi publish review" : "NO-GO · giữ cấu hình hiện hành",
        pass ? "green" : "red",
        `Đạt ${gates.filter(Boolean).length}/7 cổng; không tự áp dụng policy hoặc thay đổi quyền truy cập.`,
        `owner=${v.ownerApproved}; reviewer=${v.reviewerApproved}; schema=${v.schemaValid}; scope=${v.scopeValid}; dryRunErrors=${v.dryRunErrors}; compatible=${v.backwardCompatible}; rollback=${v.rollbackReady}`);
    })
  };

  const frozenRoutes = Object.freeze(Object.fromEntries(
    Object.entries(routes).map(([key, algorithm]) => [key, algorithm])
  ));
  window.PetCareAlgorithms = Object.freeze({
    routes: frozenRoutes,
    get(route) {
      const algorithm = frozenRoutes[route];
      if (!algorithm) throw new Error(`Chưa có thuật toán Pet Care cho route "${route}".`);
      return algorithm;
    }
  });
})();
