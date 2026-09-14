from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .api import trips

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Application Entrainement API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(trips.router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to Application Entrainement API"}
