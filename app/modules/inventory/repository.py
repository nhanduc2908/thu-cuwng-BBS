import sqlite3
from datetime import date, datetime
import math
from typing import Any

from app.modules.inventory.constants import INVENTORY_CATEGORIES
from app.modules.inventory.catalog_seed import (
    COMBO_COMPONENTS,
    COMBO_DEFINITIONS,
    catalog_products,
)
from app.modules.inventory.feeding_seed import AGE_RULES, FOOD_PROFILES


class InventoryRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def seed_feeding_profiles(self) -> tuple[int, int]:
        profiles_by_species: dict[str, list[dict[str, Any]]] = {}
        for profile in FOOD_PROFILES:
            profiles_by_species.setdefault(
                self._species_key(profile["species"]), []
            ).append(profile)

        items = self.connection.execute(
            "SELECT * FROM inventory_items WHERE is_demo = 1"
        ).fetchall()
        matched = 0
        with self.connection:
            for item in items:
                name = str(item["name"]).casefold()
                is_food = item["category"] == "FOOD" or any(
                    marker in name
                    for marker in ("thức ăn", "cỏ khô", "hay ", "pet food")
                )
                if not is_food:
                    continue
                item_species = {
                    self._species_key(part.strip())
                    for part in str(item["target_species"]).split(",")
                    if part.strip()
                }
                if not item_species:
                    continue

                exact_matches = [
                    profile
                    for species in item_species
                    for profile in profiles_by_species.get(species, [])
                    if any(
                        str(term).strip().casefold() in name
                        for term in profile["match_terms"]
                        if str(term).strip()
                    )
                ]
                exact_matches.sort(
                    key=lambda profile: max(
                        (
                            len(str(term).strip())
                            for term in profile["match_terms"]
                            if str(term).strip().casefold() in name
                        ),
                        default=0,
                    ),
                    reverse=True,
                )
                profile = exact_matches[0] if exact_matches else None

                life_stage = ""
                if item["age_group"]:
                    age_group = str(item["age_group"]).casefold()
                    if "puppy" in age_group or "kitten" in age_group:
                        life_stage = "YOUNG"
                    elif "senior" in age_group:
                        life_stage = "SENIOR"
                    elif "adult" in age_group:
                        life_stage = "ADULT"

                words = name
                if any(term in words for term in ("snack", "treat", "bánh thưởng", "que thưởng")):
                    category, food_type = "Thức ăn bổ sung", "Snack"
                elif any(term in words for term in ("pate", "mousse", "soup", "wet food")):
                    category, food_type = "Thức ăn hoàn chỉnh", "Thức ăn ướt"
                elif any(term in words for term in ("cỏ khô", "timothy", "orchard", "hay ")):
                    category, food_type = "Cỏ và forage", "Cỏ khô"
                elif any(term in words for term in ("mix", "hỗn hợp")):
                    category, food_type = "Thức ăn hoàn chỉnh", "Hỗn hợp"
                elif any(term in words for term in ("pellet", "viên nén", "thức ăn viên")):
                    category, food_type = "Thức ăn hoàn chỉnh", "Pellet"
                elif any(term in words for term in ("hạt", "dry food", "thức ăn khô")):
                    category, food_type = "Thức ăn hoàn chỉnh", "Hạt khô"
                else:
                    category, food_type = "Thức ăn hoàn chỉnh", "Theo nhãn"

                values = {
                    "animal_subspecies": profile["subspecies"] if profile else "",
                    "age_min_months": profile["age_min_months"] if profile else None,
                    "age_max_months": profile["age_max_months"] if profile else None,
                    "age_unit": profile["age_unit"] if profile else "LABEL",
                    "life_stage": profile["life_stage"] if profile else life_stage,
                    "food_category": profile["food_category"] if profile else category,
                    "food_type": profile["food_type"] if profile else food_type,
                    "food_subtype": profile["food_subtype"] if profile else "",
                    "breed_size": profile["breed_size"] if profile else "",
                    "suitable_weight_min": profile["suitable_weight_min"] if profile else None,
                    "suitable_weight_max": profile["suitable_weight_max"] if profile else None,
                    "feeding_frequency": profile["feeding_frequency"] if profile else "Theo nhãn sản phẩm",
                    "feeding_time": profile["feeding_time"] if profile else "",
                    "serving_size": profile["serving_size"] if profile else "",
                    "protein_source": profile["protein_source"] if profile else "",
                    "nutrition_type": profile["nutrition_type"] if profile else "",
                    "purpose": profile["purpose"] if profile else "Phân loại catalog; kiểm tra nhãn",
                    "vitamin_c_content": profile["vitamin_c_content"] if profile else "",
                    "water_level": profile["water_level"] if profile else "",
                    "diet_type": profile["diet_type"] if profile else "",
                }
                self.connection.execute(
                    """
                    UPDATE inventory_items SET
                        animal_subspecies = CASE WHEN animal_subspecies = ''
                            THEN ? ELSE animal_subspecies END,
                        age_min_months = COALESCE(age_min_months, ?),
                        age_max_months = COALESCE(age_max_months, ?),
                        age_unit = CASE
                            WHEN age_min_months IS NULL AND age_max_months IS NULL
                              AND life_stage = '' THEN ? ELSE age_unit END,
                        life_stage = CASE WHEN life_stage = '' THEN ? ELSE life_stage END,
                        food_category = CASE WHEN food_category = '' THEN ? ELSE food_category END,
                        food_type = CASE WHEN food_type = '' THEN ? ELSE food_type END,
                        food_subtype = CASE WHEN food_subtype = '' THEN ? ELSE food_subtype END,
                        breed_size = CASE WHEN breed_size = '' THEN ? ELSE breed_size END,
                        suitable_weight_min = COALESCE(suitable_weight_min, ?),
                        suitable_weight_max = COALESCE(suitable_weight_max, ?),
                        feeding_frequency = CASE
                            WHEN feeding_frequency = 'Theo hướng dẫn sản phẩm'
                                THEN ? ELSE feeding_frequency END,
                        feeding_time = CASE WHEN feeding_time = '' THEN ? ELSE feeding_time END,
                        serving_size = CASE WHEN serving_size = '' THEN ? ELSE serving_size END,
                        protein_source = CASE WHEN protein_source = '' THEN ? ELSE protein_source END,
                        nutrition_type = CASE WHEN nutrition_type = '' THEN ? ELSE nutrition_type END,
                        purpose = CASE WHEN purpose = '' THEN ? ELSE purpose END,
                        vitamin_c_content = CASE WHEN vitamin_c_content = '' THEN ? ELSE vitamin_c_content END,
                        water_level = CASE WHEN water_level = '' THEN ? ELSE water_level END,
                        diet_type = CASE WHEN diet_type = '' THEN ? ELSE diet_type END
                    WHERE id = ?
                    """,
                    (*values.values(), item["id"]),
                )
                matched += 1
            for rule in AGE_RULES:
                self.connection.execute(
                    """
                    INSERT OR IGNORE INTO feeding_age_rules
                        (code, species, subspecies, breed_size, life_stage,
                         age_min_months, age_max_months, age_unit, food_category,
                         food_type, status, note)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        rule["code"],
                        rule["species"],
                        rule["subspecies"],
                        rule["breed_size"],
                        rule["life_stage"],
                        rule["age_min_months"],
                        rule["age_max_months"],
                        rule["age_unit"],
                        rule["food_category"],
                        rule["food_type"],
                        rule["status"],
                        rule["note"],
                    ),
                )
        return matched, len(AGE_RULES)

    def list_items(self, search: str = "") -> list[sqlite3.Row]:
        query = """
            SELECT i.*,
                   COALESCE(SUM(b.quantity_remaining), 0) AS stock_quantity,
                   COALESCE(SUM(CASE
                       WHEN b.expiry_date IS NULL
                         OR b.expiry_date >= date('now', 'localtime')
                       THEN b.quantity_remaining ELSE 0 END), 0) AS usable_quantity,
                   COALESCE(SUM(CASE
                       WHEN b.expiry_date < date('now', 'localtime')
                         AND b.quantity_remaining > 0
                       THEN b.quantity_remaining ELSE 0 END), 0) AS expired_quantity
            FROM inventory_items i
            LEFT JOIN inventory_batches b ON b.item_id = i.id
        """
        parameters: tuple[str, ...] = ()
        if search.strip():
            pattern = f"%{search.strip()}%"
            query += """
                WHERE i.item_code LIKE ? OR i.name LIKE ?
                   OR i.catalog_category LIKE ? OR i.barcode LIKE ?
                   OR i.brand LIKE ?
            """
            parameters = (pattern, pattern, pattern, pattern, pattern)
        query += " GROUP BY i.id ORDER BY i.name COLLATE NOCASE"
        return self.connection.execute(query, parameters).fetchall()

    def get_item(self, item_id: int) -> sqlite3.Row | None:
        return self.connection.execute(
            """
            SELECT i.*,
                   COALESCE(SUM(b.quantity_remaining), 0) AS stock_quantity,
                   COALESCE(SUM(CASE
                       WHEN b.expiry_date IS NULL
                         OR b.expiry_date >= date('now', 'localtime')
                       THEN b.quantity_remaining ELSE 0 END), 0) AS usable_quantity,
                   COALESCE(SUM(CASE
                       WHEN b.expiry_date < date('now', 'localtime')
                         AND b.quantity_remaining > 0
                       THEN b.quantity_remaining ELSE 0 END), 0) AS expired_quantity
            FROM inventory_items i
            LEFT JOIN inventory_batches b ON b.item_id = i.id
            WHERE i.id = ?
            GROUP BY i.id
            """,
            (item_id,),
        ).fetchone()

    def list_age_rules(self, active_only: bool = True) -> list[sqlite3.Row]:
        where = "WHERE status = 'ACTIVE'" if active_only else ""
        return self.connection.execute(
            f"""
            SELECT * FROM feeding_age_rules {where}
            ORDER BY species, breed_size, age_min_months, life_stage
            """
        ).fetchall()

    def save_age_rule(
        self, values: dict[str, Any], rule_id: int | None = None
    ) -> int:
        code = str(values.get("code", "")).strip().upper()
        species = str(values.get("species", "")).strip().upper()
        stage = str(values.get("life_stage", "")).strip()
        size = str(values.get("breed_size", "ALL")).strip().upper() or "ALL"
        unit = str(values.get("age_unit", "MONTH")).strip().upper()
        minimum = self._optional_number(values.get("age_min_months"), "Tuổi tối thiểu")
        maximum = self._optional_number(values.get("age_max_months"), "Tuổi tối đa")
        if not code or not species or not stage:
            raise ValueError("Mã, loài và giai đoạn sống của quy tắc là bắt buộc.")
        if unit not in {"MONTH", "YEAR", "SPECIES", "LABEL"}:
            raise ValueError("Đơn vị tuổi của quy tắc không hợp lệ.")
        if minimum is not None and maximum is not None and minimum > maximum:
            raise ValueError("Tuổi tối thiểu không được lớn hơn tuổi tối đa.")
        fields = (
            code,
            species,
            str(values.get("subspecies", "")).strip(),
            size,
            stage,
            minimum,
            maximum,
            unit,
            str(values.get("food_category", "")).strip(),
            str(values.get("food_type", "")).strip(),
            "ACTIVE" if bool(values.get("is_active", True)) else "INACTIVE",
            str(values.get("note", "")).strip(),
        )
        with self.connection:
            if rule_id is None:
                cursor = self.connection.execute(
                    """
                    INSERT INTO feeding_age_rules
                        (code, species, subspecies, breed_size, life_stage,
                         age_min_months, age_max_months, age_unit, food_category,
                         food_type, status, note)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    fields,
                )
                return int(cursor.lastrowid)
            cursor = self.connection.execute(
                """
                UPDATE feeding_age_rules SET code = ?, species = ?, subspecies = ?,
                    breed_size = ?, life_stage = ?, age_min_months = ?,
                    age_max_months = ?, age_unit = ?, food_category = ?, food_type = ?,
                    status = ?, note = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (*fields, rule_id),
            )
            if cursor.rowcount != 1:
                raise ValueError("Không tìm thấy quy tắc tuổi.")
            return rule_id

    def recommend_feeding_products(
        self,
        animal: sqlite3.Row,
        water_level: str = "",
        diet_type: str = "",
    ) -> dict[str, Any]:
        species = self._species_key(str(animal["species"]))
        breed = str(animal["breed"] or "").casefold()
        weight = animal["weight"]
        age_months = self._age_in_months(str(animal["birth_date"] or ""))
        recognized_sizes = {
            size
            for size in ("toy", "small", "medium", "large", "giant")
            if size in breed
        }
        rules = [
            rule
            for rule in self.list_age_rules()
            if self._species_key(rule["species"]) == species
            and (
                not rule["subspecies"]
                or rule["subspecies"].casefold() in breed
                or breed in rule["subspecies"].casefold()
            )
            and (
                rule["breed_size"] in {"ALL", "ANY"}
                or not recognized_sizes
                or rule["breed_size"].casefold() in recognized_sizes
            )
            and (
                age_months is None
                or rule["age_unit"] in {"SPECIES", "LABEL"}
                or (
                    (
                        rule["age_min_months"] is None
                        or age_months
                        >= rule["age_min_months"]
                        * (12 if rule["age_unit"] == "YEAR" else 1)
                    )
                    and (
                        rule["age_max_months"] is None
                        or age_months
                        <= rule["age_max_months"]
                        * (12 if rule["age_unit"] == "YEAR" else 1)
                    )
                )
            )
        ]
        stages = {
            self._canonical_life_stage(str(rule["life_stage"]))
            for rule in rules
            if self._canonical_life_stage(str(rule["life_stage"]))
        }
        rule_categories = {
            self._canonical_food_tag(str(rule["food_category"]))
            for rule in rules
            if rule["food_category"]
        }
        rule_types = {
            self._canonical_food_tag(str(rule["food_type"]))
            for rule in rules
            if rule["food_type"]
            and self._canonical_food_tag(str(rule["food_type"]))
            not in {"species_dependent", "label"}
        }
        candidate_rows = self.connection.execute(
            """
            SELECT i.*,
                   COALESCE(SUM(CASE
                       WHEN b.expiry_date IS NULL
                         OR b.expiry_date >= date('now', 'localtime')
                       THEN b.quantity_remaining ELSE 0 END), 0) AS usable_quantity
            FROM inventory_items i
            LEFT JOIN inventory_batches b ON b.item_id = i.id
            WHERE i.is_active = 1
              AND i.food_type != ''
              AND i.target_species != ''
            GROUP BY i.id ORDER BY i.name COLLATE NOCASE
            """
        ).fetchall()
        candidates: list[sqlite3.Row] = []
        for item in candidate_rows:
            product_species = {
                self._species_key(value.strip())
                for value in str(item["target_species"]).split(",")
                if value.strip()
            }
            if species not in product_species and "any" not in product_species:
                continue
            if item["usable_quantity"] <= 0:
                continue
            if age_months is not None and item["age_unit"] != "LABEL":
                age_multiplier = 12 if item["age_unit"] == "YEAR" else 1
                if (
                    item["age_min_months"] is not None
                    and age_months < item["age_min_months"] * age_multiplier
                ):
                    continue
                if (
                    item["age_max_months"] is not None
                    and age_months > item["age_max_months"] * age_multiplier
                ):
                    continue
            item_stage = self._canonical_life_stage(str(item["life_stage"]))
            if item_stage and stages and item_stage not in stages:
                continue
            item_category = self._canonical_food_tag(str(item["food_category"]))
            if rule_categories and item_category not in rule_categories:
                continue
            item_type = self._canonical_food_tag(str(item["food_type"]))
            if rule_types and item_type not in rule_types:
                continue
            if weight is not None:
                if (
                    item["suitable_weight_min"] is not None
                    and weight < item["suitable_weight_min"]
                ):
                    continue
                if (
                    item["suitable_weight_max"] is not None
                    and weight > item["suitable_weight_max"]
                ):
                    continue
            if water_level and item["water_level"] and (
                water_level.casefold() != item["water_level"].casefold()
            ):
                continue
            if diet_type and item["diet_type"] and (
                diet_type.casefold() != item["diet_type"].casefold()
            ):
                continue
            candidates.append(item)
        return {
            "age_months": age_months,
            "life_stages": sorted(stages),
            "age_rules": rules,
            "products": candidates,
            "notice": (
                "Đây là bộ lọc catalog theo nhãn và quy tắc mẫu, không phải khẩu phần "
                "hay chỉ định y tế. Hãy xác minh loài/nhãn và hỏi bác sĩ thú y khi cần."
            ),
        }

    @staticmethod
    def _species_key(value: str) -> str:
        key = value.strip().casefold().replace(" ", "_")
        return {
            "dog": "cho",
            "dogs": "cho",
            "chó": "cho",
            "cat": "meo",
            "cats": "meo",
            "mèo": "meo",
            "rabbit": "tho",
            "thỏ": "tho",
            "bird": "chim",
            "guinea_pig": "chuot_lang",
            "guinea pig": "chuot_lang",
            "chuot_lang": "chuot_lang",
            "hedgehog": "nhim",
            "nhím": "nhim",
            "reptile": "bo_sat",
            "reptiles": "bo_sat",
            "bò_sát": "bo_sat",
            "turtle": "rua",
            "tortoise": "rua",
            "rùa": "rua",
            "rùa_cạn": "rua",
            "rùa_nước": "rua",
            "fish": "ca",
            "cá": "ca",
            "cá_cảnh": "ca",
            "chim_cảnh": "chim",
        }.get(key, key)

    @staticmethod
    def _canonical_life_stage(value: str) -> str:
        stage = value.strip().casefold().replace(" ", "_")
        if stage in {"", "all", "mọi_lứa_tuổi"}:
            return ""
        if stage in {
            "puppy",
            "late_puppy",
            "kitten",
            "kitten_growth",
            "late_kitten",
            "juvenile",
            "young",
            "young_adult",
        }:
            return "young"
        if stage in {"adult", "mature"}:
            return "adult"
        if stage in {"senior", "old"}:
            return "senior"
        if stage == "species_dependent":
            return ""
        return stage

    @staticmethod
    def _canonical_food_tag(value: str) -> str:
        tag = value.strip().casefold()
        return {
            "thức ăn hoàn chỉnh": "complete",
            "complete": "complete",
            "thức ăn bổ sung": "complementary",
            "complementary": "complementary",
            "cỏ và forage": "forage",
            "forage": "forage",
            "hạt khô": "dry",
            "dry": "dry",
            "thức ăn ướt": "wet",
            "wet": "wet",
            "snack": "treat",
            "treat": "treat",
            "cỏ khô": "hay",
            "hay": "hay",
            "pellet": "pellet",
            "hỗn hợp": "mix",
            "mix": "mix",
            "theo loài": "species_dependent",
            "species_dependent": "species_dependent",
            "theo nhãn": "label",
        }.get(tag, tag)

    @staticmethod
    def _age_in_months(birth_date: str) -> int | None:
        if not birth_date:
            return None
        try:
            born = date.fromisoformat(birth_date)
        except ValueError:
            return None
        current = date.today()
        if born > current:
            return None
        months = (current.year - born.year) * 12 + current.month - born.month
        if current.day < born.day:
            months -= 1
        return months

    def save_item(self, values: dict[str, Any], item_id: int | None = None) -> int:
        code = str(values.get("item_code", "")).strip()
        name = str(values.get("name", "")).strip()
        category = values.get("category")
        unit = str(values.get("unit", "")).strip()
        minimum = float(values.get("minimum_stock", 0))
        retail_price = float(values.get("retail_price", 0))
        member_price = values.get("member_price")
        member_price = None if member_price in (None, "") else float(member_price)
        promotion = float(values.get("promotion_percent", 0))
        age_min = self._optional_number(values.get("age_min_months"), "Tuổi tối thiểu")
        age_max = self._optional_number(values.get("age_max_months"), "Tuổi tối đa")
        weight_min = self._optional_number(
            values.get("suitable_weight_min"), "Cân nặng tối thiểu"
        )
        weight_max = self._optional_number(
            values.get("suitable_weight_max"), "Cân nặng tối đa"
        )
        if not code or not name or not unit:
            raise ValueError("Mã, tên vật tư và đơn vị tính là bắt buộc.")
        if category not in INVENTORY_CATEGORIES:
            raise ValueError("Loại vật tư không hợp lệ.")
        if not math.isfinite(minimum) or minimum < 0:
            raise ValueError("Mức tồn tối thiểu không thể âm.")
        if not math.isfinite(retail_price) or retail_price < 0:
            raise ValueError("Giá bán không hợp lệ.")
        if member_price is not None and (
            not math.isfinite(member_price) or member_price < 0
        ):
            raise ValueError("Giá hội viên không hợp lệ.")
        if not math.isfinite(promotion) or not 0 <= promotion <= 100:
            raise ValueError("Khuyến mãi phải từ 0 đến 100%.")
        if age_min is not None and age_max is not None and age_min > age_max:
            raise ValueError("Tuổi tối thiểu không được lớn hơn tuổi tối đa.")
        if (
            weight_min is not None
            and weight_max is not None
            and weight_min > weight_max
        ):
            raise ValueError("Cân nặng tối thiểu không được lớn hơn tối đa.")
        age_unit = str(values.get("age_unit", "MONTH")).strip().upper()
        if age_unit not in {"MONTH", "YEAR", "LABEL"}:
            raise ValueError("Đơn vị tuổi không hợp lệ.")
        food_values = (
            str(values.get("animal_subspecies", "")).strip(),
            age_min,
            age_max,
            age_unit,
            str(values.get("life_stage", "")).strip(),
            str(values.get("food_category", "")).strip(),
            str(values.get("food_type", "")).strip(),
            str(values.get("food_subtype", "")).strip(),
            str(values.get("breed_size", "")).strip(),
            weight_min,
            weight_max,
            str(values.get("feeding_frequency", "Theo hướng dẫn sản phẩm")).strip()
            or "Theo hướng dẫn sản phẩm",
            str(values.get("feeding_time", "")).strip(),
            str(values.get("serving_size", "")).strip(),
            str(values.get("protein_source", "")).strip(),
            str(values.get("nutrition_type", "")).strip(),
            str(values.get("purpose", "")).strip(),
            str(values.get("vitamin_c_content", "")).strip(),
            str(values.get("water_level", "")).strip(),
            str(values.get("diet_type", "")).strip(),
        )
        with self.connection:
            if item_id is None:
                cursor = self.connection.execute(
                    """
                    INSERT INTO inventory_items
                        (item_code, name, category, unit, minimum_stock, description,
                         catalog_category, target_species, age_group, pack_size, brand,
                         barcode, retail_price, member_price, promotion_percent,
                         promotion_note, ingredients, image_path, is_demo,
                         animal_subspecies, age_min_months, age_max_months, age_unit,
                         life_stage, food_category, food_type, food_subtype, breed_size,
                         suitable_weight_min, suitable_weight_max, feeding_frequency,
                         feeding_time, serving_size, protein_source, nutrition_type,
                         purpose, vitamin_c_content, water_level, diet_type)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        code,
                        name,
                        category,
                        unit,
                        minimum,
                        str(values.get("description", "")).strip(),
                        str(values.get("catalog_category", "")).strip(),
                        str(values.get("target_species", "")).strip(),
                        str(values.get("age_group", "")).strip(),
                        str(values.get("pack_size", "")).strip(),
                        str(values.get("brand", "")).strip(),
                        str(values.get("barcode", "")).strip(),
                        retail_price,
                        member_price,
                        promotion,
                        str(values.get("promotion_note", "")).strip(),
                        str(values.get("ingredients", "")).strip(),
                        str(values.get("image_path", "")).strip(),
                        int(bool(values.get("is_demo", False))),
                        *food_values,
                    ),
                )
                return int(cursor.lastrowid)
            cursor = self.connection.execute(
                """
                UPDATE inventory_items SET item_code = ?, name = ?, category = ?,
                    unit = ?, minimum_stock = ?, description = ?,
                    catalog_category = ?, target_species = ?, age_group = ?,
                    pack_size = ?, brand = ?, barcode = ?, retail_price = ?,
                    member_price = ?, promotion_percent = ?, promotion_note = ?,
                    ingredients = ?, image_path = ?,
                    animal_subspecies = ?, age_min_months = ?, age_max_months = ?,
                    age_unit = ?, life_stage = ?, food_category = ?, food_type = ?,
                    food_subtype = ?, breed_size = ?, suitable_weight_min = ?,
                    suitable_weight_max = ?, feeding_frequency = ?, feeding_time = ?,
                    serving_size = ?, protein_source = ?, nutrition_type = ?,
                    purpose = ?, vitamin_c_content = ?, water_level = ?, diet_type = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (
                    code,
                    name,
                    category,
                    unit,
                    minimum,
                    str(values.get("description", "")).strip(),
                    str(values.get("catalog_category", "")).strip(),
                    str(values.get("target_species", "")).strip(),
                    str(values.get("age_group", "")).strip(),
                    str(values.get("pack_size", "")).strip(),
                    str(values.get("brand", "")).strip(),
                    str(values.get("barcode", "")).strip(),
                    retail_price,
                    member_price,
                    promotion,
                    str(values.get("promotion_note", "")).strip(),
                    str(values.get("ingredients", "")).strip(),
                    str(values.get("image_path", "")).strip(),
                    *food_values,
                    item_id,
                ),
            )
            if cursor.rowcount == 0:
                raise ValueError("Không tìm thấy vật tư.")
            return item_id

    @staticmethod
    def _optional_number(value: Any, label: str) -> float | None:
        if value in (None, ""):
            return None
        try:
            number = float(value)
        except (TypeError, ValueError) as error:
            raise ValueError(f"{label} không hợp lệ.") from error
        if not math.isfinite(number) or number < 0:
            raise ValueError(f"{label} phải là số không âm.")
        return number

    def seed_catalog(self) -> None:
        with self.connection:
            for product in catalog_products():
                self.connection.execute(
                    """
                    INSERT OR IGNORE INTO inventory_items
                        (item_code, name, category, unit, description,
                         catalog_category, target_species, age_group, pack_size,
                         brand, barcode, retail_price, member_price,
                         promotion_percent, promotion_note, ingredients,
                         image_path, is_demo)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        product["item_code"],
                        product["name"],
                        product["stock_category"],
                        product["unit"],
                        product["description"],
                        product["catalog_category"],
                        product["target_species"],
                        product["age_group"],
                        product["pack_size"],
                        product["brand"],
                        product["barcode"],
                        product["retail_price"],
                        product["member_price"],
                        product["promotion_percent"],
                        product["promotion_note"],
                        product["ingredients"],
                        product["image_path"],
                        int(product["is_demo"]),
                    ),
                )
            for combo in COMBO_DEFINITIONS:
                self.connection.execute(
                    """
                    INSERT OR IGNORE INTO product_combos
                        (combo_code, name, description, target_species,
                         sale_price, is_demo, is_active)
                    VALUES (?, ?, ?, ?, ?, 1, 1)
                    """,
                    (
                        combo["code"],
                        combo["name"],
                        combo["description"],
                        combo["species"],
                        combo["price"],
                    ),
                )
                row = self.connection.execute(
                    "SELECT id FROM product_combos WHERE combo_code = ?",
                    (combo["code"],),
                ).fetchone()
                if row is None:
                    raise RuntimeError(f"Không thể khởi tạo combo {combo['code']}.")
                combo_id = int(row["id"])
                existing = self.connection.execute(
                    "SELECT 1 FROM product_combo_items WHERE combo_id = ? LIMIT 1",
                    (combo_id,),
                ).fetchone()
                if existing is not None:
                    continue
                for item_code, quantity in COMBO_COMPONENTS[combo["code"]]:
                    item = self.connection.execute(
                        "SELECT id FROM inventory_items WHERE item_code = ?",
                        (item_code,),
                    ).fetchone()
                    if item is None:
                        raise RuntimeError(
                            f"Thiếu sản phẩm demo {item_code} để cấu hình combo."
                        )
                    self.connection.execute(
                        """
                        INSERT INTO product_combo_items (combo_id, item_id, quantity)
                        VALUES (?, ?, ?)
                        """,
                        (combo_id, item["id"], quantity),
                    )

    def list_combos(self, active_only: bool = False) -> list[sqlite3.Row]:
        query = """
            SELECT c.*, COUNT(ci.item_id) AS component_count
            FROM product_combos c
            LEFT JOIN product_combo_items ci ON ci.combo_id = c.id
        """
        if active_only:
            query += " WHERE c.is_active = 1"
        return self.connection.execute(
            query + " GROUP BY c.id ORDER BY c.name COLLATE NOCASE"
        ).fetchall()

    def list_combo_items(self, combo_id: int) -> list[sqlite3.Row]:
        return self.connection.execute(
            """
            SELECT ci.*, i.item_code, i.name, i.unit, i.retail_price,
                   COALESCE(SUM(CASE
                       WHEN b.expiry_date IS NULL
                         OR b.expiry_date >= date('now', 'localtime')
                       THEN b.quantity_remaining ELSE 0 END), 0) AS usable_quantity
            FROM product_combo_items ci
            JOIN inventory_items i ON i.id = ci.item_id
            LEFT JOIN inventory_batches b ON b.item_id = i.id
            WHERE ci.combo_id = ?
            GROUP BY ci.item_id
            ORDER BY i.name COLLATE NOCASE
            """,
            (combo_id,),
        ).fetchall()

    def save_combo(
        self,
        values: dict[str, Any],
        components: list[dict[str, Any]],
        combo_id: int | None = None,
    ) -> int:
        code = str(values.get("combo_code", "")).strip().upper()
        name = str(values.get("name", "")).strip()
        price = float(values.get("sale_price", -1))
        member_price = values.get("member_price")
        member_price = None if member_price in (None, "") else float(member_price)
        promotion = float(values.get("promotion_percent", 0))
        if not code or not name:
            raise ValueError("Mã và tên combo là bắt buộc.")
        if price < 0 or (member_price is not None and member_price < 0):
            raise ValueError("Giá combo không thể âm.")
        if not 0 <= promotion <= 100:
            raise ValueError("Khuyến mãi combo phải từ 0 đến 100%.")
        if not components:
            raise ValueError("Combo cần có ít nhất một sản phẩm thành phần.")
        normalized: dict[int, float] = {}
        for component in components:
            item_id = int(component["item_id"])
            quantity = float(component["quantity"])
            if not math.isfinite(quantity) or quantity <= 0:
                raise ValueError("Số lượng thành phần combo phải lớn hơn 0.")
            normalized[item_id] = normalized.get(item_id, 0) + quantity

        with self.connection:
            for item_id in normalized:
                exists = self.connection.execute(
                    "SELECT id FROM inventory_items WHERE id = ? AND is_active = 1",
                    (item_id,),
                ).fetchone()
                if exists is None:
                    raise ValueError("Combo có sản phẩm không tồn tại hoặc đã ngừng bán.")
            fields = (
                code,
                name,
                str(values.get("description", "")).strip(),
                str(values.get("target_species", "")).strip(),
                price,
                member_price,
                promotion,
                int(bool(values.get("is_demo", False))),
                int(bool(values.get("is_active", True))),
            )
            if combo_id is None:
                cursor = self.connection.execute(
                    """
                    INSERT INTO product_combos
                        (combo_code, name, description, target_species, sale_price,
                         member_price, promotion_percent, is_demo, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    fields,
                )
                combo_id = int(cursor.lastrowid)
            else:
                cursor = self.connection.execute(
                    """
                    UPDATE product_combos SET combo_code = ?, name = ?, description = ?,
                        target_species = ?, sale_price = ?, member_price = ?,
                        promotion_percent = ?, is_demo = ?, is_active = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                    """,
                    (*fields, combo_id),
                )
                if cursor.rowcount != 1:
                    raise ValueError("Không tìm thấy combo.")
                self.connection.execute(
                    "DELETE FROM product_combo_items WHERE combo_id = ?", (combo_id,)
                )
            self.connection.executemany(
                """
                INSERT INTO product_combo_items (combo_id, item_id, quantity)
                VALUES (?, ?, ?)
                """,
                [
                    (combo_id, item_id, quantity)
                    for item_id, quantity in normalized.items()
                ],
            )
            return combo_id

    def receive_stock(self, item_id: int, values: dict[str, Any]) -> int:
        batch_code = str(values.get("batch_code", "")).strip()
        quantity = float(values.get("quantity", 0))
        unit_cost = float(values.get("unit_cost", 0))
        expiry_date = values.get("expiry_date") or None
        if not batch_code:
            raise ValueError("Mã lô là bắt buộc.")
        if not math.isfinite(quantity) or quantity <= 0:
            raise ValueError("Số lượng nhập phải lớn hơn 0.")
        if not math.isfinite(unit_cost) or unit_cost < 0:
            raise ValueError("Giá nhập không thể âm.")
        if expiry_date:
            try:
                date.fromisoformat(expiry_date)
            except ValueError as error:
                raise ValueError("Ngày hết hạn không hợp lệ.") from error
            if expiry_date < date.today().isoformat():
                raise ValueError("Không thể nhập lô đã hết hạn.")
        with self.connection:
            item = self.connection.execute(
                "SELECT id FROM inventory_items WHERE id = ? AND is_active = 1",
                (item_id,),
            ).fetchone()
            if item is None:
                raise ValueError("Không tìm thấy vật tư đang hoạt động.")
            cursor = self.connection.execute(
                """
                INSERT INTO inventory_batches
                    (item_id, batch_code, expiry_date, quantity_remaining, unit_cost)
                VALUES (?, ?, ?, ?, ?)
                """,
                (item_id, batch_code, expiry_date, quantity, unit_cost),
            )
            batch_id = int(cursor.lastrowid)
            self.connection.execute(
                """
                INSERT INTO inventory_movements
                    (item_id, batch_id, movement_type, quantity, occurred_on, reference, note)
                VALUES (?, ?, 'IN', ?, ?, ?, ?)
                """,
                (
                    item_id,
                    batch_id,
                    quantity,
                    values.get("occurred_on", date.today().isoformat()),
                    str(values.get("reference", "")).strip(),
                    str(values.get("note", "")).strip(),
                ),
            )
            return batch_id

    def consume_stock(self, item_id: int, values: dict[str, Any]) -> list[int]:
        quantity = float(values.get("quantity", 0))
        if not math.isfinite(quantity) or quantity <= 0:
            raise ValueError("Số lượng xuất dùng phải lớn hơn 0.")
        with self.connection:
            item = self.connection.execute(
                "SELECT id FROM inventory_items WHERE id = ? AND is_active = 1",
                (item_id,),
            ).fetchone()
            if item is None:
                raise ValueError("Không tìm thấy vật tư đang hoạt động.")
            batches = self.connection.execute(
                """
                SELECT id, quantity_remaining
                FROM inventory_batches
                WHERE item_id = ? AND quantity_remaining > 0
                  AND (
                      expiry_date IS NULL
                      OR expiry_date >= date('now', 'localtime')
                  )
                ORDER BY expiry_date IS NULL, expiry_date, id
                """,
                (item_id,),
            ).fetchall()
            usable = sum(float(batch["quantity_remaining"]) for batch in batches)
            if quantity > usable:
                raise ValueError(
                    f"Tồn kho dùng được không đủ (còn {usable:g}). "
                    "Lô hết hạn không được xuất dùng."
                )
            remaining = quantity
            movement_ids = []
            for batch in batches:
                if remaining <= 0:
                    break
                taken = min(remaining, float(batch["quantity_remaining"]))
                self.connection.execute(
                    """
                    UPDATE inventory_batches
                    SET quantity_remaining = quantity_remaining - ?
                    WHERE id = ?
                    """,
                    (taken, batch["id"]),
                )
                cursor = self.connection.execute(
                    """
                    INSERT INTO inventory_movements
                        (item_id, batch_id, movement_type, quantity, occurred_on,
                         animal_id, reference, note)
                    VALUES (?, ?, 'OUT', ?, ?, ?, ?, ?)
                    """,
                    (
                        item_id,
                        batch["id"],
                        taken,
                        values.get("occurred_on", date.today().isoformat()),
                        values.get("animal_id"),
                        str(values.get("reference", "")).strip(),
                        str(values.get("note", "")).strip(),
                    ),
                )
                movement_ids.append(int(cursor.lastrowid))
                remaining = round(remaining - taken, 6)
            return movement_ids

    def list_batches(self, item_id: int) -> list[sqlite3.Row]:
        return self.connection.execute(
            """
            SELECT * FROM inventory_batches
            WHERE item_id = ? ORDER BY expiry_date IS NULL, expiry_date, id
            """,
            (item_id,),
        ).fetchall()

    def list_movements(self, item_id: int) -> list[sqlite3.Row]:
        return self.connection.execute(
            """
            SELECT m.*, b.batch_code, a.animal_code, a.name AS animal_name
            FROM inventory_movements m
            JOIN inventory_batches b ON b.id = m.batch_id
            LEFT JOIN animals a ON a.id = m.animal_id
            WHERE m.item_id = ?
            ORDER BY m.occurred_on DESC, m.id DESC
            """,
            (item_id,),
        ).fetchall()

    def low_stock_items(self) -> list[sqlite3.Row]:
        return [
            item
            for item in self.list_items()
            if item["is_active"]
            and (not item["is_demo"] or item["stock_quantity"] > 0)
            and item["usable_quantity"] <= item["minimum_stock"]
        ]

    def expiring_batches(self, days: int = 30) -> list[sqlite3.Row]:
        if days < 0:
            raise ValueError("Số ngày cảnh báo không thể âm.")
        return self.connection.execute(
            """
            SELECT b.*, i.item_code, i.name AS item_name, i.unit
            FROM inventory_batches b
            JOIN inventory_items i ON i.id = b.item_id
            WHERE i.is_active = 1 AND b.quantity_remaining > 0
              AND b.expiry_date IS NOT NULL
              AND b.expiry_date <= date('now', 'localtime', ?)
            ORDER BY b.expiry_date, i.name
            """,
            (f"+{days} days",),
        ).fetchall()

    def set_item_active(self, item_id: int, active: bool) -> None:
        with self.connection:
            cursor = self.connection.execute(
                """
                UPDATE inventory_items
                SET is_active = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?
                """,
                (int(active), item_id),
            )
            if cursor.rowcount == 0:
                raise ValueError("Không tìm thấy vật tư.")
