(() => {
  "use strict";

  const input = document.getElementById("catalogSearch");
  const groupsRoot = document.getElementById("catalogGroups");
  const countNode = document.getElementById("catalogCount");
  let catalog = [];

  function render() {
    const query = input.value.trim().toLocaleLowerCase("vi");
    const visible = catalog.filter((slip) =>
      `${slip.title} ${slip.problem} ${slip.category} ${slip.permission}`
        .toLocaleLowerCase("vi").includes(query)
    );
    countNode.textContent = `Hiển thị ${visible.length} / ${catalog.length} mẫu phiếu`;
    groupsRoot.replaceChildren();
    const grouped = new Map();
    for (const slip of visible) {
      const entries = grouped.get(slip.category) || [];
      entries.push(slip);
      grouped.set(slip.category, entries);
    }
    for (const [category, entries] of grouped) {
      const section = document.createElement("section");
      section.className = "catalog-group";
      const heading = document.createElement("h2");
      heading.textContent = category;
      const grid = document.createElement("div");
      grid.className = "catalog-grid";
      for (const slip of entries) {
        const card = document.createElement("a");
        card.className = "catalog-card";
        card.href = slip.page;
        const number = document.createElement("span");
        number.className = "catalog-num";
        number.textContent = `MẪU ${String(slip.number).padStart(2, "0")} / 40`;
        const title = document.createElement("h3");
        title.textContent = slip.title;
        const problem = document.createElement("p");
        problem.textContent = slip.problem;
        const permission = document.createElement("span");
        permission.className = "catalog-meta";
        permission.textContent = `Quyền cần có: ${slip.permission}`;
        card.append(number, title, problem, permission);
        grid.append(card);
      }
      section.append(heading, grid);
      groupsRoot.append(section);
    }
    if (!visible.length) {
      const empty = document.createElement("div");
      empty.className = "catalog-empty";
      empty.textContent = "Không tìm thấy mẫu phiếu phù hợp.";
      groupsRoot.append(empty);
    }
  }

  fetch("../data/store_slips_catalog.json", {cache: "no-store"})
    .then((response) => {
      if (!response.ok) throw new Error(`Không tải được danh mục (${response.status}).`);
      return response.json();
    })
    .then((payload) => {
      if (!Array.isArray(payload)) throw new Error("Danh mục mẫu phiếu không hợp lệ.");
      catalog = payload;
      render();
    })
    .catch((error) => {
      countNode.textContent = "Không tải được danh mục phiếu";
      const message = document.createElement("div");
      message.className = "slip-status error";
      message.textContent = error.message;
      groupsRoot.replaceChildren(message);
    });

  input.addEventListener("input", render);
})();
