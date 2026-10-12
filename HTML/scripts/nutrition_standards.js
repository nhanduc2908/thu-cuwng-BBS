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
  let activeBreed = null;
  const savedProfilesKey = "petcare.saved-nutrition-profiles.v1";

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

  const stageTableMarkup = (breed) => {
    const stages = breed.profile.partIII_lifeStageNutrition || [];
    return `<div class="ns-table-wrap"><table class="ns-dossier-table">
      <thead><tr><th>Giai đoạn · độ tuổi</th><th>Năng lượng & loại thức ăn</th><th>Dưỡng chất cần lưu ý</th></tr></thead>
      <tbody>${stages.map(({ ageBand, nutritionGuidance }) => `
        <tr>
          <th scope="row">${escapeHtml(nutritionGuidance.label)}<small>${escapeHtml(ageBandLabel(ageBand))}</small></th>
          <td><strong>Năng lượng:</strong> ${escapeHtml(nutritionGuidance.energyNeed)}<br><strong>Thức ăn:</strong> ${escapeHtml(nutritionGuidance.foodType)}</td>
          <td>${escapeHtml((nutritionGuidance.nutrientPriorities || []).join("; "))}<small>Nguyên liệu tham khảo: ${escapeHtml((nutritionGuidance.ingredientPriorities || []).join("; "))}</small></td>
        </tr>`).join("")}</tbody>
    </table></div>`;
  };

  const readSavedProfiles = () => {
    try {
      const saved = JSON.parse(localStorage.getItem(savedProfilesKey) || "[]");
      return Array.isArray(saved) ? saved.filter((id) => typeof id === "string") : [];
    } catch (error) {
      console.error("Could not read saved nutrition profiles.", error);
      return [];
    }
  };

  const writeSavedProfiles = (ids) => {
    try {
      localStorage.setItem(savedProfilesKey, JSON.stringify([...new Set(ids)]));
      return true;
    } catch (error) {
      console.error("Could not save nutrition profiles.", error);
      return false;
    }
  };

  const ensureDossierDialog = () => {
    let dialog = document.getElementById("nutritionDossierDialog");
    if (dialog) return dialog;
    dialog = document.createElement("dialog");
    dialog.id = "nutritionDossierDialog";
    dialog.className = "ns-dossier-dialog";
    dialog.setAttribute("aria-labelledby", "nutritionDossierTitle");
    dialog.innerHTML = `
      <div class="ns-dialog-head">
        <div><span class="ns-kicker">PetCare · Nutrition reference</span><h2 id="nutritionDossierTitle"></h2></div>
        <button type="button" class="ns-dialog-close" aria-label="Đóng hồ sơ">×</button>
      </div>
      <div class="ns-dialog-content"></div>
      <div class="ns-dialog-actions">
        <p class="ns-dialog-status" aria-live="polite"></p>
        <div><button type="button" class="ns-button ns-save-profile">Chèn vào Trang chính & Cổng khách hàng</button>
          <button type="button" class="ns-button ns-dialog-close-secondary">Đóng</button></div>
      </div>`;
    document.body.append(dialog);
    dialog.querySelectorAll(".ns-dialog-close, .ns-dialog-close-secondary").forEach((button) => {
      button.addEventListener("click", () => dialog.close());
    });
    dialog.addEventListener("click", (event) => {
      if (event.target === dialog) dialog.close();
    });
    dialog.querySelector(".ns-save-profile").addEventListener("click", () => {
      if (!activeBreed) return;
      const saved = readSavedProfiles();
      const alreadySaved = saved.includes(activeBreed.id);
      const next = alreadySaved ? saved.filter((id) => id !== activeBreed.id) : [...saved, activeBreed.id];
      const feedback = dialog.querySelector(".ns-dialog-status");
      if (!writeSavedProfiles(next)) {
        feedback.textContent = "Không lưu được trong trình duyệt này. Hãy kiểm tra quyền lưu trữ trang web.";
        return;
      }
      updateSaveButton(dialog, activeBreed);
      feedback.textContent = alreadySaved
        ? "Đã gỡ hồ sơ khỏi Trang chính và Cổng khách hàng."
        : "Đã chèn hồ sơ. Mở lại Trang chính hoặc Cổng khách hàng để xem.";
    });
    return dialog;
  };

  const updateSaveButton = (dialog, breed) => {
    const button = dialog.querySelector(".ns-save-profile");
    const isSaved = readSavedProfiles().includes(breed.id);
    button.textContent = isSaved
      ? "Đã chèn · Gỡ khỏi Trang chính & Cổng khách hàng"
      : "Chèn vào Trang chính & Cổng khách hàng";
    button.classList.toggle("primary", !isSaved);
  };

  const openDossier = (breed) => {
    activeBreed = breed;
    const dialog = ensureDossierDialog();
    const dossier = breed.profile;
    const overview = dossier.partI_overview;
    const feeding = dossier.partIV_feedingAndIngredientChecklist;
    const facts = overview.breedSpecificFacts || [];
    const factsMarkup = facts.length
      ? `<ul>${facts.map((fact) => `<li>${escapeHtml(fact.fact || fact.note)} ${escapeHtml(fact.feedingImplication || "")}</li>`).join("")}</ul>`
      : "<p>Chưa có dữ kiện riêng theo giống được xác minh.</p>";
    dialog.querySelector("#nutritionDossierTitle").textContent = `Dinh dưỡng theo giai đoạn · ${breed.name}`;
    dialog.querySelector(".ns-dialog-content").innerHTML = `
      <p class="ns-dialog-lead">${escapeHtml(dossier.partII_nutritionPrinciples.rule)}</p>
      ${stageTableMarkup(breed)}
      <div class="ns-dialog-columns">
        <section><h3>Dưỡng chất cần đối chiếu</h3>${listMarkup(feeding.importantNutrientSources)}</section>
        <section><h3>Lưu ý riêng theo giống</h3>${factsMarkup}</section>
      </div>
      <p class="ns-record-note"><strong>Nguồn tham khảo:</strong> ${sourceMarkup(dossier.sources)}</p>
      <p class="ns-record-note">Không có khẩu phần kcal riêng theo giống. Kiểm tra nhãn của đúng sản phẩm, điều chỉnh theo thể trạng và hỏi bác sĩ thú y khi thú cưng có bệnh lý.</p>`;
    dialog.querySelector(".ns-dialog-status").textContent = "";
    updateSaveButton(dialog, breed);
    if (!dialog.open) dialog.showModal();
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
        <button class="ns-button ns-open-dossier" type="button" data-profile-id="${escapeHtml(breed.id)}">Xem hồ sơ dinh dưỡng theo giai đoạn</button>
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
      list.addEventListener("click", (event) => {
        const button = event.target.closest(".ns-open-dossier");
        if (!button) return;
        const selected = breeds.find((breed) => breed.id === button.dataset.profileId);
        if (selected) openDossier(selected);
      });
      query.addEventListener("input", () => { visibleLimit = 24; render(breeds); });
      sizeFilter.addEventListener("change", () => { visibleLimit = 24; render(breeds); });
      loadMore.addEventListener("click", () => { visibleLimit += 24; render(breeds); });
    })
    .catch((error) => {
      status.textContent = `Không thể tải dữ liệu: ${error.message}. Mở trang qua máy chủ web cục bộ để cho phép tải tệp JSON.`;
      list.innerHTML = '<p class="ns-empty">Dữ liệu giống chưa sẵn sàng; hãy kiểm tra tệp JSON và tải lại trang.</p>';
    });
})();
