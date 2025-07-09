from fastapi import FastAPI
from fastapi.responses import JSONResponse
from utils.database import engine, Base
from routers import auth
from routers import meals
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="PlateAI API", version="1.0")

# Add CORS middleware for all origins (development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=JSONResponse)
def read_root() -> dict[str, str]:
    return {"message": "PlateAI server is running."} 

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(meals.router, prefix="/api/meals", tags=["meals"])

# Meals router

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)