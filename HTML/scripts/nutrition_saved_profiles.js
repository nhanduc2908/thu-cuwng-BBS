(() => {
  "use strict";

  const storageKey = "petcare.saved-nutrition-profiles.v1";
  const target = document.querySelector("[data-saved-nutrition-profiles]");
  if (!target) return;

  const escapeHtml = (value) => String(value ?? "").replace(/[&<>"']/g, (character) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;"
  })[character]);

  const readSavedIds = () => {
    try {
      const saved = JSON.parse(localStorage.getItem(storageKey) || "[]");
      return Array.isArray(saved) ? saved.filter((id) => typeof id === "string") : [];
    } catch (error) {
      console.error("Could not read saved nutrition profiles.", error);
      target.innerHTML = '<p class="saved-nutrition-empty" role="alert">Không thể đọc danh sách hồ sơ đã chèn trong bộ nhớ trình duyệt.</p>';
      return null;
    }
  };

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

  const renderProfiles = (documentData) => {
    const savedIds = readSavedIds();
    if (!savedIds) return;
    const profilesById = new Map(documentData.profiles.map((profile) => [profile.id, profile]));
    const profiles = savedIds.map((id) => profilesById.get(id)).filter(Boolean);
    if (!profiles.length) {
      target.innerHTML = '<p class="saved-nutrition-empty">Chưa có hồ sơ nào được chèn. Mở tra cứu giống, chọn “Xem hồ sơ dinh dưỡng theo giai đoạn”, rồi bấm “Chèn vào Trang chính &amp; Cổng khách hàng”.</p>';
      return;
    }

    target.innerHTML = profiles.map((profile) => {
      const stages = profile.profile.partIII_lifeStageNutrition || [];
      return `<article class="saved-nutrition-card">
        <header class="saved-nutrition-card-head">
          <div><span class="saved-nutrition-species">${escapeHtml(profile.speciesLabel)}</span><h3>${escapeHtml(profile.name)}</h3></div>
          <button type="button" class="saved-nutrition-remove" data-remove-profile="${escapeHtml(profile.id)}" aria-label="Gỡ hồ sơ ${escapeHtml(profile.name)}">Gỡ hồ sơ</button>
        </header>
        <div class="saved-nutrition-table-wrap"><table class="saved-nutrition-table">
          <thead><tr><th>Giai đoạn</th><th>Độ tuổi</th><th>Hướng dẫn ngắn</th></tr></thead>
          <tbody>${stages.map(({ ageBand, nutritionGuidance }) => `
            <tr>
              <th scope="row">${escapeHtml(nutritionGuidance.label)}</th>
              <td>${escapeHtml(ageBandLabel(ageBand))}</td>
              <td><strong>Năng lượng:</strong> ${escapeHtml(nutritionGuidance.energyNeed)}<br>
                <strong>Thức ăn:</strong> ${escapeHtml(nutritionGuidance.foodType)}<br>
                <strong>Dưỡng chất:</strong> ${escapeHtml((nutritionGuidance.nutrientPriorities || []).join("; "))}</td>
            </tr>`).join("")}</tbody>
        </table></div>
        <p class="saved-nutrition-note">${escapeHtml(profile.profile.partVI_conclusion)}</p>
      </article>`;
    }).join("");
  };

  target.addEventListener("click", (event) => {
    const button = event.target.closest("[data-remove-profile]");
    if (!button) return;
    const saved = readSavedIds();
    if (!saved) return;
    const next = saved.filter((id) => id !== button.dataset.removeProfile);
    try {
      localStorage.setItem(storageKey, JSON.stringify(next));
      renderProfiles(window.petcareNutritionDossier);
    } catch (error) {
      console.error("Could not remove saved nutrition profile.", error);
      button.textContent = "Không gỡ được";
      button.disabled = true;
    }
  });

  window.addEventListener("storage", (event) => {
    if (event.key === storageKey && window.petcareNutritionDossier) {
      renderProfiles(window.petcareNutritionDossier);
    }
  });

  fetch(target.dataset.source)
    .then((response) => {
      if (!response.ok) throw new Error(`Không tải được hồ sơ dinh dưỡng (${response.status})`);
      return response.json();
    })
    .then((data) => {
      window.petcareNutritionDossier = data;
      renderProfiles(data);
    })
    .catch((error) => {
      console.error("Could not load the nutrition dossier catalog.", error);
      target.innerHTML = `<p class="saved-nutrition-empty" role="alert">Không tải được dữ liệu hồ sơ: ${escapeHtml(error.message)}.</p>`;
    });
})();
