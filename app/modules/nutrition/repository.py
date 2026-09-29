from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from app.database import Database, get_db_connection


class FoodNutritionRepository:
    """Repository for food catalog, nutrient facts, and nutrition guidance."""

    def __init__(self, conn=None):
        if conn is not None:
            self.conn = conn
            return

        database_path = Path.home() / 'AppData' / 'Local' / 'PetStoreManagement' / 'pet_store.db'
        try:
            self.conn = Database(database_path).connection
        except Exception:
            self.conn = get_db_connection(database_path)

    def add_food(self, *, species: str, brand: str, product_name: str, food_type: str = 'DRY',
                 life_stage: str = 'ADULT', breed_size: str = '', target_weight_kg: Optional[float] = None,
                 product_code: str = '') -> int:
        cursor = self.conn.execute(
            """
            INSERT INTO food_catalog (
                species, brand, product_name, food_type, life_stage, breed_size,
                target_weight_kg, product_code
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (species, brand, product_name, food_type, life_stage, breed_size, target_weight_kg, product_code),
        )
        self.conn.commit()
        return int(cursor.lastrowid)

    def add_nutrition(self, *, food_id: int, calories_kcal_per_kg: Optional[float] = None,
                      protein_percent: Optional[float] = None, fat_percent: Optional[float] = None,
                      carbohydrate_percent: Optional[float] = None, fiber_percent: Optional[float] = None,
                      moisture_percent: Optional[float] = None, ash_percent: Optional[float] = None,
                      energy_density: Optional[float] = None, omega_3: Optional[float] = None,
                      omega_6: Optional[float] = None, taurine: Optional[float] = None,
                      calcium: Optional[float] = None, phosphorus: Optional[float] = None,
                      sodium: Optional[float] = None, potassium: Optional[float] = None,
                      zinc: Optional[float] = None, iron: Optional[float] = None) -> int:
        cursor = self.conn.execute(
            """
            INSERT INTO food_nutrition (
                food_id, calories_kcal_per_kg, protein_percent, fat_percent, carbohydrate_percent,
                fiber_percent, moisture_percent, ash_percent, energy_density, omega_3, omega_6,
                taurine, calcium, phosphorus, sodium, potassium, zinc, iron
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (food_id, calories_kcal_per_kg, protein_percent, fat_percent, carbohydrate_percent,
             fiber_percent, moisture_percent, ash_percent, energy_density, omega_3, omega_6,
             taurine, calcium, phosphorus, sodium, potassium, zinc, iron),
        )
        self.conn.commit()
        return int(cursor.lastrowid)

    def add_ingredient(self, *, food_id: int, ingredient_name: str, ingredient_group: str = 'PROTEIN',
                       percentage: Optional[float] = None, note: str = '') -> int:
        cursor = self.conn.execute(
            """
            INSERT INTO food_ingredients (food_id, ingredient_name, ingredient_group, percentage, note)
            VALUES (?, ?, ?, ?, ?)
            """,
            (food_id, ingredient_name, ingredient_group, percentage, note),
        )
        self.conn.commit()
        return int(cursor.lastrowid)

    def add_allergen(self, *, food_id: int, allergen_name: str, severity: str = 'MEDIUM', note: str = '') -> int:
        cursor = self.conn.execute(
            """
            INSERT INTO food_allergens (food_id, allergen_name, severity, note)
            VALUES (?, ?, ?, ?)
            """,
            (food_id, allergen_name, severity, note),
        )
        self.conn.commit()
        return int(cursor.lastrowid)

    def add_species_rule(self, *, food_id: int, species: str, note: str = '') -> int:
        cursor = self.conn.execute(
            """
            INSERT INTO food_species_rules (food_id, species, note)
            VALUES (?, ?, ?)
            """,
            (food_id, species, note),
        )
        self.conn.commit()
        return int(cursor.lastrowid)

    def add_life_stage_rule(self, *, food_id: int, life_stage: str, age_min_months: Optional[float] = None,
                            age_max_months: Optional[float] = None, target_weight_kg: Optional[float] = None,
                            recommendation: str = '') -> int:
        cursor = self.conn.execute(
            """
            INSERT INTO food_life_stage_rules (
                food_id, life_stage, age_min_months, age_max_months, target_weight_kg, recommendation
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (food_id, life_stage, age_min_months, age_max_months, target_weight_kg, recommendation),
        )
        self.conn.commit()
        return int(cursor.lastrowid)

    def add_health_rule(self, *, food_id: int, condition_name: str, recommended: int = 0, note: str = '') -> int:
        cursor = self.conn.execute(
            """
            INSERT INTO food_health_rules (food_id, condition_name, recommended, note)
            VALUES (?, ?, ?, ?)
            """,
            (food_id, condition_name, recommended, note),
        )
        self.conn.commit()
        return int(cursor.lastrowid)

    def create_nutrition_profile(self, *, pet_id: Optional[int], species: str, breed_name: str = '', age_months: Optional[int] = None,
                                weight_kg: Optional[float] = None, activity_level: str = 'MEDIUM',
                                body_condition: str = 'NORMAL', protein_level: str = 'MODERATE',
                                fat_level: str = 'MODERATE', fiber_level: str = 'MODERATE',
                                omega_3_required: int = 0, energy_level: str = 'MODERATE', notes: str = '') -> int:
        cursor = self.conn.execute(
            """
            INSERT INTO nutrition_profiles (
                pet_id, species, breed_name, age_months, weight_kg, activity_level,
                body_condition, protein_level, fat_level, fiber_level,
                omega_3_required, energy_level, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (pet_id, species, breed_name, age_months, weight_kg, activity_level, body_condition,
             protein_level, fat_level, fiber_level, omega_3_required, energy_level, notes),
        )
        self.conn.commit()
        return int(cursor.lastrowid)

    def get_food(self, food_id: int) -> Optional[Dict[str, Any]]:
        row = self.conn.execute(
            """
            SELECT * FROM food_catalog WHERE id = ?
            """,
            (food_id,),
        ).fetchone()
        if row is None:
            return None
        return dict(row)

    def list_foods_for_species(self, species: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        query = "SELECT * FROM food_catalog WHERE species = ? AND is_active = 1 ORDER BY brand, product_name"
        params: List[Any] = [species]
        if limit is not None:
            query += " LIMIT ?"
            params.append(limit)
        return [dict(row) for row in self.conn.execute(query, params).fetchall()]

    def get_food_nutrition(self, food_id: int) -> Optional[Dict[str, Any]]:
        row = self.conn.execute(
            "SELECT * FROM food_nutrition WHERE food_id = ? ORDER BY id DESC LIMIT 1",
            (food_id,),
        ).fetchone()
        if row is None:
            return None
        return dict(row)

    def get_food_ingredients(self, food_id: int) -> List[Dict[str, Any]]:
        rows = self.conn.execute(
            "SELECT * FROM food_ingredients WHERE food_id = ? ORDER BY ingredient_group, ingredient_name",
            (food_id,),
        ).fetchall()
        return [dict(row) for row in rows]

    def get_food_allergens(self, food_id: int) -> List[Dict[str, Any]]:
        rows = self.conn.execute(
            "SELECT * FROM food_allergens WHERE food_id = ? ORDER BY allergen_name",
            (food_id,),
        ).fetchall()
        return [dict(row) for row in rows]

    def get_food_life_stage_rules(self, food_id: int) -> List[Dict[str, Any]]:
        rows = self.conn.execute(
            "SELECT * FROM food_life_stage_rules WHERE food_id = ? ORDER BY life_stage",
            (food_id,),
        ).fetchall()
        return [dict(row) for row in rows]

    def get_food_species_rules(self, food_id: int) -> List[Dict[str, Any]]:
        rows = self.conn.execute(
            "SELECT * FROM food_species_rules WHERE food_id = ? ORDER BY species",
            (food_id,),
        ).fetchall()
        return [dict(row) for row in rows]

    def get_food_health_rules(self, food_id: int) -> List[Dict[str, Any]]:
        rows = self.conn.execute(
            "SELECT * FROM food_health_rules WHERE food_id = ? ORDER BY condition_name",
            (food_id,),
        ).fetchall()
        return [dict(row) for row in rows]

    def get_nutrition_profile(self, pet_id: Optional[int] = None, species: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        query = "SELECT * FROM nutrition_profiles WHERE 1=1"
        params: List[Any] = []
        if pet_id is not None:
            query += " AND pet_id = ?"
            params.append(pet_id)
        if species is not None:
            query += " AND species = ?"
            params.append(species)
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        rows = self.conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]
