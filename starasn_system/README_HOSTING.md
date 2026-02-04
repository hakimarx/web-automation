# Panduan Deployment StarASN System di Shared Hosting

Aplikasi ini adalah modul PHP Native untuk sinkronisasi data StarASN yang dirancang khusus untuk berjalan di shared hosting.

## 📁 Struktur File
Upload folder `starasn_system` ke hosting Anda (misal ke `/home/username/starasn_system`).

## ⚙️ Konfigurasi
Edit file `config.php`:
1.  **Credentials**: Masukkan `STARASN_USERNAME` dan `STARASN_PASSWORD`.
2.  **OCR API**: Masukkan API Key OCR.Space ke `OCR_SPACE_API_KEY`.
3.  **Email**: Atur `NOTIFY_EMAIL` jika ingin menerima laporan.

## ⏰ Pengaturan Cron Job di cPanel (Tanpa Terminal)
Gunakan menu **Cron Jobs** di cPanel Anda (ada di bagian **Advanced**).

### Langkah-langkah:
1.  **Upload Folder**: Upload folder `starasn_system` ke hosting.
2.  **Buka Browser**: Akses file `cek_path.php` (misal: `https://domain-anda.com/starasn_system/cek_path.php`).
3.  **Salin Perintah**: Salin perintah yang muncul di sana.
4.  **Buka cPanel**: Klik icon **Cron Jobs**.
5.  **Tambah Jadwal Baru**: Masukkan jam yang diinginkan dan tempel perintah yang sudah disalin tadi.

## 🔍 Log Aktivitas
Anda bisa mengecek file `app_status.log` di dalam folder aplikasi untuk melihat riwayat aktivitas.
