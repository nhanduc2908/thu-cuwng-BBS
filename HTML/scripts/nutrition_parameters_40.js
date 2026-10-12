(() => {
  "use strict";

  const speciesSelect = document.getElementById("speciesSelect");
  const breedSearch = document.getElementById("breedSearch");
  const breedSelect = document.getElementById("breedSelect");
  const breedStatus = document.getElementById("breedStatus");
  const selectedBreed = document.getElementById("selectedBreed");
  const stageSummary = document.getElementById("stageSummary");
  const parameterRows = document.getElementById("parameterRows");
  const parameterCount = document.getElementById("parameterCount");
  const stageButtons = [...document.querySelectorAll("[data-stage]")];
  const stageOrder = ["growth", "adult", "senior"];
  const groupLabels = new Map();
  let catalogue;
  let reference;
  let currentStage = "growth";
  let currentBreed = null;

  const escapeHtml = (value) => String(value ?? "").replace(/[&<>"']/g, (character) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;"
  })[character]);

  const normalized = (value) => String(value ?? "").toLocaleLowerCase("vi").trim();

  const groupFor = (groupId) => groupLabels.get(groupId) || "Chỉ tiêu dinh dưỡng";

  const ageBandLabel = (band) => {
    if (!band) return "Theo độ trưởng thành và cá thể";
    if (band.fromAge) return band.fromAge;
    if (Number.isFinite(band.fromMonths) && Number.isFinite(band.toMonthsApprox)) {
      return `${band.fromMonths}–khoảng ${band.toMonthsApprox} tháng`;
    }
    if (Number.isFinite(band.fromMonths) && Number.isFinite(band.toMonthsExclusive)) {
      return `${band.fromMonths}–dưới ${band.toMonthsExclusive} tháng`;
    }
    if (Number.isFinite(band.fromYears) && Number.isFinite(band.toYearsExclusive)) {
      return `${band.fromYears}–dưới ${band.toYearsExclusive} tuổi`;
    }
    if (Number.isFinite(band.fromYearsExclusive)) return `Trên ${band.fromYearsExclusive} tuổi`;
    if (Number.isFinite(band.fromMonthsApprox)) return `Khoảng từ ${band.fromMonthsApprox} tháng`;
    return "Theo độ trưởng thành và cá thể";
  };

  const stageProfile = (breed, stage) => {
    const profileStages = breed.profile?.partIII_lifeStageNutrition || [];
    const expectedId = breed.speciesLabel === "Chó"
      ? { growth: "dog_growth", adult: "dog_adult_maintenance", senior: "dog_senior_individualized" }[stage]
      : { growth: "cat_growth", adult: "cat_young_adult", senior: "cat_senior" }[stage];
    return profileStages.find((item) => item.nutritionGuidance?.id === expectedId) || null;
  };

  const stageNote = (parameter, species, stage) => {
    const id = parameter.id;
    if (stage === "senior") {
      if (id === "metabolizable_energy" || id === "crude_fat") {
        return "Điều chỉnh theo cân nặng, thể trạng, hoạt động và bệnh lý; không có mức giảm cố định chỉ vì tuổi.";
      }
      if (id === "crude_protein" || parameter.group === "amino_acids") {
        return "Theo dõi khối cơ và ăn uống; không tự giảm protein. Điều chỉnh khi bác sĩ thú y xác định bệnh hoặc chỉ định khẩu phần điều trị.";
      }
      if (id === "phosphorus" || id === "calcium" || parameter.group === "minerals") {
        return "Không tự hạn chế hoặc bổ sung. Điều chỉnh khoáng theo chẩn đoán, xét nghiệm và hướng dẫn bác sĩ thú y.";
      }
      if (parameter.group === "fatty_acids") {
        return "Không mặc định cần tăng liều bổ sung; rà soát khẩu phần, thuốc và bệnh lý với bác sĩ thú y.";
      }
      return "Ưu tiên thức ăn hoàn chỉnh phù hợp; thay đổi hoặc bổ sung vi chất chỉ theo nhu cầu cá thể đã được đánh giá.";
    }

    if (stage === "growth") {
      if (id === "metabolizable_energy" || id === "crude_fat") {
        return "Đủ năng lượng cho tăng trưởng đều; tránh cho ăn dư. Chia khẩu phần và theo dõi cân nặng, thể trạng.";
      }
      if (id === "calcium" || id === "phosphorus" || id === "calcium_phosphorus_ratio") {
        return species === "Chó"
          ? "Đối chiếu đồng thời Ca, P, tỷ lệ và năng lượng. Chó lớn/khổng lồ cần thức ăn ghi rõ phù hợp tăng trưởng giống lớn."
          : "Dùng thức ăn hoàn chỉnh cho mèo con; không tự thêm calcium hoặc phosphorus.";
      }
      if (parameter.group === "amino_acids" || id === "crude_protein") {
        return "Chọn công thức hoàn chỉnh cho tăng trưởng với amino acid phù hợp; phần trăm protein thô không đủ để tự đánh giá.";
      }
      return "Đối chiếu bảng tăng trưởng đúng loài; không tự bổ sung riêng khi thức ăn đã hoàn chỉnh và cân bằng.";
    }

    if (id === "metabolizable_energy" || id === "crude_fat") {
      return "Cá thể hóa năng lượng theo thể trạng, triệt sản, vận động và xu hướng cân nặng.";
    }
    if (id === "calcium" || id === "phosphorus" || id === "calcium_phosphorus_ratio") {
      return "Duy trì công thức trưởng thành hoàn chỉnh; không dùng giới hạn tăng trưởng hoặc chế độ bệnh lý cho thú khỏe mạnh.";
    }
    if (parameter.group === "amino_acids" || id === "crude_protein") {
      return "Đối chiếu hồ sơ duy trì trưởng thành; đánh giá protein cùng amino acid và tổng năng lượng.";
    }
    return "Đối chiếu hồ sơ duy trì trưởng thành đúng loài và cơ sở tính.";
  };

  const renderBreedCard = (breed) => {
    const overview = breed.profile?.partI_overview || {};
    const facts = Array.isArray(overview.breedSpecificFacts)
      ? overview.breedSpecificFacts.map((fact) => fact.fact || fact.note).filter(Boolean)
      : [];
    const sourced = Array.isArray(overview.breedFactSourceIds)
      && overview.breedFactSourceIds.length > 0;
    const factStatus = sourced
      ? "Có một số dữ kiện riêng được đối chiếu nguồn; xem các chú thích hồ sơ giống."
      : "Chưa có dữ kiện riêng theo giống được xác minh; chỉ áp dụng khung chung theo loài.";
    selectedBreed.innerHTML = `<div>
      <span class="ns-kicker">${escapeHtml(breed.speciesLabel)} · ${escapeHtml(overview.size || "Chưa phân loại")}</span>
      <h3>${escapeHtml(breed.name)}</h3>
      <p><strong>Xuất xứ trong catalog:</strong> ${escapeHtml([overview.originRegion, overview.originCountry].filter(Boolean).join(", ") || "Chưa có dữ liệu")}</p>
      <p><strong>Cân nặng trưởng thành tham khảo:</strong> ${escapeHtml(overview.adultWeightKg || "Chưa có dữ liệu")}</p>
      <p class="ns-record-note">${escapeHtml(factStatus)}</p>
      ${facts.length ? `<ul>${facts.map((fact) => `<li>${escapeHtml(fact)}</li>`).join("")}</ul>` : ""}
    </div>`;
    selectedBreed.hidden = false;
  };

  const renderStage = () => {
    if (!currentBreed || !reference) return;
    const stage = reference.stages[currentStage];
    const specific = stageProfile(currentBreed, currentStage);
    const guidance = specific?.nutritionGuidance || {};
    const ageBand = specific?.ageBand;
    const stageId = currentStage;

    stageSummary.innerHTML = `<div class="ns-stage-summary-head">
      <div><span class="ns-kicker">${escapeHtml(currentBreed.name)} · ${escapeHtml(currentBreed.speciesLabel)}</span>
        <h3>${escapeHtml(stage.label)}${ageBand ? ` · ${escapeHtml(ageBandLabel(ageBand))}` : ""}</h3></div>
      <span class="ns-stage-tag">Áp dụng theo loài, không theo ngưỡng giống</span>
    </div>
    <p><strong>Định hướng:</strong> ${escapeHtml(guidance.energyNeed || stage[currentBreed.speciesLabel === "Chó" ? "dog" : "cat"])}</p>
    ${guidance.foodType ? `<p><strong>Loại thức ăn:</strong> ${escapeHtml(guidance.foodType)}</p>` : ""}
    ${Array.isArray(guidance.nutrientPriorities) && guidance.nutrientPriorities.length
      ? `<p><strong>Ưu tiên trong hồ sơ:</strong> ${escapeHtml(guidance.nutrientPriorities.join("; "))}</p>`
      : ""}
    <p class="ns-muted">${escapeHtml(stage[currentBreed.speciesLabel === "Chó" ? "dog" : "cat"])}</p>`;

    let rowNumber = 0;
    let previousGroup = "";
    const rows = reference.parameters.map((parameter) => {
      rowNumber += 1;
      const newGroup = parameter.group !== previousGroup;
      previousGroup = parameter.group;
      return `${newGroup ? `<tr class="ns-parameter-group"><th colspan="6">${escapeHtml(groupFor(parameter.group))}</th></tr>` : ""}
        <tr>
          <td class="ns-parameter-number">${rowNumber}</td>
          <th scope="row">${escapeHtml(parameter.label)}<small>${escapeHtml(parameter.unit)}</small></th>
          <td>${escapeHtml(parameter.role)}</td>
          <td>${escapeHtml(parameter.speciesNote)}</td>
          <td>${escapeHtml(stageNote(parameter, currentBreed.speciesLabel, stageId))}</td>
          <td><span class="ns-value-unverified">Chưa công bố ở cấp giống</span><small>Đối chiếu hồ sơ ${escapeHtml(currentBreed.speciesLabel === "Chó" ? "chó" : "mèo")} · ${escapeHtml(stage.label.toLocaleLowerCase("vi"))}</small></td>
        </tr>`;
    }).join("");
    parameterRows.innerHTML = rows;
    parameterCount.textContent = `${reference.parameters.length} chỉ tiêu dinh dưỡng · ${reference.groups.length} nhóm`;
    stageButtons.forEach((button) => button.setAttribute("aria-pressed", String(button.dataset.stage === currentStage)));
  };

  const renderBreedOptions = () => {
    const species = speciesSelect.value;
    const term = normalized(breedSearch.value);
    const matches = catalogue.profiles.filter((breed) => breed.speciesLabel === species
      && (!term || normalized(`${breed.name} ${breed.nameEn || ""}`).includes(term)));
    breedSelect.replaceChildren(new Option(
      matches.length ? "Chọn giống…" : "Không có kết quả",
      ""
    ));
    matches.forEach((breed) => breedSelect.add(new Option(breed.name, breed.id)));
    breedSelect.disabled = matches.length === 0;
    if (currentBreed && matches.some((breed) => breed.id === currentBreed.id)) {
      breedSelect.value = currentBreed.id;
      renderBreedCard(currentBreed);
      renderStage();
    } else if (matches.length) {
      breedSelect.value = matches[0].id;
      currentBreed = matches[0];
      renderBreedCard(currentBreed);
      renderStage();
    } else {
      currentBreed = null;
      selectedBreed.hidden = true;
      stageSummary.innerHTML = "";
      parameterRows.innerHTML = '<tr><td colspan="6">Không tìm thấy giống phù hợp.</td></tr>';
      parameterCount.textContent = "";
    }
    breedStatus.textContent = `${matches.length} / ${catalogue.profiles.filter((breed) => breed.speciesLabel === species).length} hồ sơ thuộc loài đang chọn.`;
  };

  const renderSources = () => {
    document.getElementById("referenceSources").innerHTML = reference.sources.map((source) => (
      `<li><a href="${escapeHtml(source.url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(source.label)}</a></li>`
    )).join("");
  };

  const loadData = async () => {
    const [catalogResponse, referenceResponse] = await Promise.all([
      fetch("../data/pet_breed_nutrition_profiles_200.json", { cache: "no-store" }),
      fetch("../data/nutrition_parameters_40.json", { cache: "no-store" })
    ]);
    if (!catalogResponse.ok) throw new Error(`Không tải được hồ sơ giống (${catalogResponse.status}).`);
    if (!referenceResponse.ok) throw new Error(`Không tải được danh mục chỉ tiêu (${referenceResponse.status}).`);
    [catalogue, reference] = await Promise.all([catalogResponse.json(), referenceResponse.json()]);
    if (!Array.isArray(catalogue.profiles) || !Array.isArray(reference.parameters)) {
      throw new Error("Cấu trúc dữ liệu giống hoặc chỉ tiêu không hợp lệ.");
    }
    const ids = new Set(reference.parameters.map((parameter) => parameter.id));
    if (reference.parameters.length !== 40 || ids.size !== 40) {
      throw new Error(`Danh mục cần đúng 40 chỉ tiêu duy nhất; hiện có ${ids.size}.`);
    }
    reference.groups.forEach((group) => groupLabels.set(group.id, group.label));
    document.getElementById("profileTotal").textContent = String(catalogue.profiles.length);
    document.getElementById("parameterTotal").textContent = String(reference.parameters.length);
    stageButtons.forEach((button) => {
      button.addEventListener("click", () => {
        if (!reference.stages[button.dataset.stage]) return;
        currentStage = button.dataset.stage;
        renderStage();
      });
    });
    const speciesValues = [...new Set(catalogue.profiles.map((profile) => profile.speciesLabel))]
      .sort((left, right) => left.localeCompare(right, "vi"));
    speciesSelect.replaceChildren(new Option("Chọn loài…", ""));
    speciesValues.forEach((species) => speciesSelect.add(new Option(species, species)));
    speciesSelect.addEventListener("change", () => {
      currentBreed = null;
      renderBreedOptions();
    });
    breedSearch.addEventListener("input", renderBreedOptions);
    breedSelect.addEventListener("change", () => {
      currentBreed = catalogue.profiles.find((profile) => profile.id === breedSelect.value) || null;
      if (currentBreed) {
        renderBreedCard(currentBreed);
        renderStage();
      }
    });
    renderSources();
    const firstSpecies = speciesValues[0];
    if (!firstSpecies || !catalogue.profiles.length) {
      throw new Error("Danh mục không có hồ sơ giống để hiển thị.");
    }
    const parameters = new URLSearchParams(window.location.search);
    const requestedBreed = catalogue.profiles.find((profile) => profile.id === parameters.get("breed"));
    const requestedStage = parameters.get("stage");
    if (requestedStage && reference.stages[requestedStage]) currentStage = requestedStage;
    currentBreed = requestedBreed || null;
    speciesSelect.value = requestedBreed?.speciesLabel || firstSpecies;
    renderBreedOptions();
    breedStatus.textContent = `${catalogue.profiles.length} hồ sơ · ${reference.parameters.length} chỉ tiêu · ${stageOrder.length} giai đoạn.`;
  };

  loadData().catch((error) => {
    console.error("Could not load the 40-parameter breed nutrition reference.", error);
    breedStatus.textContent = `Không thể tải dữ liệu: ${error.message}`;
    parameterRows.innerHTML = `<tr><td colspan="6">${escapeHtml(error.message)}</td></tr>`;
  });
})();
