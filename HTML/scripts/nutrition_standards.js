(() => {
  "use strict";

  const page = document.querySelector("[data-breed-page]");
  if (!page) return;

  const species = page.dataset.breedPage;
  const query = document.getElementById("breedSearch");
  const sizeFilter = document.getElementById("sizeFilter");
  const list = document.getElementById("breedResults");
  const count = document.getElementById("breedCount");
  const status = document.getElementById("breedStatus");
  const loadMore = document.getElementById("breedLoadMore");
  let visibleLimit = 24;

  const escapeHtml = (value) => String(value ?? "").replace(/[&<>"']/g, (character) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;"
  })[character]);

  const render = (breeds) => {
    const searchTerm = query.value.trim().toLocaleLowerCase("vi");
    const selectedSize = sizeFilter.value;
    const filtered = breeds.filter((breed) => {
      const fields = [breed.breed_name, breed.breed_name_en, breed.origin_country, breed.origin_region, breed.size]
        .filter(Boolean).join(" ").toLocaleLowerCase("vi");
      return (!searchTerm || fields.includes(searchTerm))
        && (!selectedSize || breed.size === selectedSize);
    });

    count.textContent = `${Math.min(visibleLimit, filtered.length)} / ${filtered.length} kết quả`;
    loadMore.hidden = visibleLimit >= filtered.length;
    if (!filtered.length) {
      list.innerHTML = '<p class="ns-empty">Không tìm thấy giống phù hợp. Hãy thử từ khóa hoặc kích thước khác.</p>';
      return;
    }

    list.innerHTML = filtered.slice(0, visibleLimit).map((breed, index) => {
      const disagreements = breed.conflicts || {};
      const weightConflict = disagreements.adult_weight_kg;
      const sizeConflict = disagreements.size;
      const conflictLabels = {
        size: "Kích thước",
        adult_weight_kg: "Cân nặng trưởng thành (kg)",
        origin_country: "Quốc gia xuất xứ",
        origin_region: "Vùng xuất xứ",
        climate: "Khí hậu",
        suitable_environment: "Môi trường phù hợp",
        lifespan_years: "Tuổi thọ",
        exercise_level: "Mức vận động"
      };
      const weight = weightConflict
        ? `Hồ sơ dự án có nhiều giá trị: ${escapeHtml(weightConflict.join(" / "))} kg`
        : (breed.adult_weight_kg ? `${escapeHtml(breed.adult_weight_kg)} kg` : "Chưa có dữ liệu");
      const size = sizeConflict ? sizeConflict.join(" / ") : (breed.size || "Chưa phân loại");
      const conflictNote = Object.keys(disagreements).length
        ? `<p class="ns-record-note">Sai khác giữa các bản ghi trùng tên: ${Object.entries(disagreements).map(([field, values]) => `${escapeHtml(conflictLabels[field] || field)}: ${escapeHtml(values.join(" / "))}`).join("; ")}. Các giá trị chưa được xác minh là biến thể giống.</p>`
        : "";
      return `<article class="ns-breed" style="animation-delay:${Math.min(index % 12, 11) * 25}ms">
        <h3>${escapeHtml(breed.breed_name)}</h3>
        <div class="latin">${escapeHtml(breed.breed_name_en || "")}</div>
        <div class="ns-tags"><span class="ns-tag">${escapeHtml(size)}</span><span class="ns-tag">${escapeHtml(species)}</span></div>
        <p><strong>Cân nặng trưởng thành tham khảo:</strong> ${weight}</p>
        <p><strong>Xuất xứ trong catalog:</strong> ${escapeHtml([breed.origin_region, breed.origin_country].filter(Boolean).join(", ") || "Chưa có dữ liệu")}</p>
        <p><strong>Hoạt động:</strong> ${escapeHtml(breed.exercise_level || "Chưa có dữ liệu")} · <strong>Tuổi thọ:</strong> ${escapeHtml(breed.lifespan_years || "Chưa có dữ liệu")}</p>
        <p><strong>Khung chọn khẩu phần:</strong> đối chiếu giai đoạn sống, thể trạng và tuyên bố dinh dưỡng cho ${escapeHtml(species.toLocaleLowerCase("vi"))}; không có ngưỡng AAFCO/FEDIAF riêng cho tên giống này.</p>
        ${conflictNote}
      </article>`;
    }).join("");
  };

  fetch("../data/nutrition_breed_profiles.json")
    .then((response) => {
      if (!response.ok) throw new Error(`Không tải được danh mục giống (${response.status})`);
      return response.json();
    })
    .then((data) => {
      const breeds = data.breeds.filter((breed) => breed.species === species);
      if (!breeds.length) throw new Error(`Danh mục không có hồ sơ cho loài: ${species}`);
      const totalBadge = document.getElementById(species === "Chó" ? "dogTotal" : "catTotal");
      if (totalBadge) totalBadge.textContent = String(breeds.length);
      const sizes = [...new Set(breeds.map((breed) => breed.size).filter(Boolean))]
        .sort((a, b) => a.localeCompare(b, "vi"));
      sizeFilter.innerHTML = '<option value="">Tất cả kích thước</option>'
        + sizes.map((size) => `<option value="${escapeHtml(size)}">${escapeHtml(size)}</option>`).join("");
      status.textContent = `${breeds.length} tên giống duy nhất · ${data.source_record_count} dòng nguồn, đã gộp bản ghi trùng tên và giữ cảnh báo sai khác.`;
      render(breeds);
      query.addEventListener("input", () => { visibleLimit = 24; render(breeds); });
      sizeFilter.addEventListener("change", () => { visibleLimit = 24; render(breeds); });
      loadMore.addEventListener("click", () => { visibleLimit += 24; render(breeds); });
    })
    .catch((error) => {
      status.textContent = `Không thể tải dữ liệu: ${error.message}. Mở trang qua máy chủ web cục bộ để cho phép tải tệp JSON.`;
      list.innerHTML = '<p class="ns-empty">Dữ liệu giống chưa sẵn sàng; hãy kiểm tra tệp JSON và tải lại trang.</p>';
    });
})();
