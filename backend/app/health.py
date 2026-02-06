from fastapi import APIRouter
import psycopg2
import redis
import os

router = APIRouter()

@router.get("/health")
def health():
    return {"status": "ok"}

@router.get("/ready")
def ready():
    psycopg2.connect(os.getenv("DATABASE_URL")).close()
    redis.Redis.from_url(os.getenv("REDIS_URL")).ping()
    return {"status": "ready"}
