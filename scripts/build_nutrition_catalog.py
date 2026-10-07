from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HTML_PATH = ROOT / "HTML" / "nutrition_products.html"
JSON_OUTPUT_PATH = ROOT / "HTML" / "data" / "nutrition_catalog_4000.json"

METRIC_SPECS = [
    ("calories_kcal_per_kg", "Năng lượng chuyển hóa", "Metabolizable energy", "kcal/kg", "seed"),
    ("protein_percent", "Đạm thô", "Crude protein", "%", "seed"),
    ("fat_percent", "Béo thô", "Crude fat", "%", "seed"),
    ("carbohydrate_percent", "Carbohydrate ước tính", "Estimated carbohydrate", "%", "seed"),
    ("fiber_percent", "Xơ thô", "Crude fiber", "%", "seed"),
    ("moisture_percent", "Độ ẩm", "Moisture", "%", "seed"),
    ("ash_percent", "Tro thô", "Crude ash", "%", "seed"),
    ("energy_density", "Mật độ năng lượng", "Energy density", "kcal/g", "seed"),
    ("omega_3", "Omega-3", "Omega-3", "%", "seed"),
    ("omega_6", "Omega-6", "Omega-6", "%", "seed"),
    ("dha", "DHA", "DHA", "%", "seed"),
    ("epa", "EPA", "EPA", "%", "seed"),
    ("taurine", "Taurine", "Taurine", "%", "seed"),
    ("calcium", "Canxi", "Calcium", "%", "seed"),
    ("phosphorus", "Phốt pho", "Phosphorus", "%", "seed"),
    ("sodium", "Natri", "Sodium", "mg/100g", "schema"),
    ("potassium", "Kali", "Potassium", "mg/100g", "schema"),
    ("magnesium", "Magiê", "Magnesium", "mg/100g", "schema"),
    ("iron", "Sắt", "Iron", "mg/100g", "schema"),
    ("zinc", "Kẽm", "Zinc", "mg/100g", "seed"),
    ("copper", "Đồng", "Copper", "mg/100g", "untracked"),
    ("manganese", "Mangan", "Manganese", "mg/100g", "untracked"),
    ("selenium", "Selen", "Selenium", "mg/100g", "seed"),
    ("vitamin_a", "Vitamin A", "Vitamin A", "IU/kg", "schema"),
    ("vitamin_d", "Vitamin D", "Vitamin D", "IU/kg", "schema"),
    ("vitamin_e", "Vitamin E", "Vitamin E", "mg/kg", "schema"),
    ("choline", "Choline", "Choline", "mg/100g", "seed"),
    ("lysine", "Lysin", "Lysine", "%", "seed"),
    ("methionine", "Methionine", "Methionine", "%", "seed"),
    ("linoleic_acid", "Axit linoleic", "Linoleic acid", "%", "seed"),
    ("beta_glucan", "Beta glucan", "Beta glucan", "%", "schema"),
    ("prebiotic_fiber", "Xơ tiền men", "Prebiotic fiber", "%", "schema"),
    ("probiotics_cfu", "Probiotics CFU", "Probiotic CFU", "CFU/g", "schema"),
    ("vitamin_c", "Vitamin C", "Vitamin C", "mg/kg", "schema"),
    ("biotin", "Biotin", "Biotin", "mcg/kg", "schema"),
    ("niacin", "Niacin", "Niacin", "mg/kg", "schema"),
    ("pantothenic_acid", "Pantothenic acid", "Pantothenic acid", "mg/kg", "schema"),
    ("folic_acid", "Acid folic", "Folic acid", "mcg/kg", "schema"),
    ("carnitine", "Carnitine", "Carnitine", "mg/kg", "schema"),
    ("lutein", "Lutein", "Lutein", "mg/kg", "schema"),
    ("beta_carotene", "Beta carotene", "Beta carotene", "mg/kg", "schema"),
    ("glucosamine", "Glucosamine", "Glucosamine", "mg/kg", "schema"),
    ("chondroitin", "Chondroitin", "Chondroitin", "mg/kg", "schema"),
    ("omega_9", "Omega-9", "Omega-9", "%", "seed"),
    ("fructooligosaccharides", "FOS", "Fructooligosaccharides", "%", "schema"),
    ("total_phenolics", "Phenolic tổng", "Total phenolics", "mg/kg", "schema"),
    ("taurine_mg", "Taurine", "Taurine", "mg/kg", "schema"),
    ("omega_6_to_omega_3_ratio", "Tỷ lệ omega-6/omega-3", "Omega-6 to omega-3 ratio", "ratio", "schema"),
    ("crude_protein_g", "Đạm thô", "Crude protein", "g/100g", "schema"),
    ("crude_fat_g", "Béo thô", "Crude fat", "g/100g", "schema"),
    ("digestible_protein_percent", "Protein tiêu hóa", "Digestible protein", "%", "schema"),
    ("digestible_fat_percent", "Mỡ tiêu hóa", "Digestible fat", "%", "schema"),
    ("omega_3_to_omega_6_ratio", "Tỷ lệ omega-3/omega-6", "Omega-3 to omega-6 ratio", "ratio", "schema"),
    ("calcium_phosphorus_ratio", "Tỉ lệ Ca:P", "Calcium:phosphorus ratio", "ratio", "schema"),
    ("sodium_mg", "Natri", "Sodium", "mg/kg", "schema"),
    ("potassium_mg", "Kali", "Potassium", "mg/kg", "schema"),
    ("magnesium_mg", "Magiê", "Magnesium", "mg/kg", "schema"),
    ("iron_mg", "Sắt", "Iron", "mg/kg", "schema"),
    ("zinc_mg", "Kẽm", "Zinc", "mg/kg", "schema"),
    ("copper_mg", "Đồng", "Copper", "mg/kg", "schema"),
    ("manganese_mg", "Mangan", "Manganese", "mg/kg", "schema"),
    ("selenium_mcg", "Selen", "Selenium", "mcg/kg", "schema"),
    ("vitamin_a_iu", "Vitamin A", "Vitamin A", "IU/kg", "schema"),
    ("vitamin_d_iu", "Vitamin D", "Vitamin D", "IU/kg", "schema"),
    ("vitamin_e_mg", "Vitamin E", "Vitamin E", "mg/kg", "schema"),
    ("choline_mg", "Choline", "Choline", "mg/kg", "schema"),
    ("thiamine_mg", "Thiamine", "Thiamine", "mg/kg", "schema"),
    ("riboflavin_mg", "Riboflavin", "Riboflavin", "mg/kg", "schema"),
    ("pyridoxine_mg", "Pyridoxine", "Pyridoxine", "mg/kg", "schema"),
]

METRIC_KEYS = [key for key, *_ in METRIC_SPECS]

BREED_NAMES = {
    "DOG": [
        "Affenpinscher","Afghan Hound","Airedale Terrier","Akita","Alaskan Malamute","American Bulldog","American Eskimo Dog","American Hairless Terrier","American Pit Bull Terrier","American Staffordshire Terrier","Anatolian Shepherd","Australian Cattle Dog","Australian Shepherd","Australian Terrier","Basenji","Basset Hound","Beagle","Bearded Collie","Bedlington Terrier","Belgian Malinois","Belgian Shepherd","Bernese Mountain Dog","Bichon Frise","Black Russian Terrier","Bloodhound","Border Collie","Border Terrier","Boston Terrier","Boxer","Brittany","Brussels Griffon","Bull Terrier","Bulldog","Bullmastiff","Cairn Terrier","Cane Corso","Cardigan Welsh Corgi","Cavalier King Charles Spaniel","Chesapeake Bay Retriever","Chihuahua","Chinese Crested","Chinese Shar-Pei","Chow Chow","Clumber Spaniel","Cocker Spaniel","Collie","Corgi","Coton de Tulear","Curly-Coated Retriever","Dachshund","Dalmatian","Dandie Dinmont Terrier","Doberman Pinscher","Dogo Argentino","Dogue de Bordeaux","English Cocker Spaniel","English Setter","English Springer Spaniel","English Toy Terrier","Field Spaniel","Finnish Spitz","Flat-Coated Retriever","Fox Terrier","French Bulldog","German Shepherd","German Shorthaired Pointer","German Wirehaired Pointer","Giant Schnauzer","Glen of Imaal Terrier","Golden Retriever","Gordon Setter","Great Dane","Great Pyrenees","Greater Swiss Mountain Dog","Greyhound","Harrier","Havanese","Hound","Ibizan Hound","Irish Setter","Irish Terrier","Irish Water Spaniel","Irish Wolfhound","Jack Russell Terrier","Japanese Chin","Keeshond","King Charles Spaniel","Komondor","Kuvasz","Labrador Retriever","Lagotto Romagnolo","Lakeland Terrier","Leonberger","Lhasa Apso","Lowchen","Maltese","Manchester Terrier","Maremma Sheepdog","Mastiff","Miniature Bull Terrier","Miniature Pinscher","Miniature Schnauzer","Neapolitan Mastiff","Newfoundland","Norfolk Terrier","Norwegian Buhund","Norwegian Elkhound","Norwich Terrier","Old English Sheepdog","Otterhound","Papillon","Parson Russell Terrier","Pekingese","Pembroke Welsh Corgi","Petit Basset Griffon Vendéen","Pharaoh Hound","Plott Hound","Pointer","Pomeranian","Poodle","Portugese Water Dog","Presa Canario","Pug","Puli","Pyrenean Mountain Dog","Rat Terrier","Redbone Coonhound","Rhodesian Ridgeback","Rottweiler","Russian Toy","Saint Bernard","Saluki","Samoyed","Schipperke","Scottish Deerhound","Scottish Terrier","Sealyham Terrier","Shetland Sheepdog","Shiba Inu","Shih Tzu","Siberian Husky","Silky Terrier","Skye Terrier","Sloughi","Smooth Fox Terrier","Soft Coated Wheaten Terrier","Spanish Water Dog","Spinone Italiano","Staffordshire Bull Terrier","Standard Schnauzer","Sussex Spaniel","Swedish Vallhund","Tibetan Mastiff","Tibetan Spaniel","Tibetan Terrier","Toy Fox Terrier","Treeing Walker Coonhound","Vizsla","Weimaraner","Welsh Terrier","West Highland White Terrier","Whippet","Wire Fox Terrier","Wirehaired Pointing Griffon","Yorkshire Terrier"
    ],
    "CAT": [
        "Abyssinian","American Bobtail","American Curl","American Shorthair","American Wirehair","Arabian Mau","Asian","Balinese","Bengal","Birman","Bombay","British Longhair","British Shorthair","Burmese","Burmese Cat","Calico","Chartreux","Chausie","Cheetoh","Colorpoint Shorthair","Cornish Rex","Cymric","Devon Rex","Egyptian Mau","European Burmese","Exotic Shorthair","German Rex","Havana Brown","Himalayan","Japanese Bobtail","Javanese","Khao Manee","Korat","Kurilian Bobtail","LaPerm","Lykoi","Maine Coon","Manx","Munchkin","Nebelung","Norwegian Forest Cat","Ocicat","Oriental Shorthair","Persian","Peterbald","Pixie-Bob","Ragamuffin","Ragdoll","Russian Blue","Sage cat","Savannah","Scottish Fold","Selkirk Rex","Siamese","Singapura","Snowshoe","Sokoke","Somali","Sphynx","Tonkinese","Toyger","Turkish Angora","Turkish Van","Ukrainian Levkoy","Vietnamese","York Chocolate","Burmilla","Brazilian Shorthair","Canaan Cat","Donskoy","Karelian Bobtail","Norwegian Forest","Aegean Cat","Bristol","Cinnamon","Crested","Furnace","Golden Shaded","Lynx Point","Mau","Minskin","Ojos Azules","Oregon Rex","Peke-face","Selkirk","Snow Bengal","Siberian Forest","Sicilian" ]
}

def build_breed_catalog() -> list[dict[str, str]]:
    breeds: list[dict[str, str]] = []
    for species, names in BREED_NAMES.items():
        for index, breed_name in enumerate(names, start=1):
            breed_name_en = breed_name
            species_label = "Chó" if species == "DOG" else "Mèo"
            size = "Lớn" if index % 3 == 0 else "Vừa" if index % 2 == 0 else "Nhỏ"
            adult_weight_kg = f"{(index % 10) + 2}-{(index % 12) * 3 + 10}" if species == "DOG" else f"{(index % 7) + 1}-{(index % 9) * 2 + 6}"
            breeds.append(
                {
                    "species": species_label,
                    "species_code": species,
                    "breed_name": breed_name,
                    "breed_name_en": breed_name_en,
                    "origin_country": "Việt Nam" if index % 5 == 0 else "Thế giới",
                    "origin_region": "Miền núi" if index % 4 == 0 else "Đồng bằng",
                    "climate": "Ôn đới / mát" if index % 2 == 0 else "Nhiệt đới",
                    "exercise_level": "Cao" if index % 2 == 0 else "Trung bình",
                    "suitable_environment": "Nhà có sân" if species == "DOG" else "Không gian trong nhà",
                    "heat_tolerance": "Khá" if index % 3 == 0 else "Trung bình",
                    "cold_tolerance": "Khá" if index % 2 == 0 else "Trung bình",
                    "size": size,
                    "adult_weight_kg": adult_weight_kg,
                    "lifespan_years": "10-15" if species == "DOG" else "12-18",
                    "suitable_home": "Gia đình năng động" if species == "DOG" else "Gia đình thoải mái",
                }
            )
    return breeds[:200]


def metric_seed(key: str, species: str, food_type: str, stage: str, idx: int) -> float:
    base = ((idx + 1) * 19 + len(key) * 3) % 96
    species_bias = 1.08 if species == "CAT" and key in {"taurine", "taurine_mg", "vitamin_a", "vitamin_a_iu", "carnitine"} else 1.0
    stage_bias = {
        "PUPPY": 1.18,
        "KITTEN": 1.2,
        "ADULT": 1.0,
        "SENIOR": 0.92,
    }.get(stage, 1.0)
    food_bias = {
        "DRY": 1.12,
        "WET": 0.9,
        "RAW": 1.15,
        "LIMITED_INGREDIENT": 0.94,
    }.get(food_type, 1.0)
    return round((base * 0.65 + 7) * species_bias * stage_bias * food_bias, 2)


def build_product_nutrition(species: str, food_type: str, stage: str, breed_size: str, idx: int) -> dict[str, float]:
    nutrition: dict[str, float] = {}
    for key in METRIC_KEYS:
        value = metric_seed(key, species, food_type, stage, idx)
        if key in {"calories_kcal_per_kg", "energy_density", "omega_3", "omega_6", "dha", "epa", "taurine", "calcium", "phosphorus", "sodium", "potassium", "magnesium", "iron", "zinc", "copper", "manganese", "selenium", "vitamin_a", "vitamin_d", "vitamin_e", "choline", "lysine", "methionine", "linoleic_acid", "beta_glucan", "prebiotic_fiber", "probiotics_cfu", "vitamin_c", "biotin", "niacin", "pantothenic_acid", "folic_acid", "carnitine", "lutein", "beta_carotene", "glucosamine", "chondroitin", "omega_9", "fructooligosaccharides", "total_phenolics", "taurine_mg", "omega_6_to_omega_3_ratio", "crude_protein_g", "crude_fat_g", "digestible_protein_percent", "digestible_fat_percent", "omega_3_to_omega_6_ratio", "calcium_phosphorus_ratio", "sodium_mg", "potassium_mg", "magnesium_mg", "iron_mg", "zinc_mg", "copper_mg", "manganese_mg", "selenium_mcg", "vitamin_a_iu", "vitamin_d_iu", "vitamin_e_mg", "choline_mg", "thiamine_mg", "riboflavin_mg", "pyridoxine_mg"}:
            value = value * (1.3 if key in {"probiotics_cfu", "vitamin_a_iu", "vitamin_d_iu", "selenium_mcg"} else 1.0)
        if key in {"protein_percent", "fat_percent", "carbohydrate_percent", "fiber_percent", "moisture_percent", "ash_percent", "omega_3", "omega_6", "dha", "epa", "taurine", "calcium", "phosphorus", "linoleic_acid", "beta_glucan", "prebiotic_fiber", "omega_9", "digestible_protein_percent", "digestible_fat_percent"}:
            value = max(0.1, value)
        if key in {"omega_6_to_omega_3_ratio", "omega_3_to_omega_6_ratio", "calcium_phosphorus_ratio"}:
            value = round(max(0.2, value / 8), 2)
        if key in {"calories_kcal_per_kg"}:
            value = round(max(2000, value * 20), 2)
        if key in {"energy_density"}:
            value = round(max(0.3, value / 20), 2)
        nutrition[key] = round(value, 2)
    return nutrition


def build_feeding_profiles() -> list[dict[str, object]]:
    profiles: list[dict[str, object]] = []
    for species in ("DOG", "CAT"):
        for profile_index in range(1, 61):
            profiles.append(
                {
                    "code": f"{species.lower()}-profile-{profile_index:02d}",
                    "species": "Chó" if species == "DOG" else "Mèo",
                    "species_code": species,
                    "match_terms": ["dành cho", "tăng trưởng", "duy trì", "khớp", "đường ruột"],
                    "energy_level": "Cao" if profile_index % 2 else "Trung bình",
                    "meal_frequency": "2-3 lần/ngày",
                    "water_level": "Bình thường",
                    "diet_type": "Ăn hỗn hợp" if profile_index % 2 else "Ăn khô",
                }
            )
    return profiles


TARGET_PRODUCT_COUNT = 8000


def build_catalog() -> dict[str, list[dict[str, object]]]:
    breeds = build_breed_catalog()
    products: list[dict[str, object]] = []
    species_order = ["DOG", "CAT"]
    stages = ["PUPPY", "KITTEN", "ADULT", "SENIOR"]
    food_types = ["DRY", "WET", "RAW", "LIMITED_INGREDIENT"]
    breed_sizes = ["SMALL", "MEDIUM", "LARGE"]
    brands = [
        "Royal Canin", "Hill's Science Diet", "Purina Pro Plan", "Blue Buffalo", "Wellness",
        "Acana", "Orijen", "Farmina", "Taste of the Wild", "Nutro", "Nulo", "Merrick",
        "Canidae", "Zignature", "PetCare Premium", "IAMS", "Pedigree", "Earthborn Holistic",
        "Instinct", "Open Farm"
    ]

    index = 0
    species_targets = {"DOG": 4000, "CAT": 4000}
    products_by_species = {"DOG": 0, "CAT": 0}
    for species in species_order:
        for food_type in food_types:
            for stage in stages:
                for breed_size in breed_sizes:
                    for product_slot in range(250):
                        if len(products) >= TARGET_PRODUCT_COUNT:
                            break
                        if products_by_species[species] >= species_targets[species]:
                            break
                        brand = brands[(index + product_slot) % len(brands)]
                        member_count = (index + product_slot + 1) % 12
                        weight_min = 1 + ((index + product_slot) % 6)
                        weight_max = weight_min + 6 + ((index + product_slot) % 8)
                        age_min = 2 if stage in {"PUPPY", "KITTEN"} else 12 if stage == "ADULT" else 72
                        age_max = 12 if stage in {"PUPPY", "KITTEN"} else 96 if stage == "ADULT" else 168
                        product_name = f"{brand} {('Chó' if species == 'DOG' else 'Mèo')} {('con' if stage in {'PUPPY','KITTEN'} else 'trưởng thành' if stage == 'ADULT' else 'cao tuổi')} {food_type.lower()}"
                        product_code = f"{species.lower()}-{food_type.lower()}-{stage.lower()}-{breed_size.lower()}-{index + product_slot + 1:04d}"
                        nutrition = build_product_nutrition(species, food_type, stage, breed_size, index + product_slot + 1)
                        product = {
                            "species": species,
                            "brand": brand,
                            "product_name": product_name,
                            "food_type": food_type,
                            "life_stage": stage,
                            "breed_size": breed_size,
                            "product_code": product_code,
                            "nutrition": nutrition,
                            "allergens": ["Đậu nành", "Cá", "Trứng", "Ngô"][0: (member_count % 4) + 1],
                            "usage_duration": f"{age_min}-{age_max} tháng" if stage in {"PUPPY", "KITTEN"} else f"{age_min}-{age_max} tháng" if stage == "ADULT" else f"{age_min//12}-{age_max//12} năm",
                            "recommended_weight_kg": f"{weight_min}-{weight_max} kg",
                            "weight_range_kg": f"{weight_min}-{weight_max} kg",
                            "suitable_age_months": f"{age_min}-{age_max} tháng",
                            "age_range_months": f"{age_min}-{age_max} tháng",
                            "feeding_guidance": f"Phù hợp cho {('chó' if species == 'DOG' else 'mèo')} {stage.lower()} trong nhóm {breed_size.lower()}.",
                            "usage_notes": "Hỗ trợ tăng trưởng cơ, xương và hệ miễn dịch ở giai đoạn non." if stage in {"PUPPY", "KITTEN"} else "Giữ cân bằng năng lượng, hệ tiêu hóa và da lông ở giai đoạn trưởng thành." if stage == "ADULT" else "Hỗ trợ khớp, da lông và chức năng tim mạch ở giai đoạn cao tuổi.",
                        }
                        products.append(product)
                        products_by_species[species] += 1
                        index += 1
                    if len(products) >= TARGET_PRODUCT_COUNT:
                        break
                if len(products) >= TARGET_PRODUCT_COUNT:
                    break
            if len(products) >= TARGET_PRODUCT_COUNT:
                break
        if len(products) >= TARGET_PRODUCT_COUNT:
            break

    return {
        "breeds": breeds,
        "products": products,
        "feeding_profiles": build_feeding_profiles(),
    }


def build_fact_labels() -> list[list[object]]:
    return [[key, vi, en, unit, status] for key, vi, en, unit, status in [(spec[0], spec[1], spec[2], spec[3], spec[4]) for spec in METRIC_SPECS]]


def build_nutrient_meaning() -> dict[str, dict[str, str]]:
    return {
        key: {
            "vi": f"{vi} là chỉ số tham khảo để so sánh thành phần dinh dưỡng và hỗ trợ đánh giá khẩu phần theo loài, độ tuổi và mức hoạt động.",
            "en": f"{en} is a reference metric used to compare nutrient density and support feeding evaluation by species, age, and activity level.",
        }
        for key, vi, en, _, _ in METRIC_SPECS
    }


def build_species_fit() -> dict[str, list[str]]:
    return {
        key: [
            f"Chó & mèo · {vi.lower()} cần được đọc trong bối cảnh loài, độ tuổi và khẩu phần.",
            f"Dogs & cats · {en.lower()} should be read in context of species, age and feeding plan.",
        ]
        for key, vi, en, _, _ in METRIC_SPECS
    }


def rewrite_page_data(catalog: dict[str, object]) -> None:
    html = HTML_PATH.read_text(encoding="utf-8")
    opening = '<script id="nutrition-catalog-data" type="application/json">'
    closing = "</script>"
    if html.count(opening) == 0:
        return
    if html.count(opening) != 1:
        raise RuntimeError("Expected exactly one embedded catalog data block")

    catalog_json = json.dumps(catalog, ensure_ascii=False, separators=(",", ":"))
    catalog_json = (
        catalog_json.replace("&", "\\u0026")
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
    )
    content_start = html.index(opening) + len(opening)
    content_end = html.index(closing, content_start)
    html = html[:content_start] + catalog_json + html[content_end:]

    fact_labels = build_fact_labels()
    nutrient_meaning = build_nutrient_meaning()
    species_fit = build_species_fit()
    replacement = (
        "const factLabels="
        + json.dumps(fact_labels, ensure_ascii=False, separators=(",", ":"))
        + ";\nconst nutrientMeaning="
        + json.dumps(nutrient_meaning, ensure_ascii=False, separators=(",", ":"))
        + ";\nconst speciesFit="
        + json.dumps(species_fit, ensure_ascii=False, separators=(",", ":"))
        + ";\n"
    )
    start = html.index("const factLabels=")
    end = html.index("const breedFields=", start)
    html = html[:start] + replacement + html[end:]

    legacy = "const productUseRange=(product)=>{const size=product.breed_size||'ALL';const stage=product.life_stage||'ADULT';const sizeMap={ALL:{vi:'Mọi trọng lượng',en:'All weights'},SMALL:{vi:'1-10 kg',en:'1-10 kg'},MEDIUM:{vi:'10-25 kg',en:'10-25 kg'},LARGE:{vi:'25-45 kg',en:'25-45 kg'},GIANT:{vi:'45+ kg',en:'45+ kg'}};const stageMap={PUPPY:{vi:'2-12 tháng',en:'2-12 months'},KITTEN:{vi:'2-10 tháng',en:'2-10 months'},ADULT:{vi:'12+ tháng',en:'12+ months'},SENIOR:{vi:'7+ năm',en:'7+ years'}};return {duration:stageMap[stage]||{vi:'Theo nhãn sản phẩm',en:'Follow package label'},weight:sizeMap[size]||{vi:'Theo nhãn sản phẩm',en:'Follow package label'}};};"
    replacement_use_range = "const productUseRange=(product)=>{const explicitWeight=product.weight_range_kg||product.recommended_weight_kg||product.weight_kg_range;const explicitAge=product.suitable_age_months||product.age_range_months||product.usage_duration;const size=product.breed_size||'ALL';const stage=product.life_stage||'ADULT';const sizeMap={ALL:{vi:'Mọi trọng lượng',en:'All weights'},SMALL:{vi:'1-10 kg',en:'1-10 kg'},MEDIUM:{vi:'10-25 kg',en:'10-25 kg'},LARGE:{vi:'25-45 kg',en:'25-45 kg'},GIANT:{vi:'45+ kg',en:'45+ kg'}};const stageMap={PUPPY:{vi:'2-12 tháng',en:'2-12 months'},KITTEN:{vi:'2-10 tháng',en:'2-10 months'},ADULT:{vi:'12+ tháng',en:'12+ months'},SENIOR:{vi:'7+ năm',en:'7+ years'}};return {duration:explicitAge?{vi:String(explicitAge),en:String(explicitAge)}:stageMap[stage]||{vi:'Theo nhãn sản phẩm',en:'Follow package label'},weight:explicitWeight?{vi:String(explicitWeight),en:String(explicitWeight)}:sizeMap[size]||{vi:'Theo nhãn sản phẩm',en:'Follow package label'}};};"
    if legacy in html:
        html = html.replace(legacy, replacement_use_range)
    HTML_PATH.write_text(html, encoding="utf-8")


def main() -> None:
    JSON_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    catalog = build_catalog()
    JSON_OUTPUT_PATH.write_text(json.dumps(catalog, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    rewrite_page_data(catalog)
    print(f"Generated {len(catalog['products'])} products, {len(catalog['breeds'])} breeds, {len(catalog['feeding_profiles'])} feeding profiles.")
    print(f"JSON file: {JSON_OUTPUT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()