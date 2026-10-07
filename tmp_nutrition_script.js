
(() => {
  const byId = (id) => document.getElementById(id);
  const english = () => document.body.classList.contains('show-en');

  const factLabels = [
    ['calories_kcal_per_kg', 'N?ng l??ng chuy?n h?a', 'Metabolizable energy', 'kcal/kg', 'seed'],
    ['protein_percent', '??m th?', 'Crude protein', '%', 'seed'],
    ['fat_percent', 'B?o th?', 'Crude fat', '%', 'seed'],
    ['carbohydrate_percent', 'Carbohydrate ??c t?nh', 'Estimated carbohydrate', '%', 'seed'],
    ['fiber_percent', 'X? th?', 'Crude fiber', '%', 'seed'],
    ['moisture_percent', '?? ?m', 'Moisture', '%', 'seed'],
    ['ash_percent', 'Tro th?', 'Crude ash', '%', 'seed'],
    ['energy_density', 'M?t ?? n?ng l??ng', 'Energy density', 'kcal/g', 'seed'],
    ['omega_3', 'Omega-3', 'Omega-3', '%', 'seed'],
    ['omega_6', 'Omega-6', 'Omega-6', '%', 'seed'],
    ['dha', 'DHA', 'DHA', '%', 'seed'],
    ['epa', 'EPA', 'EPA', '%', 'seed'],
    ['taurine', 'Taurine', 'Taurine', '%', 'seed'],
    ['calcium', 'Canxi', 'Calcium', '%', 'seed'],
    ['phosphorus', 'Ph?t pho', 'Phosphorus', '%', 'seed'],
    ['sodium', 'Natri', 'Sodium', 'mg/100g', 'seed'],
    ['potassium', 'Kali', 'Potassium', 'mg/100g', 'seed'],
    ['magnesium', 'Magie', 'Magnesium', 'mg/100g', 'seed'],
    ['iron', 'S?t', 'Iron', 'mg/100g', 'seed'],
    ['zinc', 'K?m', 'Zinc', 'mg/100g', 'seed'],
    ['copper', '??ng', 'Copper', 'mg/100g', 'seed'],
    ['manganese', 'Mangan', 'Manganese', 'mg/100g', 'seed'],
    ['selenium', 'Selen', 'Selenium', 'mcg/100g', 'seed'],
    ['vitamin_a', 'Vitamin A', 'Vitamin A', 'IU/kg', 'seed'],
    ['vitamin_d', 'Vitamin D', 'Vitamin D', 'IU/kg', 'seed'],
    ['vitamin_e', 'Vitamin E', 'Vitamin E', 'mg/kg', 'seed'],
    ['choline', 'Choline', 'Choline', 'mg/kg', 'seed'],
    ['lysine', 'Lysine', 'Lysine', '%', 'seed'],
    ['methionine', 'Methionine', 'Methionine', '%', 'seed'],
    ['linoleic_acid', 'Axit linoleic', 'Linoleic acid', '%', 'seed'],
    ['omega_6_to_omega_3_ratio', 'T? l? omega-6/omega-3', 'Omega-6 to omega-3 ratio', 'ratio', 'seed']
  ];

  const nutrientMeaning = {
    calories_kcal_per_kg: {
      vi: 'N?ng l??ng cung c?p cho chuy?n h?a, ho?t ??ng v? t?ng tr??ng. Ph? h?p v?i m?c ho?t ??ng v? giai ?o?n s?ng.',
      en: 'Energy available for metabolism, activity and growth. Match to activity level and life stage.'
    },
    protein_percent: {
      vi: '??m h? tr? c? b?p, m?, mi?n d?ch v? ph?c h?i. Giai ?o?n t?ng tr??ng c?n t? l? cao h?n.',
      en: 'Protein supports muscle, tissue repair, immunity and recovery. Growth stages need higher levels.'
    },
    fat_percent: {
      vi: 'B?o cung c?p n?ng l??ng c? ??c v? h? tr? da, l?ng, n?o v? h?p thu vitamin tan trong m?.',
      en: 'Fat provides concentrated energy and supports skin, coat, brain and fat-soluble vitamin absorption.'
    },
    carbohydrate_percent: {
      vi: 'Carbohydrate cung c?p n?ng l??ng nhanh; n?n ph? h?p v?i ?? ho?t ??ng v? dung n?p c? nh?n.',
      en: 'Carbohydrates provide quick energy and should match activity and individual tolerance.'
    },
    fiber_percent: {
      vi: 'X? h? tr? ti?u h?a, nhu ??ng ru?t v? c?m gi?c no; c?n ph? h?p v?i h? ti?u h?a.',
      en: 'Fiber supports digestion, gut motility and satiety; it must match the digestive system.'
    },
    omega_3: {
      vi: 'Omega-3 h? tr? m?t, n?o v? ch?c n?ng vi?m, th??ng quan tr?ng ? lo?i m?o v? ch? l?n tu?i.',
      en: 'Omega-3 supports vision, brain and inflammatory balance, especially in senior or active pets.'
    },
    taurine: {
      vi: 'Taurine h? tr? tim, m?t v? ch?c n?ng trao ??i ch?t; r?t quan tr?ng v?i m?o.',
      en: 'Taurine supports heart, eye and metabolic function; crucial for cats.'
    },
    calcium: {
      vi: 'Canxi gi?p x??ng, r?ng v? co c?; c?n c?n b?ng v?i phospho.',
      en: 'Calcium supports bones, teeth and muscle function; it must balance with phosphorus.'
    },
    phosphorus: {
      vi: 'Phospho c?n thi?t cho x??ng, ATP v? trao ??i ch?t; ph?i c?n b?ng v?i canxi.',
      en: 'Phosphorus is vital for bones, ATP and metabolism; it must balance with calcium.'
    },
    omega_6_to_omega_3_ratio: {
      vi: 'T? l? omega-6/omega-3 ?nh h??ng ??n vi?m, da v? c?i thi?n ch?t l??ng da l?ng.',
      en: 'The omega-6 to omega-3 ratio affects inflammation, skin and coat quality.'
    }
  };

  const labels = {
    DOG: ['Ch?', 'Dog'],
    CAT: ['M?o', 'Cat'],
    ADULT: ['Tr??ng th?nh', 'Adult'],
    PUPPY: ['Ch? con', 'Puppy'],
    KITTEN: ['M?o con', 'Kitten'],
    SENIOR: ['Cao tu?i', 'Senior'],
    SMALL: ['Nh?', 'Small'],
    MEDIUM: ['V?a', 'Medium'],
    LARGE: ['L?n', 'Large'],
    ALL: ['M?i c?', 'All sizes'],
    DRY: ['H?t kh?', 'Dry'],
    WET: ['Th?c ?n ??t', 'Wet'],
    RAW: ['Th?c ?n s?ng', 'Raw'],
    LIMITED_INGREDIENT: ['H?n ch? nguy?n li?u', 'Limited ingredient']
  };

  const speciesLabels = { DOG: 'Ch?', CAT: 'M?o' };
  const breedNames = [];
  const breedMap = new Map();
  let selected = new Set();
  let currentPage = 1;
  const pageSize = 8;

  function buildBreeds() {
    const prefixes = ['Golden', 'Labrador', 'Corgi', 'Shiba', 'British', 'Siamese', 'Persian', 'Maine', 'Beagle', 'Husky', 'Poodle', 'Bengal', 'Ragdoll', 'Yorkshire', 'Chihuahua', 'Bulldog', 'Tabby', 'Doberman', 'Shepherd', 'Terrier'];
    const names = [];
    for (let i = 1; i <= 200; i += 1) {
      const prefix = prefixes[(i - 1) % prefixes.length];
      const breed = `${prefix} ${i}`;
      names.push({ id: `breed_${i}`, name: breed, species: i % 2 === 0 ? 'DOG' : 'CAT', average_weight_kg: (2.5 + (i % 12) * 2.5), life_span_years: (8 + (i % 10)), temperament: i % 2 ? 'Th?n thi?n, d? nu?i' : 'Nhanh nh?n, n?ng ??ng' });
    }
    return names;
  }

  function buildFeedingProfiles() {
    return [
      { id: 'dog_adult_active', species: 'DOG', profile: 'Dog adult active', meals: '2-3 l?n/ng?y', water_level: 'B?nh th??ng', diet_type: '?n kh?', protein_focus: 'N?ng cao protein', age_range: '12-84 th?ng' },
      { id: 'dog_puppy_growth', species: 'DOG', profile: 'Dog puppy growth', meals: '3-4 l?n/ng?y', water_level: 'Khuy?n ngh? u?ng nhi?u', diet_type: '?n kh? + ??t', protein_focus: 'T?ng dinh d??ng t?ng tr??ng', age_range: '2-12 th?ng' },
      { id: 'dog_senior_joint', species: 'DOG', profile: 'Dog senior joint', meals: '2 l?n/ng?y', water_level: 'B?nh th??ng', diet_type: 'Ki?m so?t n?ng l??ng', protein_focus: 'Ch?ng vi?m, x??ng kh?p', age_range: '84+ th?ng' },
      { id: 'cat_adult_general', species: 'CAT', profile: 'Cat adult general', meals: '3-5 l?n/ng?y', water_level: 'C?n b?ng', diet_type: '?n kh?', protein_focus: 'Protein c?n b?ng', age_range: '12-96 th?ng' },
      { id: 'cat_kitten_growth', species: 'CAT', profile: 'Cat kitten growth', meals: '4-6 l?n/ng?y', water_level: 'Cao', diet_type: '?n ??t + kh?', protein_focus: 'T?ng taurine v? protein', age_range: '2-12 th?ng' },
      { id: 'cat_senior_renal', species: 'CAT', profile: 'Cat senior renal', meals: '2-4 l?n/ng?y', water_level: 'H? tr? hydrat h?a', diet_type: 'Dinh d??ng ki?m so?t kho?ng', protein_focus: 'Gi?m l??ng kho?ng, t?ng ch?t l??ng protein', age_range: '96+ th?ng' }
    ];
  }

  function buildCatalog(limit = 4000) {
    const breedNamePool = buildBreeds().map((item) => item.name);
    const speciesOrder = ['DOG', 'CAT'];
    const foodTypes = ['DRY', 'WET', 'RAW', 'LIMITED_INGREDIENT'];
    const lifeStages = ['PUPPY', 'KITTEN', 'ADULT', 'SENIOR'];
    const sizes = ['SMALL', 'MEDIUM', 'LARGE'];
    const brands = ["Royal Canin", "Hill's Science Diet", "Purina Pro Plan", "Blue Buffalo", "Wellness", "Acana", "Orijen", "Farmina", "Taste of the Wild", "Nutro", "Nulo", "Merrick", "Canidae", "Zignature", "PetCare Premium"];
    const generated = [];
    let index = 0;

    for (const species of speciesOrder) {
      for (const foodType of foodTypes) {
        for (const lifeStage of lifeStages) {
          for (const size of sizes) {
            while (generated.length < limit) {
              const brand = brands[index % brands.length];
              const speciesLabel = species === 'DOG' ? 'Ch?' : 'M?o';
              const stageLabel = lifeStage === 'PUPPY' ? 'Puppy' : lifeStage === 'KITTEN' ? 'Kitten' : lifeStage === 'SENIOR' ? 'Senior' : 'Adult';
              const foodLabel = foodType === 'DRY' ? 'H?t kh?' : foodType === 'WET' ? 'Th?c ?n ??t' : foodType === 'RAW' ? 'Th?c ph?m s?ng' : 'Gi?i h?n nguy?n li?u';
              const productName = `${brand} ${speciesLabel} ${stageLabel} ${foodLabel}`;
              const nutrition = {};
              for (const [key, viName, enName, unit, status] of factLabels) {
                const base = ((index + 1) * (key.length + 7)) % 180;
                const variance = ((index + 3) * (key.length + 5)) % 23;
                const seed = (base + variance) / 20;

                let value = 0;
                if (key === 'calories_kcal_per_kg') value = 2500 + ((index % 11) * 90) + ((species === 'DOG') ? 120 : 70);
                else if (key === 'protein_percent') value = 18 + (seed * 3.8) + ((lifeStage === 'PUPPY' || lifeStage === 'KITTEN') ? 8 : 0);
                else if (key === 'fat_percent') value = 10 + (seed * 2.7) + ((foodType === 'RAW') ? 6 : 2);
                else if (key === 'carbohydrate_percent') value = 18 + (seed * 2.4);
                else if (key === 'fiber_percent') value = 3 + (seed * 0.9);
                else if (key === 'moisture_percent') value = 8 + (seed * 0.9) + ((foodType === 'WET') ? 18 : 0);
                else if (key === 'ash_percent') value = 3 + (seed * 0.7);
                else if (key === 'energy_density') value = 3.2 + (seed * 0.06) + ((foodType === 'WET') ? 0.7 : 0);
                else if (key === 'omega_3') value = 0.6 + (seed * 0.12);
                else if (key === 'omega_6') value = 2.2 + (seed * 0.25);
                else if (key === 'dha') value = 0.15 + (seed * 0.05);
                else if (key === 'epa') value = 0.1 + (seed * 0.04);
                else if (key === 'taurine') value = 0.12 + (seed * 0.07) + ((species === 'CAT') ? 0.35 : 0.04);
                else if (key === 'calcium') value = 0.7 + (seed * 0.22);
                else if (key === 'phosphorus') value = 0.6 + (seed * 0.21);
                else if (key === 'sodium') value = 100 + (seed * 10);
                else if (key === 'potassium') value = 350 + (seed * 18);
                else if (key === 'magnesium') value = 60 + (seed * 8);
                else if (key === 'iron') value = 35 + (seed * 4);
                else if (key === 'zinc') value = 20 + (seed * 3);
                else if (key === 'copper') value = 4 + (seed * 1.2);
                else if (key === 'manganese') value = 2 + (seed * 0.9);
                else if (key === 'selenium') value = 0.08 + (seed * 0.03);
                else if (key === 'vitamin_a') value = 7000 + (seed * 160);
                else if (key === 'vitamin_d') value = 1500 + (seed * 70);
                else if (key === 'vitamin_e') value = 60 + (seed * 8);
                else if (key === 'choline') value = 2000 + (seed * 80);
                else if (key === 'lysine') value = 1.2 + (seed * 0.25);
                else if (key === 'methionine') value = 0.75 + (seed * 0.18);
                else if (key === 'linoleic_acid') value = 1.5 + (seed * 0.35);
                else if (key === 'omega_6_to_omega_3_ratio') value = 1.8 + (seed * 0.18);
                else value = 0;

                if (['protein_percent','fat_percent','carbohydrate_percent','fiber_percent','moisture_percent','ash_percent','omega_3','omega_6','dha','epa','taurine','calcium','phosphorus','linoleic_acid','omega_6_to_omega_3_ratio'].includes(key)) {
                  nutrition[key] = Number(value.toFixed(2));
                } else if (['calories_kcal_per_kg','vitamin_a','vitamin_d','vitamin_e','choline','sodium','potassium','magnesium','iron','zinc','copper','manganese','selenium'].includes(key)) {
                  nutrition[key] = Math.round(value);
                } else {
                  nutrition[key] = Number(value.toFixed(3));
                }
              }

              const usageDuration = lifeStage === 'PUPPY' || lifeStage === 'KITTEN' ? '2-10 th?ng' : lifeStage === 'SENIOR' ? '8-18 th?ng' : '12+ th?ng';
              const weightRange = size === 'SMALL' ? '2-10 kg' : size === 'MEDIUM' ? '10-25 kg' : '25-45 kg';
              const breedName = breedNamePool[(index + 1) % breedNamePool.length] || 'Mixed Breed';

              generated.push({
                species,
                product_name: productName,
                product_code: `${species.toLowerCase()}-${foodType.toLowerCase()}-${lifeStage.toLowerCase()}-${size.toLowerCase()}-${String(index + 1).padStart(4, '0')}`,
                brand,
                food_type: foodType,
                life_stage: lifeStage,
                breed_size: size,
                breed_name: breedName,
                allergens: ['Chicken', 'Beef', 'Fish', 'Egg'].slice(0, (index % 4) + 1),
                usage_duration: usageDuration,
                recommended_weight_kg: weightRange,
                suitable_age_months: lifeStage === 'PUPPY' ? '2-12 th?ng' : lifeStage === 'KITTEN' ? '2-12 th?ng' : lifeStage === 'SENIOR' ? '84-156 th?ng' : '12-84 th?ng',
                feeding_guidance: `Khuy?n ngh? cho ${speciesLabel.toLowerCase()} ${lifeStage.toLowerCase()} thu?c nh?m ${size.toLowerCase()} v? ki?u ?n ${foodType.toLowerCase()}.`,
                usage_notes: lifeStage === 'PUPPY' || lifeStage === 'KITTEN'
                  ? 'D?ng cho giai ?o?n t?ng tr??ng, h? tr? x??ng, tim, n?o v? h? mi?n d?ch.'
                  : lifeStage === 'SENIOR'
                    ? 'D?ng cho giai ?o?n duy tr? ch?c n?ng v?n ??ng, kh?p v? h? ti?u h?a.'
                    : 'D?ng cho giai ?o?n tr??ng th?nh, duy tr? n?ng l??ng v? c? b?p.' ,
                nutrition
              });

              index += 1;
              if (generated.length >= limit) break;
            }
            if (generated.length >= limit) break;
          }
          if (generated.length >= limit) break;
        }
        if (generated.length >= limit) break;
      }
      if (generated.length >= limit) break;
    }

    return generated;
  }

  function getBreedLabel(item) {
    const breed = breedMap.get(item) || breedMap.get(String(item));
    return breed ? breed.name : item || 'All breeds';
  }

  function buyFilters() {
    return {
      search: byId('product-search').value.trim().toLowerCase(),
      species: byId('species-filter').value,
      stage: byId('stage-filter').value,
      size: byId('size-filter').value,
      breed: byId('breed-filter').value,
      feedingSpecies: byId('feeding-species') ? byId('feeding-species').value : 'DOG',
    };
  }

  function getFilteredProducts() {
    const filters = buyFilters();
    return products.filter((product) => {
      const text = `${product.product_name} ${product.product_code} ${product.brand}`.toLowerCase();
      if (filters.search && !text.includes(filters.search)) return false;
      if (filters.species !== 'all' && product.species !== filters.species) return false;
      if (filters.stage !== 'all' && product.life_stage !== filters.stage) return false;
      if (filters.size !== 'all' && product.breed_size !== filters.size) return false;
      if (filters.breed !== 'all' && product.breed_name !== filters.breed) return false;
      return true;
    });
  }

  function formatMetricValue(value, unit) {
    if (value === null || value === undefined || value === '') return '?';
    if (unit === '%') return `${Number(value).toFixed(2)}%`;
    if (unit === 'kcal/kg' || unit === 'kcal/g' || unit === 'mg/100g' || unit === 'mcg/100g' || unit === 'mg/kg' || unit === 'IU/kg') return `${Number(value).toLocaleString()} ${unit}`;
    if (unit === 'ratio') return Number(value).toFixed(2);
    return `${Number(value).toLocaleString()} ${unit}`;
  }

  function getMetricInfo(key, product) {
    const info = nutrientMeaning[key] || { vi: 'Th?ng tin ch? s? dinh d??ng', en: 'Nutrient information' };
    return english() ? info.en : info.vi;
  }

  function renderBreedOptions() {
    const select = byId('breed-filter');
    if (!select) return;
    const options = ['<option value="all">All breeds / T?t c? gi?ng</option>'];
    for (const breed of breeds) {
      options.push(`<option value="${breed.name}">${breed.name}</option>`);
    }
    select.innerHTML = options.join('');
  }

  function renderFeedingOptions() {
    const select = byId('feeding-profile-select');
    if (!select) return;
    const selectedSpecies = byId('feeding-species') ? byId('feeding-species').value : 'DOG';
    const list = feedingProfiles.filter((item) => item.species === selectedSpecies);
    select.innerHTML = list.map((item) => `<option value="${item.id}">${item.profile}</option>`).join('');
    renderFeedingFields();
  }

  function renderFeedingFields() {
    const select = byId('feeding-profile-select');
    const fields = byId('feeding-profile-fields');
    if (!select || !fields) return;
    const target = feedingProfiles.find((item) => item.id === select.value);
    const entries = target ? [
      ['Profile', target.profile],
      ['Meals', target.meals],
      ['Water', target.water_level],
      ['Diet type', target.diet_type],
      ['Protein focus', target.protein_focus],
      ['Age range', target.age_range],
      ['Species', target.species]
    ] : [];
    fields.innerHTML = entries.map(([label, value]) => `<div class="breed-field"><span>${label}</span><strong>${value}</strong></div>`).join('');
  }

  function renderProducts() {
    const filtered = getFilteredProducts();
    const pageCount = Math.max(1, Math.ceil(filtered.length / pageSize));
    currentPage = Math.min(currentPage, pageCount);

    const start = (currentPage - 1) * pageSize;
    const visible = filtered.slice(start, start + pageSize);

    const grid = byId('product-grid');
    const empty = byId('empty-results');
    const pages = byId('catalog-pages');
    const pageStatus = byId('page-status');
    const count = byId('result-count');

    if (grid) {
      if (!visible.length) {
        grid.innerHTML = '';
        if (empty) empty.hidden = false;
      } else {
        if (empty) empty.hidden = true;
        grid.innerHTML = visible.map((product, idx) => {
          const highLevel = factLabels.slice(0, 4).map(([key, vi, en, unit]) => {
            const value = product.nutrition[key];
            return `
              <div class="nutrient">
                <span>${english() ? en : vi}</span>
                <strong>${value !== undefined ? formatMetricValue(value, unit) : '?'}</strong>
              </div>
            `;
          }).join('');

          return `
            <article class="product-card">
              <div class="product-top">
                <div>
                  <div class="product-brand">${product.brand}</div>
                  <h3>${product.product_name}</h3>
                </div>
                <div class="product-code">${product.product_code}</div>
              </div>
              <div class="product-badges">
                <span>${labels[product.species][english() ? 1 : 0]}</span>
                <span>${labels[product.life_stage][english() ? 1 : 0]}</span>
                <span>${labels[product.breed_size][english() ? 1 : 0]}</span>
                <span>${product.food_type}</span>
              </div>
              <div class="usage-strip">
                <div><span>Tu?i / giai ?o?n</span><strong>${product.suitable_age_months}</strong></div>
                <div><span>Kh?i l??ng khuy?n ngh?</span><strong>${product.recommended_weight_kg}</strong></div>
              </div>
              <div class="nutrient-grid">${highLevel}</div>
              <div class="product-foot">
                <div class="allergen-copy">Allergens: ${product.allergens.join(', ') || 'N/A'}</div>
                <button class="compare-button" type="button" data-compare="${product.product_code}" aria-pressed="${selected.has(product.product_code) ? 'true' : 'false'}">${selected.has(product.product_code) ? (english() ? 'Selected' : '?? ch?n') : (english() ? 'Compare' : 'So s?nh')}</button>
              </div>
            </article>
          `;
        }).join('');
      }
    }

    if (pages) pages.hidden = filtered.length <= pageSize;
    if (pageStatus) pageStatus.textContent = filtered.length ? `${currentPage}/${pageCount}` : '0/0';
    if (count) count.textContent = `${filtered.length.toLocaleString()} ${english() ? 'products' : 's?n ph?m'}`;

    const compareButtons = document.querySelectorAll('[data-compare]');
    compareButtons.forEach((button) => {
      button.addEventListener('click', () => toggleCompare(button.dataset.compare));
    });
  }

  function toggleCompare(code) {
    if (selected.has(code)) {
      selected.delete(code);
    } else if (selected.size < 3) {
      selected.add(code);
    } else {
      return;
    }
    renderProducts();
    renderComparison();
  }

  function renderComparison() {
    const panel = byId('compare-panel');
    const content = byId('compare-content');
    if (!panel || !content) return;
    const compareList = products.filter((product) => selected.has(product.product_code));
    if (!compareList.length) {
      panel.hidden = true;
      content.innerHTML = '';
      return;
    }
    panel.hidden = false;
    const columns = compareList.map((p) => `<th>${p.product_name}</th>`).join('');
    const rows = factLabels.map(([key, vi, en, unit]) => {
      const values = compareList.map((product) => {
        const value = product.nutrition[key];
        return `<td>${value !== undefined ? formatMetricValue(value, unit) : '?'}</td>`;
      }).join('');
      return `<tr><th>${english() ? en : vi}</th>${values}</tr>`;
    }).join('');
    content.innerHTML = `<table class="compare-table"><thead><tr><th>${english() ? 'Metric' : 'Ch? s?'}</th>${columns}</tr></thead><tbody>${rows}</tbody></table>`;
  }

  function populateBreedPanel(value) {
    const panel = byId('breed-panel');
    const title = byId('breed-title');
    const fields = byId('breed-fields');
    if (!panel || !title || !fields) return;
    const matched = breeds.find((item) => item.name === value);
    if (!matched) {
      panel.hidden = true;
      return;
    }
    panel.hidden = false;
    title.textContent = matched.name;
    fields.innerHTML = [
      ['Species', matched.species],
      ['Average weight', `${matched.average_weight_kg.toFixed(1)} kg`],
      ['Life span', `${matched.life_span_years} years`],
      ['Temperament', matched.temperament]
    ].map(([label, valueText]) => `<div class="breed-field"><span>${label}</span><strong>${valueText}</strong></div>`).join('');
  }

  function bindEvents() {
    const search = byId('product-search');
    if (search) search.addEventListener('input', () => { currentPage = 1; renderProducts(); });
    ['species-filter', 'stage-filter', 'size-filter', 'breed-filter'].forEach((id) => {
      const el = byId(id);
      if (el) el.addEventListener('change', () => { currentPage = 1; renderProducts(); if (id === 'breed-filter') populateBreedPanel(el.value); });
    });
    const clearBtn = byId('clear-filters');
    if (clearBtn) clearBtn.addEventListener('click', () => {
      byId('product-search').value = '';
      byId('species-filter').value = 'all';
      byId('stage-filter').value = 'all';
      byId('size-filter').value = 'all';
      byId('breed-filter').value = 'all';
      currentPage = 1;
      renderProducts();
    });
    const clearCompare = byId('clear-compare');
    if (clearCompare) clearCompare.addEventListener('click', () => {
      selected = new Set();
      renderProducts();
      renderComparison();
    });
    const prev = byId('product-prev');
    if (prev) prev.addEventListener('click', () => { currentPage = Math.max(1, currentPage - 1); renderProducts(); });
    const next = byId('product-next');
    if (next) next.addEventListener('click', () => {
      const filtered = getFilteredProducts();
      const pageCount = Math.max(1, Math.ceil(filtered.length / pageSize));
      currentPage = Math.min(pageCount, currentPage + 1);
      renderProducts();
    });
    const feedingSpecies = byId('feeding-species');
    if (feedingSpecies) feedingSpecies.addEventListener('change', renderFeedingOptions);
    const feedingProfile = byId('feeding-profile-select');
    if (feedingProfile) feedingProfile.addEventListener('change', renderFeedingFields);
  }

  function bootstrap() {
    breeds = buildBreeds();
    feedingProfiles = buildFeedingProfiles();
    products = buildCatalog(4000);
    breedMap.clear();
    breeds.forEach((breed) => breedMap.set(breed.name, breed));
    renderBreedOptions();
    renderFeedingOptions();
    bindEvents();
    renderProducts();
    renderComparison();
  }

  let products = [];
  let breeds = [];
  let feedingProfiles = [];

  bootstrap();
})();
