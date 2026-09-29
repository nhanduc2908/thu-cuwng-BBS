"""Nutrition and food domain for diet, allergen, and life-stage guidance."""

from app.modules.nutrition.recommendation_engine import recommend_foods_for_pet
from app.modules.nutrition.repository import FoodNutritionRepository

__all__ = ["FoodNutritionRepository", "recommend_foods_for_pet"]
