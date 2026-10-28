# Minggu 4 — Simple LMS (Django ORM & Model)

Praktikum **Pemrograman Sisi Server | Django Framework & ORM** — Modul Praktikum 4.

Proyek "Simple LMS" berisi model `User` (custom, dengan role), `Course`, `Lesson`,
`Enrollment`, `Assignment`, dan `Submission`, beserta seed idempotent, Django Admin,
dan unit test.

## Persyaratan

- Windows + VS Code
- Docker Desktop (Python, Django, dan PostgreSQL berjalan di container — tidak perlu
  instal Python/PostgreSQL di host)

## Menjalankan (reproduksi)

```powershell
docker compose build
docker compose up -d
docker compose ps

docker compose exec app python --version
docker compose exec app python -m django --version
docker compose exec db psql --version
```

Semua perintah Django dijalankan dari container `app`:

```powershell
docker compose exec app python manage.py ...
```

## Struktur project

```
pss-week4-demo/
├── manage.py
├── config/          # settings, urls, wsgi/asgi
├── users/           # custom User (role ADMIN/LECTURER/STUDENT) + CustomUserAdmin
├── catalog/         # Course, Lesson, Enrollment, Assignment, Submission + admin + seed + tests
├── requirements.txt
├── Dockerfile
├── compose.yaml
├── .env             # DB_NAME/DB_USER/DB_PASSWORD (tidak di-commit)
├── .gitignore
└── .dockerignore
```

## Konfigurasi

`.env` (development lokal):

```
DB_NAME=lms_db
DB_USER=lms_user
DB_PASSWORD=lms_password
```

Database PostgreSQL di `config/settings.py` dibaca dari environment (`HOST=db`, `PORT=5432`).
`AUTH_USER_MODEL = "users.User"` ditetapkan sebelum migration authentication pertama.

## Langkah implementasi

1. **Fondasi Docker** — `requirements.txt`, `Dockerfile`, `compose.yaml`, `.env`,
   `.gitignore`, `.dockerignore`; build & verifikasi container.
2. **Bootstrap project** — `django-admin startproject config .`, `startapp users`,
   `startapp catalog`; daftarkan app di `INSTALLED_APPS`.
3. **Custom User** — `users/models.py` (`User(AbstractUser)` + `Role`), lalu
   `makemigrations` & `migrate`.
4. **Superuser** — `createsuperuser` (username `admin`), set `role=ADMIN`,
   `is_staff=True`, `is_superuser=True`.
5. **Domain LMS** — `catalog/models.py`:
   - `Course` — `code` unik, FK `lecturer` (`PROTECT`, `related_name="courses_taught"`,
     `limit_choices_to={"role": "LECTURER"}`)
   - `Lesson` — FK `course` (`CASCADE`, `related_name="lessons"`), unik per
     `(course, order)`
   - `Enrollment` — intermediate model, unik per `(student, course)`
   - `Assignment` — FK `course` (`related_name="assignments"`)
   - `Submission` — FK `assignment` + `student`, `grade` decimal
6. **Django Admin** — registrasi semua model + `CustomUserAdmin` (field `role`).
7. **QuerySet traversal** — `course.lessons.all()`, `lesson.course`,
   `select_related("lecturer")`, `prefetch_related("lessons")`.
8. **Seed idempotent** — management command `seed_demo` (`get_or_create`).
9. **Testing** — minimal 3 unit test di `catalog/tests.py`.

## Verifikasi

```powershell
# migration & system check
docker compose exec app python manage.py makemigrations
docker compose exec app python manage.py migrate
docker compose exec app python manage.py showmigrations
docker compose exec app python manage.py check

# seed sample data (idempotent — aman dijalankan berulang)
docker compose exec app python manage.py seed_demo
docker compose exec app python manage.py seed_demo

# unit test (minimal 3 test: unique code, created, relationship)
docker compose exec app python manage.py test catalog

# Django Admin
# http://localhost:8000/admin/  (username: admin)
```

Cek data via shell:

```powershell
docker compose exec app python manage.py shell
```

```python
from catalog.models import Course, Lesson, Assignment, Submission, Enrollment
Course.objects.count()
Lesson.objects.count()
Assignment.objects.count()
Submission.objects.count()
Enrollment.objects.count()

course = Course.objects.get(code="PSS01")
course.lecturer.username
for lesson in course.lessons.all():
    print(lesson.order, lesson.title)
```

Contoh optimasi query (jumlah query turun):

```python
from django.db import connection, reset_queries
from catalog.models import Course

reset_queries()
for c in Course.objects.select_related("lecturer"):
    print(c.code, c.lecturer.username)
print(len(connection.queries))  # 1 query (tanpa select_related: 1 + N)

reset_queries()
for c in Course.objects.prefetch_related("lessons"):
    for l in c.lessons.all():
        print("-", l.title)
print(len(connection.queries))  # konstan, tanpa prefetch: 1 + N
```

## Data awal

| Username    | Role     | Password |
|-------------|----------|----------|
| `admin`     | ADMIN    | dibuat saat `createsuperuser` |
| `suprayogi` | LECTURER | `12345`  |
| `fauzan`    | STUDENT  | `12345`  |

> Kredensial di atas hanya untuk development lokal. Jangan commit credential nyata
> ke repository (`.env` sudah masuk `.gitignore`).

## Git

```powershell
git status --short
git add .
git commit -m "feat: complete week 4 django orm core lms models"
git branch -M main
git remote add origin https://github.com/USERNAME/REPOSITORY.git
git push -u origin main
```

---

# Minggu 5 — Database & Performance Optimization

Lanjutan Milestone 4: profiling, N+1 query, ORM optimization, EXPLAIN, dan index
pada project Simple LMS yang sama (tidak ada project baru).

Dependency tambahan (sudah ada di `requirements.txt`):

```
django-debug-toolbar
django-redis
```

Rebuild setelah perubahan dependency:

```powershell
docker compose build app
docker compose up -d
```

Django Debug Toolbar dikonfigurasi di `config/settings.py` (INSTALLED_APPS,
middleware, `INTERNAL_IPS`) dan `config/urls.py` (`__debug__/` saat `DEBUG`).
Jika toolbar tidak tampil dari Docker, gunakan `CaptureQueriesContext`
sebagai bukti benchmark.

## Membuat dataset performa (repeatable)

Dua management command — aman dijalankan berulang (tidak duplikat):

```powershell
# 10.000 Course PERF00000-PERF09999 (bulk_create, batch 500)
docker compose exec app python manage.py generate_performance_data

# Relasi: 5 lecturer + 50 student simulasi, 100 course, 1.000 enrollment,
# 500 lesson, 200 assignment, 1.000 submission
docker compose exec app python manage.py generate_relationship_data
```

Verifikasi jumlah data:

```powershell
docker compose exec app python manage.py shell -c "from catalog.models import Course; print(Course.objects.count())"
```

## Mengulang benchmark (before vs after)

Selalu pakai dataset & skenario yang sama saat membandingkan.

**1. Baseline (CHECKPOINT 1)**

```python
from django.db import connection
from django.test.utils import CaptureQueriesContext
from catalog.models import Course

with CaptureQueriesContext(connection) as ctx:
    rows = list(Course.objects.all())
print("Jumlah Course:", len(rows), "| Query SQL:", len(ctx.captured_queries))
```

**2. N+1 Course + Lecturer — BEFORE (101 query) vs AFTER (1 query)**

```python
import time
from django.db import connection
from django.test.utils import CaptureQueriesContext
from catalog.models import Course

# BEFORE
start = time.perf_counter()
with CaptureQueriesContext(connection) as ctx:
    result = [(c.title, c.lecturer.username)
              for c in Course.objects.filter(code__startswith="PERF").order_by("code")[:100]]
print("BEFORE:", len(ctx.captured_queries), "query,", round(time.perf_counter() - start, 4), "detik")

# AFTER
start = time.perf_counter()
with CaptureQueriesContext(connection) as ctx:
    result = [(c.title, c.lecturer.username)
              for c in Course.objects.filter(code__startswith="PERF").order_by("code")
              .select_related("lecturer")[:100]]
print("AFTER:", len(ctx.captured_queries), "query,", round(time.perf_counter() - start, 4), "detik")
```

**3. N+1 Course + Lesson — BEFORE (51 query) vs AFTER (2 query)**

```python
# BEFORE
with CaptureQueriesContext(connection) as ctx:
    for course in Course.objects.filter(code__startswith="PERF").order_by("code")[:50]:
        titles = [l.title for l in course.lessons.all()]
print("BEFORE:", len(ctx.captured_queries))

# AFTER
with CaptureQueriesContext(connection) as ctx:
    for course in Course.objects.filter(code__startswith="PERF").order_by("code")
            .prefetch_related("lessons")[:50]:
        titles = [l.title for l in course.lessons.all()]
print("AFTER:", len(ctx.captured_queries))
```

**4. EXPLAIN + index**

Index ditambahkan di `catalog/models.py`:

```python
class Meta:
    ordering = ["code"]
    indexes = [
        models.Index(fields=["is_active", "title"]),
    ]
```

```powershell
docker compose exec app python manage.py makemigrations
docker compose exec app python manage.py migrate
```

```python
from catalog.models import Course
print(Course.objects.filter(code="PERF05000").explain())                          # Index Scan (unique index code)
print(Course.objects.filter(is_active=True, title="Performance Course 5000").explain())  # Index Scan (index baru)
```

Sebelum index: `Seq Scan` (cost ±239) → sesudah index: `Index Scan` (cost ±8).
Catatan: PostgreSQL tidak selalu memakai index; buktikan lewat hasil `explain()`.

**5. Pastikan test tetap hijau**

```powershell
docker compose exec app python manage.py test
```

## Hasil benchmark (contoh, lingkungan Docker)

| Skenario | BEFORE | AFTER |
|---|---|---|
| 100 Course + Lecturer | 101 query, 0.0888s | 1 query, 0.0312s (`select_related`) |
| 50 Course + Lesson | 51 query, 0.0722s | 2 query, 0.0113s (`prefetch_related`) |
| Query `is_active` + `title` | Seq Scan, cost 239.01 | Index Scan, cost 8.30 |

Query count, execution time, dan plan `explain()` dicatat sebelum dan sesudah
setiap perubahan — optimasi dinilai dari pengukuran, bukan asumsi.

