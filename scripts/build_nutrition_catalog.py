from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.modules.animals.breed_catalog import BREED_CATALOG
from app.modules.nutrition.seed_data import (
    CAT_PRODUCTS,
    DOG_PRODUCTS,
    build_extended_food_products,
)
from app.modules.inventory.feeding_seed import FOOD_PROFILES


def build_catalog() -> dict[str, list[dict[str, object]]]:
    breeds: dict[tuple[str, str], dict[str, str]] = {}
    for item in BREED_CATALOG:
        species = "DOG" if item.get("species") == "Chó" else "CAT"
        name = item.get("breed_name", "")
        if name:
            breeds.setdefault((species, name), {**item, "species_code": species})

    products = DOG_PRODUCTS + CAT_PRODUCTS + build_extended_food_products()
    feeding_profiles = [
        {**profile, "species_code": "DOG" if profile["species"] == "Chó" else "CAT"}
        for profile in FOOD_PROFILES
        if profile["species"] in {"Chó", "Mèo"}
    ]
    return {
        "breeds": list(breeds.values()),
        "products": products,
        "feeding_profiles": feeding_profiles,
    }


def main() -> None:
    output = ROOT / "HTML" / "nutrition_products.html"
    html = output.read_text(encoding="utf-8")
    opening = '<script id="nutrition-catalog-data" type="application/json">'
    closing = "</script>"
    if html.count(opening) != 1:
        raise RuntimeError("Expected exactly one embedded catalog data block")

    content_start = html.index(opening) + len(opening)
    content_end = html.index(closing, content_start)
    catalog_json = json.dumps(
        build_catalog(), ensure_ascii=False, separators=(",", ":")
    )
    catalog_json = (
        catalog_json.replace("&", "\\u0026")
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
    )
    output.write_text(
        html[:content_start] + catalog_json + html[content_end:],
        encoding="utf-8",
    )
    print(f"Embedded catalog data in {output.relative_to(ROOT)}")


if __name__ == "__main__":
    main()