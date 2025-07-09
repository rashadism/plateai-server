from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime

class UserBase(BaseModel):
    name: str = Field(examples=["John Doe"])
    username: str = Field(examples=["johndoe"])

class UserCreate(UserBase):
    password: str = Field(examples=["strongpassword123"])

class UserRead(UserBase):
    user_id: UUID
    created_at: datetime

class UserAuth(BaseModel):
    username: str = Field(examples=["johndoe"])
    password: str = Field(examples=["strongpassword123"])

class UserAuthResponse(BaseModel):
    userId: UUID = Field(examples=["123e4567-e89b-12d3-a456-426614174000"])
    token: str = Field(examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."]) 