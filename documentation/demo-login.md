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

1. Password di database tersimpan sebagai **bcrypt hash**, bukan plaintext.
   Kolom `password` pada respons demo berisi **hash yang tersimpan** — bukan
   kata sandi asli yang bisa dipakai login.
2. Endpoint demo **jangan pernah diaktifkan di production**. Kalau perlu
   dilindungi, tambahkan auth dependency di handler-nya.
3. Akun seed (lihat `backend/app/db/seed.py` dan docstring
   `POST /api/v1/auth/login`) menggunakan kata sandi default yang sudah
   terdokumentasi:
   - `admin@email.com` / `admin123` (admin)
   - `ops@email.com` / `ops123` (operations)
   - `marketing@email.com` / `marketing123` (marketing)
   - `finance@email.com` / `finance123` (finance)

## Verifikasi

```bash
# daftar tajam perbedaan kedua respons (field)
curl -s http://localhost:8000/api/v1/profiles | python3 -m json.tool | head -8
curl -s http://localhost:8000/api/v1/profiles/demo | python3 -m json.tool | head -8
```

Respons demo memiliki satu field `password` ekstra per user; respons
`/profiles` tidak.