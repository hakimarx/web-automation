# Quick Start Guide

## Setup Cepat (Windows)

1. **Jalankan Setup**
   ```bash
   setup.bat
   ```

2. **Edit config.json**
   - Buka `config.json` dengan text editor
   - Isi email Gmail dan App Password
   - Isi URL website
   - Isi selector tombol yang akan diklik

3. **Jalankan Aplikasi**
   ```bash
   python web_automation.py
   ```
   atau double-click `run_example.bat`

## Mendapatkan Gmail App Password

1. Buka: https://myaccount.google.com/
2. Security → 2-Step Verification (aktifkan dulu)
3. Security → App passwords
4. Generate password untuk "Mail"
5. Copy password 16 karakter
6. Paste ke config.json di field `app_password`

## Contoh Selector

**ID Selector:**
```json
"selector": "#my-button-id"
```

**Class Selector:**
```json
"selector": ".my-button-class"
```

**XPath:**
```json
"selector": "xpath=//button[@class='submit']"
```

**Text (Playwright):**
```json
"selector": "text=Klik Saya"
```

## Test Manual

Untuk test tanpa scheduler, edit `web_automation.py`:

Di fungsi `main()`, ubah:
```python
# automation.run_scheduler()
automation.run_automation()  # Uncomment ini
```

Jalankan: `python web_automation.py`

## Troubleshooting Cepat

**Import Error?**
```bash
pip install -r requirements.txt
playwright install chromium
```

**Email gagal?**
- Pastikan App Password (bukan password biasa)
- 2-Step Verification harus aktif

**Tombol tidak diklik?**
- Cek selector di browser DevTools (F12)
- Tambah timeout di config.json

