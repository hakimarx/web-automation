"""
Aplikasi Otomatisasi Web Absensi
Untuk pusaka-v3.kemenag.go.id dan star-asn.kemenimipas.go.id
Dengan dukungan CAPTCHA solver OCR
"""

import os
import json
import time
import random
import smtplib
import argparse
import logging
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

from captcha_solver import CaptchaSolver, manual_captcha_input

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('web_automation.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class WebAutomation:
    def __init__(self, headless=True):
        """Initialize automation"""
        self.headless = headless
        self.captcha_solver = CaptchaSolver()
        
        # Load credentials from environment
        self.credentials = {
            'pusaka': {
                'username': os.getenv('PUSAKA_USERNAME'),
                'password': os.getenv('PUSAKA_PASSWORD'),
                'url': 'https://pusaka-v3.kemenag.go.id',
                'login_url': 'https://pusaka-v3.kemenag.go.id/login'
            },
            'starasn': {
                'username': os.getenv('STARASN_USERNAME'),
                'password': os.getenv('STARASN_PASSWORD'),
                'url': 'https://star-asn.kemenimipas.go.id',
                'login_url': 'https://star-asn.kemenimipas.go.id/authentication/login'
            }
        }
        
        # Email config
        self.email_config = {
            'from_email': os.getenv('EMAIL_FROM'),
            'to_email': os.getenv('EMAIL_TO', 'hakimarx@gmail.com'),
            'app_password': os.getenv('EMAIL_APP_PASSWORD')
        }
    
    def is_working_day(self):
        """Cek apakah hari ini adalah hari kerja (Senin-Jumat)"""
        return datetime.now().weekday() < 5
    
    def send_email_notification(self, success=True, message=""):
        """Kirim notifikasi via Gmail"""
        if not self.email_config.get('from_email') or not self.email_config.get('app_password'):
            logger.warning("Email tidak dikonfigurasi, skip notifikasi")
            return
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_config['from_email']
            msg['To'] = self.email_config['to_email']
            
            if success:
                msg['Subject'] = '✅ Absensi Otomatis Berhasil'
                body = f"""
Absensi otomatis telah berhasil diselesaikan!

Waktu: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{message}

---
Web Automation System
                """
            else:
                msg['Subject'] = '❌ Absensi Otomatis Gagal'
                body = f"""
Absensi otomatis mengalami error!

Waktu: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Error: {message}

---
Web Automation System
                """
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.email_config['from_email'], self.email_config['app_password'])
            server.send_message(msg)
            server.quit()
            
            logger.info("Email notifikasi berhasil dikirim")
            
        except Exception as e:
            logger.error(f"Gagal mengirim email: {str(e)}")
    
    def login_pusaka(self, page):
        """Login ke pusaka-v3.kemenag.go.id"""
        creds = self.credentials['pusaka']
        
        logger.info(f"Membuka Pusaka: {creds['login_url']}")
        page.goto(creds['login_url'], timeout=30000, wait_until='domcontentloaded')
        page.wait_for_timeout(2000)
        
        # Fill login form
        logger.info("Mengisi form login Pusaka...")
        page.fill("input[placeholder='Username']", creds['username'])
        page.fill("input[placeholder='Password']", creds['password'])
        
        # Click login button
        page.click("button.btn.bg-indigo-400")
        page.wait_for_timeout(3000)
        
        # Check if login successful (check for dashboard or error)
        current_url = page.url
        if 'login' not in current_url.lower():
            logger.info("✅ Login Pusaka berhasil!")
            print("[OK] Login Pusaka berhasil!")
            return True
        else:
            logger.error("❌ Login Pusaka gagal - masih di halaman login")
            print("[FAIL] Login Pusaka gagal - masih di halaman login")
            page.screenshot(path="login_pusaka_failed.png")
            with open("login_pusaka_failed.html", "w", encoding="utf-8") as f:
                f.write(page.content())
            return False
    
    def login_starasn(self, page):
        """Login ke star-asn.kemenimipas.go.id dengan CAPTCHA solving"""
        creds = self.credentials['starasn']
        max_captcha_attempts = 7
        
        for attempt in range(max_captcha_attempts):
            logger.info(f"Membuka Star-ASN: {creds['login_url']} (Attempt {attempt + 1})")
            page.goto(creds['login_url'], timeout=30000, wait_until='domcontentloaded')
            page.wait_for_timeout(2000)
            
            # Close any modal that appears
            try:
                close_btn = page.locator("button.btn-close, .modal-header button[aria-label='Close']")
                if close_btn.count() > 0:
                    close_btn.first.click()
                    page.wait_for_timeout(500)
            except:
                pass
            
            # Fill login form
            logger.info("Mengisi form login Star-ASN...")
            page.fill("input#username", creds['username'])
            page.fill("input#password-input", creds['password'])
            
            # Get CAPTCHA image and solve
            captcha_img = page.locator("img#kv-image")
            if captcha_img.count() > 0:
                logger.info("Mendeteksi CAPTCHA, mencoba solve dengan OCR...")
                
                # Get CAPTCHA image source
                captcha_url = captcha_img.get_attribute("src")
                if not captcha_url.startswith("http"):
                    captcha_url = f"https://star-asn.kemenimipas.go.id{captcha_url}"
                
                # Get cookies from browser for authenticated request
                cookies = page.context.cookies()
                cookie_dict = {c['name']: c['value'] for c in cookies}
                
                # Try OCR
                captcha_text = self.captcha_solver.solve_from_url(captcha_url, cookies=cookie_dict)
                
                if captcha_text and len(captcha_text) >= 4:
                    logger.info(f"CAPTCHA OCR result: {captcha_text}")
                    page.fill("input#kv-captcha", captcha_text)
                else:
                    # Fallback: manual input if not headless
                    if not self.headless:
                        logger.warning("OCR gagal, menunggu input manual...")
                        # Wait for user to manually enter CAPTCHA
                        page.wait_for_timeout(10000)  # 10 seconds to enter manually
                    else:
                        # Refresh CAPTCHA and try again
                        refresh_btn = page.locator("button.btn-sm.btn-primary")
                        if refresh_btn.count() > 0:
                            refresh_btn.click()
                            page.wait_for_timeout(1000)
                            continue
            
            # Click login button
            page.click("button.btn-primary.d-grid.w-100")
            page.wait_for_timeout(3000)
            
            # Check if login successful
            current_url = page.url
            if 'login' not in current_url.lower() and 'authentication' not in current_url.lower():
                logger.info("✅ Login Star-ASN berhasil!")
                print("[OK] Login Star-ASN berhasil!")
                return True
            else:
                logger.warning(f"❌ Login Star-ASN gagal (attempt {attempt + 1}), mencoba lagi...")
                print(f"[FAIL] Login Star-ASN gagal (attempt {attempt + 1}), mencoba lagi...")
                page.screenshot(path=f"login_starasn_failed_attempt_{attempt+1}.png")
                with open(f"login_starasn_failed_attempt_{attempt+1}.html", "w", encoding="utf-8") as f:
                    f.write(page.content())
        
        logger.error("❌ Login Star-ASN gagal setelah semua percobaan")
        print("[FAIL] Login Star-ASN gagal setelah semua percobaan")
        return False
    
    def do_presence_pusaka(self, page):
        """Melakukan presensi di Pusaka"""
        try:
            logger.info("Membuka halaman presensi...")
            page.goto("https://pusaka-v3.kemenag.go.id/profile/presence", timeout=30000)
            page.wait_for_timeout(3000)
            
            # Cek jam
            current_hour = datetime.now().hour
            
            # 1. Cek tombol Presensi MASUK
            btn_masuk = page.locator("button:has-text('Presensi Masuk'), button:has-text('Absen Masuk')")
            if btn_masuk.count() > 0:
                logger.info("Tombol Presensi Masuk ditemukan. Melakukan klik...")
                btn_masuk.first.click()
                page.wait_for_timeout(3000)
                page.screenshot(path="presensi_pusaka_result.png")
                logger.info("✅ Klik Presensi Masuk berhasil dilakukan")
                return True, "Presensi Masuk berhasil diklik"

            # 2. Cek tombol Presensi PULANG
            btn_pulang = page.locator("button:has-text('Presensi Pulang'), button:has-text('Absen Pulang'), button:has-text('Simpan')")
            if btn_pulang.count() > 0:
                if current_hour >= 16:
                    logger.info("Tombol Presensi Pulang ditemukan dan sudah waktunya. Melakukan klik...")
                    btn_pulang.first.click()
                    page.wait_for_timeout(3000)
                    page.screenshot(path="presensi_pusaka_result.png")
                    logger.info("✅ Klik Presensi Pulang berhasil dilakukan")
                    return True, "Presensi Pulang berhasil diklik"
                else:
                    return True, "Menunggu jam pulang (Tombol Pulang sudah ada)"
            
            # 3. Cek Status Sudah Absen
            if page.locator("text=Sudah Presensi").count() > 0 or page.locator("text=Anda sudah melakukan presensi").count() > 0:
                logger.info("Info: Sudah melakukan presensi hari ini")
                return True, "Sudah melakukan presensi sebelumnya"
                
            logger.warning("❌ Tidak ditemukan tombol presensi apapun")
            page.screenshot(path="presensi_pusaka_failed.png")
            return False, "Tombol Presensi tidak ditemukan"
                
        except Exception as e:
            logger.error(f"Error saat presensi: {str(e)}")
            return False, str(e)
    def do_presence_starasn(self, page):
        """Melakukan presensi di Star-ASN dashboard"""
        try:
            logger.info("Mengecek status presensi Star-ASN...")
            page.wait_for_timeout(3000)
            
            # Cek jam saat ini
            current_hour = datetime.now().hour
            
            # Prioritas: UI Based
            # 1. Cek Card MASUK dulu
            masuk_card = page.locator("div.card:has-text('PRESENSI MASUK')")
            if masuk_card.count() > 0:
                # Cek apakah ada tombol/link di dalamnya yang aktif
                action_btn = masuk_card.locator("a.btn, button.btn").first
                status_text = masuk_card.text_content()
                
                # Jika ada tombol dan status "Belum Presensi" -> KLIK (Kapanpun!)
                if action_btn.count() > 0 and "Belum Presensi" in status_text:
                    logger.info("Ditemukan tombol PRESENSI MASUK. Melakukan klik...")
                    action_btn.click()
                    page.wait_for_timeout(5000)
                    page.screenshot(path="starasn_result_masuk.png")
                    return True, "Presensi Masuk berhasil diklik"

            # 2. Cek Card PULANG
            pulang_card = page.locator("div.card:has-text('PRESENSI PULANG')")
            if pulang_card.count() > 0:
                action_btn = pulang_card.locator("a.btn, button.btn").first
                status_text = pulang_card.text_content()
                
                # Klik pulang HANYA jika jam > 16 (atau jam 23 sesuai request khusus, tapi default aman > 16)
                if action_btn.count() > 0 and "Belum Presensi" in status_text:
                    if current_hour >= 16:
                        logger.info("Ditemukan tombol PRESENSI PULANG dan sudah waktunya. Melakukan klik...")
                        action_btn.click()
                        page.wait_for_timeout(5000)
                        page.screenshot(path="starasn_result_pulang.png")
                        return True, "Presensi Pulang berhasil diklik"
                    else:
                        logger.info("Tombol Pulang ada, tapi belum waktunya (Wait until > 16:00)")
                        return True, "Menunggu jam pulang"
            
            logger.info("Tidak ada aksi presensi yang diperlukan saat ini.")
            return True, "Status OK / Sudah Presensi"

        except Exception as e:
            logger.error(f"Error presensi Star-ASN: {e}")
            return False, str(e)

    def run_automation(self, site='all'):
        """Jalankan otomatisasi dengan dynamic geolocation"""
        results = []
        
        # Koordinat (Updated sesuai alamat spesifik)
        COORD_PUSAKA = {'latitude': -7.3789, 'longitude': 112.7698}  # Jl Raya Juanda 26, Sidoarjo
        COORD_STARASN = {'latitude': -0.4937, 'longitude': 117.1505}  # Bapas Samarinda
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=self.headless)
                
                # 1. Handle Pusaka (Sidoarjo)
                if site in ['all', 'pusaka']:
                    logger.info("--- Proses Pusaka (Lokasi: Sidoarjo) ---")
                    context_pusaka = browser.new_context(
                        viewport={'width': 1280, 'height': 720},
                        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                        geolocation=COORD_PUSAKA,
                        permissions=['geolocation']
                    )
                    page_pusaka = context_pusaka.new_page()
                    try:
                        if self.login_pusaka(page_pusaka):
                            success, msg = self.do_presence_pusaka(page_pusaka)
                            # Logic khusus Pusaka: Jika msg="Presensi Masuk berhasil...", info user
                            results.append(('Pusaka', success, msg))
                        else:
                            results.append(('Pusaka', False, "Login Gagal"))
                    except Exception as e:
                        logger.error(f"Error Pusaka: {e}")
                        results.append(('Pusaka', False, str(e)))
                    context_pusaka.close()
                
                # 2. Handle Star-ASN (Samarinda)
                if site in ['all', 'starasn']:
                    logger.info("--- Proses Star-ASN (Lokasi: Samarinda) ---")
                    context_star = browser.new_context(
                        viewport={'width': 1280, 'height': 720},
                        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                        geolocation=COORD_STARASN,
                        permissions=['geolocation']
                    )
                    page_star = context_star.new_page()
                    try:
                        if self.login_starasn(page_star):
                            success, msg = self.do_presence_starasn(page_star)
                            results.append(('Star-ASN', success, msg))
                        else:
                            results.append(('Star-ASN', False, "Login Gagal"))
                    except Exception as e:
                        logger.error(f"Error Star-ASN: {e}")
                        print(f"Error Star-ASN: {e}")
                        import traceback
                        traceback.print_exc()
                        results.append(('Star-ASN', False, str(e)))
                    context_star.close()
                
                browser.close()
            
            # Send notification HANYA jika ada aksi penting (Berhasil Klik atau Gagal Error)
            # Skip notifikasi jika statusnya hanya "Sudah Presensi" atau "Menunggu jam pulang"
            should_notify = any("berhasil diklik" in str(r[2]) for r in results) or any(not r[1] for r in results)
            
            if should_notify:
                all_success = all(r[1] for r in results)
                message = "\n".join(f"- {name}: {msg}" for name, success, msg in results)
                self.send_email_notification(success=all_success, message=message)
            else:
                logger.info("Tidak ada aktivitas presensi baru, skip email.")
            
            return [(r[0], r[1]) for r in results] 
            
        except Exception as e:
            logger.error(f"Error automation: {str(e)}")
            self.send_email_notification(success=False, message=str(e))
            return []


def generate_random_times():
    """Generate waktu random untuk absen hari ini"""
    # Pagi: 06:00-07:30 (360-450 menit dari midnight)
    morning_minutes = random.randint(360, 450)
    morning_hour = morning_minutes // 60
    morning_min = morning_minutes % 60
    
    # Sore: 16:30-19:00 (990-1140 menit dari midnight)
    afternoon_minutes = random.randint(990, 1140)
    afternoon_hour = afternoon_minutes // 60
    afternoon_min = afternoon_minutes % 60
    
    return {
        'morning': {'hour': morning_hour, 'minute': morning_min},
        'afternoon': {'hour': afternoon_hour, 'minute': afternoon_min}
    }


def select_platform():
    """Memilih platform absensi di awal aplikasi"""
    print("\n" + "="*50)
    print("       PILIH PLATFORM ABSENSI")
    print("="*50)
    print("1. Pusaka (Jl Raya Juanda 26, Sidoarjo)")
    print("2. Star ASN (Bapas Samarinda)")
    print("3. Keduanya")
    print("="*50)
    
    while True:
        choice = input("\nPilihan Anda (1/2/3): ").strip()
        if choice == '1':
            return 'pusaka'
        elif choice == '2':
            return 'starasn'
        elif choice == '3':
            return 'all'
        else:
            print("Pilihan tidak valid. Masukkan 1, 2, atau 3.")


def main():
    parser = argparse.ArgumentParser(description='Web Automation')
    parser.add_argument('--test', action='store_true', help='Test run (Visual)')
    parser.add_argument('--site', choices=['all', 'pusaka', 'starasn'], default=None)
    parser.add_argument('--headless', action='store_true')
    args = parser.parse_args()
    
    # Logic Headless:
    # Jika --test: Visual (headless=False)
    # Jika tidak: Visual (headless=False) -> User request simulasi visual
    headless = False 
    if args.headless: headless = True
    
    automation = WebAutomation(headless=headless)
    
    # Jika site tidak di-specify via argumen, tanya user
    if args.site:
        site = args.site
    else:
        site = select_platform()
    
    logger.info(f"Platform dipilih: {site.upper()}")
    
    if args.test:
        logger.info("=== MODE TEST ===")
        results = automation.run_automation(site=site)
        print("\n=== HASIL TEST ===")
        for name, success in results:
            status = "[OK]" if success else "[FAIL]"
            print(f"{name}: {status}")
    else:
        # Random Time Scheduler Mode
        logger.info("="*50)
        logger.info("Memulai Random Time Scheduler...")
        
        last_date = None
        random_times = None
        morning_done = False
        afternoon_done = False
        
        while True:
            try:
                now = datetime.now()
                today = now.date()
                
                # Generate waktu baru di awal hari baru
                if last_date != today:
                    random_times = generate_random_times()
                    last_date = today
                    morning_done = False
                    afternoon_done = False
                    
                    logger.info(f"\n{'='*50}")
                    logger.info(f"Hari Baru: {today.strftime('%A, %d %B %Y')}")
                    logger.info(f"Waktu Absen Masuk : {random_times['morning']['hour']:02d}:{random_times['morning']['minute']:02d} WIB")
                    logger.info(f"Waktu Absen Pulang: {random_times['afternoon']['hour']:02d}:{random_times['afternoon']['minute']:02d} WIB")
                    logger.info(f"{'='*50}\n")
                
                if automation.is_working_day() and random_times:
                    current_hour = now.hour
                    current_min = now.minute
                    
                    # Check absen pagi
                    if not morning_done:
                        if (current_hour > random_times['morning']['hour'] or 
                            (current_hour == random_times['morning']['hour'] and current_min >= random_times['morning']['minute'])):
                            logger.info(f"⏰ Waktu Absen MASUK! ({now.strftime('%H:%M')})")
                            automation.run_automation(site=site)
                            morning_done = True
                    
                    # Check absen sore
                    if not afternoon_done:
                        if (current_hour > random_times['afternoon']['hour'] or 
                            (current_hour == random_times['afternoon']['hour'] and current_min >= random_times['afternoon']['minute'])):
                            logger.info(f"⏰ Waktu Absen PULANG! ({now.strftime('%H:%M')})")
                            automation.run_automation(site=site)
                            afternoon_done = True
                    
                    if morning_done and afternoon_done:
                        logger.info(f"✅ Absen hari ini selesai. Menunggu hari berikutnya...")
                else:
                    if not automation.is_working_day():
                        logger.info(f"Hari ini bukan hari kerja ({now.strftime('%A')}). Skip.")
                
                # Sleep 1 menit untuk cek lebih presisi
                time.sleep(60)
                
            except KeyboardInterrupt:
                logger.info("Scheduler stops.")
                break
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                time.sleep(60)


if __name__ == "__main__":
    main()
