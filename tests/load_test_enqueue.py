import requests
import uuid
import time
import os
from concurrent.futures import ThreadPoolExecutor
from PIL import Image

BASE_URL = "http://localhost:8000"
TEST_EMAIL = f"loadtest_{uuid.uuid4().hex[:8]}@example.com"
TEST_PASSWORD = "password123"
NUM_JOBS = 100
CONCURRENCY = 10 # Number of simultaneous uploads

def get_token():
    print(f"Creating test user: {TEST_EMAIL}")
    res = requests.post(f"{BASE_URL}/api/auth/signup", json={"email": TEST_EMAIL, "password": TEST_PASSWORD})
    res.raise_for_status()
    return res.json()["access_token"]

def upload_job(token, img_path):
    headers = {"Authorization": f"Bearer {token}"}
    with open(img_path, "rb") as f:
        res = requests.post(f"{BASE_URL}/api/jobs", headers=headers, files={"file": ("test.png", f, "image/png")})
        return res.json()

def main():
    token = get_token()
    
    # Create a dummy image
    img_path = "load_test_img.png"
    img = Image.new('RGB', (640, 640), color='gray') # Standard YOLO size
    img.save(img_path)

    print(f"Enqueuing {NUM_JOBS} jobs...")
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=CONCURRENCY) as executor:
        futures = [executor.submit(upload_job, token, img_path) for _ in range(NUM_JOBS)]
        results = [f.result() for f in futures]
    
    end_time = time.time()
    print(f"Finished enqueuing {NUM_JOBS} jobs in {end_time - start_time:.2f}s")
    
    if os.path.exists(img_path):
        os.remove(img_path)

if __name__ == "__main__":
    main()
