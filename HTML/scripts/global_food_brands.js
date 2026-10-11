(() => {
  "use strict";

  const DATA_URL = "../data/pet_food_brands_global.json";
  const PRODUCT_DATA_URL = "../data/pet_product_specs.json";
  const elements = {
    search: document.querySelector("#brandSearch"),
    country: document.querySelector("#countryFilter"),
    results: document.querySelector("#brandResults"),
    count: document.querySelector("#brandResultCount"),
    status: document.querySelector("#brandStatus"),
    brandCount: document.querySelector("#brandCount"),
    sectionCount: document.querySelector("#sectionCount")
  };
  let sections = [];
  let productReferences = [];

  const escapeHtml = (value) => String(value ?? "").replace(/[&<>"']/g, (character) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  })[character]);

  function render() {
    const query = elements.search.value.trim().toLocaleLowerCase("vi");
    const selectedSection = elements.country.value;
    let visibleBrands = 0;
    let visibleSections = 0;
    const groups = sections.map((section) => {
      const entries = section.entries.filter((entry) => {
        const text = [entry.name, ...(entry.lines || []), entry.note || ""]
          .join(" ").toLocaleLowerCase("vi");
        return (!query || text.includes(query))
          && (!selectedSection || section.id === selectedSection);
      });
      if (!entries.length) return "";
      visibleSections += 1;
      visibleBrands += entries.length;
      const cards = entries.map((entry) => `<article class="brand-card">
        <h3>${escapeHtml(entry.name)}</h3>
        ${entry.lines?.length ? `<p class="brand-lines">Dòng được nêu: ${entry.lines.map(escapeHtml).join(" · ")}</p>` : ""}
        ${entry.note ? `<p class="brand-entry-note">${escapeHtml(entry.note)}</p>` : ""}
        <span class="brand-card-label">Chưa xác minh độc lập</span>
        <div class="brand-card-links">
          <a class="spec-button primary" href="index.html?brand=${encodeURIComponent([entry.name, ...(entry.lines || [])].join("|"))}">Sản phẩm trong hệ thống</a>
          ${productReferences.flatMap((product) => {
            const terms = [entry.name, ...(entry.lines || [])]
              .map((term) => term.toLocaleLowerCase("vi"));
            const productTerms = [product.brand, product.productLine, product.name]
              .filter(Boolean).map((term) => term.toLocaleLowerCase("vi"));
            const matches = terms.some((term) =>
              productTerms.some((productTerm) => productTerm.includes(term) || term.includes(productTerm))
            );
            if (!matches) return [];
            return (product.sources || []).map((source) =>
              `<a class="brand-product-link" href="${escapeHtml(source.url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(product.name)} · nguồn hãng ↗</a>`
            );
          }).join("")}
        </div>
      </article>`).join("");
      const kind = section.type === "market"
        ? "Thị trường được nêu · không khẳng định xuất xứ"
        : "Quốc gia/vùng theo danh sách đầu vào · cần xác minh";
      return `<section class="brand-country" aria-label="${escapeHtml(section.name)}">
        <header class="brand-country-head">
          <h3 class="brand-country-title"><span class="brand-flag" aria-hidden="true">${escapeHtml(section.flag)}</span>${escapeHtml(section.name)}</h3>
          <span class="brand-country-kind">${kind} · ${entries.length} mục</span>
        </header>
        <div class="brand-grid">${cards}</div>
      </section>`;
    }).join("");
    elements.results.innerHTML = groups || '<div class="brand-empty">Không tìm thấy mục phù hợp. Thử tên thương hiệu khác hoặc chọn “Tất cả”.</div>';
    elements.count.textContent = `${visibleBrands} mục · ${visibleSections} nhóm`;
  }

  async function initialize() {
    try {
      const [response, productsResponse] = await Promise.all([
        fetch(DATA_URL, { cache: "no-store" }),
        fetch(PRODUCT_DATA_URL, { cache: "no-store" })
      ]);
      if (!response.ok || !productsResponse.ok) {
        throw new Error(`Không tải được danh mục thương hiệu/sản phẩm (HTTP ${response.status}/${productsResponse.status}).`);
      }
      const [catalog, productCatalog] = await Promise.all([
        response.json(), productsResponse.json()
      ]);
      if (!Array.isArray(catalog.sections) || catalog.sourcePolicy !== "user_supplied_unverified"
        || !Array.isArray(productCatalog.products)) {
        throw new Error("Cấu trúc danh mục thương hiệu không hợp lệ.");
      }
      sections = catalog.sections;
      productReferences = productCatalog.products;
      const total = sections.reduce((sum, section) => sum + section.entries.length, 0);
      elements.country.replaceChildren(new Option("Tất cả quốc gia/thị trường", ""));
      for (const section of sections) elements.country.add(new Option(section.name, section.id));
      elements.brandCount.textContent = String(total);
      elements.sectionCount.textContent = String(sections.length);
      elements.status.textContent = "Danh sách theo đầu vào người dùng; thông tin nguồn gốc và sở hữu chưa được xác minh.";
      render();
    } catch (error) {
      elements.results.innerHTML = `<div class="spec-error">${escapeHtml(error.message)}</div>`;
      elements.status.textContent = "Không thể tải danh mục thương hiệu.";
    }
  }

  elements.search.addEventListener("input", render);
  elements.country.addEventListener("change", render);
  initialize();
})();
