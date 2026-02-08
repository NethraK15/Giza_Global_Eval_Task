from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Response
from fastapi.responses import StreamingResponse
import io
import uuid, os, json
from redis import Redis
from app.auth import get_current_user
from app.models import Job
from app.database import SessionLocal
from minio import Minio

from app.logger import setup_logger

router = APIRouter()
logger = setup_logger("backend-jobs", "backend")
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
        logger.warning(f"Invalid file type attempted: {file.content_type}", extra={"user_id": str(user.id)})
        raise HTTPException(400, "Only PNG/JPG allowed")

    job_id = str(uuid.uuid4())
    db = SessionLocal()

    model_name = os.getenv("MODEL_NAME")
    model_version = os.getenv("MODEL_VERSION")

    job = Job(
        id=job_id,
        user_id=user.id,
        status="queued",
        model_name=model_name,
        model_version=model_version
    )
    db.add(job)
    db.commit()

    bucket = os.getenv("MINIO_BUCKET")
    path = f"{user.id}/{job_id}/input.png"

    try:
        minio_client.put_object(
            bucket,
            path,
            file.file,
            length=-1,
            part_size=10*1024*1024,
            content_type=file.content_type
        )
    except Exception as e:
        logger.error(f"Failed to upload to MinIO: {e}", extra={"job_id": job_id, "user_id": str(user.id)})
        raise HTTPException(500, "Storage error")

    payload = {
        "job_id": job_id,
        "user_id": str(user.id),
        "bucket": bucket,
        "path": path
    }
    redis.lpush("job_queue", json.dumps(payload))
    
    logger.info(
        f"Job {job_id} queued for user {user.id}", 
        extra={
            "job_id": job_id, 
            "user_id": str(user.id), 
            "status": "queued",
            "model_version": model_version
        }
    )

    return {"job_id": job_id, "status": "queued"}

@router.get("/jobs")
def get_jobs(user=Depends(get_current_user)):
    db = SessionLocal()
    jobs = db.query(Job).filter(Job.user_id == user.id).order_by(Job.created_at.desc()).all()
    return jobs

@router.get("/jobs/{job_id}")
def get_job(job_id: str, user=Depends(get_current_user)):
    db = SessionLocal()
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == user.id).first()
    if not job:
        raise HTTPException(404, "Job not found")
    return job

@router.get("/jobs/{job_id}/overlay")
def get_job_overlay(job_id: str, user=Depends(get_current_user)):
    db = SessionLocal()
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == user.id).first()
    if not job:
        raise HTTPException(404, "Job not found")
    
    if job.status != "succeeded":
        raise HTTPException(400, "Job not completed yet")

    bucket = os.getenv("MINIO_BUCKET")
    path = f"{user.id}/{job_id}/overlay.png"

    try:
        response = minio_client.get_object(bucket, path)
        try:
            return StreamingResponse(io.BytesIO(response.read()), media_type="image/png")
        finally:
            response.close()
            response.release_conn()
    except Exception as e:
        print(f"Error fetching overlay: {e}")
        raise HTTPException(404, "Overlay not found")

@router.get("/jobs/{job_id}/csv")
def get_job_csv(job_id: str, user=Depends(get_current_user)):
    db = SessionLocal()
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == user.id).first()
    if not job:
        raise HTTPException(404, "Job not found")
    
    if job.status != "succeeded":
        raise HTTPException(400, "Job not completed yet")

    bucket = os.getenv("MINIO_BUCKET")
    path = f"{user.id}/{job_id}/results.csv"

    try:
        response = minio_client.get_object(bucket, path)
        # return content for download/parsing
        try:
            return StreamingResponse(
                io.BytesIO(response.read()), 
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename=results-{job_id}.csv"}
            )
        finally:
            response.close()
            response.release_conn()
    except Exception as e:
        print(f"Error fetching CSV: {e}")
        raise HTTPException(404, "CSV results not found")
