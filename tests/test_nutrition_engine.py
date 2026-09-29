from app.modules.nutrition.recommendation_engine import build_pet_nutrition_profile, recommend_foods_for_pet


def test_build_pet_nutrition_profile_uses_activity_and_age():
    profile = build_pet_nutrition_profile({
        'species': 'Dog',
        'age_months': 18,
        'weight_kg': 22,
        'activity_level': 'HIGH',
        'body_condition': 'NORMAL',
        'allergies': 'Chicken',
    })

    assert profile['species'] == 'DOG'
    assert profile['protein_level'] == 'HIGH'
    assert profile['energy_level'] == 'HIGH'
    assert 'Chicken' in profile['allergies']


def test_recommend_foods_for_pet_prioritizes_matching_species_and_profile():
    foods = [
        {
            'species': 'DOG',
            'product_name': 'Chicken adult dog food',
            'life_stage': 'ADULT',
            'food_type': 'DRY',
            'allergens': ['Chicken'],
            'nutrition': {'protein_percent': 28, 'fat_percent': 16, 'fiber_percent': 4},
        },
        {
            'species': 'CAT',
            'product_name': 'Salmon cat food',
            'life_stage': 'ADULT',
            'food_type': 'DRY',
            'allergens': ['Fish'],
            'nutrition': {'protein_percent': 30, 'fat_percent': 15, 'fiber_percent': 3},
        },
    ]

    pet = {
        'species': 'Dog',
        'age_months': 36,
        'weight_kg': 25,
        'activity_level': 'HIGH',
        'body_condition': 'NORMAL',
        'allergies': 'Beef',
    }

    result = recommend_foods_for_pet(pet, foods, limit=5)
    assert result[0]['product_name'] == 'Chicken adult dog food'
    assert result[0]['nutrition_score'] >= result[1]['nutrition_score']
