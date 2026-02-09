import requests
import time
import os
import uuid

BASE_URL = "http://localhost:8000"
TEST_EMAIL = f"test_{uuid.uuid4().hex[:8]}@example.com"
TEST_PASSWORD = "testpassword123"

def test_backend_happy_path():
    # 1. Signup
    print(f"Signing up with {TEST_EMAIL}...")
    signup_res = requests.post(
        f"{BASE_URL}/api/auth/signup",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
    )
    assert signup_res.status_code == 200, f"Signup failed: {signup_res.text}"
    token = signup_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Upload Image
    # Create a dummy image
    img_path = "test_image.png"
    from PIL import Image
    img = Image.new('RGB', (100, 100), color = 'red')
    img.save(img_path)

    print("Uploading image...")
    with open(img_path, "rb") as f:
        upload_res = requests.post(
            f"{BASE_URL}/api/jobs",
            headers=headers,
            files={"file": ("test_image.png", f, "image/png")}
        )
    
    assert upload_res.status_code == 200, f"Upload failed: {upload_res.text}"
    job_id = upload_res.json()["job_id"]
    print(f"Job created: {job_id}")

    # 3. Wait for success
    print("Waiting for job to succeed...")
    max_retries = 30
    status = "queued"
    for i in range(max_retries):
        status_res = requests.get(f"{BASE_URL}/api/jobs/{job_id}", headers=headers)
        assert status_res.status_code == 200
        status = status_res.json()["status"]
        print(f"Current status: {status}")
        if status == "succeeded":
            break
        elif status == "failed":
            pytest.fail("Job failed")
        time.sleep(2)
    
    assert status == "succeeded", "Job timed out"

    # 4. Verify Output Access
    print("Verifying overlay access...")
    overlay_res = requests.get(f"{BASE_URL}/api/jobs/{job_id}/overlay", headers=headers)
    assert overlay_res.status_code == 200
    assert overlay_res.headers["content-type"] == "image/png"

    print("Verifying CSV access...")
    csv_res = requests.get(f"{BASE_URL}/api/jobs/{job_id}/csv", headers=headers)
    assert csv_res.status_code == 200
    assert "text/csv" in csv_res.headers["content-type"]

    # Cleanup
    if os.path.exists(img_path):
        os.remove(img_path)
    
    print("Backend happy path test PASSED!")

if __name__ == "__main__":
    import pytest
    pytest.main([__file__])
