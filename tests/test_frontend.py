import pytest
from playwright.sync_api import Page, expect
import os
import uuid
import time

FRONTEND_URL = "http://localhost:5173"
TEST_EMAIL = f"test_e2e_{uuid.uuid4().hex[:8]}@example.com"
TEST_PASSWORD = "testpassword123"

def test_frontend_e2e(page: Page):
    # 1. Signup
    print(f"Navigating to {FRONTEND_URL}/signup...")
    page.goto(f"{FRONTEND_URL}/signup")
    
    page.fill("#email", TEST_EMAIL)
    page.fill("#password", TEST_PASSWORD)
    page.fill("#confirmPassword", TEST_PASSWORD)
    
    print("Submitting signup...")
    page.click("button[type='submit']")
    
    # After signup, should be redirected to dashboard (/)
    expect(page).to_have_url(FRONTEND_URL + "/")
    print("Signup successful.")

    # 2. Upload Image
    # Create a dummy image for upload
    from PIL import Image
    img_path = os.path.abspath("test_e2e_image.png")
    img = Image.new('RGB', (100, 100), color = 'blue')
    img.save(img_path)

    print("Uploading image...")
    # The file input is hidden, but we can set the files on it
    page.set_input_files("input[type='file']", img_path)
    
    # Click upload button
    page.click("text=Start Machine Analysis")
    
    # 3. Wait for Succeeded
    print("Waiting for redirection to job detail...")
    # It should redirect to /jobs/<id>
    page.wait_for_url(lambda url: "/jobs/" in url)
    job_id = page.url.split("/")[-1]
    print(f"On job detail page for {job_id}")

    # Wait for the status badge to say SUCCEEDED
    print("Waiting for job success status...")
    status_locator = page.locator(".status-badge")
    expect(status_locator).to_have_text("SUCCEEDED", timeout=60000)
    print("Job status is SUCCEEDED.")

    # 4. Preview Visible
    print("Verifying preview is visible...")
    preview_img = page.locator("img[alt='Analyzed Overlay']")
    expect(preview_img).to_be_visible()
    
    # Verify CSV results table is visible
    results_table = page.locator("table")
    expect(results_table).to_be_visible()
    print("Preview and results table are visible.")

    # Cleanup
    if os.path.exists(img_path):
        os.remove(img_path)
    
    print("Frontend E2E test PASSED!")
