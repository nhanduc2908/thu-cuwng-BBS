from __future__ import annotations

from app.modules.nutrition.repository import FoodNutritionRepository


def seed_sample_foods() -> None:
    repo = FoodNutritionRepository()

    foods = [
        {
            'species': 'DOG',
            'brand': 'Royal Canin',
            'product_name': 'Adult Mini Dry Dog Food',
            'food_type': 'DRY',
            'life_stage': 'ADULT',
            'breed_size': 'SMALL',
            'product_code': 'RC-ADULT-MINI-01',
        },
        {
            'species': 'DOG',
            'brand': 'Hill\'s Science Diet',
            'product_name': 'Adult Sensitive Stomach Chicken Recipe',
            'food_type': 'DRY',
            'life_stage': 'ADULT',
            'breed_size': 'ALL',
            'product_code': 'HSD-SS-CHICKEN-01',
        },
        {
            'species': 'CAT',
            'brand': 'Purina Pro Plan',
            'product_name': 'Adult Chicken & Rice Formula',
            'food_type': 'DRY',
            'life_stage': 'ADULT',
            'breed_size': 'ALL',
            'product_code': 'PP-ADULT-CHICKEN-01',
        },
        {
            'species': 'CAT',
            'brand': 'Whiskas',
            'product_name': 'Adult Salmon Dry Cat Food',
            'food_type': 'DRY',
            'life_stage': 'ADULT',
            'breed_size': 'ALL',
            'product_code': 'WHISKAS-SALMON-01',
        },
    ]

    for item in foods:
        food_id = repo.add_food(**item)

        if item['species'] == 'DOG':
            repo.add_nutrition(
                food_id=food_id,
                calories_kcal_per_kg=3700,
                protein_percent=26,
                fat_percent=15,
                carbohydrate_percent=38,
                fiber_percent=4,
                moisture_percent=10,
                ash_percent=7,
                energy_density=3.7,
                omega_3=1.1,
                omega_6=2.8,
                calcium=1.2,
                phosphorus=0.9,
                zinc=0.12,
                iron=0.1,
            )
            repo.add_ingredient(food_id=food_id, ingredient_name='Chicken meal', ingredient_group='PROTEIN', percentage=28)
            repo.add_ingredient(food_id=food_id, ingredient_name='Brown rice', ingredient_group='CARBOHYDRATE', percentage=22)
            repo.add_ingredient(food_id=food_id, ingredient_name='Fish oil', ingredient_group='FAT', percentage=6)
            repo.add_allergen(food_id=food_id, allergen_name='Chicken', severity='MEDIUM', note='Common protein source')
            repo.add_species_rule(food_id=food_id, species='DOG', note='Suitable for adult dogs')
            repo.add_life_stage_rule(food_id=food_id, life_stage='ADULT', recommendation='Feed according to weight and activity level')
            repo.add_health_rule(food_id=food_id, condition_name='DIGESTIVE_SENSITIVE', recommended=1, note='Can be suitable for sensitive stomachs under vet guidance')
        else:
            repo.add_nutrition(
                food_id=food_id,
                calories_kcal_per_kg=3600,
                protein_percent=31,
                fat_percent=16,
                carbohydrate_percent=34,
                fiber_percent=3.5,
                moisture_percent=9,
                ash_percent=6.5,
                energy_density=3.6,
                omega_3=0.9,
                omega_6=2.5,
                taurine=0.12,
                calcium=1.0,
                phosphorus=0.8,
                zinc=0.1,
                iron=0.08,
            )
            repo.add_ingredient(food_id=food_id, ingredient_name='Chicken', ingredient_group='PROTEIN', percentage=30)
            repo.add_ingredient(food_id=food_id, ingredient_name='Rice', ingredient_group='CARBOHYDRATE', percentage=25)
            repo.add_ingredient(food_id=food_id, ingredient_name='Salmon oil', ingredient_group='FAT', percentage=5)
            repo.add_allergen(food_id=food_id, allergen_name='Fish', severity='MEDIUM', note='Check if cat has sensitivity')
            repo.add_species_rule(food_id=food_id, species='CAT', note='Suitable for adult cats')
            repo.add_life_stage_rule(food_id=food_id, life_stage='ADULT', recommendation='Provide balanced nutrition for maintenance')
            repo.add_health_rule(food_id=food_id, condition_name='HAIRBALL', recommended=1, note='May support coat and digestion in adult cats')

    repo.create_nutrition_profile(
        pet_id=None,
        species='DOG',
        breed_name='Golden Retriever',
        age_months=48,
        weight_kg=30,
        activity_level='HIGH',
        body_condition='NORMAL',
        protein_level='HIGH',
        fat_level='MODERATE',
        fiber_level='MODERATE',
        omega_3_required=1,
        energy_level='HIGH',
        notes='High activity and large breed profile',
    )

    repo.create_nutrition_profile(
        pet_id=None,
        species='CAT',
        breed_name='Siamese',
        age_months=36,
        weight_kg=4.5,
        activity_level='MEDIUM',
        body_condition='NORMAL',
        protein_level='HIGH',
        fat_level='MODERATE',
        fiber_level='LOW',
        omega_3_required=1,
        energy_level='MEDIUM',
        notes='Lean body composition with moderate activity',
    )
