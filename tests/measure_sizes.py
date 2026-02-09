import requests
import uuid
import os
from PIL import Image

BASE_URL = "http://localhost:8000"
TEST_EMAIL = f"size_test_{uuid.uuid4().hex[:8]}@example.com"
TEST_PASSWORD = "password123"

def measure_sizes():
    # Signup
    signup_res = requests.post(f"{BASE_URL}/api/auth/signup", json={"email": TEST_EMAIL, "password": TEST_PASSWORD})
    if signup_res.status_code != 200:
        print(f"Signup failed: {signup_res.text}")
        return
    
    token = signup_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Use a real 1MB image if possible, or just generate one around that size
    # A 1024x1024 white image is very small in PNG (compression). 
    # To get ~1MB we need some entropy.
    img_path = "size_test.png"
    import numpy as np
    # Generate random noise to prevent heavy PNG compression
    noise = np.random.randint(0, 256, (800, 800, 3), dtype=np.uint8)
    img = Image.fromarray(noise)
    img.save(img_path)
    
    input_size = os.path.getsize(img_path)
    print(f"Uploading {img_path} ({input_size/1024/1024:.2f} MB)...")
    
    with open(img_path, "rb") as f:
        res = requests.post(f"{BASE_URL}/api/jobs", headers=headers, files={"file": ("test.png", f, "image/png")})
    
    if res.status_code != 200:
        print(f"Job creation failed: {res.text}")
        return
        
    job_id = res.json()["job_id"]
    
    # Wait for completion
    import time
    print("Waiting for job to succeed...")
    for _ in range(30):
        status_res = requests.get(f"{BASE_URL}/api/jobs/{job_id}", headers=headers).json()
        status = status_res["status"]
        if status == "succeeded": break
        if status == "failed":
            print(f"Job failed: {status_res}")
            return
        time.sleep(2)
    
    # Get overlay size
    overlay_res = requests.get(f"{BASE_URL}/api/jobs/{job_id}/overlay", headers=headers)
    overlay_size = len(overlay_res.content)
    
    # Get CSV size
    csv_res = requests.get(f"{BASE_URL}/api/jobs/{job_id}/csv", headers=headers)
    csv_size = len(csv_res.content)
    
    print("-" * 40)
    print(f"Observed Sizes for 1 Sample Job:")
    print(f"Input:   {input_size:>10} bytes ({input_size/1024/1024:.2f} MB)")
    print(f"Overlay: {overlay_size:>10} bytes ({overlay_size/1024/1024:.2f} MB)")
    print(f"CSV:     {csv_size:>10} bytes ({csv_size/1024:.2f} KB)")
    print("-" * 40)
    
    if os.path.exists(img_path):
        os.remove(img_path)

if __name__ == "__main__":
    measure_sizes()
