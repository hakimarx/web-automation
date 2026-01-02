# Aplikasi Otomatisasi Web dengan Penjadwalan

Aplikasi Python untuk mengklik tombol web secara otomatis pada hari kerja Indonesia (Senin-Jumat) dengan notifikasi Gmail.

## Fitur

- ✅ Otomatisasi klik tombol web menggunakan Playwright
- ✅ Penjadwalan otomatis pada hari kerja (Senin-Jumat)
- ✅ Notifikasi Gmail saat tugas selesai/gagal
- ✅ Ringan resource (headless browser)
- ✅ Gratis dan open source
- ✅ Berjalan di Laptop (Windows/Mac/Linux) dan Android (via Termux)

## Instalasi

### Untuk Laptop (Windows/Mac/Linux)

1. **Install Python 3.8+**
   - Download dari [python.org](https://www.python.org/downloads/)
   - Pastikan "Add Python to PATH" dicentang saat install

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

3. **Konfigurasi Gmail App Password**
   - Buka [Google Account Settings](https://myaccount.google.com/)
   - Security → 2-Step Verification (aktifkan jika belum)
   - App passwords → Generate password baru
   - Copy password yang dihasilkan

4. **Edit File config.json**
   - Buka `config.json`
   - Isi `from_email`: email Gmail Anda
   - Isi `app_password`: App Password dari langkah 3
   - Isi `to_email`: email tujuan notifikasi
   - Isi `url`: URL website yang akan diotomasi
   - Isi `buttons`: array tombol yang akan diklik (dengan selector CSS/XPath)
   - Isi `times`: jadwal waktu (format 24 jam, contoh: "09:00", "14:00")

### Contoh Konfigurasi Selector

```json
"buttons": [
  {
    "name": "Tombol Login",
    "selector": "#login-button",  // ID selector
    "wait_after": 3  // tunggu 3 detik setelah klik
  },
  {
    "name": "Tombol Submit",
    "selector": "button[type='submit']",  // CSS selector
    "wait_after": 2
  },
  {
    "name": "Tombol dengan Text",
    "selector": "text=Klik Saya",  // Text selector Playwright
    "wait_after": 2
  }
]
```

### Cara Mendapatkan Selector

1. Buka website yang ingin diotomasi
2. Klik kanan pada tombol → Inspect
3. Copy selector:
   - ID: gunakan `#id-nama`
   - Class: gunakan `.nama-class`
   - XPath: gunakan `xpath=//button[@id='id']`
   - Text: gunakan `text=Teks Tombol`

## Menjalankan Aplikasi

### Mode Scheduler (Otomatis)
```bash
python web_automation.py
```

Aplikasi akan berjalan terus dan menjalankan tugas sesuai jadwal.

### Mode Manual (Test Sekali)
Edit `web_automation.py`, uncomment baris ini di fungsi `main()`:
```python
automation.run_automation()
```

Dan comment baris:
```python
automation.run_scheduler()
```

## Untuk Android (HP)

### Menggunakan Termux

1. **Install Termux**
   - Download dari [F-Droid](https://f-droid.org/en/packages/com.termux/) (gratis)
   - Atau dari [Play Store](https://play.google.com/store/apps/details?id=com.termux)

2. **Setup di Termux**
   ```bash
   # Update package
   pkg update && pkg upgrade
   
   # Install Python
   pkg install python
   
   # Install git (jika perlu clone repo)
   pkg install git
   
   # Install dependencies
   pip install -r requirements.txt
   playwright install chromium
   
   # Jalankan aplikasi
   python web_automation.py
   ```

3. **Agar Berjalan di Background**
   - Install `termux-wake-lock` untuk mencegah sleep
   - Atau gunakan `nohup python web_automation.py &`

### Alternatif: Menggunakan Pydroid 3 (GUI)

1. Install Pydroid 3 dari Play Store
2. Copy semua file ke folder Pydroid
3. Install dependencies melalui menu Pip
4. Jalankan `web_automation.py`

## Konfigurasi Jadwal

Jadwal diatur dalam `config.json`:
```json
"schedule": {
  "times": [
    "09:00",   // Setiap hari kerja jam 9 pagi
    "14:00",   // Setiap hari kerja jam 2 siang
    "17:00"    // Setiap hari kerja jam 5 sore
  ]
}
```

Format waktu: 24 jam (HH:MM)
Aplikasi hanya akan berjalan pada hari kerja (Senin-Jumat)

## Notifikasi Email

Notifikasi akan dikirim saat:
- ✅ Tugas berhasil diselesaikan
- ❌ Tugas gagal/error

Pastikan Gmail App Password sudah dikonfigurasi dengan benar.

## Log

Aplikasi akan membuat file log: `web_automation.log`

## Tips Penghematan Resource

1. **Headless Mode**: Browser berjalan tanpa GUI (sudah default)
2. **Single Instance**: Hanya 1 browser instance per eksekusi
3. **Timeout**: Set timeout yang wajar untuk menghindari hang
4. **Interval Check**: Scheduler check setiap 1 menit (sudah optimal)

## Troubleshooting

### Error: "Email tidak terkirim"
- Pastikan 2-Step Verification aktif
- Gunakan App Password, bukan password biasa
- Cek firewall/antivirus yang memblokir SMTP

### Error: "Timeout saat klik tombol"
- Periksa selector apakah masih valid
- Tambah timeout di config.json
- Pastikan website sudah fully loaded

### Error: "Browser tidak terinstall"
```bash
playwright install chromium
```

### Aplikasi tidak jalan di Android
- Pastikan Termux tidak di-kill oleh sistem
- Gunakan `termux-wake-lock` untuk mencegah sleep
- Atau jalankan manual saat diperlukan

## Lisensi

Gratis untuk penggunaan pribadi dan komersial.

## Support

Untuk masalah atau pertanyaan, buat issue di repository ini.

