from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from schemas.user import UserCreate, UserAuth, UserAuthResponse, UserRead
from models.user import User
from utils.database import get_db
from utils.security import verify_password, get_password_hash, create_access_token
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError

router = APIRouter()

@router.post("/signup", response_model=UserAuthResponse, status_code=201)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    hashed_password = get_password_hash(user.password)
    db_user = User(name=user.name, username=user.username, password_hash=hashed_password)
    db.add(db_user)
    try:
        db.commit()
        db.refresh(db_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Username already taken")
    token = create_access_token({"sub": str(db_user.user_id)})
    return UserAuthResponse(userId=UUID(str(db_user.user_id)), token=token)

@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == form_data.username).first()
    if not db_user or not verify_password(form_data.password, str(db_user.password_hash)):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    access_token = create_access_token({"sub": str(db_user.user_id)})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/signin", response_model=UserAuthResponse)
async def signin(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        raise HTTPException(status_code=422, detail="Username and password required")

    db_user = db.query(User).filter(User.username == username).first()
    password_str = str(password) if password is not None else ""
    if not db_user or not verify_password(password_str, str(db_user.password_hash)):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = create_access_token({"sub": str(db_user.user_id)})
    return UserAuthResponse(userId=UUID(str(db_user.user_id)), token=token) 