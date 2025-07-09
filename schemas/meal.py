from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime

class MealComponentBase(BaseModel):
    name: str = Field(examples=["Chicken Breast"], description="The name of the food item")
    calories: float = Field(examples=[165.0], description="The amount of calories in the food item")
    fat_g: float = Field(examples=[3.6], description="The amount of fat in grams")
    protein_g: float = Field(examples=[31.0], description="The amount of protein in grams")
    carbs_g: float = Field(examples=[0.0], description="The amount of carbs in grams")

class MealComponentForLLM(BaseModel):
    """Schema for LLM API calls (without examples field)"""
    name: str = Field(description="The name of the food item")
    calories: float = Field(description="The amount of calories in the food item")
    fat_g: float = Field(description="The amount of fat in grams")
    protein_g: float = Field(description="The amount of protein in grams")
    carbs_g: float = Field(description="The amount of carbs in grams")

class MealComponentCreate(MealComponentBase):
    pass

class MealComponentRead(MealComponentBase):
    component_id: UUID = Field(examples=["123e4567-e89b-12d3-a456-426614174001"])

class MealBase(BaseModel):
    meal_date: datetime = Field(examples=["2024-06-01T12:00:00Z"])
    description: Optional[str] = Field(default=None, examples=["Grilled chicken lunch"])

class MealCreate(MealBase):
    components: List[MealComponentCreate] = Field(examples=[[{"name": "Chicken Breast", "calories": 165.0, "fat_g": 3.6, "protein_g": 31.0, "carbs_g": 0.0}]])

class MealRead(MealBase):
    mealId: UUID = Field(..., alias="meal_id", examples=["123e4567-e89b-12d3-a456-426614174002"])
    components: List[MealComponentRead] = Field(examples=[[{"component_id": "123e4567-e89b-12d3-a456-426614174001", "name": "Chicken Breast", "calories": 165.0, "fat_g": 3.6, "protein_g": 31.0, "carbs_g": 0.0}]])
    created_at: datetime = Field(examples=["2024-06-01T12:05:00Z"])
    updated_at: datetime = Field(examples=["2024-06-01T12:10:00Z"])

class MealSummary(BaseModel):
    mealId: UUID = Field(..., alias="meal_id", examples=["123e4567-e89b-12d3-a456-426614174002"])
    meal_date: datetime = Field(examples=["2024-06-01T12:00:00Z"])
    description: Optional[str] = Field(default=None, examples=["Grilled chicken lunch"])
    total_calories: float = Field(examples=[165.0])

class MealAnalysisResponse(BaseModel):
    """Response schema for meal analysis endpoint"""
    components: List[MealComponentBase] = Field(
        description="List of analyzed meal components with estimated nutritional information",
        examples=[[
            {
                "name": "Oatmeal",
                "calories": 150.0,
                "fat_g": 3.0,
                "protein_g": 5.0,
                "carbs_g": 27.0
            },
            {
                "name": "Orange Juice",
                "calories": 110.0,
                "fat_g": 0.5,
                "protein_g": 2.0,
                "carbs_g": 25.0
            }
        ]]
    )

class MealAnalysisForLLM(BaseModel):
    """Schema for LLM API calls (without examples field)"""
    components: List[MealComponentForLLM] = Field(
        description="List of analyzed meal components with estimated nutritional information"
    ) 