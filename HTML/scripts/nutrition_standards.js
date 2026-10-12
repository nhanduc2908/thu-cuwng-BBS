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
  let sourceReferences = {};

  const escapeHtml = (value) => String(value ?? "").replace(/[&<>"']/g, (character) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;"
  })[character]);

  const ageBandLabel = (band) => {
    if (!band) return "Theo hướng dẫn chung của loài";
    if (band.fromAge) return band.fromAge;
    if (Number.isFinite(band.fromMonths) && Number.isFinite(band.toMonthsApprox)) {
      return `${band.fromMonths}–khoảng ${band.toMonthsApprox} tháng`;
    }
    if (Number.isFinite(band.fromMonthsApprox)) return `Khoảng từ ${band.fromMonthsApprox} tháng`;
    if (Number.isFinite(band.fromMonths) && Number.isFinite(band.toMonthsExclusive)) {
      return `${band.fromMonths}–dưới ${band.toMonthsExclusive} tháng`;
    }
    if (Number.isFinite(band.fromYears) && Number.isFinite(band.toYearsExclusive)) {
      return `${band.fromYears}–dưới ${band.toYearsExclusive} tuổi`;
    }
    if (Number.isFinite(band.fromYears) && Number.isFinite(band.toYearsInclusive)) {
      return `${band.fromYears}–${band.toYearsInclusive} tuổi`;
    }
    if (Number.isFinite(band.fromYearsExclusive)) return `Trên ${band.fromYearsExclusive} tuổi`;
    if (Number.isFinite(band.fromMonths)) return `Từ ${band.fromMonths} tháng`;
    return "Theo cá thể và bác sĩ thú y";
  };

  const listMarkup = (items) => Array.isArray(items) && items.length
    ? `<ul>${items.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>`
    : "";

  const sourceMarkup = (ids) => (ids || []).map((id) => {
    const source = sourceReferences[id];
    return source
      ? `<a href="${escapeHtml(source.url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(source.label)}</a>`
      : "";
  }).filter(Boolean).join(" · ");

  const factStatusLabel = (status) => ({
    partial_source_checked: "Một số dữ kiện cơ bản đã đối chiếu nguồn",
    recognition_only_source_checked: "Chỉ tình trạng ghi nhận giống đã có nguồn",
    alias_source_checked: "Tên gọi khác đã đối chiếu nguồn",
    supplemental_name_only_unverified: "Chỉ có tên giống/loài; chưa xác minh thuộc tính",
    project_reference_unverified: "Thông tin tham khảo từ catalog dự án; chưa xác minh độc lập"
  })[status] || "Trạng thái dữ liệu chưa xác định";

  const dossierMarkup = (breed) => {
    const dossier = breed.profile;
    const overview = dossier.partI_overview;
    const feeding = dossier.partIV_feedingAndIngredientChecklist;
    const specificNotes = overview.breedSpecificFacts || [];
    const stages = dossier.partIII_lifeStageNutrition || [];
    const stageMarkup = stages.map(({ ageBand, nutritionGuidance, sourceIds }) => `
      <section class="ns-dossier-stage">
        <h5>${escapeHtml(nutritionGuidance.label)} <span>· ${escapeHtml(ageBandLabel(ageBand))}</span></h5>
        <p><strong>Năng lượng:</strong> ${escapeHtml(nutritionGuidance.energyNeed)}</p>
        <p><strong>Loại thức ăn:</strong> ${escapeHtml(nutritionGuidance.foodType)}</p>
        <p><strong>Ưu tiên dinh dưỡng:</strong> ${escapeHtml((nutritionGuidance.nutrientPriorities || []).join("; "))}</p>
        <p><strong>Nguyên liệu tham khảo:</strong> ${escapeHtml((nutritionGuidance.ingredientPriorities || []).join("; "))}</p>
        <p class="ns-record-note">${sourceMarkup(sourceIds)}</p>
      </section>`).join("");
    const factsMarkup = specificNotes.map((fact) => fact.fact
      ? `<li><strong>${escapeHtml(fact.fact)}</strong><br>${escapeHtml(fact.feedingImplication || "")}</li>`
      : `<li>${escapeHtml(fact.note || "Chưa có dữ kiện riêng của giống được xác minh.")}</li>`
    ).join("");
    const supplementNote = breed.verificationStatus === "supplemental_name_only_unverified"
      ? '<p class="ns-record-note"><strong>Chỉ mục bổ sung chưa xác minh:</strong> hiện chỉ có tên giống và loài; không có dữ liệu mô tả riêng.</p>'
      : "";

    return `<details class="ns-dossier">
      <summary>Xem hồ sơ dinh dưỡng theo giai đoạn</summary>
      ${supplementNote}
      <p><strong>Nguyên tắc:</strong> ${escapeHtml(dossier.partII_nutritionPrinciples.rule)}</p>
      <p><strong>Năng lượng:</strong> ${escapeHtml(feeding.dailyCalories.reason)} ${escapeHtml(feeding.dailyCalories.method)}</p>
      <h4>Giai đoạn sống</h4>
      ${stageMarkup}
      <h4>Dưỡng chất cần đối chiếu</h4>
      ${listMarkup(feeding.importantNutrientSources)}
      <h4>Lưu ý riêng theo giống</h4>
      <ul>${factsMarkup}</ul>
      <h4>Checklist chọn thức ăn</h4>
      ${listMarkup(feeding.checklist)}
      <p><strong>Kết luận:</strong> ${escapeHtml(dossier.partVI_conclusion)}</p>
      <p class="ns-record-note"><strong>Nguồn:</strong> ${sourceMarkup(dossier.sources)}</p>
    </details>`;
  };

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
      const overview = breed.profile.partI_overview;
      const hasBreedSource = overview.breedFactSourceIds?.length > 0;
      const weightConflict = hasBreedSource ? null : disagreements.adult_weight_kg;
      const sizeConflict = hasBreedSource ? null : disagreements.size;
      const conflictLabels = {
        size: "Kích thước",
        adult_weight_kg: "Cân nặng trưởng thành (kg)",
        origin_country: "Quốc gia xuất xứ",
        origin_region: "Vùng xuất xứ",
        climate: "Khí hậu",
        suitable_environment: "Môi trường phù hợp",
        suitable_home: "Môi trường sống gợi ý",
        lifespan_years: "Tuổi thọ",
        exercise_level: "Mức vận động",
        heat_tolerance: "Khả năng chịu nóng",
        cold_tolerance: "Khả năng chịu lạnh"
      };
      const weight = weightConflict
        ? `Hồ sơ dự án có nhiều giá trị: ${escapeHtml(weightConflict.join(" / "))} kg`
        : (overview.adultWeightKg ? `${escapeHtml(overview.adultWeightKg)} kg` : "Chưa có dữ liệu");
      const size = sizeConflict ? sizeConflict.join(" / ") : (overview.size || "Chưa phân loại");
      const conflictNote = Object.keys(disagreements).length
        ? `<p class="ns-record-note">${hasBreedSource
          ? "Catalog nội bộ có dữ kiện khác nhau; các trường được nguồn riêng xác nhận bên trên được ưu tiên. Các trường còn lại vẫn chưa xác minh."
          : `Sai khác giữa các bản ghi trùng tên: ${Object.entries(disagreements).map(([field, values]) => `${escapeHtml(conflictLabels[field] || field)}: ${escapeHtml(values.join(" / "))}`).join("; ")}. Các giá trị chưa được xác minh là biến thể giống.`}</p>`
        : "";
      const activity = [breed.exercise_level, overview.dailyExercise].filter(Boolean).join(" · ");
      return `<article class="ns-breed" style="animation-delay:${Math.min(index % 12, 11) * 25}ms">
        <h3>${escapeHtml(breed.breed_name)}</h3>
        <div class="latin">${escapeHtml(breed.breed_name_en || "")}</div>
        <div class="ns-tags"><span class="ns-tag">${escapeHtml(size)}</span><span class="ns-tag">${escapeHtml(species)}</span></div>
        <p><strong>Cân nặng trưởng thành tham khảo:</strong> ${weight}</p>
        <p><strong>Xuất xứ trong catalog:</strong> ${escapeHtml([overview.originRegion, overview.originCountry].filter(Boolean).join(", ") || "Chưa có dữ liệu")}</p>
        <p><strong>Hoạt động/vận động:</strong> ${escapeHtml(activity || "Chưa có dữ liệu")} · <strong>Tuổi thọ:</strong> ${escapeHtml(overview.lifespanYears || "Chưa có dữ liệu")}</p>
        <p class="ns-record-note"><strong>Trạng thái dữ kiện:</strong> ${escapeHtml(factStatusLabel(overview.breedFactStatus))}${overview.breedFactSourceIds?.length ? `<br><strong>Nguồn giống:</strong> ${sourceMarkup(overview.breedFactSourceIds)}` : ""}</p>
        <p><strong>Khung chọn khẩu phần:</strong> đối chiếu giai đoạn sống, thể trạng và tuyên bố dinh dưỡng cho ${escapeHtml(species.toLocaleLowerCase("vi"))}; không có ngưỡng AAFCO/FEDIAF riêng cho tên giống này.</p>
        ${conflictNote}
        ${dossierMarkup(breed)}
      </article>`;
    }).join("");
  };

  fetch("../data/pet_breed_nutrition_profiles_200.json")
    .then((response) => {
      if (!response.ok) throw new Error(`Không tải được danh mục giống (${response.status})`);
      return response.json();
    })
    .then((data) => {
      sourceReferences = Object.fromEntries((data.sourceReferences || []).map((source) => [source.id, source]));
      const breeds = data.profiles
        .filter((breed) => breed.speciesLabel === species)
        .map((breed) => ({
          ...breed,
          breed_name: breed.name,
          breed_name_en: breed.nameEn,
          origin_country: breed.profile.partI_overview.originCountry,
          origin_region: breed.profile.partI_overview.originRegion,
          size: breed.profile.partI_overview.size,
          adult_weight_kg: breed.profile.partI_overview.adultWeightKg,
          lifespan_years: breed.profile.partI_overview.lifespanYears,
          exercise_level: breed.profile.partI_overview.exerciseLevel,
          conflicts: breed.profile.partI_overview.conflicts || {}
        }));
      if (!breeds.length) throw new Error(`Danh mục không có hồ sơ cho loài: ${species}`);
      const totalBadge = document.getElementById(species === "Chó" ? "dogTotal" : "catTotal");
      if (totalBadge) totalBadge.textContent = String(breeds.length);
      const sizes = [...new Set(breeds.map((breed) => breed.size).filter(Boolean))]
        .sort((a, b) => a.localeCompare(b, "vi"));
      sizeFilter.innerHTML = '<option value="">Tất cả kích thước</option>'
        + sizes.map((size) => `<option value="${escapeHtml(size)}">${escapeHtml(size)}</option>`).join("");
      status.textContent = `${breeds.length} hồ sơ giống · khung dinh dưỡng theo giai đoạn; ${data.summary.profilesWithBreedSpecificSourceFacts} hồ sơ có một số dữ kiện giống kèm nguồn, các trường khác giữ trạng thái riêng.`;
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
