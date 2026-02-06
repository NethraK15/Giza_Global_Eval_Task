from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
import uuid, os, json
from redis import Redis
from app.auth import get_current_user
from app.models import Job
from app.database import SessionLocal
from minio import Minio

router = APIRouter()
redis = Redis.from_url(os.getenv("REDIS_URL"))

minio_client = Minio(
    os.getenv("MINIO_ENDPOINT"),
    access_key=os.getenv("MINIO_ACCESS_KEY"),
    secret_key=os.getenv("MINIO_SECRET_KEY"),
    secure=False
)

@router.post("/jobs")
def create_job(
    file: UploadFile = File(...),
    user=Depends(get_current_user)
):
    if file.content_type not in ["image/png", "image/jpeg"]:
        raise HTTPException(400, "Only PNG/JPG allowed")

    job_id = str(uuid.uuid4())
    db = SessionLocal()

    job = Job(
        id=job_id,
        user_id=user.id,
        status="queued",
        model_name=os.getenv("MODEL_NAME"),
        model_version=os.getenv("MODEL_VERSION")
    )
    db.add(job)
    db.commit()

    bucket = os.getenv("MINIO_BUCKET")
    path = f"{user.id}/{job_id}/input.png"

    minio_client.put_object(
        bucket,
        path,
        file.file,
        length=-1,
        part_size=10*1024*1024,
        content_type=file.content_type
    )

    payload = {
        "job_id": job_id,
        "user_id": str(user.id),
        "bucket": bucket,
        "path": path
    }
    redis.lpush("job_queue", json.dumps(payload))

    return {"job_id": job_id, "status": "queued"}

@router.get("/jobs")
def get_jobs(user=Depends(get_current_user)):
    db = SessionLocal()
    jobs = db.query(Job).filter(Job.user_id == user.id).order_by(Job.created_at.desc()).all()
    return jobs
