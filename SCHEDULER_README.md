# Pusaka Auto Attendance - README

## Status Sistem

### Temuan Penting

Pusaka Kemenag menggunakan **2 metode presensi berbeda**:

| Tipe | Metode | Otomatisasi |
|------|--------|-------------|
| **Presensi MASUK** | Face Recognition (Verifikasi Wajah) | ❌ TIDAK BISA - memerlukan kamera |
| **Presensi PULANG** | Button Click + Konfirmasi | ✅ BISA via Playwright |

### Implikasi untuk cPanel

**cPanel shared hosting TIDAK BISA** menjalankan Playwright karena:
- Tidak ada Chrome/Chromium browser
- Tidak ada akses root untuk install dependencies

**Solusi yang tersedia:**

1. **Komputer Windows (Playwright)** - Full automation (masuk + pulang)
2. **cPanel (HTTP requests)** - PULANG only, MASUK via app manual

---

## Files

| File | Deskripsi |
|------|-----------|
| `web_automation.py` | Full Playwright automation (Windows only) |
| `pusaka_cpanel.py` | HTTP-based (cPanel compatible, PULANG only) |

---

## Opsi Deployment

### Opsi 1: Windows Task Scheduler (RECOMMENDED)

Full automation untuk MASUK dan PULANG dengan waktu random.

**Setup sudah selesai:**
- Task: `PusakaAttendance`
- Script: `C:\Scripts\pusaka.bat`
- Status: Ready (jalankan saat login)

**Jalankan manual:**
```bash
python web_automation.py --test --site pusaka
```

### Opsi 2: cPanel Cron Job (PULANG ONLY)

Hanya bisa melakukan presensi PULANG karena MASUK memerlukan Face Recognition.

**Setup:**
1. Upload `pusaka_cpanel.py`, `requirements_cpanel.txt`, `.env`
2. Install requirements via SSH:
   ```bash
   pip install -r requirements_cpanel.txt
   ```
3. Setup cron job untuk run setiap 30 menit:
   ```
   */30 * * * * cd /home/hafizjat/pusaka && python pusaka_cpanel.py
   ```

---

## Rekomendasi

**Untuk otomatisasi penuh (MASUK + PULANG):**
- Gunakan Windows Task Scheduler dengan `web_automation.py`
- Pastikan komputer menyala dan user login

**Untuk presensi PULANG saja:**
- Bisa gunakan cPanel
- Presensi MASUK harus dilakukan manual via Aplikasi Pusaka Mobile
