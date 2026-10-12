(() => {
  "use strict";

  const page = document.querySelector("[data-slip-type]");
  if (!page) return;
  const slipType = page.dataset.slipType;
  const byId = (id) => document.getElementById(id);
  const escapeHtml = (value) => String(value ?? "").replace(/[&<>"']/g, (character) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  })[character]);
  let definition;
  let savedRecord;

  async function api(path, options = {}) {
    const response = await fetch(`/api${path}`, {
      credentials: "same-origin",
      ...options
    });
    let result;
    try {
      result = await response.json();
    } catch {
      throw new Error(`Máy chủ trả về dữ liệu không hợp lệ (${response.status}).`);
    }
    if (!response.ok) throw new Error(result.error || `Yêu cầu thất bại (${response.status}).`);
    return result;
  }

  function setStatus(message, error = false) {
    const status = byId("slipStatus");
    status.textContent = message;
    status.hidden = !message;
    status.classList.toggle("error", error);
  }

  function renderForm() {
    byId("slipCategory").textContent = definition.category;
    byId("slipTitle").textContent = `Phiếu ${String(definition.number).padStart(2, "0")} · ${definition.title}`;
    byId("slipDescription").textContent = definition.problem;
    document.title = `${definition.title} · Phiếu xuất Bông Bông Pet Care`;
    const fields = byId("slipFields");
    fields.innerHTML = definition.fields.map((field) => {
      const wide = field.type === "textarea" ? " wide" : "";
      const control = field.type === "textarea"
        ? `<textarea id="field-${field.name}" name="${field.name}" ${field.required ? "required" : ""}></textarea>`
        : `<input id="field-${field.name}" name="${field.name}" type="${field.type}" ${field.required ? "required" : ""} ${field.type === "number" ? 'min="0.000001" step="any"' : ""}>`;
      return `<div class="slip-field${wide}"><label for="field-${field.name}">${escapeHtml(field.label)}${field.required ? " *" : ""}</label>${control}</div>`;
    }).join("");
    const dateField = byId("field-issue_date");
    if (dateField) {
      const now = new Date();
      dateField.value = new Date(now.getTime() - now.getTimezoneOffset() * 60000).toISOString().slice(0, 10);
    }
    if (definition.category === "Bàn giao thú cưng") {
      const animalQuantity = byId("field-quantity");
      if (animalQuantity) {
        animalQuantity.step = "1";
        animalQuantity.min = "1";
      }
    }
    fields.addEventListener("input", onFormEdit);
    fields.addEventListener("change", onFormEdit);
  }

  function onFormEdit() {
    if (!savedRecord) return;
    savedRecord = null;
    byId("slipPaper").classList.remove("visible");
    byId("printSlip").disabled = true;
    byId("saveSlip").disabled = false;
    setStatus("Biểu mẫu đã thay đổi. Hãy lưu thành hồ sơ mới trước khi in.");
  }

  function currentPayload() {
    return Object.fromEntries(definition.fields.map((field) => {
      const control = byId(`field-${field.name}`);
      return [field.name, control.type === "number" && control.value ? Number(control.value) : control.value.trim()];
    }));
  }

  function renderPaper(record) {
    const payload = record.payload;
    byId("slipPaperTitle").textContent = definition.title;
    byId("slipPaperCode").textContent = record.code;
    byId("slipPaperDate").textContent = payload.issue_date || record.created_at;
    byId("slipData").innerHTML = definition.fields
      .filter((field) => payload[field.name] !== "" && payload[field.name] !== undefined)
      .map((field) => `<div class="slip-data-item"><strong>${escapeHtml(field.label)}</strong>${escapeHtml(payload[field.name])}</div>`)
      .join("");
    byId("slipPaper").classList.add("visible");
    byId("printSlip").disabled = false;
  }

  function addHistoryButton(record) {
    const item = document.createElement("li");
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = `${record.slip_code} · ${record.created_at}`;
    button.addEventListener("click", () => openSavedRecord(record.id));
    item.append(button);
    byId("slipHistory").prepend(item);
  }

  async function openSavedRecord(id) {
    try {
      const result = await api(`/store/slips/${encodeURIComponent(id)}`);
      savedRecord = result.record;
      for (const field of definition.fields) {
        const control = byId(`field-${field.name}`);
        if (control) control.value = result.record.payload[field.name] ?? "";
      }
      byId("saveSlip").disabled = true;
      renderPaper(savedRecord);
      setStatus(`Đang xem lại phiếu đã lưu ${savedRecord.code}. Không chỉnh sửa được bản ghi này.`);
    } catch (error) {
      setStatus(error.message, true);
    }
  }

  async function loadHistory() {
    const result = await api(`/store/slips?type=${encodeURIComponent(slipType)}`);
    byId("slipHistory").replaceChildren();
    if (!result.records.length) {
      const empty = document.createElement("li");
      empty.textContent = "Chưa có phiếu nào được lưu.";
      byId("slipHistory").append(empty);
      return;
    }
    for (const record of result.records) addHistoryButton(record);
  }

  byId("loginForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    setStatus("");
    try {
      await api("/login", {
        method: "POST",
        headers: {"Content-Type": "application/json", "X-PetCare-Request": "1"},
        body: JSON.stringify({
          username: byId("username").value,
          password: byId("password").value
        })
      });
      byId("password").value = "";
      await initialize();
    } catch (error) {
      setStatus(error.message, true);
    }
  });

  byId("slipForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    byId("saveSlip").disabled = true;
    setStatus("");
    try {
      const result = await api("/store/slips", {
        method: "POST",
        headers: {"Content-Type": "application/json", "X-PetCare-Request": "1"},
        body: JSON.stringify({type: slipType, payload: currentPayload()})
      });
      savedRecord = result.record;
      renderPaper(savedRecord);
      await loadHistory();
      setStatus(`Đã lưu phiếu ${savedRecord.code} vào SQLite. Có thể in hoặc mở lại từ danh sách phiếu đã lưu.`);
    } catch (error) {
      byId("saveSlip").disabled = false;
      setStatus(error.message, true);
    }
  });

  byId("printSlip").addEventListener("click", () => {
    if (savedRecord) window.print();
  });

  async function initialize() {
    if (location.protocol !== "http:") {
      throw new Error("Hãy mở trang từ máy chủ cục bộ PetCare (http://localhost), không mở trực tiếp bằng file HTML.");
    }
    const session = await api("/session");
    if (!session.authenticated) throw new Error("Đăng nhập nhân viên để tiếp tục.");
    const result = await api(`/store/slip-types/${encodeURIComponent(slipType)}`);
    definition = result.type;
    renderForm();
    byId("staffName").textContent = `Nhân viên: ${session.user.display_name} · ${session.user.role}`;
    byId("loginPanel").hidden = true;
    byId("slipWorkspace").hidden = false;
    await loadHistory();
    setStatus("");
  }

  initialize().catch((error) => {
    byId("loginPanel").hidden = false;
    byId("slipWorkspace").hidden = true;
    setStatus(error.message, true);
  });
})();
