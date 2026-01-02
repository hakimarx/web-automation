# Panduan Upload ke GitHub

Repository Git sudah diinisialisasi dan commit awal sudah dibuat. Ikuti langkah berikut untuk upload ke GitHub:

## Langkah 1: Buat Repository Baru di GitHub

1. Buka https://github.com dan login ke akun Anda
2. Klik tombol **"+"** di kanan atas → pilih **"New repository"**
3. Isi informasi repository:
   - **Repository name**: `web_automation` (atau nama lain sesuai keinginan)
   - **Description**: (opsional) "Aplikasi Python untuk otomatisasi web dengan penjadwalan dan notifikasi Gmail"
   - **Visibility**: Pilih **Public** atau **Private**
   - **JANGAN** centang "Initialize this repository with a README" (karena sudah ada)
   - **JANGAN** pilih .gitignore atau license (sudah ada)
4. Klik **"Create repository"**

## Langkah 2: Upload Kode ke GitHub

Setelah repository dibuat, GitHub akan menampilkan instruksi. Gunakan perintah berikut di terminal/command prompt:

### Jika menggunakan HTTPS:
```bash
git remote add origin https://github.com/USERNAME/web_automation.git
git branch -M main
git push -u origin main
```

### Jika menggunakan SSH:
```bash
git remote add origin git@github.com:USERNAME/web_automation.git
git branch -M main
git push -u origin main
```

**Catatan:** Ganti `USERNAME` dengan username GitHub Anda.

Jika branch Anda masih `master`, gunakan:
```bash
git branch -M master main
git push -u origin main
```

## Langkah 3: Konfigurasi Git (Opsional - jika belum)

Jika ingin mengatur identitas Git secara global untuk commit selanjutnya:
```bash
git config --global user.name "Nama Anda"
git config --global user.email "email@example.com"
```

## Catatan Penting

✅ **config.json** sudah diabaikan oleh Git (tidak akan di-upload) - ini untuk keamanan
✅ File **config.json.example** sudah dibuat sebagai template untuk pengguna lain
✅ Semua file penting sudah siap untuk di-upload

## Setelah Upload Berhasil

1. Repository Anda akan muncul di https://github.com/USERNAME/web_automation
2. Pengguna lain bisa clone repository dengan:
   ```bash
   git clone https://github.com/USERNAME/web_automation.git
   ```
3. Mereka perlu membuat `config.json` dari `config.json.example`:
   ```bash
   cp config.json.example config.json
   # lalu edit config.json sesuai kebutuhan
   ```

