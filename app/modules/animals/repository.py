import sqlite3
from typing import Any

from app.modules.animals.breed_catalog import BREED_CATALOG
from app.modules.animals.constants import ANIMAL_PROFILE_FIELDS


class BreedRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def seed_default_catalog(self) -> int:
        inserted = 0
        with self.connection:
            for breed in BREED_CATALOG:
                profile = {
                    "species": breed.get("species", ""),
                    "breed_name": breed.get("breed_name", ""),
                    "breed_name_en": breed.get("breed_name_en", breed.get("breed_name", "")),
                    "origin_country": breed.get("origin_country", ""),
                    "origin_region": breed.get("origin_region", ""),
                    "climate": breed.get("climate", ""),
                    "suitable_environment": breed.get("suitable_environment", ""),
                    "exercise_level": breed.get("exercise_level", ""),
                    "activity_level": breed.get("activity_level", breed.get("exercise_level", "")),
                    "energy_level": breed.get("energy_level", breed.get("exercise_level", "")),
                    "protein_preferences": breed.get("protein_preferences", "Gà, cá, bò"),
                    "texture_preferences": breed.get("texture_preferences", "Hạt, pate"),
                    "flavor_preferences": breed.get("flavor_preferences", "Gà, cá"),
                    "treat_preferences": breed.get("treat_preferences", "Jerky, bánh thưởng"),
                    "heat_tolerance": breed.get("heat_tolerance", ""),
                    "cold_tolerance": breed.get("cold_tolerance", ""),
                    "size": breed.get("size", ""),
                    "adult_weight_kg": breed.get("adult_weight_kg", breed.get("adult_weight_kg", "")),
                    "lifespan_years": breed.get("lifespan_years", ""),
                    "suitable_home": breed.get("suitable_home", ""),
                    "exercise_requirement": breed.get("exercise_requirement", breed.get("suitable_environment", "")),
                    "preferred_home": breed.get("preferred_home", breed.get("suitable_home", "")),
                    "temperature_range": breed.get("temperature_range", breed.get("climate", "")),
                }
                columns = (
                    "species",
                    "breed_name",
                    "breed_name_en",
                    "origin_country",
                    "origin_region",
                    "climate",
                    "suitable_environment",
                    "exercise_level",
                    "activity_level",
                    "energy_level",
                    "protein_preferences",
                    "texture_preferences",
                    "flavor_preferences",
                    "treat_preferences",
                    "heat_tolerance",
                    "cold_tolerance",
                    "size",
                    "adult_weight_kg",
                    "lifespan_years",
                    "suitable_home",
                    "exercise_requirement",
                    "preferred_home",
                    "temperature_range",
                )
                placeholders = ", ".join("?" for _ in columns)
                values = tuple(profile[column] for column in columns)
                self.connection.execute(
                    f"INSERT OR IGNORE INTO breed_profiles ({', '.join(columns)}) VALUES ({placeholders})",
                    values,
                )
                inserted += 1
        return inserted

    def list_breeds(self, species: str | None = None) -> list[sqlite3.Row]:
        if species is None:
            query = "SELECT * FROM breed_profiles ORDER BY species, breed_name"
            params: tuple[Any, ...] = ()
        else:
            query = "SELECT * FROM breed_profiles WHERE species = ? ORDER BY breed_name"
            params = (species,)
        return self.connection.execute(query, params).fetchall()

    def get_breed(self, species: str, breed_name: str) -> sqlite3.Row | None:
        return self.connection.execute(
            "SELECT * FROM breed_profiles WHERE species = ? AND breed_name = ?",
            (species, breed_name),
        ).fetchone()


class AnimalRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def list_animals(
        self, search: str = "", status: str | None = None
    ) -> list[sqlite3.Row]:
        conditions: list[str] = []
        parameters: list[Any] = []
        if search.strip():
            pattern = f"%{search.strip()}%"
            conditions.append(
                "(a.animal_code LIKE ? OR a.name LIKE ? OR a.species LIKE ? OR a.breed LIKE ?)"
            )
            parameters.extend((pattern, pattern, pattern, pattern))
        if status:
            conditions.append("a.status = ?")
            parameters.append(status)

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        return self.connection.execute(
            f"""
            SELECT a.*, r.received_at, r.received_by
            FROM animals a
            LEFT JOIN animal_intake_receipts r ON r.animal_id = a.id
            {where_clause}
            ORDER BY a.id DESC
            """,
            parameters,
        ).fetchall()

    def get_animal(self, animal_id: int) -> sqlite3.Row | None:
        return self.connection.execute(
            """
            SELECT a.*, r.received_at, r.received_by
            FROM animals a
            LEFT JOIN animal_intake_receipts r ON r.animal_id = a.id
            WHERE a.id = ?
            """,
            (animal_id,),
        ).fetchone()

    def save_animal(self, values: dict[str, Any], animal_id: int | None = None) -> int:
        fields = ANIMAL_PROFILE_FIELDS
        defaults = {
            "breed": "",
            "gender": "Chưa rõ",
            "birth_date": "",
            "color": "",
            "weight": None,
            "origin": "",
            "purchase_price": 0,
            "sale_price": 0,
            "status": "PENDING_INSPECTION",
            "health_status": "Bình thường",
            "description": "",
            "supplier_name": "",
            "intake_date": "",
            "microchip_id": "",
            "cage_location": "",
            "diet": "",
            "feeding_schedule": "",
            "allergies": "",
            "vaccination_status": "",
            "last_vet_visit": "",
            "exercise_needs": "",
            "behavior": "",
        }
        data = [
            values[field] if field in values else defaults[field]
            for field in fields
        ]
        with self.connection:
            if animal_id is None:
                placeholders = ", ".join("?" for _ in fields)
                cursor = self.connection.execute(
                    f"INSERT INTO animals ({', '.join(fields)}) VALUES ({placeholders})",
                    data,
                )
                return int(cursor.lastrowid)

            active_cage = self.connection.execute(
                """
                SELECT c.name, c.accepted_species
                FROM animal_cage_assignments a
                JOIN cages c ON c.id = a.cage_id
                WHERE a.animal_id = ? AND a.released_at IS NULL
                """,
                (animal_id,),
            ).fetchone()
            if active_cage:
                if (
                    active_cage["accepted_species"]
                    and active_cage["accepted_species"].casefold()
                    != str(values["species"]).strip().casefold()
                ):
                    raise ValueError(
                        "Không thể đổi loài vì động vật đang ở chuồng chỉ nhận "
                        f"{active_cage['accepted_species']}."
                    )
                data[fields.index("cage_location")] = active_cage["name"]

            assignments = ", ".join(f"{field} = ?" for field in fields)
            self.connection.execute(
                f"""
                UPDATE animals SET {assignments}, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (*data, animal_id),
            )
            return animal_id

    def delete_animal(self, animal_id: int) -> None:
        with self.connection:
            self.connection.execute("DELETE FROM animals WHERE id = ?", (animal_id,))
