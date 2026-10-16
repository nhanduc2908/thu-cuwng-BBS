(() => {
  const STORAGE_KEY = "waggy-ecosystem-demo-sync-v2";
  const SCHEMA_VERSION = 4;
  const dataset = window.WaggySharedDemoData;
  if (!dataset || dataset.schemaVersion !== 2 || !dataset.systems || !Array.isArray(dataset.records)) {
    throw new Error("Thiếu bộ dữ liệu dùng chung trong thư mục data.");
  }
  const systems = dataset.systems;
  const blueprints = dataset.records;
  const now = () => new Date().toISOString();
  const makeId = (prefix) => `${prefix}-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 7)}`;
  const createInitialState = () => ({
    schemaVersion: SCHEMA_VERSION,
    revision: 1,
    lastSyncAt: null,
    records: blueprints.map((record) => ({
      ...record,
      payload: { ...record.payload },
      references: record.references || [],
      version: 1,
      replicas: Object.fromEntries(record.targets.map((target) => [target, {
        version: 1,
        fields: Object.fromEntries((record.projections[target] || []).map((field) => [field, record.payload[field]]))
      }]))
    })),
    events: [],
    conflicts: [],
    audit: [{ id: "AUDIT-SEED", at: now(), message: "Nạp bộ dữ liệu giả lập ban đầu · 8 miền nghiệp vụ." }]
  });
  let store;
  let storageAvailable = true;
  let mountedRoot;
  let currentSystem;
  let notify = () => {};
  let loaded = false;
  const subscribers = new Set();

  const projectFields = (record, target) => Object.fromEntries(
    (record.projections[target] || []).map((field) => [field, record.payload[field]])
  );
  const isCurrentRecord = (record) => record && typeof record.id === "string" &&
    typeof record.type === "string" && typeof record.label === "string" &&
    systems[record.source] && typeof record.field === "string" &&
    typeof record.value === "string" && Number.isInteger(record.version) && record.version > 0 &&
    record.payload && typeof record.payload === "object" && record.payload[record.field] === record.value &&
    Array.isArray(record.targets) && record.targets.every((target) =>
      systems[target] && record.projections?.[target] &&
      record.replicas?.[target] && record.replicas[target].fields &&
      Array.isArray(record.projections[target]) &&
      record.projections[target].includes(record.field) &&
      record.projections[target].every((field) => Object.prototype.hasOwnProperty.call(record.replicas[target].fields, field))
    ) && Array.isArray(record.references);

  const migrateState = (parsed) => {
    const initial = createInitialState();
    const previousRecords = Array.isArray(parsed.records) ? parsed.records : [];
    initial.records = initial.records.map((seed) => {
      const previous = previousRecords.find((record) => record.id === seed.id);
      if (!previous) return seed;
      const migrated = {
        ...seed,
        version: Number.isInteger(previous.version) && previous.version > 0 ? previous.version : 1,
        value: typeof previous.value === "string" ? previous.value : seed.value
      };
      migrated.payload[migrated.field] = migrated.value;
      migrated.replicas = Object.fromEntries(migrated.targets.map((target) => [
        target,
        { version: migrated.version, fields: projectFields(migrated, target) }
      ]));
      return migrated;
    });
    initial.revision = Number.isInteger(parsed.revision) ? parsed.revision : initial.revision;
    initial.lastSyncAt = parsed.lastSyncAt || null;
    initial.events = Array.isArray(parsed.events) ? parsed.events.map((event) => ({
      ...event,
      schemaVersion: event.status === "pending" ? SCHEMA_VERSION : event.schemaVersion
    })) : [];
    initial.conflicts = Array.isArray(parsed.conflicts) ? parsed.conflicts : [];
    initial.audit = Array.isArray(parsed.audit) ? parsed.audit.slice(0, 30) : initial.audit;
    return initial;
  };

  const load = () => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) {
        store = createInitialState();
        loaded = true;
        save();
        return;
      }
      const parsed = JSON.parse(raw);
      if (![2, 3, SCHEMA_VERSION].includes(parsed.schemaVersion) || !Array.isArray(parsed.records) || !Array.isArray(parsed.events) ||
          (parsed.schemaVersion === SCHEMA_VERSION && !parsed.records.every(isCurrentRecord))) {
        throw new Error("Phiên bản dữ liệu demo không hợp lệ.");
      }
      store = parsed.schemaVersion === SCHEMA_VERSION ? parsed : migrateState(parsed);
      if (parsed.schemaVersion !== SCHEMA_VERSION) save();
      loaded = true;
    } catch (error) {
      storageAvailable = false;
      if (store) return;
      store = createInitialState();
      loaded = true;
      notify(`Không đọc được kho demo đã lưu (${error.message}). Đang dùng dữ liệu tạm trong tab này; hãy nạp lại bộ mẫu để khôi phục.`);
    }
  };
  const save = () => {
    store.revision += 1;
    if (!storageAvailable) return;
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(store));
      subscribers.forEach((subscriber) => subscriber());
    } catch (error) {
      storageAvailable = false;
      notify(`Không thể lưu trạng thái demo trên trình duyệt (${error.message}). Thao tác chỉ còn trong tab hiện tại.`);
    }
  };
  const recordById = (id) => store.records.find((record) => record.id === id);
  const snapshotFor = (system) => {
    if (!systems[system]) throw new Error(`Hệ thống không hợp lệ: ${system}`);
    if (!loaded) load();
    const records = store.records
      .filter((record) => record.source === system || record.targets.includes(system))
      .map((record) => {
        const isOwner = record.source === system;
        const fields = isOwner ? record.payload : record.replicas[system]?.fields;
        if (!fields) return null;
        return {
          id: record.id,
          type: record.type,
          label: record.label,
          source: record.source,
          sourceName: systems[record.source],
          value: isOwner ? record.value : fields[record.field],
          version: isOwner ? record.version : (record.replicas[system]?.version || 1),
          fields: { ...fields },
          references: record.references.filter((reference) => isOwner || fields[reference.id] !== undefined || record.targets.includes(system)),
          scope: record.scope,
          owner: isOwner
        };
      })
      .filter(Boolean);
    return {
      schemaVersion: SCHEMA_VERSION,
      revision: store.revision,
      lastSyncAt: store.lastSyncAt,
      storageAvailable,
      records
    };
  };
  const pushAudit = (message) => {
    store.audit.unshift({ id: makeId("AUD"), at: now(), message });
    store.audit = store.audit.slice(0, 30);
  };
  const createEvent = (record, source, value) => ({
    id: makeId("EVT"),
    schemaVersion: SCHEMA_VERSION,
    entityId: record.id,
    source,
    field: record.field,
    baseVersion: record.version,
    value,
    createdAt: now(),
    status: "pending"
  });
  const render = () => {
    if (!mountedRoot || !store) return;
    const pending = store.events.filter((event) => event.status === "pending").length;
    const openConflicts = store.conflicts.filter((conflict) => conflict.status === "open").length;
    const visibleRecords = store.records.filter((record) =>
      record.source === currentSystem || record.targets.includes(currentSystem)
    );
    const records = visibleRecords.map((record) => {
      const syncCount = Object.keys(record.replicas).length;
      const references = record.references.map((reference) => `${reference.id} · ${reference.relation}`).join(" | ");
      const projectedFields = currentSystem === record.source
        ? record.payload
        : record.replicas[currentSystem]?.fields || {};
      const dataSummary = Object.entries(projectedFields)
        .map(([key, value]) => `${key}: ${Array.isArray(value) ? value.join(", ") : value}`)
        .join(" · ");
      return `<tr>
        <td><strong>${escapeHtml(record.id)}</strong><small>${escapeHtml(record.type)}</small></td>
        <td>${escapeHtml(record.label)}<small>${escapeHtml(dataSummary)}</small></td>
        <td>${escapeHtml(references || "Bản ghi độc lập")}</td>
        <td>${escapeHtml(systems[record.source])}</td>
        <td><span class="sync-version">v${record.version}</span><small>${syncCount} hệ thống nhận</small></td>
        <td>${escapeHtml(record.scope)}</td>
      </tr>`;
    }).join("");
    const recentEvents = [...store.events].slice(-5).reverse().map((event) => `
      <div class="sync-event"><span class="sync-event-dot ${event.status}"></span><div><strong>${escapeHtml(event.entityId)} · ${escapeHtml(event.statusLabel || event.status)}</strong><small>${escapeHtml(systems[event.source] || event.source)} · ${escapeHtml(event.value)}</small></div><time>${new Date(event.createdAt).toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit" })}</time></div>`).join("");
    const conflicts = store.conflicts.filter((conflict) => conflict.status === "open").map((conflict) => `
      <article class="sync-conflict"><div><strong>${escapeHtml(conflict.entityId)} · phiên bản gốc v${conflict.baseVersion} → v${conflict.currentVersion}</strong><p>Giá trị đang giữ: <b>${escapeHtml(conflict.currentValue)}</b><br>Giá trị đến sau: <b>${escapeHtml(conflict.incomingValue)}</b></p></div><div class="sync-conflict-actions"><button type="button" data-sync-resolve="${escapeHtml(conflict.id)}" data-strategy="keep-current">Giữ bản hiện hành</button><button type="button" data-sync-resolve="${escapeHtml(conflict.id)}" data-strategy="accept-incoming">Duyệt bản đến</button></div></article>`).join("");
    mountedRoot.innerHTML = `
      <div class="sync-heading"><div><span class="sync-eyebrow">WAGGY ECOSYSTEM · SANDBOX</span><h2 id="sync-title">Trung tâm đồng bộ &amp; đánh giá</h2><p>Một bộ dữ liệu giả liên thông 8 miền; theo dõi phiên bản, luồng sự kiện, quyền chia sẻ và xung đột.</p></div><span class="sync-storage ${storageAvailable ? "" : "warning"}">${storageAvailable ? "Lưu cục bộ trình duyệt" : "Chỉ lưu trong tab"}</span></div>
      <div class="sync-stats">
        <article><span>Miền dữ liệu</span><strong>08</strong><small>8 hệ thống · một bộ khóa tham chiếu</small></article>
        <article><span>Thực thể dữ liệu</span><strong>${store.records.length}</strong><small>${visibleRecords.length} bản ghi liên quan hệ thống đang chọn</small></article>
        <article><span>Đang chờ</span><strong>${pending}</strong><small>Sự kiện chưa xử lý</small></article>
        <article class="${openConflicts ? "attention" : ""}"><span>Xung đột mở</span><strong>${openConflicts}</strong><small>${openConflicts ? "Cần quyết định thủ công" : "Không có xung đột mở"}</small></article>
      </div>
      <div class="sync-toolbar">
        <div class="sync-toolbar-copy"><strong>Đang xem: ${escapeHtml(systems[currentSystem])}</strong><span>Phạm vi chỉ gồm dữ liệu sở hữu và các trường được phép nhận từ 7 hệ thống còn lại.</span><label class="sync-system-picker">Chọn miền dữ liệu <select data-sync-system aria-label="Chọn hệ thống để xem dữ liệu chung">${Object.entries(systems).map(([id, name]) => `<option value="${id}" ${id === currentSystem ? "selected" : ""}>${escapeHtml(name)}</option>`).join("")}</select></label></div>
        <div class="sync-actions">
          <button type="button" data-sync-action="change">Tạo sự kiện mẫu</button>
          <button type="button" data-sync-action="conflict">Tạo xung đột kiểm thử</button>
          <button type="button" class="primary" data-sync-action="run">Chạy đồng bộ</button>
          <button type="button" data-sync-action="export">Xuất dữ liệu JSON</button>
          <button type="button" data-sync-action="reset">Nạp lại dữ liệu mẫu</button>
        </div>
      </div>
      ${conflicts ? `<div class="sync-conflicts"><h3>Hàng đợi cần phân xử <span>${openConflicts}</span></h3>${conflicts}</div>` : ""}
      <div class="sync-columns">
        <div class="sync-table-wrap"><div class="sync-subhead"><div><h3>Sổ dữ liệu chung · ${visibleRecords.length} bản ghi</h3><p>Quan hệ dùng mã tham chiếu; mỗi hệ thống chỉ xem projection theo quyền khai báo.</p></div><span>v${store.revision} · ${store.lastSyncAt ? `Đồng bộ ${new Date(store.lastSyncAt).toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit" })}` : "Chưa chạy batch"}</span></div><div class="table-wrap"><table class="sync-table"><thead><tr><th>Thực thể</th><th>Dữ liệu được cấp</th><th>Liên kết</th><th>Nguồn chuẩn</th><th>Phiên bản</th><th>Phạm vi</th></tr></thead><tbody>${records}</tbody></table></div></div>
        <aside class="sync-side"><div class="sync-subhead"><div><h3>Luồng sự kiện</h3><p>Event ID · schema · trạng thái xử lý</p></div></div><div class="sync-event-list">${recentEvents || `<p class="sync-empty">Chưa có sự kiện. Tạo thay đổi mẫu để bắt đầu.</p>`}</div><div class="sync-algorithm"><h3>Quy tắc đồng bộ</h3><ol><li><b>Validate:</b> schema, ID và quyền nguồn.</li><li><b>Deduplicate:</b> event ID chỉ áp dụng một lần.</li><li><b>Version check:</b> base version không khớp sẽ vào hàng đợi xung đột.</li><li><b>Project:</b> chỉ phát các trường/aggregate được cho phép.</li><li><b>Audit:</b> ghi kết quả; xung đột cần người duyệt.</li></ol></div></aside>
      </div>
      <div class="sync-audit"><strong>Nhật ký đánh giá</strong><div>${store.audit.slice(0, 4).map((entry) => `<span><time>${new Date(entry.at).toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit", second: "2-digit" })}</time>${escapeHtml(entry.message)}</span>`).join("")}</div></div>
      <p class="sync-disclaimer">Mô hình minh họa chạy trên localStorage của trình duyệt, không có server, giao dịch, dữ liệu khách thật hay bảo đảm nhất quán phân tán. Không dùng kết quả này thay cho đặc tả/kiểm thử production.</p>`;
  };
  const escapeHtml = (value) => String(value).replace(/[&<>"']/g, (char) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  })[char]);
  const createChange = () => {
    const primaryRecords = {
      "pet-care": "PET-1001",
      "pet-service": "SVC-2081",
      "pet-health": "HLT-0634",
      "pet-commerce": "COM-0917",
      "pet-business": "BUS-3408",
      "pet-community": "COM-0412",
      "pet-connect": "CON-24061",
      "pet-intelligence": "INT-0104"
    };
    const record = recordById(primaryRecords[currentSystem]) || store.records.find((item) => item.source === currentSystem);
    if (!record) {
      notify("Hệ thống này không có bản ghi mẫu để phát sự kiện.");
      return;
    }
    store.events.push(createEvent(record, currentSystem, `${record.value} · cập nhật v${record.version + 1}`));
    pushAudit(`Tạo sự kiện mẫu ${record.id} từ ${systems[currentSystem]}.`);
    save();
    render();
    notify(`Đã tạo sự kiện chờ đồng bộ cho ${record.id}.`);
  };
  const exportData = () => {
    const snapshot = snapshotFor(currentSystem);
    const payload = {
      title: "WAGGY shared demo dataset",
      exportedAt: now(),
      system: currentSystem,
      schemaVersion: snapshot.schemaVersion,
      revision: snapshot.revision,
      records: snapshot.records
    };
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = `waggy-${currentSystem}-shared-data.json`;
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    window.setTimeout(() => URL.revokeObjectURL(url), 1000);
    pushAudit(`Xuất ${snapshot.records.length} bản ghi projection của ${systems[currentSystem]}.`);
    save();
    render();
    notify("Đã xuất dữ liệu JSON theo đúng projection của hệ thống đang chọn.");
  };
  const createConflict = () => {
    const primaryRecords = {
      "pet-care": "PET-1001",
      "pet-service": "SVC-2081",
      "pet-health": "HLT-0634",
      "pet-commerce": "COM-0917",
      "pet-business": "BUS-3408",
      "pet-community": "COM-0412",
      "pet-connect": "CON-24061",
      "pet-intelligence": "INT-0104"
    };
    const record = recordById(primaryRecords[currentSystem]) || store.records.find((item) => item.source === currentSystem);
    if (!record) {
      notify("Hệ thống này không có bản ghi mẫu để tạo xung đột.");
      return;
    }
    const base = record.version;
    store.events.push(createEvent(record, currentSystem, `${record.value} · phiên A`));
    store.events.push(createEvent(record, currentSystem, `${record.value} · phiên B`));
    store.events[store.events.length - 1].baseVersion = base;
    pushAudit(`Tạo hai cập nhật đồng thời cho ${record.id} để kiểm tra optimistic locking.`);
    save();
    render();
    notify("Đã tạo hai sự kiện cùng base version; chạy đồng bộ để xem xung đột.");
  };
  const runSync = () => {
    const queue = store.events.filter((event) => event.status === "pending");
    if (!queue.length) {
      notify("Hàng đợi trống; không có sự kiện mới để đồng bộ.");
      return;
    }
    let applied = 0;
    let conflicts = 0;
    queue.forEach((event) => {
      if (event.schemaVersion !== SCHEMA_VERSION) {
        event.status = "quarantined";
        event.statusLabel = "Sai schema · cách ly";
        pushAudit(`Cách ly ${event.id}: schema không được hỗ trợ.`);
        return;
      }
      if (store.events.some((candidate) => candidate.id === event.id && candidate !== event && candidate.status === "synced")) {
        event.status = "duplicate";
        event.statusLabel = "Trùng · bỏ qua";
        return;
      }
      const record = recordById(event.entityId);
      if (!record || event.source !== record.source || event.field !== record.field) {
        event.status = "quarantined";
        event.statusLabel = "Nguồn không hợp lệ · cách ly";
        pushAudit(`Cách ly ${event.id}: bản ghi, nguồn chuẩn hoặc trường dữ liệu không hợp lệ.`);
        return;
      }
      if (event.baseVersion !== record.version) {
        event.status = "conflict";
        event.statusLabel = "Xung đột phiên bản";
        store.conflicts.push({
          id: makeId("CONFLICT"), eventId: event.id, entityId: record.id,
          baseVersion: event.baseVersion, currentVersion: record.version,
          currentValue: record.value, incomingValue: event.value, status: "open"
        });
        conflicts += 1;
        pushAudit(`${event.id} chuyển sang phân xử: ${record.id} đã ở v${record.version}.`);
        return;
      }
      record.value = event.value;
      record.version += 1;
      record.payload[record.field] = event.value;
      record.replicas = Object.fromEntries(record.targets.map((target) => [
        target,
        { version: record.version, fields: projectFields(record, target) }
      ]));
      event.status = "synced";
      event.statusLabel = "Đã áp dụng";
      event.appliedAt = now();
      applied += 1;
      pushAudit(`Áp dụng ${event.id} cho ${record.id} → v${record.version}; phát projection tới ${record.targets.length} đích.`);
    });
    store.lastSyncAt = now();
    save();
    render();
    notify(`Batch hoàn tất: ${applied} sự kiện áp dụng, ${conflicts} xung đột cần duyệt.`);
  };
  const resolveConflict = (conflictId, strategy) => {
    const conflict = store.conflicts.find((item) => item.id === conflictId && item.status === "open");
    if (!conflict) return;
    const record = recordById(conflict.entityId);
    if (!record) {
      notify(`Không thể phân xử: không tìm thấy bản ghi ${conflict.entityId}.`);
      return;
    }
    if (strategy === "accept-incoming") {
      record.value = conflict.incomingValue;
      record.version += 1;
      record.payload[record.field] = conflict.incomingValue;
      record.replicas = Object.fromEntries(record.targets.map((target) => [
        target,
        { version: record.version, fields: projectFields(record, target) }
      ]));
    }
    conflict.status = "resolved";
    conflict.resolution = strategy;
    conflict.resolvedAt = now();
    pushAudit(`Phân xử ${conflict.entityId}: ${strategy === "accept-incoming" ? "duyệt bản đến" : "giữ bản hiện hành"} tại v${record.version}.`);
    save();
    render();
    notify("Đã ghi nhận quyết định phân xử trong nhật ký demo.");
  };
  const reset = () => {
    store = createInitialState();
    storageAvailable = true;
    save();
    render();
    notify("Đã nạp lại dữ liệu giả lập ban đầu.");
  };
  const mount = (root, system, onNotify) => {
    mountedRoot = root;
    currentSystem = system;
    notify = onNotify;
    load();
    render();
    root.addEventListener("click", (event) => {
      const target = event.target.closest("[data-sync-action],[data-sync-resolve]");
      if (!target) return;
      if (target.dataset.syncAction === "change") createChange();
      if (target.dataset.syncAction === "conflict") createConflict();
      if (target.dataset.syncAction === "run") runSync();
      if (target.dataset.syncAction === "export") {
        try {
          exportData();
        } catch (error) {
          notify(`Không thể xuất dữ liệu JSON (${error.message}).`);
        }
      }
      if (target.dataset.syncAction === "reset") reset();
      if (target.dataset.syncResolve) resolveConflict(target.dataset.syncResolve, target.dataset.strategy);
    });
    root.addEventListener("change", (event) => {
      const picker = event.target.closest("[data-sync-system]");
      if (!picker || !systems[picker.value]) return;
      currentSystem = picker.value;
      const url = new URL(window.location.href);
      url.searchParams.set("system", currentSystem);
      window.history.replaceState({}, "", url);
      render();
    });
  };
  window.addEventListener("storage", (event) => {
    if (event.key !== STORAGE_KEY || !event.newValue) return;
    try {
      const next = JSON.parse(event.newValue);
      if (next.schemaVersion !== SCHEMA_VERSION || !Array.isArray(next.records) || !Array.isArray(next.events)) {
        throw new Error("Phiên bản kho dữ liệu không được hỗ trợ.");
      }
      store = next;
      loaded = true;
      if (mountedRoot) {
        render();
        notify("Nhận trạng thái dữ liệu chung mới từ tab khác.");
      }
      subscribers.forEach((subscriber) => subscriber());
    } catch (error) {
      if (mountedRoot) notify(`Không thể nạp bản đồng bộ từ tab khác (${error.message}).`);
    }
  });
  window.WaggyDemoSync = {
    mount,
    snapshotFor,
    subscribe(callback) {
      if (typeof callback !== "function") throw new TypeError("Callback đồng bộ phải là một hàm.");
      subscribers.add(callback);
      return () => subscribers.delete(callback);
    }
  };
})();
