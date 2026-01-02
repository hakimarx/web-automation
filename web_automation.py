"""
Aplikasi Otomatisasi Web dengan Penjadwalan
Mengklik tombol web secara otomatis pada hari kerja Indonesia (Senin-Jumat)
Mengirim notifikasi Gmail saat tugas selesai
"""

import json
import time
import smtplib
import schedule
import logging
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

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
    def __init__(self, config_file='config.json'):
        """Initialize dengan file konfigurasi"""
        with open(config_file, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.email_config = self.config.get('email', {})
        self.automation_config = self.config.get('automation', {})
        self.schedule_config = self.config.get('schedule', {})
    
    def is_working_day(self):
        """Cek apakah hari ini adalah hari kerja Indonesia (Senin-Jumat)"""
        today = datetime.now()
        day_of_week = today.weekday()  # 0=Monday, 6=Sunday
        
        # Senin-Jumat (0-4)
        if day_of_week < 5:
            return True
        return False
    
    def send_email_notification(self, success=True, message=""):
        """Kirim notifikasi via Gmail"""
        if not self.email_config.get('enabled', False):
            return
        
        try:
            # Setup email
            msg = MIMEMultipart()
            msg['From'] = self.email_config['from_email']
            msg['To'] = self.email_config['to_email']
            
            if success:
                msg['Subject'] = self.email_config.get('subject_success', '✅ Tugas Otomatisasi Berhasil')
                body = f"""
Tugas otomatisasi web telah berhasil diselesaikan!

Waktu: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{message}

---
Aplikasi Web Automation
                """
            else:
                msg['Subject'] = self.email_config.get('subject_error', '❌ Tugas Otomatisasi Gagal')
                body = f"""
Tugas otomatisasi web mengalami error!

Waktu: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Error: {message}

---
Aplikasi Web Automation
                """
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # Kirim email via SMTP Gmail
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.email_config['from_email'], self.email_config['app_password'])
            server.send_message(msg)
            server.quit()
            
            logger.info("Email notifikasi berhasil dikirim")
            
        except Exception as e:
            logger.error(f"Gagal mengirim email: {str(e)}")
    
    def run_automation(self):
        """Jalankan otomatisasi klik tombol web"""
        if not self.is_working_day():
            logger.info("Hari ini bukan hari kerja, tugas dilewati")
            return
        
        url = self.automation_config.get('url')
        buttons = self.automation_config.get('buttons', [])
        wait_time = self.automation_config.get('wait_time_between_clicks', 2)
        timeout = self.automation_config.get('timeout', 30000)  # 30 detik default
        
        if not url or not buttons:
            logger.error("URL atau tombol tidak dikonfigurasi")
            self.send_email_notification(success=False, message="Konfigurasi tidak lengkap")
            return
        
        try:
            logger.info(f"Memulai otomatisasi untuk URL: {url}")
            
            with sync_playwright() as p:
                # Launch browser dalam headless mode untuk efisiensi resource
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    viewport={'width': 1280, 'height': 720},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                )
                page = context.new_page()
                
                # Buka URL
                logger.info(f"Membuka URL: {url}")
                page.goto(url, timeout=timeout, wait_until='domcontentloaded')
                
                # Tunggu sebentar untuk halaman load
                page.wait_for_timeout(2000)
                
                # Klik setiap tombol sesuai konfigurasi
                clicked_buttons = []
                for i, button_config in enumerate(buttons):
                    selector = button_config.get('selector')
                    name = button_config.get('name', f'Button {i+1}')
                    wait_after = button_config.get('wait_after', wait_time)
                    
                    if not selector:
                        logger.warning(f"Selector tidak ditemukan untuk tombol: {name}")
                        continue
                    
                    try:
                        logger.info(f"Mengklik tombol: {name} (selector: {selector})")
                        page.click(selector, timeout=timeout)
                        clicked_buttons.append(name)
                        
                        # Tunggu setelah klik
                        if wait_after > 0:
                            page.wait_for_timeout(wait_after * 1000)
                        
                    except PlaywrightTimeoutError:
                        logger.error(f"Timeout saat mengklik tombol: {name}")
                    except Exception as e:
                        logger.error(f"Error saat mengklik tombol {name}: {str(e)}")
                
                # Tunggu sebelum close
                page.wait_for_timeout(1000)
                
                browser.close()
            
            # Kirim notifikasi sukses
            success_message = f"Berhasil mengklik {len(clicked_buttons)} tombol:\n" + "\n".join(f"- {btn}" for btn in clicked_buttons)
            logger.info(f"Otomatisasi selesai: {success_message}")
            self.send_email_notification(success=True, message=success_message)
            
        except Exception as e:
            error_message = f"Error saat menjalankan otomatisasi: {str(e)}"
            logger.error(error_message)
            self.send_email_notification(success=False, message=error_message)
    
    def setup_schedule(self):
        """Setup penjadwalan berdasarkan konfigurasi"""
        schedule_times = self.schedule_config.get('times', [])
        
        for time_str in schedule_times:
            # Format waktu: "HH:MM" (24 jam)
            schedule.every().monday.at(time_str).do(self.run_automation)
            schedule.every().tuesday.at(time_str).do(self.run_automation)
            schedule.every().wednesday.at(time_str).do(self.run_automation)
            schedule.every().thursday.at(time_str).do(self.run_automation)
            schedule.every().friday.at(time_str).do(self.run_automation)
            
            logger.info(f"Penjadwalan ditambahkan: {time_str} (Senin-Jumat)")
    
    def run_scheduler(self):
        """Jalankan scheduler (blocking)"""
        logger.info("Scheduler dimulai...")
        logger.info("Aplikasi akan berjalan terus. Tekan Ctrl+C untuk berhenti.")
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # Cek setiap 1 menit


def main():
    """Main function"""
    try:
        automation = WebAutomation()
        automation.setup_schedule()
        
        # Jalankan sekali sekarang jika dijadwalkan
        # automation.run_automation()
        
        # Jalankan scheduler
        automation.run_scheduler()
        
    except KeyboardInterrupt:
        logger.info("Aplikasi dihentikan oleh user")
    except Exception as e:
        logger.error(f"Error: {str(e)}")


if __name__ == "__main__":
    main()

