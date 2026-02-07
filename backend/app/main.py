from fastapi import FastAPI
from app import models
from app.database import engine
from app.health import router as health_router
from app.jobs import router as jobs_router
from app.auth_routes import router as auth_router
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

# Create database tables
# models.Base.metadata.drop_all(bind=engine) # Uncomment if you need to reset the DB
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
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(jobs_router, prefix="/api")


@app.on_event("startup")
def startup_event():
    print("Startup: Initializing mock user...")
    try:
        from app.database import SessionLocal
        from app.models import User
        from app.auth import MOCK_USER_ID
        import uuid
        
        db = SessionLocal()
        mock_user = db.query(User).filter(User.id == uuid.UUID(MOCK_USER_ID)).first()
        if not mock_user:
            print(f"Startup: Creating mock user {MOCK_USER_ID}")
            mock_user = User(
                id=uuid.UUID(MOCK_USER_ID),
                email="test@example.com",
                password_hash="mock_hash"
            )
            db.add(mock_user)
            db.commit()
        db.close()
        print("Startup: Mock user initialization complete.")
    except Exception as e:
        print(f"Startup Error (User): {e}")

    print("Startup: Initializing MinIO bucket...")
    try:
        from minio import Minio
        import os
        minio_client = Minio(
            os.getenv("MINIO_ENDPOINT"),
            access_key=os.getenv("MINIO_ACCESS_KEY"),
            secret_key=os.getenv("MINIO_SECRET_KEY"),
            secure=False
        )
        bucket = os.getenv("MINIO_BUCKET")
        if not minio_client.bucket_exists(bucket):
            print(f"Startup: Creating bucket {bucket}")
            minio_client.make_bucket(bucket)
        print("Startup: MinIO initialization complete.")
    except Exception as e:
        print(f"Startup Error (MinIO): {e}")



@app.get("/")
def read_root():
    return {"message": "PID Parser SaaS Backend"}
