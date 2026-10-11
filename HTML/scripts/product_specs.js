(() => {
  "use strict";

  const DATA_URL = "../data/pet_product_specs.json";
  const SCHEMA_URL = "../data/product_spec_fields.json";
  const UNKNOWN = "Chưa có dữ liệu được xác minh";
  const NOT_APPLICABLE = "Không áp dụng";
  const state = { products: [], groups: [], selectedProductId: null, compared: new Set() };
  const elements = {
    search: document.querySelector("#productSearch"),
    species: document.querySelector("#speciesFilter"),
    category: document.querySelector("#categoryFilter"),
    lifeStage: document.querySelector("#lifeStageFilter"),
    results: document.querySelector("#productResults"),
    count: document.querySelector("#resultCount"),
    detail: document.querySelector("#productDetails"),
    compare: document.querySelector("#comparison"),
    status: document.querySelector("#catalogStatus"),
    verifiedCount: document.querySelector("#verifiedCount"),
    fieldCount: document.querySelector("#fieldCount")
  };

  const escapeHtml = (value) => String(value ?? "").replace(/[&<>"']/g, (character) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  })[character]);
  const displayValue = (value) => {
    if (value === undefined || value === null || value === "") return UNKNOWN;
    if (typeof value === "object") {
      if (value.status === "not_applicable") return NOT_APPLICABLE;
      if (value.status === "not_disclosed") return "Không công bố trên nguồn đã đối chiếu";
      const amount = value.value ?? "";
      return [amount, value.unit].filter(Boolean).join(" ") || UNKNOWN;
    }
    return String(value);
  };
  const categoryLabel = (product) => product.categoryLabel || product.category || "Khác";
  const productMatches = (product) => {
    const query = elements.search.value.trim().toLocaleLowerCase("vi");
    const text = [
      product.brand, product.name, product.productLine, product.categoryLabel,
      product.speciesLabel, product.lifeStageLabel,
      product.intendedUse, product.specs?.intended_use, product.specs?.label_claims,
      ...(product.breeds || [])
    ].join(" ").toLocaleLowerCase("vi");
    return (!query || text.includes(query))
      && (!elements.species.value || product.species === elements.species.value)
      && (!elements.category.value || product.category === elements.category.value)
      && (!elements.lifeStage.value || (product.lifeStages || []).includes(elements.lifeStage.value));
  };

  function renderCards() {
    const products = state.products.filter(productMatches);
    elements.count.textContent = `${products.length} / ${state.products.length} sản phẩm`;
    if (!products.length) {
      elements.results.innerHTML = '<div class="spec-empty">Chưa có sản phẩm phù hợp với bộ lọc. Chỉ sản phẩm có nguồn nhãn/tài liệu chính thức mới được đưa vào danh mục.</div>';
      return;
    }
    elements.results.innerHTML = products.map((product) => {
      const checked = state.compared.has(product.id);
      return `<article class="product-card">
        <div class="product-meta"><span class="product-chip">${escapeHtml(product.speciesLabel || product.species)}</span><span class="product-chip">${escapeHtml(categoryLabel(product))}</span><span class="product-chip">${escapeHtml(product.verificationStatusLabel || "Chưa xác minh")}</span></div>
        <h3>${escapeHtml(product.name)}</h3><div class="product-brand">${escapeHtml(product.brand || "Chưa rõ thương hiệu")}</div>
        <p>${escapeHtml(product.intendedUse || "Công dụng sẽ hiển thị theo nhãn/tài liệu chính thức.")}</p>
        <div class="product-actions">
          <button class="spec-button primary" type="button" data-open="${escapeHtml(product.id)}">Xem đủ 70 thông số</button>
          <button class="spec-button" type="button" data-compare="${escapeHtml(product.id)}" aria-pressed="${checked}">${checked ? "Đã chọn so sánh" : "So sánh"}</button>
        </div>
      </article>`;
    }).join("");
  }

  function renderDetail(productId) {
    const product = state.products.find((item) => item.id === productId);
    if (!product) return;
    state.selectedProductId = productId;
    const specValues = product.specs || {};
    const groupsHtml = state.groups.map((group) => {
      const rows = group.fields.map((field) => {
        const value = displayValue(specValues[field.id]);
        const isUnknown = value === UNKNOWN || value === "Không công bố trên nguồn đã đối chiếu";
        const isNa = value === NOT_APPLICABLE;
        const className = isUnknown ? "value-unknown" : isNa ? "value-na" : "";
        const display = field.id === "official_source_url" && product.sources?.length
          ? product.sources.map((source, index) =>
            `<a class="source-link" href="${escapeHtml(source.url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(source.label || `Nguồn ${index + 1}`)}</a>`
          ).join("<br>")
          : escapeHtml(value);
        return `<tr><th scope="row">${escapeHtml(field.label)}${field.unit ? ` (${escapeHtml(field.unit)})` : ""}</th><td class="${className}">${display}</td></tr>`;
      }).join("");
      return `<section class="detail-group"><h3>${escapeHtml(group.label)}</h3><div class="spec-table-wrap"><table class="spec-table"><tbody>${rows}</tbody></table></div></section>`;
    }).join("");
    const sourceList = (product.sources || []).map((source) =>
      `<li><a class="source-link" href="${escapeHtml(source.url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(source.label)}</a>${source.accessedAt ? ` · truy cập ${escapeHtml(source.accessedAt)}` : ""}</li>`
    ).join("");
    elements.detail.innerHTML = `<div class="detail-head"><div><h2>${escapeHtml(product.name)}</h2><p>${escapeHtml(product.brand || "")} · ${escapeHtml(categoryLabel(product))} · ${escapeHtml(product.speciesLabel || product.species || "")}</p></div><button class="spec-button" type="button" data-close-detail>Đóng chi tiết</button></div>
      <div class="detail-groups">${groupsHtml}</div>
      ${product.category === "veterinary_medicine" ? '<p class="medical-warning"><strong>Thuốc thú y:</strong> thông tin nhãn không thay thế khám, chẩn đoán hoặc chỉ định của bác sĩ thú y. Không tự dùng thuốc hoặc suy diễn liều.</p>' : ""}
      <div class="data-foot"><strong>Nguồn đối chiếu</strong><ul>${sourceList || "<li>Chưa có nguồn chính thức được ghi nhận.</li>"}</ul></div>`;
    elements.detail.hidden = false;
    elements.detail.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function renderComparison() {
    const products = state.products.filter((item) => state.compared.has(item.id));
    if (products.length < 2) {
      elements.compare.hidden = true;
      elements.compare.innerHTML = "";
      return;
    }
    const heading = `<div class="detail-head"><div><h2>So sánh thông số</h2><p>Chỉ giá trị có nguồn được đối chiếu mới được xem là dữ kiện; không xếp hạng y khoa.</p></div><button class="spec-button" type="button" data-clear-compare>Xóa so sánh</button></div>`;
    const rows = state.groups.flatMap((group) => group.fields.map((field) => ({
      group: group.label, field, values: products.map((product) => displayValue((product.specs || {})[field.id]))
    })));
    const html = `${heading}<div class="spec-table-wrap"><table class="spec-table"><thead><tr><th>Thông số</th>${products.map((product) => `<th>${escapeHtml(product.name)}</th>`).join("")}</tr></thead><tbody>${rows.map((row) => `<tr><th scope="row">${escapeHtml(row.group)} · ${escapeHtml(row.field.label)}</th>${row.values.map((value) => `<td class="${value === UNKNOWN ? "value-unknown" : ""}">${escapeHtml(value)}</td>`).join("")}</tr>`).join("")}</tbody></table></div>`;
    elements.compare.innerHTML = html;
    elements.compare.hidden = false;
  }

  function renderFilters() {
    const setOptions = (select, values, label) => {
      select.replaceChildren(new Option(`Tất cả ${label}`, ""));
      for (const [value, text] of values) select.add(new Option(text, value));
    };
    setOptions(elements.species, [
      ["DOG", "Chó"], ["CAT", "Mèo"]
    ], "loài");
    setOptions(elements.category, [
      ["complete_food", "Thức ăn hoàn chỉnh"],
      ["supplement", "Thực phẩm bổ sung"],
      ["care_product", "Sản phẩm chăm sóc"],
      ["veterinary_medicine", "Thuốc thú y"]
    ], "nhóm sản phẩm");
    setOptions(elements.lifeStage, [
      ["kitten", "Mèo con"], ["puppy", "Chó con"], ["adult", "Trưởng thành"],
      ["senior", "Cao tuổi"], ["all_life_stages", "Mọi giai đoạn"]
    ], "giai đoạn sống");
  }

  async function initialize() {
    try {
      const [catalogResponse, schemaResponse] = await Promise.all([
        fetch(DATA_URL, { cache: "no-store" }),
        fetch(SCHEMA_URL, { cache: "no-store" })
      ]);
      if (!catalogResponse.ok || !schemaResponse.ok) {
        throw new Error(`Không tải được catalog/chuẩn thông số (HTTP ${catalogResponse.status}/${schemaResponse.status}).`);
      }
      const [catalog, schema] = await Promise.all([catalogResponse.json(), schemaResponse.json()]);
      const groups = schema.groups;
      const fieldCount = groups.reduce((total, group) => total + group.fields.length, 0);
      if (!Array.isArray(catalog.products) || !Array.isArray(groups) || fieldCount !== 70) {
        throw new Error("Cấu trúc catalog không hợp lệ: yêu cầu danh sách sản phẩm và đúng 70 trường thông số.");
      }
      state.products = catalog.products;
      state.groups = groups;
      renderFilters();
      renderCards();
      elements.verifiedCount.textContent = String(state.products.filter((product) => (product.sources || []).some((source) => source.type === "manufacturer_product_page")).length);
      elements.fieldCount.textContent = String(fieldCount);
      elements.status.textContent = `Nguồn: ${catalog.sourcePolicy === "official_sources_only" ? "nhãn/tài liệu chính thức" : "đang rà soát"} · Thị trường: Việt Nam`;
    } catch (error) {
      elements.results.innerHTML = `<div class="spec-error">${escapeHtml(error.message)}</div>`;
      elements.status.textContent = "Không thể tải dữ liệu thông số.";
    }
  }

  for (const filter of [elements.search, elements.species, elements.category, elements.lifeStage]) {
    filter.addEventListener("input", renderCards);
    filter.addEventListener("change", renderCards);
  }
  elements.results.addEventListener("click", (event) => {
    const openButton = event.target.closest("[data-open]");
    if (openButton) renderDetail(openButton.dataset.open);
    const compareButton = event.target.closest("[data-compare]");
    if (compareButton) {
      const id = compareButton.dataset.compare;
      if (state.compared.has(id)) state.compared.delete(id);
      else if (state.compared.size < 3) state.compared.add(id);
      else {
        compareButton.textContent = "Tối đa 3 sản phẩm";
        return;
      }
      renderCards();
      renderComparison();
    }
  });
  elements.detail.addEventListener("click", (event) => {
    if (event.target.closest("[data-close-detail]")) elements.detail.hidden = true;
  });
  elements.compare.addEventListener("click", (event) => {
    if (event.target.closest("[data-clear-compare]")) {
      state.compared.clear();
      renderCards();
      renderComparison();
    }
  });
  initialize();
})();
