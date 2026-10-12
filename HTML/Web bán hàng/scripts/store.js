(() => {
  "use strict";

  const CART_KEY = "bong-bong-store-cart-v1";
  const ORDER_PREFIX = "bong-bong-store-order-v1:";
  const PRODUCT_PAGE_SIZE = 48;
  const money = new Intl.NumberFormat("vi-VN", {
    style: "currency",
    currency: "VND",
    maximumFractionDigits: 0,
  });
  const categories = [
    ["Thức ăn chó mèo", "thuc-an-thu-cung.html", "🥣", "Công thức theo loài và giai đoạn sống"],
    ["Dụng cụ & thiết bị", "phu-kien-thiet-bi.html", "🧺", "Vận chuyển, ăn uống, vệ sinh, chăm sóc"],
  ];
  const navItems = [
    ["Trang chủ", "index.html"],
    ["Tất cả sản phẩm", "san-pham.html"],
    ["Thức ăn", "thuc-an-thu-cung.html"],
    ["Phụ kiện & thiết bị", "phu-kien-thiet-bi.html"],
  ];
  let products = [];
  let visibleLimit = PRODUCT_PAGE_SIZE;
  let toastTimer;

  const escapeHtml = (value) => String(value ?? "").replace(/[&<>"']/g, (character) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  })[character]);

  function showToast(message) {
    const toast = document.getElementById("store-toast");
    if (!toast) return;
    toast.textContent = message;
    toast.hidden = false;
    window.clearTimeout(toastTimer);
    toastTimer = window.setTimeout(() => { toast.hidden = true; }, 3200);
  }

  function getCart() {
    const raw = localStorage.getItem(CART_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed) || parsed.some((item) =>
      !item || typeof item.id !== "string" || !Number.isInteger(item.quantity) || item.quantity < 1
    )) throw new Error("Dữ liệu giỏ hàng lưu trên trình duyệt không hợp lệ.");
    return parsed;
  }

  function saveCart(cart) {
    localStorage.setItem(CART_KEY, JSON.stringify(cart));
    updateCartCount();
  }

  function updateCartCount() {
    const count = getCart().reduce((sum, item) => sum + item.quantity, 0);
    document.querySelectorAll("[data-cart-count]").forEach((node) => { node.textContent = String(count); });
  }

  function formatPrice(product) {
    if (product.price == null) return '<span class="price-contact">Liên hệ xác nhận giá</span>';
    const priceLabel = "Giá niêm yết · đã gồm VAT 10%";
    const memberPrice = product.memberPrice == null ? "" : `<small>Giá hội viên: ${money.format(product.memberPrice)}</small>`;
    const promotion = product.promotionPercent > 0 ? `<small>Giảm ${product.promotionPercent}% · giá gốc ${money.format(product.regularPrice)}</small>` : "";
    return `${money.format(product.price)}<small>${priceLabel}</small>${promotion}${memberPrice}`;
  }

  function productIcon(product) {
    const text = `${product.category || ""} ${product.name || ""}`.toLocaleLowerCase("vi");
    if (product.type === "food") return product.target_species.toLocaleLowerCase("vi").includes("mèo") ? "🐈" : "🐕";
    if (product.type === "combo") return "🎁";
    if (text.includes("vận chuyển") || text.includes("túi")) return "🧳";
    if (text.includes("bát") || text.includes("khay")) return "🥣";
    if (text.includes("lược") || text.includes("sữa tắm")) return "🧼";
    if (text.includes("vòng cổ") || text.includes("dây")) return "🦮";
    if (text.includes("vệ sinh") || text.includes("cát")) return "🧹";
    if (text.includes("thảm") || text.includes("ổ nằm")) return "🛏️";
    if (text.includes("đồ chơi") || text.includes("bóng")) return "🎾";
    if (text.includes("áo")) return "🧥";
    if (text.includes("cá") || text.includes("bò sát")) return "🐠";
    return "🐾";
  }

  function renderHeader() {
    const host = document.getElementById("store-header");
    if (!host) return;
    host.innerHTML = `
      <div class="container header-inner">
        <a class="brand" href="index.html" aria-label="Bông Bông Pet Care - trang chủ">
          <span class="brand-mark" aria-hidden="true">B</span>
          <span class="brand-copy">BÔNG BÔNG<small>PET CARE · CỬA HÀNG</small></span>
        </a>
        <button class="menu-toggle" type="button" aria-expanded="false" aria-controls="store-nav">Menu</button>
        <nav class="main-nav" id="store-nav" aria-label="Điều hướng cửa hàng">
          ${navItems.map(([label, href]) => `<a href="${href}"${location.pathname.endsWith(href) ? ' aria-current="page"' : ""}>${label}</a>`).join("")}
        </nav>
        <a class="cart-link" href="gio-hang.html" aria-label="Giỏ hàng">
          <span aria-hidden="true">Giỏ hàng</span><span class="cart-count" data-cart-count>0</span>
        </a>
      </div>
      <div class="demo-banner" id="store-sync-status" role="status" aria-live="polite">Đang đồng bộ catalog sản phẩm…</div>`;
    const toggle = host.querySelector(".menu-toggle");
    const nav = host.querySelector(".main-nav");
    toggle.addEventListener("click", () => {
      const open = nav.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", String(open));
    });
  }

  function formatSpecies(value) {
    const labels = {
      DOG: "Chó", CAT: "Mèo", RABBIT: "Thỏ", HAMSTER: "Hamster",
      BIRD: "Chim", FISH: "Cá", REPTILE: "Bò sát",
    };
    return String(value || "").split(",").map((part) => {
      const code = part.trim().toUpperCase();
      return labels[code] || part.trim();
    }).filter(Boolean).join(", ") || "Theo thông tin sản phẩm";
  }

  function formatLifeStage(value) {
    const stage = String(value || "").trim();
    const labels = {
      YOUNG: "Tăng trưởng",
      PUPPY: "Chó con",
      KITTEN: "Mèo con",
      ADULT: "Trưởng thành",
      SENIOR: "Lớn tuổi",
    };
    return labels[stage.toUpperCase()] || stage || "Theo nhãn sản phẩm";
  }

  function matchesSpecies(product, filter) {
    if (!filter) return true;
    const species = `${product.target_species || ""} ${product.species || ""}`.toLocaleLowerCase("vi");
    const accepted = {
      DOG: ["dog", "chó"],
      CAT: ["cat", "mèo"],
      "Chó, Mèo": ["chó", "mèo", "dog", "cat"],
      Cá: ["cá", "fish"],
      "Bò sát": ["bò sát", "reptile"],
      "Hamster, Thỏ": ["hamster", "thỏ", "rabbit"],
    }[filter] || [filter.toLocaleLowerCase("vi")];
    return accepted.some((value) => species.includes(value));
  }

  function normalizeProduct(item, type) {
    const isFood = item.category === "FOOD";
    const category = type === "combo"
      ? "Combo"
      : item.catalog_category || item.food_category || item.category || "Sản phẩm";
    const demo = Boolean(item.is_demo);
    const ownerConfirmedOfficial = String(item.item_code || "").startsWith("DEMO-BREED-");
    const usable = Number(item.usable_quantity || 0);
    const promotion = Number(item.promotion_percent || 0);
    const retailPrice = Number(item.retail_price || 0);
    const product = {
      ...item,
      id: item.id || item.item_code || item.combo_code,
      type: type || (isFood ? "food" : item.category === "MEDICINE" ? "medicine" : "accessory"),
      category,
      target_species: item.target_species || "",
      speciesLabel: formatSpecies(item.target_species || ""),
      stage: formatLifeStage(item.life_stage || item.age_group),
      price: retailPrice > 0 ? retailPrice * (1 - promotion / 100) : null,
      regularPrice: retailPrice,
      memberPrice: item.member_price == null ? null : Number(item.member_price),
      promotionPercent: promotion,
      stockQuantity: Number(item.stock_quantity || 0),
      usableQuantity: usable,
      components: item.components || [],
      summary: item.description || item.purpose || "Thông tin từ catalog SQLite PetCare.",
      ownerConfirmedOfficial,
      status: ownerConfirmedOfficial
        ? "Catalog chính thức theo xác nhận quản trị viên · chi tiết cần đối chiếu"
        : "Catalog cửa hàng",
      brand: item.brand || "",
    };
    return product;
  }

  function validateCatalog(catalog) {
    if (!catalog || !Array.isArray(catalog.products) || !Array.isArray(catalog.combos)) {
      throw new Error("Cấu trúc catalog SQLite không hợp lệ.");
    }
    return catalog;
  }

  async function loadProducts() {
    let catalog;
    let liveError;
    try {
      const response = await fetch("/api/storefront/catalog", { cache: "no-store" });
      if (!response.ok) throw new Error(`Bridge trả về HTTP ${response.status}.`);
      catalog = validateCatalog(await response.json());
    } catch (error) {
      liveError = error;
      const snapshotResponse = await fetch("data/store_catalog.json", { cache: "no-store" });
      if (!snapshotResponse.ok) {
        throw new Error(`Không tải được dữ liệu SQLite (${error.message}) hoặc snapshot (${snapshotResponse.status}).`);
      }
      catalog = validateCatalog(await snapshotResponse.json());
      catalog.sourceType = "sqlite_snapshot";
      catalog.liveSyncError = error.message;
    }

    products = [
      ...catalog.products.map((item) => normalizeProduct(item)),
      ...catalog.combos.map((item) => normalizeProduct(item, "combo")),
    ];
    const status = document.getElementById("store-sync-status");
    if (status) {
      const sourceLabel = catalog.sourceType === "live_sqlite"
        ? "Đang đồng bộ trực tiếp từ SQLite ứng dụng"
        : `Đang xem snapshot ${escapeHtml(catalog.generatedAt || "chưa rõ thời điểm")}`;
      const problem = catalog.dataStatus === "demo_only"
        ? "Dữ liệu catalog có trạng thái demo hoặc cần xác minh; hãy xem trạng thái riêng của từng hồ sơ trước khi sử dụng."
        : "Hãy kiểm tra trạng thái giá và tồn kho trong chi tiết hàng hóa.";
      const ownerConfirmedCount = products.filter((product) => product.ownerConfirmedOfficial).length;
      const ownerConfirmedNotice = ownerConfirmedCount
        ? ` ${ownerConfirmedCount} hồ sơ giống được quản trị viên xác nhận là catalog chính thức; trường chưa có nhãn/tài liệu đối chiếu vẫn được ghi rõ.`
        : "";
      const fallback = catalog.liveSyncError
        ? ` Live API chưa kết nối (${escapeHtml(catalog.liveSyncError)}).`
        : "";
      status.innerHTML = `<strong>${sourceLabel} · ${products.length} mặt hàng/combo.</strong> ${problem}${ownerConfirmedNotice}${fallback}`;
    }
    return { catalog, liveError };
  }

  function productCard(product) {
    const href = `chi-tiet-san-pham.html?id=${encodeURIComponent(product.id)}`;
    const stockLabel = product.usableQuantity > 0
      ? `Còn ${product.usableQuantity} ${product.unit || "đơn vị"}`
      : "Chưa có tồn khả dụng";
    const buttonLabel = product.usableQuantity > 0 ? "Thêm vào giỏ" : "Yêu cầu xác nhận";
    return `<article class="product-card fade-in">
      <a class="product-art" href="${href}" aria-label="Xem ${escapeHtml(product.name)}"><span class="art-icon" aria-hidden="true">${productIcon(product)}</span></a>
      <div class="product-info">
        <span class="product-tag">${escapeHtml(product.category)}</span>
        <small class="product-status">${escapeHtml(product.status)}</small>
        <h3><a href="${href}">${escapeHtml(product.name)}</a></h3>
        <div class="product-meta">${escapeHtml(product.speciesLabel)} · ${escapeHtml(product.stage)} · ${escapeHtml(stockLabel)}</div>
        <div class="product-price">${formatPrice(product)}</div>
        <div class="product-actions"><button class="button" type="button" data-add="${escapeHtml(product.id)}">${buttonLabel}</button><a class="button-secondary" href="${href}" aria-label="Chi tiết ${escapeHtml(product.name)}">Chi tiết</a></div>
      </div>
    </article>`;
  }

  function renderProductList() {
    const root = document.querySelector("[data-product-grid]");
    if (!root) return;
    const mode = document.body.dataset.catalog || "all";
    const query = document.getElementById("catalog-search")?.value.trim().toLocaleLowerCase("vi") || "";
    const category = document.getElementById("catalog-category")?.value || "";
    const species = document.getElementById("catalog-species")?.value || "";
    const featuredIds = new Set(products.slice(0, 8).map((product) => product.id));
    const visible = products.filter((product) => {
      const isFood = product.type === "food";
      const contextMatch = mode === "all"
        || (mode === "food" && isFood)
        || (mode === "accessory" && !isFood)
        || (mode === "featured" && (isFood || featuredIds.has(product.id)));
      const queryMatch = `${product.name} ${product.brand} ${product.category} ${product.speciesLabel} ${product.summary} ${product.item_code || ""}`.toLocaleLowerCase("vi").includes(query);
      return contextMatch && queryMatch && (!category || product.category === category) && matchesSpecies(product, species);
    });
    const featured = mode === "featured" ? visible.slice(0, 8) : visible.slice(0, visibleLimit);
    const moreButton = mode !== "featured" && visible.length > visibleLimit
      ? `<button class="button" type="button" data-load-more>Xem thêm ${Math.min(PRODUCT_PAGE_SIZE, visible.length - visibleLimit)} sản phẩm</button>`
      : "";
    root.innerHTML = (featured.map(productCard).join("") || '<div class="empty-state">Không tìm thấy sản phẩm phù hợp với bộ lọc.</div>') + moreButton;
    const count = document.querySelector("[data-product-count]");
    if (count) {
      count.textContent = mode === "featured"
        ? `Đang xem ${visible.length} sản phẩm`
        : `Đang xem ${Math.min(visible.length, visibleLimit)} trên ${visible.length} sản phẩm`;
    }
  }

  function renderCategories() {
    const root = document.querySelector("[data-category-grid]");
    if (root) root.innerHTML = categories.map(([label, href, icon, description]) =>
      `<a class="category-tile" href="${href}"><span class="category-icon" aria-hidden="true">${icon}</span><strong>${label}</strong><small>${description}</small></a>`
    ).join("");
  }

  function addProduct(id) {
    const product = products.find((item) => item.id === id);
    if (!product) throw new Error("Không tìm thấy sản phẩm trong catalog.");
    const cart = getCart();
    const entry = cart.find((item) => item.id === id);
    if (entry) entry.quantity += 1;
    else cart.push({ id, quantity: 1 });
    saveCart(cart);
    showToast("Đã thêm vào giỏ yêu cầu. Giá và tồn kho sẽ cần cửa hàng xác nhận.");
  }

  function bindAddButtons() {
    document.addEventListener("click", (event) => {
      if (event.target.closest("[data-load-more]")) {
        visibleLimit += PRODUCT_PAGE_SIZE;
        renderProductList();
        return;
      }
      const button = event.target.closest("[data-add]");
      if (!button) return;
      try { addProduct(button.dataset.add); } catch (error) { showToast(error.message); }
    });
  }

  function populateFilters() {
    const categorySelect = document.getElementById("catalog-category");
    if (categorySelect) {
      const mode = document.body.dataset.catalog || "all";
      const visibleProducts = products.filter((product) =>
        mode === "food" ? product.type === "food" : mode === "accessory" ? product.type !== "food" : true
      );
      const options = [...new Set(visibleProducts.map((product) => product.category))].sort((a, b) => a.localeCompare(b, "vi"));
      categorySelect.innerHTML = '<option value="">Mọi nhóm hàng</option>' + options
        .map((option) => `<option value="${escapeHtml(option)}">${escapeHtml(option)}</option>`).join("");
    }
  }

  function renderCart() {
    const root = document.querySelector("[data-cart-list]");
    if (!root) return;
    const cart = getCart();
    const items = cart.map((entry) => ({
      ...entry,
      product: products.find((product) => product.id === entry.id),
    })).filter((entry) => entry.product);
    if (items.length !== cart.length) saveCart(items.map(({ id, quantity }) => ({ id, quantity })));
    root.innerHTML = items.length ? items.map(({ id, quantity, product }) => `
      <article class="cart-row">
        <div><h3><a href="chi-tiet-san-pham.html?id=${encodeURIComponent(id)}">${escapeHtml(product.name)}</a></h3><p>${escapeHtml(product.category)} · ${escapeHtml(product.status)}</p></div>
        <strong>${product.price == null ? "Liên hệ" : money.format(product.price * quantity)}</strong>
        <label class="quantity-control">SL <input type="number" min="1" max="99" value="${quantity}" data-quantity="${escapeHtml(id)}" aria-label="Số lượng ${escapeHtml(product.name)}"></label>
        <button class="remove-button" type="button" data-remove="${escapeHtml(id)}">Gỡ</button>
      </article>`).join("") : '<div class="empty-state">Giỏ hàng đang trống. Hãy chọn sản phẩm để tạo yêu cầu báo giá.</div>';
    const priced = items.filter(({ product }) => product.price != null);
    const total = priced.reduce((sum, item) => sum + item.product.price * item.quantity, 0);
    const hasUnpriced = items.some(({ product }) => product.price == null);
    const totalNode = document.querySelector("[data-cart-total]");
    if (totalNode) totalNode.textContent = hasUnpriced ? `${money.format(total)} + sản phẩm cần xác nhận giá` : money.format(total);
    const itemCount = document.querySelector("[data-cart-items]");
    if (itemCount) itemCount.textContent = String(items.reduce((sum, item) => sum + item.quantity, 0));
    document.querySelectorAll("[data-remove]").forEach((button) => button.addEventListener("click", () => {
      saveCart(getCart().filter((item) => item.id !== button.dataset.remove));
      renderCart();
    }));
    document.querySelectorAll("[data-quantity]").forEach((input) => input.addEventListener("change", () => {
      const quantity = Number(input.value);
      if (!Number.isInteger(quantity) || quantity < 1 || quantity > 99) {
        showToast("Số lượng phải là số nguyên từ 1 đến 99.");
        renderCart();
        return;
      }
      const updated = getCart().map((item) => item.id === input.dataset.quantity ? { ...item, quantity } : item);
      saveCart(updated);
      renderCart();
    }));
    const checkout = document.querySelector("[data-checkout-link]");
    if (checkout) checkout.hidden = items.length === 0;
  }

  function detailValue(product, key) {
    const value = product[key];
    if (value == null || value === "") return "Chưa được cung cấp trong catalog";
    if (key === "target_species") return formatSpecies(value);
    if (key === "age_unit") {
      return { MONTH: "Tháng", YEAR: "Năm", LABEL: "Theo nhãn" }[value] || String(value);
    }
    if (key === "life_stage") {
      return {
        YOUNG: "Tăng trưởng",
        ADULT: "Trưởng thành",
        SENIOR: "Lớn tuổi",
      }[value] || String(value);
    }
    if (key === "stock_status") {
      return value === "in_stock" ? "Còn tồn khả dụng" : "Chưa có tồn khả dụng";
    }
    if (key === "is_active" || key === "is_demo") return value ? "Có" : "Không";
    if (key === "retail_price" || key === "member_price") {
      return Number(value) > 0 ? money.format(Number(value)) : "Chưa có giá được xác minh";
    }
    if (key === "promotion_percent") return `${value}%`;
    if (key === "usable_quantity" || key === "stock_quantity") {
      const unit = product.unit && product.unit.toLocaleLowerCase("vi") !== "mẫu demo"
        ? ` ${product.unit}`
        : "";
      return `${value}${unit}`;
    }
    if (key === "components") {
      return Array.isArray(value) && value.length
        ? value.map((component) =>
          `${component.name} · ${component.quantity} ${component.unit || ""}`.trim()
        ).join("; ")
        : "Chưa cấu hình SKU thành phần";
    }
    return String(value);
  }

  function detailSection(title, fields, product) {
    const rows = fields.map(([key, label]) =>
      `<li><small>${escapeHtml(label)}</small><span>${escapeHtml(detailValue(product, key))}</span></li>`
    );
    return `<section class="panel product-detail-panel"><h2>${escapeHtml(title)}</h2><ul class="detail-list">${rows.join("")}</ul></section>`;
  }

  function renderDetail() {
    const root = document.querySelector("[data-product-detail]");
    if (!root) return;
    const id = new URLSearchParams(location.search).get("id");
    const product = products.find((item) => item.id === id);
    if (!product) {
      root.innerHTML = '<div class="empty-state"><h2>Không tìm thấy sản phẩm</h2><p>Liên kết sản phẩm không hợp lệ hoặc mặt hàng không còn trong dữ liệu trang.</p><a class="button" href="san-pham.html">Quay lại danh mục</a></div>';
      return;
    }
    const identityFields = [
      ["item_code", "Mã sản phẩm"],
      ["catalog_category", "Danh mục catalog"],
      ["target_species", "Loài ghi trên catalog"],
      ["animal_subspecies", "Giống được gắn trong catalog"],
      ["age_group", "Nhóm tuổi"],
      ["life_stage", "Giai đoạn sống"],
      ["unit", "Đơn vị"],
      ["pack_size", "Quy cách đóng gói"],
      ["brand", "Thương hiệu"],
      ["barcode", "Mã vạch"],
    ];
    const nutritionFields = [
      ["food_category", "Nhóm thức ăn"],
      ["food_type", "Dạng thức ăn"],
      ["food_subtype", "Phân loại"],
      ["ingredients", "Thành phần ghi trong catalog"],
      ["protein_source", "Nguồn protein ghi trong catalog"],
      ["nutrition_type", "Loại dinh dưỡng"],
      ["diet_type", "Chế độ ăn"],
      ["age_min_months", "Tuổi tối thiểu (tháng)"],
      ["age_max_months", "Tuổi tối đa (tháng)"],
      ["age_unit", "Cách ghi đơn vị tuổi"],
      ["suitable_weight_min", "Cân nặng tối thiểu (kg)"],
      ["suitable_weight_max", "Cân nặng tối đa (kg)"],
      ["vitamin_c_content", "Vitamin C ghi trong catalog"],
      ["water_level", "Độ ẩm ghi trong catalog"],
      ["feeding_frequency", "Tần suất ghi trong catalog"],
      ["feeding_time", "Thời điểm ghi trong catalog"],
      ["serving_size", "Khẩu phần ghi trong catalog"],
      ["purpose", "Mục đích ghi trong catalog"],
    ];
    const commerceFields = [
      ["retail_price", "Giá bán"],
      ["member_price", "Giá hội viên"],
      ["promotion_percent", "Khuyến mãi"],
      ["promotion_note", "Điều kiện khuyến mãi"],
      ["stock_quantity", "Số lượng trong lô"],
      ["usable_quantity", "Số lượng còn khả dụng"],
      ["stock_status", "Trạng thái tồn"],
    ];
    const comboFields = [["components", "SKU thành phần"]];
    const facts = [
      ["Loài", product.speciesLabel],
      ["Nhóm tuổi / giai đoạn", product.stage],
      ["Mã hàng", product.id],
      ["Tồn khả dụng", detailValue(product, "usable_quantity")],
    ];
    const productDetails = detailSection("Thông tin sản phẩm", identityFields, product);
    const nutritionDetails = product.type === "food"
      ? detailSection("Thành phần, dinh dưỡng và hướng dẫn", nutritionFields, product)
      : "";
    const commerceDetails = detailSection("Giá và tình trạng tồn kho", commerceFields, product);
    const comboDetails = product.type === "combo"
      ? detailSection("Thành phần combo", comboFields, product)
      : "";
    root.innerHTML = `<div class="product-detail fade-in">
      <div class="product-art"><span class="art-icon" aria-hidden="true">${productIcon(product)}</span></div>
      <div class="detail-copy">
        <span class="product-tag">${escapeHtml(product.category)}</span>
        <h1>${escapeHtml(product.name)}</h1>
        <p class="page-lead">${escapeHtml(product.summary)}</p>
        <div class="product-price">${formatPrice(product)}</div>
        <p class="notice">${escapeHtml(product.status)}. Nội dung dưới đây phản ánh các trường đã lưu trong catalog, không thay thế nhãn sản phẩm. Trường chưa có dữ liệu được ghi rõ${product.ownerConfirmedOfficial ? "; các chi tiết SKU cần đối chiếu với nhãn/tài liệu gốc" : "; dữ liệu demo cần được cửa hàng xác minh trước khi sử dụng"}.</p>
        <ul class="detail-list">${facts.map(([label, value]) => `<li><small>${escapeHtml(label)}</small>${escapeHtml(value || "Chưa có dữ liệu")}</li>`).join("")}</ul>
        ${productDetails}
        ${nutritionDetails}
        ${commerceDetails}
        ${comboDetails}
        <button class="button" type="button" data-add="${escapeHtml(product.id)}">Thêm vào giỏ yêu cầu</button>
      </div>
    </div>`;
  }

  function renderCheckout() {
    const root = document.querySelector("[data-checkout-summary]");
    if (!root) return;
    const items = getCart().map((entry) => ({
      ...entry,
      product: products.find((product) => product.id === entry.id),
    })).filter((entry) => entry.product);
    if (!items.length) {
      root.innerHTML = '<div class="empty-state">Giỏ hàng trống. <a class="text-link" href="san-pham.html">Quay lại chọn sản phẩm</a></div>';
      const form = document.querySelector("[data-checkout-form]");
      if (form) form.hidden = true;
      return;
    }
    const hasUnpriced = items.some(({ product }) => product.price == null);
    const total = items.reduce((sum, item) => sum + (item.product.price || 0) * item.quantity, 0);
    root.innerHTML = `<h2>Tóm tắt yêu cầu</h2>
      ${items.map(({ product, quantity }) => `<div class="summary-line"><span>${escapeHtml(product.name)} × ${quantity}</span><strong>${product.price == null ? "Xác nhận giá" : money.format(product.price * quantity)}</strong></div>`).join("")}
      <div class="summary-line total"><span>Tạm tính mẫu</span><strong>${hasUnpriced ? `${money.format(total)} + xác nhận giá` : money.format(total)}</strong></div>
      <p class="checkout-disclaimer">Số tiền trên là giá demo nếu có; chưa bao gồm phí giao hàng và không phải số tiền thanh toán.</p>`;
  }

  function bindCheckout() {
    const form = document.querySelector("[data-checkout-form]");
    if (!form) return;
    form.addEventListener("submit", (event) => {
      event.preventDefault();
      const cart = getCart();
      if (!cart.length) { showToast("Giỏ hàng đang trống."); return; }
      const data = new FormData(form);
      const orderCode = `BB-${new Date().toISOString().slice(0, 10).replaceAll("-", "")}-${Math.random().toString(36).slice(2, 7).toUpperCase()}`;
      const request = {
        code: orderCode,
        createdAt: new Date().toISOString(),
        customer: {
          name: String(data.get("name") || "").trim(),
          phone: String(data.get("phone") || "").trim(),
          address: String(data.get("address") || "").trim(),
          note: String(data.get("note") || "").trim(),
        },
        items: cart,
        status: "local_request_only",
      };
      if (!request.customer.name || !request.customer.phone) {
        showToast("Vui lòng nhập họ tên và số điện thoại.");
        return;
      }
      localStorage.setItem(`${ORDER_PREFIX}${orderCode}`, JSON.stringify(request));
      localStorage.setItem("bong-bong-store-last-order-v1", orderCode);
      localStorage.removeItem(CART_KEY);
      location.href = `dat-hang-thanh-cong.html?code=${encodeURIComponent(orderCode)}`;
    });
  }

  function renderConfirmation() {
    const root = document.querySelector("[data-order-confirmation]");
    if (!root) return;
    const code = new URLSearchParams(location.search).get("code")
      || localStorage.getItem("bong-bong-store-last-order-v1");
    if (!code) {
      root.innerHTML = '<div class="empty-state"><h1>Chưa có yêu cầu đặt hàng</h1><p>Hãy chọn sản phẩm và gửi yêu cầu báo giá trước.</p><a class="button" href="san-pham.html">Xem sản phẩm</a></div>';
      return;
    }
    const raw = localStorage.getItem(`${ORDER_PREFIX}${code}`);
    if (!raw) {
      root.innerHTML = '<div class="empty-state"><h1>Không tìm thấy yêu cầu</h1><p>Yêu cầu chỉ được lưu trong trình duyệt đã tạo; dữ liệu trình duyệt có thể đã bị xóa.</p><a class="button" href="index.html">Về cửa hàng</a></div>';
      return;
    }
    const order = JSON.parse(raw);
    root.innerHTML = `<div class="success-card">
      <span class="success-icon" aria-hidden="true">✓</span>
      <span class="eyebrow">Yêu cầu được lưu trên thiết bị</span>
      <h1>Đã tạo bản nháp yêu cầu</h1>
      <p>Mã tham chiếu <strong>${escapeHtml(order.code)}</strong></p>
      <p>Đây chưa phải đơn hàng gửi đến cửa hàng. Không có thanh toán hoặc thông báo nào được gửi; thông tin chỉ nằm trong bộ nhớ trình duyệt này.</p>
      <p>Người nhận: ${escapeHtml(order.customer.name)} · ${escapeHtml(order.customer.phone)}</p>
      <a class="button" href="san-pham.html">Tiếp tục xem sản phẩm</a>
    </div>`;
  }

  function bindFilters() {
    ["catalog-search", "catalog-category", "catalog-species"].forEach((id) => {
      const filter = document.getElementById(id);
      const resetAndRender = () => {
        visibleLimit = PRODUCT_PAGE_SIZE;
        renderProductList();
      };
      filter?.addEventListener("input", resetAndRender);
      filter?.addEventListener("change", resetAndRender);
    });
  }

  async function init() {
    renderHeader();
    renderCategories();
    try {
      await loadProducts();
      populateFilters();
      updateCartCount();
      renderProductList();
      bindAddButtons();
      renderDetail();
      renderCart();
      renderCheckout();
      renderConfirmation();
      bindFilters();
      bindCheckout();
    } catch (error) {
      console.error("Storefront could not initialize.", error);
      document.querySelectorAll("[data-product-grid], [data-product-detail], [data-cart-list], [data-checkout-summary], [data-order-confirmation]")
        .forEach((node) => { node.innerHTML = `<div class="empty-state" role="alert">${escapeHtml(error.message)}</div>`; });
    }
  }

  init();
})();
