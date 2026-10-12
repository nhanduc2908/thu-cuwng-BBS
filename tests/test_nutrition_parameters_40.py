import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "HTML" / "data"


def test_nutrition_reference_has_40_unique_parameters_and_three_stages():
    reference = json.loads(
        (DATA_DIR / "nutrition_parameters_40.json").read_text(encoding="utf-8")
    )
    parameters = reference["parameters"]
    parameter_ids = [parameter["id"] for parameter in parameters]

    assert len(parameters) == 40
    assert len(set(parameter_ids)) == 40
    assert len(reference["stages"]) == 3
    assert {parameter["group"] for parameter in parameters} == {
        group["id"] for group in reference["groups"]
    }
    assert all(parameter["role"] and parameter["speciesNote"] for parameter in parameters)
    assert reference["stages"]["senior"]["senior"] is True


def test_every_breed_has_growth_adult_and_senior_profiles():
    catalog = json.loads(
        (DATA_DIR / "pet_breed_nutrition_profiles_200.json").read_text(encoding="utf-8")
    )
    expected_stage_ids = {
        "Chó": {"growth": "dog_growth", "adult": "dog_adult_maintenance", "senior": "dog_senior_individualized"},
        "Mèo": {"growth": "cat_growth", "adult": "cat_young_adult", "senior": "cat_senior"},
    }

    assert len(catalog["profiles"]) == 200
    assert len({profile["id"] for profile in catalog["profiles"]}) == 200
    for profile in catalog["profiles"]:
        stage_ids = {
            stage["nutritionGuidance"]["id"]
            for stage in profile["profile"]["partIII_lifeStageNutrition"]
        }
        assert set(expected_stage_ids[profile["speciesLabel"]].values()) <= stage_ids


def test_new_reference_page_is_linked_from_the_nutrition_catalog():
    page = (
        PROJECT_ROOT
        / "HTML"
        / "Trang thông số của các sản phẩm"
        / "nutrient-reference-40.html"
    ).read_text(encoding="utf-8")
    overview = (
        PROJECT_ROOT
        / "HTML"
        / "Trang thông số của các sản phẩm"
        / "nutrition-standards.html"
    ).read_text(encoding="utf-8")
    breed_script = (
        PROJECT_ROOT / "HTML" / "scripts" / "nutrition_standards.js"
    ).read_text(encoding="utf-8")

    assert "nutrition_parameters_40.js" in page
    assert "nutrition_parameters_40.css" in page
    assert "nutrient-reference-40.html" in overview
    assert "40 chỉ tiêu · 3 giai đoạn" in breed_script
    assert "URLSearchParams(window.location.search)" in (
        PROJECT_ROOT / "HTML" / "scripts" / "nutrition_parameters_40.js"
    ).read_text(encoding="utf-8")
