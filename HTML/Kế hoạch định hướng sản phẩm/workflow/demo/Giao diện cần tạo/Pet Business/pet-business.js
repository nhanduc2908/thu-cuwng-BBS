(() => {
  "use strict";

  const root = document.getElementById("demoApp");
  if (!root || document.body.dataset.demo !== "pet-business") return;

  const skipLink = document.querySelector('.skip-link[href="#demoApp"]');
  skipLink?.addEventListener("click", (event) => {
    event.preventDefault();
    root.focus();
  });

  const fail = (message) => {
    console.error(`[Pet Business] ${message}`);
    root.setAttribute("aria-busy", "false");
    const section = document.createElement("section");
    section.className = "business-app-error";
    section.setAttribute("role", "alert");
    const title = document.createElement("strong");
    title.textContent = "Không thể khởi tạo công cụ Pet Business";
    const detail = document.createElement("p");
    detail.textContent = message;
    const reload = document.createElement("a");
    reload.href = "index.html";
    reload.textContent = "Tải lại Control tower";
    section.append(title, detail, reload);
    root.replaceChildren(section);
  };
  const config = window.PetBusinessConfig;
  if (!config || !Array.isArray(config.routes)) {
    fail("Không nạp được pet-business-config.js. Hãy tải lại trang và kiểm tra thứ tự script.");
    return;
  }
  if (root.getAttribute("aria-busy") !== "false" || !root.querySelector('[data-system="pet-business"]')) {
    fail("Ứng dụng nghiệp vụ chưa khởi tạo thành công. Kiểm tra demo.js và dữ liệu route.");
    return;
  }

  const activeRoute = document.body.dataset.demoPage;
  if (!config.routes.some(({ key }) => key === activeRoute)) {
    fail(`Route "${activeRoute || "(trống)"}" chưa được đăng ký trong cấu hình Pet Business.`);
    return;
  }

  const app = root.querySelector('[data-system="pet-business"]');
  const tools = app.querySelector(".business-topbar .frame-tools");
  if (!tools) {
    fail("Không tìm thấy vùng công cụ trên thanh điều hướng.");
    return;
  }

  const trigger = document.createElement("button");
  trigger.type = "button";
  trigger.className = "icon-action business-command-trigger";
  trigger.setAttribute("aria-label", "Mở chuyển nhanh màn hình");
  trigger.setAttribute("aria-haspopup", "dialog");
  trigger.setAttribute("aria-keyshortcuts", "Control+K Meta+K");
  trigger.title = "Chuyển nhanh màn hình (Ctrl/Cmd+K)";
  trigger.textContent = "⌕";
  tools.prepend(trigger);

  const dialog = document.createElement("dialog");
  dialog.className = "business-command-dialog";
  dialog.setAttribute("aria-labelledby", "business-command-title");
  dialog.innerHTML = `
    <div class="business-command-head">
      <div><span class="workspace-kicker">PET BUSINESS · QUICK NAVIGATION</span><h2 id="business-command-title">Chuyển nhanh màn hình</h2></div>
      <button class="business-command-close" type="button" aria-label="Đóng chuyển nhanh">Esc</button>
    </div>
    <label class="business-command-search-label" for="business-command-search">Tìm trang theo tên hoặc nghiệp vụ</label>
    <input id="business-command-search" class="business-command-search" type="search" autocomplete="off" placeholder="Ví dụ: tồn kho, duyệt, báo cáo">
    <nav class="business-command-routes" aria-label="Màn hình Pet Business"></nav>
    <p class="business-command-empty" role="status" hidden>Không tìm thấy màn hình phù hợp.</p>
    <p class="business-command-hint">Phím tắt: Ctrl/Cmd + K · ↑/↓ để chọn · Enter để mở · Esc để đóng</p>`;
  app.append(dialog);

  const routeList = dialog.querySelector(".business-command-routes");
  const search = dialog.querySelector(".business-command-search");
  const closeButton = dialog.querySelector(".business-command-close");
  const emptyState = dialog.querySelector(".business-command-empty");
  const routeLinks = config.routes.map((route, index) => {
    const link = document.createElement("a");
    link.className = "business-command-route";
    link.href = route.key === "overview" ? "index.html" : `${route.key}.html`;
    link.dataset.search = `${route.label} ${route.group} ${route.hint}`.toLocaleLowerCase("vi");
    link.dataset.routeIndex = String(index);
    link.setAttribute("aria-current", route.key === activeRoute ? "page" : "false");
    link.innerHTML = `<span class="business-command-route-index">${String(index + 1).padStart(2, "0")}</span><span class="business-command-route-copy"><strong></strong><small></small></span><span class="business-command-route-group"></span>`;
    link.querySelector("strong").textContent = route.label;
    link.querySelector("small").textContent = route.hint;
    link.querySelector(".business-command-route-group").textContent = route.group;
    routeList.append(link);
    return link;
  });

  const visibleRoutes = () => routeLinks.filter((link) => !link.hidden);
  const updateRoutes = () => {
    const query = search.value.trim().toLocaleLowerCase("vi");
    for (const link of routeLinks) link.hidden = !link.dataset.search.includes(query);
    const visible = visibleRoutes();
    emptyState.hidden = visible.length > 0;
    visible.forEach((link, index) => link.classList.toggle("is-selected", index === 0));
  };
  const openPalette = () => {
    if (dialog.open) return;
    dialog.showModal();
    search.value = "";
    updateRoutes();
    search.focus();
  };
  const closePalette = () => {
    if (dialog.open) dialog.close();
    trigger.focus();
  };

  trigger.addEventListener("click", openPalette);
  closeButton.addEventListener("click", closePalette);
  search.addEventListener("input", updateRoutes);
  search.addEventListener("keydown", (event) => {
    if (event.key !== "ArrowDown" && event.key !== "ArrowUp" && event.key !== "Enter") return;
    const visible = visibleRoutes();
    if (!visible.length) return;
    event.preventDefault();
    const selectedIndex = Math.max(0, visible.findIndex((link) => link.classList.contains("is-selected")));
    if (event.key === "Enter") {
      visible[selectedIndex].click();
      return;
    }
    const direction = event.key === "ArrowDown" ? 1 : -1;
    const nextIndex = (selectedIndex + direction + visible.length) % visible.length;
    visible.forEach((link, index) => link.classList.toggle("is-selected", index === nextIndex));
    visible[nextIndex].scrollIntoView({ block: "nearest" });
  });
  routeList.addEventListener("pointermove", (event) => {
    const route = event.target.closest(".business-command-route");
    if (!route || route.hidden) return;
    for (const link of visibleRoutes()) link.classList.toggle("is-selected", link === route);
  });
  dialog.addEventListener("click", (event) => {
    if (event.target === dialog) closePalette();
  });
  dialog.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      event.preventDefault();
      closePalette();
    }
  });
  dialog.addEventListener("close", () => trigger.focus());
  document.addEventListener("keydown", (event) => {
    if (event.key.toLowerCase() === "k" && (event.ctrlKey || event.metaKey) &&
        !event.altKey && !event.shiftKey && !/^(input|textarea|select)$/i.test(document.activeElement?.tagName || "")) {
      event.preventDefault();
      openPalette();
    }
  });
})();
