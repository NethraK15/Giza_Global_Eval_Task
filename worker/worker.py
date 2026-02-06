import time
import json
import os
import redis
from minio import Minio
from sqlalchemy import create_engine, MetaData, Table, Column, String, update
from sqlalchemy.dialects.postgresql import UUID
from yolo import YoloModel

# Configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@db:5432/appdb")
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "models")

# Setup connections
r = redis.Redis.from_url(REDIS_URL)

minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False
)

engine = create_engine(DATABASE_URL)
metadata = MetaData()

# Reflect or define jobs table
jobs = Table(
    'jobs', metadata,
    Column('id', UUID(as_uuid=True), primary_key=True),
    Column('status', String),
    Column('result', String)
)

model = YoloModel()

print("Worker started. Listening for jobs...")

while True:
    # Blocking pop from Redis
    raw_data = r.brpop("job_queue", timeout=5)
    
    if raw_data:
        queue_name, payload_bytes = raw_data
        payload = json.loads(payload_bytes.decode('utf-8'))
        job_id = payload["job_id"]
        bucket = payload["bucket"]
        path = payload["path"]
        
        print(f"Processing job: {job_id}")

        try:
            # Update status to processing
            with engine.connect() as conn:
                conn.execute(
                    update(jobs).where(jobs.c.id == job_id).values(status="processing")
                )
                conn.commit()

            # Download image from Minio
            local_path = f"/tmp/{job_id}.png"
            minio_client.fget_object(bucket, path, local_path)
            
            # Run inference
            result = model.predict(local_path)
            
            # Update status to completed and store result
            with engine.connect() as conn:
                conn.execute(
                    update(jobs).where(jobs.c.id == job_id).values(
                        status="completed",
                        result=json.dumps(result)
                    )
                )
                conn.commit()
            
            # Cleanup
            if os.path.exists(local_path):
                os.remove(local_path)
                
            print(f"Job {job_id} completed.")

        except Exception as e:
            print(f"Error processing job {job_id}: {e}")
            with engine.connect() as conn:
                conn.execute(
                    update(jobs).where(jobs.c.id == job_id).values(status="failed")
                )
                conn.commit()
