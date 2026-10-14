(() => {
  "use strict";

  const CART_KEY = "bong-bong-store-cart-v1";
  const CHECKOUT_REQUEST_KEY = "bong-bong-store-checkout-request-id-v1";
  const API_URL_KEY = "petcare.central-api-url.v1";
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
    ["Kiểm tra đơn", "dat-hang-thanh-cong.html"],
    ["Kết nối hệ thống", "index.html#api-connection"],
  ];
  let products = [];
  let visibleLimit = PRODUCT_PAGE_SIZE;
  let toastTimer;
  let catalogSourceType = "";

  const escapeHtml = (value) => String(value ?? "").replace(/[&<>"']/g, (character) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  })[character]);
  const displaySku = (value) => String(value ?? "").replace(/^DEMO-/i, "");

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

  function getApiBaseUrl() {
    const queryUrl = new URLSearchParams(location.search).get("api");
    if (queryUrl) {
      const normalized = validateApiBaseUrl(queryUrl);
      localStorage.setItem(API_URL_KEY, normalized);
      return normalized;
    }
    return localStorage.getItem(API_URL_KEY) || "";
  }

  function validateApiBaseUrl(value) {
    let url;
    try {
      url = new URL(value.trim());
    } catch {
      throw new Error("Nhập URL Central API hợp lệ, bao gồm https://.");
    }
    const localHttp = url.protocol === "http:"
      && ["localhost", "127.0.0.1", "::1"].includes(url.hostname);
    if ((!localHttp && url.protocol !== "https:") || !url.hostname
      || url.username || url.password || url.search || url.hash) {
      throw new Error("Central API phải dùng HTTPS và không chứa thông tin đăng nhập hoặc tham số URL.");
    }
    return url.origin + url.pathname.replace(/\/+$/, "");
  }

  function apiUrl(path) {
    return `${getApiBaseUrl()}${path}`;
  }

  function bindApiSettings() {
    const form = document.querySelector("[data-api-settings]");
    if (!form) return;
    const input = form.querySelector("[name='api-url']");
    const status = form.querySelector("[data-api-status]");
    const savedUrl = getApiBaseUrl();
    if (input) input.value = savedUrl;
    if (status) {
      status.textContent = savedUrl
        ? "Đã cấu hình Central API. Catalog và đơn hàng dùng chung dữ liệu với desktop/mobile."
        : "Chưa cấu hình Central API. Trang chỉ dùng bridge cục bộ hoặc snapshot catalog.";
    }
    form.addEventListener("submit", (event) => {
      event.preventDefault();
      try {
        const value = String(input?.value || "").trim();
        if (!value) {
          localStorage.removeItem(API_URL_KEY);
        } else {
          localStorage.setItem(API_URL_KEY, validateApiBaseUrl(value));
        }
        showToast(value ? "Đã lưu địa chỉ Central API." : "Đã xóa cấu hình Central API.");
        window.location.reload();
      } catch (error) {
        if (status) status.textContent = error.message;
        showToast(error.message);
      }
    });
    form.querySelector("[data-api-clear]")?.addEventListener("click", () => {
      localStorage.removeItem(API_URL_KEY);
      window.location.reload();
    });
  }

  function getCheckoutRequestId() {
    let requestId = localStorage.getItem(CHECKOUT_REQUEST_KEY);
    if (!requestId) {
      if (!window.crypto?.randomUUID) {
        throw new Error("Trình duyệt không hỗ trợ mã hóa an toàn để gửi đơn.");
      }
      requestId = window.crypto.randomUUID();
      localStorage.setItem(CHECKOUT_REQUEST_KEY, requestId);
    }
    return requestId;
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
      </div>`;
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
      popularity30d: {
        soldQuantity: Number(item.popularity_30d?.sold_quantity || 0),
        paidOrderCount: Number(item.popularity_30d?.paid_order_count || 0),
        revenue: Number(item.popularity_30d?.revenue || 0),
        requestCount: Number(item.popularity_30d?.request_count || 0),
        requestedQuantity: Number(item.popularity_30d?.requested_quantity || 0),
        score: Number(item.popularity_30d?.score || 0),
      },
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
    const centralApi = getApiBaseUrl();
    try {
      const response = await fetch(apiUrl("/api/storefront/catalog"), { cache: "no-store" });
      if (!response.ok) {
        const payload = await response.json().catch(() => ({}));
        throw new Error(payload.detail || payload.error || `Central API trả về HTTP ${response.status}.`);
      }
      catalog = validateCatalog(await response.json());
    } catch (error) {
      if (centralApi) throw error;
      liveError = error;
      const snapshotResponse = await fetch("data/store_catalog.json", { cache: "no-store" });
      if (!snapshotResponse.ok) {
        throw new Error(`Không tải được dữ liệu SQLite (${error.message}) hoặc snapshot (${snapshotResponse.status}).`);
      }
      catalog = validateCatalog(await snapshotResponse.json());
      catalog.sourceType = "sqlite_snapshot";
      catalog.liveSyncError = error.message;
    }

    catalogSourceType = catalog.sourceType || "";
    products = [
      ...catalog.products.map((item) => normalizeProduct(item)),
      ...catalog.combos.map((item) => normalizeProduct(item, "combo")),
    ];
    return { catalog, liveError };
  }

  function productCard(product, showPopularity = false) {
    const href = `chi-tiet-san-pham.html?id=${encodeURIComponent(product.id)}`;
    const stockLabel = product.usableQuantity >= 5
      ? `Còn ${product.usableQuantity} ${product.unit || "đơn vị"}`
      : "Hết hàng (còn dưới 5)";
    const canOrder = canSubmitOrder(product);
    const popularity = product.popularity30d;
    const popularityLabel = popularity.paidOrderCount > 0
      ? "Bán gần đây"
      : "Được yêu cầu";
    const soldQuantityLabel = product.type === "combo"
      ? ""
      : `${popularity.soldQuantity} đã bán · `;
    const popularityDetail = popularity.paidOrderCount > 0
      ? `${soldQuantityLabel}${popularity.paidOrderCount} đơn đã thanh toán`
      : `${popularity.requestCount} lượt yêu cầu · không tính là doanh số`;
    return `<article class="product-card fade-in">
      <a class="product-art" href="${href}" aria-label="Xem ${escapeHtml(product.name)}"><span class="art-icon" aria-hidden="true">${productIcon(product)}</span></a>
      <div class="product-info">
        <span class="product-tag">${escapeHtml(product.category)}</span>
        ${showPopularity ? `<span class="popularity-badge">${popularityLabel}</span><small class="popularity-detail">${escapeHtml(popularityDetail)}</small>` : ""}
        <small class="product-status">${escapeHtml(product.status)}</small>
        <h3><a href="${href}">${escapeHtml(product.name)}</a></h3>
        <div class="product-meta">${escapeHtml(product.speciesLabel)} · ${escapeHtml(product.stage)} · ${escapeHtml(stockLabel)}</div>
        <div class="product-price">${formatPrice(product)}</div>
        <div class="product-actions">${orderButton(product)}<a class="button-secondary" href="${href}" aria-label="Chi tiết ${escapeHtml(product.name)}">Chi tiết</a></div>
      </div>
    </article>`;
  }

  function canSubmitOrder(product) {
    return product.usableQuantity >= 5 && !product.is_demo && product.price != null;
  }

  function orderButton(product) {
    const enabled = canSubmitOrder(product);
    const label = enabled
      ? "Thêm vào giỏ yêu cầu"
      : product.usableQuantity < 5
        ? "Hết hàng (còn dưới 5)"
        : product.is_demo
          ? "Chưa xác minh"
          : "Chưa có giá";
    return `<button class="button" type="button" ${enabled ? `data-add="${escapeHtml(product.id)}"` : "disabled"}>${label}</button>`;
  }

  function comparePopularity(first, second) {
    return second.popularity30d.score - first.popularity30d.score
      || second.popularity30d.soldQuantity - first.popularity30d.soldQuantity
      || second.popularity30d.paidOrderCount - first.popularity30d.paidOrderCount
      || second.popularity30d.requestCount - first.popularity30d.requestCount
      || first.name.localeCompare(second.name, "vi");
  }

  function compareProducts(first, second, sortBy) {
    if (sortBy === "price-asc" || sortBy === "price-desc") {
      if (first.price == null && second.price != null) return 1;
      if (first.price != null && second.price == null) return -1;
      if (first.price != null && second.price != null) {
        const priceOrder = first.price - second.price;
        if (priceOrder) return sortBy === "price-asc" ? priceOrder : -priceOrder;
      }
    } else if (sortBy === "stock") {
      const stockOrder = second.usableQuantity - first.usableQuantity;
      if (stockOrder) return stockOrder;
    } else if (sortBy === "popular") {
      const popularityOrder = comparePopularity(first, second);
      if (popularityOrder) return popularityOrder;
    }
    return first.name.localeCompare(second.name, "vi");
  }

  function renderRecommendations() {
    const root = document.querySelector("[data-recommendation-grid]");
    if (!root) return;
    const ranked = products
      .filter((product) => product.popularity30d.score > 0)
      .sort(comparePopularity);
    if (!ranked.length) {
      root.innerHTML = catalogSourceType === "sqlite_snapshot"
        ? '<div class="empty-state">Snapshot tĩnh chưa có thống kê bán hàng. Mở cửa hàng từ ứng dụng PetCare để đồng bộ xu hướng giao dịch gần nhất.</div>'
        : '<div class="empty-state">Chưa có giao dịch đã thanh toán hoặc yêu cầu mua trong 30 ngày gần đây để xếp hạng. Bạn có thể khám phá các sản phẩm nổi bật bên dưới.</div>';
      return;
    }
    root.innerHTML = ranked.slice(0, 8).map((product) => productCard(product, true)).join("");
  }

  function renderProductList() {
    const root = document.querySelector("[data-product-grid]");
    if (!root) return;
    const mode = document.body.dataset.catalog || "all";
    const query = document.getElementById("catalog-search")?.value.trim().toLocaleLowerCase("vi") || "";
    const category = document.getElementById("catalog-category")?.value || "";
    const species = document.getElementById("catalog-species")?.value || "";
    const sortBy = document.getElementById("catalog-sort")?.value || "popular";
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
    const sorted = mode === "featured" ? visible : visible.sort((first, second) => compareProducts(first, second, sortBy));
    const page = mode === "featured" ? sorted.slice(0, 8) : sorted.slice(0, visibleLimit);
    const moreButton = mode !== "featured" && sorted.length > visibleLimit
      ? `<button class="button" type="button" data-load-more>Xem thêm ${Math.min(PRODUCT_PAGE_SIZE, sorted.length - visibleLimit)} sản phẩm</button>`
      : "";
    root.innerHTML = (page.map(productCard).join("") || '<div class="empty-state">Không tìm thấy sản phẩm phù hợp với bộ lọc.</div>') + moreButton;
    const sortStatus = document.querySelector("[data-sort-status]");
    if (sortStatus) {
      const hasPopularity = products.some((product) => product.popularity30d.score > 0);
      sortStatus.textContent = sortBy === "popular" && !hasPopularity
        ? "Chưa có dữ liệu bán hàng hoặc yêu cầu trong 30 ngày gần đây; danh sách xu hướng đang hiển thị theo tên."
        : "";
    }
    const count = document.querySelector("[data-product-count]");
    if (count) {
      count.textContent = mode === "featured"
        ? `Đang xem ${sorted.length} sản phẩm`
        : `Đang xem ${Math.min(sorted.length, visibleLimit)} trên ${sorted.length} sản phẩm`;
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
    if (key === "item_code" || key === "combo_code") return displaySku(value);
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
      ["Mã hàng", displaySku(product.item_code || product.combo_code || product.id)],
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
        ${orderButton(product)}
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
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const cart = getCart();
      if (!cart.length) { showToast("Giỏ hàng đang trống."); return; }
      const data = new FormData(form);
      const name = String(data.get("name") || "").trim();
      const phone = String(data.get("phone") || "").trim();
      if (!name || !phone) {
        showToast("Vui lòng nhập họ tên và số điện thoại.");
        return;
      }
      if (!data.get("consent")) {
        showToast("Vui lòng đồng ý gửi thông tin đến cửa hàng.");
        return;
      }
      const submitButton = form.querySelector('[type="submit"]');
      if (submitButton) submitButton.disabled = true;
      try {
        const response = await fetch(apiUrl("/api/storefront/order-requests"), {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-PetCare-Request": "1",
          },
          body: JSON.stringify({
            name,
            phone,
            address: String(data.get("address") || "").trim(),
            note: String(data.get("note") || "").trim(),
            consent: true,
            clientRequestId: getCheckoutRequestId(),
            items: cart,
          }),
        });
        let result;
        try {
          result = await response.json();
        } catch {
          throw new Error("Không nhận được phản hồi từ bridge ứng dụng; yêu cầu chưa được lưu.");
        }
        if (!response.ok) {
          throw new Error(result.detail || result.error || "Không thể gửi yêu cầu đến cửa hàng.");
        }
        if (!result.requestCode) {
          throw new Error("Bridge không trả mã yêu cầu; vui lòng kiểm tra lại trước khi gửi tiếp.");
        }
        localStorage.removeItem(CART_KEY);
        localStorage.removeItem(CHECKOUT_REQUEST_KEY);
        location.href = `dat-hang-thanh-cong.html?code=${encodeURIComponent(result.requestCode)}`;
      } catch (error) {
        console.error("Storefront request could not be submitted.", error);
        showToast(error.message || "Không thể gửi yêu cầu. Giỏ hàng vẫn được giữ.");
      } finally {
        if (submitButton) submitButton.disabled = false;
      }
    });
  }

  async function renderConfirmation() {
    const root = document.querySelector("[data-order-confirmation]");
    if (!root) return;
    const form = document.querySelector("[data-order-lookup]");
    const codeInput = form?.querySelector('[name="code"]');
    const queryCode = new URLSearchParams(location.search).get("code") || "";
    if (codeInput) codeInput.value = queryCode;
    form?.addEventListener("submit", async (event) => {
      event.preventDefault();
      const code = String(new FormData(form).get("code") || "").trim().toUpperCase();
      if (codeInput) codeInput.value = code;
      await lookupStoreOrder(code, root);
    });
    if (queryCode) {
      await lookupStoreOrder(queryCode.toUpperCase(), root);
    } else {
      root.innerHTML = '<div class="empty-state">Nhập mã tham chiếu để kiểm tra trạng thái đơn hàng.</div>';
    }
  }

  async function lookupStoreOrder(code, root) {
    root.innerHTML = '<div class="empty-state" role="status">Đang kiểm tra đơn hàng…</div>';
    let result;
    try {
      const response = await fetch(
        apiUrl(`/api/storefront/order-requests/${encodeURIComponent(code)}`),
        { cache: "no-store" },
      );
      result = await response.json();
      if (!response.ok || result.requestCode !== code) {
        root.innerHTML = '<div class="empty-state" role="alert"><h2>Không tìm thấy đơn hàng</h2><p>Mã tham chiếu không khớp với đơn đã lưu.</p></div>';
        return;
      }
    } catch (error) {
      console.error("Storefront order lookup could not be verified.", error);
      root.innerHTML = '<div class="empty-state" role="alert"><h2>Chưa kiểm tra được đơn hàng</h2><p>Không kết nối được với bridge cửa hàng. Hãy mở trang qua ứng dụng để tra cứu.</p></div>';
      return;
    }
    const orderStatusLabels = {
      OPEN: "Chờ thanh toán",
      PARTIALLY_PAID: "Đã thanh toán một phần",
      PAID: "Đã thanh toán",
      CANCELLED: "Đã hủy",
    };
    const hasSalesOrder = Boolean(result.salesOrderCode);
    root.innerHTML = `<div class="success-card">
      <span class="success-icon" aria-hidden="true">✓</span>
      <span class="eyebrow">${hasSalesOrder ? "Đơn hàng cửa hàng đã được ghi nhận" : "Yêu cầu cửa hàng"}</span>
      <h1>${hasSalesOrder ? "Đã tạo đơn bán" : "Yêu cầu chưa liên kết đơn bán"}</h1>
      <p>Mã tham chiếu: <strong>${escapeHtml(code)}</strong></p>
      ${hasSalesOrder
        ? `<p>Mã đơn bán: <strong>${escapeHtml(result.salesOrderCode)}</strong></p>
          <p>Trạng thái: <strong>${escapeHtml(orderStatusLabels[result.salesOrderStatus] || "Đang kiểm tra")}</strong>
            · ${money.format(Number(result.salesOrderTotal || 0))}</p>
          <p>${result.inventoryFulfilled
            ? "Kho đã xuất sản phẩm ngay khi tạo đơn. Đơn chưa được thanh toán; vui lòng liên hệ cửa hàng để hoàn tất thanh toán."
            : "Đơn chưa ghi nhận xuất kho. Vui lòng liên hệ cửa hàng để kiểm tra trạng thái."}</p>`
        : "<p>Yêu cầu này được lưu trước khi cửa hàng tự động tạo đơn bán. Chưa có đơn bán hoặc bút toán xuất kho được liên kết.</p>"}
      <a class="button" href="san-pham.html">Tiếp tục xem sản phẩm</a>
    </div>`;
  }

  function bindFilters() {
    ["catalog-search", "catalog-category", "catalog-species", "catalog-sort"].forEach((id) => {
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
    bindApiSettings();
    try {
      await loadProducts();
      populateFilters();
      updateCartCount();
      renderRecommendations();
      renderProductList();
      bindAddButtons();
      renderDetail();
      renderCart();
      renderCheckout();
      await renderConfirmation();
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
