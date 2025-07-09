from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, HTTPBearer
from typing import List
from uuid import UUID
from utils.database import get_db
from models.meal import Meal, MealComponent
from models.user import User
from schemas.meal import MealCreate, MealComponentCreate, MealComponentRead, MealRead, MealSummary, MealAnalysisResponse, MealAnalysisForLLM
from jose import JWTError, jwt
from settings import settings
from datetime import datetime
from utils.llm import client

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

# Helper to get current user from JWT
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = str(payload.get("sub"))  # Ensure user_id is always a string
        if not user_id:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.user_id == user_id).first()
    if user is None:
        raise credentials_exception
    return user

# POST /analyze (dummy implementation)
@router.post("/analyze", status_code=200, response_model=MealAnalysisResponse)
def analyze_meal(request: dict, current_user: User = Depends(get_current_user)):
    description = request.get("description")
    if not isinstance(description, str):
        raise HTTPException(status_code=400, detail="description must be a string")


    # Check if Google API client is available
    if client is None:
        raise HTTPException(
            status_code=503, 
            detail="Meal analysis service is not available. Please check Google API configuration."
        )
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"Identify the food items in the following description and break into components and estimate the nutritional information for each component. If no components are detected, return an empty list. Description: {description}",
            config={
                "response_mime_type": "application/json",
                "response_schema": MealAnalysisForLLM,
            },
        )
        
        # Parse the LLM response
        if response.text:
            llm_result = MealAnalysisForLLM.model_validate_json(response.text)
            # Convert to MealAnalysisResponse format
            return MealAnalysisResponse(
                components=[
                    MealComponentCreate(
                        name=comp.name,
                        calories=comp.calories,
                        fat_g=comp.fat_g,
                        protein_g=comp.protein_g,
                        carbs_g=comp.carbs_g
                    ) for comp in llm_result.components
                ]
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to analyze meal. Please try again."
            )
    except Exception as e:
        print(f"LLM analysis error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to analyze meal. Please try again later."
        )

# POST / (Save a Meal)
@router.post("/", status_code=201)
def create_meal(meal: MealCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_meal = Meal(
        user_id=current_user.user_id,
        meal_date=meal.meal_date,
        description=meal.description
    )
    db.add(db_meal)
    db.commit()
    db.refresh(db_meal)
    for comp in meal.components:
        db_comp = MealComponent(
            meal_id=db_meal.meal_id,
            name=comp.name,
            calories=comp.calories,
            fat_g=comp.fat_g,
            protein_g=comp.protein_g,
            carbs_g=comp.carbs_g
        )
        db.add(db_comp)
    db.commit()
    return {"mealId": db_meal.meal_id, "message": "Meal saved successfully."}

# GET / (Get All Meals for a User)
@router.get("/", status_code=200)
def get_meals(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    meals = db.query(Meal).filter(Meal.user_id == current_user.user_id).order_by(Meal.meal_date.desc()).all()
    result = []
    for meal in meals:
        total_calories = db.query(MealComponent).filter(MealComponent.meal_id == meal.meal_id).all()
        def to_float(val):
            try:
                return float(val)
            except Exception:
                return val.__float__() if hasattr(val, "__float__") else 0.0
        total_calories_sum = sum([to_float(c.calories) for c in total_calories])
        result.append({
            "mealId": meal.meal_id,
            "meal_date": meal.meal_date,
            "description": meal.description,
            "total_calories": total_calories_sum
        })
    return result

# GET /:mealId (Get a Specific Meal)
@router.get("/{meal_id}", status_code=200)
def get_meal(meal_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    meal = db.query(Meal).filter(Meal.meal_id == meal_id, Meal.user_id == current_user.user_id).first()
    if not meal:
        raise HTTPException(status_code=404, detail="Meal not found")
    components = db.query(MealComponent).filter(MealComponent.meal_id == meal.meal_id).all()
    def to_float(val):
        try:
            return float(val)
        except Exception:
            return val.__float__() if hasattr(val, "__float__") else 0.0
    return {
        "mealId": meal.meal_id,
        "meal_date": meal.meal_date,
        "description": meal.description,
        "components": [
            {
                "name": c.name,
                "calories": to_float(c.calories),
                "fat_g": to_float(c.fat_g),
                "protein_g": to_float(c.protein_g),
                "carbs_g": to_float(c.carbs_g)
            } for c in components
        ]
    }

# PUT /:mealId (Update a Meal)
@router.put("/{meal_id}", status_code=200)
def update_meal(meal_id: UUID, meal: MealCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_meal = db.query(Meal).filter(Meal.meal_id == meal_id, Meal.user_id == current_user.user_id).first()
    if not db_meal:
        raise HTTPException(status_code=404, detail="Meal not found")
    setattr(db_meal, 'meal_date', meal.meal_date)
    setattr(db_meal, 'description', meal.description)
    setattr(db_meal, 'updated_at', datetime.utcnow())
    db.query(MealComponent).filter(MealComponent.meal_id == meal_id).delete()
    db.commit()
    for comp in meal.components:
        db_comp = MealComponent(
            meal_id=db_meal.meal_id,
            name=comp.name,
            calories=comp.calories,
            fat_g=comp.fat_g,
            protein_g=comp.protein_g,
            carbs_g=comp.carbs_g
        )
        db.add(db_comp)
    db.commit()
    return {"mealId": db_meal.meal_id, "message": "Meal updated successfully."}

# DELETE /:mealId (Delete a Meal)
@router.delete("/{meal_id}", status_code=204)
def delete_meal(meal_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_meal = db.query(Meal).filter(Meal.meal_id == meal_id, Meal.user_id == current_user.user_id).first()
    if not db_meal:
        raise HTTPException(status_code=404, detail="Meal not found")
    db.query(MealComponent).filter(MealComponent.meal_id == meal_id).delete()
    db.delete(db_meal)
    db.commit()
    return None 