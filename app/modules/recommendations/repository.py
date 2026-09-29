from __future__ import annotations

import math
import sqlite3
from typing import Any

from app.modules.recommendations.constants import (
    RECOMMENDATION_AGE_GROUPS,
    RECOMMENDATION_CATEGORIES,
    RECOMMENDATION_EVENTS,
)
from app.modules.recommendations.engine import encode_tags, parse_tags


class RecommendationRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def list_products(self) -> list[sqlite3.Row]:
        return self.connection.execute(
            """
            SELECT i.id AS item_id, i.item_code,
                   i.name || CASE WHEN i.pack_size = '' THEN '' ELSE ' · ' || i.pack_size END
                       AS name,
                   i.category AS stock_category,
                   i.unit, i.is_active, i.description AS item_description,
                   p.recommendation_category, p.species_tags, p.age_groups,
                   p.breed_tags, p.gender_tags, p.needs_tags, p.health_tags, p.activity_tags,
                   p.coat_tags, p.environment_tags, p.avoid_tags,
                   p.minimum_weight, p.maximum_weight, p.recommendation_price,
                   p.popularity, p.note,
                   i.age_min_months, i.age_max_months, i.age_unit,
                   i.life_stage, i.food_category, i.food_type, i.food_subtype,
                   i.animal_subspecies, i.suitable_weight_min, i.suitable_weight_max,
                   i.feeding_frequency, i.serving_size, i.protein_source,
                   i.nutrition_type, i.purpose, i.vitamin_c_content,
                   i.water_level, i.diet_type,
                   COALESCE(SUM(CASE
                       WHEN b.expiry_date IS NULL
                         OR b.expiry_date >= date('now', 'localtime')
                       THEN b.quantity_remaining ELSE 0 END), 0) AS usable_quantity
            FROM product_recommendation_profiles p
            JOIN inventory_items i ON i.id = p.item_id
            LEFT JOIN inventory_batches b ON b.item_id = i.id
            WHERE i.is_active = 1
            GROUP BY i.id
            ORDER BY i.name COLLATE NOCASE
            """
        ).fetchall()

    def get_profile(self, item_id: int) -> sqlite3.Row | None:
        return self.connection.execute(
            """
            SELECT i.id AS item_id, i.item_code,
                   i.name || CASE WHEN i.pack_size = '' THEN '' ELSE ' · ' || i.pack_size END
                       AS name,
                   i.is_active,
                   p.recommendation_category, p.species_tags, p.age_groups,
                   p.breed_tags, p.gender_tags, p.needs_tags, p.health_tags, p.activity_tags,
                   p.coat_tags, p.environment_tags, p.avoid_tags,
                   p.minimum_weight, p.maximum_weight, p.recommendation_price,
                   p.popularity, p.note
            FROM inventory_items i
            LEFT JOIN product_recommendation_profiles p ON p.item_id = i.id
            WHERE i.id = ?
            """,
            (item_id,),
        ).fetchone()

    def save_profile(self, item_id: int, values: dict[str, Any]) -> None:
        category = str(values.get("recommendation_category", ""))
        if category not in RECOMMENDATION_CATEGORIES:
            raise ValueError("Nhóm sản phẩm gợi ý không hợp lệ.")
        product = self.connection.execute(
            "SELECT is_active FROM inventory_items WHERE id = ?", (item_id,)
        ).fetchone()
        if product is None:
            raise ValueError("Không tìm thấy vật tư liên kết.")
        if not product["is_active"]:
            raise ValueError("Chỉ cấu hình gợi ý cho vật tư đang hoạt động.")

        tags = {
            field: encode_tags(values.get(field, ""))
            for field in (
                "species_tags",
                "age_groups",
                "breed_tags",
                "gender_tags",
                "needs_tags",
                "health_tags",
                "activity_tags",
                "coat_tags",
                "environment_tags",
                "avoid_tags",
            )
        }
        invalid_age_groups = parse_tags(values.get("age_groups", "")) - {
            group.casefold() for group in RECOMMENDATION_AGE_GROUPS
        }
        if invalid_age_groups:
            raise ValueError(
                "Nhóm tuổi chỉ gồm BABY, YOUNG, ADULT hoặc SENIOR."
            )
        if category in {"FOOD", "SUPPLEMENT"} and not parse_tags(
            values.get("species_tags", "")
        ):
            raise ValueError(
                "Sản phẩm ăn uống/bổ sung phải khai báo loài phù hợp để tránh gợi ý nhầm."
            )

        price = float(values.get("recommendation_price", 0))
        popularity = int(values.get("popularity", 0))
        if not math.isfinite(price) or price < 0:
            raise ValueError("Giá bán gợi ý phải là số không âm.")
        if popularity < 0 or popularity > 100:
            raise ValueError("Độ phổ biến phải từ 0 đến 100.")
        minimum_weight = values.get("minimum_weight")
        maximum_weight = values.get("maximum_weight")
        minimum_weight = float(minimum_weight) if minimum_weight is not None else None
        maximum_weight = float(maximum_weight) if maximum_weight is not None else None
        for weight in (minimum_weight, maximum_weight):
            if weight is not None and (not math.isfinite(weight) or weight < 0):
                raise ValueError("Giới hạn cân nặng phải là số không âm.")
        if (
            minimum_weight is not None
            and maximum_weight is not None
            and minimum_weight > maximum_weight
        ):
            raise ValueError("Cân nặng tối thiểu không được lớn hơn tối đa.")

        with self.connection:
            self.connection.execute(
                """
                INSERT INTO product_recommendation_profiles (
                    item_id, recommendation_category, species_tags, age_groups,
                    breed_tags, gender_tags, needs_tags, health_tags, activity_tags, coat_tags,
                    environment_tags, avoid_tags, minimum_weight, maximum_weight,
                    recommendation_price, popularity, note, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                          CURRENT_TIMESTAMP)
                ON CONFLICT(item_id) DO UPDATE SET
                    recommendation_category = excluded.recommendation_category,
                    species_tags = excluded.species_tags,
                    age_groups = excluded.age_groups,
                    breed_tags = excluded.breed_tags,
                    gender_tags = excluded.gender_tags,
                    needs_tags = excluded.needs_tags,
                    health_tags = excluded.health_tags,
                    activity_tags = excluded.activity_tags,
                    coat_tags = excluded.coat_tags,
                    environment_tags = excluded.environment_tags,
                    avoid_tags = excluded.avoid_tags,
                    minimum_weight = excluded.minimum_weight,
                    maximum_weight = excluded.maximum_weight,
                    recommendation_price = excluded.recommendation_price,
                    popularity = excluded.popularity,
                    note = excluded.note,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (
                    item_id,
                    category,
                    tags["species_tags"],
                    tags["age_groups"],
                    tags["breed_tags"],
                    tags["gender_tags"],
                    tags["needs_tags"],
                    tags["health_tags"],
                    tags["activity_tags"],
                    tags["coat_tags"],
                    tags["environment_tags"],
                    tags["avoid_tags"],
                    minimum_weight,
                    maximum_weight,
                    price,
                    popularity,
                    str(values.get("note", "")).strip(),
                ),
            )

    def delete_profile(self, item_id: int) -> None:
        with self.connection:
            cursor = self.connection.execute(
                "DELETE FROM product_recommendation_profiles WHERE item_id = ?",
                (item_id,),
            )
            if cursor.rowcount == 0:
                raise ValueError("Sản phẩm chưa được cấu hình gợi ý.")

    def list_interactions(
        self, animal_id: int, customer_id: int | None = None
    ) -> list[dict[str, Any]]:
        rows = self.connection.execute(
            """
            SELECT r.item_id, r.event_type, r.occurred_at, r.note,
                   p.needs_tags, p.health_tags, p.activity_tags, p.coat_tags,
                   p.environment_tags, p.species_tags, p.age_groups,
                   p.breed_tags, p.gender_tags,
                   p.recommendation_category AS recommendation_category
            FROM recommendation_interactions r
            JOIN product_recommendation_profiles p ON p.item_id = r.item_id
            WHERE r.animal_id = ?
              AND (? IS NULL OR r.customer_id IS NULL OR r.customer_id = ?)
            ORDER BY r.occurred_at DESC
            LIMIT 500
            """,
            (animal_id, customer_id, customer_id),
        ).fetchall()
        interactions = []
        for row in rows:
            interaction = dict(row)
            interaction["purpose_tags"] = encode_tags(
                interaction["recommendation_category"]
            )
            del interaction["recommendation_category"]
            interactions.append(interaction)
        return interactions

    def list_peer_interactions(
        self, animal_id: int, customer_id: int | None = None
    ) -> list[dict[str, Any]]:
        rows = self.connection.execute(
            """
            SELECT DISTINCT peer2.animal_id AS peer_animal_id,
                   peer1.item_id AS anchor_item_id, peer2.item_id,
                   peer2.event_type, peer2.occurred_at,
                   p.needs_tags, p.health_tags, p.activity_tags, p.coat_tags,
                   p.environment_tags, p.species_tags, p.age_groups,
                   p.breed_tags, p.gender_tags,
                   p.recommendation_category AS recommendation_category
            FROM recommendation_interactions target
            JOIN recommendation_interactions peer1
              ON peer1.item_id = target.item_id
             AND peer1.animal_id <> target.animal_id
            JOIN recommendation_interactions peer2
              ON peer2.animal_id = peer1.animal_id
             AND peer2.item_id <> peer1.item_id
             AND peer2.event_type IN ('LIKE', 'ADD_TO_CART', 'PURCHASE', 'REVIEW')
            JOIN product_recommendation_profiles p ON p.item_id = peer2.item_id
            WHERE target.animal_id = ?
              AND target.event_type IN ('VIEW', 'CLICK', 'LIKE', 'ADD_TO_CART', 'PURCHASE')
              AND peer1.event_type IN ('VIEW', 'CLICK', 'LIKE', 'ADD_TO_CART', 'PURCHASE')
              AND (? IS NULL OR peer1.customer_id IS NULL OR peer1.customer_id = ?)
            ORDER BY peer2.occurred_at DESC
            LIMIT 2000
            """,
            (animal_id, customer_id, customer_id),
        ).fetchall()
        interactions = []
        for row in rows:
            interaction = dict(row)
            interaction["purpose_tags"] = encode_tags(
                interaction["recommendation_category"]
            )
            del interaction["recommendation_category"]
            interactions.append(interaction)
        return interactions

    def record_interaction(
        self,
        animal_id: int,
        item_id: int,
        event_type: str,
        actor_id: int | None,
        customer_id: int | None,
        note: str,
    ) -> int:
        if event_type not in RECOMMENDATION_EVENTS:
            raise ValueError("Loại hành vi sản phẩm không hợp lệ.")
        with self.connection:
            animal = self.connection.execute(
                "SELECT id FROM animals WHERE id = ?", (animal_id,)
            ).fetchone()
            if animal is None:
                raise ValueError("Không tìm thấy thú cưng.")
            profile = self.connection.execute(
                """
                SELECT p.item_id FROM product_recommendation_profiles p
                JOIN inventory_items i ON i.id = p.item_id
                WHERE p.item_id = ? AND i.is_active = 1
                """,
                (item_id,),
            ).fetchone()
            if profile is None:
                raise ValueError("Sản phẩm chưa có hồ sơ gợi ý đang hoạt động.")
            if customer_id is not None and self.connection.execute(
                "SELECT id FROM customers WHERE id = ?", (customer_id,)
            ).fetchone() is None:
                raise ValueError("Không tìm thấy khách hàng.")
            cursor = self.connection.execute(
                """
                INSERT INTO recommendation_interactions
                    (animal_id, item_id, customer_id, actor_id, event_type, note)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    animal_id,
                    item_id,
                    customer_id,
                    actor_id,
                    event_type,
                    str(note).strip(),
                ),
            )
            return int(cursor.lastrowid)

    def list_animal_product_preferences(
        self, animal_id: int
    ) -> list[dict[str, Any]]:
        if self.connection.execute(
            "SELECT id FROM animals WHERE id = ?", (animal_id,)
        ).fetchone() is None:
            raise ValueError("Không tìm thấy thú cưng.")
        return [
            dict(row)
            for row in self.connection.execute(
                """
                SELECT preference.item_id, item.item_code, item.name,
                       preference.preference, preference.note,
                       preference.created_at, preference.updated_at
                FROM animal_product_preferences preference
                JOIN inventory_items item ON item.id = preference.item_id
                WHERE preference.animal_id = ?
                ORDER BY preference.updated_at DESC, item.name COLLATE NOCASE
                """,
                (animal_id,),
            ).fetchall()
        ]

    def save_animal_product_preference(
        self,
        animal_id: int,
        item_id: int,
        preference: str,
        actor_id: int | None,
        note: str,
    ) -> None:
        if preference not in {"LIKE", "AVOID"}:
            raise ValueError("Loại sở thích sản phẩm không hợp lệ.")
        if self.connection.execute(
            "SELECT id FROM animals WHERE id = ?", (animal_id,)
        ).fetchone() is None:
            raise ValueError("Không tìm thấy thú cưng.")
        if self.connection.execute(
            """
            SELECT p.item_id
            FROM product_recommendation_profiles p
            JOIN inventory_items item ON item.id = p.item_id
            WHERE p.item_id = ? AND item.is_active = 1
            """,
            (item_id,),
        ).fetchone() is None:
            raise ValueError("Sản phẩm cần có cấu hình gợi ý và đang hoạt động.")
        with self.connection:
            self.connection.execute(
                """
                INSERT INTO animal_product_preferences
                    (animal_id, item_id, preference, note, actor_id)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(animal_id, item_id) DO UPDATE SET
                    preference = excluded.preference,
                    note = excluded.note,
                    actor_id = excluded.actor_id,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (animal_id, item_id, preference, str(note).strip(), actor_id),
            )

    def delete_animal_product_preference(self, animal_id: int, item_id: int) -> None:
        with self.connection:
            cursor = self.connection.execute(
                """
                DELETE FROM animal_product_preferences
                WHERE animal_id = ? AND item_id = ?
                """,
                (animal_id, item_id),
            )
            if cursor.rowcount == 0:
                raise ValueError("Không tìm thấy ghi nhớ sở thích để xóa.")
