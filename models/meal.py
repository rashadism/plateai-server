from sqlalchemy import Column, String, TIMESTAMP, Text, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
import sqlalchemy
from utils.database import Base

class Meal(Base):
    __tablename__ = "meals"

    meal_id = Column(UUID(as_uuid=True), primary_key=True, default=sqlalchemy.text('gen_random_uuid()'))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    meal_date = Column(TIMESTAMP(timezone=True), nullable=False)
    description = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=sqlalchemy.text('NOW()'))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=sqlalchemy.text('NOW()'))

class MealComponent(Base):
    __tablename__ = "meal_components"

    component_id = Column(UUID(as_uuid=True), primary_key=True, default=sqlalchemy.text('gen_random_uuid()'))
    meal_id = Column(UUID(as_uuid=True), ForeignKey("meals.meal_id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    calories = Column(Numeric(10, 2), nullable=False)
    fat_g = Column(Numeric(10, 2), nullable=False)
    protein_g = Column(Numeric(10, 2), nullable=False)
    carbs_g = Column(Numeric(10, 2), nullable=False) 