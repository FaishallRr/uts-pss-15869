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
