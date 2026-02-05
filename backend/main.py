from fastapi import FastAPI
from app import models
from app.database import engine
from app.health import router as health_router
from app.jobs import router as jobs_router
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(jobs_router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "PID Parser SaaS Backend"}
