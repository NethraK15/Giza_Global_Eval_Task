import time
import json
import os
import redis
from minio import Minio
from sqlalchemy import create_engine, MetaData, Table, Column, String, update
from sqlalchemy.dialects.postgresql import UUID
import io
import csv
from PIL import Image, ImageDraw
from yolo import YoloModel
from logger import setup_logger

logger = setup_logger("worker-main", "worker")

# Configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@db:5432/appdb")
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "models")
MODEL_NAME = os.getenv("MODEL_NAME", "yolov8n.pt")
MODEL_VERSION = os.getenv("MODEL_VERSION", "v1")

# Setup connections
try:
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
except Exception as e:
    logger.error(f"Initialization error: {e}")
    raise e

# Determine model name from environment
# Normalize common shorthand
if MODEL_NAME == "yolov8":
    MODEL_NAME = "yolov8n.pt"

logger.info(f"Initializing YoloModel with {MODEL_NAME}...")
try:
    model = YoloModel(MODEL_NAME)
except Exception as e:
    logger.error(f"Failed to load model {MODEL_NAME}: {e}")
    raise e

logger.info("Worker started. Listening for jobs...")

while True:
    # Blocking pop from Redis
    try:
        raw_data = r.brpop("job_queue", timeout=5)
    except Exception as e:
        logger.error(f"Redis error: {e}")
        time.sleep(5)
        continue
    
    if raw_data:
        queue_name, payload_bytes = raw_data
        try:
            payload = json.loads(payload_bytes.decode('utf-8'))
            job_id = payload["job_id"]
            bucket = payload["bucket"]
            path = payload["path"]
            user_id = payload["user_id"]
            
            logger.info(f"Processing job: {job_id}", extra={"job_id": job_id, "user_id": user_id, "status": "processing"})
    
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
                
                # --- Perform "Analysis" ---
                detect_start = time.time()
                detections = model.predict(local_path)
                latency_ms = (time.time() - detect_start) * 1000
                
                logger.info(
                    f"Inference complete. Found {len(detections)} objects.", 
                    extra={
                        "job_id": job_id, 
                        "user_id": user_id, 
                        "latency_ms": latency_ms, 
                        "object_count": len(detections),
                        "model_version": MODEL_VERSION
                    }
                )
    
                # 1. Generate Overlay Image & CSV
                detected_classes = set()
                
                try:
                    with Image.open(local_path) as img:
                        # Handle transparency/mode
                        if img.mode != 'RGB':
                            img = img.convert('RGB')
                            
                        draw = ImageDraw.Draw(img)
                        
                        csv_buffer = io.StringIO()
                        csv_writer = csv.writer(csv_buffer)
                        csv_writer.writerow(["Label", "Confidence", "X1", "Y1", "X2", "Y2"])
    
                        for item in detections:
                            label = item["label"]
                            conf = item["confidence"]
                            box = item["box"] # [x1, y1, x2, y2]
                            
                            detected_classes.add(label)
                            
                            # Draw box
                            draw.rectangle(box, outline="#00ff00", width=3)
                            # Draw text background for readability
                            text_content = f"{label} {conf:.2f}"
                            # Simple estimation of text size or just draw plainly
                            draw.text((box[0], box[1] - 10 if box[1] > 20 else box[1] + 5), text_content, fill="#00ff00")
                            
                            # Add to CSV
                            csv_writer.writerow([label, f"{conf:.2f}", int(box[0]), int(box[1]), int(box[2]), int(box[3])])
                        
                        # Save overlay to buffer
                        overlay_buffer = io.BytesIO()
                        img.save(overlay_buffer, format="PNG")
                        overlay_buffer.seek(0)
                        
                        # Upload overlay
                        overlay_path = f"{user_id}/{job_id}/overlay.png"
                        minio_client.put_object(
                            bucket,
                            overlay_path,
                            overlay_buffer,
                            length=overlay_buffer.getbuffer().nbytes,
                            content_type="image/png"
                        )
                        
                        # Upload CSV
                        csv_content = csv_buffer.getvalue().encode('utf-8')
                        csv_path = f"{user_id}/{job_id}/results.csv"
                        minio_client.put_object(
                            bucket,
                            csv_path,
                            io.BytesIO(csv_content),
                            length=len(csv_content),
                            content_type="text/csv"
                        )
    
                except Exception as e:
                    logger.error(f"Error generating results: {e}", extra={"job_id": job_id})
                    raise e
    
                # --- Update status to SUCCEEDED ---
                result_json = {"detected": list(detected_classes), "count": len(detections)}
    
                with engine.connect() as conn:
                    conn.execute(
                        update(jobs).where(jobs.c.id == job_id).values(
                            status="succeeded",
                            result=json.dumps(result_json)
                        )
                    )
                    conn.commit()
                
                # Cleanup
                if os.path.exists(local_path):
                    os.remove(local_path)
                    
                logger.info(f"Job {job_id} succeeded.", extra={"job_id": job_id, "status": "succeeded"})
    
            except Exception as e:
                logger.error(f"Error processing job {job_id}: {e}", extra={"job_id": job_id, "status": "failed"})
                with engine.connect() as conn:
                    conn.execute(
                        update(jobs).where(jobs.c.id == job_id).values(status="failed")
                    )
                    conn.commit()
        except Exception as e:
             logger.error(f"Error parsing job payload: {e}")
