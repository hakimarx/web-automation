# Panduan Upload ke cPanel

## Akses cPanel

1. Buka browser dan akses: **http://159.69.183.150:2082/**
2. Login dengan:
   - Username: `hafizjat`
   - Password: `RIhzuC[5[21x4M`

## Upload Files

### Langkah 1: Buka File Manager
1. Di cPanel dashboard, cari dan klik **"File Manager"**
2. Akan membuka file browser

### Langkah 2: Buat Folder
1. Klik **"+ Folder"** untuk buat folder baru
2. Nama folder: `pusaka`
3. Klik "Create New Folder"

### Langkah 3: Upload Files
1. Klik folder `pusaka`
2. Klik **"Upload"** di toolbar atas
3. Upload 3 file berikut dari folder `c:\Users\Administrator\web otomasi\web-automation`:
   - `pusaka_cpanel.py`
   - `requirements_cpanel.txt` → rename jadi `requirements.txt`
   - `cpanel_env` → rename jadi `.env`

### Langkah 4: Setup Cron Job
1. Kembali ke cPanel dashboard
2. Cari dan klik **"Cron Jobs"**
3. Tambahkan cron job baru:
   - **Common Settings**: Pilih "Every 30 minutes"
   - **Command**: 
     ```
     cd /home/hafizjat/pusaka && /usr/bin/python3 pusaka_cpanel.py >> /home/hafizjat/pusaka/cron.log 2>&1
     ```
4. Klik **"Add New Cron Job"**

## Verifikasi

Setelah setup, cron akan berjalan setiap 30 menit dan:
- Pagi (06:00-07:30): Akan absen MASUK pada waktu random
- Sore (16:30-19:00): Akan absen PULANG pada waktu random

Log tersimpan di `/home/hafizjat/pusaka/pusaka_cpanel.log`

---

## Files yang Perlu di-Upload

| File Lokal | File di cPanel |
|-----------|----------------|
| `pusaka_cpanel.py` | `pusaka_cpanel.py` |
| `requirements_cpanel.txt` | `requirements.txt` |
| `cpanel_env` | `.env` |

## Isi File .env

```
PUSAKA_USERNAME=198104302009011011
PUSAKA_PASSWORD=g4yung4n
EMAIL_FROM=
EMAIL_TO=hakimarx@gmail.com
EMAIL_APP_PASSWORD=
```
