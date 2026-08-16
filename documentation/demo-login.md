# Demo Login Helper — Endpoint `/profiles/demo`

## Tujuan

Halaman login (`frontend/app/pages/login.vue`) menampilkan daftar akun
terdaftar beserta **password** sebagai alat bantu masuk ke sistem saat demo
atau pengembangan lokal.

Agar endpoint production tidak berubah, dibuat **endpoint demo terpisah**
yang hanya menyertakan kolom `password` pada responsnya.

## Endpoint

| Endpoint | Schema respons | Kolom password |
| --- | --- | --- |
| `GET /api/v1/profiles` | `ProfileResponse` (`backend/app/schemas/profile.py`) | **Tidak ada** (production) |
| `GET /api/v1/profiles/demo` | `ProfileDemoResponse` (turunan dari `ProfileResponse`) | Ada (`password: str`) |

Keduanya mengembalikan daftar user terbaru di atas (urut `created_at` desc).
Endpoint demo **bukan** perubahan dari endpoint lama — endpoint lama
`GET /profiles` dibiarkan apa adanya.

## Implementasi

- `backend/app/schemas/profile.py` — definisi `ProfileDemoResponse(ProfileResponse)`.
- `backend/app/api/v1/endpoints/profiles.py` — handler `list_profiles_demo`
  (terdaftar **sebelum** `/profiles/{id}` agar rute tidak tertangkap sebagai `id`).
- `frontend/app/pages/login.vue` — `useAsyncData` memanggil `/profiles/demo`.

## Catatan penting (keamanan)

1. Password login tersimpan sebagai **bcrypt hash** di kolom `password`
   (satu arah, tidak bisa di-decrypt). Endpoint demo membaca salinan plaintext
   dari kolom **`demo_password`** (hanya untuk demo):
   - `User.demo_password` diisi saat user dibuat/diubah (`POST/PUT /profiles`)
     dan saat seed (`backend/app/db/seed.py`).
   - Endpoint demo mengembalikan `password` = nilai `demo_password`
     (fallback `""` bila kosong, misal user lama/buatan luar sistem).
   - Kolom `demo_password` **tidak pernah** digunakan untuk autentikasi —
     login tetap `bcrypt.verify` terhadap kolom `password`.
2. Endpoint demo **jangan pernah diaktifkan di production**. Kalau perlu
   dilindungi, tambahkan auth dependency di handler-nya.
3. Akun seed (lihat `backend/app/db/seed.py` dan docstring
   `POST /api/v1/auth/login`) menggunakan kata sandi default yang sudah
   terdokumentasi:
   - `admin@mapetroleum.co.id` / `admin123` (admin)
   - `ops@mapetroleum.co.id` / `ops123` (operations)
   - `marketing@mapetroleum.co.id` / `marketing123` (marketing)
   - `finance@mapetroleum.co.id` / `finance123` (finance)
   - `accounting@mapetroleum.co.id` / `accounting123` (accounting)

## Migrasi database

Kolom `demo_password` ditambahkan ke model `User`, tetapi `create_all`
tidak mengubah tabel yang sudah ada. Untuk database lama, jalankan sekali:

```bash
docker exec mandalan-db mysql -uroot -proot mandalan \
  -e "ALTER TABLE users ADD COLUMN demo_password VARCHAR(255) NULL"
```

Lalu isi user existing (contoh, sesuai kebutuhan):

```bash
docker exec mandalan-db mysql -uroot -proot mandalan \
  -e "UPDATE users SET demo_password='xxx' WHERE email='user@example.com'"
```

## Verifikasi

```bash
# daftar tajam perbedaan kedua respons (field)
curl -s http://localhost:8000/api/v1/profiles | python3 -m json.tool | head -8
curl -s http://localhost:8000/api/v1/profiles/demo | python3 -m json.tool | head -8
```

Respons demo memiliki satu field `password` ekstra per user (plaintext dari
`demo_password`); respons `/profiles` tidak, dan autentikasi tetap memakai
hash bcrypt (kolom `password`).