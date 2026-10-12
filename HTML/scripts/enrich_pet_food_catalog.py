import json
import re
import unicodedata
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CATALOG_PATH = DATA / "pet_food_breed_allergen_catalog.json"
PRODUCT_SOURCE_PATH = DATA / "pet_product_specs.json"
BREED_SOURCE_PATH = DATA / "nutrition_breed_profiles.json"
LEGACY_BREED_INDEX_PATH = DATA / "nutrition_catalog_4000.json"
BREED_DOSSIER_PATH = DATA / "pet_breed_nutrition_profiles_200.json"
BREED_FACT_OVERRIDES_PATH = DATA / "breed_fact_overrides.json"

SUPPLEMENTAL_BREED_NAMES = {
    ("Chó", "Affenpinscher"),
    ("Chó", "Bearded Collie"),
    ("Mèo", "Arabian Mau"),
    ("Mèo", "Khao Manee"),
}


def normalize(text: str) -> str:
    text = text.replace("đ", "d").replace("Đ", "D")
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()


def slug(text: str) -> str:
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", normalize(text))).strip("-")


def breed_age_group(breed: dict) -> dict:
    if breed["species"] in ("CAT", "Mèo"):
        return {
            "lifeStageIds": ["cat_growth", "cat_young_adult", "cat_mature_adult", "cat_senior"],
            "ageBands": [
                {"stageId": "cat_growth", "fromMonths": 0, "toMonthsExclusive": 12},
                {"stageId": "cat_young_adult", "fromYears": 1, "toYearsExclusive": 7},
                {"stageId": "cat_mature_adult", "fromYears": 7, "toYearsInclusive": 10},
                {"stageId": "cat_senior", "fromYearsExclusive": 10},
            ],
            "ageBasis": "AAHA/AAFP feline life-stage categories; age stage does not by itself prescribe a different diet.",
        }

    size = normalize(breed.get("sizeInProjectCatalog") or breed.get("size") or "")
    if not size:
        return {
            "lifeStageIds": ["dog_growth", "dog_adult_maintenance", "dog_senior_individualized"],
            "growthToAdultTransitionApproxMonths": None,
            "sizeGroupUsed": "unclassified_size_needs_verification",
            "ageBands": [
                {
                    "stageId": "dog_growth",
                    "fromMonths": 0,
                    "toMonthsApprox": None,
                    "transitionNote": "Thiếu phân loại kích thước đã xác minh; không ước tính tuổi trưởng thành riêng cho giống.",
                },
                {
                    "stageId": "dog_adult_maintenance",
                    "fromAge": "Sau khi xác nhận trưởng thành theo cá thể và tư vấn thú y.",
                },
                {
                    "stageId": "dog_senior_individualized",
                    "fromAge": "Đánh giá cá thể hóa cùng bác sĩ thú y; không có tuổi bắt đầu senior thống nhất.",
                },
            ],
            "ageBasis": "Thiếu kích thước/tuổi trưởng thành đáng tin cậy trong hồ sơ; áp dụng giai đoạn theo nhãn và bác sĩ thú y.",
        }
    if any(term in size for term in ("large", "lon", "great")):
        maturity = {"fromMonths": 18, "toMonths": 24}
        maturity_group = "large_or_giant"
    else:
        maturity = {"fromMonths": 10, "toMonths": 12}
        maturity_group = "small_or_medium"
    return {
        "lifeStageIds": ["dog_growth", "dog_adult_maintenance", "dog_senior_individualized"],
        "growthToAdultTransitionApproxMonths": maturity,
        "sizeGroupUsed": maturity_group,
        "ageBands": [
            {
                "stageId": "dog_growth",
                "fromMonths": 0,
                "toMonthsApprox": maturity["toMonths"],
                "transitionNote": "Mốc trưởng thành thay đổi theo giống và cá thể; khoảng tuổi chỉ là ước lượng theo nhóm kích thước.",
            },
            {
                "stageId": "dog_adult_maintenance",
                "fromMonthsApprox": maturity["fromMonths"],
                "toAge": "Trước khi xuất hiện nhu cầu/chuyển biến liên quan tuổi già; không có mốc cố định cho mọi chó.",
            },
            {
                "stageId": "dog_senior_individualized",
                "fromAge": "Đánh giá cá thể hóa cùng bác sĩ thú y; không có tuổi bắt đầu senior thống nhất trong hồ sơ giống này.",
            },
        ],
        "ageBasis": "Ước lượng trưởng thành chó con theo nhóm kích thước dựa trên VCA; tuổi senior cần cá thể hóa. Kích thước trong catalog dự án chưa được xác minh độc lập.",
    }


def breed_id(species: str, name: str) -> str:
    species_code = "dog" if species == "Chó" else "cat"
    return f"{species_code}-{slug(name)}"


def build_breed_records() -> tuple[list[dict], dict[str, int], dict[str, bool]]:
    source = json.loads(BREED_SOURCE_PATH.read_text(encoding="utf-8"))
    legacy = json.loads(LEGACY_BREED_INDEX_PATH.read_text(encoding="utf-8"))
    fact_overrides = json.loads(BREED_FACT_OVERRIDES_PATH.read_text(encoding="utf-8"))
    legacy_breeds = legacy.get("breeds", [])
    breed_rows = [dict(item) for item in source["breeds"]]
    included_names = {(item["species"], item["breed_name"]) for item in breed_rows}
    legacy_names = {
        (item.get("species") or item.get("species_code"), item.get("breed_name"))
        for item in legacy_breeds
    }
    if not SUPPLEMENTAL_BREED_NAMES.issubset(legacy_names):
        missing = sorted(SUPPLEMENTAL_BREED_NAMES - legacy_names)
        raise ValueError(f"Supplemental breed names are missing from the internal index: {missing}")
    if SUPPLEMENTAL_BREED_NAMES & included_names:
        raise ValueError("A supplemental breed name already exists in the source catalog.")

    for species, name in sorted(SUPPLEMENTAL_BREED_NAMES):
        breed_rows.append(
            {
                "species": species,
                "breed_name": name,
                "breed_name_en": name,
                "origin_country": None,
                "origin_region": None,
                "climate": None,
                "suitable_environment": None,
                "exercise_level": None,
                "heat_tolerance": None,
                "cold_tolerance": None,
                "size": None,
                "adult_weight_kg": None,
                "lifespan_years": None,
                "suitable_home": None,
                "source_record_count": 0,
                "conflicts": {},
                "source_status": "name_only_from_unverified_legacy_index",
            }
        )

    fact_lookup = {
        (item["speciesLabel"], item["name"]): item
        for item in fact_overrides["profiles"]
    }
    for item in breed_rows:
        reference = fact_lookup.get((item["species"], item["breed_name"]))
        if not reference:
            continue
        if reference.get("sourcePath"):
            source_id = f"pdsa_{slug(item['breed_name'])}"
            reference["sourceIds"] = list(dict.fromkeys(reference.get("sourceIds", []) + [source_id]))
            reference.setdefault("notes", []).append(
                "PDSA cho các thông tin kích thước/cân nặng/tuổi thọ/vận động được ghi ở trên; trang này không xác minh xuất xứ. Tên giống có phân nhóm được giữ đúng như chú thích nguồn."
            )
        for field, value in reference.get("values", {}).items():
            if field not in {
                "size",
                "adult_weight_kg",
                "lifespan_years",
                "origin_country",
                "origin_region",
                "exercise_level",
                "daily_exercise",
            }:
                raise ValueError(f"Unsupported breed fact field: {field}")
            item[field] = value
        item["breedFactReference"] = reference

    for item in breed_rows:
        item["ageStageGrouping"] = breed_age_group(item)
    counts = {
        species: sum(1 for item in breed_rows if item["species"] == species)
        for species in ("Chó", "Mèo")
    }
    if len(breed_rows) != 200 or len({(item["species"], item["breed_name"]) for item in breed_rows}) != 200:
        raise ValueError(f"Expected 200 unique species/breed profiles, got {len(breed_rows)}.")
    supplemental = {breed_id(species, name): True for species, name in SUPPLEMENTAL_BREED_NAMES}
    return breed_rows, counts, supplemental


def stage(
    stage_id: str,
    label: str,
    species: str,
    age_range: str,
    energy: str,
    food: str,
    nutrients: list[str],
    ingredients: list[str],
    notes: list[str],
) -> dict:
    return {
        "id": stage_id,
        "label": label,
        "species": species,
        "ageRange": age_range,
        "energyNeed": energy,
        "foodType": food,
        "nutrientPriorities": nutrients,
        "ingredientPriorities": ingredients,
        "notes": notes,
    }


GUIDANCE = {
    "energyMethod": {
        "unit": "qualitative_by_life_stage",
        "rule": "Không ấn định kcal/ ngày chỉ từ tên giống hoặc tuổi. Dùng kcal/100 g hoặc kcal/kg trên nhãn, bảng cho ăn của đúng SKU, cân nặng hiện tại, thể trạng, vận động và tư vấn thú y.",
        "adjustment": "Theo dõi cân nặng và body condition score; điều chỉnh khẩu phần theo xu hướng thể trạng và hoạt động.",
        "foodFormNote": "Thức ăn khô hay ướt đều có thể phù hợp nếu là thức ăn hoàn chỉnh cho đúng loài/giai đoạn; so lượng theo năng lượng và hướng dẫn trên nhãn, không so theo thể tích.",
    },
    "principles": [
        "Ưu tiên tuyên bố thức ăn hoàn chỉnh và cân bằng cho đúng loài, giai đoạn sống và tình trạng sức khỏe; thứ tự thành phần trên nhãn không tự chứng minh chất lượng hay khả năng tiêu hóa.",
        "Không chuyển trực tiếp mức protein/năng lượng giữa sản phẩm khô và ướt nếu chưa xét độ ẩm, năng lượng và cùng cơ sở tính.",
        "Không tự bổ sung calcium, vitamin hoặc khoáng cho khẩu phần hoàn chỉnh, đặc biệt trong giai đoạn tăng trưởng, nếu bác sĩ thú y chưa chỉ định.",
        "Dị ứng thức ăn không thể chẩn đoán chỉ từ danh sách thành phần; cần bác sĩ thú y đánh giá và khẩu phần loại trừ có kiểm soát khi phù hợp.",
    ],
    "stages": [
        stage(
            "dog_growth",
            "Chó con · tăng trưởng",
            "DOG",
            "Từ cai sữa đến trưởng thành; chó nhỏ/vừa thường khoảng 10–12 tháng, chó lớn/khổng lồ có thể khoảng 18–24 tháng.",
            "Nhu cầu năng lượng và dưỡng chất trên mỗi kg thường cao hơn chó trưởng thành; tăng trưởng cần đều, tránh cho ăn dư để thúc tăng nhanh.",
            "Thức ăn hoàn chỉnh ghi cho tăng trưởng/chó con; với chó lớn hoặc khổng lồ, chọn công thức ghi rõ phù hợp tăng trưởng giống lớn. Hạt hoặc ướt đều được nếu nhãn đáp ứng.",
            ["Protein và amino acid thiết yếu", "Chất béo và acid béo thiết yếu", "Calcium và phosphorus cân đối, đúng hồ sơ tăng trưởng", "Vitamin và khoáng chất đầy đủ"],
            ["Nguồn protein dễ tiêu được khai báo rõ", "Nguồn chất béo và acid béo thiết yếu", "Nguồn calcium/phosphorus được cân đối trong công thức hoàn chỉnh"],
            [
                "Không cần tối đa hóa tốc độ tăng trưởng; khẩu phần dư năng lượng có thể gây tăng cân quá mức.",
                "Chó lớn/khổng lồ nhạy với cân bằng năng lượng và calcium trong giai đoạn tăng trưởng; không tự thêm calcium.",
            ],
        ),
        stage(
            "dog_adult_maintenance",
            "Chó trưởng thành · duy trì",
            "DOG",
            "Sau khi trưởng thành theo kích thước/giống đến khi bác sĩ thú y xác định cần điều chỉnh theo tuổi hoặc sức khỏe.",
            "Mức duy trì biến thiên theo vận động, triệt sản, khí hậu và thể trạng; chó làm việc/vận động nhiều có thể cần nhiều năng lượng hơn chó ít hoạt động.",
            "Thức ăn hoàn chỉnh cho chó trưởng thành/maintenance; chọn lượng theo bảng cho ăn của đúng SKU và theo dõi thể trạng.",
            ["Protein đủ amino acid thiết yếu", "Chất béo và acid béo thiết yếu", "Vitamin/khoáng chất và tỷ lệ dinh dưỡng cân bằng"],
            ["Thành phần được khai báo trên nhãn và phù hợp với tiền sử dung nạp cá thể", "Nguồn protein và chất béo trong thức ăn hoàn chỉnh"],
            ["Không mặc định mọi chó trưởng thành cùng mức kcal.", "Dòng công thức theo kích cỡ là chỉ định nhà sản xuất nếu ghi trên nhãn, không phải chuẩn riêng của mọi giống cùng cỡ."],
        ),
        stage(
            "dog_senior_individualized",
            "Chó lớn tuổi · đánh giá cá thể",
            "DOG",
            "Không có mốc tuổi bắt đầu duy nhất; đánh giá theo sức khỏe, thể trạng, vận động và tuổi thọ/đặc điểm cá thể với bác sĩ thú y.",
            "Có thể giảm khi ít vận động hoặc thừa cân, nhưng không tự động giảm ở mọi chó lớn tuổi; bệnh lý hoặc mất khối cơ có thể làm nhu cầu khác đi.",
            "Duy trì thức ăn hoàn chỉnh phù hợp; chỉ chuyển sang công thức senior hoặc chế độ điều trị sau khi đối chiếu tình trạng và nhãn với bác sĩ thú y.",
            ["Protein chất lượng phù hợp để duy trì khối cơ", "Năng lượng điều chỉnh theo body condition", "Vi chất cân đối; điều chỉnh riêng nếu chẩn đoán bệnh"],
            ["Không có một nguyên liệu đơn lẻ bắt buộc cho mọi chó senior; ưu tiên khẩu phần hoàn chỉnh và dung nạp tốt."],
            ["AAFCO không tạo profile riêng theo tên giống hoặc một ngưỡng tuổi senior áp dụng chung.", "Không hạn chế protein hoặc khoáng chất tùy tiện khi chưa có chẩn đoán."],
        ),
        stage(
            "dog_reproduction",
            "Chó mang thai/cho bú",
            "DOG",
            "Trong thai kỳ và thời kỳ tiết sữa; thời điểm, khẩu phần và chuyển đổi cần bác sĩ thú y hướng dẫn.",
            "Nhu cầu thay đổi theo giai đoạn thai kỳ, số con và lượng sữa; đặc biệt tăng trong tiết sữa.",
            "Thức ăn ghi cho tăng trưởng/sinh sản hoặc all life stages phù hợp theo nhãn và tư vấn thú y.",
            ["Năng lượng và protein phù hợp giai đoạn", "Calcium/phosphorus và vi chất cân đối trong thức ăn hoàn chỉnh", "Nước sạch luôn sẵn có khi cho bú"],
            ["Thức ăn hoàn chỉnh được ghi rõ cho tăng trưởng/sinh sản hoặc mọi giai đoạn sống."],
            ["Không tự bổ sung calcium trong thai kỳ nếu bác sĩ thú y chưa chỉ định."],
        ),
        stage(
            "cat_growth",
            "Mèo con · tăng trưởng",
            "CAT",
            "0 đến dưới 1 tuổi theo khung giai đoạn mèo AAHA/AAFP; nhu cầu bú/cai sữa cần chăm sóc theo tuổi và bác sĩ thú y.",
            "Nhu cầu năng lượng và dưỡng chất cao cho tăng trưởng; chia bữa theo hướng dẫn và tránh nuôi tăng cân quá nhanh.",
            "Thức ăn hoàn chỉnh cho mèo con/growth hoặc all life stages ghi phù hợp; thức ăn khô hay ướt đều được nếu đạt tuyên bố dinh dưỡng.",
            ["Protein và amino acid thiết yếu", "Chất béo và acid béo thiết yếu", "Taurine", "Vitamin A dạng phù hợp cho mèo", "Calcium/phosphorus cân đối"],
            ["Nguồn protein phù hợp công thức cho mèo con", "Taurine và vitamin/khoáng chất được bảo đảm trong thức ăn hoàn chỉnh"],
            ["Không tự bổ sung vitamin/khoáng cho thức ăn hoàn chỉnh nếu bác sĩ thú y chưa chỉ định."],
        ),
        stage(
            "cat_young_adult",
            "Mèo trưởng thành trẻ",
            "CAT",
            "1 đến dưới 7 tuổi theo AAHA/AAFP.",
            "Nhu cầu duy trì; điều chỉnh theo vận động, triệt sản, môi trường trong nhà/ngoài trời và thể trạng.",
            "Thức ăn hoàn chỉnh cho mèo trưởng thành/maintenance; khớp lượng ăn với năng lượng của đúng SKU.",
            ["Protein và amino acid thiết yếu", "Taurine", "Vitamin A dạng phù hợp cho mèo", "Acid arachidonic và acid béo thiết yếu", "Khoáng/vitamin cân bằng"],
            ["Nguồn protein khai báo rõ; taurine và vi chất được bảo đảm bởi công thức hoàn chỉnh."],
            ["Mèo cần dưỡng chất đặc thù loài; không dùng thức ăn chó làm khẩu phần chính cho mèo."],
        ),
        stage(
            "cat_mature_adult",
            "Mèo trưởng thành giai đoạn giữa",
            "CAT",
            "7 đến 10 tuổi theo AAHA/AAFP.",
            "Theo dõi thay đổi chuyển hóa và thể trạng; không mặc định phải giảm hay tăng kcal chỉ vì tuổi.",
            "Thức ăn hoàn chỉnh phù hợp cho mèo và tình trạng cá thể; điều chỉnh nếu khám phát hiện vấn đề sức khỏe.",
            ["Protein đủ và phù hợp duy trì khối cơ", "Taurine", "Vitamin A dạng phù hợp cho mèo", "Năng lượng và khoáng chất được điều chỉnh theo đánh giá thú y"],
            ["Không có một thành phần đơn lẻ áp dụng cho mọi mèo giai đoạn này; ưu tiên đủ chất, dung nạp và nhãn minh bạch."],
            ["Khám định kỳ giúp phát hiện bệnh có thể làm thay đổi nhu cầu dinh dưỡng."],
        ),
        stage(
            "cat_senior",
            "Mèo cao tuổi",
            "CAT",
            "Trên 10 tuổi theo AAHA/AAFP; bệnh lý và khác biệt từng cá thể có thể đòi hỏi đánh giá sớm hơn.",
            "Biến thiên; theo dõi cân nặng, khẩu vị và khối cơ. Không hạn chế protein/khoáng chất chỉ theo tuổi nếu chưa có chỉ định.",
            "Thức ăn hoàn chỉnh cho mèo; công thức senior hoặc điều trị chỉ chọn dựa trên tình trạng sức khỏe và tư vấn thú y.",
            ["Protein và năng lượng theo khối cơ/thể trạng", "Taurine", "Vitamin A dạng phù hợp cho mèo", "Điều chỉnh dưỡng chất khi có chẩn đoán"],
            ["Không có một nguyên liệu bắt buộc cho mọi mèo cao tuổi; chọn theo hồ sơ dinh dưỡng và bệnh lý."],
            ["Cân nặng giảm, bỏ ăn hoặc thay đổi uống/tiểu cần được bác sĩ thú y đánh giá."],
        ),
        stage(
            "cat_reproduction",
            "Mèo mang thai/cho bú",
            "CAT",
            "Trong thai kỳ và thời kỳ tiết sữa; theo dõi với bác sĩ thú y.",
            "Nhu cầu tăng theo thai kỳ và đặc biệt khi nuôi con; lượng ăn và nước cần được theo dõi sát.",
            "Thức ăn cho tăng trưởng/sinh sản hoặc all life stages phù hợp theo tuyên bố nhãn và tư vấn thú y.",
            ["Năng lượng và protein cho sinh sản/tiết sữa", "Taurine", "Vitamin A dạng phù hợp cho mèo", "Khoáng/vitamin cân đối"],
            ["Thức ăn hoàn chỉnh được ghi phù hợp cho tăng trưởng/sinh sản hoặc mọi giai đoạn sống."],
            ["Không tự bổ sung calcium/vitamin nếu chưa được bác sĩ thú y hướng dẫn."],
        ),
    ],
    "sources": [
        {
            "label": "AAFCO · Selecting the Right Pet Food",
            "url": "https://www.aafco.org/consumers/understanding-pet-food/selecting-the-right-pet-food/",
            "supports": "Chọn theo loài, giai đoạn sống, tình trạng; nhu cầu và feeding directions khác nhau theo giai đoạn.",
        },
        {
            "label": "AAFCO · Reading Pet Food Labels",
            "url": "https://www.aafco.org/consumers/understanding-pet-food/reading-labels/",
            "supports": "Tuyên bố nutritional adequacy, loài, life stages và cách hiểu thức ăn complete and balanced.",
        },
        {
            "label": "VCA Animal Hospitals · Feeding Growing Puppies",
            "url": "https://vcahospitals.com/know-your-pet/feeding-growing-puppies",
            "supports": "Tăng trưởng nhỏ/vừa thường 10–12 tháng, lớn/khổng lồ đến 18–24 tháng; protein, béo, calcium và kiểm soát tăng trưởng.",
        },
        {
            "label": "VCA Animal Hospitals · Feeding Growing Kittens",
            "url": "https://vcahospitals.com/know-your-pet/feeding-growing-kittens",
            "supports": "Mèo con trưởng thành khoảng 10–12 tháng; dinh dưỡng growth và kiểm soát tốc độ tăng trưởng.",
        },
        {
            "label": "AAHA/AAFP · 2021 Feline Life Stage Guidelines",
            "url": "https://www.aaha.org/resources/2021-aaha-aafp-feline-life-stage-guidelines/",
            "supports": "Mèo con 0–1; young adult 1–6; mature 7–10; senior trên 10 tuổi.",
        },
        {
            "label": "U.S. FDA · Complete and Balanced Pet Food",
            "url": "https://www.fda.gov/animal-veterinary/animal-health-literacy/complete-and-balanced-pet-food",
            "supports": "Profile tăng trưởng/sinh sản và adult maintenance; khác biệt nhu cầu, nhãn và cơ sở so sánh dinh dưỡng.",
        },
    ],
}

BREED_SOURCES = [
    {
        "label": "AAFCO · Selecting the Right Pet Food",
        "url": "https://www.aafco.org/consumers/understanding-pet-food/selecting-the-right-pet-food/",
        "supports": "Chọn thức ăn theo loài, giai đoạn sống, tình trạng và hướng dẫn nhãn.",
    },
    {
        "label": "AAFCO · Reading Pet Food Labels",
        "url": "https://www.aafco.org/consumers/understanding-pet-food/reading-labels/",
        "supports": "Tuyên bố complete and balanced và giai đoạn sống; không có mức riêng theo tên giống.",
    },
    {
        "label": "VCA · Feeding Growing Puppies",
        "url": "https://vcahospitals.com/know-your-pet/feeding-growing-puppies",
        "supports": "Tăng trưởng chó con theo nhóm kích thước; nhu cầu và lượng ăn cần được cá thể hóa.",
    },
    {
        "label": "VCA · Feeding Growing Kittens",
        "url": "https://vcahospitals.com/know-your-pet/feeding-growing-kittens",
        "supports": "Tăng trưởng mèo con thường đến trưởng thành khoảng 10–12 tháng; tránh tăng trưởng quá nhanh.",
    },
    {
        "label": "AAHA/AAFP · 2021 Feline Life Stage Guidelines",
        "url": "https://www.aaha.org/resources/2021-aaha-aafp-feline-life-stage-guidelines/",
        "supports": "Mốc giai đoạn mèo con, trưởng thành trẻ, trưởng thành giữa và senior.",
    },
    {
        "label": "U.S. FDA · Complete and Balanced Pet Food",
        "url": "https://www.fda.gov/animal-veterinary/animal-health-literacy/complete-and-balanced-pet-food",
        "supports": "Tuyên bố dinh dưỡng, giai đoạn sống và cách so sánh dưỡng chất có xét độ ẩm.",
    },
]

MAINE_COON_SOURCES = [
    {
        "label": "GCCF · Maine Coon",
        "url": "https://www.gccfcats.org/getting-a-cat/choosing/cat-breeds/maine-coon/",
        "supports": "Giống lớn; mèo đực có thể nặng tới 18–20 lb; trưởng thành chậm, có thể đến khoảng bốn năm.",
    },
    {
        "label": "Cornell Feline Health Center · Hypertrophic Cardiomyopathy",
        "url": "https://www.vet.cornell.edu/departments-centers-and-institutes/cornell-feline-health-center/health-information/feline-health-topics/hypertrophic-cardiomyopathy",
        "supports": "Maine Coon thuộc các giống có ghi nhận khuynh hướng HCM; chẩn đoán cần bác sĩ thú y.",
    },
]


def breed_stage_ids(species: str) -> list[str]:
    if species == "Chó":
        return ["dog_growth", "dog_adult_maintenance", "dog_senior_individualized", "dog_reproduction"]
    return ["cat_growth", "cat_young_adult", "cat_mature_adult", "cat_senior", "cat_reproduction"]


def nutrition_dossier(
    breed: dict,
    stage_lookup: dict[str, dict],
    supplementary: bool,
) -> dict:
    species = breed["species"]
    stage_ids = breed_stage_ids(species)
    age_grouping = breed["ageStageGrouping"]
    fact_reference = breed.get("breedFactReference", {})
    known_name = breed["breed_name"] == "Maine Coon" and species == "Mèo"
    breed_specific_facts = []
    if known_name:
        breed_specific_facts = [
            {
                "fact": "GCCF mô tả Maine Coon trưởng thành chậm, có thể mất đến khoảng bốn năm.",
                "sourceIds": ["gccf_maine_coon"],
                "status": "source_checked",
                "feedingImplication": "Mốc đạt kích thước cơ thể không tự động kéo dài giai đoạn thức ăn mèo con đến bốn tuổi; chọn theo nutritional adequacy statement và trao đổi với bác sĩ thú y nếu cân nhắc kéo dài.",
            },
            {
                "fact": "GCCF ghi mèo đực có thể nặng tới khoảng 18–20 lb; đây không phải cân nặng mục tiêu cho mọi cá thể và không cung cấp khoảng tương ứng cho mèo cái.",
                "sourceIds": ["gccf_maine_coon"],
                "status": "source_checked",
                "feedingImplication": "Không dùng cân nặng trên để suy ra kcal hoặc khẩu phần; đánh giá cân nặng lý tưởng và body condition của từng mèo.",
            },
            {
                "fact": "Cornell Feline Health Center liệt kê Maine Coon trong nhóm giống có khuynh hướng HCM được ghi nhận.",
                "sourceIds": ["cornell_hcm"],
                "status": "source_checked",
                "feedingImplication": "Đây là lưu ý sức khỏe để trao đổi với bác sĩ thú y, không phải căn cứ tự bổ sung taurine, omega-3, thuốc hoặc chọn chế độ điều trị.",
            },
        ]
    elif fact_reference.get("notes"):
        breed_specific_facts = [
            {
                "fact": note,
                "sourceIds": fact_reference.get("sourceIds", []),
                "status": fact_reference.get("status"),
                "feedingImplication": "Dùng như thông tin nhận diện/tham khảo giống; không suy ra khẩu phần, kcal hay điều trị từ dữ kiện này.",
            }
            for note in fact_reference["notes"]
        ]
    else:
        breed_specific_facts = [
            {
                "fact": None,
                "status": "not_independently_verified",
                "note": "Không gán đặc điểm y khoa, tuổi trưởng thành kéo dài hoặc yêu cầu dinh dưỡng riêng cho giống này khi chưa có nguồn đáng tin cậy đã đối chiếu.",
            }
        ]

    nutrition_stages = []
    age_bands = {item["stageId"]: item for item in age_grouping["ageBands"]}
    stage_source_ids = {
        "dog_growth": ["aafco_selecting_food", "vcahospitals_puppies", "fda_complete_balanced", "fediaf_nutritional_guidelines"],
        "dog_adult_maintenance": ["aafco_selecting_food", "aafco_reading_labels", "fda_complete_balanced", "fediaf_nutritional_guidelines"],
        "dog_senior_individualized": ["aafco_selecting_food", "fda_complete_balanced", "fediaf_nutritional_guidelines"],
        "dog_reproduction": ["aafco_reading_labels", "fda_complete_balanced", "fediaf_nutritional_guidelines"],
        "cat_growth": ["aafco_selecting_food", "vcahospitals_kittens", "aaha_aafp_cats", "fda_complete_balanced", "fediaf_nutritional_guidelines"],
        "cat_young_adult": ["aaha_aafp_cats", "aafco_reading_labels", "fda_complete_balanced", "fediaf_nutritional_guidelines"],
        "cat_mature_adult": ["aaha_aafp_cats", "aafco_reading_labels", "fda_complete_balanced", "fediaf_nutritional_guidelines"],
        "cat_senior": ["aaha_aafp_cats", "aafco_selecting_food", "fda_complete_balanced", "fediaf_nutritional_guidelines"],
        "cat_reproduction": ["aafco_reading_labels", "fda_complete_balanced", "fediaf_nutritional_guidelines"],
    }
    for stage_id in stage_ids:
        nutrition_stages.append(
            {
                "ageBand": age_bands.get(stage_id),
                "nutritionGuidance": stage_lookup[stage_id],
                "sourceIds": stage_source_ids[stage_id],
            }
        )

    unverified_claims = []
    if known_name:
        unverified_claims = [
            "Mức protein/chất béo/mineral khuyến nghị riêng Maine Coon trong tài liệu mẫu chưa có nguồn chuẩn được đối chiếu; không chuyển thành ngưỡng dinh dưỡng chính thức.",
            "Các bảng kcal/ngày hoặc gram thức ăn theo cân nặng trong tài liệu mẫu không áp dụng cho mọi cá thể/SKU; thiếu dữ liệu năng lượng sản phẩm và đánh giá thể trạng nên không đưa vào khuyến nghị.",
            "Khẳng định kéo dài thức ăn mèo con đến 15–18 tháng, giảm khẩu phần cố định sau triệt sản, hoặc bổ sung glucosamine/omega-3 cho mọi Maine Coon cần nguồn và đánh giá cá thể; không trình bày như quy tắc bắt buộc.",
        ]

    size_note = (
        "Có một số dữ kiện cơ bản đối chiếu được nguồn; các trường không có nguồn vẫn để trống hoặc gắn trạng thái chưa xác minh."
        if fact_reference
        else "Bản ghi bổ sung chỉ có tên loài/giống từ chỉ mục nội bộ chưa xác minh; các thuộc tính khác để trống."
        if supplementary
        else "Đặc điểm giống lấy từ catalog nội bộ dự án, chưa xác minh độc lập; xem conflicts nếu có sai khác."
    )
    overview = {
        "breedName": breed["breed_name"],
        "species": species,
        "originCountry": breed.get("origin_country"),
        "originRegion": breed.get("origin_region"),
        "size": breed.get("size"),
        "adultWeightKg": breed.get("adult_weight_kg"),
        "lifespanYears": breed.get("lifespan_years"),
        "exerciseLevel": breed.get("exercise_level"),
        "dailyExercise": breed.get("daily_exercise"),
        "maturityEstimate": (
            "Trưởng thành chậm, có thể đến khoảng 4 năm theo GCCF; điều này không xác định riêng tuổi chuyển thức ăn."
            if known_name
            else age_grouping.get("growthToAdultTransitionApproxMonths")
            or age_grouping.get("ageBands")
        ),
        "dataStatus": fact_reference.get(
            "status",
            "supplemental_name_only_unverified"
            if supplementary
            else "project_reference_unverified",
        ),
        "sourceNote": size_note,
        "conflicts": breed.get("conflicts", {}),
        "breedFactStatus": fact_reference.get("status", "project_reference_unverified"),
        "breedFactSourceIds": fact_reference.get("sourceIds", []),
        "breedFactNotes": fact_reference.get("notes", []),
        "breedSpecificFacts": breed_specific_facts,
    }

    checklists = [
        "Xác định đúng loài và life stage trên nhãn; ưu tiên tuyên bố complete and balanced phù hợp.",
        "Dùng kcal và bảng khẩu phần trên đúng SKU làm điểm khởi đầu; điều chỉnh theo cân nặng, body condition, hoạt động và theo dõi thực tế.",
        "Chọn dạng khô/ướt theo mức năng lượng, khả năng ăn/uống và nhu cầu cá thể; không so gam/cốc trực tiếp khi mật độ năng lượng khác.",
        "Đối chiếu danh sách thành phần với dị ứng đã được bác sĩ thú y xác định; danh sách thành phần tự nó không chẩn đoán dị ứng.",
        "Không tự bổ sung vitamin, calcium, taurine, dầu hoặc joint supplements cho thức ăn hoàn chỉnh nếu chưa có tư vấn thú y.",
    ]
    return {
        "templateVersion": 1,
        "partI_overview": overview,
        "partII_nutritionPrinciples": {
            "aafcoFediafBreedSpecificThreshold": False,
            "rule": "Không có profile AAFCO/FEDIAF độc lập theo tên giống trong dữ liệu này. Chọn theo loài, giai đoạn sống, tuyên bố nhãn và tình trạng sức khỏe.",
            "energy": GUIDANCE["energyMethod"],
            "speciesCriticalNutrients": (
                ["Protein/amino acid thiết yếu", "Taurine", "Vitamin A dạng phù hợp cho mèo", "Acid béo thiết yếu", "Nước"]
                if species == "Mèo"
                else ["Protein/amino acid thiết yếu", "Acid béo thiết yếu", "Năng lượng phù hợp hoạt động", "Vitamin và khoáng cân bằng", "Nước"]
            ),
            "stagePrinciples": GUIDANCE["principles"],
        },
        "partIII_lifeStageNutrition": nutrition_stages,
        "partIV_feedingAndIngredientChecklist": {
            "dailyCalories": {
                "value": None,
                "reason": "Không đủ dữ liệu cá thể về cân nặng lý tưởng, body condition, triệt sản, vận động và kcal của SKU.",
                "method": GUIDANCE["energyMethod"]["rule"],
            },
            "mealFrequency": "Theo hướng dẫn sản phẩm và sinh hoạt cá thể; không ấn định số bữa bắt buộc theo giống.",
            "foodTypes": ["Thức ăn khô hoàn chỉnh phù hợp loài/life stage", "Thức ăn ướt hoàn chỉnh phù hợp loài/life stage"],
            "importantNutrientSources": (
                ["Nguồn cung cấp amino acid thiết yếu trong công thức hoàn chỉnh", "Taurine", "Vitamin A phù hợp cho mèo", "Acid béo thiết yếu"]
                if species == "Mèo"
                else ["Nguồn cung cấp amino acid thiết yếu trong công thức hoàn chỉnh", "Acid béo thiết yếu", "Calcium/phosphorus cân bằng khi tăng trưởng"]
            ),
            "ingredientInterpretation": "Không có một nguyên liệu cụ thể bắt buộc đứng đầu cho mọi cá thể giống này. Đánh giá công thức, adequacy statement, độ dung nạp, dị ứng được xác định và nhãn sản phẩm; thứ tự thành phần không tự chứng minh chất lượng.",
            "checklist": checklists,
            "breedSpecificNotes": breed_specific_facts,
        },
        "partV_quickSummary": {
            "lifeStages": [item["nutritionGuidance"]["label"] for item in nutrition_stages],
            "energyRule": "Không có kcal riêng cho giống; điều chỉnh theo cá thể, nhãn và body condition.",
            "keyNutrients": (
                ["Taurine", "Vitamin A phù hợp cho mèo", "Amino acid và acid béo thiết yếu"]
                if species == "Mèo"
                else ["Amino acid thiết yếu", "Acid béo thiết yếu", "Cân bằng calcium/phosphorus trong tăng trưởng"]
            ),
            "breedSpecificStandard": "Không có ngưỡng AAFCO/FEDIAF riêng theo giống được xác minh.",
        },
        "partVI_conclusion": "Áp dụng chuẩn theo loài và giai đoạn sống; điều chỉnh lượng ăn theo thể trạng cá thể. Không xem size, tuổi trưởng thành hay tên giống là chỉ định tự động về kcal, thành phần đơn lẻ hoặc thức ăn điều trị.",
        "unverifiedClaimsNotAdoptedFromSample": unverified_claims,
        "sources": ["aafco_selecting_food", "aafco_reading_labels", "vcahospitals_puppies", "vcahospitals_kittens", "aaha_aafp_cats", "fda_complete_balanced", "fediaf_nutritional_guidelines"]
        + (["gccf_maine_coon", "cornell_hcm"] if known_name else []),
    }


def ingredient_watchlist(product: dict, source_product: dict) -> list[dict]:
    raw_list = source_product.get("specs", {}).get("ingredient_list") or ""
    if normalize(raw_list).startswith("khong tim thay"):
        return []

    categories = {
        "poultry": ("gia cam",),
        "wheat_or_gluten": ("lua mi", "bot mi"),
        "corn": ("ngo",),
        "soy": ("dau nanh",),
        "fish": ("dau ca",),
        "unspecified_animal_fat_or_protein": ("mo dong vat", "protein dong vat", "chat beo dong vat"),
    }
    matches: dict[str, list[str]] = {}
    for ingredient in re.split(r"[,;]", raw_list):
        ingredient = ingredient.strip()
        folded = normalize(ingredient)
        for category, terms in categories.items():
            if any(term in folded for term in terms):
                matches.setdefault(category, []).append(ingredient)
    return [
        {"category": category, "matchedIngredientTerms": values}
        for category, values in matches.items()
    ]


def main() -> None:
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    original_products = json.loads(PRODUCT_SOURCE_PATH.read_text(encoding="utf-8"))["products"]
    originals_by_id = {product["id"]: product for product in original_products}
    fact_overrides = json.loads(BREED_FACT_OVERRIDES_PATH.read_text(encoding="utf-8"))
    breed_rows, breed_counts, supplemental_ids = build_breed_records()
    stage_lookup = {item["id"]: item for item in GUIDANCE["stages"]}

    catalog["title"] = "Danh mục sản phẩm thức ăn chó mèo, 70 trường, liên kết giống và thành phần cần lưu ý"
    catalog["sourceFiles"]["breedNutritionDossiers"] = "HTML/data/pet_breed_nutrition_profiles_200.json"
    catalog["sourceFiles"]["breedFactOverrides"] = "HTML/data/breed_fact_overrides.json"
    catalog["lifeStageGuidance"] = GUIDANCE
    catalog["breeds"] = [
        {
            "id": breed_id(breed["species"], breed["breed_name"]),
            "species": "DOG" if breed["species"] == "Chó" else "CAT",
            "speciesLabel": breed["species"],
            "name": breed["breed_name"],
            "nameEn": breed.get("breed_name_en"),
            "sizeInProjectCatalog": breed.get("size"),
            "adultWeightKgInProjectCatalog": breed.get("adult_weight_kg"),
            "lifespanYearsInProjectCatalog": breed.get("lifespan_years"),
            "dailyExercise": breed.get("daily_exercise"),
            "sourceRecordCount": breed.get("source_record_count", 0),
            "conflicts": breed.get("conflicts", {}),
            "dataSource": (
                "HTML/data/breed_fact_overrides.json"
                if breed.get("breedFactReference")
                else "unverified_legacy_index_name_only"
                if breed_id(breed["species"], breed["breed_name"]) in supplemental_ids
                else "app/modules/animals/breed_catalog.py"
            ),
            "verificationStatus": breed.get("breedFactReference", {}).get(
                "status",
                "supplemental_name_only_unverified"
                if breed_id(breed["species"], breed["breed_name"]) in supplemental_ids
                else "project_reference_unverified",
            ),
            "ageStageGrouping": breed["ageStageGrouping"],
        }
        for breed in breed_rows
    ]

    source_references = []
    source_details = [
        ("aafco_selecting_food", BREED_SOURCES[0]),
        ("aafco_reading_labels", BREED_SOURCES[1]),
        ("vcahospitals_puppies", BREED_SOURCES[2]),
        ("vcahospitals_kittens", BREED_SOURCES[3]),
        ("aaha_aafp_cats", BREED_SOURCES[4]),
        ("fda_complete_balanced", BREED_SOURCES[5]),
        (
            "fediaf_nutritional_guidelines",
            {
                "label": "FEDIAF · Nutritional Guidelines",
                "url": "https://europeanpetfood.org/self-regulation/nutritional-guidelines/",
                "supports": "Tài liệu hướng dẫn dinh dưỡng tham chiếu; cần đối chiếu phiên bản hiện hành và chú thích, không phải chứng nhận sản phẩm.",
            },
        ),
        ("gccf_maine_coon", MAINE_COON_SOURCES[0]),
        ("cornell_hcm", MAINE_COON_SOURCES[1]),
    ]
    source_references.extend(
        {"id": item["id"], **item}
        for item in fact_overrides["sourceReferences"]
    )
    for item in fact_overrides["profiles"]:
        if item.get("sourcePath"):
            source_id = f"pdsa_{slug(item['name'])}"
            source_references.append(
                {
                    "id": source_id,
                    "label": f"PDSA · {item['name']}",
                    "url": (
                        "https://www.pdsa.org.uk/pet-help-and-advice/looking-after-your-pet/"
                        f"puppies-dogs/{item['sourcePath']}"
                    ),
                    "supports": "Kích thước phân loại, cân nặng và tuổi thọ tham khảo; khuyến nghị vận động hằng ngày nếu trang giống có nêu.",
                }
            )
    for source_id, source in source_details:
        source_references.append({"id": source_id, **source})

    dossier_profiles = []
    for breed in breed_rows:
        profile_id = breed_id(breed["species"], breed["breed_name"])
        supplementary = profile_id in supplemental_ids
        dossier_profiles.append(
            {
                "id": profile_id,
                "species": "DOG" if breed["species"] == "Chó" else "CAT",
                "speciesLabel": breed["species"],
                "name": breed["breed_name"],
                "nameEn": breed.get("breed_name_en"),
                "sourceRecordCount": breed.get("source_record_count", 0),
                "verificationStatus": breed.get("breedFactReference", {}).get(
                    "status",
                    "supplemental_name_only_unverified"
                    if supplementary
                    else "project_reference_unverified",
                ),
                "profile": nutrition_dossier(breed, stage_lookup, supplementary),
            }
        )

    dossier_document = {
        "schemaVersion": 1,
        "title": "Hồ sơ dinh dưỡng tham khảo theo 200 giống chó và mèo",
        "generatedAt": catalog.get("generatedAt"),
        "status": "reference_not_veterinary_advice",
        "summary": {
            "profileCount": len(dossier_profiles),
            "dogProfileCount": breed_counts["Chó"],
            "catProfileCount": breed_counts["Mèo"],
            "supplementalNameOnlyCount": sum(
                profile["verificationStatus"] == "supplemental_name_only_unverified"
                for profile in dossier_profiles
            ),
            "profilesWithBreedSpecificSourceFacts": sum(
                bool(profile["profile"]["partI_overview"]["breedFactSourceIds"])
                for profile in dossier_profiles
            ),
            "breedSpecificAafcoFediafThresholdsVerified": 0,
        },
        "methodology": (
            "Mỗi hồ sơ dùng khung loài/giai đoạn sống và tài liệu tham chiếu; không suy ra ngưỡng "
            "dinh dưỡng, kcal hoặc khẩu phần theo giống nếu không có nguồn đã xác minh. Dữ kiện "
            "giống chỉ được thay thế khi có nguồn phù hợp; các trường chưa đối chiếu tiếp tục mang "
            "trạng thái tham khảo/chưa xác minh. Một số tên chung hoặc tên đồng nghĩa cần phân biệt."
        ),
        "lifeStageGuidance": GUIDANCE,
        "sourceReferences": source_references,
        "profiles": dossier_profiles,
    }
    BREED_DOSSIER_PATH.write_text(
        json.dumps(dossier_document, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    for product in catalog["products"]:
        source_product = originals_by_id[product["id"]]
        if product.get("lifeStages") == ["puppy"]:
            reference_stages = ["dog_growth"]
        elif product.get("lifeStages") == ["kitten"]:
            reference_stages = ["cat_growth"]
        elif product["species"] == "DOG":
            reference_stages = ["dog_adult_maintenance"]
        else:
            reference_stages = ["cat_young_adult", "cat_mature_adult"]
        product["ingredients"]["ingredientsToCheckAgainstKnownSensitivity"] = ingredient_watchlist(
            product, source_product
        )
        product["ageEnergyFoodGuidance"] = {
            "referenceStageIds": reference_stages,
            "requiresVeterinaryReviewForStages": [
                f"{product['species'].lower()}_senior_individualized"
                if product["species"] == "DOG"
                else "cat_senior"
            ]
            if "adult" in product.get("lifeStages", [])
            else [],
            "energyAssessment": "Dùng hướng dẫn khẩu phần và năng lượng trên nhãn đúng SKU; catalog không có dữ liệu xác minh kcal cho sản phẩm này.",
            "productLifeStageEvidence": product.get("lifeStages", []),
            "breedApplicabilityBasis": product["breedApplicability"]["basis"],
            "ingredientWatchlistMeaning": "Các thành phần cần đối chiếu với tiền sử nhạy cảm được trích từ danh sách ghi nhận; không phải dị nguyên đã chẩn đoán.",
        }

    catalog["summary"]["lifeStageGuidanceCount"] = len(GUIDANCE["stages"])
    catalog["summary"]["productsWithQuantitativeEnergyVerified"] = 0
    catalog["summary"]["breedProfileCount"] = len(breed_rows)
    catalog["summary"]["dogBreedProfileCount"] = breed_counts["Chó"]
    catalog["summary"]["catBreedProfileCount"] = breed_counts["Mèo"]
    catalog["summary"]["breedProfilesWithSpecificSources"] = sum(
        bool(breed.get("breedFactReference", {}).get("sourceIds"))
        for breed in breed_rows
    )
    catalog["limitations"] = [
        "Đây là hồ sơ đã có trong pet_product_specs.json, không phải danh mục toàn bộ thức ăn đang bán trên thị trường.",
        "Chỉ có 4 hồ sơ tham khảo; phần lớn trường nhãn/dinh dưỡng chưa xác minh và để null.",
        "Các nutrition_catalog_*_4000.json bị loại vì manifest đánh dấu generated_catalog; thông số và dữ liệu nguyên liệu trong đó chưa xác minh thương mại.",
        "Liên kết giống chỉ theo loài, không khẳng định phù hợp theo tên giống. Cần đối chiếu đúng giai đoạn sống và nhãn SKU.",
        "Thành phần cần lưu ý chỉ được trích từ danh sách thành phần đã ghi nhận; không phải tuyên bố dị nguyên hoặc chẩn đoán.",
        "Hồ sơ giống lấy từ catalog nội bộ; bản ghi trùng tên và sai khác được giữ trong conflicts, chưa xác minh độc lập.",
        "Tuổi trưởng thành theo kích thước chó chỉ là khoảng ước lượng; tuổi chuyển senior cần đánh giá thú y và không suy ra riêng từ tên giống.",
        "Hướng dẫn năng lượng là định tính theo giai đoạn; không tạo kcal hoặc khẩu phần chỉ từ tên giống.",
        "Các hồ sơ bổ sung và những trường giống đã đối chiếu chỉ có phạm vi nguồn một phần; trường thiếu nguồn vẫn không được suy đoán. Không sử dụng dữ liệu dinh dưỡng từ danh mục tạo tự động.",
    ]
    CATALOG_PATH.write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        f"Updated product/breed catalog: {len(catalog['breeds'])} breeds, "
        f"{len(catalog['products'])} products, {len(GUIDANCE['stages'])} age/feeding stages."
    )
    print(
        f"Updated nutrition dossier catalog: {len(dossier_profiles)} breed dossiers "
        f"({breed_counts['Chó']} dogs, {breed_counts['Mèo']} cats)."
    )


if __name__ == "__main__":
    main()
