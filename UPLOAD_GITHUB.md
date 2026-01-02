# Cara Upload ke GitHub (Langkah Cepat)

## Langkah 1: Buat Repository di GitHub

1. Buka https://github.com/new (atau klik **"+"** → **"New repository"**)
2. Isi form:
   - **Repository name**: `web_automation`
   - **Description**: (opsional) "Aplikasi Python untuk otomatisasi web"
   - **Visibility**: Pilih **Public** atau **Private**
   - **JANGAN centang** "Initialize with README" (karena sudah ada)
3. Klik **"Create repository"**

## Langkah 2: Upload Kode

Setelah repository dibuat, jalankan salah satu cara berikut:

### Cara A: Menggunakan Script Otomatis (Mudah)
```bash
push_to_github.bat
```
Script akan meminta URL repository, lalu upload otomatis.

### Cara B: Manual (Copy-Paste)

Ganti `USERNAME` dengan username GitHub Anda, lalu jalankan:

```bash
git remote add origin https://github.com/USERNAME/web_automation.git
git branch -M main
git push -u origin main
```

**Catatan:** Jika diminta password, gunakan **Personal Access Token** (bukan password biasa).

### Cara C: Menggunakan SSH (Jika sudah setup SSH key)

```bash
git remote add origin git@github.com:USERNAME/web_automation.git
git branch -M main
git push -u origin main
```

## Membuat Personal Access Token (Jika diperlukan)

1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token (classic)
3. Beri nama: `web_automation`
4. Pilih scope: **repo** (full control)
5. Generate token
6. **Copy token** (hanya muncul sekali!)
7. Gunakan token sebagai password saat push

## Selesai! ✅

Repository Anda akan tersedia di: `https://github.com/USERNAME/web_automation`

