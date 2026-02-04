
import os
import time
import requests
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from captcha_solver import CaptchaSolver

# Load env
load_dotenv()

def debug_starasn_captcha():
    solver = CaptchaSolver()
    
    with sync_playwright() as p:
        print("Launching browser...")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        print("Navigating to StarASN Login...")
        page.goto('https://star-asn.kemenimipas.go.id/authentication/login')
        page.wait_for_timeout(2000)
        
        # Handle modal
        try:
            close_btn = page.locator("button.btn-close, .modal-header button[aria-label='Close']")
            if close_btn.count() > 0:
                close_btn.first.click()
                print("Closed modal.")
        except:
            pass
            
        # Locate Captcha
        captcha_img = page.locator("img#kv-image")
        if captcha_img.count() == 0:
            print("Captcha image element not found!")
            browser.close()
            return

        captcha_src = captcha_img.get_attribute("src")
        print(f"Captcha Source: {captcha_src}")
        
        
        # Screenshot the element directly to ensure we have the exact image shown
        print("Capturing captcha element screenshot...")
        try:
            captcha_img.screenshot(path="debug_captcha_original.png")
            print("Saved debug_captcha_original.png via screenshot")
            img = Image.open("debug_captcha_original.png")
            
            # Solve
            text = solver.solve_image(img, debug_save_path="debug_captcha_processed")
            print(f"Solved Text: '{text}'")
            
            # Try to Login
            print("Attempting login with this captcha...")
            
            page.fill("input#username", os.getenv('STARASN_USERNAME', ''))
            page.fill("input#password-input", os.getenv('STARASN_PASSWORD', ''))
            
            if text:
                page.fill("input#kv-captcha", text)
            else:
                print("No text solved, filling with DUMMY")
                page.fill("input#kv-captcha", "DUMMY")
                
            page.click("button.btn-primary.d-grid.w-100")
            page.wait_for_timeout(5000)
            
            if 'login' not in page.url.lower():
                print("LOGIN SUCCESS!")
                # Optional: Screenshot success
                page.screenshot(path="debug_login_success.png")
                return True
            else:
                print("LOGIN FAILED. Check debug_login_result.png")
                page.screenshot(path="debug_login_result.png")
                # Try to catch error message
                error_msg = page.locator(".alert, .text-danger, .invalid-feedback").all_text_contents()
                print(f"Error messages found: {error_msg}")
                return False
                
        except Exception as e:
            print(f"Error processing captcha: {e}")
            return False
            
        finally:
            browser.close()

if __name__ == "__main__":
    for i in range(10):
        print(f"\n--- Attempt {i+1} ---")
        success = debug_starasn_captcha()
        if success:
            print(f"Stopping after {i+1} attempts.")
            break
        time.sleep(2)
