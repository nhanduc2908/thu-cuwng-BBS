from __future__ import annotations

from app.modules.nutrition.repository import FoodNutritionRepository


DOG_PRODUCTS = [
    {
        'species': 'DOG', 'brand': 'Royal Canin', 'product_name': 'Adult Mini Dry Dog Food', 'food_type': 'DRY', 'life_stage': 'ADULT', 'breed_size': 'SMALL', 'product_code': 'RC-ADULT-MINI-01',
        'nutrition': {'calories_kcal_per_kg': 3700, 'protein_percent': 28, 'fat_percent': 16, 'carbohydrate_percent': 36, 'fiber_percent': 3.5, 'moisture_percent': 10, 'ash_percent': 6.5, 'energy_density': 3.7, 'omega_3': 0.85, 'omega_6': 2.5, 'taurine': 0.0, 'calcium': 1.2, 'phosphorus': 0.9, 'zinc': 0.15},
        'allergens': ['Chicken', 'Corn'],
    },
    {
        'species': 'DOG', 'brand': 'Hill\'s Science Diet', 'product_name': 'Adult Sensitive Stomach Chicken Recipe', 'food_type': 'DRY', 'life_stage': 'ADULT', 'breed_size': 'ALL', 'product_code': 'HSD-SS-CHICKEN-01',
        'nutrition': {'calories_kcal_per_kg': 3520, 'protein_percent': 24, 'fat_percent': 14, 'carbohydrate_percent': 40, 'fiber_percent': 4.2, 'moisture_percent': 10, 'ash_percent': 7.0, 'energy_density': 3.5, 'omega_3': 0.7, 'omega_6': 2.2, 'taurine': 0.0, 'calcium': 1.0, 'phosphorus': 0.8, 'zinc': 0.12},
        'allergens': ['Chicken'],
    },
    {
        'species': 'DOG', 'brand': 'Purina Pro Plan', 'product_name': 'Adult Large Breed Chicken & Rice', 'food_type': 'DRY', 'life_stage': 'ADULT', 'breed_size': 'LARGE', 'product_code': 'PP-LARGE-CHICKEN-01',
        'nutrition': {'calories_kcal_per_kg': 3650, 'protein_percent': 26, 'fat_percent': 15, 'carbohydrate_percent': 38, 'fiber_percent': 4.0, 'moisture_percent': 10, 'ash_percent': 7.2, 'energy_density': 3.65, 'omega_3': 0.9, 'omega_6': 2.6, 'taurine': 0.0, 'calcium': 1.1, 'phosphorus': 0.9, 'zinc': 0.13},
        'allergens': ['Chicken', 'Rice'],
    },
    {
        'species': 'DOG', 'brand': 'Pedigree', 'product_name': 'Adult Beef & Vegetable', 'food_type': 'DRY', 'life_stage': 'ADULT', 'breed_size': 'ALL', 'product_code': 'PED-BEEF-01',
        'nutrition': {'calories_kcal_per_kg': 3300, 'protein_percent': 21, 'fat_percent': 9, 'carbohydrate_percent': 45, 'fiber_percent': 5, 'moisture_percent': 10, 'ash_percent': 7.5, 'energy_density': 3.3, 'omega_3': 0.5, 'omega_6': 1.9, 'taurine': 0.0, 'calcium': 0.9, 'phosphorus': 0.7, 'zinc': 0.11},
        'allergens': ['Beef'],
    },
    {
        'species': 'DOG', 'brand': 'Blue Buffalo', 'product_name': 'Life Protection Formula Chicken & Brown Rice', 'food_type': 'DRY', 'life_stage': 'ADULT', 'breed_size': 'ALL', 'product_code': 'BB-CHICKEN-BR-01',
        'nutrition': {'calories_kcal_per_kg': 3540, 'protein_percent': 24, 'fat_percent': 14, 'carbohydrate_percent': 39, 'fiber_percent': 5, 'moisture_percent': 9, 'ash_percent': 7.8, 'energy_density': 3.54, 'omega_3': 0.8, 'omega_6': 2.6, 'taurine': 0.0, 'calcium': 1.1, 'phosphorus': 0.8, 'zinc': 0.12},
        'allergens': ['Chicken', 'Grain'],
    },
    {
        'species': 'DOG', 'brand': 'Wellness', 'product_name': 'Core Natural Chicken & Oat Recipe', 'food_type': 'DRY', 'life_stage': 'ADULT', 'breed_size': 'ALL', 'product_code': 'WL-CORE-CHICKEN-01',
        'nutrition': {'calories_kcal_per_kg': 3600, 'protein_percent': 27, 'fat_percent': 15, 'carbohydrate_percent': 35, 'fiber_percent': 4.5, 'moisture_percent': 10, 'ash_percent': 6.8, 'energy_density': 3.6, 'omega_3': 0.9, 'omega_6': 2.7, 'taurine': 0.0, 'calcium': 1.2, 'phosphorus': 0.9, 'zinc': 0.14},
        'allergens': ['Chicken', 'Oats'],
    },
    {
        'species': 'DOG', 'brand': 'Nutro', 'product_name': 'Adult Chicken & Brown Rice Recipe', 'food_type': 'DRY', 'life_stage': 'ADULT', 'breed_size': 'ALL', 'product_code': 'NUTRO-CHICKEN-01',
        'nutrition': {'calories_kcal_per_kg': 3490, 'protein_percent': 23, 'fat_percent': 12, 'carbohydrate_percent': 41, 'fiber_percent': 4.0, 'moisture_percent': 10, 'ash_percent': 6.5, 'energy_density': 3.49, 'omega_3': 0.75, 'omega_6': 2.2, 'taurine': 0.0, 'calcium': 1.0, 'phosphorus': 0.8, 'zinc': 0.12},
        'allergens': ['Chicken'],
    },
    {
        'species': 'DOG', 'brand': 'Iams', 'product_name': 'Proactive Health Adult Chicken', 'food_type': 'DRY', 'life_stage': 'ADULT', 'breed_size': 'ALL', 'product_code': 'IAMS-CHICKEN-01',
        'nutrition': {'calories_kcal_per_kg': 3440, 'protein_percent': 22, 'fat_percent': 12, 'carbohydrate_percent': 42, 'fiber_percent': 3.8, 'moisture_percent': 10, 'ash_percent': 6.8, 'energy_density': 3.44, 'omega_3': 0.7, 'omega_6': 2.2, 'taurine': 0.0, 'calcium': 0.95, 'phosphorus': 0.8, 'zinc': 0.1},
        'allergens': ['Chicken'],
    },
    {
        'species': 'DOG', 'brand': 'Canagan', 'product_name': 'Free Range Chicken & Venison', 'food_type': 'DRY', 'life_stage': 'ADULT', 'breed_size': 'ALL', 'product_code': 'CANAGAN-CHICKEN-01',
        'nutrition': {'calories_kcal_per_kg': 3750, 'protein_percent': 29, 'fat_percent': 17, 'carbohydrate_percent': 30, 'fiber_percent': 3.8, 'moisture_percent': 10, 'ash_percent': 6.7, 'energy_density': 3.75, 'omega_3': 0.9, 'omega_6': 2.7, 'taurine': 0.0, 'calcium': 1.2, 'phosphorus': 0.9, 'zinc': 0.14},
        'allergens': ['Chicken', 'Venison'],
    },
    {
        'species': 'DOG', 'brand': 'Acana', 'product_name': 'Regionals Puppy Recipe', 'food_type': 'DRY', 'life_stage': 'PUPPY', 'breed_size': 'ALL', 'product_code': 'ACANA-PUPPY-01',
        'nutrition': {'calories_kcal_per_kg': 3800, 'protein_percent': 31, 'fat_percent': 18, 'carbohydrate_percent': 28, 'fiber_percent': 4.2, 'moisture_percent': 10, 'ash_percent': 7.1, 'energy_density': 3.8, 'omega_3': 0.95, 'omega_6': 2.9, 'taurine': 0.0, 'calcium': 1.3, 'phosphorus': 1.0, 'zinc': 0.15},
        'allergens': ['Chicken'],
    },
    {
        'species': 'DOG', 'brand': 'Eukanuba', 'product_name': 'Adult Large Breed Formula', 'food_type': 'DRY', 'life_stage': 'ADULT', 'breed_size': 'LARGE', 'product_code': 'EUK-LARGE-01',
        'nutrition': {'calories_kcal_per_kg': 3620, 'protein_percent': 25, 'fat_percent': 14, 'carbohydrate_percent': 39, 'fiber_percent': 4.5, 'moisture_percent': 10, 'ash_percent': 6.9, 'energy_density': 3.62, 'omega_3': 0.8, 'omega_6': 2.4, 'taurine': 0.0, 'calcium': 1.0, 'phosphorus': 0.8, 'zinc': 0.12},
        'allergens': ['Chicken'],
    },
    {
        'species': 'DOG', 'brand': 'Forthglade', 'product_name': 'Adult Salmon & Sweet Potato', 'food_type': 'WET', 'life_stage': 'ADULT', 'breed_size': 'ALL', 'product_code': 'FG-SALMON-01',
        'nutrition': {'calories_kcal_per_kg': 3000, 'protein_percent': 22, 'fat_percent': 12, 'carbohydrate_percent': 24, 'fiber_percent': 1.8, 'moisture_percent': 78, 'ash_percent': 2.8, 'energy_density': 3.0, 'omega_3': 0.9, 'omega_6': 1.8, 'taurine': 0.0, 'calcium': 0.9, 'phosphorus': 0.7, 'zinc': 0.09},
        'allergens': ['Salmon'],
    },
    {
        'species': 'DOG', 'brand': 'James Wellbeloved', 'product_name': 'Turkey & Rice Adult Dog Food', 'food_type': 'DRY', 'life_stage': 'ADULT', 'breed_size': 'ALL', 'product_code': 'JW-TURKEY-01',
        'nutrition': {'calories_kcal_per_kg': 3410, 'protein_percent': 23, 'fat_percent': 13, 'carbohydrate_percent': 40, 'fiber_percent': 4.0, 'moisture_percent': 9.5, 'ash_percent': 6.9, 'energy_density': 3.41, 'omega_3': 0.65, 'omega_6': 2.1, 'taurine': 0.0, 'calcium': 1.0, 'phosphorus': 0.8, 'zinc': 0.11},
        'allergens': ['Turkey'],
    },
    {
        'species': 'DOG', 'brand': 'Earthborn Holistic', 'product_name': 'Smaller Breed Chicken & Barley', 'food_type': 'DRY', 'life_stage': 'ADULT', 'breed_size': 'SMALL', 'product_code': 'EBH-CHICKEN-BARLEY-01',
        'nutrition': {'calories_kcal_per_kg': 3650, 'protein_percent': 28, 'fat_percent': 15, 'carbohydrate_percent': 36, 'fiber_percent': 4.5, 'moisture_percent': 9, 'ash_percent': 6.4, 'energy_density': 3.65, 'omega_3': 0.8, 'omega_6': 2.7, 'taurine': 0.0, 'calcium': 1.2, 'phosphorus': 0.9, 'zinc': 0.13},
        'allergens': ['Chicken', 'Barley'],
    },
    {
        'species': 'DOG', 'brand': 'Alpha Spirit', 'product_name': 'Adult Grain Free Salmon', 'food_type': 'DRY', 'life_stage': 'ADULT', 'breed_size': 'ALL', 'product_code': 'ALPHA-SALMON-01',
        'nutrition': {'calories_kcal_per_kg': 3700, 'protein_percent': 30, 'fat_percent': 16, 'carbohydrate_percent': 24, 'fiber_percent': 4.2, 'moisture_percent': 10, 'ash_percent': 6.3, 'energy_density': 3.7, 'omega_3': 1.1, 'omega_6': 2.8, 'taurine': 0.0, 'calcium': 1.3, 'phosphorus': 1.0, 'zinc': 0.14},
        'allergens': ['Salmon'],
    },
    {
        'species': 'DOG', 'brand': 'Farmina', 'product_name': 'N&D Chicken & Pomegranate', 'food_type': 'DRY', 'life_stage': 'ADULT', 'breed_size': 'ALL', 'product_code': 'FARMINA-CHICKEN-01',
        'nutrition': {'calories_kcal_per_kg': 3600, 'protein_percent': 28, 'fat_percent': 15, 'carbohydrate_percent': 28, 'fiber_percent': 3.8, 'moisture_percent': 9, 'ash_percent': 6.5, 'energy_density': 3.6, 'omega_3': 1.0, 'omega_6': 2.6, 'taurine': 0.0, 'calcium': 1.2, 'phosphorus': 0.9, 'zinc': 0.14},
        'allergens': ['Chicken'],
    },
]

CAT_PRODUCTS = [
    {
        'species': 'CAT', 'brand': 'Purina Pro Plan', 'product_name': 'Adult Chicken & Rice Formula', 'food_type': 'DRY', 'life_stage': 'ADULT', 'breed_size': 'ALL', 'product_code': 'PP-CAT-CHICKEN-01',
        'nutrition': {'calories_kcal_per_kg': 3600, 'protein_percent': 32, 'fat_percent': 16, 'carbohydrate_percent': 35, 'fiber_percent': 3.5, 'moisture_percent': 9, 'ash_percent': 6.8, 'energy_density': 3.6, 'omega_3': 0.8, 'omega_6': 2.5, 'taurine': 0.15, 'calcium': 1.0, 'phosphorus': 0.8, 'zinc': 0.11},
        'allergens': ['Chicken'],
    },
    {
        'species': 'CAT', 'brand': 'Whiskas', 'product_name': 'Adult Salmon Dry Cat Food', 'food_type': 'DRY', 'life_stage': 'ADULT', 'breed_size': 'ALL', 'product_code': 'WHISKAS-SALMON-01',
        'nutrition': {'calories_kcal_per_kg': 3500, 'protein_percent': 29, 'fat_percent': 15, 'carbohydrate_percent': 38, 'fiber_percent': 3.0, 'moisture_percent': 9, 'ash_percent': 6.0, 'energy_density': 3.5, 'omega_3': 0.9, 'omega_6': 2.4, 'taurine': 0.14, 'calcium': 0.9, 'phosphorus': 0.7, 'zinc': 0.10},
        'allergens': ['Fish'],
    },
    {
        'species': 'CAT', 'brand': 'Royal Canin', 'product_name': 'Feline Adult Indoor Dry Food', 'food_type': 'DRY', 'life_stage': 'ADULT', 'breed_size': 'ALL', 'product_code': 'RC-CAT-INDOOR-01',
        'nutrition': {'calories_kcal_per_kg': 3400, 'protein_percent': 30, 'fat_percent': 13, 'carbohydrate_percent': 31, 'fiber_percent': 5.5, 'moisture_percent': 8, 'ash_percent': 6.9, 'energy_density': 3.4, 'omega_3': 0.7, 'omega_6': 2.3, 'taurine': 0.14, 'calcium': 1.0, 'phosphorus': 0.8, 'zinc': 0.10},
        'allergens': ['Chicken'],
    },
    {
        'species': 'CAT', 'brand': 'Hill\'s Science Diet', 'product_name': 'Adult Sensitive Stomach Chicken Recipe', 'food_type': 'DRY', 'life_stage': 'ADULT', 'breed_size': 'ALL', 'product_code': 'HSD-CAT-SS-01',
        'nutrition': {'calories_kcal_per_kg': 3550, 'protein_percent': 31, 'fat_percent': 15, 'carbohydrate_percent': 29, 'fiber_percent': 4.2, 'moisture_percent': 8, 'ash_percent': 6.5, 'energy_density': 3.55, 'omega_3': 0.8, 'omega_6': 2.4, 'taurine': 0.15, 'calcium': 1.0, 'phosphorus': 0.8, 'zinc': 0.11},
        'allergens': ['Chicken'],
    },
    {
        'species': 'CAT', 'brand': 'Blue Buffalo', 'product_name': 'Healthy Gourmet Chicken Recipe', 'food_type': 'DRY', 'life_stage': 'ADULT', 'breed_size': 'ALL', 'product_code': 'BB-CAT-CHICKEN-01',
        'nutrition': {'calories_kcal_per_kg': 3590, 'protein_percent': 33, 'fat_percent': 15, 'carbohydrate_percent': 30, 'fiber_percent': 4.5, 'moisture_percent': 9, 'ash_percent': 6.7, 'energy_density': 3.59, 'omega_3': 0.9, 'omega_6': 2.6, 'taurine': 0.17, 'calcium': 1.1, 'phosphorus': 0.9, 'zinc': 0.12},
        'allergens': ['Chicken'],
    },
    {
        'species': 'CAT', 'brand': 'Wellness', 'product_name': 'Complete Health Chicken Recipe', 'food_type': 'DRY', 'life_stage': 'ADULT', 'breed_size': 'ALL', 'product_code': 'WL-CAT-CHICKEN-01',
        'nutrition': {'calories_kcal_per_kg': 3670, 'protein_percent': 34, 'fat_percent': 16, 'carbohydrate_percent': 28, 'fiber_percent': 4.0, 'moisture_percent': 8, 'ash_percent': 6.8, 'energy_density': 3.67, 'omega_3': 0.9, 'omega_6': 2.7, 'taurine': 0.16, 'calcium': 1.1, 'phosphorus': 0.8, 'zinc': 0.12},
        'allergens': ['Chicken'],
    },
    {
        'species': 'CAT', 'brand': 'Nutro', 'product_name': 'Adult Salmon & Brown Rice Recipe', 'food_type': 'DRY', 'life_stage': 'ADULT', 'breed_size': 'ALL', 'product_code': 'NUTRO-CAT-SALMON-01',
        'nutrition': {'calories_kcal_per_kg': 3560, 'protein_percent': 31, 'fat_percent': 14, 'carbohydrate_percent': 32, 'fiber_percent': 4.0, 'moisture_percent': 8.5, 'ash_percent': 6.4, 'energy_density': 3.56, 'omega_3': 0.9, 'omega_6': 2.4, 'taurine': 0.15, 'calcium': 1.0, 'phosphorus': 0.8, 'zinc': 0.10},
        'allergens': ['Fish'],
    },
    {
        'species': 'CAT', 'brand': 'Iams', 'product_name': 'Proactive Health Adult Salmon', 'food_type': 'DRY', 'life_stage': 'ADULT', 'breed_size': 'ALL', 'product_code': 'IAMS-CAT-SALMON-01',
        'nutrition': {'calories_kcal_per_kg': 3480, 'protein_percent': 30, 'fat_percent': 13, 'carbohydrate_percent': 33, 'fiber_percent': 3.8, 'moisture_percent': 8, 'ash_percent': 6.6, 'energy_density': 3.48, 'omega_3': 0.8, 'omega_6': 2.1, 'taurine': 0.15, 'calcium': 0.9, 'phosphorus': 0.7, 'zinc': 0.10},
        'allergens': ['Fish'],
    },
    {
        'species': 'CAT', 'brand': 'Acana', 'product_name': 'Cat & Kitten Recipe', 'food_type': 'DRY', 'life_stage': 'KITTEN', 'breed_size': 'ALL', 'product_code': 'ACANA-KITTEN-01',
        'nutrition': {'calories_kcal_per_kg': 3800, 'protein_percent': 36, 'fat_percent': 18, 'carbohydrate_percent': 24, 'fiber_percent': 4.0, 'moisture_percent': 10, 'ash_percent': 7.0, 'energy_density': 3.8, 'omega_3': 1.0, 'omega_6': 2.8, 'taurine': 0.17, 'calcium': 1.2, 'phosphorus': 1.0, 'zinc': 0.13},
        'allergens': ['Chicken'],
    },
    {
        'species': 'CAT', 'brand': 'Eukanuba', 'product_name': 'Adult Hairball Control Formula', 'food_type': 'DRY', 'life_stage': 'ADULT', 'breed_size': 'ALL', 'product_code': 'EUK-CAT-HAIRBALL-01',
        'nutrition': {'calories_kcal_per_kg': 3500, 'protein_percent': 31, 'fat_percent': 14, 'carbohydrate_percent': 30, 'fiber_percent': 6.5, 'moisture_percent': 8, 'ash_percent': 6.8, 'energy_density': 3.5, 'omega_3': 0.8, 'omega_6': 2.2, 'taurine': 0.15, 'calcium': 1.0, 'phosphorus': 0.8, 'zinc': 0.11},
        'allergens': ['Chicken'],
    },
    {
        'species': 'CAT', 'brand': 'Forthglade', 'product_name': 'Adult Tuna & Chicken Wet Food', 'food_type': 'WET', 'life_stage': 'ADULT', 'breed_size': 'ALL', 'product_code': 'FG-CAT-TUNA-01',
        'nutrition': {'calories_kcal_per_kg': 2900, 'protein_percent': 24, 'fat_percent': 11, 'carbohydrate_percent': 20, 'fiber_percent': 1.5, 'moisture_percent': 78, 'ash_percent': 2.6, 'energy_density': 2.9, 'omega_3': 0.7, 'omega_6': 1.8, 'taurine': 0.12, 'calcium': 0.9, 'phosphorus': 0.7, 'zinc': 0.09},
        'allergens': ['Fish', 'Chicken'],
    },
    {
        'species': 'CAT', 'brand': 'James Wellbeloved', 'product_name': 'Turkey & Rice Kitten Food', 'food_type': 'DRY', 'life_stage': 'KITTEN', 'breed_size': 'ALL', 'product_code': 'JW-CAT-TURKEY-01',
        'nutrition': {'calories_kcal_per_kg': 3650, 'protein_percent': 35, 'fat_percent': 17, 'carbohydrate_percent': 30, 'fiber_percent': 3.5, 'moisture_percent': 9, 'ash_percent': 6.9, 'energy_density': 3.65, 'omega_3': 0.9, 'omega_6': 2.5, 'taurine': 0.17, 'calcium': 1.2, 'phosphorus': 1.0, 'zinc': 0.12},
        'allergens': ['Turkey'],
    },
    {
        'species': 'CAT', 'brand': 'Farmina', 'product_name': 'N&D Chicken & Pumpkin', 'food_type': 'DRY', 'life_stage': 'ADULT', 'breed_size': 'ALL', 'product_code': 'FARMINA-CAT-CHICKEN-01',
        'nutrition': {'calories_kcal_per_kg': 3600, 'protein_percent': 32, 'fat_percent': 15, 'carbohydrate_percent': 29, 'fiber_percent': 4.0, 'moisture_percent': 8.5, 'ash_percent': 6.5, 'energy_density': 3.6, 'omega_3': 0.9, 'omega_6': 2.6, 'taurine': 0.16, 'calcium': 1.0, 'phosphorus': 0.8, 'zinc': 0.11},
        'allergens': ['Chicken'],
    },
]


def seed_sample_foods() -> None:
    repo = FoodNutritionRepository()
    for item in DOG_PRODUCTS + CAT_PRODUCTS:
        food_id = repo.add_food(
            species=item['species'],
            brand=item['brand'],
            product_name=item['product_name'],
            food_type=item['food_type'],
            life_stage=item['life_stage'],
            breed_size=item['breed_size'],
            product_code=item['product_code'],
        )
        nutrition = item.get('nutrition', {})
        repo.add_nutrition(
            food_id=food_id,
            calories_kcal_per_kg=nutrition.get('calories_kcal_per_kg'),
            protein_percent=nutrition.get('protein_percent'),
            fat_percent=nutrition.get('fat_percent'),
            carbohydrate_percent=nutrition.get('carbohydrate_percent'),
            fiber_percent=nutrition.get('fiber_percent'),
            moisture_percent=nutrition.get('moisture_percent'),
            ash_percent=nutrition.get('ash_percent'),
            energy_density=nutrition.get('energy_density'),
            omega_3=nutrition.get('omega_3'),
            omega_6=nutrition.get('omega_6'),
            taurine=nutrition.get('taurine'),
            calcium=nutrition.get('calcium'),
            phosphorus=nutrition.get('phosphorus'),
            sodium=None,
            potassium=None,
            zinc=nutrition.get('zinc'),
            iron=None,
        )
        for allergen in item.get('allergens', []):
            repo.add_allergen(food_id=food_id, allergen_name=allergen, severity='MEDIUM', note='Check for pet sensitivity')
        repo.add_species_rule(food_id=food_id, species=item['species'], note='Suitable for species-specific nutrition support')
        repo.add_life_stage_rule(food_id=food_id, life_stage=item['life_stage'], recommendation='Use according to age, activity, and health status')

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
